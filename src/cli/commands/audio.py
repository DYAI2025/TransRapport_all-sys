"""
Audio Command Group
Audio capture and processing commands for TransRapport CLI
"""

import click
import logging
from pathlib import Path
from typing import Dict, Any

from src.lib.audio.capture import AudioCapture
from src.lib.transcription.whisper_service import WhisperService
from src.lib.transcription.whisperx_service import WhisperXService
from ..core.config import CLIConfig
from ..core.database import ensure_database_connection, get_conversation_store

logger = logging.getLogger(__name__)

# Global audio capture instance
_audio_capture: AudioCapture = None

def get_audio_capture():
    """Get or create audio capture instance"""
    global _audio_capture
    if _audio_capture is None:
        _audio_capture = AudioCapture()
    return _audio_capture


@click.group()
@click.pass_context
def audio_group(ctx):
    """Audio capture and processing operations"""
    pass


@audio_group.command('start')
@click.option('--conv', required=True, help='Conversation ID/name')
@click.option('--device', help='Audio device ID/name (optional)')
@click.option('--format', default='wav', help='Audio format (wav, mp3)')
@click.option('--sample-rate', default=16000, type=int, help='Sample rate (Hz)')
@click.option('--channels', default=1, type=int, help='Number of channels')
@click.pass_context
def start_recording(ctx, conv: str, device: str, format: str, sample_rate: int, channels: int):
    """Start audio recording"""
    config: CLIConfig = ctx.obj['config']
    
    # Create session directory
    session_dir = Path(f"sessions/{conv}")
    session_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = session_dir / f"raw.{format}"
    
    try:
        capture = get_audio_capture()
        
        click.echo(f"🎤 Starting recording for conversation: {conv}")
        click.echo(f"📂 Output: {output_file}")
        click.echo(f"🔧 Format: {format}, Sample Rate: {sample_rate}Hz, Channels: {channels}")
        
        if device:
            click.echo(f"🎧 Device: {device}")
        
        # Start recording
        session_id = capture.start_recording(
            str(output_file), 
            device_id=device,
            sample_rate=sample_rate,
            channels=channels
        )
        
        click.echo(f"✅ Recording started - Session ID: {session_id}")
        click.echo("Press Ctrl+C or use 'me audio stop' to end recording")
        
        # Store session info for stop command
        session_info_file = session_dir / "recording_session.txt"
        with open(session_info_file, 'w') as f:
            f.write(f"{session_id}\n{output_file}\n")
        
    except Exception as e:
        click.echo(f"❌ Failed to start recording: {e}", err=True)


@audio_group.command('stop')
@click.option('--conv', required=True, help='Conversation ID/name')
@click.option('--out', help='Output file path (overrides default)')
@click.pass_context
def stop_recording(ctx, conv: str, out: str):
    """Stop audio recording"""
    session_dir = Path(f"sessions/{conv}")
    session_info_file = session_dir / "recording_session.txt"
    
    if not session_info_file.exists():
        click.echo(f"❌ No active recording session found for conversation: {conv}", err=True)
        return
    
    try:
        # Read session info
        with open(session_info_file, 'r') as f:
            lines = f.read().strip().split('\n')
            session_id = lines[0]
            output_file = lines[1]
        
        capture = get_audio_capture()
        
        click.echo(f"🛑 Stopping recording for conversation: {conv}")
        
        # Stop recording
        result = capture.stop_recording(session_id)
        
        # Move to specified output if provided
        if out:
            output_path = Path(out)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            Path(output_file).rename(output_path)
            result['file_path'] = str(output_path)
        
        click.echo(f"✅ Recording completed:")
        click.echo(f"  📁 File: {result['file_path']}")
        click.echo(f"  ⏱️  Duration: {result['duration']:.1f} seconds")
        click.echo(f"  💾 Size: {result['file_size']} bytes")
        
        # Cleanup session file
        session_info_file.unlink()
        
    except Exception as e:
        click.echo(f"❌ Failed to stop recording: {e}", err=True)


@audio_group.command('devices')
@click.pass_context
def list_devices(ctx):
    """List available audio devices"""
    try:
        capture = get_audio_capture()
        devices = capture.get_available_devices()
        
        click.echo("🎧 Available Audio Devices:")
        click.echo("=" * 40)
        
        for device in devices:
            status = "✅ [DEFAULT]" if device.is_default else "📱"
            click.echo(f"{status} {device.name}")
            click.echo(f"    ID: {device.id}")
            click.echo(f"    Channels: {device.max_input_channels}")
            click.echo(f"    Sample Rate: {device.default_sample_rate:.0f}Hz")
            click.echo()
        
    except Exception as e:
        click.echo(f"❌ Failed to list devices: {e}", err=True)