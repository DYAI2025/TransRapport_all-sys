"""
Transcription Command Group
Whisper transcription commands for TransRapport CLI
"""

import click
import json
import logging
from pathlib import Path
from typing import Dict, Any

from src.lib.transcription.whisper_service import WhisperService
from ..core.config import CLIConfig
from ..core.database import ensure_database_connection, get_conversation_store

logger = logging.getLogger(__name__)


@click.group()
@click.pass_context
def transcribe_group(ctx):
    """Transcription operations"""
    pass


@transcribe_group.command()
@click.option('--conv', required=True, help='Conversation ID/name')
@click.option('--model', default='large-v3', help='Whisper model (tiny, base, small, medium, large-v3)')
@click.option('--lang', help='Language code (auto-detect if not specified)')
@click.option('--audio', help='Audio file path (uses sessions/<conv>/raw.wav if not specified)')
@click.option('--output-json', is_flag=True, help='Output results as JSON')
@click.pass_context
def transcribe(ctx, conv: str, model: str, lang: str, audio: str, output_json: bool):
    """Transcribe audio file using Whisper"""
    config: CLIConfig = ctx.obj['config']
    
    # Determine audio file path
    if not audio:
        audio = f"sessions/{conv}/raw.wav"
    
    audio_path = Path(audio)
    if not audio_path.exists():
        click.echo(f"❌ Audio file not found: {audio}", err=True)
        return
    
    try:
        # Initialize Whisper service
        whisper_service = WhisperService(model_size=model)
        
        if not output_json:
            click.echo(f"🎙️ Transcribing: {conv}")
            click.echo(f"📁 Audio file: {audio}")
            click.echo(f"🤖 Model: {model}")
            if lang:
                click.echo(f"🌍 Language: {lang}")
            click.echo("=" * 50)
        
        # Transcribe
        result = whisper_service.transcribe(str(audio_path), language=lang)
        
        # Save transcript to session directory
        session_dir = Path(f"sessions/{conv}")
        session_dir.mkdir(parents=True, exist_ok=True)
        
        transcript_file = session_dir / "transcript.json"
        transcript_data = {
            'conversation_id': conv,
            'text': result.text,
            'language': result.language,
            'duration': result.duration,
            'segments': [
                {
                    'id': seg.id,
                    'start': seg.start,
                    'end': seg.end,
                    'text': seg.text,
                    'confidence': seg.confidence
                }
                for seg in result.segments
            ],
            'model': model,
            'audio_file': str(audio_path)
        }
        
        with open(transcript_file, 'w', encoding='utf-8') as f:
            json.dump(transcript_data, f, indent=2, ensure_ascii=False)
        
        if output_json:
            click.echo(json.dumps(transcript_data, indent=2, ensure_ascii=False))
        else:
            click.echo(f"✅ Transcription completed:")
            click.echo(f"  📝 Language: {result.language}")
            click.echo(f"  ⏱️  Duration: {result.duration:.1f} seconds") 
            click.echo(f"  📋 Segments: {len(result.segments)}")
            click.echo(f"  💾 Saved to: {transcript_file}")
            click.echo()
            click.echo("📄 Transcript:")
            click.echo("-" * 40)
            click.echo(result.text)
        
    except Exception as e:
        if output_json:
            click.echo(json.dumps({'error': str(e)}), err=True)
        else:
            click.echo(f"❌ Transcription failed: {e}", err=True)