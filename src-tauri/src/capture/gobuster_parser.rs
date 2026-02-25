use std::fs;
use crate::normalization::sosm::{Endpoint, Observation, SOSM, ConfidenceScore};

pub fn parse_gobuster_file(file_path: &str) -> Result<SOSM, Box<dyn std::error::Error>> {
    let data = fs::read_to_string(file_path)?;
    let mut sosm = crate::normalization::sosm::init_sosm();

    for line in data.lines() {
        if line.trim().is_empty() { continue; }
        
        let mut path = line.to_string();
        let mut status_code = None;

        if let Some(idx) = line.find(" (Status: ") {
            path = line[..idx].trim().to_string();
            if let Some(end_idx) = line[idx..].find(')') {
                let status_str = &line[idx + 10 .. idx + end_idx];
                status_code = status_str.parse::<u16>().ok();
            }
        } else {
            // Check if it's just a raw path starting with /
            if !line.starts_with('/') { continue; }
            let parts: Vec<&str> = line.split_whitespace().collect();
            path = parts[0].to_string();
        }

        let endpoint = Endpoint {
            url: path.clone(),
            method: "GET".to_string(),
            status_code,
            content_type: None,
            size: None,
        };
        sosm.endpoints.push(endpoint);

        let obs = Observation {
            tool_source: "Gobuster".to_string(),
            description: format!("Discovered endpoint via brute-force: {}", path),
            timestamp: chrono::Utc::now().to_rfc3339(),
            raw_data: Some(line.to_string()),
            confidence: ConfidenceScore::High,
        };
        sosm.observations.push(obs);
    }
    Ok(sosm)
}
