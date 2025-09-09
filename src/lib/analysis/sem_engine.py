"""
SEM (Semantic) Marker Engine
Detects semantic alignment and meaning-related markers following LD-3.4 constitution
CONSTITUTIONAL COMPLIANCE: Uses existing LD-3.4 framework, no CLI modifications
"""

import re
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from src.models.marker_event import MarkerEvent, MarkerType
from .ato_engine import AttentionPattern  # Reuse pattern structure

logger = logging.getLogger(__name__)


class SEMMarkerEngine:
    """
    SEM (Semantic) Marker Detection Engine
    Detects semantic alignment, understanding, and meaning construction
    """
    
    def __init__(self, confidence_threshold: float = 0.7):
        self.marker_type = "SEM"
        self.confidence_threshold = confidence_threshold
        self.constitutional_source = "LD-3.4-constitution"
        self.analysis_method = "LD-3.4"
        
        self.semantic_patterns = self._load_constitutional_semantic_patterns()
        
        logger.info(f"SEM marker engine initialized (threshold: {confidence_threshold})")
    
    def _load_constitutional_semantic_patterns(self) -> List[AttentionPattern]:
        """Load constitutional semantic alignment patterns"""
        
        return [
            AttentionPattern(
                pattern_id="sem_alignment_agreement",
                keywords=["exactly", "precisely", "that's right", "correct", "yes", "absolutely"],
                regex_patterns=[
                    r"\b(?:exactly|precisely|that's\s+right|absolutely)\b",
                    r"\b(?:yes|yeah)\s*[,.]?\s*(?:exactly|that's\s+it|correct)\b",
                    r"\b(?:I agree|you're right|that makes sense)\b"
                ],
                marker_subtype="semantic_alignment",
                confidence_weight=0.9
            ),
            
            AttentionPattern(
                pattern_id="sem_clarification_request",
                keywords=["what do you mean", "can you explain", "I don't understand", "clarify"],
                regex_patterns=[
                    r"\b(?:what do you mean|can you explain|I don't understand)\b",
                    r"\b(?:can you clarify|what does that mean|I'm not sure)\b",
                    r"\b(?:could you elaborate|tell me more about)\b"
                ],
                marker_subtype="semantic_clarification",
                confidence_weight=0.85
            ),
            
            AttentionPattern(
                pattern_id="sem_understanding_demonstration",
                keywords=["I understand", "I see", "so you're saying", "in other words"],
                regex_patterns=[
                    r"\b(?:I understand|I see|I get it)\b",
                    r"\b(?:so you're saying|in other words|what I hear)\b",
                    r"\b(?:if I understand correctly|so what you mean)\b"
                ],
                marker_subtype="semantic_understanding",
                confidence_weight=0.85
            ),
            
            AttentionPattern(
                pattern_id="sem_expansion_elaboration",
                keywords=["furthermore", "additionally", "also", "moreover", "building on"],
                regex_patterns=[
                    r"\b(?:furthermore|additionally|moreover|also)\b",
                    r"\b(?:building on|expanding on|to add to)\b",
                    r"\b(?:another point|related to that|similarly)\b"
                ],
                marker_subtype="semantic_expansion",
                confidence_weight=0.8
            ),
            
            AttentionPattern(
                pattern_id="sem_contradiction_disagreement",
                keywords=["I disagree", "that's not right", "actually", "however", "but"],
                regex_patterns=[
                    r"\b(?:I disagree|that's not right|I don't think so)\b",
                    r"\b(?:actually|however|but)\s+(?:I think|I believe|I feel)\b",
                    r"\b(?:on the contrary|I see it differently)\b"
                ],
                marker_subtype="semantic_divergence",
                confidence_weight=0.8
            )
        ]
    
    def analyze_transcript_segments(self, transcript_segments: List[Dict[str, Any]]) -> List[MarkerEvent]:
        """Analyze transcript segments for SEM markers"""
        detected_markers = []
        
        for i, segment in enumerate(transcript_segments):
            context = self._get_segment_context(transcript_segments, i)
            segment_markers = self._detect_semantic_markers(segment, context)
            detected_markers.extend(segment_markers)
        
        processed_markers = self._process_semantic_relationships(detected_markers)
        
        logger.info(f"SEM analysis completed: {len(processed_markers)} markers detected")
        return processed_markers
    
    def _get_segment_context(self, segments: List[Dict[str, Any]], current_index: int) -> Dict[str, Any]:
        """Get semantic context around segment"""
        context = {
            'current_segment': segments[current_index],
            'previous_segments': segments[max(0, current_index-2):current_index],
            'next_segments': segments[current_index+1:min(len(segments), current_index+3)],
            'semantic_continuity': True
        }
        return context
    
    def _detect_semantic_markers(self, segment: Dict[str, Any], context: Dict[str, Any]) -> List[MarkerEvent]:
        """Detect semantic markers in segment"""
        markers = []
        text = segment.get('text', '').strip()
        
        if not text:
            return markers
        
        for pattern in self.semantic_patterns:
            confidence = self._calculate_semantic_confidence(text, pattern, context)
            
            if confidence >= self.confidence_threshold:
                marker = self._create_semantic_marker(pattern, segment, context, confidence)
                markers.append(marker)
        
        return markers
    
    def _calculate_semantic_confidence(self, text: str, pattern: AttentionPattern, 
                                     context: Dict[str, Any]) -> float:
        """Calculate semantic pattern confidence"""
        text_lower = text.lower()
        
        # Lexical matching
        keyword_matches = sum(1 for keyword in pattern.keywords if keyword.lower() in text_lower)
        lexical_score = min(keyword_matches / len(pattern.keywords), 1.0) * 0.5
        
        # Regex matching
        regex_matches = sum(1 for regex in pattern.regex_patterns 
                           if re.search(regex, text, re.IGNORECASE))
        regex_score = min(regex_matches / len(pattern.regex_patterns), 1.0) * 0.5
        
        # Semantic context evaluation
        context_score = self._evaluate_semantic_context(pattern, context)
        
        total_confidence = (lexical_score + regex_score + context_score * 0.3) * pattern.confidence_weight
        return min(total_confidence, 1.0)
    
    def _evaluate_semantic_context(self, pattern: AttentionPattern, context: Dict[str, Any]) -> float:
        """Evaluate semantic context appropriateness"""
        # Check if semantic marker makes sense in conversation flow
        previous_text = ' '.join(seg.get('text', '') for seg in context['previous_segments'])
        
        if pattern.marker_subtype == "semantic_alignment":
            # Alignment should follow statements or questions
            return 0.8 if previous_text else 0.5
            
        elif pattern.marker_subtype == "semantic_clarification":
            # Clarification requests suggest confusion or complexity
            complex_indicators = ['technical', 'complex', 'difficult', 'unclear']
            if any(indicator in previous_text.lower() for indicator in complex_indicators):
                return 0.9
            return 0.6
            
        elif pattern.marker_subtype == "semantic_understanding":
            # Understanding follows explanation or discussion
            explanation_indicators = ['because', 'therefore', 'so', 'thus', 'hence']
            if any(indicator in previous_text.lower() for indicator in explanation_indicators):
                return 0.8
            return 0.6
            
        return 0.7
    
    def _create_semantic_marker(self, pattern: AttentionPattern, segment: Dict[str, Any],
                              context: Dict[str, Any], confidence: float) -> MarkerEvent:
        """Create SEM marker event"""
        
        explanations = {
            "semantic_alignment": "Speaker demonstrates semantic alignment and agreement with previous statements",
            "semantic_clarification": "Speaker requests clarification or demonstrates semantic uncertainty",
            "semantic_understanding": "Speaker demonstrates semantic understanding and comprehension",
            "semantic_expansion": "Speaker expands semantic content building on previous statements",
            "semantic_divergence": "Speaker expresses semantic disagreement or alternative perspective"
        }
        
        explanation = explanations.get(pattern.marker_subtype, "Semantic marker detected")
        
        marker = MarkerEvent(
            marker_type=MarkerType.SEM,
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
    
    def _process_semantic_relationships(self, markers: List[MarkerEvent]) -> List[MarkerEvent]:
        """Process relationships between semantic markers"""
        # Remove overlapping markers and identify semantic chains
        markers.sort(key=lambda m: m.start_time)
        
        # Identify clarification->understanding chains
        for i, marker in enumerate(markers):
            if marker.marker_subtype == "semantic_clarification":
                # Look for understanding markers that follow
                for j in range(i + 1, min(i + 3, len(markers))):
                    next_marker = markers[j]
                    if (next_marker.marker_subtype == "semantic_understanding" and
                        next_marker.start_time - marker.end_time <= 30.0):
                        marker.add_related_marker(next_marker.id)
                        next_marker.add_related_marker(marker.id)
                        break
        
        return markers