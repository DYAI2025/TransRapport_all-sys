"""
Markers Command Group
Constitutional marker operations for TransRapport CLI
CONSTITUTIONAL COMPLIANCE: Uses existing LD-3.4 framework, no modifications
"""

import click
import json
import logging
from typing import Dict, Any

from src.lib.analysis import LD34AnalysisPipeline, AnalysisConfig
from ..core.config import CLIConfig
from ..core.database import ensure_database_connection, get_database_manager

logger = logging.getLogger(__name__)


@click.group()
@click.pass_context
def markers_group(ctx):
    """Constitutional marker operations"""
    pass


@markers_group.command('load')
@click.option('--force', is_flag=True, help='Force reload of marker definitions')
@click.pass_context
def load_markers(ctx, force: bool):
    """Load constitutional marker definitions"""
    config: CLIConfig = ctx.obj['config']
    
    click.echo("📋 Loading Constitutional Markers (LD-3.4 Framework)")
    click.echo("=" * 60)
    
    try:
        # Initialize analysis pipeline to load marker definitions
        analysis_config = AnalysisConfig(
            confidence_threshold=config.confidence_threshold,
            enable_ato=config.enable_ato,
            enable_sem=config.enable_sem,
            enable_clu=config.enable_clu,
            enable_mema=config.enable_mema,
            constitutional_source=config.constitutional_source,
            analysis_method=config.analysis_method
        )
        
        pipeline = LD34AnalysisPipeline(analysis_config)
        engine_info = pipeline.get_engine_info()
        
        click.echo(f"✅ Constitutional Framework: {config.constitutional_source}")
        click.echo(f"✅ Analysis Method: {config.analysis_method}")
        click.echo(f"✅ Confidence Threshold: {config.confidence_threshold}")
        click.echo("")
        
        click.echo("🔍 Marker Engines Loaded:")
        for engine_name in engine_info['engines']:
            engine_details = engine_info['engine_details'].get(engine_name, {})
            pattern_count = engine_details.get('patterns', 0)
            click.echo(f"  {engine_name}: {pattern_count} constitutional patterns")
        
        click.echo("")
        click.echo("📊 Marker Types Available:")
        click.echo("  ATO  - Attention markers (direction, acknowledgment, shift, maintenance, focus)")
        click.echo("  SEM  - Semantic markers (alignment, clarification, understanding, expansion, divergence)")
        click.echo("  CLU  - Cluster markers (formation, recognition, reinforcement, dissolution, transition)")
        click.echo("  MEMA - Memory markers (reference, alignment, correction, expansion, integration)")
        
        click.echo("")
        click.echo("✅ Constitutional markers loaded successfully")
        click.echo("Next: Use 'me markers validate --strict' to verify constitutional compliance")
        
    except Exception as e:
        click.echo(f"❌ Failed to load constitutional markers: {e}", err=True)
        if ctx.obj['verbose']:
            logger.exception("Marker loading failed")


@markers_group.command('validate')
@click.option('--strict', is_flag=True, help='Enable strict validation mode')
@click.option('--conv', help='Validate markers for specific conversation')
@click.pass_context
def validate_markers(ctx, strict: bool, conv: str):
    """Validate constitutional marker compliance"""
    config: CLIConfig = ctx.obj['config']
    
    click.echo("🔍 Constitutional Marker Validation (LD-3.4)")
    click.echo("=" * 50)
    
    try:
        # Initialize analysis pipeline for validation
        analysis_config = AnalysisConfig(
            confidence_threshold=config.confidence_threshold,
            constitutional_source=config.constitutional_source,
            analysis_method=config.analysis_method
        )
        
        pipeline = LD34AnalysisPipeline(analysis_config)
        
        if conv:
            # Validate markers for specific conversation
            click.echo(f"🔍 Validating conversation: {conv}")
            
            # Get database connection
            passphrase = click.prompt("Enter database passphrase", hide_input=True)
            if not ensure_database_connection(config, passphrase):
                click.echo("❌ Failed to connect to database", err=True)
                return
            
            from ..core.database import get_marker_store
            marker_store = get_marker_store(config)
            
            # Get markers for conversation
            markers = marker_store.get_markers(conv)
            
            if not markers:
                click.echo(f"⚠️  No markers found for conversation '{conv}'")
                return
            
            # Validate markers
            is_valid, errors = pipeline.validate_markers(markers, strict=strict)
            
            click.echo(f"📊 Validation Results:")
            click.echo(f"  Markers validated: {len(markers)}")
            click.echo(f"  Validation mode: {'strict' if strict else 'standard'}")
            click.echo(f"  Constitutional compliance: {'✅ PASSED' if is_valid else '❌ FAILED'}")
            
            if errors:
                click.echo(f"\n⚠️  Validation Errors ({len(errors)}):")
                for error in errors[:10]:  # Show first 10 errors
                    click.echo(f"  - {error}")
                
                if len(errors) > 10:
                    click.echo(f"  ... and {len(errors) - 10} more errors")
        else:
            # General constitutional compliance validation
            engine_info = pipeline.get_engine_info()
            
            click.echo("🏛️  Constitutional Compliance Check:")
            click.echo(f"  Framework: {config.constitutional_source}")
            click.echo(f"  Analysis Method: {config.analysis_method}")
            click.echo(f"  Engines Active: {len(engine_info['engines'])}")
            click.echo(f"  Rapport Calculation: {'✅' if engine_info['configuration']['rapport_enabled'] else '❌'}")
            
            # Validate engine configuration
            validation_checks = [
                ("Constitutional Source", config.constitutional_source == "LD-3.4-constitution"),
                ("Analysis Method", config.analysis_method == "LD-3.4"),
                ("ATO Engine", "ATO" in engine_info['engines']),
                ("SEM Engine", "SEM" in engine_info['engines']),
                ("CLU Engine", "CLU" in engine_info['engines']),
                ("MEMA Engine", "MEMA" in engine_info['engines']),
                ("Confidence Threshold", config.confidence_threshold >= 0.5),
            ]
            
            click.echo(f"\n🔍 Constitutional Compliance Tests:")
            all_passed = True
            for check_name, passed in validation_checks:
                status = "✅" if passed else "❌"
                click.echo(f"  {status} {check_name}")
                if not passed:
                    all_passed = False
            
            click.echo(f"\n🏛️  Overall Compliance: {'✅ CONSTITUTIONAL' if all_passed else '❌ NON-COMPLIANT'}")
            
            if strict and all_passed:
                click.echo("✅ Strict validation PASSED - Full LD-3.4 constitutional compliance")
            elif not strict and all_passed:
                click.echo("✅ Standard validation PASSED - Basic constitutional compliance")
        
    except Exception as e:
        click.echo(f"❌ Validation failed: {e}", err=True)
        if ctx.obj['verbose']:
            logger.exception("Marker validation failed")


@markers_group.command('list')
@click.option('--type', help='Filter by marker type (ATO, SEM, CLU, MEMA)')
@click.option('--conv', help='List markers for specific conversation')
@click.option('--limit', type=int, default=20, help='Maximum number of markers to show')
@click.pass_context
def list_markers(ctx, type: str, conv: str, limit: int):
    """List constitutional markers"""
    config: CLIConfig = ctx.obj['config']
    
    if not conv:
        click.echo("❌ Conversation ID required. Use --conv <conversation_id>", err=True)
        return
    
    try:
        # Get database connection
        passphrase = click.prompt("Enter database passphrase", hide_input=True)
        if not ensure_database_connection(config, passphrase):
            click.echo("❌ Failed to connect to database", err=True)
            return
        
        from ..core.database import get_marker_store
        marker_store = get_marker_store(config)
        
        # Get markers
        markers = marker_store.get_markers(conv, marker_type=type)
        
        if not markers:
            type_filter = f" of type {type}" if type else ""
            click.echo(f"⚠️  No markers found for conversation '{conv}'{type_filter}")
            return
        
        # Limit results
        display_markers = markers[:limit]
        
        click.echo(f"📋 Constitutional Markers for '{conv}'")
        if type:
            click.echo(f"🔍 Filtered by type: {type}")
        click.echo(f"📊 Showing {len(display_markers)} of {len(markers)} markers")
        click.echo("=" * 80)
        
        for marker in display_markers:
            click.echo(f"[{marker.start_time:6.1f}s] {marker.marker_type} - {marker.marker_subtype}")
            click.echo(f"  Speaker: {marker.speaker or 'Unknown'}")
            click.echo(f"  Confidence: {marker.confidence:.3f}")
            click.echo(f"  Evidence: {marker.evidence[:60]}{'...' if len(marker.evidence) > 60 else ''}")
            click.echo()
        
        if len(markers) > limit:
            click.echo(f"... and {len(markers) - limit} more markers")
            click.echo(f"Use --limit {len(markers)} to see all markers")
        
    except Exception as e:
        click.echo(f"❌ Failed to list markers: {e}", err=True)
        if ctx.obj['verbose']:
            logger.exception("Marker listing failed")


@markers_group.command('info')
@click.pass_context
def marker_info(ctx):
    """Show constitutional marker framework information"""
    config: CLIConfig = ctx.obj['config']
    
    click.echo("🏛️  Constitutional Marker Framework Information")
    click.echo("=" * 60)
    
    click.echo(f"📋 Framework: {config.constitutional_source}")
    click.echo(f"🔬 Analysis Method: {config.analysis_method}")
    click.echo(f"⚖️  Confidence Threshold: {config.confidence_threshold}")
    click.echo("")
    
    click.echo("🔍 Constitutional Marker Types:")
    click.echo("")
    
    marker_types = {
        "ATO (Attention)": {
            "description": "Attention and focus markers in conversational flow",
            "subtypes": ["direction", "acknowledgment", "shift", "maintenance", "focus"]
        },
        "SEM (Semantic)": {
            "description": "Semantic alignment and meaning construction markers",
            "subtypes": ["alignment", "clarification", "understanding", "expansion", "divergence"]
        },
        "CLU (Cluster)": {
            "description": "Cluster formation and shared understanding markers",
            "subtypes": ["formation", "recognition", "reinforcement", "dissolution", "transition"]
        },
        "MEMA (Memory)": {
            "description": "Memory references and conversational memory markers",
            "subtypes": ["reference", "alignment", "correction", "expansion", "integration"]
        }
    }
    
    for marker_type, info in marker_types.items():
        click.echo(f"📌 {marker_type}")
        click.echo(f"   {info['description']}")
        click.echo(f"   Subtypes: {', '.join(info['subtypes'])}")
        click.echo()
    
    click.echo("🎯 Constitutional Compliance:")
    click.echo("  ✓ Library reuse approach (no framework modifications)")
    click.echo("  ✓ Existing LD-3.4 pattern definitions")
    click.echo("  ✓ Constitutional source attribution")
    click.echo("  ✓ Confidence-based marker validation")
    click.echo("")
    
    click.echo("Next steps:")
    click.echo("  me job create --help     # Create analysis job")
    click.echo("  me run scan --help       # Execute constitutional analysis")