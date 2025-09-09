"""
PDF Report Generator
Creates formatted PDF reports from analysis results
CONSTITUTIONAL COMPLIANCE: Uses existing LD-3.4 framework, offline only
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    # Mock classes for testing
    canvas = None
    letter = A4 = (612, 792)
    SimpleDocTemplate = object

from src.models.marker_event import MarkerEvent, MarkerType
from src.models.rapport_indicator import RapportIndicator

logger = logging.getLogger(__name__)


@dataclass
class ReportConfig:
    """Configuration for PDF report generation"""
    title: str = "TransRapport Analysis Report"
    include_executive_summary: bool = True
    include_marker_details: bool = True
    include_rapport_analysis: bool = True
    include_timeline: bool = True
    page_size: tuple = A4
    font_size: int = 12
    constitutional_source: str = "LD-3.4-constitution"


class PDFReportGenerator:
    """
    PDF Report Generator for TransRapport Analysis
    Creates professional reports from constitutional marker analysis
    """
    
    def __init__(self, config: Optional[ReportConfig] = None):
        self.config = config or ReportConfig()
        self.constitutional_source = self.config.constitutional_source
        
        if not REPORTLAB_AVAILABLE:
            logger.warning("ReportLab not available - PDF generation will create text-based reports")
        
        logger.info("PDF report generator initialized")
    
    def generate_report(self, markers: List[MarkerEvent], 
                       rapport_indicators: List[RapportIndicator],
                       metadata: Dict[str, Any],
                       output_path: str) -> bool:
        """
        Generate comprehensive PDF report from analysis results
        
        Args:
            markers: Detected constitutional markers
            rapport_indicators: Rapport timeline indicators
            metadata: Analysis metadata
            output_path: Path for output PDF file
            
        Returns:
            True if report generated successfully
        """
        try:
            if REPORTLAB_AVAILABLE:
                return self._generate_pdf_report(markers, rapport_indicators, metadata, output_path)
            else:
                return self._generate_text_report(markers, rapport_indicators, metadata, output_path)
        except Exception as e:
            logger.error(f"Failed to generate PDF report: {e}")
            return False
    
    def _generate_pdf_report(self, markers: List[MarkerEvent], 
                           rapport_indicators: List[RapportIndicator],
                           metadata: Dict[str, Any],
                           output_path: str) -> bool:
        """Generate actual PDF report using ReportLab"""
        
        # Create document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=self.config.page_size,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build story (content)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center
        )
        story.append(Paragraph(self.config.title, title_style))
        story.append(Spacer(1, 20))
        
        # Metadata section
        story.extend(self._create_metadata_section(metadata, styles))
        
        # Executive summary
        if self.config.include_executive_summary:
            story.extend(self._create_executive_summary(markers, rapport_indicators, styles))
        
        # Marker details
        if self.config.include_marker_details:
            story.extend(self._create_marker_details(markers, styles))
        
        # Rapport analysis
        if self.config.include_rapport_analysis and rapport_indicators:
            story.extend(self._create_rapport_analysis(rapport_indicators, styles))
        
        # Timeline
        if self.config.include_timeline:
            story.extend(self._create_timeline_section(markers, styles))
        
        # Build PDF
        doc.build(story)
        logger.info(f"PDF report generated: {output_path}")
        return True
    
    def _generate_text_report(self, markers: List[MarkerEvent], 
                            rapport_indicators: List[RapportIndicator],
                            metadata: Dict[str, Any],
                            output_path: str) -> bool:
        """Generate text-based report when ReportLab unavailable"""
        
        report_content = []
        
        # Header
        report_content.append("=" * 80)
        report_content.append(f"{self.config.title}")
        report_content.append("=" * 80)
        report_content.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_content.append(f"Constitutional Source: {self.constitutional_source}")
        report_content.append("")
        
        # Executive Summary
        report_content.append("EXECUTIVE SUMMARY")
        report_content.append("-" * 40)
        report_content.append(f"Total Markers Detected: {len(markers)}")
        
        # Count by type
        marker_counts = {}
        for marker in markers:
            marker_type = marker.marker_type.value if hasattr(marker.marker_type, 'value') else str(marker.marker_type)
            marker_counts[marker_type] = marker_counts.get(marker_type, 0) + 1
        
        for marker_type, count in marker_counts.items():
            report_content.append(f"  {marker_type}: {count} markers")
        
        if rapport_indicators:
            avg_rapport = sum(ind.value for ind in rapport_indicators) / len(rapport_indicators)
            report_content.append(f"Average Rapport: {avg_rapport:.3f}")
        
        report_content.append("")
        
        # Marker Details
        report_content.append("MARKER DETAILS")
        report_content.append("-" * 40)
        
        for marker in sorted(markers, key=lambda m: m.start_time):
            report_content.append(f"[{marker.start_time:.1f}s] {marker.marker_type} - {marker.marker_subtype}")
            report_content.append(f"  Speaker: {marker.speaker}")
            report_content.append(f"  Evidence: {marker.evidence}")
            report_content.append(f"  Confidence: {marker.confidence:.3f}")
            report_content.append("")
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_content))
        
        logger.info(f"Text-based report generated: {output_path}")
        return True
    
    def _create_metadata_section(self, metadata: Dict[str, Any], styles) -> List:
        """Create metadata section for PDF"""
        content = []
        
        content.append(Paragraph("Analysis Metadata", styles['Heading2']))
        
        metadata_data = [
            ['Property', 'Value'],
            ['Analysis Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Constitutional Source', self.constitutional_source],
            ['Total Segments', str(metadata.get('transcript_segments', 'Unknown'))],
            ['Processing Time', f"{metadata.get('processing_time', 0):.2f}s"],
        ]
        
        # Add engine statistics if available
        engine_stats = metadata.get('engine_stats', {})
        for engine, count in engine_stats.items():
            metadata_data.append([f'{engine} Markers', str(count)])
        
        table = Table(metadata_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        content.append(table)
        content.append(Spacer(1, 20))
        
        return content
    
    def _create_executive_summary(self, markers: List[MarkerEvent], 
                                rapport_indicators: List[RapportIndicator], 
                                styles) -> List:
        """Create executive summary section"""
        content = []
        
        content.append(Paragraph("Executive Summary", styles['Heading2']))
        
        # Summary statistics
        total_markers = len(markers)
        marker_counts = {}
        for marker in markers:
            marker_type = marker.marker_type.value if hasattr(marker.marker_type, 'value') else str(marker.marker_type)
            marker_counts[marker_type] = marker_counts.get(marker_type, 0) + 1
        
        summary_text = f"Analysis detected {total_markers} constitutional markers across the conversation. "
        
        for marker_type, count in marker_counts.items():
            percentage = (count / total_markers * 100) if total_markers > 0 else 0
            summary_text += f"{marker_type}: {count} ({percentage:.1f}%), "
        
        if rapport_indicators:
            avg_rapport = sum(ind.value for ind in rapport_indicators) / len(rapport_indicators)
            summary_text += f"Average rapport score: {avg_rapport:.3f}."
        
        content.append(Paragraph(summary_text.rstrip(', '), styles['Normal']))
        content.append(Spacer(1, 20))
        
        return content
    
    def _create_marker_details(self, markers: List[MarkerEvent], styles) -> List:
        """Create detailed marker analysis section"""
        content = []
        
        content.append(Paragraph("Constitutional Marker Analysis", styles['Heading2']))
        
        # Group markers by type
        marker_groups = {}
        for marker in markers:
            marker_type = marker.marker_type.value if hasattr(marker.marker_type, 'value') else str(marker.marker_type)
            if marker_type not in marker_groups:
                marker_groups[marker_type] = []
            marker_groups[marker_type].append(marker)
        
        for marker_type, group_markers in marker_groups.items():
            content.append(Paragraph(f"{marker_type} Markers ({len(group_markers)})", styles['Heading3']))
            
            # Create table for markers
            marker_data = [['Time', 'Speaker', 'Subtype', 'Evidence', 'Confidence']]
            
            for marker in sorted(group_markers, key=lambda m: m.start_time):
                marker_data.append([
                    f"{marker.start_time:.1f}s",
                    marker.speaker or 'Unknown',
                    marker.marker_subtype or 'None',
                    marker.evidence[:50] + '...' if len(marker.evidence) > 50 else marker.evidence,
                    f"{marker.confidence:.3f}"
                ])
            
            table = Table(marker_data, colWidths=[1*inch, 1*inch, 1.5*inch, 3*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            
            content.append(table)
            content.append(Spacer(1, 15))
        
        return content
    
    def _create_rapport_analysis(self, rapport_indicators: List[RapportIndicator], styles) -> List:
        """Create rapport analysis section"""
        content = []
        
        content.append(Paragraph("Rapport Analysis", styles['Heading2']))
        
        if not rapport_indicators:
            content.append(Paragraph("No rapport indicators available.", styles['Normal']))
            return content
        
        # Rapport statistics
        values = [ind.value for ind in rapport_indicators]
        avg_rapport = sum(values) / len(values)
        max_rapport = max(values)
        min_rapport = min(values)
        
        stats_text = (f"Rapport analysis across {len(rapport_indicators)} time points. "
                     f"Average: {avg_rapport:.3f}, Range: {min_rapport:.3f} to {max_rapport:.3f}.")
        
        content.append(Paragraph(stats_text, styles['Normal']))
        content.append(Spacer(1, 10))
        
        # Key moments
        high_rapport_moments = [ind for ind in rapport_indicators if ind.value > 0.7]
        if high_rapport_moments:
            content.append(Paragraph("High Rapport Moments:", styles['Heading3']))
            for moment in high_rapport_moments[:5]:  # Top 5
                moment_text = f"Time {moment.timestamp:.1f}s: Rapport {moment.value:.3f} ({len(moment.contributing_markers)} markers)"
                content.append(Paragraph(moment_text, styles['Normal']))
        
        content.append(Spacer(1, 20))
        return content
    
    def _create_timeline_section(self, markers: List[MarkerEvent], styles) -> List:
        """Create timeline section"""
        content = []
        
        content.append(Paragraph("Conversation Timeline", styles['Heading2']))
        
        # Sort markers by time
        sorted_markers = sorted(markers, key=lambda m: m.start_time)
        
        timeline_data = [['Time', 'Type', 'Speaker', 'Evidence']]
        
        for marker in sorted_markers:
            timeline_data.append([
                f"{marker.start_time:.1f}s",
                str(marker.marker_type),
                marker.speaker or 'Unknown',
                marker.evidence[:60] + '...' if len(marker.evidence) > 60 else marker.evidence
            ])
        
        table = Table(timeline_data, colWidths=[1*inch, 1.5*inch, 1*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        content.append(table)
        return content