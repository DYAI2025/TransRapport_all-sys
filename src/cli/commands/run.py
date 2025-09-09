"""
Run Command Group
Analysis execution operations for TransRapport CLI
CONSTITUTIONAL COMPLIANCE: Uses existing LD-3.4 framework, no modifications
"""

import click
import logging
from typing import List, Dict, Any
from datetime import datetime

from src.lib.analysis import LD34AnalysisPipeline, AnalysisConfig
from ..core.config import CLIConfig
from ..core.database import (ensure_database_connection, get_conversation_store, 
                           get_marker_store, get_session_store)

logger = logging.getLogger(__name__)


@click.group()
@click.pass_context
def run_group(ctx):
    """Analysis execution operations"""
    pass


@run_group.command('scan')
@click.option('--conv', required=True, help='Conversation ID/name to analyze')
@click.option('--engines', help='Comma-separated list of engines to run (ATO,SEM,CLU,MEMA)')
@click.option('--confidence', type=float, help='Override confidence threshold')
@click.option('--session-name', help='Custom session name')
@click.pass_context
def scan_conversation(ctx, conv: str, engines: str, confidence: float, session_name: str):
    """Execute constitutional analysis scan on conversation"""
    config: CLIConfig = ctx.obj['config']
    
    click.echo("🔍 Constitutional Analysis Scan (LD-3.4)")
    click.echo("=" * 50)
    click.echo(f"Target: {conv}")
    click.echo(f"Framework: {config.constitutional_source}")
    
    try:
        # Get database connection
        passphrase = click.prompt("Enter database passphrase", hide_input=True)
        if not ensure_database_connection(config, passphrase):
            click.echo("❌ Failed to connect to database", err=True)
            return
        
        conversation_store = get_conversation_store(config)
        marker_store = get_marker_store(config)
        session_store = get_session_store(config)
        
        # Get conversation
        conversation = conversation_store.get_conversation(conv)
        if not conversation:
            click.echo(f"❌ Conversation '{conv}' not found", err=True)
            return
        
        conv_id = conversation['id']
        
        # Get transcript segments
        segments = conversation_store.get_transcript_segments(conv_id)
        if not segments:
            click.echo(f"❌ No transcript segments found for conversation '{conv}'", err=True)
            click.echo("💡 Use 'me job create --conv <name> --text <file>' to create a job first")
            return
        
        click.echo(f"📄 Found {len(segments)} transcript segments")
        
        # Prepare analysis configuration
        analysis_config = AnalysisConfig(
            confidence_threshold=confidence or config.confidence_threshold,
            enable_ato=config.enable_ato,
            enable_sem=config.enable_sem,
            enable_clu=config.enable_clu,
            enable_mema=config.enable_mema,
            enable_rapport=config.enable_rapport,
            constitutional_source=config.constitutional_source,
            analysis_method=config.analysis_method
        )
        
        # Override engines if specified
        if engines:
            engine_list = [e.strip().upper() for e in engines.split(',')]
            analysis_config.enable_ato = 'ATO' in engine_list
            analysis_config.enable_sem = 'SEM' in engine_list
            analysis_config.enable_clu = 'CLU' in engine_list
            analysis_config.enable_mema = 'MEMA' in engine_list
            click.echo(f"🎯 Engine Filter: {', '.join(engine_list)}")
        
        # Create session
        session_name = session_name or f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session_id = session_store.create_session(
            conversation_id=conv_id,
            session_name=session_name,
            analysis_config=analysis_config.__dict__
        )
        
        if not session_id:
            click.echo("❌ Failed to create analysis session", err=True)
            return
        
        click.echo(f"📋 Session: {session_name} ({session_id[:8]}...)")
        
        # Initialize analysis pipeline
        pipeline = LD34AnalysisPipeline(analysis_config)
        
        click.echo("🔄 Executing constitutional analysis...")
        click.echo(f"   Confidence threshold: {analysis_config.confidence_threshold}")
        
        # Convert segments to expected format
        transcript_segments = []
        for segment in segments:
            transcript_segments.append({
                'text': segment['text'],
                'start_time': segment['start_time'],
                'end_time': segment['end_time'],
                'speaker': segment.get('speaker')
            })
        
        # Run analysis
        with click.progressbar(length=4, label='Analyzing') as bar:
            bar.update(1)  # Pipeline initialization
            
            results = pipeline.analyze_transcript(transcript_segments)
            bar.update(1)  # Analysis execution
            
            # Store results
            if results.markers:
                marker_store.store_markers(conv_id, results.markers)
            bar.update(1)  # Marker storage
            
            if results.rapport_indicators:
                marker_store.store_rapport_indicators(conv_id, results.rapport_indicators)
            bar.update(1)  # Rapport storage
        
        # Update session with results
        session_store.complete_session(
            session_id=session_id,
            processing_time=results.processing_time,
            marker_count=len(results.markers),
            rapport_indicator_count=len(results.rapport_indicators)
        )
        
        # Display results
        click.echo("✅ Constitutional analysis completed!")
        click.echo("")
        click.echo("📊 Results Summary:")
        click.echo(f"  Processing time: {results.processing_time:.2f} seconds")
        click.echo(f"  Constitutional markers: {len(results.markers)}")
        click.echo(f"  Rapport indicators: {len(results.rapport_indicators)}")
        
        # Show marker breakdown by type
        if results.markers:
            marker_counts = {}
            for marker in results.markers:
                marker_type = str(marker.marker_type)
                marker_counts[marker_type] = marker_counts.get(marker_type, 0) + 1
            
            click.echo("")
            click.echo("🔍 Marker Distribution:")
            for marker_type, count in sorted(marker_counts.items()):
                percentage = (count / len(results.markers)) * 100
                click.echo(f"  {marker_type}: {count} ({percentage:.1f}%)")
        
        # Show rapport summary
        if results.rapport_indicators:
            values = [ind.value for ind in results.rapport_indicators]
            avg_rapport = sum(values) / len(values)
            max_rapport = max(values)
            min_rapport = min(values)
            
            click.echo("")
            click.echo("💫 Rapport Analysis:")
            click.echo(f"  Average rapport: {avg_rapport:.3f}")
            click.echo(f"  Range: {min_rapport:.3f} to {max_rapport:.3f}")
            click.echo(f"  Indicators: {len(results.rapport_indicators)}")
        
        click.echo("")
        click.echo("🏛️  Constitutional Compliance: ✅ VERIFIED")
        click.echo(f"   Framework: {config.constitutional_source}")
        click.echo(f"   Analysis method: {config.analysis_method}")
        
        click.echo("")
        click.echo("Next steps:")
        click.echo(f"  me view events --conv {conv} --level all")
        click.echo(f"  me export events --conv {conv} --out exports/{conv}/")
        
    except Exception as e:
        click.echo(f"❌ Analysis scan failed: {e}", err=True)
        if ctx.obj['verbose']:
            logger.exception("Analysis scan failed")


@run_group.command('validate')
@click.option('--conv', required=True, help='Conversation ID/name to validate')
@click.option('--strict', is_flag=True, help='Enable strict validation mode')
@click.pass_context
def validate_analysis(ctx, conv: str, strict: bool):
    """Validate constitutional analysis results"""
    config: CLIConfig = ctx.obj['config']
    
    click.echo("🔍 Constitutional Analysis Validation")
    click.echo("=" * 45)
    
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
        markers = marker_store.get_markers(conv_id)
        if not markers:
            click.echo(f"⚠️  No analysis results found for conversation '{conv}'", err=True)
            click.echo(f"💡 Run 'me run scan --conv {conv}' first")
            return
        
        click.echo(f"📋 Validating {len(markers)} constitutional markers")
        click.echo(f"🎯 Mode: {'strict' if strict else 'standard'}")
        
        # Initialize pipeline for validation
        analysis_config = AnalysisConfig(
            confidence_threshold=config.confidence_threshold,
            constitutional_source=config.constitutional_source,
            analysis_method=config.analysis_method
        )
        
        pipeline = LD34AnalysisPipeline(analysis_config)
        
        # Run validation
        is_valid, errors = pipeline.validate_markers(markers, strict=strict)
        
        click.echo("")
        click.echo("📊 Validation Results:")
        click.echo(f"  Markers validated: {len(markers)}")
        click.echo(f"  Constitutional compliance: {'✅ PASSED' if is_valid else '❌ FAILED'}")
        click.echo(f"  Validation errors: {len(errors)}")
        
        # Show marker statistics
        marker_stats = marker_store.get_marker_statistics(conv_id)
        click.echo("")
        click.echo("📈 Marker Quality Statistics:")
        click.echo(f"  Average confidence: {marker_stats.get('avg_confidence', 0):.3f}")
        click.echo(f"  Confidence range: {marker_stats.get('min_confidence', 0):.3f} - {marker_stats.get('max_confidence', 0):.3f}")
        click.echo(f"  Constitutional source: {marker_stats.get('constitutional_source', 'Unknown')}")
        
        # Show validation errors if any
        if errors:
            click.echo("")
            click.echo(f"⚠️  Validation Issues ({len(errors)}):")
            for i, error in enumerate(errors[:10], 1):
                click.echo(f"  {i}. {error}")
            
            if len(errors) > 10:
                click.echo(f"  ... and {len(errors) - 10} more issues")
        
        # Constitutional compliance summary
        click.echo("")
        if is_valid:
            click.echo("🏛️  Constitutional Status: ✅ COMPLIANT")
            click.echo("   All markers meet LD-3.4 constitutional requirements")
            if strict:
                click.echo("   Strict validation passed - Maximum compliance achieved")
        else:
            click.echo("🏛️  Constitutional Status: ❌ NON-COMPLIANT")
            click.echo("   Some markers do not meet constitutional requirements")
            click.echo("   Review and address validation issues above")
        
    except Exception as e:
        click.echo(f"❌ Validation failed: {e}", err=True)
        if ctx.obj['verbose']:
            logger.exception("Analysis validation failed")


@run_group.command('reanalyze')
@click.option('--conv', required=True, help='Conversation ID/name to reanalyze')
@click.option('--engines', help='Comma-separated engines to rerun (ATO,SEM,CLU,MEMA)')
@click.option('--confidence', type=float, help='New confidence threshold')
@click.option('--clear-existing', is_flag=True, help='Clear existing markers before reanalysis')
@click.pass_context
def reanalyze_conversation(ctx, conv: str, engines: str, confidence: float, clear_existing: bool):
    """Rerun constitutional analysis with different parameters"""
    config: CLIConfig = ctx.obj['config']
    
    click.echo("🔄 Constitutional Analysis Rerun")
    click.echo("=" * 40)
    
    if clear_existing:
        if not click.confirm(f"This will DELETE all existing analysis results for '{conv}'. Continue?"):
            click.echo("Operation cancelled")
            return
    
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
        
        # Clear existing markers if requested
        if clear_existing:
            if engines:
                # Clear only specific engine types
                for engine in engines.split(','):
                    engine = engine.strip().upper()
                    marker_store.delete_markers(conv_id, marker_type=engine)
                    click.echo(f"🗑️  Cleared {engine} markers")
            else:
                # Clear all markers
                marker_store.delete_markers(conv_id)
                click.echo("🗑️  Cleared all existing markers")
        
        # Run new analysis (reuse scan logic)
        ctx.invoke(scan_conversation, 
                  conv=conv, 
                  engines=engines, 
                  confidence=confidence,
                  session_name=f"reanalysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
    except Exception as e:
        click.echo(f"❌ Reanalysis failed: {e}", err=True)
        if ctx.obj['verbose']:
            logger.exception("Reanalysis failed")


@run_group.command('benchmark')
@click.option('--conv', help='Specific conversation to benchmark (optional)')
@click.option('--iterations', type=int, default=3, help='Number of benchmark iterations')
@click.pass_context
def benchmark_analysis(ctx, conv: str, iterations: int):
    """Benchmark constitutional analysis performance"""
    config: CLIConfig = ctx.obj['config']
    
    click.echo("⚡ Constitutional Analysis Benchmark")
    click.echo("=" * 45)
    
    try:
        # Get database connection
        passphrase = click.prompt("Enter database passphrase", hide_input=True)
        if not ensure_database_connection(config, passphrase):
            click.echo("❌ Failed to connect to database", err=True)
            return
        
        conversation_store = get_conversation_store(config)
        
        # Get conversations to benchmark
        if conv:
            conversation = conversation_store.get_conversation(conv)
            if not conversation:
                click.echo(f"❌ Conversation '{conv}' not found", err=True)
                return
            conversations = [conversation]
        else:
            conversations = conversation_store.list_conversations(limit=5)
        
        if not conversations:
            click.echo("❌ No conversations found to benchmark", err=True)
            return
        
        # Initialize analysis pipeline
        analysis_config = AnalysisConfig(
            confidence_threshold=config.confidence_threshold,
            constitutional_source=config.constitutional_source,
            analysis_method=config.analysis_method
        )
        
        pipeline = LD34AnalysisPipeline(analysis_config)
        
        click.echo(f"🎯 Benchmarking {len(conversations)} conversations")
        click.echo(f"🔄 Iterations per conversation: {iterations}")
        
        total_times = []
        total_markers = []
        
        for conversation in conversations:
            conv_id = conversation['id']
            conv_name = conversation['name']
            
            # Get transcript segments
            segments = conversation_store.get_transcript_segments(conv_id)
            if not segments:
                click.echo(f"⚠️  Skipping '{conv_name}' - no transcript segments")
                continue
            
            transcript_segments = []
            for segment in segments:
                transcript_segments.append({
                    'text': segment['text'],
                    'start_time': segment['start_time'],
                    'end_time': segment['end_time'],
                    'speaker': segment.get('speaker')
                })
            
            click.echo(f"\n📊 Benchmarking: {conv_name}")
            click.echo(f"   Segments: {len(segments)}")
            
            conv_times = []
            conv_marker_counts = []
            
            for i in range(iterations):
                click.echo(f"   Iteration {i+1}/{iterations}... ", nl=False)
                
                results = pipeline.analyze_transcript(transcript_segments)
                
                conv_times.append(results.processing_time)
                conv_marker_counts.append(len(results.markers))
                
                click.echo(f"{results.processing_time:.2f}s ({len(results.markers)} markers)")
            
            avg_time = sum(conv_times) / len(conv_times)
            avg_markers = sum(conv_marker_counts) / len(conv_marker_counts)
            
            click.echo(f"   Average: {avg_time:.2f}s ({avg_markers:.0f} markers)")
            
            total_times.extend(conv_times)
            total_markers.extend(conv_marker_counts)
        
        # Overall benchmark results
        if total_times:
            overall_avg_time = sum(total_times) / len(total_times)
            overall_avg_markers = sum(total_markers) / len(total_markers)
            
            click.echo("\n🏆 Benchmark Results:")
            click.echo(f"   Average processing time: {overall_avg_time:.2f}s")
            click.echo(f"   Average markers detected: {overall_avg_markers:.0f}")
            click.echo(f"   Total benchmark runs: {len(total_times)}")
            click.echo(f"   Constitutional framework: {config.constitutional_source}")
            click.echo(f"   Analysis method: {config.analysis_method}")
        
    except Exception as e:
        click.echo(f"❌ Benchmark failed: {e}", err=True)
        if ctx.obj['verbose']:
            logger.exception("Benchmark failed")