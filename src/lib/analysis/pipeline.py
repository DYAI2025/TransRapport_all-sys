"""
LD-3.4 Analysis Pipeline
Orchestrates constitutional marker analysis following LD-3.4 framework
CONSTITUTIONAL COMPLIANCE: Uses existing LD-3.4 framework, no CLI modifications
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from src.models.marker_event import MarkerEvent, MarkerType
from src.models.rapport_indicator import RapportIndicator
from .ato_engine import ATOMarkerEngine
from .sem_engine import SEMMarkerEngine
from .clu_engine import CLUMarkerEngine
from .mema_engine import MEMAMarkerEngine
from .rapport_calculator import RapportCalculator

logger = logging.getLogger(__name__)


@dataclass
class AnalysisConfig:
    """Configuration for LD-3.4 analysis pipeline"""
    confidence_threshold: float = 0.7
    enable_ato: bool = True
    enable_sem: bool = True
    enable_clu: bool = True
    enable_mema: bool = True
    enable_rapport: bool = True
    constitutional_source: str = "LD-3.4-constitution"
    analysis_method: str = "LD-3.4"


@dataclass
class AnalysisResults:
    """Results from LD-3.4 analysis pipeline"""
    markers: List[MarkerEvent] = field(default_factory=list)
    rapport_indicators: List[RapportIndicator] = field(default_factory=list)
    analysis_metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    
    def get_markers_by_type(self, marker_type: MarkerType) -> List[MarkerEvent]:
        """Get markers filtered by type"""
        return [m for m in self.markers if m.marker_type == marker_type]
    
    def get_markers_by_subtype(self, subtype: str) -> List[MarkerEvent]:
        """Get markers filtered by subtype"""
        return [m for m in self.markers if m.marker_subtype == subtype]


class LD34AnalysisPipeline:
    """
    LD-3.4 Constitutional Analysis Pipeline
    Orchestrates ATO→SEM→CLU→MEMA marker analysis and rapport calculation
    """
    
    def __init__(self, config: Optional[AnalysisConfig] = None):
        self.config = config or AnalysisConfig()
        self.constitutional_source = self.config.constitutional_source
        self.analysis_method = self.config.analysis_method
        
        # Initialize marker engines according to configuration
        self.engines = {}
        if self.config.enable_ato:
            self.engines['ATO'] = ATOMarkerEngine(self.config.confidence_threshold)
        if self.config.enable_sem:
            self.engines['SEM'] = SEMMarkerEngine(self.config.confidence_threshold)
        if self.config.enable_clu:
            self.engines['CLU'] = CLUMarkerEngine(self.config.confidence_threshold)
        if self.config.enable_mema:
            self.engines['MEMA'] = MEMAMarkerEngine(self.config.confidence_threshold)
        
        # Initialize rapport calculator if enabled
        self.rapport_calculator = None
        if self.config.enable_rapport:
            self.rapport_calculator = RapportCalculator()
        
        logger.info(f"LD-3.4 pipeline initialized with engines: {list(self.engines.keys())}")
    
    def analyze_transcript(self, transcript_segments: List[Dict[str, Any]]) -> AnalysisResults:
        """
        Run complete LD-3.4 analysis on transcript segments
        
        Args:
            transcript_segments: List of transcript segments with text, timing, and speaker info
            
        Returns:
            AnalysisResults containing markers and rapport metrics
        """
        start_time = datetime.now()
        
        if not transcript_segments:
            logger.warning("Empty transcript provided to analysis pipeline")
            return AnalysisResults()
        
        logger.info(f"Starting LD-3.4 analysis on {len(transcript_segments)} transcript segments")
        
        # Run marker detection engines in constitutional order: ATO→SEM→CLU→MEMA
        all_markers = []
        engine_stats = {}
        
        for engine_name in ['ATO', 'SEM', 'CLU', 'MEMA']:
            if engine_name in self.engines:
                engine = self.engines[engine_name]
                engine_markers = engine.analyze_transcript_segments(transcript_segments)
                all_markers.extend(engine_markers)
                engine_stats[engine_name] = len(engine_markers)
                logger.info(f"{engine_name} engine detected {len(engine_markers)} markers")
        
        # Sort markers by temporal order
        all_markers.sort(key=lambda m: m.start_time)
        
        # Calculate rapport indicators if enabled
        rapport_indicators = []
        if self.rapport_calculator and all_markers:
            # Calculate session duration from markers
            session_duration = max(marker.end_time for marker in all_markers) if all_markers else 60.0
            rapport_indicators = self.rapport_calculator.calculate_rapport_timeline(all_markers, session_duration)
            logger.info(f"Rapport calculation completed: {len(rapport_indicators)} indicators generated")
        
        # Build analysis metadata
        processing_time = (datetime.now() - start_time).total_seconds()
        metadata = {
            'transcript_segments': len(transcript_segments),
            'total_markers': len(all_markers),
            'engine_stats': engine_stats,
            'constitutional_source': self.constitutional_source,
            'analysis_method': self.analysis_method,
            'configuration': {
                'confidence_threshold': self.config.confidence_threshold,
                'enabled_engines': list(self.engines.keys()),
                'rapport_enabled': self.rapport_calculator is not None
            }
        }
        
        results = AnalysisResults(
            markers=all_markers,
            rapport_indicators=rapport_indicators,
            analysis_metadata=metadata,
            processing_time=processing_time
        )
        
        avg_rapport = sum(ind.value for ind in rapport_indicators) / len(rapport_indicators) if rapport_indicators else 0.0
        rapport_str = f"{avg_rapport:.3f}" if rapport_indicators else "disabled"
        logger.info(f"LD-3.4 analysis completed in {processing_time:.2f}s: "
                   f"{len(all_markers)} markers, rapport={rapport_str}")
        
        return results
    
    def analyze_segments_by_engine(self, transcript_segments: List[Dict[str, Any]], 
                                  engine_types: List[str]) -> Dict[str, List[MarkerEvent]]:
        """
        Run analysis with specific engines only
        
        Args:
            transcript_segments: Transcript segments to analyze
            engine_types: List of engine names to run ('ATO', 'SEM', 'CLU', 'MEMA')
            
        Returns:
            Dictionary mapping engine names to their detected markers
        """
        results = {}
        
        for engine_type in engine_types:
            if engine_type in self.engines:
                engine = self.engines[engine_type]
                markers = engine.analyze_transcript_segments(transcript_segments)
                results[engine_type] = markers
                logger.info(f"{engine_type} engine detected {len(markers)} markers")
            else:
                logger.warning(f"Engine {engine_type} not available in current configuration")
                results[engine_type] = []
        
        return results
    
    def validate_markers(self, markers: List[MarkerEvent], strict: bool = False) -> Tuple[bool, List[str]]:
        """
        Validate detected markers for constitutional compliance
        
        Args:
            markers: List of markers to validate
            strict: Whether to apply strict validation rules
            
        Returns:
            Tuple of (is_valid, validation_errors)
        """
        errors = []
        
        for marker in markers:
            # Constitutional source validation
            if marker.constitutional_source != self.constitutional_source:
                errors.append(f"Marker {marker.id} has incorrect constitutional source: "
                            f"{marker.constitutional_source}")
            
            # Analysis method validation
            if marker.analysis_method != self.analysis_method:
                errors.append(f"Marker {marker.id} has incorrect analysis method: "
                            f"{marker.analysis_method}")
            
            # Confidence threshold validation
            if marker.confidence < self.config.confidence_threshold:
                errors.append(f"Marker {marker.id} below confidence threshold: "
                            f"{marker.confidence:.3f} < {self.config.confidence_threshold}")
            
            # Temporal consistency validation
            if marker.start_time > marker.end_time:
                errors.append(f"Marker {marker.id} has invalid time range: "
                            f"{marker.start_time} > {marker.end_time}")
            
            # Evidence validation
            if not marker.evidence or not marker.evidence.strip():
                errors.append(f"Marker {marker.id} has empty evidence")
            
            if strict:
                # Strict validation: require explanation and subtype
                if not marker.explanation:
                    errors.append(f"Marker {marker.id} missing explanation (strict mode)")
                
                if not marker.marker_subtype:
                    errors.append(f"Marker {marker.id} missing subtype (strict mode)")
        
        # Check for temporal overlaps (strict mode)
        if strict and len(markers) > 1:
            sorted_markers = sorted(markers, key=lambda m: m.start_time)
            for i in range(len(sorted_markers) - 1):
                current = sorted_markers[i]
                next_marker = sorted_markers[i + 1]
                
                if (current.end_time > next_marker.start_time and 
                    current.speaker == next_marker.speaker):
                    errors.append(f"Temporal overlap detected between markers {current.id} "
                                f"and {next_marker.id} for same speaker")
        
        is_valid = len(errors) == 0
        
        if is_valid:
            logger.info(f"Marker validation passed: {len(markers)} markers validated")
        else:
            logger.warning(f"Marker validation failed: {len(errors)} errors found")
        
        return is_valid, errors
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Get information about configured engines"""
        return {
            'engines': list(self.engines.keys()),
            'configuration': {
                'confidence_threshold': self.config.confidence_threshold,
                'constitutional_source': self.constitutional_source,
                'analysis_method': self.analysis_method,
                'rapport_enabled': self.rapport_calculator is not None
            },
            'engine_details': {
                name: {
                    'type': engine.__class__.__name__,
                    'marker_type': getattr(engine, 'marker_type', 'unknown'),
                    'patterns': len(getattr(engine, f'{name.lower()}_patterns', []))
                }
                for name, engine in self.engines.items()
            }
        }