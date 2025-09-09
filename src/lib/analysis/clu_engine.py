"""
CLU (Cluster) Marker Engine  
Detects cluster formation and shared understanding markers following LD-3.4 constitution
CONSTITUTIONAL COMPLIANCE: Uses existing LD-3.4 framework, no CLI modifications
"""

import re
import logging
from typing import Dict, List, Optional, Any

from src.models.marker_event import MarkerEvent, MarkerType
from .ato_engine import AttentionPattern

logger = logging.getLogger(__name__)


class CLUMarkerEngine:
    """
    CLU (Cluster) Marker Detection Engine
    Detects cluster formation, shared understanding, and collective recognition
    """
    
    def __init__(self, confidence_threshold: float = 0.7):
        self.marker_type = "CLU" 
        self.confidence_threshold = confidence_threshold
        self.constitutional_source = "LD-3.4-constitution"
        self.analysis_method = "LD-3.4"
        
        self.cluster_patterns = self._load_constitutional_cluster_patterns()
        
        logger.info(f"CLU marker engine initialized (threshold: {confidence_threshold})")
    
    def _load_constitutional_cluster_patterns(self) -> List[AttentionPattern]:
        """Load constitutional cluster formation patterns"""
        
        return [
            AttentionPattern(
                pattern_id="clu_formation_collective",
                keywords=["we", "us", "our", "together", "both", "all of us"],
                regex_patterns=[
                    r"\b(?:we|us|our)\s+(?:both|all|together)\b",
                    r"\b(?:we both|both of us|all of us)\s+(?:understand|agree|see)\b",
                    r"\b(?:together|collectively|as a group)\s+(?:we|can|should)\b"
                ],
                marker_subtype="cluster_formation",
                confidence_weight=0.9
            ),
            
            AttentionPattern(
                pattern_id="clu_recognition_shared",
                keywords=["we both know", "as we discussed", "we agree", "we understand"],
                regex_patterns=[
                    r"\b(?:we both know|as we discussed|we agree|we understand)\b",
                    r"\b(?:we're on the same page|we see eye to eye)\b",
                    r"\b(?:we both realize|we recognize|we acknowledge)\b"
                ],
                marker_subtype="cluster_recognition",
                confidence_weight=0.85
            ),
            
            AttentionPattern(
                pattern_id="clu_reinforcement_mutual",
                keywords=["exactly", "right", "absolutely", "that's what I was thinking"],
                regex_patterns=[
                    r"\b(?:exactly|absolutely|right)\s*[!.]?\s*(?:that's|yes|indeed)\b",
                    r"\b(?:that's what I was thinking|I was thinking the same)\b",
                    r"\b(?:my thoughts exactly|couldn't agree more)\b"
                ],
                marker_subtype="cluster_reinforcement", 
                confidence_weight=0.8
            ),
            
            AttentionPattern(
                pattern_id="clu_dissolution_separation",
                keywords=["I disagree", "I see it differently", "actually", "but I think"],
                regex_patterns=[
                    r"\b(?:I disagree|I see it differently|I don't think so)\b",
                    r"\b(?:actually|but|however)\s+(?:I think|I believe|I feel)\b",
                    r"\b(?:on the other hand|from my perspective|I would say)\b"
                ],
                marker_subtype="cluster_dissolution",
                confidence_weight=0.8
            ),
            
            AttentionPattern(
                pattern_id="clu_transition_shifting",
                keywords=["moving on", "let's consider", "what about", "another perspective"],
                regex_patterns=[
                    r"\b(?:moving on|let's consider|what about|another perspective)\b",
                    r"\b(?:shifting focus|changing topics|different angle)\b",
                    r"\b(?:on a related note|speaking of|that reminds me)\b"
                ],
                marker_subtype="cluster_transition",
                confidence_weight=0.75
            )
        ]
    
    def analyze_transcript_segments(self, transcript_segments: List[Dict[str, Any]]) -> List[MarkerEvent]:
        """Analyze transcript segments for CLU markers"""
        detected_markers = []
        
        for i, segment in enumerate(transcript_segments):
            context = self._get_cluster_context(transcript_segments, i)
            segment_markers = self._detect_cluster_markers(segment, context)
            detected_markers.extend(segment_markers)
        
        processed_markers = self._process_cluster_relationships(detected_markers)
        
        logger.info(f"CLU analysis completed: {len(processed_markers)} markers detected")
        return processed_markers
    
    def _get_cluster_context(self, segments: List[Dict[str, Any]], current_index: int) -> Dict[str, Any]:
        """Get cluster formation context"""
        context = {
            'current_segment': segments[current_index],
            'previous_segments': segments[max(0, current_index-3):current_index],
            'speaker_history': [],
            'topic_continuity': True
        }
        
        # Build speaker interaction history
        for seg in context['previous_segments'] + [context['current_segment']]:
            context['speaker_history'].append(seg.get('speaker', 'unknown'))
        
        return context
    
    def _detect_cluster_markers(self, segment: Dict[str, Any], context: Dict[str, Any]) -> List[MarkerEvent]:
        """Detect cluster markers in segment"""
        markers = []
        text = segment.get('text', '').strip()
        
        if not text:
            return markers
        
        for pattern in self.cluster_patterns:
            confidence = self._calculate_cluster_confidence(text, pattern, context)
            
            if confidence >= self.confidence_threshold:
                marker = self._create_cluster_marker(pattern, segment, context, confidence)
                markers.append(marker)
        
        return markers
    
    def _calculate_cluster_confidence(self, text: str, pattern: AttentionPattern,
                                   context: Dict[str, Any]) -> float:
        """Calculate cluster pattern confidence"""
        text_lower = text.lower()
        
        # Lexical matching
        keyword_matches = sum(1 for keyword in pattern.keywords if keyword.lower() in text_lower)
        lexical_score = min(keyword_matches / len(pattern.keywords), 1.0) * 0.6
        
        # Regex matching  
        regex_matches = sum(1 for regex in pattern.regex_patterns
                           if re.search(regex, text, re.IGNORECASE))
        regex_score = min(regex_matches / len(pattern.regex_patterns), 1.0) * 0.4
        
        # Cluster context evaluation
        context_score = self._evaluate_cluster_context(pattern, context)
        
        # Speaker interaction patterns
        interaction_score = self._evaluate_speaker_interactions(pattern, context)
        
        total_confidence = (
            lexical_score + regex_score + 
            context_score * 0.25 + interaction_score * 0.25
        ) * pattern.confidence_weight
        
        return min(total_confidence, 1.0)
    
    def _evaluate_cluster_context(self, pattern: AttentionPattern, context: Dict[str, Any]) -> float:
        """Evaluate cluster formation context"""
        previous_text = ' '.join(seg.get('text', '') for seg in context['previous_segments'])
        
        if pattern.marker_subtype == "cluster_formation":
            # Formation should happen after individual statements
            individual_indicators = ['I think', 'I believe', 'my view', 'personally']
            if any(indicator in previous_text.lower() for indicator in individual_indicators):
                return 0.9
            return 0.6
            
        elif pattern.marker_subtype == "cluster_recognition":
            # Recognition should follow discussion or agreement
            discussion_indicators = ['discussed', 'talked about', 'mentioned', 'said']
            if any(indicator in previous_text.lower() for indicator in discussion_indicators):
                return 0.8
            return 0.6
            
        elif pattern.marker_subtype == "cluster_reinforcement":
            # Reinforcement should follow alignment or agreement
            alignment_indicators = ['agree', 'exactly', 'right', 'correct', 'yes']
            if any(indicator in previous_text.lower() for indicator in alignment_indicators):
                return 0.8
            return 0.5
        
        return 0.7
    
    def _evaluate_speaker_interactions(self, pattern: AttentionPattern, context: Dict[str, Any]) -> float:
        """Evaluate speaker interaction patterns for cluster formation"""
        speaker_history = context['speaker_history']
        
        if len(speaker_history) < 2:
            return 0.5
        
        current_speaker = speaker_history[-1]
        
        # Cluster formation benefits from multi-speaker participation
        unique_speakers = len(set(speaker_history))
        speaker_diversity = min(unique_speakers / 3, 1.0)  # Normalize to max 3 speakers
        
        if pattern.marker_subtype == "cluster_formation":
            # Formation benefits from multiple speakers contributing
            return 0.3 + (speaker_diversity * 0.7)
            
        elif pattern.marker_subtype == "cluster_recognition":
            # Recognition can come from any speaker but benefits from consensus
            return 0.5 + (speaker_diversity * 0.5)
            
        elif pattern.marker_subtype == "cluster_reinforcement":
            # Reinforcement often involves back-and-forth confirmation
            recent_changes = len(set(speaker_history[-3:])) if len(speaker_history) >= 3 else 1
            return 0.4 + (min(recent_changes / 2, 1.0) * 0.6)
        
        return 0.6
    
    def _create_cluster_marker(self, pattern: AttentionPattern, segment: Dict[str, Any],
                             context: Dict[str, Any], confidence: float) -> MarkerEvent:
        """Create CLU marker event"""
        
        explanations = {
            "cluster_formation": "Speakers forming collective understanding or shared perspective",
            "cluster_recognition": "Recognition of shared understanding or collective agreement", 
            "cluster_reinforcement": "Reinforcement of established cluster or shared viewpoint",
            "cluster_dissolution": "Dissolution or challenge to established cluster understanding",
            "cluster_transition": "Transition between different cluster formations or topics"
        }
        
        explanation = explanations.get(pattern.marker_subtype, "Cluster formation marker detected")
        
        # Add speaker context to explanation
        speaker_count = len(set(context['speaker_history']))
        if speaker_count > 1:
            explanation += f" involving {speaker_count} speakers"
        
        marker = MarkerEvent(
            marker_type=MarkerType.CLU,
            start_time=segment.get('start_time', 0.0),
            end_time=segment.get('end_time', 0.0),
            confidence=confidence,
            evidence=segment.get('text', '').strip(),
            explanation=explanation,
            marker_subtype=pattern.marker_subtype,
            speaker=segment.get('speaker'),
            constitutional_source=self.constitutional_source,
            analysis_method=self.analysis_method
        )
        
        return marker
    
    def _process_cluster_relationships(self, markers: List[MarkerEvent]) -> List[MarkerEvent]:
        """Process relationships between cluster markers"""
        markers.sort(key=lambda m: m.start_time)
        
        # Identify cluster formation sequences
        for i, marker in enumerate(markers):
            if marker.marker_subtype == "cluster_formation":
                # Look for reinforcement markers that follow
                for j in range(i + 1, min(i + 4, len(markers))):
                    next_marker = markers[j]
                    if (next_marker.marker_subtype == "cluster_reinforcement" and
                        next_marker.start_time - marker.end_time <= 45.0):
                        marker.add_related_marker(next_marker.id)
                        next_marker.add_related_marker(marker.id)
        
        return markers