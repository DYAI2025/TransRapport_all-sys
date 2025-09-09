# TransRapport v0.1.0-pilot Data Schema Documentation

🏛️ **Constitutional Framework: LD-3.4**  
📊 **Frozen Data Structures**  
🔒 **Production-Ready Schemas**

## 📋 Schema Overview

TransRapport v0.1.0-pilot uses **frozen** data schemas ensuring consistency across analysis sessions. All data structures are locked for the pilot release.

## 🎵 Audio Data Schema

### Audio Device Information
```json
{
  "devices": [
    {
      "id": "string",
      "name": "string", 
      "is_default": "boolean",
      "max_input_channels": "integer",
      "default_sample_rate": "integer"
    }
  ]
}
```

**Example:**
```json
{
  "devices": [
    {
      "id": "default",
      "name": "Default Audio Device",
      "is_default": true,
      "max_input_channels": 2,
      "default_sample_rate": 44100
    }
  ]
}
```

### Recording Session
```json
{
  "session_id": "string",
  "start_time": "ISO8601",
  "end_time": "ISO8601",
  "duration": "float (seconds)",
  "device": "string",
  "format": "string",
  "sample_rate": "integer",
  "channels": "integer",
  "file_path": "string"
}
```

## 📝 Transcription Schema

### Transcription Result
```json
{
  "text": "string",
  "language": "string",
  "duration": "float (seconds)",
  "model": "string",
  "confidence": "float (0.0-1.0)",
  "segments": [
    {
      "id": "string",
      "start": "float (seconds)",
      "end": "float (seconds)", 
      "text": "string",
      "confidence": "float (0.0-1.0)"
    }
  ],
  "metadata": {
    "whisper_version": "string",
    "model_size": "string",
    "processing_time": "float (seconds)"
  }
}
```

**Example:**
```json
{
  "text": "Hello, how are you today? I'm doing well, thank you for asking.",
  "language": "en",
  "duration": 5.2,
  "model": "base",
  "confidence": 0.95,
  "segments": [
    {
      "id": "1",
      "start": 0.0,
      "end": 2.1,
      "text": "Hello, how are you today?",
      "confidence": 0.98
    },
    {
      "id": "2", 
      "start": 2.1,
      "end": 5.2,
      "text": "I'm doing well, thank you for asking.",
      "confidence": 0.92
    }
  ],
  "metadata": {
    "whisper_version": "1.0",
    "model_size": "base",
    "processing_time": 3.7
  }
}
```

## 👥 Diarization Schema

### Speaker Diarization Result
```json
{
  "speakers": [
    {
      "id": "string",
      "label": "string",
      "speaking_time": "float (seconds)",
      "segment_count": "integer",
      "average_confidence": "float (0.0-1.0)"
    }
  ],
  "segments": [
    {
      "id": "string",
      "start": "float (seconds)",
      "end": "float (seconds)",
      "speaker": "string",
      "text": "string",
      "confidence": "float (0.0-1.0)",
      "duration": "float (seconds)"
    }
  ],
  "diarization_info": {
    "model": "string",
    "min_duration": "float (seconds)",
    "total_speakers": "integer",
    "processing_time": "float (seconds)"
  }
}
```

**Example:**
```json
{
  "speakers": [
    {
      "id": "SPEAKER_00",
      "label": "Speaker A",
      "speaking_time": 45.2,
      "segment_count": 8,
      "average_confidence": 0.89
    },
    {
      "id": "SPEAKER_01", 
      "label": "Speaker B",
      "speaking_time": 38.7,
      "segment_count": 6,
      "average_confidence": 0.92
    }
  ],
  "segments": [
    {
      "id": "1",
      "start": 0.0,
      "end": 2.1,
      "speaker": "SPEAKER_00",
      "text": "Hello, how are you today?",
      "confidence": 0.95,
      "duration": 2.1
    }
  ],
  "diarization_info": {
    "model": "pyannote",
    "min_duration": 1.5,
    "total_speakers": 2,
    "processing_time": 12.3
  }
}
```

## 🏛️ Constitutional Analysis Schema (LD-3.4)

### Analysis Event (Core Structure)
```json
{
  "id": "string (UUID)",
  "marker_type": "string (ATO|SEM|CLU|MEMA)",
  "marker_subtype": "string",
  "start_time": "float (seconds)",
  "end_time": "float (seconds)",
  "confidence": "float (0.0-1.0)",
  "evidence": "string",
  "speaker": "string",
  "context": {
    "surrounding_text": "string",
    "segment_count": "integer",
    "window_applied": "string"
  },
  "constitutional_metadata": {
    "framework_version": "string (LD-3.4)",
    "analysis_version": "string (v0.1.0-pilot)",
    "timestamp": "ISO8601"
  }
}
```

### ATO (Autonomy) Markers
```json
{
  "marker_type": "ATO",
  "marker_subtype": "question_open|choice_offering|permission_seeking",
  "evidence": "string (detected pattern)",
  "constitutional_significance": "string"
}
```

### SEM (Semantic) Markers  
```json
{
  "marker_type": "SEM",
  "marker_subtype": "empathy_expression|validation|understanding_check",
  "evidence": "string (semantic pattern)",
  "understanding_depth": "float (0.0-1.0)"
}
```

### CLU (Clustering) Markers
```json
{
  "marker_type": "CLU", 
  "marker_subtype": "shared_experience|similarity_acknowledgment|group_identity",
  "evidence": "string (connection pattern)",
  "connection_strength": "float (0.0-1.0)"
}
```

### MEMA (Memory/Mental Model) Markers
```json
{
  "marker_type": "MEMA",
  "marker_subtype": "reference_recall|context_building|assumption_check", 
  "evidence": "string (cognitive pattern)",
  "cognitive_load": "float (0.0-1.0)"
}
```

### Complete Analysis Result
```json
{
  "analysis_id": "string (UUID)",
  "session_id": "string",
  "constitutional_framework": "LD-3.4",
  "analysis_version": "v0.1.0-pilot",
  "timestamp": "ISO8601",
  "configuration": {
    "confidence_threshold": 0.75,
    "window_sem": "ANY 2 IN 3",
    "window_clu": "AT_LEAST 1 IN 5",
    "min_duration": 1.5
  },
  "events": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "marker_type": "ATO",
      "marker_subtype": "question_open", 
      "start_time": 12.3,
      "end_time": 15.8,
      "confidence": 0.87,
      "evidence": "Open-ended question detected: 'What do you think about...'",
      "speaker": "SPEAKER_00",
      "context": {
        "surrounding_text": "So what do you think about the proposal we discussed?",
        "segment_count": 3,
        "window_applied": "ANY 2 IN 3"
      },
      "constitutional_metadata": {
        "framework_version": "LD-3.4",
        "analysis_version": "v0.1.0-pilot",
        "timestamp": "2025-09-09T20:15:30Z"
      }
    }
  ],
  "summary": {
    "total_events": "integer",
    "events_by_type": {
      "ATO": "integer",
      "SEM": "integer", 
      "CLU": "integer",
      "MEMA": "integer"
    },
    "constitutional_score": "float (0.0-1.0)",
    "processing_time": "float (seconds)"
  }
}
```

## 📊 Session Management Schema

### Session Information
```json
{
  "id": "string",
  "name": "string", 
  "status": "idle|recording|processing|completed",
  "created": "ISO8601",
  "updated": "ISO8601",
  "duration": "float (seconds)",
  "files": {
    "raw_audio": "string (path)",
    "transcript": "string (path)", 
    "diarization": "string (path)",
    "analysis": "string (path)"
  },
  "metadata": {
    "version": "v0.1.0-pilot",
    "constitutional_framework": "LD-3.4",
    "privacy_mode": "offline-only"
  }
}
```

## 📤 Export Schemas

### PDF Report Schema
```json
{
  "export_type": "report",
  "format": "pdf",
  "session_id": "string",
  "generated": "ISO8601",
  "sections": [
    "executive_summary",
    "constitutional_analysis", 
    "speaker_dynamics",
    "temporal_patterns",
    "recommendations"
  ],
  "output_path": "string",
  "file_size": "integer (bytes)"
}
```

### CSV Export Schema
```json
{
  "export_type": "data",
  "format": "csv", 
  "session_id": "string",
  "generated": "ISO8601",
  "files": {
    "events.csv": "string (path)",
    "speakers.csv": "string (path)", 
    "segments.csv": "string (path)",
    "summary.csv": "string (path)"
  },
  "total_records": "integer"
}
```

## 🔒 Configuration Schema (FROZEN v0.1.0)

### System Configuration
```json
{
  "version": "0.1.0-pilot",
  "constitutional_framework": "LD-3.4",
  "analysis_method": "LD-3.4",
  "frozen": true,
  "defaults": {
    "confidence_threshold": 0.75,
    "default_window_sem": "ANY 2 IN 3",
    "default_window_clu": "AT_LEAST 1 IN 5", 
    "min_duration_threshold": 1.5,
    "default_whisper_model": "base",
    "default_language": "de",
    "default_audio_format": "wav",
    "default_sample_rate": 16000,
    "default_report_format": "pdf"
  },
  "markers": {
    "ATO": {
      "enabled": true,
      "subtypes": ["question_open", "choice_offering", "permission_seeking"],
      "weight": 1.0
    },
    "SEM": {
      "enabled": true,
      "subtypes": ["empathy_expression", "validation", "understanding_check"],
      "weight": 1.0
    },
    "CLU": {
      "enabled": true,
      "subtypes": ["shared_experience", "similarity_acknowledgment", "group_identity"],
      "weight": 1.0
    },
    "MEMA": {
      "enabled": true,
      "subtypes": ["reference_recall", "context_building", "assumption_check"],
      "weight": 1.0
    }
  }
}
```

## 🔄 Schema Validation

### JSON Schema Validation
All schemas are validated using JSON Schema Draft-07:

```bash
# Validate transcription output
python3 -c "
import json, jsonschema
# Load schema and validate
"
```

### Required Fields Validation
- All `*_time` fields must be non-negative floats
- All `confidence` fields must be between 0.0 and 1.0
- All `id` fields must be non-empty strings
- Constitutional markers must match frozen v0.1.0 specification

## 📝 Schema Evolution

### v0.1.0-pilot Constraints
- ❌ **No schema modifications** - All structures are frozen
- ❌ **No new marker types** - ATO/SEM/CLU/MEMA only
- ❌ **No configuration changes** - Settings locked
- ✅ **Forward compatibility** - Future versions will read v0.1.0 data

### Future Considerations
- Additional constitutional markers (post-pilot)
- Enhanced metadata fields
- Improved validation rules
- Extended export formats

---

**All schemas are frozen for TransRapport v0.1.0-pilot to ensure consistency and reliability during the pilot phase.**