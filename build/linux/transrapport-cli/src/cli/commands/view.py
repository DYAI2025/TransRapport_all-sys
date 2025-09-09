"""
View Command Group
Data viewing operations for TransRapport CLI
CONSTITUTIONAL COMPLIANCE: Uses existing LD-3.4 framework, no modifications
"""

import click
import json
import logging
from typing import Optional, List

from ..core.config import CLIConfig
from ..core.database import (ensure_database_connection, get_conversation_store, 
                           get_marker_store, get_session_store)

logger = logging.getLogger(__name__)


@click.group()
@click.pass_context
def view_group(ctx):
    """Data viewing operations"""
    pass


@view_group.command('events')
@click.option('--conv', required=True, help='Conversation ID/name')
@click.option('--level', 
              type=click.Choice(['all', 'ato', 'sem', 'clu', 'mema'], case_sensitive=False),
              default='all', help='Marker level to view')
@click.option('--last', type=int, help='Show last N events')
@click.option('--start-time', type=float, help='Start time filter (seconds)')
@click.option('--end-time', type=float, help='End time filter (seconds)')
@click.option('--min-confidence', type=float, help='Minimum confidence threshold')
@click.option('--format', 'output_format',
              type=click.Choice(['table', 'json', 'timeline'], case_sensitive=False),
              default='table', help='Output format')
@click.pass_context
def view_events(ctx, conv: str, level: str, last: Optional[int], 
                start_time: Optional[float], end_time: Optional[float],
                min_confidence: Optional[float], output_format: str):
    """View constitutional marker events"""
    config: CLIConfig = ctx.obj['config']
    
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
        
        # Get markers with filters
        marker_type = None if level.lower() == 'all' else level.upper()
        markers = marker_store.get_markers(
            conversation_id=conv_id,
            marker_type=marker_type,
            start_time=start_time,
            end_time=end_time,
            min_confidence=min_confidence
        )
        
        if not markers:
            filter_desc = f" ({level} level)" if level != 'all' else ""
            click.echo(f"📝 No constitutional markers found for '{conv}'{filter_desc}")
            return
        
        # Sort by time and apply limit
        markers.sort(key=lambda m: m.start_time)
        if last and last < len(markers):
            markers = markers[-last:]
        
        # Display based on format
        if output_format == 'table':
            _display_markers_table(markers, conversation['name'], level)
        elif output_format == 'json':
            _display_markers_json(markers)
        elif output_format == 'timeline':
            _display_markers_timeline(markers, conversation['name'])
        
    except Exception as e:
        click.echo(f"❌ Failed to view events: {e}", err=True)
        if ctx.obj['verbose']:
            logger.exception("Event viewing failed")


def _display_markers_table(markers: List, conv_name: str, level: str):
    """Display markers in table format"""
    click.echo(f"🔍 Constitutional Markers: {conv_name}")
    click.echo(f"📊 Level: {level.upper()} | Count: {len(markers)}")
    click.echo("=" * 100)
    
    # Header
    click.echo(f"{'Time':>8} {'Type':>4} {'Subtype':<20} {'Conf':>5} {'Speaker':<10} {'Evidence':<40}")
    click.echo("-" * 100)
    
    # Markers
    for marker in markers:
        evidence_short = marker.evidence[:37] + "..." if len(marker.evidence) > 40 else marker.evidence
        
        click.echo(
            f"{marker.start_time:8.1f}s "
            f"{str(marker.marker_type):>4} "
            f"{marker.marker_subtype or 'None':<20} "
            f"{marker.confidence:5.3f} "
            f"{marker.speaker or 'Unknown':<10} "
            f"{evidence_short:<40}"
        )


def _display_markers_json(markers: List):
    """Display markers in JSON format"""
    markers_data = []
    
    for marker in markers:
        marker_data = {
            'id': marker.id,
            'type': str(marker.marker_type),
            'subtype': marker.marker_subtype,
            'start_time': marker.start_time,
            'end_time': marker.end_time,
            'confidence': marker.confidence,
            'speaker': marker.speaker,
            'evidence': marker.evidence,
            'explanation': marker.explanation,
            'constitutional_source': marker.constitutional_source,
            'analysis_method': marker.analysis_method
        }
        markers_data.append(marker_data)
    
    click.echo(json.dumps(markers_data, indent=2, ensure_ascii=False))


def _display_markers_timeline(markers: List, conv_name: str):
    """Display markers in timeline format"""
    click.echo(f"📈 Timeline View: {conv_name}")
    click.echo(f"📊 Markers: {len(markers)}")
    click.echo("=" * 80)
    
    for marker in markers:
        # Timeline entry
        click.echo(f"[{marker.start_time:6.1f}s] {marker.marker_type} • {marker.marker_subtype}")
        
        # Speaker and confidence
        speaker = marker.speaker or "Unknown"
        click.echo(f"           👤 {speaker} | 📊 {marker.confidence:.3f}")
        
        # Evidence
        click.echo(f"           💬 {marker.evidence}")
        
        # Explanation if available
        if marker.explanation:
            explanation = marker.explanation[:100] + "..." if len(marker.explanation) > 100 else marker.explanation
            click.echo(f"           💭 {explanation}")
        
        click.echo()


@view_group.command('rapport')
@click.option('--conv', required=True, help='Conversation ID/name')
@click.option('--start-time', type=float, help='Start time filter (seconds)')
@click.option('--end-time', type=float, help='End time filter (seconds)')
@click.option('--format', 'output_format',
              type=click.Choice(['summary', 'timeline', 'json'], case_sensitive=False),
              default='summary', help='Output format')
@click.pass_context
def view_rapport(ctx, conv: str, start_time: Optional[float], 
                 end_time: Optional[float], output_format: str):
    """View rapport analysis results"""
    config: CLIConfig = ctx.obj['config']
    
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
        
        # Get rapport indicators
        indicators = marker_store.get_rapport_indicators(
            conversation_id=conv_id,
            start_time=start_time,
            end_time=end_time
        )
        
        if not indicators:
            click.echo(f"📊 No rapport indicators found for conversation '{conv}'")
            click.echo("💡 Run 'me run scan --conv <name>' to generate rapport analysis")
            return
        
        # Display based on format
        if output_format == 'summary':
            _display_rapport_summary(indicators, conversation['name'])
        elif output_format == 'timeline':
            _display_rapport_timeline(indicators, conversation['name'])
        elif output_format == 'json':
            _display_rapport_json(indicators)
        
    except Exception as e:
        click.echo(f"❌ Failed to view rapport: {e}", err=True)
        if ctx.obj['verbose']:
            logger.exception("Rapport viewing failed")


def _display_rapport_summary(indicators: List, conv_name: str):
    """Display rapport summary"""
    values = [ind.value for ind in indicators]
    
    avg_rapport = sum(values) / len(values)
    max_rapport = max(values)
    min_rapport = min(values)
    
    # Trend analysis
    trend_counts = {}
    for ind in indicators:
        trend = str(ind.trend)
        trend_counts[trend] = trend_counts.get(trend, 0) + 1
    
    click.echo(f"💫 Rapport Analysis: {conv_name}")
    click.echo("=" * 50)
    
    click.echo(f"📊 Summary Statistics:")
    click.echo(f"  Indicators: {len(indicators)}")
    click.echo(f"  Average rapport: {avg_rapport:.3f}")
    click.echo(f"  Range: {min_rapport:.3f} to {max_rapport:.3f}")
    click.echo()
    
    click.echo(f"📈 Rapport Trends:")
    for trend, count in sorted(trend_counts.items()):
        percentage = (count / len(indicators)) * 100
        click.echo(f"  {trend}: {count} ({percentage:.1f}%)")
    click.echo()
    
    # Rapport quality assessment
    high_rapport = sum(1 for v in values if v > 0.7)
    medium_rapport = sum(1 for v in values if 0.3 <= v <= 0.7)
    low_rapport = sum(1 for v in values if v < 0.3)
    
    click.echo(f"🎯 Rapport Quality:")
    click.echo(f"  High rapport (>0.7): {high_rapport} ({high_rapport/len(indicators)*100:.1f}%)")
    click.echo(f"  Medium rapport (0.3-0.7): {medium_rapport} ({medium_rapport/len(indicators)*100:.1f}%)")
    click.echo(f"  Low rapport (<0.3): {low_rapport} ({low_rapport/len(indicators)*100:.1f}%)")


def _display_rapport_timeline(indicators: List, conv_name: str):
    """Display rapport timeline"""
    click.echo(f"📈 Rapport Timeline: {conv_name}")
    click.echo("=" * 60)
    
    for indicator in indicators:
        # Rapport bar visualization
        bar_width = int(indicator.value * 20)  # Scale to 20 chars
        bar = "█" * bar_width + "░" * (20 - bar_width)
        
        # Trend icon
        trend_icons = {
            'INCREASING': '📈',
            'DECREASING': '📉', 
            'STABLE': '➡️',
            'VOLATILE': '📊'
        }
        trend_icon = trend_icons.get(str(indicator.trend), '❓')
        
        click.echo(f"[{indicator.timestamp:6.1f}s] {bar} {indicator.value:.3f} {trend_icon}")


def _display_rapport_json(indicators: List):
    """Display rapport indicators in JSON format"""
    indicators_data = []
    
    for indicator in indicators:
        indicator_data = {
            'timestamp': indicator.timestamp,
            'value': indicator.value,
            'trend': str(indicator.trend),
            'confidence': indicator.confidence
        }
        indicators_data.append(indicator_data)
    
    click.echo(json.dumps(indicators_data, indent=2))


@view_group.command('stats')
@click.option('--conv', help='Conversation ID/name (show all if not specified)')
@click.pass_context
def view_stats(ctx, conv: Optional[str]):
    """View analysis statistics"""
    config: CLIConfig = ctx.obj['config']
    
    try:
        # Get database connection
        passphrase = click.prompt("Enter database passphrase", hide_input=True)
        if not ensure_database_connection(config, passphrase):
            click.echo("❌ Failed to connect to database", err=True)
            return
        
        conversation_store = get_conversation_store(config)
        marker_store = get_marker_store(config)
        session_store = get_session_store(config)
        
        if conv:
            # Show stats for specific conversation
            conversation = conversation_store.get_conversation(conv)
            if not conversation:
                click.echo(f"❌ Conversation '{conv}' not found", err=True)
                return
            
            conv_id = conversation['id']
            
            # Get comprehensive statistics
            conv_stats = conversation_store.get_conversation_statistics(conv_id)
            marker_stats = marker_store.get_marker_statistics(conv_id)
            session_summary = session_store.get_session_summary(conv_id)
            
            _display_conversation_stats(conversation, conv_stats, marker_stats, session_summary)
            
        else:
            # Show overall system statistics
            conversations = conversation_store.list_conversations()
            
            click.echo("📊 TransRapport System Statistics")
            click.echo("=" * 50)
            
            click.echo(f"🏛️  Constitutional Framework: {config.constitutional_source}")
            click.echo(f"📚 Analysis Method: {config.analysis_method}")
            click.echo()
            
            click.echo(f"📝 Conversations: {len(conversations)}")
            
            # Aggregate statistics
            total_segments = 0
            total_markers = 0
            total_sessions = 0
            
            for conversation in conversations:
                conv_stats = conversation_store.get_conversation_statistics(conversation['id'])
                session_summary = session_store.get_session_summary(conversation['id'])
                
                total_segments += conv_stats.get('segment_count', 0)
                total_markers += conv_stats.get('marker_count', 0)
                total_sessions += session_summary.get('total_sessions', 0)
            
            click.echo(f"📄 Total transcript segments: {total_segments}")
            click.echo(f"🔍 Total constitutional markers: {total_markers}")
            click.echo(f"⚙️  Total analysis sessions: {total_sessions}")
            
            if conversations:
                click.echo()
                click.echo("📋 Recent Conversations:")
                for conv in conversations[:5]:
                    status_icon = "✅" if conv['status'] == 'active' else "📁"
                    click.echo(f"  {status_icon} {conv['name']} ({conv['created_at'][:10]})")
        
    except Exception as e:
        click.echo(f"❌ Failed to view statistics: {e}", err=True)
        if ctx.obj['verbose']:
            logger.exception("Statistics viewing failed")


def _display_conversation_stats(conversation: dict, conv_stats: dict, 
                              marker_stats: dict, session_summary: dict):
    """Display detailed conversation statistics"""
    click.echo(f"📊 Statistics: {conversation['name']}")
    click.echo("=" * 60)
    
    click.echo(f"🆔 Conversation ID: {conversation['id']}")
    click.echo(f"📅 Created: {conversation['created_at']}")
    click.echo(f"🏛️  Constitutional Source: {conversation.get('constitutional_source', 'Unknown')}")
    click.echo()
    
    click.echo("📄 Content Statistics:")
    click.echo(f"  Transcript segments: {conv_stats.get('segment_count', 0)}")
    click.echo(f"  Total duration: {conv_stats.get('total_duration', 0):.1f} seconds")
    click.echo(f"  Speakers detected: {conv_stats.get('speaker_count', 0)}")
    click.echo()
    
    click.echo("🔍 Constitutional Marker Analysis:")
    click.echo(f"  Total markers: {marker_stats.get('total_markers', 0)}")
    click.echo(f"  Unique marker types: {marker_stats.get('unique_types', 0)}")
    click.echo(f"  Unique subtypes: {marker_stats.get('unique_subtypes', 0)}")
    click.echo(f"  Average confidence: {marker_stats.get('avg_confidence', 0):.3f}")
    click.echo(f"  Confidence range: {marker_stats.get('min_confidence', 0):.3f} - {marker_stats.get('max_confidence', 0):.3f}")
    click.echo()
    
    # Marker type distribution
    type_dist = marker_stats.get('type_distribution', {})
    if type_dist:
        click.echo("📋 Marker Type Distribution:")
        for marker_type, stats in type_dist.items():
            click.echo(f"  {marker_type}: {stats['count']} (avg conf: {stats['avg_confidence']:.3f})")
        click.echo()
    
    click.echo("💫 Rapport Analysis:")
    click.echo(f"  Rapport indicators: {conv_stats.get('indicator_count', 0)}")
    click.echo(f"  Average rapport: {conv_stats.get('avg_rapport', 0):.3f}")
    click.echo()
    
    click.echo("⚙️  Analysis Sessions:")
    click.echo(f"  Total sessions: {session_summary.get('total_sessions', 0)}")
    click.echo(f"  Completed: {session_summary.get('completed_sessions', 0)}")
    click.echo(f"  Pending: {session_summary.get('pending_sessions', 0)}")
    click.echo(f"  Failed: {session_summary.get('failed_sessions', 0)}")
    
    avg_processing = session_summary.get('avg_processing_time', 0)
    if avg_processing > 0:
        click.echo(f"  Average processing time: {avg_processing:.2f} seconds")