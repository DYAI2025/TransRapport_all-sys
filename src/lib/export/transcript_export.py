"""
Transcript Export Service
Exports transcripts in various formats with constitutional marker annotations
CONSTITUTIONAL COMPLIANCE: Uses existing LD-3.4 framework, offline only
"""

import logging
import json
import csv
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from src.models.marker_event import MarkerEvent, MarkerType

logger = logging.getLogger(__name__)


class TranscriptFormat(Enum):
    """Supported transcript export formats"""
    TXT = "txt"
    JSON = "json"
    CSV = "csv"
    SRT = "srt"
    VTT = "vtt"
    ANNOTATED_TXT = "annotated_txt"


@dataclass
class TranscriptExportConfig:
    """Configuration for transcript export"""
    include_timestamps: bool = True
    include_speaker_labels: bool = True
    include_markers: bool = True
    include_confidence_scores: bool = False
    word_wrap_length: int = 80
    constitutional_source: str = "LD-3.4-constitution"
    time_format: str = "seconds"  # "seconds", "hms", "srt"


class TranscriptExporter:
    """
    Transcript Export Service for TransRapport
    Exports transcripts with constitutional marker annotations
    """
    
    def __init__(self, config: Optional[TranscriptExportConfig] = None):
        self.config = config or TranscriptExportConfig()
        self.constitutional_source = self.config.constitutional_source
        
        logger.info("Transcript exporter initialized")
    
    def export_transcript(self, transcript_segments: List[Dict[str, Any]], 
                         markers: List[MarkerEvent],
                         output_path: str,
                         format_type: TranscriptFormat) -> bool:
        """
        Export transcript in specified format
        
        Args:
            transcript_segments: Raw transcript segments
            markers: Constitutional markers to include
            output_path: Output file path
            format_type: Export format
            
        Returns:
            True if export successful
        """
        try:
            format_handlers = {
                TranscriptFormat.TXT: self._export_plain_text,
                TranscriptFormat.JSON: self._export_json,
                TranscriptFormat.CSV: self._export_csv,
                TranscriptFormat.SRT: self._export_srt,
                TranscriptFormat.VTT: self._export_vtt,
                TranscriptFormat.ANNOTATED_TXT: self._export_annotated_text
            }
            
            handler = format_handlers.get(format_type)
            if not handler:
                logger.error(f"Unsupported export format: {format_type}")
                return False
            
            success = handler(transcript_segments, markers, output_path)
            if success:
                logger.info(f"Transcript exported to {output_path} in {format_type.value} format")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to export transcript: {e}")
            return False
    
    def _export_plain_text(self, segments: List[Dict[str, Any]], 
                          markers: List[MarkerEvent],
                          output_path: str) -> bool:
        """Export as plain text with optional speaker labels and timestamps"""
        
        lines = []
        
        # Header
        if self.config.include_markers or self.config.include_timestamps:
            lines.append("TransRapport Transcript Export")
            lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(f"Constitutional Source: {self.constitutional_source}")
            lines.append("")
        
        # Process segments
        for segment in segments:
            line_parts = []
            
            # Add timestamp
            if self.config.include_timestamps:
                timestamp = self._format_timestamp(segment.get('start_time', 0))
                line_parts.append(f"[{timestamp}]")
            
            # Add speaker
            if self.config.include_speaker_labels and segment.get('speaker'):
                line_parts.append(f"{segment['speaker']}:")
            
            # Add text
            text = segment.get('text', '').strip()
            if text:
                line_parts.append(text)
            
            if line_parts:
                line = " ".join(line_parts)
                
                # Word wrap
                if self.config.word_wrap_length and len(line) > self.config.word_wrap_length:
                    lines.extend(self._word_wrap(line, self.config.word_wrap_length))
                else:
                    lines.append(line)
                
                lines.append("")  # Empty line between segments
        
        # Write file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return True
    
    def _export_json(self, segments: List[Dict[str, Any]], 
                    markers: List[MarkerEvent],
                    output_path: str) -> bool:
        """Export as structured JSON with full metadata"""
        
        # Prepare export data
        export_data = {
            'metadata': {
                'export_timestamp': datetime.now().isoformat(),
                'constitutional_source': self.constitutional_source,
                'segment_count': len(segments),
                'marker_count': len(markers),
                'export_config': {
                    'include_timestamps': self.config.include_timestamps,
                    'include_speaker_labels': self.config.include_speaker_labels,
                    'include_markers': self.config.include_markers,
                    'include_confidence_scores': self.config.include_confidence_scores
                }
            },
            'segments': [],
            'markers': [] if self.config.include_markers else None
        }
        
        # Process segments
        for segment in segments:
            segment_data = {
                'text': segment.get('text', ''),
                'speaker': segment.get('speaker') if self.config.include_speaker_labels else None,
                'start_time': segment.get('start_time') if self.config.include_timestamps else None,
                'end_time': segment.get('end_time') if self.config.include_timestamps else None,
                'confidence': segment.get('confidence') if self.config.include_confidence_scores else None
            }
            
            # Remove None values
            segment_data = {k: v for k, v in segment_data.items() if v is not None}
            export_data['segments'].append(segment_data)
        
        # Process markers if included
        if self.config.include_markers:
            for marker in markers:
                marker_data = {
                    'id': marker.id,
                    'marker_type': marker.marker_type.value if hasattr(marker.marker_type, 'value') else str(marker.marker_type),
                    'marker_subtype': marker.marker_subtype,
                    'start_time': marker.start_time,
                    'end_time': marker.end_time,
                    'confidence': marker.confidence,
                    'evidence': marker.evidence,
                    'explanation': marker.explanation,
                    'speaker': marker.speaker,
                    'constitutional_source': marker.constitutional_source,
                    'analysis_method': marker.analysis_method
                }
                export_data['markers'].append(marker_data)
        else:
            export_data.pop('markers')
        
        # Write JSON file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return True
    
    def _export_csv(self, segments: List[Dict[str, Any]], 
                   markers: List[MarkerEvent],
                   output_path: str) -> bool:
        """Export as CSV with configurable columns"""
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            # Define columns based on configuration
            fieldnames = ['text']
            
            if self.config.include_speaker_labels:
                fieldnames.insert(0, 'speaker')
            
            if self.config.include_timestamps:
                fieldnames.insert(0, 'end_time')
                fieldnames.insert(0, 'start_time')
            
            if self.config.include_confidence_scores:
                fieldnames.append('confidence')
            
            if self.config.include_markers:
                fieldnames.extend(['marker_types', 'marker_count'])
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Create marker lookup for segments
            segment_markers = {}
            if self.config.include_markers:
                for marker in markers:
                    for segment in segments:
                        if (segment.get('start_time', 0) <= marker.start_time <= segment.get('end_time', 0)):
                            seg_id = id(segment)
                            if seg_id not in segment_markers:
                                segment_markers[seg_id] = []
                            segment_markers[seg_id].append(marker)
            
            # Write segment rows
            for segment in segments:
                row_data = {'text': segment.get('text', '')}
                
                if self.config.include_speaker_labels:
                    row_data['speaker'] = segment.get('speaker', '')
                
                if self.config.include_timestamps:
                    row_data['start_time'] = segment.get('start_time', 0)
                    row_data['end_time'] = segment.get('end_time', 0)
                
                if self.config.include_confidence_scores:
                    row_data['confidence'] = segment.get('confidence', 0)
                
                if self.config.include_markers:
                    seg_markers = segment_markers.get(id(segment), [])
                    marker_types = list(set(str(m.marker_type) for m in seg_markers))
                    row_data['marker_types'] = '; '.join(marker_types)
                    row_data['marker_count'] = len(seg_markers)
                
                writer.writerow(row_data)
        
        return True
    
    def _export_srt(self, segments: List[Dict[str, Any]], 
                   markers: List[MarkerEvent],
                   output_path: str) -> bool:
        """Export as SRT subtitle format"""
        
        lines = []
        
        for i, segment in enumerate(segments, 1):
            # Sequence number
            lines.append(str(i))
            
            # Timestamp range in SRT format
            start_time = self._format_srt_timestamp(segment.get('start_time', 0))
            end_time = self._format_srt_timestamp(segment.get('end_time', 0))
            lines.append(f"{start_time} --> {end_time}")
            
            # Text with optional speaker label
            text = segment.get('text', '').strip()
            if self.config.include_speaker_labels and segment.get('speaker'):
                text = f"<b>{segment['speaker']}:</b> {text}"
            
            lines.append(text)
            lines.append("")  # Empty line between entries
        
        # Write file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return True
    
    def _export_vtt(self, segments: List[Dict[str, Any]], 
                   markers: List[MarkerEvent],
                   output_path: str) -> bool:
        """Export as WebVTT format"""
        
        lines = ["WEBVTT", "", "NOTE", "Generated by TransRapport", ""]
        
        for segment in segments:
            # Timestamp range in VTT format
            start_time = self._format_vtt_timestamp(segment.get('start_time', 0))
            end_time = self._format_vtt_timestamp(segment.get('end_time', 0))
            lines.append(f"{start_time} --> {end_time}")
            
            # Text with optional speaker label
            text = segment.get('text', '').strip()
            if self.config.include_speaker_labels and segment.get('speaker'):
                text = f"<v {segment['speaker']}>{text}"
            
            lines.append(text)
            lines.append("")  # Empty line between entries
        
        # Write file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return True
    
    def _export_annotated_text(self, segments: List[Dict[str, Any]], 
                              markers: List[MarkerEvent],
                              output_path: str) -> bool:
        """Export with inline constitutional marker annotations"""
        
        lines = []
        
        # Header with constitutional compliance
        lines.append("TransRapport Constitutional Analysis - Annotated Transcript")
        lines.append("=" * 60)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Constitutional Source: {self.constitutional_source}")
        lines.append(f"Total Segments: {len(segments)}")
        lines.append(f"Total Markers: {len(markers)}")
        lines.append("")
        
        # Legend
        lines.append("MARKER LEGEND:")
        marker_types = set(str(m.marker_type) for m in markers)
        for marker_type in sorted(marker_types):
            lines.append(f"  [{marker_type}] = {self._get_marker_description(marker_type)}")
        lines.append("")
        
        # Create timeline with annotations
        timeline_events = []
        
        # Add segments
        for segment in segments:
            timeline_events.append({
                'time': segment.get('start_time', 0),
                'type': 'segment',
                'data': segment
            })
        
        # Add markers
        for marker in markers:
            timeline_events.append({
                'time': marker.start_time,
                'type': 'marker',
                'data': marker
            })
        
        # Sort by time
        timeline_events.sort(key=lambda x: x['time'])
        
        # Generate annotated content
        current_segment = None
        for event in timeline_events:
            if event['type'] == 'segment':
                current_segment = event['data']
                
                # Segment header
                line_parts = []
                if self.config.include_timestamps:
                    timestamp = self._format_timestamp(current_segment.get('start_time', 0))
                    line_parts.append(f"[{timestamp}]")
                
                if self.config.include_speaker_labels and current_segment.get('speaker'):
                    line_parts.append(f"{current_segment['speaker']}:")
                
                if line_parts:
                    lines.append(" ".join(line_parts))
                
                # Segment text
                text = current_segment.get('text', '').strip()
                if text:
                    lines.append(text)
                
            elif event['type'] == 'marker' and self.config.include_markers:
                marker = event['data']
                
                # Marker annotation
                annotation = (f"    >>> [{marker.marker_type}] {marker.marker_subtype} "
                            f"(confidence: {marker.confidence:.3f})")
                lines.append(annotation)
                
                if marker.explanation:
                    explanation = f"        {marker.explanation}"
                    lines.append(explanation)
        
        lines.append("")
        
        # Constitutional compliance footer
        lines.append("Constitutional Compliance Statement:")
        lines.append(f"This analysis follows the {self.constitutional_source} framework")
        lines.append("Analysis performed using existing library components without CLI modifications")
        
        # Write file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return True
    
    def _format_timestamp(self, seconds: float) -> str:
        """Format timestamp according to configuration"""
        if self.config.time_format == "seconds":
            return f"{seconds:.1f}s"
        elif self.config.time_format == "hms":
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = seconds % 60
            return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"
        elif self.config.time_format == "srt":
            return self._format_srt_timestamp(seconds)
        else:
            return f"{seconds:.1f}s"
    
    def _format_srt_timestamp(self, seconds: float) -> str:
        """Format timestamp for SRT format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds * 1000) % 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def _format_vtt_timestamp(self, seconds: float) -> str:
        """Format timestamp for VTT format"""
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes:02d}:{secs:06.3f}"
    
    def _word_wrap(self, text: str, width: int) -> List[str]:
        """Simple word wrapping"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + len(current_line) <= width:
                current_line.append(word)
                current_length += len(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(" ".join(current_line))
        
        return lines
    
    def _get_marker_description(self, marker_type: str) -> str:
        """Get description for marker type"""
        descriptions = {
            'ATO': 'Attention markers (direction, acknowledgment, shift, maintenance, focus)',
            'SEM': 'Semantic markers (alignment, clarification, understanding, expansion, divergence)',
            'CLU': 'Cluster markers (formation, recognition, reinforcement, dissolution, transition)',
            'MEMA': 'Memory markers (reference, alignment, correction, expansion, integration)'
        }
        return descriptions.get(marker_type, 'Constitutional marker')
    
    def get_supported_formats(self) -> List[TranscriptFormat]:
        """Get list of supported export formats"""
        return list(TranscriptFormat)