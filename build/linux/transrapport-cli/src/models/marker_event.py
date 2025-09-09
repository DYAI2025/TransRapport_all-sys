"""
MarkerEvent Data Model
Represents LD-3.4 marker analysis results with evidence and confidence scoring
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from enum import Enum
import uuid


class MarkerType(Enum):
    """LD-3.4 marker types"""
    ATO = "ATO"  # Attention markers
    SEM = "SEM"  # Semantic markers  
    CLU = "CLU"  # Cluster markers
    MEMA = "MEMA"  # Memory markers


class MarkerConfidenceLevel(Enum):
    """Confidence level categories"""
    LOW = "low"         # 0.0 - 0.5
    MEDIUM = "medium"   # 0.5 - 0.7  
    HIGH = "high"       # 0.7 - 0.9
    VERY_HIGH = "very_high"  # 0.9 - 1.0


@dataclass
class MarkerEvent:
    """
    LD-3.4 marker event with evidence and analysis
    
    Represents a detected conversational marker with timing,
    confidence scoring, and supporting evidence from transcript.
    """
    
    # Required core fields
    marker_type: MarkerType
    start_time: float  # Start time in seconds
    end_time: float    # End time in seconds
    confidence: float  # Confidence score 0.0-1.0
    evidence: str      # Supporting text evidence
    explanation: str   # Human-readable explanation
    
    # Identification
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: Optional[str] = None
    
    # Optional classification
    marker_subtype: Optional[str] = None
    speaker: Optional[str] = None
    
    # Timing and context
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    transcript_segment_id: Optional[str] = None
    
    # Analysis details
    confidence_breakdown: Dict[str, float] = field(default_factory=dict)
    context_window: Dict[str, Any] = field(default_factory=dict)
    related_markers: List[str] = field(default_factory=list)
    
    # Constitutional compliance
    constitutional_source: Optional[str] = None
    analysis_method: str = "LD-3.4"
    
    # Quality and validation
    reviewed: bool = False
    manual_confirmation: Optional[bool] = None
    reviewer_notes: str = ""
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    custom_data: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization validation"""
        # Validate marker type
        if isinstance(self.marker_type, str):
            try:
                self.marker_type = MarkerType(self.marker_type.upper())
            except ValueError:
                raise ValueError(f"Invalid marker type: {self.marker_type}")
        
        # Validate timing
        if self.start_time < 0:
            raise ValueError("Start time cannot be negative")
        
        if self.end_time <= self.start_time:
            raise ValueError("End time must be greater than start time")
        
        # Validate confidence
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        
        # Validate required text fields
        if not self.evidence or not self.evidence.strip():
            raise ValueError("Evidence cannot be empty")
        
        if not self.explanation or not self.explanation.strip():
            raise ValueError("Explanation cannot be empty")
        
        # Validate marker subtype if provided
        if self.marker_subtype:
            self._validate_marker_subtype()
    
    def _validate_marker_subtype(self):
        """Validate marker subtype against known LD-3.4 patterns"""
        valid_subtypes = {
            MarkerType.ATO: [
                "attention_direction", "attention_acknowledgment", 
                "attention_shift", "attention_maintenance", "attention_focus"
            ],
            MarkerType.SEM: [
                "semantic_alignment", "semantic_divergence", 
                "semantic_clarification", "semantic_expansion", "semantic_agreement"
            ],
            MarkerType.CLU: [
                "cluster_formation", "cluster_reinforcement", 
                "cluster_dissolution", "cluster_transition", "cluster_recognition"
            ],
            MarkerType.MEMA: [
                "memory_reference", "memory_alignment", 
                "memory_correction", "memory_expansion", "memory_integration"
            ]
        }
        
        if self.marker_subtype not in valid_subtypes.get(self.marker_type, []):
            raise ValueError(
                f"Invalid subtype '{self.marker_subtype}' for marker type {self.marker_type.value}"
            )
    
    @property
    def duration(self) -> float:
        """Get marker duration in seconds"""
        return self.end_time - self.start_time
    
    @property
    def confidence_level(self) -> MarkerConfidenceLevel:
        """Get categorical confidence level"""
        if self.confidence >= 0.9:
            return MarkerConfidenceLevel.VERY_HIGH
        elif self.confidence >= 0.7:
            return MarkerConfidenceLevel.HIGH
        elif self.confidence >= 0.5:
            return MarkerConfidenceLevel.MEDIUM
        else:
            return MarkerConfidenceLevel.LOW
    
    def is_high_confidence(self) -> bool:
        """Check if marker has high confidence (>= 0.7)"""
        return self.confidence >= 0.7
    
    def get_time_range(self) -> tuple[float, float]:
        """Get time range as tuple"""
        return (self.start_time, self.end_time)
    
    def overlaps_with(self, other: 'MarkerEvent') -> bool:
        """Check if this marker overlaps with another marker"""
        return not (self.end_time <= other.start_time or other.end_time <= self.start_time)
    
    def get_overlap_duration(self, other: 'MarkerEvent') -> float:
        """Get overlap duration with another marker"""
        if not self.overlaps_with(other):
            return 0.0
        
        overlap_start = max(self.start_time, other.start_time)
        overlap_end = min(self.end_time, other.end_time)
        return overlap_end - overlap_start
    
    def add_related_marker(self, marker_id: str) -> None:
        """Add related marker reference"""
        if marker_id not in self.related_markers:
            self.related_markers.append(marker_id)
    
    def set_confidence_breakdown(self, lexical: float, contextual: float, 
                               temporal: float, speaker: float = 0.0) -> None:
        """Set detailed confidence breakdown"""
        self.confidence_breakdown = {
            'lexical_match': lexical,
            'contextual_relevance': contextual,
            'temporal_consistency': temporal,
            'speaker_pattern': speaker
        }
        
        # Validate breakdown values
        for key, value in self.confidence_breakdown.items():
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"Confidence breakdown '{key}' must be between 0.0 and 1.0")
    
    def get_confidence_factors(self) -> Dict[str, float]:
        """Get confidence breakdown factors"""
        return self.confidence_breakdown.copy()
    
    def set_context_window(self, before_text: str = "", after_text: str = "", 
                          window_duration: float = 10.0) -> None:
        """Set surrounding context information"""
        self.context_window = {
            'before_text': before_text,
            'after_text': after_text,
            'window_duration': window_duration,
            'total_context': f"{before_text} {self.evidence} {after_text}".strip()
        }
    
    def mark_reviewed(self, confirmed: bool, reviewer_notes: str = "") -> None:
        """Mark marker as manually reviewed"""
        self.reviewed = True
        self.manual_confirmation = confirmed
        self.reviewer_notes = reviewer_notes
    
    def get_validation_status(self) -> str:
        """Get validation status string"""
        if not self.reviewed:
            return "pending_review"
        elif self.manual_confirmation is True:
            return "confirmed"
        elif self.manual_confirmation is False:
            return "rejected"
        else:
            return "reviewed_neutral"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert marker to dictionary for serialization"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, (MarkerType, MarkerConfidenceLevel)):
                result[key] = value.value
            elif key == 'marker_type':
                result[key] = value.value
            else:
                result[key] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MarkerEvent':
        """Create marker from dictionary"""
        # Convert datetime fields
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        # Convert enum fields
        if 'marker_type' in data and isinstance(data['marker_type'], str):
            data['marker_type'] = MarkerType(data['marker_type'].upper())
        
        return cls(**data)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get marker summary for display"""
        return {
            'id': self.id,
            'type': self.marker_type.value,
            'subtype': self.marker_subtype,
            'time_range': f"{self.start_time:.1f}s - {self.end_time:.1f}s",
            'duration': f"{self.duration:.1f}s",
            'confidence': f"{self.confidence:.2f}",
            'confidence_level': self.confidence_level.value,
            'speaker': self.speaker,
            'evidence_preview': self.evidence[:100] + '...' if len(self.evidence) > 100 else self.evidence,
            'reviewed': self.reviewed
        }
    
    def get_constitutional_info(self) -> Dict[str, Any]:
        """Get constitutional compliance information"""
        return {
            'analysis_method': self.analysis_method,
            'constitutional_source': self.constitutional_source,
            'uses_existing_framework': self.analysis_method == "LD-3.4",
            'library_reuse_approach': True,
            'no_modifications_to_cli': True
        }
    
    def is_within_time_window(self, start: float, end: float) -> bool:
        """Check if marker falls within specified time window"""
        return (self.start_time >= start and self.end_time <= end) or self.overlaps_with_time_range(start, end)
    
    def overlaps_with_time_range(self, start: float, end: float) -> bool:
        """Check if marker overlaps with time range"""
        return not (self.end_time <= start or end <= self.start_time)
    
    def add_tag(self, tag: str) -> None:
        """Add tag to marker"""
        tag = tag.strip().lower()
        if tag and tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str) -> None:
        """Remove tag from marker"""
        tag = tag.strip().lower()
        if tag in self.tags:
            self.tags.remove(tag)