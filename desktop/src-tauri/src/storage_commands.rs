use tauri::State;
use serde::{Deserialize, Serialize};
use sqlx::{SqlitePool, Row};
use chrono::{DateTime, Utc};

#[derive(Debug, Serialize, Deserialize)]
pub struct ConversationSession {
    pub id: String,
    pub name: String,
    pub session_type: String, // "therapy", "legal", "business"
    pub client_reference: Option<String>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
    pub status: String, // "recording", "transcribing", "analyzing", "completed"
    pub duration: Option<f64>,
    pub file_path: Option<String>,
}

pub async fn initialize_database() -> Result<(), Box<dyn std::error::Error>> {
    // TODO: Initialize SQLCipher database with encryption
    log::info!("Initializing encrypted database");
    
    // For now, use SQLite without encryption - will be upgraded to SQLCipher
    let database_url = "sqlite:transrapport.db";
    let pool = SqlitePool::connect(database_url).await?;
    
    // Create tables
    sqlx::query(
        r#"
        CREATE TABLE IF NOT EXISTS conversation_sessions (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            session_type TEXT NOT NULL,
            client_reference TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'created',
            duration REAL,
            file_path TEXT
        )
        "#,
    )
    .execute(&pool)
    .await?;
    
    log::info!("Database initialized successfully");
    Ok(())
}

#[tauri::command]
pub async fn create_session(
    name: String,
    session_type: String,
    client_reference: Option<String>
) -> Result<ConversationSession, String> {
    // TODO: Implement session creation with database storage
    log::info!("Creating new session: {} of type: {}", name, session_type);
    
    let session = ConversationSession {
        id: uuid::Uuid::new_v4().to_string(),
        name,
        session_type,
        client_reference,
        created_at: Utc::now(),
        updated_at: Utc::now(),
        status: "created".to_string(),
        duration: None,
        file_path: None,
    };
    
    Ok(session)
}

#[tauri::command]
pub async fn get_sessions(limit: Option<u32>) -> Result<Vec<ConversationSession>, String> {
    // TODO: Implement session retrieval from database
    log::info!("Retrieving sessions with limit: {:?}", limit);
    
    // Mock data for now
    Ok(vec![
        ConversationSession {
            id: "session-1".to_string(),
            name: "Client A - Therapy Session".to_string(),
            session_type: "therapy".to_string(),
            client_reference: Some("CLIENT-001-2025".to_string()),
            created_at: Utc::now(),
            updated_at: Utc::now(),
            status: "completed".to_string(),
            duration: Some(3600.0),
            file_path: Some("/tmp/session1.wav".to_string()),
        }
    ])
}

#[tauri::command]
pub async fn save_transcript(
    session_id: String,
    segments: Vec<crate::transcription_commands::SpeakerSegment>
) -> Result<String, String> {
    // TODO: Implement transcript saving to encrypted database
    log::info!("Saving transcript for session: {} with {} segments", 
               session_id, segments.len());
    
    Ok("Transcript saved successfully".to_string())
}

#[tauri::command]
pub async fn load_session(session_id: String) -> Result<ConversationSession, String> {
    // TODO: Implement session loading from database
    log::info!("Loading session: {}", session_id);
    
    // Mock session for now
    Ok(ConversationSession {
        id: session_id.clone(),
        name: "Loaded Session".to_string(),
        session_type: "therapy".to_string(),
        client_reference: None,
        created_at: Utc::now(),
        updated_at: Utc::now(),
        status: "completed".to_string(),
        duration: Some(1800.0),
        file_path: Some("/tmp/loaded_session.wav".to_string()),
    })
}