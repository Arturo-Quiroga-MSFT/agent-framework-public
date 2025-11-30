// Prevents additional console window on Windows in release
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod commands;
mod python_bridge;

use tauri::Manager;

fn main() {
    // Initialize Python environment on startup
    if let Err(e) = python_bridge::initialize_python() {
        eprintln!("Failed to initialize Python: {}", e);
    }
    
    tauri::Builder::default()
        .manage(commands::AppState::default())
        .setup(|app| {
            #[cfg(debug_assertions)]
            {
                let window = app.get_webview_window("main").unwrap();
                window.open_devtools();
            }
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
