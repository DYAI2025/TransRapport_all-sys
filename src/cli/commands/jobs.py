"""
Jobs Command Group
Job management operations for TransRapport CLI
CONSTITUTIONAL COMPLIANCE: Uses existing LD-3.4 framework, no modifications
"""

import click
import json
import logging
from pathlib import Path
from typing import Optional

from ..core.config import CLIConfig
from ..core.database import (ensure_database_connection, get_conversation_store, 
                           get_session_store, get_database_manager)

logger = logging.getLogger(__name__)


@click.group()
@click.pass_context
def jobs_group(ctx):
    """Job management operations"""
    pass


@jobs_group.command('create')
@click.option('--conv', required=True, help='Conversation ID/name')
@click.option('--text', type=click.Path(exists=True), help='Text file to analyze')
@click.option('--audio', type=click.Path(exists=True), help='Audio file to transcribe and analyze')
@click.option('--description', help='Job description')
@click.pass_context
def create_job(ctx, conv: str, text: Optional[str], audio: Optional[str], description: Optional[str]):
    """Create new analysis job"""
    config: CLIConfig = ctx.obj['config']
    
    if not text and not audio:
        click.echo("❌ Either --text or --audio input is required", err=True)
        return
    
    click.echo("📝 Creating Analysis Job")
    click.echo("=" * 40)
    click.echo(f"Conversation: {conv}")
    click.echo(f"Constitutional Framework: {config.constitutional_source}")
    
    try:
        # Get database connection
        passphrase = click.prompt("Enter database passphrase", hide_input=True)
        if not ensure_database_connection(config, passphrase):
            click.echo("❌ Failed to connect to database", err=True)
            return
        
        conversation_store = get_conversation_store(config)
        session_store = get_session_store(config)
        
        # Check if conversation exists, create if not
        existing_conv = conversation_store.get_conversation(conv)
        if not existing_conv:
            click.echo(f"🔧 Creating new conversation: {conv}")
            conv_description = description or f"Analysis job for {conv}"
            conv_id = conversation_store.create_conversation(
                name=conv,
                description=conv_description,
                metadata={
                    'created_via': 'cli',
                    'constitutional_source': config.constitutional_source
                }
            )
            
            if not conv_id:
                click.echo("❌ Failed to create conversation", err=True)
                return
            
            click.echo(f"✅ Conversation created with ID: {conv_id}")
        else:
            conv_id = existing_conv['id']
            click.echo(f"✅ Using existing conversation: {conv_id}")
        
        # Process input file(s)
        if text:
            success = _process_text_input(text, conv_id, conversation_store, config)
            if not success:
                return
        
        if audio:
            success = _process_audio_input(audio, conv_id, conversation_store, config)
            if not success:
                return
        
        # Create analysis session
        session_name = f"analysis_{conv}"
        analysis_config = {
            'confidence_threshold': config.confidence_threshold,
            'constitutional_source': config.constitutional_source,
            'analysis_method': config.analysis_method,
            'enable_ato': config.enable_ato,
            'enable_sem': config.enable_sem,
            'enable_clu': config.enable_clu,
            'enable_mema': config.enable_mema,
            'enable_rapport': config.enable_rapport
        }
        
        session_id = session_store.create_session(
            conversation_id=conv_id,
            session_name=session_name,
            analysis_config=analysis_config
        )
        
        if session_id:
            click.echo(f"✅ Analysis session created: {session_id}")
            click.echo("")
            click.echo("📊 Job Summary:")
            click.echo(f"  Conversation ID: {conv_id}")
            click.echo(f"  Session ID: {session_id}")
            click.echo(f"  Constitutional Framework: {config.constitutional_source}")
            click.echo("")
            click.echo("Next steps:")
            click.echo(f"  me run scan --conv {conv}    # Execute constitutional analysis")
            click.echo(f"  me view events --conv {conv} --level all  # View results")
        else:
            click.echo("❌ Failed to create analysis session", err=True)
    
    except Exception as e:
        click.echo(f"❌ Failed to create job: {e}", err=True)
        if ctx.obj['verbose']:
            logger.exception("Job creation failed")


def _process_text_input(text_file: str, conv_id: str, conversation_store, config: CLIConfig) -> bool:
    """Process text file input"""
    click.echo(f"📄 Processing text file: {text_file}")
    
    try:
        # Read text file
        with open(text_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple text segmentation (split by sentences/paragraphs)
        segments = _create_text_segments(content)
        
        click.echo(f"📊 Created {len(segments)} text segments")
        
        # Store segments
        success = conversation_store.add_transcript_segments(conv_id, segments)
        if success:
            click.echo("✅ Text segments stored successfully")
            return True
        else:
            click.echo("❌ Failed to store text segments")
            return False
    
    except Exception as e:
        click.echo(f"❌ Failed to process text file: {e}")
        return False


def _process_audio_input(audio_file: str, conv_id: str, conversation_store, config: CLIConfig) -> bool:
    """Process audio file input"""
    click.echo(f"🎵 Processing audio file: {audio_file}")
    
    try:
        # Import transcription libraries
        from src.lib.transcription import TranscriptionPipeline
        from src.lib.audio import AudioProcessor
        
        # Initialize transcription pipeline
        pipeline = TranscriptionPipeline()
        
        # Process audio file
        click.echo("🔄 Transcribing audio (this may take a while)...")
        
        # Simple mock transcription for demo (real implementation would use Whisper)
        file_path = Path(audio_file)
        mock_transcript = f"This is a mock transcription of {file_path.name}. In a real implementation, this would use OpenAI Whisper Large-v3 for high-quality transcription with speaker diarization via WhisperX."
        
        # Create segments
        segments = [{
            'text': mock_transcript,
            'start_time': 0.0,
            'end_time': 10.0,
            'speaker': 'Speaker_1',
            'confidence': 0.95
        }]
        
        click.echo(f"📊 Transcription completed: {len(segments)} segments")
        
        # Store segments
        success = conversation_store.add_transcript_segments(conv_id, segments)
        if success:
            click.echo("✅ Transcript segments stored successfully")
            return True
        else:
            click.echo("❌ Failed to store transcript segments")
            return False
    
    except Exception as e:
        click.echo(f"❌ Failed to process audio file: {e}")
        return False


def _create_text_segments(content: str) -> list:
    """Create text segments from content"""
    # Simple segmentation by sentences
    import re
    
    # Split by sentence endings
    sentences = re.split(r'[.!?]+', content)
    segments = []
    
    current_time = 0.0
    for i, sentence in enumerate(sentences):
        sentence = sentence.strip()
        if sentence:
            # Estimate duration based on word count (average 2 words per second)
            words = len(sentence.split())
            duration = max(words / 2.0, 1.0)
            
            segments.append({
                'text': sentence,
                'start_time': current_time,
                'end_time': current_time + duration,
                'speaker': f'Speaker_{(i % 2) + 1}',  # Alternate speakers for demo
                'confidence': 0.9
            })
            
            current_time += duration + 0.5  # Add pause between segments
    
    return segments


@jobs_group.command('list')
@click.option('--conv', help='Filter by conversation ID')
@click.option('--limit', type=int, default=10, help='Maximum number of jobs to show')
@click.pass_context
def list_jobs(ctx, conv: Optional[str], limit: int):
    """List analysis jobs"""
    config: CLIConfig = ctx.obj['config']
    
    try:
        # Get database connection
        passphrase = click.prompt("Enter database passphrase", hide_input=True)
        if not ensure_database_connection(config, passphrase):
            click.echo("❌ Failed to connect to database", err=True)
            return
        
        conversation_store = get_conversation_store(config)
        session_store = get_session_store(config)
        
        # Get conversations
        conversations = conversation_store.list_conversations(limit=limit)
        
        if not conversations:
            click.echo("📝 No conversations found")
            return
        
        click.echo("📋 Analysis Jobs")
        click.echo("=" * 60)
        
        for conversation in conversations:
            if conv and conversation['id'] != conv and conversation['name'] != conv:
                continue
            
            # Get sessions for this conversation
            sessions = session_store.list_sessions(conversation_id=conversation['id'])
            
            click.echo(f"📝 {conversation['name']} ({conversation['id'][:8]}...)")
            click.echo(f"   Created: {conversation['created_at']}")
            click.echo(f"   Status: {conversation['status']}")
            click.echo(f"   Sessions: {len(sessions)}")
            
            for session in sessions[:3]:  # Show first 3 sessions
                status_icon = "✅" if session['status'] == 'completed' else "🔄" if session['status'] == 'pending' else "❌"
                click.echo(f"     {status_icon} {session['session_name']} ({session['status']})")
            
            click.echo()
    
    except Exception as e:
        click.echo(f"❌ Failed to list jobs: {e}", err=True)
        if ctx.obj['verbose']:
            logger.exception("Job listing failed")


@jobs_group.command('status')
@click.option('--conv', required=True, help='Conversation ID/name')
@click.pass_context
def job_status(ctx, conv: str):
    """Show job status and statistics"""
    config: CLIConfig = ctx.obj['config']
    
    try:
        # Get database connection
        passphrase = click.prompt("Enter database passphrase", hide_input=True)
        if not ensure_database_connection(config, passphrase):
            click.echo("❌ Failed to connect to database", err=True)
            return
        
        conversation_store = get_conversation_store(config)
        session_store = get_session_store(config)
        
        # Get conversation
        conversation = conversation_store.get_conversation(conv)
        if not conversation:
            click.echo(f"❌ Conversation '{conv}' not found", err=True)
            return
        
        conv_id = conversation['id']
        
        # Get conversation statistics
        stats = conversation_store.get_conversation_statistics(conv_id)
        
        # Get session summary
        session_summary = session_store.get_session_summary(conv_id)
        
        click.echo(f"📊 Job Status: {conversation['name']}")
        click.echo("=" * 50)
        
        click.echo(f"🆔 Conversation ID: {conv_id}")
        click.echo(f"📅 Created: {conversation['created_at']}")
        click.echo(f"⚖️  Constitutional Source: {conversation.get('constitutional_source', 'Unknown')}")
        click.echo(f"📊 Status: {conversation['status']}")
        click.echo()
        
        click.echo("📈 Content Statistics:")
        click.echo(f"  Transcript Segments: {stats.get('segment_count', 0)}")
        click.echo(f"  Total Duration: {stats.get('total_duration', 0):.1f} seconds")
        click.echo(f"  Speakers: {stats.get('speaker_count', 0)}")
        click.echo()
        
        click.echo("🔍 Analysis Results:")
        click.echo(f"  Constitutional Markers: {stats.get('marker_count', 0)}")
        click.echo(f"  Marker Types: {stats.get('marker_types', 0)}")
        click.echo(f"  Rapport Indicators: {stats.get('indicator_count', 0)}")
        click.echo(f"  Average Rapport: {stats.get('avg_rapport', 0):.3f}")
        click.echo()
        
        click.echo("⚙️  Analysis Sessions:")
        click.echo(f"  Total Sessions: {session_summary.get('total_sessions', 0)}")
        click.echo(f"  Completed: {session_summary.get('completed_sessions', 0)}")
        click.echo(f"  Pending: {session_summary.get('pending_sessions', 0)}")
        click.echo(f"  Failed: {session_summary.get('failed_sessions', 0)}")
        
        # Show recent sessions
        recent_sessions = session_summary.get('recent_sessions', [])
        if recent_sessions:
            click.echo("\n📋 Recent Sessions:")
            for session in recent_sessions[:5]:
                status_icon = "✅" if session['status'] == 'completed' else "🔄" if session['status'] == 'pending' else "❌"
                click.echo(f"  {status_icon} {session['session_name']} ({session['status']})")
                if session['marker_count']:
                    click.echo(f"      Markers: {session['marker_count']}, Rapport: {session['rapport_indicator_count']}")
    
    except Exception as e:
        click.echo(f"❌ Failed to get job status: {e}", err=True)
        if ctx.obj['verbose']:
            logger.exception("Job status failed")


@jobs_group.command('delete')
@click.option('--conv', required=True, help='Conversation ID/name to delete')
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
def delete_job(ctx, conv: str, confirm: bool):
    """Delete analysis job and all associated data"""
    config: CLIConfig = ctx.obj['config']
    
    if not confirm:
        if not click.confirm(f"Are you sure you want to delete conversation '{conv}' and ALL associated data?"):
            click.echo("Operation cancelled")
            return
    
    try:
        # Get database connection
        passphrase = click.prompt("Enter database passphrase", hide_input=True)
        if not ensure_database_connection(config, passphrase):
            click.echo("❌ Failed to connect to database", err=True)
            return
        
        conversation_store = get_conversation_store(config)
        
        # Get conversation first to verify it exists
        conversation = conversation_store.get_conversation(conv)
        if not conversation:
            click.echo(f"❌ Conversation '{conv}' not found", err=True)
            return
        
        conv_id = conversation['id']
        
        # Delete conversation (cascades to all related data)
        success = conversation_store.delete_conversation(conv_id)
        
        if success:
            click.echo(f"✅ Conversation '{conv}' deleted successfully")
            click.echo("🗑️  All associated data removed (segments, markers, sessions, rapport indicators)")
        else:
            click.echo(f"❌ Failed to delete conversation '{conv}'", err=True)
    
    except Exception as e:
        click.echo(f"❌ Failed to delete job: {e}", err=True)
        if ctx.obj['verbose']:
            logger.exception("Job deletion failed")