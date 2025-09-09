use tauri::State;
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct MarkerEvent {
    pub id: String,
    pub marker_type: String, // ATO, SEM, CLU, MEMA
    pub start_time: f64,
    pub end_time: f64,
    pub confidence: f64,
    pub evidence: String,
    pub explanation: String,
    pub speaker: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct RapportIndicator {
    pub timestamp: f64,
    pub value: f64, // -1.0 to 1.0
    pub trend: String, // "increasing", "decreasing", "stable"
    pub contributing_markers: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct AnalysisProgress {
    pub session_id: String,
    pub progress: f64,
    pub current_stage: String, // "ATO", "SEM", "CLU", "MEMA", "Rapport"
    pub markers_detected: u32,
}

#[tauri::command]
pub async fn analyze_transcript(
    session_id: String,
    transcript_segments: Vec<crate::transcription_commands::SpeakerSegment>
) -> Result<String, String> {
    // TODO: Implement LD-3.4 marker analysis pipeline
    log::info!("Starting LD-3.4 analysis for session: {}", session_id);
    
    // TODO: Call Python integration for marker analysis
    // This will use the existing LD-3.4 pipeline via library reuse
    
    Ok("Analysis started successfully".to_string())
}

#[tauri::command]
pub async fn get_analysis_progress(session_id: String) -> Result<AnalysisProgress, String> {
    // TODO: Implement analysis progress tracking
    log::info!("Getting analysis progress for session: {}", session_id);
    
    Ok(AnalysisProgress {
        session_id: session_id.clone(),
        progress: 0.60,
        current_stage: "CLU".to_string(),
        markers_detected: 15,
    })
}

#[tauri::command]
pub async fn calculate_rapport(
    session_id: String,
    markers: Vec<MarkerEvent>
) -> Result<Vec<RapportIndicator>, String> {
    // TODO: Implement rapport calculation from marker patterns
    log::info!("Calculating rapport indicators for session: {}", session_id);
    
    // Mock rapport calculation
    Ok(vec![
        RapportIndicator {
            timestamp: 60.0,
            value: 0.7,
            trend: "increasing".to_string(),
            contributing_markers: vec!["ATO_001".to_string(), "SEM_003".to_string()],
        },
        RapportIndicator {
            timestamp: 120.0,
            value: 0.8,
            trend: "stable".to_string(),
            contributing_markers: vec!["CLU_002".to_string()],
        },
    ])
}