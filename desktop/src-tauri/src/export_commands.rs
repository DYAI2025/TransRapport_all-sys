use tauri::State;
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct ReportTemplate {
    pub id: String,
    pub name: String,
    pub template_type: String, // "therapy", "legal", "business"
    pub description: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ExportOptions {
    pub format: String, // "pdf", "docx", "txt", "csv", "json"
    pub include_markers: bool,
    pub include_rapport: bool,
    pub include_transcript: bool,
    pub confidentiality_level: String,
}

#[tauri::command]
pub async fn generate_report(
    session_id: String,
    template_id: String,
    export_options: ExportOptions
) -> Result<String, String> {
    // TODO: Implement professional report generation
    log::info!("Generating report for session: {} with template: {}", 
               session_id, template_id);
    
    // TODO: Use template engine to generate report
    let output_path = format!("/tmp/report_{}_{}.{}", 
                             session_id, template_id, export_options.format);
    
    Ok(output_path)
}

#[tauri::command]
pub async fn export_transcript(
    session_id: String,
    format: String, // "txt", "srt", "vtt", "json"
    include_speakers: bool
) -> Result<String, String> {
    // TODO: Implement transcript export in various formats
    log::info!("Exporting transcript for session: {} in format: {}", 
               session_id, format);
    
    let output_path = format!("/tmp/transcript_{}.{}", session_id, format);
    
    Ok(output_path)
}

#[tauri::command]
pub async fn export_markers(
    session_id: String,
    format: String, // "csv", "json", "jsonl"
    marker_types: Vec<String> // Filter by marker types
) -> Result<String, String> {
    // TODO: Implement marker events export
    log::info!("Exporting markers for session: {} in format: {} with types: {:?}", 
               session_id, format, marker_types);
    
    let output_path = format!("/tmp/markers_{}.{}", session_id, format);
    
    Ok(output_path)
}