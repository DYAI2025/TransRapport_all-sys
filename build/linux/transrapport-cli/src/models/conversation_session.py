"""
ConversationSession Data Model
Represents a transcription session with metadata and state tracking
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from enum import Enum
import uuid


class SessionStatus(Enum):
    """Session status enumeration"""
    CREATED = "created"
    RECORDING = "recording"
    TRANSCRIBING = "transcribing"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class SessionType(Enum):
    """Session type enumeration for professional contexts"""
    THERAPY = "therapy"
    LEGAL = "legal"
    BUSINESS = "business"
    CONSULTATION = "consultation"
    OTHER = "other"


@dataclass
class ConversationSession:
    """
    Core data model for conversation sessions
    
    Represents a complete transcription session with metadata,
    tracking state, and professional context information.
    """
    
    # Required fields
    name: str
    session_type: SessionType
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Optional identification
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    client_reference: Optional[str] = None
    
    # Timestamps
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Session state
    status: SessionStatus = SessionStatus.CREATED
    
    # File and duration information
    audio_file_path: Optional[str] = None
    duration: Optional[float] = None  # Duration in seconds
    file_size: Optional[int] = None   # File size in bytes
    
    # Audio technical details
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    audio_format: Optional[str] = None
    
    # Professional context
    participant_count: Optional[int] = None
    privacy_level: str = "standard"  # "standard", "confidential", "privileged"
    consent_given: bool = False
    
    # Processing information
    transcription_model: Optional[str] = None
    language: Optional[str] = None
    processing_options: Dict[str, Any] = field(default_factory=dict)
    
    # Analysis results
    transcript_available: bool = False
    analysis_available: bool = False
    markers_count: int = 0
    rapport_calculated: bool = False
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    custom_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization validation and setup"""
        # Validate required fields
        if not self.name or not self.name.strip():
            raise ValueError("Session name cannot be empty")
        
        # Ensure session_type is SessionType enum
        if isinstance(self.session_type, str):
            try:
                self.session_type = SessionType(self.session_type.lower())
            except ValueError:
                raise ValueError(f"Invalid session type: {self.session_type}")
        
        # Ensure status is SessionStatus enum
        if isinstance(self.status, str):
            try:
                self.status = SessionStatus(self.status.lower())
            except ValueError:
                raise ValueError(f"Invalid session status: {self.status}")
        
        # Validate privacy level
        if self.privacy_level not in ["standard", "confidential", "privileged"]:
            raise ValueError(f"Invalid privacy level: {self.privacy_level}")
        
        # Validate duration if provided
        if self.duration is not None and self.duration < 0:
            raise ValueError("Duration cannot be negative")
        
        # Validate participant count
        if self.participant_count is not None and self.participant_count < 1:
            raise ValueError("Participant count must be at least 1")
    
    def start_session(self) -> None:
        """Mark session as started"""
        if self.status != SessionStatus.CREATED:
            raise ValueError(f"Cannot start session in status: {self.status}")
        
        self.status = SessionStatus.RECORDING
        self.started_at = datetime.now(timezone.utc)
        self.updated_at = self.started_at
    
    def complete_session(self) -> None:
        """Mark session as completed"""
        if self.status == SessionStatus.COMPLETED:
            return  # Already completed
        
        self.status = SessionStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc)
        self.updated_at = self.completed_at
    
    def fail_session(self, reason: str = "") -> None:
        """Mark session as failed"""
        self.status = SessionStatus.FAILED
        self.updated_at = datetime.now(timezone.utc)
        if reason:
            self.notes = f"Failed: {reason}\n{self.notes}".strip()
    
    def update_status(self, new_status: SessionStatus) -> None:
        """Update session status with validation"""
        if isinstance(new_status, str):
            new_status = SessionStatus(new_status.lower())
        
        # Validate status transitions
        valid_transitions = {
            SessionStatus.CREATED: [SessionStatus.RECORDING, SessionStatus.FAILED],
            SessionStatus.RECORDING: [SessionStatus.TRANSCRIBING, SessionStatus.COMPLETED, SessionStatus.FAILED],
            SessionStatus.TRANSCRIBING: [SessionStatus.ANALYZING, SessionStatus.COMPLETED, SessionStatus.FAILED],
            SessionStatus.ANALYZING: [SessionStatus.COMPLETED, SessionStatus.FAILED],
            SessionStatus.COMPLETED: [],  # Terminal state
            SessionStatus.FAILED: [SessionStatus.CREATED]  # Can retry
        }
        
        if new_status not in valid_transitions[self.status]:
            raise ValueError(f"Invalid status transition from {self.status} to {new_status}")
        
        self.status = new_status
        self.updated_at = datetime.now(timezone.utc)
        
        # Set completion timestamp
        if new_status == SessionStatus.COMPLETED:
            self.completed_at = self.updated_at
    
    def set_audio_info(self, file_path: str, duration: float, 
                      sample_rate: int = None, channels: int = None,
                      file_format: str = None, file_size: int = None) -> None:
        """Set audio file information"""
        self.audio_file_path = file_path
        self.duration = duration
        self.sample_rate = sample_rate
        self.channels = channels
        self.audio_format = file_format
        self.file_size = file_size
        self.updated_at = datetime.now(timezone.utc)
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the session"""
        tag = tag.strip().lower()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now(timezone.utc)
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the session"""
        tag = tag.strip().lower()
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now(timezone.utc)
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of the session"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.session_type.value,
            'status': self.status.value,
            'duration': self.duration,
            'created_at': self.created_at.isoformat(),
            'privacy_level': self.privacy_level,
            'has_transcript': self.transcript_available,
            'has_analysis': self.analysis_available,
            'markers_count': self.markers_count,
            'participant_count': self.participant_count,
            'tags': self.tags
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for serialization"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, (SessionStatus, SessionType)):
                result[key] = value.value
            else:
                result[key] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationSession':
        """Create session from dictionary"""
        # Convert datetime fields
        datetime_fields = ['created_at', 'updated_at', 'started_at', 'completed_at']
        for field in datetime_fields:
            if field in data and data[field]:
                if isinstance(data[field], str):
                    data[field] = datetime.fromisoformat(data[field])
        
        # Convert enum fields
        if 'session_type' in data and isinstance(data['session_type'], str):
            data['session_type'] = SessionType(data['session_type'])
        
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = SessionStatus(data['status'])
        
        return cls(**data)
    
    def is_active(self) -> bool:
        """Check if session is currently active (recording or processing)"""
        return self.status in [SessionStatus.RECORDING, SessionStatus.TRANSCRIBING, SessionStatus.ANALYZING]
    
    def get_elapsed_time(self) -> Optional[float]:
        """Get elapsed time since session started (in seconds)"""
        if not self.started_at:
            return None
        
        end_time = self.completed_at or datetime.now(timezone.utc)
        return (end_time - self.started_at).total_seconds()
    
    def requires_consent_verification(self) -> bool:
        """Check if session requires explicit consent verification"""
        return (
            self.privacy_level in ["confidential", "privileged"] or
            self.session_type in [SessionType.THERAPY, SessionType.LEGAL] or
            not self.consent_given
        )