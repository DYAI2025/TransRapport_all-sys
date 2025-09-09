"""
Constitutional Marker Export Service
Exports constitutional markers in various formats for analysis and reporting
CONSTITUTIONAL COMPLIANCE: Uses existing LD-3.4 framework, offline only
"""

import logging
import json
import csv
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from src.models.marker_event import MarkerEvent, MarkerType
from src.models.rapport_indicator import RapportIndicator

logger = logging.getLogger(__name__)


class MarkerExportFormat(Enum):
    """Supported marker export formats"""
    JSON = "json"
    CSV = "csv"
    TSV = "tsv"
    XML = "xml"
    ANALYTICS = "analytics"


@dataclass
class MarkerExportConfig:
    """Configuration for constitutional marker export"""
    include_metadata: bool = True
    include_relationships: bool = True
    include_evidence: bool = True
    include_explanations: bool = True
    constitutional_source: str = "LD-3.4-constitution"
    export_timestamp: bool = True
    group_by_type: bool = False
    anonymize_speakers: bool = False


class MarkerExporter:
    """
    Constitutional Marker Export Service for TransRapport
    Exports LD-3.4 constitutional markers for analysis and reporting
    """
    
    def __init__(self, config: Optional[MarkerExportConfig] = None):
        self.config = config or MarkerExportConfig()
        self.constitutional_source = self.config.constitutional_source
        
        logger.info("Constitutional marker exporter initialized")
    
    def export_markers(self, markers: List[MarkerEvent],
                      output_path: str,
                      format_type: MarkerExportFormat,
                      rapport_indicators: Optional[List[RapportIndicator]] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Export constitutional markers in specified format
        
        Args:
            markers: Constitutional markers to export
            rapport_indicators: Optional rapport indicators to include
            output_path: Output file path
            format_type: Export format
            metadata: Additional metadata to include
            
        Returns:
            True if export successful
        """
        try:
            format_handlers = {
                MarkerExportFormat.JSON: self._export_json,
                MarkerExportFormat.CSV: self._export_csv,
                MarkerExportFormat.TSV: self._export_tsv,
                MarkerExportFormat.XML: self._export_xml,
                MarkerExportFormat.ANALYTICS: self._export_analytics
            }
            
            handler = format_handlers.get(format_type)
            if not handler:
                logger.error(f"Unsupported marker export format: {format_type}")
                return False
            
            success = handler(markers, rapport_indicators, output_path, metadata or {})
            if success:
                logger.info(f"Constitutional markers exported to {output_path} in {format_type.value} format")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to export constitutional markers: {e}")
            return False
    
    def _export_json(self, markers: List[MarkerEvent],
                    rapport_indicators: Optional[List[RapportIndicator]],
                    output_path: str,
                    metadata: Dict[str, Any]) -> bool:
        """Export markers as structured JSON"""
        
        export_data = {}
        
        # Add metadata if configured
        if self.config.include_metadata:
            export_data['metadata'] = {
                'export_timestamp': datetime.now().isoformat() if self.config.export_timestamp else None,
                'constitutional_source': self.constitutional_source,
                'marker_count': len(markers),
                'rapport_indicator_count': len(rapport_indicators) if rapport_indicators else 0,
                'export_config': {
                    'include_relationships': self.config.include_relationships,
                    'include_evidence': self.config.include_evidence,
                    'include_explanations': self.config.include_explanations,
                    'group_by_type': self.config.group_by_type,
                    'anonymize_speakers': self.config.anonymize_speakers
                },
                'analysis_metadata': metadata
            }
        
        # Process markers
        if self.config.group_by_type:
            marker_groups = {}
            for marker in markers:
                marker_type = marker.marker_type.value if hasattr(marker.marker_type, 'value') else str(marker.marker_type)
                if marker_type not in marker_groups:
                    marker_groups[marker_type] = []
                marker_groups[marker_type].append(self._serialize_marker(marker))
            
            export_data['markers_by_type'] = marker_groups
        else:
            export_data['markers'] = [self._serialize_marker(marker) for marker in markers]
        
        # Add rapport indicators if provided
        if rapport_indicators:
            export_data['rapport_indicators'] = [
                self._serialize_rapport_indicator(indicator) 
                for indicator in rapport_indicators
            ]
        
        # Write JSON file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return True
    
    def _export_csv(self, markers: List[MarkerEvent],
                   rapport_indicators: Optional[List[RapportIndicator]],
                   output_path: str,
                   metadata: Dict[str, Any]) -> bool:
        """Export markers as CSV with comprehensive columns"""
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            # Define fieldnames based on configuration
            fieldnames = [
                'id', 'marker_type', 'marker_subtype', 'start_time', 'end_time',
                'confidence', 'speaker', 'constitutional_source', 'analysis_method'
            ]
            
            if self.config.include_evidence:
                fieldnames.append('evidence')
            
            if self.config.include_explanations:
                fieldnames.append('explanation')
            
            if self.config.include_relationships:
                fieldnames.extend(['related_marker_ids', 'relationship_count'])
            
            if self.config.include_metadata:
                fieldnames.extend(['duration_seconds', 'marker_density'])
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header with constitutional compliance note
            if self.config.include_metadata:
                csvfile.write(f"# TransRapport Constitutional Marker Export\n")
                csvfile.write(f"# Generated: {datetime.now().isoformat()}\n")
                csvfile.write(f"# Constitutional Source: {self.constitutional_source}\n")
                csvfile.write(f"# Total Markers: {len(markers)}\n")
                csvfile.write("#\n")
            
            writer.writeheader()
            
            # Write marker rows
            for marker in markers:
                row_data = {
                    'id': marker.id,
                    'marker_type': marker.marker_type.value if hasattr(marker.marker_type, 'value') else str(marker.marker_type),
                    'marker_subtype': marker.marker_subtype or '',
                    'start_time': marker.start_time,
                    'end_time': marker.end_time,
                    'confidence': marker.confidence,
                    'speaker': self._anonymize_speaker(marker.speaker) if self.config.anonymize_speakers else marker.speaker or '',
                    'constitutional_source': marker.constitutional_source or '',
                    'analysis_method': marker.analysis_method or ''
                }
                
                if self.config.include_evidence:
                    row_data['evidence'] = marker.evidence or ''
                
                if self.config.include_explanations:
                    row_data['explanation'] = marker.explanation or ''
                
                if self.config.include_relationships:
                    related_ids = getattr(marker, 'related_marker_ids', [])
                    row_data['related_marker_ids'] = '; '.join(related_ids) if related_ids else ''
                    row_data['relationship_count'] = len(related_ids) if related_ids else 0
                
                if self.config.include_metadata:
                    duration = marker.end_time - marker.start_time
                    row_data['duration_seconds'] = duration
                    # Simple density calculation (markers per minute in local window)
                    row_data['marker_density'] = self._calculate_marker_density(marker, markers)
                
                writer.writerow(row_data)
        
        return True
    
    def _export_tsv(self, markers: List[MarkerEvent],
                   rapport_indicators: Optional[List[RapportIndicator]],
                   output_path: str,
                   metadata: Dict[str, Any]) -> bool:
        """Export markers as TSV (Tab-Separated Values)"""
        
        # TSV is CSV with tab delimiter
        with open(output_path, 'w', newline='', encoding='utf-8') as tsvfile:
            fieldnames = [
                'id', 'marker_type', 'marker_subtype', 'start_time', 'end_time',
                'confidence', 'speaker', 'evidence', 'explanation',
                'constitutional_source', 'analysis_method'
            ]
            
            writer = csv.DictWriter(tsvfile, fieldnames=fieldnames, delimiter='\t')
            writer.writeheader()
            
            for marker in markers:
                writer.writerow({
                    'id': marker.id,
                    'marker_type': marker.marker_type.value if hasattr(marker.marker_type, 'value') else str(marker.marker_type),
                    'marker_subtype': marker.marker_subtype or '',
                    'start_time': marker.start_time,
                    'end_time': marker.end_time,
                    'confidence': marker.confidence,
                    'speaker': self._anonymize_speaker(marker.speaker) if self.config.anonymize_speakers else marker.speaker or '',
                    'evidence': marker.evidence or '' if self.config.include_evidence else '',
                    'explanation': marker.explanation or '' if self.config.include_explanations else '',
                    'constitutional_source': marker.constitutional_source or '',
                    'analysis_method': marker.analysis_method or ''
                })
        
        return True
    
    def _export_xml(self, markers: List[MarkerEvent],
                   rapport_indicators: Optional[List[RapportIndicator]],
                   output_path: str,
                   metadata: Dict[str, Any]) -> bool:
        """Export markers as XML with constitutional structure"""
        
        xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml_lines.append('<constitutional_analysis>')
        
        # Metadata
        if self.config.include_metadata:
            xml_lines.append('  <metadata>')
            xml_lines.append(f'    <export_timestamp>{datetime.now().isoformat()}</export_timestamp>')
            xml_lines.append(f'    <constitutional_source>{self.constitutional_source}</constitutional_source>')
            xml_lines.append(f'    <marker_count>{len(markers)}</marker_count>')
            xml_lines.append('  </metadata>')
        
        # Markers section
        xml_lines.append('  <markers>')
        
        for marker in markers:
            xml_lines.append('    <marker>')
            xml_lines.append(f'      <id>{self._xml_escape(marker.id)}</id>')
            xml_lines.append(f'      <type>{self._xml_escape(str(marker.marker_type))}</type>')
            xml_lines.append(f'      <subtype>{self._xml_escape(marker.marker_subtype or "")}</subtype>')
            xml_lines.append(f'      <start_time>{marker.start_time}</start_time>')
            xml_lines.append(f'      <end_time>{marker.end_time}</end_time>')
            xml_lines.append(f'      <confidence>{marker.confidence}</confidence>')
            
            speaker = self._anonymize_speaker(marker.speaker) if self.config.anonymize_speakers else marker.speaker
            xml_lines.append(f'      <speaker>{self._xml_escape(speaker or "")}</speaker>')
            
            if self.config.include_evidence:
                xml_lines.append(f'      <evidence>{self._xml_escape(marker.evidence or "")}</evidence>')
            
            if self.config.include_explanations:
                xml_lines.append(f'      <explanation>{self._xml_escape(marker.explanation or "")}</explanation>')
            
            xml_lines.append(f'      <constitutional_source>{self._xml_escape(marker.constitutional_source or "")}</constitutional_source>')
            xml_lines.append(f'      <analysis_method>{self._xml_escape(marker.analysis_method or "")}</analysis_method>')
            
            xml_lines.append('    </marker>')
        
        xml_lines.append('  </markers>')
        
        # Rapport indicators if provided
        if rapport_indicators:
            xml_lines.append('  <rapport_indicators>')
            for indicator in rapport_indicators:
                xml_lines.append('    <indicator>')
                xml_lines.append(f'      <timestamp>{indicator.timestamp}</timestamp>')
                xml_lines.append(f'      <value>{indicator.value}</value>')
                xml_lines.append(f'      <trend>{indicator.trend.value if hasattr(indicator.trend, "value") else str(indicator.trend)}</trend>')
                xml_lines.append(f'      <confidence>{indicator.confidence}</confidence>')
                xml_lines.append(f'      <contributing_markers_count>{len(indicator.contributing_markers)}</contributing_markers_count>')
                xml_lines.append('    </indicator>')
            xml_lines.append('  </rapport_indicators>')
        
        xml_lines.append('</constitutional_analysis>')
        
        # Write XML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(xml_lines))
        
        return True
    
    def _export_analytics(self, markers: List[MarkerEvent],
                         rapport_indicators: Optional[List[RapportIndicator]],
                         output_path: str,
                         metadata: Dict[str, Any]) -> bool:
        """Export analytical summary and statistics"""
        
        analytics_data = {
            'constitutional_analysis_summary': {
                'export_timestamp': datetime.now().isoformat(),
                'constitutional_source': self.constitutional_source,
                'total_markers': len(markers),
                'session_duration': max(m.end_time for m in markers) - min(m.start_time for m in markers) if markers else 0
            }
        }
        
        # Marker type distribution
        type_counts = {}
        subtype_counts = {}
        speaker_counts = {}
        
        for marker in markers:
            marker_type = marker.marker_type.value if hasattr(marker.marker_type, 'value') else str(marker.marker_type)
            type_counts[marker_type] = type_counts.get(marker_type, 0) + 1
            
            if marker.marker_subtype:
                subtype_counts[marker.marker_subtype] = subtype_counts.get(marker.marker_subtype, 0) + 1
            
            if marker.speaker and not self.config.anonymize_speakers:
                speaker_counts[marker.speaker] = speaker_counts.get(marker.speaker, 0) + 1
        
        analytics_data['marker_distribution'] = {
            'by_type': type_counts,
            'by_subtype': subtype_counts,
            'by_speaker': speaker_counts if not self.config.anonymize_speakers else {}
        }
        
        # Confidence statistics
        confidences = [m.confidence for m in markers]
        if confidences:
            analytics_data['confidence_statistics'] = {
                'mean': sum(confidences) / len(confidences),
                'min': min(confidences),
                'max': max(confidences),
                'high_confidence_count': sum(1 for c in confidences if c >= 0.8),
                'medium_confidence_count': sum(1 for c in confidences if 0.5 <= c < 0.8),
                'low_confidence_count': sum(1 for c in confidences if c < 0.5)
            }
        
        # Temporal analysis
        if len(markers) > 1:
            sorted_markers = sorted(markers, key=lambda m: m.start_time)
            intervals = [sorted_markers[i+1].start_time - sorted_markers[i].start_time 
                        for i in range(len(sorted_markers)-1)]
            
            analytics_data['temporal_analysis'] = {
                'marker_frequency_per_minute': len(markers) / (analytics_data['constitutional_analysis_summary']['session_duration'] / 60) if analytics_data['constitutional_analysis_summary']['session_duration'] > 0 else 0,
                'average_marker_interval': sum(intervals) / len(intervals) if intervals else 0,
                'marker_clustering': self._analyze_marker_clustering(sorted_markers)
            }
        
        # Rapport analysis if provided
        if rapport_indicators:
            values = [ind.value for ind in rapport_indicators]
            analytics_data['rapport_analysis'] = {
                'indicator_count': len(rapport_indicators),
                'mean_rapport': sum(values) / len(values),
                'min_rapport': min(values),
                'max_rapport': max(values),
                'rapport_stability': self._calculate_rapport_stability(values),
                'high_rapport_periods': sum(1 for v in values if v > 0.7),
                'low_rapport_periods': sum(1 for v in values if v < 0.3)
            }
        
        # Constitutional compliance report
        analytics_data['constitutional_compliance'] = {
            'framework_compliance': 'LD-3.4',
            'marker_validation': {
                'all_markers_have_constitutional_source': all(m.constitutional_source for m in markers),
                'all_markers_have_analysis_method': all(m.analysis_method for m in markers),
                'all_markers_above_threshold': all(m.confidence >= 0.5 for m in markers)  # Assumed threshold
            }
        }
        
        # Write analytics JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analytics_data, f, indent=2, ensure_ascii=False)
        
        return True
    
    def _serialize_marker(self, marker: MarkerEvent) -> Dict[str, Any]:
        """Serialize a marker event to dictionary"""
        data = {
            'id': marker.id,
            'marker_type': marker.marker_type.value if hasattr(marker.marker_type, 'value') else str(marker.marker_type),
            'marker_subtype': marker.marker_subtype,
            'start_time': marker.start_time,
            'end_time': marker.end_time,
            'confidence': marker.confidence,
            'speaker': self._anonymize_speaker(marker.speaker) if self.config.anonymize_speakers else marker.speaker,
            'constitutional_source': marker.constitutional_source,
            'analysis_method': marker.analysis_method
        }
        
        if self.config.include_evidence:
            data['evidence'] = marker.evidence
        
        if self.config.include_explanations:
            data['explanation'] = marker.explanation
        
        if self.config.include_relationships:
            data['related_marker_ids'] = getattr(marker, 'related_marker_ids', [])
        
        return data
    
    def _serialize_rapport_indicator(self, indicator: RapportIndicator) -> Dict[str, Any]:
        """Serialize a rapport indicator to dictionary"""
        return {
            'timestamp': indicator.timestamp,
            'value': indicator.value,
            'trend': indicator.trend.value if hasattr(indicator.trend, 'value') else str(indicator.trend),
            'confidence': indicator.confidence,
            'contributing_markers_count': len(indicator.contributing_markers)
        }
    
    def _anonymize_speaker(self, speaker: Optional[str]) -> Optional[str]:
        """Anonymize speaker identifier if configured"""
        if not speaker:
            return speaker
        
        # Simple anonymization - replace with generic labels
        speaker_map = getattr(self, '_speaker_map', {})
        if speaker not in speaker_map:
            speaker_map[speaker] = f"Speaker_{len(speaker_map) + 1}"
            self._speaker_map = speaker_map
        
        return speaker_map[speaker]
    
    def _calculate_marker_density(self, target_marker: MarkerEvent, all_markers: List[MarkerEvent]) -> float:
        """Calculate marker density around target marker"""
        window_size = 60.0  # 1-minute window
        
        start_window = target_marker.start_time - window_size / 2
        end_window = target_marker.start_time + window_size / 2
        
        markers_in_window = sum(1 for m in all_markers 
                              if start_window <= m.start_time <= end_window)
        
        return markers_in_window / (window_size / 60)  # Markers per minute
    
    def _analyze_marker_clustering(self, sorted_markers: List[MarkerEvent]) -> Dict[str, Any]:
        """Analyze clustering patterns in markers"""
        if len(sorted_markers) < 2:
            return {'clustering_detected': False}
        
        intervals = [sorted_markers[i+1].start_time - sorted_markers[i].start_time 
                    for i in range(len(sorted_markers)-1)]
        
        mean_interval = sum(intervals) / len(intervals)
        
        # Simple clustering detection - short intervals suggest clustering
        short_intervals = sum(1 for interval in intervals if interval < mean_interval * 0.5)
        clustering_ratio = short_intervals / len(intervals)
        
        return {
            'clustering_detected': clustering_ratio > 0.3,
            'clustering_ratio': clustering_ratio,
            'mean_interval': mean_interval,
            'clusters_detected': short_intervals
        }
    
    def _calculate_rapport_stability(self, values: List[float]) -> float:
        """Calculate stability of rapport values (inverse of variance)"""
        if len(values) < 2:
            return 1.0
        
        mean_val = sum(values) / len(values)
        variance = sum((v - mean_val) ** 2 for v in values) / len(values)
        
        # Stability is inverse of variance, normalized
        return 1.0 / (1.0 + variance)
    
    def _xml_escape(self, text: str) -> str:
        """Escape XML special characters"""
        if not text:
            return ""
        
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#39;'))
    
    def get_supported_formats(self) -> List[MarkerExportFormat]:
        """Get list of supported export formats"""
        return list(MarkerExportFormat)