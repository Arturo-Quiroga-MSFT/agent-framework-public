use serde::{Deserialize, Serialize};
use std::sync::Mutex;
use tauri::State;
use crate::python_bridge;

// Application state
pub struct AppState {
    pub is_connected: Mutex<bool>,
    pub server_name: Mutex<Option<String>>,
    pub database_name: Mutex<Option<String>>,
    pub conversation_history: Mutex<Vec<(String, String)>>, // (user_query, assistant_response)
}

impl Default for AppState {
    fn default() -> Self {
        Self {
            is_connected: Mutex::new(false),
            server_name: Mutex::new(None),
            database_name: Mutex::new(None),
            conversation_history: Mutex::new(Vec::new()),
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
pub async fn run_dba_query(query: String, state: State<'_, AppState>) -> Result<QueryResult, String> {
    let start = std::time::Instant::now();
    
    // Get conversation history
    let history = state.conversation_history.lock().unwrap().clone();
    
    // Call Python bridge with history
    let result = match python_bridge::run_python_query_with_history(query.clone(), history) {
        Ok(response) => response,
        Err(e) => return Err(format!("Python error: {}", e)),
    };
    
    // Save to conversation history
    state.conversation_history.lock().unwrap().push((query, result.clone()));
    
    let elapsed = start.elapsed().as_millis() as u64;
    
    Ok(QueryResult {
        success: true,
        message: "Query executed successfully".to_string(),
        data: Some(result),
        execution_time_ms: elapsed,
    })
}

#[tauri::command]
pub fn clear_conversation(state: State<'_, AppState>) -> String {
    state.conversation_history.lock().unwrap().clear();
    "Conversation cleared".to_string()
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
