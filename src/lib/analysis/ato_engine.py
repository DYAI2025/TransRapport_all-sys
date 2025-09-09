"""
ATO (Attention) Marker Engine
Detects attention-related conversational markers following LD-3.4 constitution
CONSTITUTIONAL COMPLIANCE: Uses existing LD-3.4 framework, no CLI modifications
"""

import re
import time
import uuid
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

from src.models.marker_event import MarkerEvent, MarkerType

logger = logging.getLogger(__name__)


@dataclass
class AttentionPattern:
    """Attention detection pattern"""
    pattern_id: str
    keywords: List[str]
    regex_patterns: List[str]
    marker_subtype: str
    confidence_weight: float
    context_requirements: Dict[str, Any] = field(default_factory=dict)


class ATOMarkerEngine:
    """
    ATO (Attention) Marker Detection Engine
    
    Constitutional compliance:
    - Uses existing LD-3.4 constitutional framework
    - Library reuse approach (no CLI modifications)
    - Constitutional marker pattern definitions
    """
    
    def __init__(self, confidence_threshold: float = 0.7, 
                 enable_evidence_collection: bool = True):
        self.marker_type = "ATO"
        self.confidence_threshold = confidence_threshold
        self.evidence_collection_enabled = enable_evidence_collection
        self.constitutional_source = "LD-3.4-constitution"
        self.analysis_method = "LD-3.4"
        
        # Load constitutional attention patterns
        self.attention_patterns = self._load_constitutional_patterns()
        
        logger.info(f"ATO marker engine initialized (threshold: {confidence_threshold})")
    
    def _load_constitutional_patterns(self) -> List[AttentionPattern]:
        """Load constitutional LD-3.4 attention patterns (library reuse)"""
        
        # Constitutional attention direction patterns
        attention_patterns = [
            AttentionPattern(
                pattern_id="ato_direction_focus",
                keywords=["focus", "concentrate", "pay attention", "look at", "notice"],
                regex_patterns=[
                    r"\b(?:focus|concentrate|pay attention)\s+(?:on|to)\b",
                    r"\b(?:look at|notice|observe)\s+(?:this|that|how)\b",
                    r"\bI want you to\s+(?:focus|notice|see|look)\b"
                ],
                marker_subtype="attention_direction",
                confidence_weight=0.9,
                context_requirements={
                    "speaker_change": False,  # Usually same speaker directing
                    "imperative_mood": True   # Commands/requests
                }
            ),
            
            AttentionPattern(
                pattern_id="ato_acknowledgment_recognition",
                keywords=["I see", "oh", "ah", "right", "yes", "understand", "got it"],
                regex_patterns=[
                    r"\b(?:I see|oh|ah|right)\s+(?:what you mean|now|that)\b",
                    r"\b(?:yes|yeah|okay)\s*[,.]?\s*(?:I see|I understand|I get it)\b",
                    r"\b(?:that makes sense|I understand|got it|I follow)\b"
                ],
                marker_subtype="attention_acknowledgment",
                confidence_weight=0.85,
                context_requirements={
                    "follows_direction": True,   # Usually after direction
                    "speaker_change": True       # Different speaker responding
                }
            ),
            
            AttentionPattern(
                pattern_id="ato_shift_redirection",
                keywords=["wait", "actually", "but", "however", "let me", "hold on"],
                regex_patterns=[
                    r"\b(?:wait|hold on|actually)\s*[,.]?\s*(?:let me|I want to|can we)\b",
                    r"\b(?:but|however|although)\s+(?:I think|what about|consider)\b",
                    r"\b(?:let me|can we|what if we)\s+(?:focus|look at|consider)\b"
                ],
                marker_subtype="attention_shift", 
                confidence_weight=0.8,
                context_requirements={
                    "interruption_marker": True,
                    "redirection": True
                }
            ),
            
            AttentionPattern(
                pattern_id="ato_maintenance_sustained",
                keywords=["keep", "continue", "stay", "remain", "maintain", "don't lose"],
                regex_patterns=[
                    r"\b(?:keep|continue|stay|remain)\s+(?:focused|focused on|looking at)\b",
                    r"\b(?:maintain|hold)\s+(?:your|that|this)\s+(?:focus|attention)\b",
                    r"\b(?:don't lose|stay with|keep on)\s+(?:focus|track|attention)\b"
                ],
                marker_subtype="attention_maintenance",
                confidence_weight=0.75,
                context_requirements={
                    "sustained_attention": True,
                    "duration_context": True
                }
            ),
            
            AttentionPattern(
                pattern_id="ato_focus_specification",
                keywords=["specifically", "particularly", "especially", "in particular", "precisely"],
                regex_patterns=[
                    r"\b(?:specifically|particularly|especially|precisely)\s+(?:focus|look|notice)\b",
                    r"\b(?:focus|pay attention)\s+(?:specifically|particularly)\s+(?:on|to)\b",
                    r"\bin particular\s*[,.]?\s*(?:notice|see|focus on)\b"
                ],
                marker_subtype="attention_focus",
                confidence_weight=0.85,
                context_requirements={
                    "specificity_marker": True,
                    "directed_attention": True
                }
            )
        ]
        
        return attention_patterns
    
    def get_attention_patterns(self) -> List[Dict[str, Any]]:
        """Get constitutional attention patterns for validation"""
        return [
            {
                'id': pattern.pattern_id,
                'keywords': pattern.keywords,
                'subtype': pattern.marker_subtype,
                'constitutional_source': self.constitutional_source
            }
            for pattern in self.attention_patterns
        ]
    
    def analyze_transcript_segments(self, transcript_segments: List[Dict[str, Any]]) -> List[MarkerEvent]:
        """
        Analyze transcript segments for ATO markers
        
        Args:
            transcript_segments: List of transcript segments with speaker, text, timing
            
        Returns:
            List of detected ATO marker events
        """
        detected_markers = []
        
        for i, segment in enumerate(transcript_segments):
            # Get context window (previous and next segments)
            context = self._get_segment_context(transcript_segments, i)
            
            # Detect attention markers in this segment
            segment_markers = self._detect_attention_markers(segment, context)
            detected_markers.extend(segment_markers)
        
        # Post-process markers for sequences and relationships
        processed_markers = self._process_marker_relationships(detected_markers)
        
        logger.info(f"ATO analysis completed: {len(processed_markers)} markers detected")
        return processed_markers
    
    def _get_segment_context(self, segments: List[Dict[str, Any]], current_index: int,
                           window_size: int = 2) -> Dict[str, Any]:
        """Get context around current segment"""
        context = {
            'current_segment': segments[current_index],
            'previous_segments': [],
            'next_segments': [],
            'speaker_sequence': [],
            'time_window': 30.0  # 30 seconds context window
        }
        
        # Get previous segments
        start_idx = max(0, current_index - window_size)
        context['previous_segments'] = segments[start_idx:current_index]
        
        # Get next segments
        end_idx = min(len(segments), current_index + window_size + 1)
        context['next_segments'] = segments[current_index + 1:end_idx]
        
        # Build speaker sequence for pattern matching
        for seg in context['previous_segments'] + [context['current_segment']] + context['next_segments']:
            context['speaker_sequence'].append(seg.get('speaker', 'unknown'))
        
        return context
    
    def _detect_attention_markers(self, segment: Dict[str, Any], 
                                context: Dict[str, Any]) -> List[MarkerEvent]:
        """Detect attention markers in segment with context"""
        markers = []
        text = segment.get('text', '').strip()
        speaker = segment.get('speaker', 'unknown')
        start_time = segment.get('start_time', 0.0)
        end_time = segment.get('end_time', 0.0)
        
        if not text:
            return markers
        
        # Check each constitutional pattern
        for pattern in self.attention_patterns:
            confidence = self._calculate_pattern_confidence(text, pattern, context)
            
            if confidence >= self.confidence_threshold:
                # Create marker event
                marker = self._create_attention_marker(
                    pattern, segment, context, confidence
                )
                markers.append(marker)
        
        return markers
    
    def _calculate_pattern_confidence(self, text: str, pattern: AttentionPattern, 
                                    context: Dict[str, Any]) -> float:
        """Calculate confidence score for pattern match"""
        text_lower = text.lower()
        confidence_components = {
            'lexical_match': 0.0,
            'contextual_relevance': 0.0,
            'temporal_consistency': 0.0,
            'speaker_pattern': 0.0
        }
        
        # Lexical matching (keywords and regex)
        keyword_matches = sum(1 for keyword in pattern.keywords if keyword.lower() in text_lower)
        keyword_score = min(keyword_matches / len(pattern.keywords), 1.0) * 0.6
        
        regex_matches = 0
        for regex_pattern in pattern.regex_patterns:
            if re.search(regex_pattern, text, re.IGNORECASE):
                regex_matches += 1
        
        regex_score = min(regex_matches / len(pattern.regex_patterns), 1.0) * 0.4
        confidence_components['lexical_match'] = keyword_score + regex_score
        
        # Contextual relevance
        context_score = self._evaluate_context_requirements(pattern, context)
        confidence_components['contextual_relevance'] = context_score
        
        # Temporal consistency (attention markers should have reasonable timing)
        current_segment = context['current_segment']
        duration = current_segment.get('end_time', 0) - current_segment.get('start_time', 0)
        if 1.0 <= duration <= 15.0:  # Reasonable attention marker duration
            confidence_components['temporal_consistency'] = 0.8
        else:
            confidence_components['temporal_consistency'] = 0.4
        
        # Speaker pattern analysis
        speaker_score = self._evaluate_speaker_patterns(pattern, context)
        confidence_components['speaker_pattern'] = speaker_score
        
        # Weighted combination
        total_confidence = (
            confidence_components['lexical_match'] * 0.4 +
            confidence_components['contextual_relevance'] * 0.3 +
            confidence_components['temporal_consistency'] * 0.2 +
            confidence_components['speaker_pattern'] * 0.1
        ) * pattern.confidence_weight
        
        return min(total_confidence, 1.0)
    
    def _evaluate_context_requirements(self, pattern: AttentionPattern, 
                                     context: Dict[str, Any]) -> float:
        """Evaluate how well context matches pattern requirements"""
        requirements = pattern.context_requirements
        score = 0.0
        max_score = len(requirements) if requirements else 1
        
        if not requirements:
            return 0.7  # Default score if no requirements
        
        current_speaker = context['current_segment'].get('speaker', '')
        speaker_sequence = context['speaker_sequence']
        
        # Check speaker change requirement
        if 'speaker_change' in requirements:
            expected_change = requirements['speaker_change']
            actual_change = len(set(speaker_sequence[-2:])) > 1 if len(speaker_sequence) >= 2 else False
            if expected_change == actual_change:
                score += 1
        
        # Check follows direction requirement
        if 'follows_direction' in requirements and requirements['follows_direction']:
            # Check if previous segments contain direction patterns
            previous_text = ' '.join(seg.get('text', '') for seg in context['previous_segments'][-2:])
            direction_indicators = ['focus', 'look at', 'pay attention', 'notice', 'consider']
            if any(indicator in previous_text.lower() for indicator in direction_indicators):
                score += 1
        
        # Check imperative mood
        if 'imperative_mood' in requirements and requirements['imperative_mood']:
            text = context['current_segment'].get('text', '')
            imperative_indicators = ['you should', 'I want you to', 'please', 'let\'s', 'can you']
            if any(indicator in text.lower() for indicator in imperative_indicators):
                score += 1
        
        # Check interruption marker
        if 'interruption_marker' in requirements and requirements['interruption_marker']:
            text = context['current_segment'].get('text', '')
            interruption_words = ['wait', 'hold on', 'actually', 'but', 'however']
            if any(word in text.lower() for word in interruption_words):
                score += 1
        
        return score / max_score if max_score > 0 else 0.7
    
    def _evaluate_speaker_patterns(self, pattern: AttentionPattern, 
                                 context: Dict[str, Any]) -> float:
        """Evaluate speaker interaction patterns"""
        speaker_sequence = context['speaker_sequence']
        
        if len(speaker_sequence) < 2:
            return 0.5  # Insufficient data
        
        current_speaker = context['current_segment'].get('speaker', '')
        
        # Analyze speaker patterns based on marker subtype
        if pattern.marker_subtype == "attention_direction":
            # Direction typically comes from facilitator/leader
            # Check if speaker continues or starts sequence
            return 0.8 if current_speaker != speaker_sequence[-2] else 0.6
            
        elif pattern.marker_subtype == "attention_acknowledgment":
            # Acknowledgment typically from different speaker
            return 0.8 if current_speaker != speaker_sequence[-2] else 0.4
            
        elif pattern.marker_subtype == "attention_shift":
            # Shifts can come from any speaker but often indicate role change
            return 0.7
        
        return 0.6  # Default score
    
    def _create_attention_marker(self, pattern: AttentionPattern, segment: Dict[str, Any],
                               context: Dict[str, Any], confidence: float) -> MarkerEvent:
        """Create ATO marker event"""
        
        # Extract evidence text
        evidence = segment.get('text', '').strip()
        
        # Create explanation
        explanation = self._generate_marker_explanation(pattern, context)
        
        # Build confidence breakdown
        confidence_breakdown = {
            'lexical_match': confidence * 0.4,
            'contextual_relevance': confidence * 0.3,
            'temporal_consistency': confidence * 0.2,
            'speaker_pattern': confidence * 0.1
        }
        
        marker = MarkerEvent(
            marker_type=MarkerType.ATO,
            start_time=segment.get('start_time', 0.0),
            end_time=segment.get('end_time', 0.0),
            confidence=confidence,
            evidence=evidence,
            explanation=explanation,
            marker_subtype=pattern.marker_subtype,
            speaker=segment.get('speaker'),
            constitutional_source=self.constitutional_source,
            analysis_method=self.analysis_method
        )
        
        marker.set_confidence_breakdown(**confidence_breakdown)
        
        # Set context window if evidence collection enabled
        if self.evidence_collection_enabled:
            before_text = ' '.join(seg.get('text', '') for seg in context['previous_segments'])
            after_text = ' '.join(seg.get('text', '') for seg in context['next_segments'])
            marker.set_context_window(before_text, after_text, 30.0)
        
        return marker
    
    def _generate_marker_explanation(self, pattern: AttentionPattern, 
                                   context: Dict[str, Any]) -> str:
        """Generate human-readable explanation for marker"""
        
        explanations = {
            "attention_direction": "Speaker is directing attention or focus to a specific topic or aspect",
            "attention_acknowledgment": "Speaker is acknowledging attention direction or showing understanding",
            "attention_shift": "Speaker is shifting attention to a different topic or perspective", 
            "attention_maintenance": "Speaker is requesting sustained attention on current topic",
            "attention_focus": "Speaker is specifying particular focus or precision in attention"
        }
        
        base_explanation = explanations.get(pattern.marker_subtype, "Attention-related marker detected")
        
        # Add context-specific details
        current_speaker = context['current_segment'].get('speaker', 'Speaker')
        previous_speakers = [seg.get('speaker', '') for seg in context['previous_segments'][-2:]]
        
        if pattern.marker_subtype == "attention_acknowledgment" and previous_speakers:
            if len(set(previous_speakers)) > 0:
                base_explanation += f" following direction from previous speaker"
        
        return base_explanation
    
    def _process_marker_relationships(self, markers: List[MarkerEvent]) -> List[MarkerEvent]:
        """Process relationships between markers and remove duplicates"""
        
        if not markers:
            return markers
        
        # Sort markers by time
        markers.sort(key=lambda m: m.start_time)
        
        # Remove overlapping markers (keep highest confidence)
        filtered_markers = []
        for marker in markers:
            # Check for overlaps with existing markers
            has_overlap = False
            for existing in filtered_markers:
                if marker.overlaps_with(existing):
                    # If new marker has higher confidence, replace
                    if marker.confidence > existing.confidence:
                        filtered_markers.remove(existing)
                        filtered_markers.append(marker)
                    has_overlap = True
                    break
            
            if not has_overlap:
                filtered_markers.append(marker)
        
        # Identify marker sequences
        for i, marker in enumerate(filtered_markers):
            if i < len(filtered_markers) - 1:
                next_marker = filtered_markers[i + 1]
                time_gap = next_marker.start_time - marker.end_time
                
                # If markers are close in time, add relationship
                if time_gap <= 30.0:  # 30 second window
                    marker.add_related_marker(next_marker.id)
                    next_marker.add_related_marker(marker.id)
        
        return filtered_markers
    
    def identify_marker_sequences(self, markers: List[MarkerEvent]) -> List[Dict[str, Any]]:
        """Identify temporal sequences of attention markers"""
        sequences = []
        
        if len(markers) < 2:
            return sequences
        
        # Look for direction -> acknowledgment patterns
        for i, marker in enumerate(markers[:-1]):
            if marker.marker_subtype == "attention_direction":
                # Look for acknowledgment within reasonable time window
                for j in range(i + 1, min(i + 4, len(markers))):  # Check next few markers
                    next_marker = markers[j]
                    if (next_marker.marker_subtype == "attention_acknowledgment" and
                        next_marker.start_time - marker.end_time <= 30.0):
                        
                        sequences.append({
                            'pattern_type': 'direction_acknowledgment',
                            'markers': [marker, next_marker],
                            'time_span': next_marker.end_time - marker.start_time,
                            'confidence': min(marker.confidence, next_marker.confidence),
                            'description': 'Attention direction followed by acknowledgment'
                        })
                        break
        
        return sequences
    
    def analyze_speaker_roles(self, markers: List[MarkerEvent], 
                            segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze speaker roles based on attention patterns"""
        
        if not markers:
            return {}
        
        speaker_stats = {}
        
        # Count marker types per speaker
        for marker in markers:
            speaker = marker.speaker or 'unknown'
            if speaker not in speaker_stats:
                speaker_stats[speaker] = {
                    'direction_count': 0,
                    'acknowledgment_count': 0,
                    'shift_count': 0,
                    'total_markers': 0,
                    'average_confidence': 0.0
                }
            
            stats = speaker_stats[speaker]
            stats['total_markers'] += 1
            
            if marker.marker_subtype == "attention_direction":
                stats['direction_count'] += 1
            elif marker.marker_subtype == "attention_acknowledgment":
                stats['acknowledgment_count'] += 1
            elif marker.marker_subtype == "attention_shift":
                stats['shift_count'] += 1
        
        # Calculate average confidence per speaker
        for speaker in speaker_stats:
            speaker_markers = [m for m in markers if m.speaker == speaker]
            if speaker_markers:
                avg_confidence = sum(m.confidence for m in speaker_markers) / len(speaker_markers)
                speaker_stats[speaker]['average_confidence'] = avg_confidence
        
        # Identify roles
        facilitator = None
        recipient = None
        
        if speaker_stats:
            # Facilitator typically has more direction markers
            facilitator = max(
                speaker_stats.items(),
                key=lambda x: x[1]['direction_count']
            )[0]
            
            # Recipient typically has more acknowledgment markers
            acknowledgment_speakers = {s: stats['acknowledgment_count'] 
                                    for s, stats in speaker_stats.items() 
                                    if stats['acknowledgment_count'] > 0}
            
            if acknowledgment_speakers:
                recipient = max(acknowledgment_speakers.items(), key=lambda x: x[1])[0]
        
        return {
            'attention_facilitator': facilitator,
            'attention_recipient': recipient,
            'facilitator_markers': speaker_stats.get(facilitator, {}).get('total_markers', 0),
            'recipient_markers': speaker_stats.get(recipient, {}).get('total_markers', 0),
            'speaker_statistics': speaker_stats
        }
    
    def get_constitutional_compliance_info(self) -> Dict[str, Any]:
        """Get constitutional compliance information"""
        return {
            'uses_existing_framework': True,
            'constitutional_source': self.constitutional_source,
            'analysis_method': self.analysis_method,
            'no_modifications_to_cli': True,
            'library_reuse_approach': True,
            'marker_definitions_source': 'LD-3.4 constitution'
        }
    
    def get_marker_definitions(self) -> Dict[str, Any]:
        """Get constitutional marker definitions"""
        return {
            'marker_type': self.marker_type,
            'constitutional_source': self.constitutional_source,
            'subtypes': [pattern.marker_subtype for pattern in self.attention_patterns],
            'total_patterns': len(self.attention_patterns),
            'confidence_threshold': self.confidence_threshold
        }