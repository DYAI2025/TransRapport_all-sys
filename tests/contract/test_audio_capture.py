"""
Contract Tests for Audio Capture Library
CRITICAL: These tests MUST FAIL before implementation exists
"""

import pytest
import asyncio
from pathlib import Path
import tempfile
import time

# Import the audio capture library (will fail until implemented)
try:
    from src.lib.audio.capture import AudioCapture
    from src.lib.audio.monitor import AudioMonitor
except ImportError:
    pytest.skip("Audio capture library not implemented yet", allow_module_level=True)


class TestAudioCaptureContract:
    """Contract tests for AudioCapture service"""
    
    @pytest.fixture
    def audio_capture(self):
        """Initialize AudioCapture instance"""
        return AudioCapture()
    
    @pytest.fixture
    def temp_output_file(self):
        """Create temporary output file for recordings"""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            yield Path(f.name)
        Path(f.name).unlink(missing_ok=True)
    
    def test_start_recording_returns_session_id(self, audio_capture, temp_output_file):
        """MUST return unique session ID when starting recording"""
        session_id = audio_capture.start_recording(
            output_file=str(temp_output_file),
            device_id=None  # Use default device
        )
        
        assert isinstance(session_id, str)
        assert len(session_id) > 0
        assert session_id != ""
    
    def test_start_recording_with_specific_device(self, audio_capture, temp_output_file):
        """MUST accept specific audio device ID"""
        # This will fail until device enumeration is implemented
        devices = audio_capture.get_available_devices()
        assert len(devices) > 0
        
        device_id = devices[0]['id']
        session_id = audio_capture.start_recording(
            output_file=str(temp_output_file),
            device_id=device_id
        )
        
        assert isinstance(session_id, str)
    
    def test_stop_recording_requires_valid_session(self, audio_capture, temp_output_file):
        """MUST require valid session ID to stop recording"""
        # Start recording first
        session_id = audio_capture.start_recording(
            output_file=str(temp_output_file)
        )
        
        # Stop with valid session should succeed
        result = audio_capture.stop_recording(session_id)
        assert result['success'] is True
        assert result['file_path'] == str(temp_output_file)
        assert result['duration'] > 0
        
        # Stop with invalid session should fail
        with pytest.raises(ValueError, match="Invalid session"):
            audio_capture.stop_recording("invalid-session-id")
    
    def test_recording_creates_valid_audio_file(self, audio_capture, temp_output_file):
        """MUST create valid WAV file with correct format"""
        session_id = audio_capture.start_recording(
            output_file=str(temp_output_file),
            sample_rate=16000,  # Whisper requirement
            channels=1  # Mono
        )
        
        # Record for 1 second
        time.sleep(1)
        
        result = audio_capture.stop_recording(session_id)
        
        # File must exist and be valid
        assert temp_output_file.exists()
        assert temp_output_file.stat().st_size > 0
        
        # Must have correct audio properties
        audio_info = audio_capture.get_audio_info(str(temp_output_file))
        assert audio_info['sample_rate'] == 16000
        assert audio_info['channels'] == 1
        assert audio_info['format'] == 'WAV'
        assert audio_info['duration'] >= 0.9  # At least 900ms recorded
    
    def test_concurrent_recordings_not_allowed(self, audio_capture, temp_output_file):
        """MUST prevent multiple simultaneous recordings from same device"""
        session_id1 = audio_capture.start_recording(
            output_file=str(temp_output_file)
        )
        
        # Second recording on same device should fail
        with pytest.raises(RuntimeError, match="Device already in use"):
            audio_capture.start_recording(
                output_file=str(temp_output_file).replace('.wav', '2.wav')
            )
        
        # Clean up
        audio_capture.stop_recording(session_id1)
    
    def test_get_recording_status(self, audio_capture, temp_output_file):
        """MUST provide real-time recording status"""
        session_id = audio_capture.start_recording(
            output_file=str(temp_output_file)
        )
        
        status = audio_capture.get_recording_status(session_id)
        assert status['is_recording'] is True
        assert status['duration'] >= 0
        assert status['session_id'] == session_id
        
        audio_capture.stop_recording(session_id)
        
        status = audio_capture.get_recording_status(session_id)
        assert status['is_recording'] is False


class TestAudioMonitorContract:
    """Contract tests for real-time audio monitoring"""
    
    @pytest.fixture
    def audio_monitor(self):
        """Initialize AudioMonitor instance"""
        return AudioMonitor()
    
    def test_real_time_level_monitoring(self, audio_monitor):
        """MUST provide real-time audio level monitoring"""
        # Start monitoring
        session_id = audio_monitor.start_monitoring()
        
        # Get level readings
        levels = []
        for _ in range(5):
            level = audio_monitor.get_current_level()
            levels.append(level)
            time.sleep(0.1)
        
        # Levels must be in valid range
        for level in levels:
            assert 0.0 <= level <= 1.0
        
        audio_monitor.stop_monitoring(session_id)
    
    def test_voice_activity_detection(self, audio_monitor):
        """MUST detect voice activity in real-time"""
        session_id = audio_monitor.start_monitoring(
            enable_vad=True,
            vad_threshold=0.5
        )
        
        # Get VAD status
        vad_status = audio_monitor.get_voice_activity()
        assert 'is_speaking' in vad_status
        assert 'confidence' in vad_status
        assert isinstance(vad_status['is_speaking'], bool)
        assert 0.0 <= vad_status['confidence'] <= 1.0
        
        audio_monitor.stop_monitoring(session_id)


if __name__ == "__main__":
    # Run these tests to verify they FAIL before implementation
    pytest.main([__file__, "-v", "--tb=short"])