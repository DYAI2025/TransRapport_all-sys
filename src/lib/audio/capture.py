"""
TransRapport Audio Capture System
Cross-platform audio recording with system audio support
"""

import logging
import platform
import threading
import time
import wave
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import queue

logger = logging.getLogger(__name__)

@dataclass
class AudioDevice:
    """Audio device information"""
    id: str
    name: str
    is_default: bool
    max_input_channels: int
    default_sample_rate: float
    is_system_audio: bool = False

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
    is_system_audio: bool = False

class AudioCaptureError(Exception):
    """Base exception for audio capture errors"""
    pass

class AudioCaptureBase:
    """Abstract base class for platform-specific audio capture"""

    def __init__(self):
        self.pyaudio_instance = None
        self.active_sessions: Dict[str, RecordingSession] = {}
        self.device_streams: Dict[str, Any] = {}
        self.audio_queue = queue.Queue()

    def get_available_devices(self) -> List[AudioDevice]:
        """Get list of available audio input devices"""
        raise NotImplementedError

    def start_recording(self, output_file: str, device_id: Optional[str] = None,
                       sample_rate: int = 16000, channels: int = 1,
                       system_audio: bool = False) -> str:
        """Start audio recording session"""
        raise NotImplementedError

    def stop_recording(self, session_id: str) -> Dict[str, Any]:
        """Stop recording session"""
        raise NotImplementedError

    def get_recording_status(self, session_id: str) -> Dict[str, Any]:
        """Get current recording status"""
        raise NotImplementedError

    def is_device_available(self, device_id: str) -> bool:
        """Check if device is available for recording"""
        devices = self.get_available_devices()
        return any(device.id == device_id for device in devices)

    def cleanup(self):
        """Cleanup audio resources"""
        raise NotImplementedError

class WindowsAudioCapture(AudioCaptureBase):
    """Windows audio capture using PyAudio and system audio support"""

    def __init__(self):
        super().__init__()
        self._initialize_audio_system()

    def _initialize_audio_system(self):
        """Initialize PyAudio system for Windows"""
        try:
            import pyaudio  # type: ignore
            self.pyaudio_instance = pyaudio.PyAudio()
            logger.info("Windows audio system initialized successfully")
        except ImportError:
            raise AudioCaptureError("PyAudio not available. Install with: pip install pyaudio")
        except Exception as e:
            raise AudioCaptureError(f"Failed to initialize Windows audio system: {e}")

    def get_available_devices(self) -> List[AudioDevice]:
        """Get Windows audio devices"""
        devices = []

        try:
            import pyaudio  # type: ignore
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
                            default_sample_rate=info['defaultSampleRate'],
                            is_system_audio=False
                        ))
                except Exception as e:
                    logger.warning(f"Could not get info for Windows device {i}: {e}")

            # Add system audio device if available
            try:
                # Try to detect stereo mix or similar system audio device
                for device in devices:
                    if 'stereo mix' in device.name.lower() or 'what u hear' in device.name.lower():
                        device.is_system_audio = True
                        break
            except Exception:
                pass

        except Exception as e:
            logger.error(f"Failed to enumerate Windows audio devices: {e}")

        return devices

    def start_recording(self, output_file: str, device_id: Optional[str] = None,
                       sample_rate: int = 16000, channels: int = 1,
                       system_audio: bool = False) -> str:
        """Start Windows recording"""
        if device_id and device_id in self.device_streams:
            raise AudioCaptureError(f"Device {device_id} already in use")

        session_id = str(uuid.uuid4())
        session = RecordingSession(
            id=session_id,
            device_id=device_id or "default",
            output_file=output_file,
            is_recording=False,
            duration=0.0,
            sample_rate=sample_rate,
            channels=channels,
            start_time=time.time(),
            is_system_audio=system_audio
        )

        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        try:
            import pyaudio  # type: ignore
            device_index = None if device_id == "default" else int(device_id)

            recording_thread = threading.Thread(
                target=self._recording_worker,
                args=(session, device_index),
                daemon=True
            )
            recording_thread.start()

            session.is_recording = True
            self.active_sessions[session_id] = session
            self.device_streams[session.device_id] = recording_thread

            logger.info(f"Windows recording started: {session_id} -> {output_file}")
            return session_id

        except Exception as e:
            logger.error(f"Failed to start Windows recording: {e}")
            raise AudioCaptureError(f"Failed to start Windows recording: {e}")

    def _recording_worker(self, session: RecordingSession, device_index: Optional[int]):
        """Windows recording worker thread"""
        try:
            import pyaudio  # type: ignore
            stream = self.pyaudio_instance.open(
                format=pyaudio.paInt16,
                channels=session.channels,
                rate=session.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=1024
            )

            with wave.open(session.output_file, 'wb') as wf:
                wf.setnchannels(session.channels)
                wf.setsampwidth(self.pyaudio_instance.get_sample_size(pyaudio.paInt16))
                wf.setframerate(session.sample_rate)

                while session.is_recording:
                    try:
                        data = stream.read(1024, exception_on_overflow=False)
                        wf.writeframes(data)
                        session.duration = time.time() - session.start_time
                    except Exception as e:
                        logger.warning(f"Windows recording error: {e}")
                        break

            stream.stop_stream()
            stream.close()

        except Exception as e:
            logger.error(f"Windows recording worker failed: {e}")
            session.is_recording = False

    def stop_recording(self, session_id: str) -> Dict[str, Any]:
        """Stop Windows recording"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Invalid session ID: {session_id}")

        session = self.active_sessions[session_id]
        session.is_recording = False

        if session.device_id in self.device_streams:
            thread = self.device_streams[session.device_id]
            if thread.is_alive():
                thread.join(timeout=2.0)
            del self.device_streams[session.device_id]

        if session.duration < 0.001:  # Use small epsilon instead of == 0.0
            session.duration = time.time() - session.start_time

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
            'channels': session.channels,
            'system_audio': session.is_system_audio
        }

        del self.active_sessions[session_id]
        logger.info(f"Windows recording stopped: {session_id}, duration: {session.duration:.1f}s")
        return result

    def get_recording_status(self, session_id: str) -> Dict[str, Any]:
        """Get Windows recording status"""
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
            'channels': session.channels,
            'system_audio': session.is_system_audio
        }

    def cleanup(self):
        """Cleanup Windows audio resources"""
        active_sessions = list(self.active_sessions.keys())
        for session_id in active_sessions:
            try:
                self.stop_recording(session_id)
            except Exception as e:
                logger.warning(f"Error stopping Windows session {session_id}: {e}")

        if self.pyaudio_instance:
            self.pyaudio_instance.terminate()
            self.pyaudio_instance = None

        logger.info("Windows audio capture cleanup completed")

class LinuxAudioCapture(AudioCaptureBase):
    """Linux audio capture using sounddevice"""

    def __init__(self):
        super().__init__()
        self._initialize_audio_system()

    def _initialize_audio_system(self):
        """Initialize sounddevice for Linux"""
        try:
            import sounddevice as sd  # type: ignore
            logger.info("Linux audio system initialized successfully")
        except ImportError:
            raise AudioCaptureError("sounddevice not available. Install with: pip install sounddevice")

    def get_available_devices(self) -> List[AudioDevice]:
        """Get Linux audio devices"""
        devices = []

        try:
            import sounddevice as sd  # type: ignore
            device_list = sd.query_devices()
            default_device = sd.default.device[0]  # Input device

            for i, device in enumerate(device_list):
                if device.get('max_input_channels', 0) > 0:
                    devices.append(AudioDevice(
                        id=str(i),
                        name=device.get('name', f'Device {i}'),
                        is_default=(i == default_device),
                        max_input_channels=device.get('max_input_channels', 0),
                        default_sample_rate=device.get('default_samplerate', 44100.0),
                        is_system_audio=False
                    ))

            # Add PulseAudio monitor for system audio
            try:
                # Look for monitor devices (system audio)
                for device in devices:
                    if 'monitor' in device.name.lower() or 'pulse' in device.name.lower():
                        device.is_system_audio = True
                        break
            except Exception:
                pass

        except Exception as e:
            logger.error(f"Failed to enumerate Linux audio devices: {e}")

        return devices

    def start_recording(self, output_file: str, device_id: Optional[str] = None,
                       sample_rate: int = 16000, channels: int = 1,
                       system_audio: bool = False) -> str:
        """Start Linux recording"""
        if device_id and device_id in self.device_streams:
            raise AudioCaptureError(f"Device {device_id} already in use")

        session_id = str(uuid.uuid4())
        session = RecordingSession(
            id=session_id,
            device_id=device_id or "default",
            output_file=output_file,
            is_recording=False,
            duration=0.0,
            sample_rate=sample_rate,
            channels=channels,
            start_time=time.time(),
            is_system_audio=system_audio
        )

        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        try:
            import sounddevice as sd  # type: ignore
            import numpy as np  # type: ignore
            device_index = None if device_id == "default" else int(device_id)

            recording_thread = threading.Thread(
                target=self._linux_recording_worker,
                args=(session, device_index),
                daemon=True
            )
            recording_thread.start()

            session.is_recording = True
            self.active_sessions[session_id] = session
            self.device_streams[session.device_id] = recording_thread

            logger.info(f"Linux recording started: {session_id} -> {output_file}")
            return session_id

        except Exception as e:
            logger.error(f"Failed to start Linux recording: {e}")
            raise AudioCaptureError(f"Failed to start Linux recording: {e}")

    def _linux_recording_worker(self, session: RecordingSession, device_index: Optional[int]):
        """Linux recording worker thread"""
        try:
            import sounddevice as sd  # type: ignore
            import numpy as np  # type: ignore
            audio_data = []

            def callback(indata, frames, time, status):
                if session.is_recording:
                    audio_data.append(indata.copy())

            stream = sd.InputStream(
                device=device_index,
                channels=session.channels,
                samplerate=session.sample_rate,
                callback=callback
            )

            stream.start()

            # Record until stopped
            while session.is_recording:
                time.sleep(0.1)
                session.duration = time.time() - session.start_time

            stream.stop()
            stream.close()

            # Save to WAV file
            if audio_data:
                audio_array = np.concatenate(audio_data, axis=0)
                audio_array = (audio_array * 32767).astype(np.int16)

                with wave.open(session.output_file, 'wb') as wf:
                    wf.setnchannels(session.channels)
                    wf.setsampwidth(2)  # 16-bit
                    wf.setframerate(session.sample_rate)
                    wf.writeframes(audio_array.tobytes())

        except Exception as e:
            logger.error(f"Linux recording worker failed: {e}")
            session.is_recording = False

    def stop_recording(self, session_id: str) -> Dict[str, Any]:
        """Stop Linux recording"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Invalid session ID: {session_id}")

        session = self.active_sessions[session_id]
        session.is_recording = False

        if session.device_id in self.device_streams:
            thread = self.device_streams[session.device_id]
            if thread.is_alive():
                thread.join(timeout=2.0)
            del self.device_streams[session.device_id]

        if session.duration < 0.001:  # Use small epsilon instead of == 0.0
            session.duration = time.time() - session.start_time

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
            'channels': session.channels,
            'system_audio': session.is_system_audio
        }

        del self.active_sessions[session_id]
        logger.info(f"Linux recording stopped: {session_id}, duration: {session.duration:.1f}s")
        return result

    def get_recording_status(self, session_id: str) -> Dict[str, Any]:
        """Get Linux recording status"""
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
            'channels': session.channels,
            'system_audio': session.is_system_audio
        }

    def cleanup(self):
        """Cleanup Linux audio resources"""
        active_sessions = list(self.active_sessions.keys())
        for session_id in active_sessions:
            try:
                self.stop_recording(session_id)
            except Exception as e:
                logger.warning(f"Error stopping Linux session {session_id}: {e}")

        logger.info("Linux audio capture cleanup completed")

class MacOSAudioCapture(AudioCaptureBase):
    """macOS audio capture using sounddevice"""

    def __init__(self):
        super().__init__()
        self._initialize_audio_system()

    def _initialize_audio_system(self):
        """Initialize sounddevice for macOS"""
        try:
            import sounddevice as sd  # type: ignore
            logger.info("macOS audio system initialized successfully")
        except ImportError:
            raise AudioCaptureError("sounddevice not available. Install with: pip install sounddevice")

    def get_available_devices(self) -> List[AudioDevice]:
        """Get macOS audio devices"""
        devices = []

        try:
            import sounddevice as sd  # type: ignore
            device_list = sd.query_devices()
            default_device = sd.default.device[0]  # Input device

            for i, device in enumerate(device_list):
                if device.get('max_input_channels', 0) > 0:
                    devices.append(AudioDevice(
                        id=str(i),
                        name=device.get('name', f'Device {i}'),
                        is_default=(i == default_device),
                        max_input_channels=device.get('max_input_channels', 0),
                        default_sample_rate=device.get('default_samplerate', 44100.0),
                        is_system_audio=False
                    ))

            # Add BlackHole or Soundflower for system audio
            try:
                for device in devices:
                    if any(name in device.name.lower() for name in ['blackhole', 'soundflower', 'loopback']):
                        device.is_system_audio = True
                        break
            except Exception:
                pass

        except Exception as e:
            logger.error(f"Failed to enumerate macOS audio devices: {e}")

        return devices

    def start_recording(self, output_file: str, device_id: Optional[str] = None,
                       sample_rate: int = 16000, channels: int = 1,
                       system_audio: bool = False) -> str:
        """Start macOS recording"""
        if device_id and device_id in self.device_streams:
            raise AudioCaptureError(f"Device {device_id} already in use")

        session_id = str(uuid.uuid4())
        session = RecordingSession(
            id=session_id,
            device_id=device_id or "default",
            output_file=output_file,
            is_recording=False,
            duration=0.0,
            sample_rate=sample_rate,
            channels=channels,
            start_time=time.time(),
            is_system_audio=system_audio
        )

        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        try:
            import sounddevice as sd  # type: ignore
            import numpy as np  # type: ignore
            device_index = None if device_id == "default" else int(device_id)

            recording_thread = threading.Thread(
                target=self._macos_recording_worker,
                args=(session, device_index),
                daemon=True
            )
            recording_thread.start()

            session.is_recording = True
            self.active_sessions[session_id] = session
            self.device_streams[session.device_id] = recording_thread

            logger.info(f"macOS recording started: {session_id} -> {output_file}")
            return session_id

        except Exception as e:
            logger.error(f"Failed to start macOS recording: {e}")
            raise AudioCaptureError(f"Failed to start macOS recording: {e}")

    def _macos_recording_worker(self, session: RecordingSession, device_index: Optional[int]):
        """macOS recording worker thread"""
        try:
            import sounddevice as sd  # type: ignore
            import numpy as np  # type: ignore
            audio_data = []

            def callback(indata, frames, time, status):
                if session.is_recording:
                    audio_data.append(indata.copy())

            stream = sd.InputStream(
                device=device_index,
                channels=session.channels,
                samplerate=session.sample_rate,
                callback=callback
            )

            stream.start()

            while session.is_recording:
                time.sleep(0.1)
                session.duration = time.time() - session.start_time

            stream.stop()
            stream.close()

            if audio_data:
                audio_array = np.concatenate(audio_data, axis=0)
                audio_array = (audio_array * 32767).astype(np.int16)

                with wave.open(session.output_file, 'wb') as wf:
                    wf.setnchannels(session.channels)
                    wf.setsampwidth(2)  # 16-bit
                    wf.setframerate(session.sample_rate)
                    wf.writeframes(audio_array.tobytes())

        except Exception as e:
            logger.error(f"macOS recording worker failed: {e}")
            session.is_recording = False

    def stop_recording(self, session_id: str) -> Dict[str, Any]:
        """Stop macOS recording"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Invalid session ID: {session_id}")

        session = self.active_sessions[session_id]
        session.is_recording = False

        if session.device_id in self.device_streams:
            thread = self.device_streams[session.device_id]
            if thread.is_alive():
                thread.join(timeout=2.0)
            del self.device_streams[session.device_id]

        if session.duration < 0.001:  # Use small epsilon instead of == 0.0
            session.duration = time.time() - session.start_time

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
            'channels': session.channels,
            'system_audio': session.is_system_audio
        }

        del self.active_sessions[session_id]
        logger.info(f"macOS recording stopped: {session_id}, duration: {session.duration:.1f}s")
        return result

    def get_recording_status(self, session_id: str) -> Dict[str, Any]:
        """Get macOS recording status"""
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
            'channels': session.channels,
            'system_audio': session.is_system_audio
        }

    def cleanup(self):
        """Cleanup macOS audio resources"""
        active_sessions = list(self.active_sessions.keys())
        for session_id in active_sessions:
            try:
                self.stop_recording(session_id)
            except Exception as e:
                logger.warning(f"Error stopping macOS session {session_id}: {e}")

        logger.info("macOS audio capture cleanup completed")

class AudioCapture:
    """
    Cross-platform audio capture service for TransRapport
    Supports microphone and system audio recording with real-time monitoring
    """

    def __init__(self):
        self.platform_capture = None
        self._initialize_platform_capture()

    def _initialize_platform_capture(self):
        """Initialize platform-specific audio capture"""
        system = platform.system().lower()

        try:
            if system == "windows":
                self.platform_capture = WindowsAudioCapture()
            elif system == "linux":
                self.platform_capture = LinuxAudioCapture()
            elif system == "darwin":  # macOS
                self.platform_capture = MacOSAudioCapture()
            else:
                raise AudioCaptureError(f"Unsupported platform: {system}")

            logger.info(f"Audio capture initialized for {system}")

        except AudioCaptureError:
            raise  # Re-raise AudioCaptureError
        except Exception as e:
            raise AudioCaptureError(f"Failed to initialize audio capture: {e}")

    def get_available_devices(self) -> List[AudioDevice]:
        """Get list of available audio input devices"""
        return self.platform_capture.get_available_devices()

    def start_recording(self, output_file: str, device_id: Optional[str] = None,
                       sample_rate: int = 16000, channels: int = 1,
                       system_audio: bool = False) -> str:
        """
        Start audio recording session

        Args:
            output_file: Path to output WAV file
            device_id: Audio device ID (None for default)
            sample_rate: Sample rate in Hz (16kHz for Whisper)
            channels: Number of channels (1 for mono)
            system_audio: Whether to record system audio instead of microphone

        Returns:
            Session ID for managing the recording
        """
        return self.platform_capture.start_recording(
            output_file, device_id, sample_rate, channels, system_audio
        )

    def stop_recording(self, session_id: str) -> Dict[str, Any]:
        """Stop recording session"""
        return self.platform_capture.stop_recording(session_id)

    def get_recording_status(self, session_id: str) -> Dict[str, Any]:
        """Get current recording status"""
        return self.platform_capture.get_recording_status(session_id)

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
        return self.platform_capture.is_device_available(device_id)

    def get_active_sessions(self) -> List[str]:
        """Get list of active recording session IDs"""
        return list(self.platform_capture.active_sessions.keys())

    def cleanup(self):
        """Cleanup audio resources"""
        if self.platform_capture:
            self.platform_capture.cleanup()

    def __del__(self):
        """Destructor cleanup"""
        self.cleanup()

# Utility functions
def test_audio_capture():
    """Test audio capture functionality"""
    print("Testing audio capture...")

    try:
        capture = AudioCapture()

        # Test device listing
        devices = capture.get_available_devices()
        print(f"Found {len(devices)} audio devices:")
        for device in devices:
            print(f"  {device.id}: {device.name} (default: {device.is_default}, system: {device.is_system_audio})")

        print("Audio capture test completed successfully")

    except AudioCaptureError as e:
        print(f"Audio capture test failed: {e}")
    except Exception as e:
        print(f"Unexpected error during test: {e}")

if __name__ == "__main__":
    test_audio_capture()