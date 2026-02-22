use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, Clone)]
pub enum ConfidenceScore {
    Low,
    Medium,
    High,
    Confirmed,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Host {
    pub ip: String,
    pub hostname: Option<String>,
    pub os: Option<String>,
    pub status: String,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Port {
    pub number: u16,
    pub protocol: String,
    pub state: String,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Service {
    pub port: Port,
    pub name: String,
    pub product: Option<String>,
    pub version: Option<String>,
    pub extra_info: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Endpoint {
    pub url: String,
    pub method: String,
    pub status_code: Option<u16>,
    pub content_type: Option<String>,
    pub size: Option<usize>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Vulnerability {
    pub id: String, // CVE or custom ID
    pub title: String,
    pub description: String,
    pub severity: String,
    pub confidence: ConfidenceScore,
    pub references: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Observation {
    pub tool_source: String,
    pub description: String,
    pub timestamp: String,
    pub raw_data: Option<String>,
    pub confidence: ConfidenceScore,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Hypothesis {
    pub id: String,
    pub related_observations: Vec<String>,
    pub theory: String,
    pub recommended_action: String,
    pub confidence: ConfidenceScore,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct SOSM {
    pub hosts: Vec<Host>,
    pub services: Vec<Service>,
    pub endpoints: Vec<Endpoint>,
    pub observations: Vec<Observation>,
    pub vulnerabilities: Vec<Vulnerability>,
    pub hypotheses: Vec<Hypothesis>,
}

pub fn init_sosm() -> SOSM {
    SOSM {
        hosts: Vec::new(),
        services: Vec::new(),
        endpoints: Vec::new(),
        observations: Vec::new(),
        vulnerabilities: Vec::new(),
        hypotheses: Vec::new(),
    }
}

