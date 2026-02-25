use surrealdb::engine::local::{Db, Mem};
use surrealdb::Surreal;
use std::sync::Arc;
use tokio::sync::Mutex;

use crate::normalization::sosm::{Host, Observation, Hypothesis, Endpoint, Vulnerability};

pub struct SurrealMemoryStore {
    db: Surreal<Db>,
}

impl SurrealMemoryStore {
    pub async fn new() -> Result<Self, surrealdb::Error> {
        // Initialize an in-memory database instance
        let db = Surreal::new::<Mem>(()).await?;
        db.use_ns("kalpai").use_db("memory").await?;
        Ok(Self { db })
    }

    /// Insert a Host into the operational memory
    pub async fn insert_host(&self, host: &Host) -> Result<(), surrealdb::Error> {
        let _: Option<Host> = self.db.create(("host", host.ip.clone())).content(host.clone()).await?;
        Ok(())
    }

    /// Insert an Observation into the environmental memory
    pub async fn insert_observation(&self, obs: &Observation) -> Result<(), surrealdb::Error> {
        let _: Option<Observation> = self.db.create("observation").content(obs.clone()).await?;
        Ok(())
    }

    /// Insert a Hypothesis
    pub async fn insert_hypothesis(&self, hypo: &Hypothesis) -> Result<(), surrealdb::Error> {
        let _: Option<Hypothesis> = self.db.create(("hypothesis", hypo.id.clone())).content(hypo.clone()).await?;
        Ok(())
    }

    /// Retrieve all Hosts in memory
    pub async fn get_hosts(&self) -> Result<Vec<Host>, surrealdb::Error> {
        let hosts: Vec<Host> = self.db.select("host").await?;
        Ok(hosts)
    }

    /// Retrieve all Observations
    pub async fn get_observations(&self) -> Result<Vec<Observation>, surrealdb::Error> {
        let obs: Vec<Observation> = self.db.select("observation").await?;
        Ok(obs)
    }

    /// Retrieve all Hypotheses
    pub async fn get_hypotheses(&self) -> Result<Vec<Hypothesis>, surrealdb::Error> {
        let hypos: Vec<Hypothesis> = self.db.select("hypothesis").await?;
        Ok(hypos)
    }

    /// Insert an Endpoint
    pub async fn insert_endpoint(&self, endpoint: &Endpoint) -> Result<(), surrealdb::Error> {
        let _: Option<Endpoint> = self.db.create("endpoint").content(endpoint.clone()).await?;
        Ok(())
    }

    /// Retrieve all Endpoints
    pub async fn get_endpoints(&self) -> Result<Vec<Endpoint>, surrealdb::Error> {
        let endpoints: Vec<Endpoint> = self.db.select("endpoint").await?;
        Ok(endpoints)
    }

    /// Insert a Vulnerability
    pub async fn insert_vulnerability(&self, vuln: &Vulnerability) -> Result<(), surrealdb::Error> {
        let _: Option<Vulnerability> = self.db.create(("vulnerability", vuln.id.clone())).content(vuln.clone()).await?;
        Ok(())
    }

    /// Retrieve all Vulnerabilities
    pub async fn get_vulnerabilities(&self) -> Result<Vec<Vulnerability>, surrealdb::Error> {
        let vulns: Vec<Vulnerability> = self.db.select("vulnerability").await?;
        Ok(vulns)
    }
}

pub type SharedMemoryStore = Arc<Mutex<SurrealMemoryStore>>;

pub async fn init_shared_store() -> Result<SharedMemoryStore, surrealdb::Error> {
    let store = SurrealMemoryStore::new().await?;
    Ok(Arc::new(Mutex::new(store)))
}
