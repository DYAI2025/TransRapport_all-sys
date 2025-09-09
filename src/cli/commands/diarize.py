"""
Diarization Command Group
Speaker diarization commands for TransRapport CLI
"""

import click
import json
import logging
from pathlib import Path
from typing import Dict, Any

from src.lib.transcription.whisperx_service import WhisperXService
from ..core.config import CLIConfig
from ..core.database import ensure_database_connection, get_conversation_store

logger = logging.getLogger(__name__)


@click.group()
@click.pass_context
def diarize_group(ctx):
    """Speaker diarization operations"""
    pass


@diarize_group.command()
@click.option('--conv', required=True, help='Conversation ID/name')
@click.option('--min-speakers', default=2, type=int, help='Minimum number of speakers')
@click.option('--max-speakers', default=6, type=int, help='Maximum number of speakers')
@click.option('--min-duration', default=1.0, type=float, help='Minimum segment duration in seconds')
@click.option('--audio', help='Audio file path (uses sessions/<conv>/raw.wav if not specified)')
@click.option('--output-json', is_flag=True, help='Output results as JSON')
@click.pass_context
def diarize(ctx, conv: str, min_speakers: int, max_speakers: int, min_duration: float, audio: str, output_json: bool):
    """Perform speaker diarization on audio"""
    config: CLIConfig = ctx.obj['config']
    
    # Determine audio file path
    if not audio:
        audio = f"sessions/{conv}/raw.wav"
    
    audio_path = Path(audio)
    if not audio_path.exists():
        click.echo(f"❌ Audio file not found: {audio}", err=True)
        return
    
    try:
        # Initialize WhisperX service for diarization
        whisperx_service = WhisperXService(enable_diarization=True)
        
        if not output_json:
            click.echo(f"👥 Diarizing speakers: {conv}")
            click.echo(f"📁 Audio file: {audio}")
            click.echo(f"👤 Speaker range: {min_speakers}-{max_speakers}")
            click.echo(f"⏱️  Min duration: {min_duration}s")
            click.echo("=" * 50)
        
        # Perform diarization
        result = whisperx_service.transcribe_with_diarization(
            str(audio_path),
            min_speakers=min_speakers,
            max_speakers=max_speakers
        )
        
        # Filter segments by minimum duration
        filtered_segments = [
            seg for seg in result.segments 
            if (seg.end - seg.start) >= min_duration
        ]
        
        # Save diarization results to session directory
        session_dir = Path(f"sessions/{conv}")
        session_dir.mkdir(parents=True, exist_ok=True)
        
        diarization_file = session_dir / "diarization.json"
        diarization_data = {
            'conversation_id': conv,
            'speakers': [
                {
                    'id': speaker.id,
                    'label': speaker.label,
                    'speaking_time': speaker.speaking_time,
                    'segment_count': speaker.segment_count,
                    'average_confidence': speaker.average_confidence,
                    'voice_characteristics': speaker.voice_characteristics
                }
                for speaker in result.speakers
            ],
            'segments': [
                {
                    'id': seg.id,
                    'start': seg.start,
                    'end': seg.end,
                    'speaker': seg.speaker,
                    'text': seg.text,
                    'confidence': seg.confidence,
                    'duration': seg.end - seg.start
                }
                for seg in filtered_segments
            ],
            'diarization_info': result.diarization_info,
            'min_duration_filter': min_duration,
            'total_segments': len(result.segments),
            'filtered_segments': len(filtered_segments)
        }
        
        with open(diarization_file, 'w', encoding='utf-8') as f:
            json.dump(diarization_data, f, indent=2, ensure_ascii=False)
        
        if output_json:
            click.echo(json.dumps(diarization_data, indent=2, ensure_ascii=False))
        else:
            click.echo(f"✅ Diarization completed:")
            click.echo(f"  👥 Speakers detected: {len(result.speakers)}")
            click.echo(f"  📋 Total segments: {len(result.segments)}")
            click.echo(f"  🔽 Filtered segments: {len(filtered_segments)} (≥{min_duration}s)")
            click.echo(f"  💾 Saved to: {diarization_file}")
            click.echo()
            
            # Show speaker summary
            click.echo("👤 Speaker Summary:")
            click.echo("-" * 40)
            for speaker in result.speakers:
                click.echo(f"{speaker.id}: {speaker.speaking_time:.1f}s ({speaker.segment_count} segments)")
            
            # Show timeline preview
            click.echo()
            click.echo("📅 Timeline Preview (first 5 segments):")
            click.echo("-" * 40)
            for seg in filtered_segments[:5]:
                duration = seg.end - seg.start
                click.echo(f"[{seg.start:6.1f}-{seg.end:6.1f}s] {seg.speaker}: {seg.text[:50]}{'...' if len(seg.text) > 50 else ''}")
        
    except Exception as e:
        if output_json:
            click.echo(json.dumps({'error': str(e)}), err=True)
        else:
            click.echo(f"❌ Diarization failed: {e}", err=True)