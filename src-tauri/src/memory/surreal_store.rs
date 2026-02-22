use surrealdb::engine::any::{connect, Any};
use surrealdb::Surreal;
use std::sync::Arc;
use crate::normalization::sosm::{Host, Service, Endpoint, Observation, Vulnerability, Hypothesis, SOSM};

pub struct MemoryStore {
    db: Arc<Surreal<Any>>,
}

impl MemoryStore {
    pub async fn new() -> Result<Self, surrealdb::Error> {
        let db = connect("mem://").await?;
        db.use_ns("kalpai").use_db("cognitive_memory").await?;
        
        Ok(Self { db: Arc::new(db) })
    }

    pub async fn ingest_sosm(&self, sosm: SOSM) -> Result<(), surrealdb::Error> {
        for host in sosm.hosts {
            // Using insert for specific table names instead of create for generic types
            let _: Option<Host> = self.db.insert("host").content(host).await?.into_iter().next();
        }

        for service in sosm.services {
            let _: Option<Service> = self.db.insert("service").content(service).await?.into_iter().next();
        }

        for endpoint in sosm.endpoints {
            let _: Option<Endpoint> = self.db.insert("endpoint").content(endpoint).await?.into_iter().next();
        }

        for observation in sosm.observations {
            let _: Option<Observation> = self.db.insert("observation").content(observation).await?.into_iter().next();
        }

        for vuln in sosm.vulnerabilities {
            let _: Option<Vulnerability> = self.db.insert("vulnerability").content(vuln).await?.into_iter().next();
        }

        for hypothesis in sosm.hypotheses {
            let _: Option<Hypothesis> = self.db.insert("hypothesis").content(hypothesis).await?.into_iter().next();
        }

        Ok(())
    }
}


