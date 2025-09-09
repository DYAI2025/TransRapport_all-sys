"""
Audio Capture Service
Real-time audio recording with device management and format control
"""

import threading
import time
import wave
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

try:
    import pyaudio
    import numpy as np
except ImportError:
    pyaudio = None
    np = None

logger = logging.getLogger(__name__)


@dataclass
class AudioDevice:
    """Audio device information"""
    id: str
    name: str
    is_default: bool
    max_input_channels: int
    default_sample_rate: float


@dataclass
class RecordingSession:
    """Active recording session information"""
    id: str
    device_id: str
    output_file: str
    is_recording: bool
    duration: float
    sample_rate: int
    channels: int
    start_time: float


class AudioCapture:
    """
    Professional audio capture service for offline transcription
    Supports microphone and system audio recording with real-time monitoring
    """
    
    def __init__(self):
        self.pyaudio_instance = None
        self.active_sessions: Dict[str, RecordingSession] = {}
        self.device_streams: Dict[str, Any] = {}
        self._initialize_audio_system()
    
    def _initialize_audio_system(self):
        """Initialize PyAudio system"""
        if pyaudio is None:
            logger.warning("PyAudio not available - audio capture disabled")
            return
        
        try:
            self.pyaudio_instance = pyaudio.PyAudio()
            logger.info("Audio system initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize audio system: {e}")
            self.pyaudio_instance = None
    
    def get_available_devices(self) -> List[AudioDevice]:
        """Get list of available audio input devices"""
        devices = []
        
        if self.pyaudio_instance is None:
            # Return mock devices for testing
            return [
                AudioDevice(
                    id="default",
                    name="Default Audio Device",
                    is_default=True,
                    max_input_channels=2,
                    default_sample_rate=44100.0
                ),
                AudioDevice(
                    id="mic1",
                    name="Built-in Microphone",
                    is_default=False,
                    max_input_channels=1,
                    default_sample_rate=44100.0
                )
            ]
        
        try:
            default_device = self.pyaudio_instance.get_default_input_device_info()
            device_count = self.pyaudio_instance.get_device_count()
            
            for i in range(device_count):
                try:
                    info = self.pyaudio_instance.get_device_info_by_index(i)
                    if info['maxInputChannels'] > 0:  # Input device
                        devices.append(AudioDevice(
                            id=str(i),
                            name=info['name'],
                            is_default=(i == default_device['index']),
                            max_input_channels=info['maxInputChannels'],
                            default_sample_rate=info['defaultSampleRate']
                        ))
                except Exception as e:
                    logger.warning(f"Could not get info for device {i}: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to enumerate audio devices: {e}")
        
        return devices
    
    def start_recording(self, output_file: str, device_id: Optional[str] = None,
                       sample_rate: int = 16000, channels: int = 1) -> str:
        """
        Start audio recording session
        
        Args:
            output_file: Path to output WAV file
            device_id: Audio device ID (None for default)
            sample_rate: Sample rate in Hz (16kHz for Whisper)
            channels: Number of channels (1 for mono)
            
        Returns:
            Session ID for managing the recording
        """
        # Validate device availability
        if device_id and device_id in self.device_streams:
            raise RuntimeError(f"Device {device_id} already in use")
        
        # Create session
        session_id = str(uuid.uuid4())
        session = RecordingSession(
            id=session_id,
            device_id=device_id or "default",
            output_file=output_file,
            is_recording=False,
            duration=0.0,
            sample_rate=sample_rate,
            channels=channels,
            start_time=time.time()
        )
        
        # Create output directory if needed
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        if self.pyaudio_instance is None:
            # Mock recording for testing
            session.is_recording = True
            self.active_sessions[session_id] = session
            logger.info(f"Mock recording started: {session_id}")
            return session_id
        
        try:
            # Configure audio stream
            device_index = None if device_id == "default" else int(device_id)
            
            # Start recording thread
            recording_thread = threading.Thread(
                target=self._recording_worker,
                args=(session, device_index),
                daemon=True
            )
            recording_thread.start()
            
            session.is_recording = True
            self.active_sessions[session_id] = session
            self.device_streams[session.device_id] = recording_thread
            
            logger.info(f"Recording started: {session_id} -> {output_file}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            raise RuntimeError(f"Failed to start recording: {e}")
    
    def _recording_worker(self, session: RecordingSession, device_index: Optional[int]):
        """Background recording worker thread"""
        try:
            # Open audio stream
            stream = self.pyaudio_instance.open(
                format=pyaudio.paInt16,
                channels=session.channels,
                rate=session.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=1024
            )
            
            # Open output file
            with wave.open(session.output_file, 'wb') as wf:
                wf.setnchannels(session.channels)
                wf.setsampwidth(self.pyaudio_instance.get_sample_size(pyaudio.paInt16))
                wf.setframerate(session.sample_rate)
                
                # Record until stopped
                while session.is_recording:
                    try:
                        data = stream.read(1024, exception_on_overflow=False)
                        wf.writeframes(data)
                        session.duration = time.time() - session.start_time
                    except Exception as e:
                        logger.warning(f"Recording error: {e}")
                        break
            
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            logger.error(f"Recording worker failed: {e}")
            session.is_recording = False
    
    def stop_recording(self, session_id: str) -> Dict[str, Any]:
        """
        Stop recording session
        
        Args:
            session_id: Session ID from start_recording
            
        Returns:
            Recording result information
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Invalid session ID: {session_id}")
        
        session = self.active_sessions[session_id]
        session.is_recording = False
        
        # Wait for recording thread to finish
        if session.device_id in self.device_streams:
            thread = self.device_streams[session.device_id]
            if thread.is_alive():
                thread.join(timeout=2.0)
            del self.device_streams[session.device_id]
        
        # Calculate final duration
        if session.duration == 0.0:
            session.duration = time.time() - session.start_time
        
        # Verify file was created
        output_path = Path(session.output_file)
        file_exists = output_path.exists()
        file_size = output_path.stat().st_size if file_exists else 0
        
        result = {
            'success': True,
            'session_id': session_id,
            'file_path': session.output_file,
            'duration': session.duration,
            'file_exists': file_exists,
            'file_size': file_size,
            'sample_rate': session.sample_rate,
            'channels': session.channels
        }
        
        # Clean up
        del self.active_sessions[session_id]
        
        logger.info(f"Recording stopped: {session_id}, duration: {session.duration:.1f}s")
        return result
    
    def get_recording_status(self, session_id: str) -> Dict[str, Any]:
        """Get current recording status"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Invalid session ID: {session_id}")
        
        session = self.active_sessions[session_id]
        current_duration = time.time() - session.start_time if session.is_recording else session.duration
        
        return {
            'session_id': session_id,
            'is_recording': session.is_recording,
            'duration': current_duration,
            'output_file': session.output_file,
            'sample_rate': session.sample_rate,
            'channels': session.channels
        }
    
    def get_audio_info(self, audio_file: str) -> Dict[str, Any]:
        """Get audio file information"""
        try:
            with wave.open(audio_file, 'rb') as wf:
                return {
                    'sample_rate': wf.getframerate(),
                    'channels': wf.getnchannels(),
                    'format': 'WAV',
                    'frames': wf.getnframes(),
                    'duration': wf.getnframes() / wf.getframerate(),
                    'sample_width': wf.getsampwidth()
                }
        except Exception as e:
            logger.error(f"Failed to read audio file info: {e}")
            raise ValueError(f"Invalid audio file: {e}")
    
    def is_device_available(self, device_id: str) -> bool:
        """Check if device is available for recording"""
        return device_id not in self.device_streams
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active recording session IDs"""
        return list(self.active_sessions.keys())
    
    def cleanup(self):
        """Cleanup audio resources"""
        # Stop all active recordings
        active_sessions = list(self.active_sessions.keys())
        for session_id in active_sessions:
            try:
                self.stop_recording(session_id)
            except Exception as e:
                logger.warning(f"Error stopping session {session_id}: {e}")
        
        # Close PyAudio
        if self.pyaudio_instance:
            self.pyaudio_instance.terminate()
            self.pyaudio_instance = None
        
        logger.info("Audio capture cleanup completed")
    
    def __del__(self):
        """Destructor cleanup"""
        self.cleanup()