"""
Contract Tests for Rapport Calculation from LD-3.4 Markers
CRITICAL: These tests MUST FAIL before implementation exists
"""

import pytest
import json
from datetime import datetime, timedelta

# Import the rapport calculation library (will fail until implemented)
try:
    from src.lib.analysis.rapport_calculator import RapportCalculator
    from src.models.rapport_indicator import RapportIndicator
    from src.models.marker_event import MarkerEvent
except ImportError:
    pytest.skip("Rapport calculation library not implemented yet", allow_module_level=True)


class TestRapportCalculatorContract:
    """Contract tests for rapport calculation from marker patterns"""
    
    @pytest.fixture
    def rapport_calculator(self):
        """Initialize rapport calculator"""
        return RapportCalculator(
            calculation_window=60.0,  # 1-minute windows
            smoothing_factor=0.3,
            include_trend_analysis=True
        )
    
    @pytest.fixture
    def sample_marker_events(self):
        """Sample LD-3.4 marker events for rapport calculation"""
        base_time = datetime.now()
        return [
            MarkerEvent(
                id="ato_001",
                marker_type="ATO",
                marker_subtype="attention_direction",
                start_time=0.0,
                end_time=5.0,
                speaker="THERAPIST",
                confidence=0.9,
                evidence="I want you to focus on what you're feeling",
                explanation="Therapist directing client attention"
            ),
            MarkerEvent(
                id="ato_002",
                marker_type="ATO",
                marker_subtype="attention_acknowledgment",
                start_time=15.0,
                end_time=20.0,
                speaker="CLIENT",
                confidence=0.85,
                evidence="Oh, I see what you mean",
                explanation="Client acknowledging attention direction"
            ),
            MarkerEvent(
                id="sem_001",
                marker_type="SEM",
                marker_subtype="semantic_alignment",
                start_time=25.0,
                end_time=30.0,
                speaker="CLIENT",
                confidence=0.8,
                evidence="Yes, that makes sense",
                explanation="Client showing semantic understanding"
            ),
            MarkerEvent(
                id="clu_001",
                marker_type="CLU",
                marker_subtype="cluster_formation",
                start_time=45.0,
                end_time=55.0,
                speaker="THERAPIST",
                confidence=0.75,
                evidence="We both understand this pattern",
                explanation="Recognition of shared understanding"
            ),
            MarkerEvent(
                id="mema_001",
                marker_type="MEMA",
                marker_subtype="memory_alignment",
                start_time=70.0,
                end_time=75.0,
                speaker="CLIENT",
                confidence=0.88,
                evidence="Like we talked about last time",
                explanation="Reference to shared conversational memory"
            )
        ]
    
    def test_rapport_calculator_initialization(self, rapport_calculator):
        """MUST initialize rapport calculator with proper configuration"""
        assert rapport_calculator.calculation_window == 60.0
        assert rapport_calculator.smoothing_factor == 0.3
        assert rapport_calculator.trend_analysis_enabled is True
        
        # Must have access to rapport calculation models
        models = rapport_calculator.get_calculation_models()
        assert 'marker_weights' in models
        assert 'temporal_decay' in models
        assert 'speaker_interaction_weights' in models
    
    def test_calculate_rapport_indicators_from_markers(self, rapport_calculator, sample_marker_events):
        """MUST calculate rapport indicators from LD-3.4 marker events"""
        rapport_indicators = rapport_calculator.calculate_rapport_timeline(
            marker_events=sample_marker_events,
            session_duration=120.0
        )
        
        # Must return list of rapport indicators
        assert isinstance(rapport_indicators, list)
        assert len(rapport_indicators) > 0
        
        # Each indicator must have required fields
        for indicator in rapport_indicators:
            assert hasattr(indicator, 'timestamp')
            assert hasattr(indicator, 'value')
            assert hasattr(indicator, 'trend')
            assert hasattr(indicator, 'contributing_markers')
            assert hasattr(indicator, 'confidence')
            
            # Rapport value must be in valid range
            assert -1.0 <= indicator.value <= 1.0
            
            # Must reference actual markers
            assert len(indicator.contributing_markers) > 0
            marker_ids = [m.id for m in sample_marker_events]
            assert all(marker_id in marker_ids for marker_id in indicator.contributing_markers)
    
    def test_rapport_calculation_with_marker_weights(self, rapport_calculator, sample_marker_events):
        """MUST weight different marker types appropriately for rapport"""
        # Configure marker weights
        rapport_calculator.set_marker_weights({
            'ATO': 0.8,  # High weight for attention markers
            'SEM': 0.9,  # Highest weight for semantic alignment
            'CLU': 0.7,  # Good weight for cluster formation
            'MEMA': 0.6  # Moderate weight for memory markers
        })
        
        rapport_indicators = rapport_calculator.calculate_rapport_timeline(
            sample_marker_events,
            session_duration=120.0
        )
        
        # Must reflect weighted contributions
        for indicator in rapport_indicators:
            weights_info = indicator.get_weights_breakdown()
            assert 'marker_contributions' in weights_info
            
            # SEM markers should have highest contribution when present
            sem_contributions = [c for c in weights_info['marker_contributions'] 
                               if c['marker_type'] == 'SEM']
            if sem_contributions:
                assert sem_contributions[0]['weight'] >= 0.9
    
    def test_rapport_trend_analysis(self, rapport_calculator, sample_marker_events):
        """MUST provide trend analysis for rapport progression"""
        rapport_indicators = rapport_calculator.calculate_rapport_timeline(
            sample_marker_events,
            session_duration=120.0
        )
        
        # Must calculate trends
        for indicator in rapport_indicators:
            assert indicator.trend in ['increasing', 'decreasing', 'stable', 'volatile']
            
            # Trend must be based on historical values
            if hasattr(indicator, 'trend_confidence'):
                assert 0.0 <= indicator.trend_confidence <= 1.0
        
        # Must provide overall session trend
        session_trend = rapport_calculator.calculate_session_trend(rapport_indicators)
        assert 'overall_direction' in session_trend
        assert 'trend_strength' in session_trend
        assert 'key_moments' in session_trend
        
        assert session_trend['overall_direction'] in ['improving', 'declining', 'stable', 'mixed']
        assert 0.0 <= session_trend['trend_strength'] <= 1.0
    
    def test_rapport_with_speaker_interaction_patterns(self, rapport_calculator, sample_marker_events):
        """MUST account for speaker interaction patterns in rapport calculation"""
        # Add speaker interaction context
        interaction_context = {
            'primary_speakers': ['THERAPIST', 'CLIENT'],
            'speaker_roles': {
                'THERAPIST': 'facilitator',
                'CLIENT': 'participant'
            },
            'interaction_style': 'therapeutic'
        }
        
        rapport_indicators = rapport_calculator.calculate_rapport_timeline(
            marker_events=sample_marker_events,
            session_duration=120.0,
            interaction_context=interaction_context
        )
        
        # Must reflect role-appropriate rapport patterns
        for indicator in rapport_indicators:
            interaction_analysis = indicator.get_interaction_analysis()
            assert 'speaker_balance' in interaction_analysis
            assert 'role_fulfillment' in interaction_analysis
            assert 'mutual_engagement' in interaction_analysis
    
    def test_rapport_temporal_smoothing(self, rapport_calculator, sample_marker_events):
        """MUST apply temporal smoothing to rapport calculations"""
        # Test with different smoothing factors
        no_smoothing = rapport_calculator.calculate_rapport_timeline(
            sample_marker_events,
            session_duration=120.0,
            smoothing_factor=0.0
        )
        
        high_smoothing = rapport_calculator.calculate_rapport_timeline(
            sample_marker_events,
            session_duration=120.0,
            smoothing_factor=0.8
        )
        
        # High smoothing should produce less volatile values
        no_smooth_variance = rapport_calculator.calculate_variance(
            [i.value for i in no_smoothing]
        )
        high_smooth_variance = rapport_calculator.calculate_variance(
            [i.value for i in high_smoothing]
        )
        
        assert high_smooth_variance <= no_smooth_variance
    
    def test_rapport_confidence_scoring(self, rapport_calculator, sample_marker_events):
        """MUST provide confidence scores for rapport calculations"""
        rapport_indicators = rapport_calculator.calculate_rapport_timeline(
            sample_marker_events,
            session_duration=120.0
        )
        
        for indicator in rapport_indicators:
            # Must have confidence score
            assert hasattr(indicator, 'confidence')
            assert 0.0 <= indicator.confidence <= 1.0
            
            # Confidence must be based on marker quality and quantity
            confidence_factors = indicator.get_confidence_factors()
            assert 'marker_quality' in confidence_factors
            assert 'marker_quantity' in confidence_factors
            assert 'temporal_consistency' in confidence_factors
            
            # High-confidence indicators should have supporting evidence
            if indicator.confidence >= 0.8:
                assert len(indicator.contributing_markers) >= 2
    
    def test_rapport_export_for_visualization(self, rapport_calculator, sample_marker_events):
        """MUST export rapport data suitable for UI visualization"""
        rapport_indicators = rapport_calculator.calculate_rapport_timeline(
            sample_marker_events,
            session_duration=120.0
        )
        
        # Export for chart visualization
        chart_data = rapport_calculator.export_for_chart(rapport_indicators)
        
        assert 'timestamps' in chart_data
        assert 'values' in chart_data
        assert 'trends' in chart_data
        assert 'confidence_bands' in chart_data
        
        # Data must be properly formatted
        assert len(chart_data['timestamps']) == len(chart_data['values'])
        assert all(isinstance(ts, float) for ts in chart_data['timestamps'])
        assert all(-1.0 <= val <= 1.0 for val in chart_data['values'])
        
        # Export for detailed analysis
        detailed_export = rapport_calculator.export_detailed_analysis(rapport_indicators)
        
        assert 'summary_statistics' in detailed_export
        assert 'key_moments' in detailed_export
        assert 'marker_contributions' in detailed_export
        assert 'trend_analysis' in detailed_export
    
    def test_rapport_real_time_calculation(self, rapport_calculator):
        """MUST support real-time rapport calculation during analysis"""
        # Initialize real-time calculator
        realtime_session = rapport_calculator.start_realtime_calculation(
            update_interval=5.0
        )
        
        # Must accept incremental marker updates
        marker1 = sample_marker_events[0]  # Would need fixture access
        current_rapport = rapport_calculator.add_marker_realtime(
            realtime_session, marker1
        )
        
        assert isinstance(current_rapport, float)
        assert -1.0 <= current_rapport <= 1.0
        
        # Must provide current trend
        current_trend = rapport_calculator.get_current_trend(realtime_session)
        assert 'direction' in current_trend
        assert 'confidence' in current_trend
        assert 'recent_change' in current_trend
        
        rapport_calculator.stop_realtime_calculation(realtime_session)


class TestRapportIndicatorContract:
    """Contract tests for RapportIndicator model"""
    
    def test_rapport_indicator_creation(self):
        """MUST create rapport indicators with required fields"""
        indicator = RapportIndicator(
            timestamp=60.0,
            value=0.75,
            trend="increasing",
            contributing_markers=["ato_001", "sem_001"],
            confidence=0.85
        )
        
        assert indicator.timestamp == 60.0
        assert indicator.value == 0.75
        assert indicator.trend == "increasing"
        assert len(indicator.contributing_markers) == 2
        assert indicator.confidence == 0.85
    
    def test_rapport_indicator_validation(self):
        """MUST validate rapport indicator values"""
        # Invalid rapport value should raise error
        with pytest.raises(ValueError, match="Rapport value must be between -1.0 and 1.0"):
            RapportIndicator(
                timestamp=60.0,
                value=1.5,  # Invalid: > 1.0
                trend="increasing",
                contributing_markers=["test"],
                confidence=0.8
            )
        
        # Invalid trend should raise error
        with pytest.raises(ValueError, match="Invalid trend"):
            RapportIndicator(
                timestamp=60.0,
                value=0.5,
                trend="unknown_trend",  # Invalid trend
                contributing_markers=["test"],
                confidence=0.8
            )


if __name__ == "__main__":
    # Run these tests to verify they FAIL before implementation
    pytest.main([__file__, "-v", "--tb=short"])