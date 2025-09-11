"""
Rapport Calculator from LD-3.4 Marker Patterns
Calculates rapport indicators based on constitutional marker analysis
CONSTITUTIONAL COMPLIANCE: Uses existing LD-3.4 framework, no CLI modifications
"""

import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import uuid

from src.models.marker_event import MarkerEvent
from src.models.rapport_indicator import RapportIndicator, RapportTrend

logger = logging.getLogger(__name__)


@dataclass
class MarkerWeightConfig:
    """Configuration for marker type weights in rapport calculation"""
    ato_weight: float = 0.8    # Attention markers
    sem_weight: float = 0.9    # Semantic alignment (highest)
    clu_weight: float = 0.7    # Cluster formation
    mema_weight: float = 0.6   # Memory references
    
    # Subtype modifiers
    positive_modifier: float = 1.2  # Alignment, agreement, understanding
    neutral_modifier: float = 1.0   # Direction, reference, transition
    negative_modifier: float = -0.8 # Disagreement, dissolution, correction


class RapportCalculator:
    """
    Constitutional rapport calculation from LD-3.4 markers
    Calculates rapport trends based on marker patterns and speaker interactions
    """
    
    def __init__(self, calculation_window: float = 60.0, 
                 smoothing_factor: float = 0.3,
                 include_trend_analysis: bool = True):
        self.calculation_window = calculation_window
        self.smoothing_factor = smoothing_factor
        self.trend_analysis_enabled = include_trend_analysis
        self.constitutional_source = "LD-3.4-constitution"
        
        # Load constitutional marker weights
        self.marker_weights = MarkerWeightConfig()
        self.calculation_models = self._load_constitutional_models()
        
        logger.info(f"RapportCalculator initialized (window: {calculation_window}s)")
    
    def _load_constitutional_models(self) -> Dict[str, Any]:
        """Load constitutional rapport calculation models"""
        return {
            'marker_weights': {
                'ATO': self.marker_weights.ato_weight,
                'SEM': self.marker_weights.sem_weight, 
                'CLU': self.marker_weights.clu_weight,
                'MEMA': self.marker_weights.mema_weight
            },
            'temporal_decay': {
                'half_life': 120.0,  # 2 minutes
                'decay_rate': 0.8
            },
            'speaker_interaction_weights': {
                'bidirectional_bonus': 0.2,
                'turn_taking_penalty': -0.1,
                'silence_penalty': -0.05
            }
        }
    
    def get_calculation_models(self) -> Dict[str, Any]:
        """Get constitutional rapport calculation models"""
        return self.calculation_models.copy()
    
    def set_marker_weights(self, weights: Dict[str, float]):
        """Set marker type weights for rapport calculation"""
        for marker_type, weight in weights.items():
            if marker_type in self.calculation_models['marker_weights']:
                self.calculation_models['marker_weights'][marker_type] = weight
        
        logger.info(f"Marker weights updated: {weights}")
    
    def calculate_rapport_timeline(self, marker_events: List[MarkerEvent],
                                 session_duration: float,
                                 interaction_context: Optional[Dict[str, Any]] = None,
                                 smoothing_factor: Optional[float] = None) -> List[RapportIndicator]:
        """
        Calculate rapport indicators timeline from marker events
        
        Args:
            marker_events: List of detected LD-3.4 markers
            session_duration: Total session duration in seconds
            interaction_context: Speaker roles and interaction style context
            smoothing_factor: Override smoothing factor for this calculation
            
        Returns:
            List of rapport indicators with temporal progression
        """
        if not marker_events:
            return []
        
        # Use provided smoothing factor or instance default
        effective_smoothing = smoothing_factor if smoothing_factor is not None else self.smoothing_factor
        
        # Sort markers by time
        markers = sorted(marker_events, key=lambda m: m.start_time)
        
        # Generate time points for rapport calculation
        time_points = self._generate_time_points(session_duration)
        
        rapport_indicators = []
        previous_value = 0.0
        
        for timestamp in time_points:
            # Calculate rapport at this time point
            rapport_value, contributing_markers, contributions = self._calculate_rapport_at_time(
                timestamp, markers, interaction_context
            )
            
            # Apply temporal smoothing
            if effective_smoothing > 0 and rapport_indicators:
                rapport_value = self._apply_smoothing(rapport_value, previous_value)
            
            # Calculate trend
            trend = self._calculate_trend(rapport_indicators, rapport_value)
            
            # Calculate confidence
            confidence = self._calculate_confidence(contributing_markers, timestamp)
            
            # Create rapport indicator
            indicator = RapportIndicator(
                timestamp=timestamp,
                value=rapport_value,
                trend=trend,
                confidence=confidence,
                contributing_markers=[m.id for m in contributing_markers],
                calculation_window=self.calculation_window
            )
            
            # Set detailed contributions
            indicator.marker_contributions = {m.id: contrib for m, contrib in contributions.items()}
            
            # Set interaction context if provided
            if interaction_context:
                indicator.set_interaction_context(
                    interaction_context.get('speaker_roles', {}),
                    interaction_context.get('interaction_style', 'unknown'),
                    interaction_context.get('session_phase', '')
                )
            
            rapport_indicators.append(indicator)
            previous_value = rapport_value
        
        logger.info(f"Rapport timeline calculated: {len(rapport_indicators)} indicators")
        return rapport_indicators
    
    def _generate_time_points(self, session_duration: float) -> List[float]:
        """Generate time points for rapport calculation"""
        # Calculate every 30 seconds or at marker events
        interval = min(30.0, self.calculation_window / 2)
        time_points = []
        
        current_time = self.calculation_window / 2  # Start from window center
        while current_time <= session_duration - self.calculation_window / 2:
            time_points.append(current_time)
            current_time += interval
        
        return time_points
    
    def _calculate_rapport_at_time(self, timestamp: float, markers: List[MarkerEvent],
                                 interaction_context: Optional[Dict[str, Any]]) -> Tuple[float, List[MarkerEvent], Dict[MarkerEvent, float]]:
        """Calculate rapport value at specific timestamp"""
        
        # Find markers within calculation window
        window_start = timestamp - self.calculation_window / 2
        window_end = timestamp + self.calculation_window / 2
        
        relevant_markers = [
            m for m in markers 
            if m.is_within_time_window(window_start, window_end)
        ]
        
        if not relevant_markers:
            return 0.0, [], {}
        
        # Calculate weighted contributions
        marker_contributions = {}
        total_weighted_value = 0.0
        total_weights = 0.0
        
        for marker in relevant_markers:
            # Base weight from marker type
            base_weight = self.calculation_models['marker_weights'].get(marker.marker_type.value, 0.5)
            
            # Subtype modifier
            subtype_modifier = self._get_subtype_modifier(marker)
            
            # Confidence modifier
            confidence_modifier = marker.confidence
            
            # Temporal distance modifier (closer to timestamp = higher weight)
            distance = abs(marker.start_time - timestamp)
            temporal_modifier = max(0.1, 1.0 - (distance / (self.calculation_window / 2)))
            
            # Calculate final weight and contribution
            final_weight = base_weight * subtype_modifier * confidence_modifier * temporal_modifier
            marker_contributions[marker] = final_weight
            
            # Determine marker's rapport contribution value
            marker_value = self._get_marker_rapport_value(marker, interaction_context)
            
            total_weighted_value += marker_value * abs(final_weight)
            total_weights += abs(final_weight)
        
        # Calculate final rapport value
        if total_weights > 0:
            rapport_value = total_weighted_value / total_weights
            # Normalize to [-1, 1] range
            rapport_value = max(-1.0, min(1.0, rapport_value))
        else:
            rapport_value = 0.0
        
        return rapport_value, relevant_markers, marker_contributions
    
    def _get_subtype_modifier(self, marker: MarkerEvent) -> float:
        """Get subtype modifier for marker contribution"""
        positive_subtypes = {
            'attention_acknowledgment', 'semantic_alignment', 'semantic_understanding',
            'cluster_formation', 'cluster_reinforcement', 'memory_alignment'
        }
        
        negative_subtypes = {
            'semantic_divergence', 'cluster_dissolution', 'memory_correction'
        }
        
        if marker.marker_subtype in positive_subtypes:
            return self.marker_weights.positive_modifier
        elif marker.marker_subtype in negative_subtypes:
            return self.marker_weights.negative_modifier
        else:
            return self.marker_weights.neutral_modifier
    
    def _get_marker_rapport_value(self, marker: MarkerEvent, 
                                interaction_context: Optional[Dict[str, Any]]) -> float:
        """Get rapport value contribution for marker"""
        
        # Base values by marker type and subtype
        rapport_values = {
            'ATO': {
                'attention_direction': 0.3,      # Neutral - guidance
                'attention_acknowledgment': 0.7,  # Positive - engagement
                'attention_shift': 0.1,          # Neutral - navigation
                'attention_maintenance': 0.4,    # Slightly positive
                'attention_focus': 0.5          # Neutral to positive
            },
            'SEM': {
                'semantic_alignment': 0.8,       # Strong positive
                'semantic_clarification': 0.2,   # Neutral - normal process
                'semantic_understanding': 0.9,   # Very positive
                'semantic_expansion': 0.6,       # Positive - building
                'semantic_divergence': -0.6      # Negative - disagreement
            },
            'CLU': {
                'cluster_formation': 0.8,        # Strong positive
                'cluster_recognition': 0.7,      # Positive
                'cluster_reinforcement': 0.9,    # Very positive
                'cluster_dissolution': -0.5,     # Negative
                'cluster_transition': 0.2        # Neutral - change
            },
            'MEMA': {
                'memory_reference': 0.4,         # Positive - continuity
                'memory_alignment': 0.8,         # Strong positive
                'memory_correction': -0.2,       # Slightly negative
                'memory_expansion': 0.6,         # Positive - building
                'memory_integration': 0.7        # Positive - synthesis
            }
        }
        
        marker_type = marker.marker_type.value
        marker_subtype = marker.marker_subtype
        
        if marker_type in rapport_values and marker_subtype in rapport_values[marker_type]:
            base_value = rapport_values[marker_type][marker_subtype]
        else:
            base_value = 0.0
        
        # Apply interaction context modifiers
        if interaction_context and 'speaker_roles' in interaction_context:
            # Modifiers based on speaker roles could be applied here
            pass
        
        return base_value
    
    def _apply_smoothing(self, current_value: float, previous_value: float) -> float:
        """Apply temporal smoothing to rapport values"""
        return (previous_value * self.smoothing_factor + 
                current_value * (1.0 - self.smoothing_factor))
    
    def _calculate_trend(self, previous_indicators: List[RapportIndicator], 
                        current_value: float) -> RapportTrend:
        """Calculate rapport trend direction"""
        if len(previous_indicators) < 2:
            return RapportTrend.STABLE
        
        # Look at last few values for trend
        recent_values = [ind.value for ind in previous_indicators[-3:]] + [current_value]
        
        if len(recent_values) < 2:
            return RapportTrend.STABLE
        
        # Calculate trend direction
        differences = [recent_values[i] - recent_values[i-1] for i in range(1, len(recent_values))]
        avg_change = sum(differences) / len(differences)
        change_variance = sum((d - avg_change) ** 2 for d in differences) / len(differences)
        
        # Determine trend based on average change and variance
        if change_variance > 0.1:  # High variance
            return RapportTrend.VOLATILE
        elif avg_change > 0.05:    # Increasing
            return RapportTrend.INCREASING
        elif avg_change < -0.05:   # Decreasing
            return RapportTrend.DECREASING
        else:                      # Stable
            return RapportTrend.STABLE
    
    def _calculate_confidence(self, markers: List[MarkerEvent], timestamp: float) -> float:
        """Calculate confidence in rapport calculation"""
        if not markers:
            return 0.0
        
        # Factors affecting confidence
        marker_quality = sum(m.confidence for m in markers) / len(markers)
        marker_quantity = min(len(markers) / 5, 1.0)  # Normalize to max 5 markers
        
        # Temporal consistency (markers spread across window)
        if len(markers) > 1:
            time_span = max(m.start_time for m in markers) - min(m.start_time for m in markers)
            temporal_consistency = min(time_span / self.calculation_window, 1.0)
        else:
            temporal_consistency = 0.5
        
        # Weighted combination
        confidence = (
            marker_quality * 0.5 +
            marker_quantity * 0.3 +
            temporal_consistency * 0.2
        )
        
        return min(confidence, 1.0)
    
    def calculate_session_trend(self, rapport_indicators: List[RapportIndicator]) -> Dict[str, Any]:
        """Calculate overall session trend analysis"""
        if len(rapport_indicators) < 3:
            return {
                'overall_direction': 'insufficient_data',
                'trend_strength': 0.0,
                'key_moments': []
            }
        
        values = [ind.value for ind in rapport_indicators]
        
        # Linear trend analysis
        n = len(values)
        x_values = list(range(n))
        
        # Simple linear regression
        x_mean = sum(x_values) / n
        y_mean = sum(values) / n
        
        numerator = sum((x_values[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
        
        if denominator > 0:
            slope = numerator / denominator
            trend_strength = abs(slope)
        else:
            slope = 0
            trend_strength = 0
        
        # Overall direction
        if slope > 0.02:
            overall_direction = 'improving'
        elif slope < -0.02:
            overall_direction = 'declining'
        else:
            overall_direction = 'stable'
        
        # Identify key moments (significant changes)
        key_moments = []
        for i in range(1, len(rapport_indicators)):
            change = rapport_indicators[i].value - rapport_indicators[i-1].value
            if abs(change) > 0.2:  # Significant change threshold
                key_moments.append({
                    'timestamp': rapport_indicators[i].timestamp,
                    'change': change,
                    'value': rapport_indicators[i].value,
                    'type': 'increase' if change > 0 else 'decrease'
                })
        
        return {
            'overall_direction': overall_direction,
            'trend_strength': trend_strength,
            'key_moments': key_moments[:5],  # Top 5 key moments
            'final_rapport': values[-1] if values else 0.0,
            'average_rapport': sum(values) / len(values) if values else 0.0,
            'rapport_range': (min(values), max(values)) if values else (0.0, 0.0)
        }
    
    def start_realtime_calculation(self, update_interval: float = 5.0) -> str:
        """Start real-time rapport calculation session"""
        session_id = str(uuid.uuid4())
        
        # In real implementation, would manage real-time updates
        logger.info(f"Real-time rapport calculation started: {session_id}")
        return session_id
    
    def add_marker_realtime(self, session_id: str, marker: MarkerEvent) -> float:
        """Add marker to real-time calculation and get current rapport"""
        # Simplified real-time calculation
        marker_value = self._get_marker_rapport_value(marker, None)
        current_rapport = max(-1.0, min(1.0, marker_value))
        
        return current_rapport
    
    def get_current_trend(self, session_id: str) -> Dict[str, Any]:
        """Get current trend for real-time session"""
        return {
            'direction': 'stable',
            'confidence': 0.7,
            'recent_change': 0.1
        }
    
    def stop_realtime_calculation(self, session_id: str):
        """Stop real-time calculation session"""
        logger.info(f"Real-time rapport calculation stopped: {session_id}")
    
    def export_for_chart(self, rapport_indicators: List[RapportIndicator]) -> Dict[str, Any]:
        """Export rapport data for chart visualization"""
        if not rapport_indicators:
            return {
                'timestamps': [],
                'values': [],
                'trends': [],
                'confidence_bands': []
            }
        
        return {
            'timestamps': [ind.timestamp for ind in rapport_indicators],
            'values': [ind.value for ind in rapport_indicators],
            'trends': [ind.trend.value for ind in rapport_indicators],
            'confidence_bands': [ind.confidence for ind in rapport_indicators]
        }
    
    def export_detailed_analysis(self, rapport_indicators: List[RapportIndicator]) -> Dict[str, Any]:
        """Export detailed rapport analysis"""
        if not rapport_indicators:
            return {}
        
        session_trend = self.calculate_session_trend(rapport_indicators)
        
        # Calculate marker type contributions
        marker_type_contributions = {}
        for indicator in rapport_indicators:
            for marker_id, contribution in indicator.marker_contributions.items():
                # In real implementation, would lookup marker type by ID
                marker_type = 'unknown'  # Placeholder
                if marker_type not in marker_type_contributions:
                    marker_type_contributions[marker_type] = []
                marker_type_contributions[marker_type].append(contribution)
        
        return {
            'summary_statistics': {
                'total_indicators': len(rapport_indicators),
                'average_rapport': sum(ind.value for ind in rapport_indicators) / len(rapport_indicators),
                'average_confidence': sum(ind.confidence for ind in rapport_indicators) / len(rapport_indicators),
                'duration': rapport_indicators[-1].timestamp - rapport_indicators[0].timestamp if len(rapport_indicators) > 1 else 0.0
            },
            'trend_analysis': session_trend,
            'key_moments': session_trend['key_moments'],
            'marker_contributions': marker_type_contributions
        }
    
    def calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of values"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        return variance