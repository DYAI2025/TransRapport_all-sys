"""
RapportIndicator Data Model
Represents calculated rapport values with trends and contributing factors
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from enum import Enum
import uuid


class RapportTrend(Enum):
    """Rapport trend direction"""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"


class RapportLevel(Enum):
    """Categorical rapport levels"""
    VERY_LOW = "very_low"      # -1.0 to -0.6
    LOW = "low"                # -0.6 to -0.2
    NEUTRAL = "neutral"        # -0.2 to 0.2
    MODERATE = "moderate"      # 0.2 to 0.6
    HIGH = "high"              # 0.6 to 0.8
    VERY_HIGH = "very_high"    # 0.8 to 1.0


@dataclass
class RapportIndicator:
    """
    Rapport indicator calculated from LD-3.4 marker patterns
    
    Represents rapport value at a specific timestamp with
    trend analysis and contributing marker information.
    """
    
    # Core rapport data
    timestamp: float  # Time point in seconds
    value: float      # Rapport value -1.0 to 1.0
    trend: RapportTrend
    confidence: float  # Confidence in calculation 0.0-1.0
    
    # Contributing factors
    contributing_markers: List[str] = field(default_factory=list)  # Marker IDs
    
    # Identification
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: Optional[str] = None
    
    # Analysis metadata
    calculation_window: float = 60.0  # Window size in seconds
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Detailed analysis
    marker_contributions: Dict[str, float] = field(default_factory=dict)
    speaker_contributions: Dict[str, float] = field(default_factory=dict)
    trend_analysis: Dict[str, Any] = field(default_factory=dict)
    
    # Quality metrics
    confidence_factors: Dict[str, float] = field(default_factory=dict)
    smoothing_applied: bool = False
    outlier_filtered: bool = False
    
    # Context information
    interaction_context: Dict[str, Any] = field(default_factory=dict)
    temporal_context: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    notes: str = ""
    custom_data: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization validation"""
        # Validate rapport value range
        if not -1.0 <= self.value <= 1.0:
            raise ValueError("Rapport value must be between -1.0 and 1.0")
        
        # Validate confidence
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        
        # Validate timestamp
        if self.timestamp < 0:
            raise ValueError("Timestamp cannot be negative")
        
        # Validate calculation window
        if self.calculation_window <= 0:
            raise ValueError("Calculation window must be positive")
        
        # Convert trend to enum if string
        if isinstance(self.trend, str):
            try:
                self.trend = RapportTrend(self.trend.lower())
            except ValueError:
                raise ValueError(f"Invalid rapport trend: {self.trend}")
    
    @property
    def rapport_level(self) -> RapportLevel:
        """Get categorical rapport level"""
        if self.value >= 0.8:
            return RapportLevel.VERY_HIGH
        elif self.value >= 0.6:
            return RapportLevel.HIGH
        elif self.value >= 0.2:
            return RapportLevel.MODERATE
        elif self.value >= -0.2:
            return RapportLevel.NEUTRAL
        elif self.value >= -0.6:
            return RapportLevel.LOW
        else:
            return RapportLevel.VERY_LOW
    
    @property
    def is_positive_rapport(self) -> bool:
        """Check if rapport is positive (> 0.0)"""
        return self.value > 0.0
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if calculation has high confidence (>= 0.7)"""
        return self.confidence >= 0.7
    
    def get_time_window(self) -> tuple[float, float]:
        """Get the time window this indicator represents"""
        start_time = max(0.0, self.timestamp - self.calculation_window / 2)
        end_time = self.timestamp + self.calculation_window / 2
        return (start_time, end_time)
    
    def add_contributing_marker(self, marker_id: str, contribution: float = 1.0) -> None:
        """Add a contributing marker with its contribution weight"""
        if marker_id not in self.contributing_markers:
            self.contributing_markers.append(marker_id)
        
        self.marker_contributions[marker_id] = contribution
    
    def set_speaker_contributions(self, contributions: Dict[str, float]) -> None:
        """Set speaker contribution weights"""
        # Validate contributions sum to reasonable total
        total = sum(contributions.values())
        if total > 0:
            # Normalize to ensure they represent relative contributions
            self.speaker_contributions = {
                speaker: contrib / total for speaker, contrib in contributions.items()
            }
        else:
            self.speaker_contributions = contributions.copy()
    
    def set_confidence_factors(self, marker_quality: float, marker_quantity: float,
                             temporal_consistency: float, speaker_balance: float = 0.0) -> None:
        """Set detailed confidence breakdown"""
        self.confidence_factors = {
            'marker_quality': marker_quality,
            'marker_quantity': marker_quantity,
            'temporal_consistency': temporal_consistency,
            'speaker_balance': speaker_balance
        }
        
        # Validate factor values
        for factor, value in self.confidence_factors.items():
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"Confidence factor '{factor}' must be between 0.0 and 1.0")
    
    def get_confidence_factors(self) -> Dict[str, float]:
        """Get confidence factor breakdown"""
        return self.confidence_factors.copy()
    
    def set_trend_analysis(self, direction: str, strength: float, 
                          recent_change: float, volatility: float) -> None:
        """Set detailed trend analysis"""
        self.trend_analysis = {
            'direction': direction,
            'strength': strength,
            'recent_change': recent_change,
            'volatility': volatility,
            'trend_confidence': min(strength, 1.0 - volatility)
        }
    
    def get_trend_info(self) -> Dict[str, Any]:
        """Get trend analysis information"""
        return {
            'trend': self.trend.value,
            'analysis': self.trend_analysis,
            'is_trending_up': self.trend == RapportTrend.INCREASING,
            'is_stable': self.trend == RapportTrend.STABLE,
            'is_volatile': self.trend == RapportTrend.VOLATILE
        }
    
    def set_interaction_context(self, speaker_roles: Dict[str, str],
                              interaction_style: str, session_phase: str = "") -> None:
        """Set interaction context information"""
        self.interaction_context = {
            'speaker_roles': speaker_roles,
            'interaction_style': interaction_style,
            'session_phase': session_phase,
            'primary_speakers': list(speaker_roles.keys())
        }
    
    def get_interaction_analysis(self) -> Dict[str, Any]:
        """Get interaction pattern analysis"""
        if not self.interaction_context:
            return {}
        
        analysis = self.interaction_context.copy()
        
        # Add speaker balance analysis
        if self.speaker_contributions:
            analysis['speaker_balance'] = self._calculate_speaker_balance()
            analysis['primary_contributor'] = max(
                self.speaker_contributions.items(), 
                key=lambda x: x[1]
            )[0] if self.speaker_contributions else None
        
        return analysis
    
    def _calculate_speaker_balance(self) -> float:
        """Calculate speaker balance (0.0 = imbalanced, 1.0 = perfectly balanced)"""
        if not self.speaker_contributions:
            return 0.0
        
        contributions = list(self.speaker_contributions.values())
        if len(contributions) < 2:
            return 0.0
        
        # Calculate how close contributions are to being equal
        ideal_contribution = 1.0 / len(contributions)
        deviations = [abs(contrib - ideal_contribution) for contrib in contributions]
        avg_deviation = sum(deviations) / len(deviations)
        
        # Convert to balance score (lower deviation = higher balance)
        balance = 1.0 - (avg_deviation / ideal_contribution)
        return max(0.0, min(1.0, balance))
    
    def get_weights_breakdown(self) -> Dict[str, Any]:
        """Get detailed breakdown of how rapport was calculated"""
        return {
            'marker_contributions': self.marker_contributions,
            'speaker_contributions': self.speaker_contributions,
            'total_markers': len(self.contributing_markers),
            'calculation_window': self.calculation_window,
            'smoothing_applied': self.smoothing_applied,
            'outlier_filtered': self.outlier_filtered
        }
    
    def is_within_time_range(self, start_time: float, end_time: float) -> bool:
        """Check if indicator falls within specified time range"""
        return start_time <= self.timestamp <= end_time
    
    def get_distance_from_time(self, target_time: float) -> float:
        """Get temporal distance from target time"""
        return abs(self.timestamp - target_time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, (RapportTrend, RapportLevel)):
                result[key] = value.value
            else:
                result[key] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RapportIndicator':
        """Create from dictionary"""
        # Convert datetime fields
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        # Convert enum fields
        if 'trend' in data and isinstance(data['trend'], str):
            data['trend'] = RapportTrend(data['trend'])
        
        return cls(**data)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get rapport indicator summary for display"""
        return {
            'timestamp': f"{self.timestamp:.1f}s",
            'value': f"{self.value:.3f}",
            'level': self.rapport_level.value,
            'trend': self.trend.value,
            'confidence': f"{self.confidence:.2f}",
            'contributing_markers_count': len(self.contributing_markers),
            'calculation_window': f"{self.calculation_window:.1f}s",
            'is_high_confidence': self.is_high_confidence
        }
    
    def get_visualization_data(self) -> Dict[str, Any]:
        """Get data formatted for chart visualization"""
        return {
            'x': self.timestamp,
            'y': self.value,
            'confidence': self.confidence,
            'trend': self.trend.value,
            'level': self.rapport_level.value,
            'marker_count': len(self.contributing_markers),
            'tooltip': f"t={self.timestamp:.1f}s, rapport={self.value:.3f}, conf={self.confidence:.2f}"
        }
    
    def compare_with(self, other: 'RapportIndicator') -> Dict[str, Any]:
        """Compare this indicator with another"""
        if not isinstance(other, RapportIndicator):
            raise ValueError("Can only compare with another RapportIndicator")
        
        return {
            'value_difference': self.value - other.value,
            'confidence_difference': self.confidence - other.confidence,
            'time_difference': self.timestamp - other.timestamp,
            'trend_changed': self.trend != other.trend,
            'level_changed': self.rapport_level != other.rapport_level,
            'markers_difference': len(self.contributing_markers) - len(other.contributing_markers)
        }