use serde::{Deserialize, Serialize};
use std::sync::Mutex;
use tauri::State;

// Application state
pub struct AppState {
    pub is_connected: Mutex<bool>,
    pub server_name: Mutex<Option<String>>,
    pub database_name: Mutex<Option<String>>,
}

impl Default for AppState {
    fn default() -> Self {
        Self {
            is_connected: Mutex::new(false),
            server_name: Mutex::new(None),
            database_name: Mutex::new(None),
        }
    }
}

// Data structures
#[derive(Debug, Serialize, Deserialize)]
pub struct ConnectionInfo {
    pub server: String,
    pub database: String,
    pub username: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct QueryResult {
    pub success: bool,
    pub message: String,
    pub data: Option<String>,
    pub execution_time_ms: u64,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ConnectionStatus {
    pub is_connected: bool,
    pub server: Option<String>,
    pub database: Option<String>,
}

// Tauri Commands

#[tauri::command]
pub fn greet(name: &str) -> String {
    format!("Hello, {}! Welcome to RDBMS Assistant.", name)
}

#[tauri::command]
pub async fn run_dba_query(query: String, _state: State<'_, AppState>) -> Result<QueryResult, String> {
    // TODO: Integrate with Python agent via python_bridge
    // For now, return a mock response
    
    let start = std::time::Instant::now();
    
    // Simulate processing time
    tokio::time::sleep(tokio::time::Duration::from_millis(500)).await;
    
    let elapsed = start.elapsed().as_millis() as u64;
    
    Ok(QueryResult {
        success: true,
        message: format!("Query processed successfully: {}", query),
        data: Some("Mock response - Python integration coming soon".to_string()),
        execution_time_ms: elapsed,
    })
}

#[tauri::command]
pub async fn connect_database(
    connection_info: ConnectionInfo,
    state: State<'_, AppState>,
) -> Result<String, String> {
    // TODO: Integrate with Python agent to establish connection
    
    // Update state
    *state.is_connected.lock().unwrap() = true;
    *state.server_name.lock().unwrap() = Some(connection_info.server.clone());
    *state.database_name.lock().unwrap() = Some(connection_info.database.clone());
    
    Ok(format!(
        "Connected to {}.{}",
        connection_info.server, connection_info.database
    ))
}

#[tauri::command]
pub fn get_connection_status(state: State<'_, AppState>) -> ConnectionStatus {
    ConnectionStatus {
        is_connected: *state.is_connected.lock().unwrap(),
        server: state.server_name.lock().unwrap().clone(),
        database: state.database_name.lock().unwrap().clone(),
    }
}
