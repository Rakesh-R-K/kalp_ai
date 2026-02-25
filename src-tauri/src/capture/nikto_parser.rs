use std::fs;
use serde::Deserialize;
use crate::normalization::sosm::{Observation, Vulnerability, ConfidenceScore, SOSM};

#[derive(Deserialize, Debug)]
struct NiktoOutput {
    pub vulnerabilities: Option<Vec<NiktoVuln>>,
    pub host: Option<String>,
}

#[derive(Deserialize, Debug)]
struct NiktoVuln {
    pub id: Option<String>,
    pub msg: Option<String>,
    pub url: Option<String>,
}

pub fn parse_nikto_json(file_path: &str) -> Result<SOSM, Box<dyn std::error::Error>> {
    let data = fs::read_to_string(file_path)?;
    let mut sosm = crate::normalization::sosm::init_sosm();

    if let Ok(json_data) = serde_json::from_str::<NiktoOutput>(&data) {
        if let Some(vulns) = json_data.vulnerabilities {
            for (i, v) in vulns.iter().enumerate() {
                let msg = v.msg.clone().unwrap_or_else(|| "Unknown Nikto Finding".to_string());
                
                let vuln = Vulnerability {
                    id: v.id.clone().unwrap_or_else(|| format!("NIKTO-VAR-{}", i)),
                    title: "Nikto Scan Finding".to_string(),
                    description: msg.clone(),
                    severity: "Unknown".to_string(),
                    confidence: ConfidenceScore::Medium,
                    references: vec![v.url.clone().unwrap_or_default()],
                };
                sosm.vulnerabilities.push(vuln);
                
                let obs = Observation {
                    tool_source: "Nikto".to_string(),
                    description: format!("Nikto identified: {}", msg),
                    timestamp: chrono::Utc::now().to_rfc3339(),
                    raw_data: Some(msg.clone()),
                    confidence: ConfidenceScore::Medium,
                };
                sosm.observations.push(obs);
            }
        }
    } else {
        // Fallback or plain text parsing could go here, for now return error
         return Err("Failed to parse Nikto JSON. Please ensure -Format json is used.".into());
    }

    Ok(sosm)
}
