use serde::Deserialize;
use std::fs;
use crate::normalization::sosm::{Host, Port as SosmPort, Service as SosmService, Endpoint, SOSM};

#[derive(Debug, Deserialize)]
pub struct NmapRun {
    #[serde(rename = "host", default)]
    pub hosts: Vec<NmapHost>,
}

#[derive(Debug, Deserialize)]
pub struct NmapHost {
    pub status: Status,
    pub address: Address,
    pub hostnames: Option<Hostnames>,
    pub ports: Option<Ports>,
}

#[derive(Debug, Deserialize)]
pub struct Status {
    pub state: String,
}

#[derive(Debug, Deserialize)]
pub struct Address {
    pub addr: String,
}

#[derive(Debug, Deserialize)]
pub struct Hostnames {
    #[serde(rename = "hostname", default)]
    pub hostnames: Vec<Hostname>,
}

#[derive(Debug, Deserialize)]
pub struct Hostname {
    pub name: String,
}

#[derive(Debug, Deserialize)]
pub struct Ports {
    #[serde(rename = "port", default)]
    pub ports: Vec<Port>,
}

#[derive(Debug, Deserialize)]
pub struct Port {
    pub protocol: String,
    pub portid: u16,
    pub state: PortState,
    pub service: Option<Service>,
}

#[derive(Debug, Deserialize)]
pub struct PortState {
    pub state: String,
}

#[derive(Debug, Deserialize)]
pub struct Service {
    pub name: String,
    pub product: Option<String>,
    pub version: Option<String>,
    pub extrainfo: Option<String>,
}

pub fn parse_nmap_xml(file_path: &str) -> Result<SOSM, Box<dyn std::error::Error>> {
    let xml_data = fs::read_to_string(file_path)?;
    let nmap_run: NmapRun = quick_xml::de::from_str(&xml_data)?;

    let mut sosm = SOSM {
        hosts: Vec::new(),
        services: Vec::new(),
        endpoints: Vec::new(),
        observations: Vec::new(),
        vulnerabilities: Vec::new(),
        hypotheses: Vec::new(),
    };

    for nmap_host in nmap_run.hosts {
        // Map Host
        let primary_hostname = nmap_host.hostnames
            .and_then(|h| h.hostnames.first().map(|hn| hn.name.clone()));

        let sosm_host = Host {
            ip: nmap_host.address.addr.clone(),
            hostname: primary_hostname,
            os: None, // Nmap OS scanning can be added later
            status: nmap_host.status.state,
        };
        sosm.hosts.push(sosm_host);

        // Map Ports and Services
        if let Some(ports) = nmap_host.ports {
            for nmap_port in ports.ports {
                let sosm_port = SosmPort {
                    number: nmap_port.portid,
                    protocol: nmap_port.protocol.clone(),
                    state: nmap_port.state.state,
                };

                if let Some(nmap_service) = nmap_port.service {
                    let sosm_service = SosmService {
                        port: sosm_port.clone(),
                        name: nmap_service.name,
                        product: nmap_service.product,
                        version: nmap_service.version,
                        extra_info: nmap_service.extrainfo,
                    };
                    sosm.services.push(sosm_service);
                }
            }
        }
    }

    Ok(sosm)
}
