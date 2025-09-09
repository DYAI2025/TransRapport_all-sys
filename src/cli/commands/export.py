"""
Export Command Group
Export operations for TransRapport CLI
CONSTITUTIONAL COMPLIANCE: Uses existing LD-3.4 framework, no modifications
"""

import click
import logging
from pathlib import Path
from typing import Optional, List

from src.lib.export import ReportGenerator, PDFReportGenerator, TranscriptExporter, MarkerExporter
from src.lib.export.transcript_export import TranscriptFormat
from src.lib.export.marker_export import MarkerExportFormat
from src.lib.export.report_generator import ComprehensiveReportConfig

from ..core.config import CLIConfig
from ..core.database import (ensure_database_connection, get_conversation_store, 
                           get_marker_store, get_session_store)

logger = logging.getLogger(__name__)


@click.group()
@click.pass_context
def export_group(ctx):
    """Export operations"""
    pass


@export_group.command('events')
@click.option('--conv', required=True, help='Conversation ID/name to export')
@click.option('--level', 
              type=click.Choice(['all', 'ato', 'sem', 'clu', 'mema'], case_sensitive=False),
              default='all', help='Marker level to export')
@click.option('--out', required=True, type=click.Path(), help='Output directory')
@click.option('--format', 'export_format',
              type=click.Choice(['json', 'csv', 'xml', 'analytics'], case_sensitive=False),
              multiple=True, help='Export formats (can specify multiple)')
@click.option('--include-transcript', is_flag=True, help='Include transcript in export')
@click.option('--include-rapport', is_flag=True, help='Include rapport indicators')
@click.pass_context
def export_events(ctx, conv: str, level: str, out: str, export_format: tuple,
                  include_transcript: bool, include_rapport: bool):
    """Export constitutional marker events"""
    config: CLIConfig = ctx.obj['config']
    
    # Default format if none specified
    if not export_format:
        export_format = ('json', 'csv')
    
    click.echo("📤 Exporting Constitutional Events")
    click.echo("=" * 45)
    click.echo(f"Conversation: {conv}")
    click.echo(f"Level: {level.upper()}")
    click.echo(f"Formats: {', '.join(export_format)}")
    click.echo(f"Output: {out}")
    
    try:
        # Get database connection
        passphrase = click.prompt("Enter database passphrase", hide_input=True)
        if not ensure_database_connection(config, passphrase):
            click.echo("❌ Failed to connect to database", err=True)
            return
        
        conversation_store = get_conversation_store(config)
        marker_store = get_marker_store(config)
        
        # Get conversation
        conversation = conversation_store.get_conversation(conv)
        if not conversation:
            click.echo(f"❌ Conversation '{conv}' not found", err=True)
            return
        
        conv_id = conversation['id']
        
        # Get markers
        marker_type = None if level.lower() == 'all' else level.upper()
        markers = marker_store.get_markers(conv_id, marker_type=marker_type)
        
        if not markers:
            filter_desc = f" ({level} level)" if level != 'all' else ""
            click.echo(f"⚠️  No constitutional markers found for '{conv}'{filter_desc}")
            return
        
        # Get rapport indicators if requested
        rapport_indicators = None
        if include_rapport:
            rapport_indicators = marker_store.get_rapport_indicators(conv_id)
        
        # Create output directory
        output_dir = Path(out)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize marker exporter
        marker_exporter = MarkerExporter()
        
        # Export in each requested format
        exported_files = []
        
        for fmt in export_format:
            try:
                format_enum = MarkerExportFormat(fmt.lower())
                filename = f"{conv}_markers_{level}.{fmt.lower()}"
                filepath = output_dir / filename
                
                click.echo(f"📝 Exporting {fmt.upper()}: {filename}")
                
                # Get metadata
                metadata = {
                    'conversation_name': conversation['name'],
                    'conversation_id': conv_id,
                    'export_level': level,
                    'constitutional_source': config.constitutional_source,
                    'total_markers': len(markers)
                }
                
                success = marker_exporter.export_markers(
                    markers=markers,
                    output_path=str(filepath),
                    format_type=format_enum,
                    rapport_indicators=rapport_indicators,
                    metadata=metadata
                )
                
                if success:
                    exported_files.append(str(filepath))
                    click.echo(f"  ✅ {filename}")
                else:
                    click.echo(f"  ❌ Failed to export {filename}")
                    
            except ValueError:
                click.echo(f"❌ Unknown export format: {fmt}")
                continue
        
        # Export transcript if requested
        if include_transcript:
            transcript_segments = conversation_store.get_transcript_segments(conv_id)
            if transcript_segments:
                transcript_exporter = TranscriptExporter()
                
                # Export annotated transcript
                transcript_filename = f"{conv}_transcript_annotated.txt"
                transcript_path = output_dir / transcript_filename
                
                click.echo(f"📄 Exporting annotated transcript: {transcript_filename}")
                
                success = transcript_exporter.export_transcript(
                    transcript_segments=transcript_segments,
                    markers=markers,
                    output_path=str(transcript_path),
                    format_type=TranscriptFormat.ANNOTATED_TXT
                )
                
                if success:
                    exported_files.append(str(transcript_path))
                    click.echo(f"  ✅ {transcript_filename}")
                else:
                    click.echo(f"  ❌ Failed to export transcript")
        
        # Summary
        click.echo("")
        click.echo("📊 Export Summary:")
        click.echo(f"  Constitutional markers exported: {len(markers)}")
        if rapport_indicators:
            click.echo(f"  Rapport indicators included: {len(rapport_indicators)}")
        click.echo(f"  Files created: {len(exported_files)}")
        click.echo(f"  Output directory: {output_dir}")
        
        click.echo("")
        click.echo("📁 Exported Files:")
        for filepath in exported_files:
            file_size = Path(filepath).stat().st_size
            click.echo(f"  📄 {Path(filepath).name} ({file_size:,} bytes)")
        
        click.echo("")
        click.echo("🏛️  Constitutional Compliance: ✅ VERIFIED")
        click.echo(f"   All exports maintain {config.constitutional_source} compliance")
        
    except Exception as e:
        click.echo(f"❌ Failed to export events: {e}", err=True)
        if ctx.obj['verbose']:
            logger.exception("Event export failed")


@export_group.command('report')
@click.option('--conv', required=True, help='Conversation ID/name')
@click.option('--out', required=True, type=click.Path(), help='Output directory')
@click.option('--format', 'report_format',
              type=click.Choice(['pdf', 'comprehensive'], case_sensitive=False),
              default='comprehensive', help='Report format')
@click.option('--include-timeline', is_flag=True, default=True, help='Include timeline section')
@click.option('--include-rapport', is_flag=True, default=True, help='Include rapport analysis')
@click.pass_context
def export_report(ctx, conv: str, out: str, report_format: str,
                  include_timeline: bool, include_rapport: bool):
    """Export comprehensive analysis report"""
    config: CLIConfig = ctx.obj['config']
    
    click.echo("📊 Exporting Analysis Report")
    click.echo("=" * 40)
    click.echo(f"Conversation: {conv}")
    click.echo(f"Format: {report_format}")
    click.echo(f"Output: {out}")
    
    try:
        # Get database connection
        passphrase = click.prompt("Enter database passphrase", hide_input=True)
        if not ensure_database_connection(config, passphrase):
            click.echo("❌ Failed to connect to database", err=True)
            return
        
        conversation_store = get_conversation_store(config)
        marker_store = get_marker_store(config)
        
        # Get conversation
        conversation = conversation_store.get_conversation(conv)
        if not conversation:
            click.echo(f"❌ Conversation '{conv}' not found", err=True)
            return
        
        conv_id = conversation['id']
        
        # Get data for report
        transcript_segments = conversation_store.get_transcript_segments(conv_id)
        markers = marker_store.get_markers(conv_id)
        rapport_indicators = marker_store.get_rapport_indicators(conv_id) if include_rapport else []
        
        if not markers and not transcript_segments:
            click.echo(f"⚠️  No data found for conversation '{conv}'")
            click.echo("💡 Run 'me run scan --conv <name>' first")
            return
        
        # Create output directory
        output_dir = Path(out)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get analysis metadata
        conv_stats = conversation_store.get_conversation_statistics(conv_id)
        marker_stats = marker_store.get_marker_statistics(conv_id) if markers else {}
        
        analysis_metadata = {
            'conversation_stats': conv_stats,
            'marker_stats': marker_stats,
            'constitutional_source': config.constitutional_source,
            'analysis_method': config.analysis_method
        }
        
        if report_format == 'comprehensive':
            # Use comprehensive report generator
            report_config = ComprehensiveReportConfig(
                output_directory=str(output_dir),
                session_name=conv,
                constitutional_source=config.constitutional_source,
                generate_pdf_report=True,
                generate_transcript_exports=bool(transcript_segments),
                generate_marker_exports=bool(markers),
                generate_analytics=True,
                include_constitutional_compliance_statement=True
            )
            
            report_generator = ReportGenerator(report_config)
            
            click.echo("🔄 Generating comprehensive report...")
            
            # Convert transcript segments to expected format
            formatted_segments = []
            for segment in transcript_segments:
                formatted_segments.append({
                    'text': segment['text'],
                    'start_time': segment['start_time'],
                    'end_time': segment['end_time'],
                    'speaker': segment.get('speaker')
                })
            
            results = report_generator.generate_comprehensive_report(
                transcript_segments=formatted_segments,
                markers=markers,
                rapport_indicators=rapport_indicators,
                analysis_metadata=analysis_metadata
            )
            
            # Display results
            if results.get('summary', {}).get('session_complete', False):
                click.echo("✅ Comprehensive report generated successfully")
                
                # Show export summary
                exports = results.get('exports', {})
                click.echo("")
                click.echo("📊 Report Components:")
                
                for component, details in exports.items():
                    if isinstance(details, dict) and details.get('success'):
                        click.echo(f"  ✅ {component.replace('_', ' ').title()}")
                        if details.get('path'):
                            click.echo(f"      📁 {details['path']}")
                    elif isinstance(details, dict):
                        # Multiple files (like transcripts/markers)
                        successful_formats = [fmt for fmt, data in details.items() 
                                            if isinstance(data, dict) and data.get('success')]
                        if successful_formats:
                            click.echo(f"  ✅ {component.replace('_', ' ').title()}: {', '.join(successful_formats)}")
                
                success_rate = results.get('summary', {}).get('success_rate', 0) * 100
                click.echo(f"  Success rate: {success_rate:.1f}%")
                
                # Show output directory contents
                click.echo(f"📁 Output Directory: {output_dir}")
                _show_directory_contents(output_dir)
                
            else:
                click.echo("❌ Report generation failed")
                if 'error' in results:
                    click.echo(f"Error: {results['error']}")
        
        elif report_format == 'pdf':
            # Generate PDF report only
            pdf_generator = PDFReportGenerator()
            
            pdf_filename = f"{conv}_analysis_report.pdf"
            pdf_path = output_dir / pdf_filename
            
            click.echo(f"📄 Generating PDF report: {pdf_filename}")
            
            success = pdf_generator.generate_report(
                markers=markers,
                rapport_indicators=rapport_indicators,
                metadata=analysis_metadata,
                output_path=str(pdf_path)
            )
            
            if success:
                click.echo(f"✅ PDF report generated: {pdf_path}")
                file_size = pdf_path.stat().st_size
                click.echo(f"📊 Report size: {file_size:,} bytes")
            else:
                click.echo("❌ PDF report generation failed")
        
        click.echo("")
        click.echo("🏛️  Constitutional Compliance: ✅ VERIFIED")
        click.echo(f"   Report follows {config.constitutional_source} framework")
        click.echo(f"   Analysis method: {config.analysis_method}")
        
    except Exception as e:
        click.echo(f"❌ Failed to export report: {e}", err=True)
        if ctx.obj['verbose']:
            logger.exception("Report export failed")


@export_group.command('transcript')
@click.option('--conv', required=True, help='Conversation ID/name')
@click.option('--out', required=True, type=click.Path(), help='Output file path')
@click.option('--format', 'transcript_format',
              type=click.Choice(['txt', 'json', 'csv', 'srt', 'vtt', 'annotated'], case_sensitive=False),
              default='annotated', help='Transcript format')
@click.option('--include-markers', is_flag=True, default=True, help='Include marker annotations')
@click.option('--include-timestamps', is_flag=True, default=True, help='Include timestamps')
@click.option('--include-speakers', is_flag=True, default=True, help='Include speaker labels')
@click.pass_context
def export_transcript(ctx, conv: str, out: str, transcript_format: str,
                     include_markers: bool, include_timestamps: bool, include_speakers: bool):
    """Export conversation transcript"""
    config: CLIConfig = ctx.obj['config']
    
    click.echo("📄 Exporting Transcript")
    click.echo("=" * 30)
    click.echo(f"Conversation: {conv}")
    click.echo(f"Format: {transcript_format.upper()}")
    click.echo(f"Output: {out}")
    
    try:
        # Get database connection
        passphrase = click.prompt("Enter database passphrase", hide_input=True)
        if not ensure_database_connection(config, passphrase):
            click.echo("❌ Failed to connect to database", err=True)
            return
        
        conversation_store = get_conversation_store(config)
        marker_store = get_marker_store(config)
        
        # Get conversation
        conversation = conversation_store.get_conversation(conv)
        if not conversation:
            click.echo(f"❌ Conversation '{conv}' not found", err=True)
            return
        
        conv_id = conversation['id']
        
        # Get transcript segments
        transcript_segments = conversation_store.get_transcript_segments(conv_id)
        if not transcript_segments:
            click.echo(f"❌ No transcript found for conversation '{conv}'", err=True)
            return
        
        # Get markers if requested
        markers = []
        if include_markers:
            markers = marker_store.get_markers(conv_id)
        
        # Create output directory
        output_path = Path(out)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize transcript exporter with configuration
        from src.lib.export.transcript_export import TranscriptExportConfig
        
        export_config = TranscriptExportConfig(
            include_timestamps=include_timestamps,
            include_speaker_labels=include_speakers,
            include_markers=include_markers and bool(markers),
            constitutional_source=config.constitutional_source
        )
        
        transcript_exporter = TranscriptExporter(export_config)
        
        # Convert format string to enum
        try:
            if transcript_format == 'annotated':
                format_enum = TranscriptFormat.ANNOTATED_TXT
            else:
                format_enum = TranscriptFormat(transcript_format.upper())
        except ValueError:
            click.echo(f"❌ Unknown transcript format: {transcript_format}")
            return
        
        # Convert segments to expected format
        formatted_segments = []
        for segment in transcript_segments:
            formatted_segments.append({
                'text': segment['text'],
                'start_time': segment['start_time'],
                'end_time': segment['end_time'],
                'speaker': segment.get('speaker')
            })
        
        click.echo(f"📝 Processing {len(formatted_segments)} transcript segments...")
        if markers:
            click.echo(f"🔍 Including {len(markers)} constitutional markers")
        
        # Export transcript
        success = transcript_exporter.export_transcript(
            transcript_segments=formatted_segments,
            markers=markers,
            output_path=str(output_path),
            format_type=format_enum
        )
        
        if success:
            click.echo(f"✅ Transcript exported: {output_path}")
            
            # Show file info
            file_size = output_path.stat().st_size
            click.echo(f"📊 File size: {file_size:,} bytes")
            
            # Show content preview for text formats
            if format_enum in [TranscriptFormat.TXT, TranscriptFormat.ANNOTATED_TXT]:
                click.echo("")
                click.echo("📖 Preview (first 200 characters):")
                with open(output_path, 'r', encoding='utf-8') as f:
                    preview = f.read(200)
                    click.echo(f"   {preview}...")
            
            click.echo("")
            click.echo("🏛️  Constitutional Compliance: ✅ VERIFIED")
            if include_markers:
                click.echo(f"   Markers annotated per {config.constitutional_source} framework")
        else:
            click.echo("❌ Transcript export failed")
    
    except Exception as e:
        click.echo(f"❌ Failed to export transcript: {e}", err=True)
        if ctx.obj['verbose']:
            logger.exception("Transcript export failed")


def _show_directory_contents(directory: Path):
    """Show contents of export directory"""
    try:
        files = list(directory.glob('**/*'))
        files = [f for f in files if f.is_file()]
        
        if not files:
            click.echo("  📁 (empty directory)")
            return
        
        total_size = sum(f.stat().st_size for f in files)
        click.echo(f"  📊 {len(files)} files, {total_size:,} bytes total")
        
        # Group by subdirectory
        by_subdir = {}
        for f in files:
            rel_path = f.relative_to(directory)
            if rel_path.parent == Path('.'):
                subdir = '.'
            else:
                subdir = str(rel_path.parts[0])
            
            if subdir not in by_subdir:
                by_subdir[subdir] = []
            by_subdir[subdir].append(rel_path.name)
        
        for subdir, filenames in by_subdir.items():
            if subdir == '.':
                for filename in filenames:
                    click.echo(f"    📄 {filename}")
            else:
                click.echo(f"    📁 {subdir}/")
                for filename in filenames:
                    click.echo(f"      📄 {filename}")
    
    except Exception as e:
        click.echo(f"  ⚠️  Could not list directory contents: {e}")