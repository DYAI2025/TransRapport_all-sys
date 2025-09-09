"""
MEMA (Memory) Marker Engine
Detects memory-related conversational markers following LD-3.4 constitution
CONSTITUTIONAL COMPLIANCE: Uses existing LD-3.4 framework, no CLI modifications
"""

import re
import logging
from typing import Dict, List, Optional, Any

from src.models.marker_event import MarkerEvent, MarkerType
from .ato_engine import AttentionPattern

logger = logging.getLogger(__name__)


class MEMAMarkerEngine:
    """
    MEMA (Memory) Marker Detection Engine
    Detects memory references, shared conversational memory, and memory alignment
    """
    
    def __init__(self, confidence_threshold: float = 0.7):
        self.marker_type = "MEMA"
        self.confidence_threshold = confidence_threshold
        self.constitutional_source = "LD-3.4-constitution"
        self.analysis_method = "LD-3.4"
        
        self.memory_patterns = self._load_constitutional_memory_patterns()
        
        logger.info(f"MEMA marker engine initialized (threshold: {confidence_threshold})")
    
    def _load_constitutional_memory_patterns(self) -> List[AttentionPattern]:
        """Load constitutional memory reference patterns"""
        
        return [
            AttentionPattern(
                pattern_id="mema_reference_explicit",
                keywords=["remember", "recall", "as we discussed", "like we talked about", "you mentioned"],
                regex_patterns=[
                    r"\b(?:remember|recall)\s+(?:when|how|that|what)\b",
                    r"\b(?:as we discussed|like we talked about|you mentioned)\b",
                    r"\b(?:last time|previously|earlier|before)\s+(?:we|you|I)\s+(?:said|talked|discussed)\b"
                ],
                marker_subtype="memory_reference",
                confidence_weight=0.9
            ),
            
            AttentionPattern(
                pattern_id="mema_alignment_shared",
                keywords=["we both remember", "as we know", "we established", "we agreed"],
                regex_patterns=[
                    r"\b(?:we both remember|as we know|we established|we agreed)\b",
                    r"\b(?:we've established|we determined|we concluded)\s+(?:that|how)\b",
                    r"\b(?:our understanding|our agreement|our discussion)\s+(?:was|is)\b"
                ],
                marker_subtype="memory_alignment",
                confidence_weight=0.85
            ),
            
            AttentionPattern(
                pattern_id="mema_correction_update",
                keywords=["actually", "correction", "I misspoke", "let me clarify", "to correct"],
                regex_patterns=[
                    r"\b(?:actually|correction|I misspoke|let me clarify|to correct)\b",
                    r"\b(?:I meant to say|what I meant was|to be more accurate)\b",
                    r"\b(?:I should clarify|let me rephrase|more precisely)\b"
                ],
                marker_subtype="memory_correction",
                confidence_weight=0.8
            ),
            
            AttentionPattern(
                pattern_id="mema_expansion_elaboration",
                keywords=["building on", "adding to", "expanding on", "to elaborate", "furthermore"],
                regex_patterns=[
                    r"\b(?:building on|adding to|expanding on|to elaborate|furthermore)\b",
                    r"\b(?:to add to that|in addition to|along with)\s+(?:what|that)\b",
                    r"\b(?:related to|connected to|following up on)\s+(?:what|that|our)\b"
                ],
                marker_subtype="memory_expansion",
                confidence_weight=0.8
            ),
            
            AttentionPattern(
                pattern_id="mema_integration_synthesis",
                keywords=["putting it together", "connecting", "synthesis", "overall", "in summary"],
                regex_patterns=[
                    r"\b(?:putting it together|connecting|synthesis|overall|in summary)\b",
                    r"\b(?:bringing together|combining|integrating)\s+(?:what|our|these)\b",
                    r"\b(?:the big picture|overall understanding|complete picture)\b"
                ],
                marker_subtype="memory_integration",
                confidence_weight=0.85
            )
        ]
    
    def analyze_transcript_segments(self, transcript_segments: List[Dict[str, Any]]) -> List[MarkerEvent]:
        """Analyze transcript segments for MEMA markers"""
        detected_markers = []
        
        for i, segment in enumerate(transcript_segments):
            context = self._get_memory_context(transcript_segments, i)
            segment_markers = self._detect_memory_markers(segment, context)
            detected_markers.extend(segment_markers)
        
        processed_markers = self._process_memory_relationships(detected_markers)
        
        logger.info(f"MEMA analysis completed: {len(processed_markers)} markers detected")
        return processed_markers
    
    def _get_memory_context(self, segments: List[Dict[str, Any]], current_index: int) -> Dict[str, Any]:
        """Get memory context for segment analysis"""
        context = {
            'current_segment': segments[current_index],
            'previous_segments': segments[max(0, current_index-5):current_index],  # Longer memory window
            'conversation_history': segments[:current_index],
            'temporal_distance': current_index * 10.0  # Approximate time from start
        }
        
        # Build topic/theme tracking for memory references
        context['referenced_topics'] = self._extract_topics_from_history(context['conversation_history'])
        
        return context
    
    def _extract_topics_from_history(self, history: List[Dict[str, Any]]) -> List[str]:
        """Extract key topics from conversation history for memory reference validation"""
        topics = []
        
        # Simple keyword extraction for topic tracking
        topic_keywords = set()
        for segment in history:
            text = segment.get('text', '').lower()
            # Extract potential topic words (nouns, important adjectives)
            words = re.findall(r'\b[a-z]{4,}\b', text)  # Words 4+ chars
            topic_keywords.update(words)
        
        # Filter to most relevant topics (simplified approach)
        topics = list(topic_keywords)[:20]  # Top 20 potential topics
        return topics
    
    def _detect_memory_markers(self, segment: Dict[str, Any], context: Dict[str, Any]) -> List[MarkerEvent]:
        """Detect memory markers in segment"""
        markers = []
        text = segment.get('text', '').strip()
        
        if not text:
            return markers
        
        for pattern in self.memory_patterns:
            confidence = self._calculate_memory_confidence(text, pattern, context)
            
            if confidence >= self.confidence_threshold:
                marker = self._create_memory_marker(pattern, segment, context, confidence)
                markers.append(marker)
        
        return markers
    
    def _calculate_memory_confidence(self, text: str, pattern: AttentionPattern,
                                   context: Dict[str, Any]) -> float:
        """Calculate memory pattern confidence"""
        text_lower = text.lower()
        
        # Lexical matching
        keyword_matches = sum(1 for keyword in pattern.keywords if keyword.lower() in text_lower)
        lexical_score = min(keyword_matches / len(pattern.keywords), 1.0) * 0.5
        
        # Regex matching
        regex_matches = sum(1 for regex in pattern.regex_patterns
                           if re.search(regex, text, re.IGNORECASE))
        regex_score = min(regex_matches / len(pattern.regex_patterns), 1.0) * 0.5
        
        # Memory context evaluation
        memory_context_score = self._evaluate_memory_context(pattern, context)
        
        # Temporal consistency (memory references should make temporal sense)
        temporal_score = self._evaluate_temporal_consistency(pattern, context)
        
        total_confidence = (
            lexical_score + regex_score + 
            memory_context_score * 0.3 + temporal_score * 0.2
        ) * pattern.confidence_weight
        
        return min(total_confidence, 1.0)
    
    def _evaluate_memory_context(self, pattern: AttentionPattern, context: Dict[str, Any]) -> float:
        """Evaluate memory context appropriateness"""
        
        if pattern.marker_subtype == "memory_reference":
            # Reference should connect to earlier content
            current_text = context['current_segment'].get('text', '').lower()
            history_text = ' '.join(seg.get('text', '') for seg in context['conversation_history']).lower()
            
            # Look for topic continuity
            current_words = set(re.findall(r'\b[a-z]{3,}\b', current_text))
            history_words = set(re.findall(r'\b[a-z]{3,}\b', history_text))
            
            overlap = len(current_words.intersection(history_words))
            if overlap > 2:  # Meaningful topic overlap
                return 0.9
            elif overlap > 0:
                return 0.6
            return 0.4
            
        elif pattern.marker_subtype == "memory_alignment":
            # Alignment requires shared conversational history
            if len(context['conversation_history']) > 5:  # Sufficient history for alignment
                return 0.8
            return 0.5
            
        elif pattern.marker_subtype == "memory_correction":
            # Correction should reference recent statements
            recent_text = ' '.join(seg.get('text', '') for seg in context['previous_segments'][-3:])
            if recent_text:
                return 0.8
            return 0.4
            
        elif pattern.marker_subtype == "memory_expansion":
            # Expansion builds on previous content
            if context['previous_segments']:
                return 0.7
            return 0.4
            
        elif pattern.marker_subtype == "memory_integration":
            # Integration requires substantial conversation history
            if len(context['conversation_history']) > 10:
                return 0.9
            elif len(context['conversation_history']) > 5:
                return 0.7
            return 0.4
        
        return 0.6
    
    def _evaluate_temporal_consistency(self, pattern: AttentionPattern, context: Dict[str, Any]) -> float:
        """Evaluate temporal consistency of memory references"""
        current_text = context['current_segment'].get('text', '').lower()
        
        # Check for temporal markers
        recent_markers = ['just now', 'recently', 'a moment ago', 'earlier']
        distant_markers = ['long ago', 'much earlier', 'at the beginning', 'initially']
        
        has_recent_marker = any(marker in current_text for marker in recent_markers)
        has_distant_marker = any(marker in current_text for marker in distant_markers)
        
        conversation_length = len(context['conversation_history'])
        
        if pattern.marker_subtype == "memory_reference":
            if has_recent_marker and conversation_length > 2:
                return 0.8
            elif has_distant_marker and conversation_length > 10:
                return 0.8
            elif conversation_length > 5:  # General memory reference
                return 0.7
            return 0.5
        
        return 0.7
    
    def _create_memory_marker(self, pattern: AttentionPattern, segment: Dict[str, Any],
                            context: Dict[str, Any], confidence: float) -> MarkerEvent:
        """Create MEMA marker event"""
        
        explanations = {
            "memory_reference": "Speaker making explicit reference to previous conversational content or shared memory",
            "memory_alignment": "Speakers demonstrating shared conversational memory and aligned understanding",
            "memory_correction": "Speaker correcting or updating previous statements or shared understanding",
            "memory_expansion": "Speaker expanding on or elaborating previous conversational content",
            "memory_integration": "Speaker integrating multiple conversational memories into coherent understanding"
        }
        
        explanation = explanations.get(pattern.marker_subtype, "Memory-related marker detected")
        
        # Add temporal context to explanation
        conversation_length = len(context['conversation_history'])
        if conversation_length > 0:
            explanation += f" (referencing conversation history of {conversation_length} segments)"
        
        marker = MarkerEvent(
            marker_type=MarkerType.MEMA,
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
    
    def _process_memory_relationships(self, markers: List[MarkerEvent]) -> List[MarkerEvent]:
        """Process relationships between memory markers"""
        markers.sort(key=lambda m: m.start_time)
        
        # Identify correction->expansion chains
        for i, marker in enumerate(markers):
            if marker.marker_subtype == "memory_correction":
                # Look for expansion or integration that follows
                for j in range(i + 1, min(i + 3, len(markers))):
                    next_marker = markers[j]
                    if (next_marker.marker_subtype in ["memory_expansion", "memory_integration"] and
                        next_marker.start_time - marker.end_time <= 60.0):  # 1-minute window
                        marker.add_related_marker(next_marker.id)
                        next_marker.add_related_marker(marker.id)
        
        # Identify reference->alignment chains
        for i, marker in enumerate(markers):
            if marker.marker_subtype == "memory_reference":
                for j in range(i + 1, min(i + 3, len(markers))):
                    next_marker = markers[j]
                    if (next_marker.marker_subtype == "memory_alignment" and
                        next_marker.start_time - marker.end_time <= 45.0):
                        marker.add_related_marker(next_marker.id)
                        next_marker.add_related_marker(marker.id)
        
        return markers