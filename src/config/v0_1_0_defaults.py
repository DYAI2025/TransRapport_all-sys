"""
v0.1.0-pilot Frozen Defaults
CONSTITUTIONAL COMPLIANCE: LD-3.4 framework locked for pilot release
NO MODIFICATIONS ALLOWED - Production ready defaults
"""

from dataclasses import dataclass
from typing import Dict, Any

# FROZEN v0.1.0 DEFAULTS - DO NOT MODIFY
V0_1_0_DEFAULTS = {
    # Core System
    "VERSION": "0.1.0-pilot",
    "CONSTITUTIONAL_FRAMEWORK": "LD-3.4",
    "ANALYSIS_METHOD": "LD-3.4", 
    "CONFIDENCE_THRESHOLD": 0.75,
    
    # Directories
    "DATABASE_PATH": "data/transrapport.db",
    "EXPORT_DIRECTORY": "exports",
    "TEMP_DIRECTORY": "temp",
    "SESSIONS_DIRECTORY": "sessions",
    
    # Constitutional Analysis - FROZEN
    "ENABLE_ATO": True,
    "ENABLE_SEM": True, 
    "ENABLE_CLU": True,
    "ENABLE_MEMA": True,
    "ENABLE_RAPPORT": True,
    
    # Analysis Windows - LOCKED FOR PILOT
    "DEFAULT_WINDOW_SEM": "ANY 2 IN 3",
    "DEFAULT_WINDOW_CLU": "AT_LEAST 1 IN 5",
    "MIN_DURATION_THRESHOLD": 1.5,
    
    # Audio Defaults
    "DEFAULT_AUDIO_FORMAT": "wav",
    "DEFAULT_SAMPLE_RATE": 16000,
    "DEFAULT_CHANNELS": 1,
    
    # Transcription Defaults
    "DEFAULT_WHISPER_MODEL": "base",
    "DEFAULT_LANGUAGE": "de",
    "OUTPUT_JSON": True,
    
    # Export Formats - PILOT READY
    "DEFAULT_TRANSCRIPT_FORMATS": ["annotated_txt", "json", "csv"],
    "DEFAULT_MARKER_FORMATS": ["json", "csv", "analytics"],
    "DEFAULT_REPORT_FORMAT": "pdf",
    
    # Logging
    "LOG_LEVEL": "INFO",
    "MAX_LOG_FILES": 10,
    "LOG_ROTATION_SIZE": "10MB",
    
    # Desktop UI
    "UI_THEME": "default",
    "UI_MAX_LOGS": 50,
    "UI_PROGRESS_UPDATE_MS": 200,
}

# FROZEN MARKER DEFINITIONS - v0.1.0 PILOT
FROZEN_MARKERS_V0_1_0 = {
    "ATO": {
        "description": "Autonomy markers - decision making freedom",
        "subtypes": ["question_open", "choice_offering", "permission_seeking"],
        "weight": 1.0,
        "enabled": True
    },
    "SEM": {
        "description": "Semantic markers - understanding validation", 
        "subtypes": ["empathy_expression", "validation", "understanding_check"],
        "weight": 1.0,
        "enabled": True
    },
    "CLU": {
        "description": "Clustering markers - connection building",
        "subtypes": ["shared_experience", "similarity_acknowledgment", "group_identity"],
        "weight": 1.0,
        "enabled": True
    },
    "MEMA": {
        "description": "Memory/mental model markers - cognitive alignment",
        "subtypes": ["reference_recall", "context_building", "assumption_check"],
        "weight": 1.0,
        "enabled": True
    }
}

@dataclass
class FrozenConfigV010:
    """FROZEN v0.1.0 configuration - DO NOT MODIFY"""
    
    def __init__(self):
        for key, value in V0_1_0_DEFAULTS.items():
            setattr(self, key.lower(), value)
    
    def get_markers(self) -> Dict[str, Any]:
        """Return frozen marker definitions"""
        return FROZEN_MARKERS_V0_1_0.copy()
    
    def get_version(self) -> str:
        """Return frozen version"""
        return V0_1_0_DEFAULTS["VERSION"]
    
    def is_frozen(self) -> bool:
        """Confirm this is a frozen configuration"""
        return True


def get_v010_config() -> FrozenConfigV010:
    """Get the frozen v0.1.0 configuration"""
    return FrozenConfigV010()


# Validation check
assert V0_1_0_DEFAULTS["VERSION"] == "0.1.0-pilot", "Version mismatch in frozen defaults"
assert V0_1_0_DEFAULTS["CONSTITUTIONAL_FRAMEWORK"] == "LD-3.4", "Constitutional framework mismatch"