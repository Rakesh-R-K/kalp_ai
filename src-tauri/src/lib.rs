pub mod capture;
pub mod normalization;
pub mod memory;
pub mod cognitive;

use std::sync::Arc;
use tokio::sync::Mutex;
use tauri::{Manager, State};

use crate::memory::surreal_store::SurrealMemoryStore;
use crate::cognitive::onnx_runner::CognitiveModel;

struct AppState {
    memory_store: Arc<Mutex<SurrealMemoryStore>>,
    cognitive_model: Arc<Mutex<CognitiveModel>>,
}

#[tauri::command]
async fn process_nmap_file(file_path: String, state: State<'_, AppState>) -> Result<String, String> {
    let sosm = capture::nmap_parser::parse_nmap_xml(&file_path)
        .map_err(|e| format!("Failed to parse {}: {}", file_path, e))?;
    
    let db = state.memory_store.lock().await;
    for host in &sosm.hosts {
        db.insert_host(host).await.map_err(|e| format!("DB Error: {}", e))?;
    }
    for obs in &sosm.observations {
        db.insert_observation(obs).await.map_err(|e| format!("DB Error: {}", e))?;
    }
    
    Ok(format!("Parsed Nmap output. Saved {} hosts into KalpAI memory.", sosm.hosts.len()))
}

#[tauri::command]
async fn process_gobuster_file(file_path: String, state: State<'_, AppState>) -> Result<String, String> {
    let sosm = capture::gobuster_parser::parse_gobuster_file(&file_path)
        .map_err(|e| format!("Failed to parse {}: {}", file_path, e))?;
    
    let db = state.memory_store.lock().await;
    for endpoint in &sosm.endpoints {
        db.insert_endpoint(endpoint).await.map_err(|e| format!("DB Error: {}", e))?;
    }
    for obs in &sosm.observations {
        db.insert_observation(obs).await.map_err(|e| format!("DB Error: {}", e))?;
    }
    
    Ok(format!("Parsed Gobuster output. Saved {} endpoints and {} observations.", sosm.endpoints.len(), sosm.observations.len()))
}

#[tauri::command]
async fn process_nikto_file(file_path: String, state: State<'_, AppState>) -> Result<String, String> {
    let sosm = capture::nikto_parser::parse_nikto_json(&file_path)
        .map_err(|e| format!("Failed to parse {}: {}", file_path, e))?;
    
    let db = state.memory_store.lock().await;
    for vuln in &sosm.vulnerabilities {
        db.insert_vulnerability(vuln).await.map_err(|e| format!("DB Error: {}", e))?;
    }
    for obs in &sosm.observations {
        db.insert_observation(obs).await.map_err(|e| format!("DB Error: {}", e))?;
    }
    
    Ok(format!("Parsed Nikto output. Saved {} vulnerabilities and {} observations.", sosm.vulnerabilities.len(), sosm.observations.len()))
}

#[tauri::command]
async fn get_memory_context(state: State<'_, AppState>) -> Result<normalization::sosm::SOSM, String> {
    let db = state.memory_store.lock().await;
    let hosts = db.get_hosts().await.unwrap_or_default();
    let observations = db.get_observations().await.unwrap_or_default();
    let hypotheses = db.get_hypotheses().await.unwrap_or_default();
    let endpoints = db.get_endpoints().await.unwrap_or_default();
    let vulnerabilities = db.get_vulnerabilities().await.unwrap_or_default();
    
    Ok(normalization::sosm::SOSM {
        hosts,
        services: vec![],
        endpoints,
        observations,
        vulnerabilities,
        hypotheses,
    })
}

#[tauri::command]
async fn reason_next_steps(state: State<'_, AppState>) -> Result<normalization::sosm::Hypothesis, String> {
    let sosm = get_memory_context(state.clone()).await?;
    let prompt = cognitive::prompt_layer::generate_reasoning_prompt(&sosm);

    let cog = state.cognitive_model.lock().await;
    let hypothesis = cog.generate_hypothesis(&prompt).await.map_err(|e| format!("SLM error: {}", e))?;
    
    let db = state.memory_store.lock().await;
    let _ = db.insert_hypothesis(&hypothesis).await;

    Ok(hypothesis)
}

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .setup(|app| {
            tauri::async_runtime::block_on(async move {
                let memory_store = SurrealMemoryStore::new().await.expect("Failed to init SurrealDB");
                let cognitive_model = CognitiveModel::new(None).expect("Failed to start cognitive model");

                app.manage(AppState {
                    memory_store: Arc::new(Mutex::new(memory_store)),
                    cognitive_model: Arc::new(Mutex::new(cognitive_model)),
                });
            });
            Ok(())
        })
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![
            greet,
            process_nmap_file,
            process_gobuster_file,
            process_nikto_file,
            get_memory_context,
            reason_next_steps
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
