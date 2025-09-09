// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod audio_commands;
mod transcription_commands;
mod analysis_commands;
mod export_commands;
mod storage_commands;
mod python_integration;

use tauri::Manager;

fn main() {
    env_logger::init();
    
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_process::init())
        .invoke_handler(tauri::generate_handler![
            // Audio commands
            audio_commands::start_recording,
            audio_commands::stop_recording,
            audio_commands::import_audio_file,
            audio_commands::get_audio_devices,
            
            // Transcription commands
            transcription_commands::start_transcription,
            transcription_commands::get_transcription_progress,
            transcription_commands::update_speaker_labels,
            
            // Analysis commands
            analysis_commands::analyze_transcript,
            analysis_commands::get_analysis_progress,
            analysis_commands::calculate_rapport,
            
            // Export commands
            export_commands::generate_report,
            export_commands::export_transcript,
            export_commands::export_markers,
            
            // Storage commands
            storage_commands::create_session,
            storage_commands::get_sessions,
            storage_commands::save_transcript,
            storage_commands::load_session
        ])
        .setup(|app| {
            // Initialize database
            let app_handle = app.handle();
            tauri::async_runtime::spawn(async move {
                if let Err(e) = storage_commands::initialize_database().await {
                    log::error!("Failed to initialize database: {}", e);
                }
            });
            
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}