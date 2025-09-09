use tauri::State;
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct TranscriptionProgress {
    pub session_id: String,
    pub progress: f64, // 0.0 to 1.0
    pub current_stage: String,
    pub estimated_remaining: Option<u64>, // seconds
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SpeakerSegment {
    pub speaker_id: String,
    pub speaker_label: String,
    pub start_time: f64,
    pub end_time: f64,
    pub text: String,
    pub confidence: f64,
}

#[tauri::command]
pub async fn start_transcription(
    audio_file_path: String,
    language: Option<String>,
    model_size: Option<String>
) -> Result<String, String> {
    // TODO: Implement Whisper transcription start
    log::info!("Starting transcription for: {} with language: {:?}", 
               audio_file_path, language);
    
    let session_id = uuid::Uuid::new_v4().to_string();
    
    // TODO: Start background transcription process with WhisperX
    Ok(session_id)
}

#[tauri::command]
pub async fn get_transcription_progress(session_id: String) -> Result<TranscriptionProgress, String> {
    // TODO: Implement transcription progress tracking
    log::info!("Getting transcription progress for session: {}", session_id);
    
    Ok(TranscriptionProgress {
        session_id: session_id.clone(),
        progress: 0.75, // Mock progress
        current_stage: "Speaker diarization".to_string(),
        estimated_remaining: Some(30),
    })
}

#[tauri::command]
pub async fn update_speaker_labels(
    session_id: String,
    speaker_mappings: Vec<(String, String)> // (speaker_id, new_label)
) -> Result<String, String> {
    // TODO: Implement speaker label updates
    log::info!("Updating speaker labels for session: {}", session_id);
    
    for (speaker_id, new_label) in speaker_mappings {
        log::info!("Mapping speaker {} to label: {}", speaker_id, new_label);
    }
    
    Ok("Speaker labels updated successfully".to_string())
}