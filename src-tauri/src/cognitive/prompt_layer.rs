use crate::normalization::sosm::SOSM;

/// Evaluates the existing context (SOSM footprint) and generates an exploration 
/// prompt for the ONNX SLM model to hypothesize about next steps
pub fn generate_reasoning_prompt(context: &SOSM) -> String {
    let mut state_summary = String::new();

    // Summarize hosts
    if !context.hosts.is_empty() {
        state_summary.push_str("Discovered Hosts:\n");
        for host in &context.hosts {
            let hostname = host.hostname.clone().unwrap_or_else(|| "Unknown".to_string());
            let os = host.os.clone().unwrap_or_else(|| "Unknown OS".to_string());
            state_summary.push_str(&format!("  - IP: {} ({}), OS: {}, Status: {}\n", host.ip, hostname, os, host.status));
        }
    }

    // Summarize services
    if !context.services.is_empty() {
        state_summary.push_str("\nActive Services:\n");
        for svc in &context.services {
            let product = svc.product.clone().unwrap_or_else(|| "Unknown Product".to_string());
            let version = svc.version.clone().unwrap_or_else(|| "Unknown Version".to_string());
            state_summary.push_str(&format!("  - Port {}/{} ({}): {} {}\n", 
                svc.port.number, svc.port.protocol, svc.name, product, version));
        }
    }

    // Include recent observations
    if !context.observations.is_empty() {
        state_summary.push_str("\nRecent Observations:\n");
        for obs in context.observations.iter().rev().take(5) { // Last 5
            state_summary.push_str(&format!("  - [{}] {}: {}\n", obs.timestamp, obs.tool_source, obs.description));
        }
    }

    // Core SLM instruction template 
    format!(
"You are KalpAI, a cognitive reasoning assistant for cybersecurity professionals.
You must interpret the current environmental context and suggest analytical hypotheses.
Do NOT execute actions or write scripts. Provide reasoning-driven guidance.

CURRENT ENVIRONMENTAL CONTEXT:
==============================
{}
==============================

Based on the context above, provide the following:
1. Explain what this environment likely represents.
2. Formulate 2 plausible vulnerability hypotheses based on the active services.
3. Suggest the next logical reconnaissance or verification step for the analyst.", 
        state_summary
    )
}
