use tauri::State;
use serde::{Deserialize, Serialize};
use std::process::{Command, Stdio};
use std::io::{BufRead, BufReader};

#[derive(Debug, Serialize, Deserialize)]
pub struct PythonCommand {
    pub script_path: String,
    pub args: Vec<String>,
    pub working_dir: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct PythonResult {
    pub success: bool,
    pub stdout: String,
    pub stderr: String,
    pub exit_code: Option<i32>,
}

/// Execute Python script for ASR and analysis integration
pub async fn execute_python_script(
    script_path: &str,
    args: Vec<String>
) -> Result<PythonResult, String> {
    log::info!("Executing Python script: {} with args: {:?}", script_path, args);
    
    let mut cmd = Command::new("python3")
        .arg(script_path)
        .args(&args)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| format!("Failed to spawn Python process: {}", e))?;
    
    let output = cmd.wait_with_output()
        .map_err(|e| format!("Failed to read Python output: {}", e))?;
    
    Ok(PythonResult {
        success: output.status.success(),
        stdout: String::from_utf8_lossy(&output.stdout).to_string(),
        stderr: String::from_utf8_lossy(&output.stderr).to_string(),
        exit_code: output.status.code(),
    })
}

/// Start WhisperX transcription process
pub async fn start_whisperx_transcription(
    audio_file: &str,
    language: Option<&str>,
    model_size: Option<&str>
) -> Result<String, String> {
    let mut args = vec![
        "--audio".to_string(),
        audio_file.to_string(),
        "--output_dir".to_string(),
        "/tmp/transcription".to_string(),
    ];
    
    if let Some(lang) = language {
        args.extend(vec!["--language".to_string(), lang.to_string()]);
    }
    
    if let Some(model) = model_size {
        args.extend(vec!["--model".to_string(), model.to_string()]);
    }
    
    let result = execute_python_script("src/lib/transcription/whisperx_cli.py", args).await?;
    
    if result.success {
        Ok(result.stdout)
    } else {
        Err(format!("WhisperX failed: {}", result.stderr))
    }
}

/// Execute LD-3.4 marker analysis
pub async fn analyze_markers(
    transcript_file: &str,
    session_id: &str
) -> Result<String, String> {
    let args = vec![
        "--transcript".to_string(),
        transcript_file.to_string(),
        "--session_id".to_string(),
        session_id.to_string(),
        "--output_format".to_string(),
        "json".to_string(),
    ];
    
    let result = execute_python_script("src/lib/analysis/marker_analysis_cli.py", args).await?;
    
    if result.success {
        Ok(result.stdout)
    } else {
        Err(format!("Marker analysis failed: {}", result.stderr))
    }
}

/// Calculate rapport indicators from markers
pub async fn calculate_rapport_indicators(
    markers_file: &str,
    session_id: &str
) -> Result<String, String> {
    let args = vec![
        "--markers".to_string(),
        markers_file.to_string(),
        "--session_id".to_string(),
        session_id.to_string(),
    ];
    
    let result = execute_python_script("src/lib/analysis/rapport_calculation_cli.py", args).await?;
    
    if result.success {
        Ok(result.stdout)
    } else {
        Err(format!("Rapport calculation failed: {}", result.stderr))
    }
}