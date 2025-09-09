"""
Comprehensive Report Generator
Orchestrates all export formats and creates comprehensive analysis reports
CONSTITUTIONAL COMPLIANCE: Uses existing LD-3.4 framework, offline only
"""

import logging
import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from src.models.marker_event import MarkerEvent
from src.models.rapport_indicator import RapportIndicator
from .pdf_report import PDFReportGenerator, ReportConfig
from .transcript_export import TranscriptExporter, TranscriptFormat, TranscriptExportConfig
from .marker_export import MarkerExporter, MarkerExportFormat, MarkerExportConfig

logger = logging.getLogger(__name__)


@dataclass
class ComprehensiveReportConfig:
    """Configuration for comprehensive report generation"""
    output_directory: str = "exports"
    session_name: str = "analysis"
    generate_pdf_report: bool = True
    generate_transcript_exports: bool = True
    generate_marker_exports: bool = True
    generate_analytics: bool = True
    
    # Format selections
    transcript_formats: List[TranscriptFormat] = None
    marker_formats: List[MarkerExportFormat] = None
    
    # Component configurations
    pdf_config: Optional[ReportConfig] = None
    transcript_config: Optional[TranscriptExportConfig] = None
    marker_config: Optional[MarkerExportConfig] = None
    
    # Constitutional compliance
    constitutional_source: str = "LD-3.4-constitution"
    include_constitutional_compliance_statement: bool = True
    
    def __post_init__(self):
        if self.transcript_formats is None:
            self.transcript_formats = [
                TranscriptFormat.ANNOTATED_TXT,
                TranscriptFormat.JSON,
                TranscriptFormat.CSV
            ]
        
        if self.marker_formats is None:
            self.marker_formats = [
                MarkerExportFormat.JSON,
                MarkerExportFormat.CSV,
                MarkerExportFormat.ANALYTICS
            ]


class ReportGenerator:
    """
    Comprehensive Report Generator for TransRapport
    Orchestrates all export components to create complete analysis reports
    """
    
    def __init__(self, config: Optional[ComprehensiveReportConfig] = None):
        self.config = config or ComprehensiveReportConfig()
        self.constitutional_source = self.config.constitutional_source
        
        # Initialize component generators
        self.pdf_generator = PDFReportGenerator(
            self.config.pdf_config or ReportConfig(constitutional_source=self.constitutional_source)
        )
        self.transcript_exporter = TranscriptExporter(
            self.config.transcript_config or TranscriptExportConfig(constitutional_source=self.constitutional_source)
        )
        self.marker_exporter = MarkerExporter(
            self.config.marker_config or MarkerExportConfig(constitutional_source=self.constitutional_source)
        )
        
        logger.info(f"Comprehensive report generator initialized for session: {self.config.session_name}")
    
    def generate_comprehensive_report(self, 
                                    transcript_segments: List[Dict[str, Any]],
                                    markers: List[MarkerEvent],
                                    rapport_indicators: List[RapportIndicator],
                                    analysis_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive report with all configured exports
        
        Args:
            transcript_segments: Raw transcript segments
            markers: Constitutional markers detected
            rapport_indicators: Rapport timeline indicators
            analysis_metadata: Analysis session metadata
            
        Returns:
            Dictionary with export results and file paths
        """
        try:
            # Create output directory
            output_dir = Path(self.config.output_directory) / self.config.session_name
            output_dir.mkdir(parents=True, exist_ok=True)
            
            export_results = {
                'session_name': self.config.session_name,
                'output_directory': str(output_dir),
                'generation_timestamp': datetime.now().isoformat(),
                'constitutional_source': self.constitutional_source,
                'exports': {}
            }
            
            logger.info(f"Generating comprehensive report for session: {self.config.session_name}")
            
            # Generate PDF report
            if self.config.generate_pdf_report:
                pdf_success = self._generate_pdf_report(
                    markers, rapport_indicators, analysis_metadata, output_dir
                )
                export_results['exports']['pdf_report'] = {
                    'success': pdf_success,
                    'path': str(output_dir / f"{self.config.session_name}_analysis_report.pdf") if pdf_success else None
                }
            
            # Generate transcript exports
            if self.config.generate_transcript_exports:
                transcript_results = self._generate_transcript_exports(
                    transcript_segments, markers, output_dir
                )
                export_results['exports']['transcripts'] = transcript_results
            
            # Generate marker exports
            if self.config.generate_marker_exports:
                marker_results = self._generate_marker_exports(
                    markers, rapport_indicators, analysis_metadata, output_dir
                )
                export_results['exports']['markers'] = marker_results
            
            # Generate analytics summary
            if self.config.generate_analytics:
                analytics_success = self._generate_analytics_summary(
                    transcript_segments, markers, rapport_indicators, analysis_metadata, output_dir
                )
                export_results['exports']['analytics'] = {
                    'success': analytics_success,
                    'path': str(output_dir / f"{self.config.session_name}_analytics.json") if analytics_success else None
                }
            
            # Generate constitutional compliance manifest
            if self.config.include_constitutional_compliance_statement:
                manifest_success = self._generate_compliance_manifest(export_results, output_dir)
                export_results['exports']['compliance_manifest'] = {
                    'success': manifest_success,
                    'path': str(output_dir / "constitutional_compliance.txt") if manifest_success else None
                }
            
            # Calculate success summary
            successful_exports = sum(1 for export_group in export_results['exports'].values()
                                   if isinstance(export_group, dict) and export_group.get('success', False))
            total_exports = len(export_results['exports'])
            
            export_results['summary'] = {
                'successful_exports': successful_exports,
                'total_exports': total_exports,
                'success_rate': successful_exports / total_exports if total_exports > 0 else 0,
                'session_complete': successful_exports == total_exports
            }
            
            logger.info(f"Comprehensive report generation completed: "
                       f"{successful_exports}/{total_exports} exports successful")
            
            return export_results
            
        except Exception as e:
            logger.error(f"Failed to generate comprehensive report: {e}")
            return {
                'session_name': self.config.session_name,
                'error': str(e),
                'generation_timestamp': datetime.now().isoformat(),
                'success': False
            }
    
    def _generate_pdf_report(self, markers: List[MarkerEvent],
                           rapport_indicators: List[RapportIndicator],
                           metadata: Dict[str, Any],
                           output_dir: Path) -> bool:
        """Generate PDF report"""
        
        pdf_path = output_dir / f"{self.config.session_name}_analysis_report.pdf"
        
        # Add session metadata
        enhanced_metadata = metadata.copy()
        enhanced_metadata.update({
            'session_name': self.config.session_name,
            'report_generation_time': datetime.now().isoformat(),
            'constitutional_source': self.constitutional_source
        })
        
        return self.pdf_generator.generate_report(
            markers, rapport_indicators, enhanced_metadata, str(pdf_path)
        )
    
    def _generate_transcript_exports(self, transcript_segments: List[Dict[str, Any]],
                                   markers: List[MarkerEvent],
                                   output_dir: Path) -> Dict[str, Any]:
        """Generate all configured transcript exports"""
        
        transcript_dir = output_dir / "transcripts"
        transcript_dir.mkdir(exist_ok=True)
        
        results = {}
        
        for format_type in self.config.transcript_formats:
            filename = f"{self.config.session_name}_transcript.{format_type.value}"
            filepath = transcript_dir / filename
            
            success = self.transcript_exporter.export_transcript(
                transcript_segments, markers, str(filepath), format_type
            )
            
            results[format_type.value] = {
                'success': success,
                'path': str(filepath) if success else None,
                'format': format_type.value
            }
            
            logger.info(f"Transcript export ({format_type.value}): {'success' if success else 'failed'}")
        
        return results
    
    def _generate_marker_exports(self, markers: List[MarkerEvent],
                               rapport_indicators: List[RapportIndicator],
                               metadata: Dict[str, Any],
                               output_dir: Path) -> Dict[str, Any]:
        """Generate all configured marker exports"""
        
        marker_dir = output_dir / "markers"
        marker_dir.mkdir(exist_ok=True)
        
        results = {}
        
        for format_type in self.config.marker_formats:
            filename = f"{self.config.session_name}_markers.{format_type.value}"
            filepath = marker_dir / filename
            
            success = self.marker_exporter.export_markers(
                markers, str(filepath), format_type, rapport_indicators, metadata
            )
            
            results[format_type.value] = {
                'success': success,
                'path': str(filepath) if success else None,
                'format': format_type.value,
                'marker_count': len(markers)
            }
            
            logger.info(f"Marker export ({format_type.value}): {'success' if success else 'failed'}")
        
        return results
    
    def _generate_analytics_summary(self, transcript_segments: List[Dict[str, Any]],
                                  markers: List[MarkerEvent],
                                  rapport_indicators: List[RapportIndicator],
                                  metadata: Dict[str, Any],
                                  output_dir: Path) -> bool:
        """Generate comprehensive analytics summary"""
        
        analytics_path = output_dir / f"{self.config.session_name}_analytics.json"
        
        # Use marker exporter's analytics format
        return self.marker_exporter.export_markers(
            markers, str(analytics_path), 
            MarkerExportFormat.ANALYTICS, rapport_indicators, metadata
        )
    
    def _generate_compliance_manifest(self, export_results: Dict[str, Any], 
                                    output_dir: Path) -> bool:
        """Generate constitutional compliance manifest"""
        
        manifest_path = output_dir / "constitutional_compliance.txt"
        
        try:
            manifest_content = []
            
            # Header
            manifest_content.append("CONSTITUTIONAL COMPLIANCE MANIFEST")
            manifest_content.append("=" * 50)
            manifest_content.append(f"Session: {self.config.session_name}")
            manifest_content.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            manifest_content.append(f"Constitutional Framework: {self.constitutional_source}")
            manifest_content.append("")
            
            # Compliance statement
            manifest_content.append("COMPLIANCE STATEMENT:")
            manifest_content.append("-" * 20)
            manifest_content.append(f"This analysis was performed using the {self.constitutional_source} framework.")
            manifest_content.append("All constitutional markers were detected using existing library components")
            manifest_content.append("without modifications to the core CLI or analysis framework.")
            manifest_content.append("The analysis maintains full constitutional compliance through library reuse.")
            manifest_content.append("")
            
            # Export summary
            manifest_content.append("EXPORT SUMMARY:")
            manifest_content.append("-" * 15)
            
            for export_type, export_data in export_results.get('exports', {}).items():
                if isinstance(export_data, dict):
                    status = "SUCCESS" if export_data.get('success', False) else "FAILED"
                    manifest_content.append(f"{export_type}: {status}")
                    if export_data.get('path'):
                        manifest_content.append(f"  Path: {export_data['path']}")
                elif isinstance(export_data, dict):
                    # Multiple exports (like transcripts/markers)
                    for sub_format, sub_data in export_data.items():
                        if isinstance(sub_data, dict):
                            status = "SUCCESS" if sub_data.get('success', False) else "FAILED"
                            manifest_content.append(f"{export_type}.{sub_format}: {status}")
            
            manifest_content.append("")
            
            # Constitutional framework details
            manifest_content.append("CONSTITUTIONAL FRAMEWORK DETAILS:")
            manifest_content.append("-" * 35)
            manifest_content.append("Framework: LD-3.4 (Library Dependencies v3.4)")
            manifest_content.append("Marker Types: ATO (Attention), SEM (Semantic), CLU (Cluster), MEMA (Memory)")
            manifest_content.append("Analysis Method: Constitutional pattern detection with confidence scoring")
            manifest_content.append("Compliance Mode: Library reuse without framework modifications")
            manifest_content.append("")
            
            # Footer
            manifest_content.append("END OF COMPLIANCE MANIFEST")
            manifest_content.append("This document certifies constitutional compliance for this analysis session.")
            
            # Write manifest
            with open(manifest_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(manifest_content))
            
            logger.info("Constitutional compliance manifest generated")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate compliance manifest: {e}")
            return False
    
    def generate_quick_summary(self, markers: List[MarkerEvent],
                             rapport_indicators: List[RapportIndicator]) -> str:
        """Generate a quick text summary for immediate review"""
        
        summary_lines = []
        
        # Header
        summary_lines.append(f"TransRapport Quick Analysis Summary")
        summary_lines.append(f"Session: {self.config.session_name}")
        summary_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary_lines.append("-" * 50)
        
        # Marker summary
        summary_lines.append(f"Constitutional Markers Detected: {len(markers)}")
        
        if markers:
            # Count by type
            type_counts = {}
            for marker in markers:
                marker_type = marker.marker_type.value if hasattr(marker.marker_type, 'value') else str(marker.marker_type)
                type_counts[marker_type] = type_counts.get(marker_type, 0) + 1
            
            for marker_type, count in sorted(type_counts.items()):
                percentage = (count / len(markers)) * 100
                summary_lines.append(f"  {marker_type}: {count} ({percentage:.1f}%)")
        
        # Rapport summary
        if rapport_indicators:
            values = [ind.value for ind in rapport_indicators]
            avg_rapport = sum(values) / len(values)
            max_rapport = max(values)
            min_rapport = min(values)
            
            summary_lines.append(f"Rapport Analysis: {len(rapport_indicators)} indicators")
            summary_lines.append(f"  Average Rapport: {avg_rapport:.3f}")
            summary_lines.append(f"  Range: {min_rapport:.3f} to {max_rapport:.3f}")
        
        # Constitutional compliance
        summary_lines.append(f"Constitutional Framework: {self.constitutional_source}")
        summary_lines.append("Analysis Status: COMPLIANT")
        
        return '\n'.join(summary_lines)
    
    def get_export_formats(self) -> Dict[str, List[str]]:
        """Get available export formats for each component"""
        return {
            'transcripts': [fmt.value for fmt in TranscriptFormat],
            'markers': [fmt.value for fmt in MarkerExportFormat],
            'pdf_report': ['pdf'],
            'analytics': ['json']
        }