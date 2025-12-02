// Prevents additional console window on Windows in release
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod commands;
mod python_bridge;

fn main() {
    // Load .env file from DBMS-ASSISTANT directory
    let mut env_path = std::path::PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    env_path.pop(); // Remove "src-tauri"
    env_path.pop(); // Remove "UI"
    env_path.push(".env");
    
    if env_path.exists() {
        let _ = dotenvy::from_path(&env_path);
    }
    
    // Initialize Python environment on startup
    let _ = python_bridge::initialize_python();
    
    tauri::Builder::default()
        .manage(commands::AppState::default())
        .setup(|_app| {
            // DevTools can be opened manually with Cmd+Shift+I if needed
            Ok(())
        })
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .invoke_handler(tauri::generate_handler![
            commands::greet,
            commands::run_dba_query,
            commands::connect_database,
            commands::get_connection_status,
            commands::clear_conversation,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
