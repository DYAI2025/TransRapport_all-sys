"""
Audio Monitoring Service  
Real-time audio level monitoring and voice activity detection
"""

import threading
import time
import uuid
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from collections import deque

try:
    import pyaudio
    import numpy as np
    import webrtcvad
except ImportError:
    pyaudio = None
    np = None
    webrtcvad = None

logger = logging.getLogger(__name__)


@dataclass
class AudioLevel:
    """Audio level measurement"""
    timestamp: float
    rms_level: float      # Root Mean Square level (0.0 - 1.0)
    peak_level: float     # Peak level (0.0 - 1.0)
    db_level: float       # Decibel level
    is_clipping: bool     # True if clipping detected


@dataclass
class VoiceActivity:
    """Voice activity detection result"""
    timestamp: float
    is_speaking: bool
    confidence: float     # VAD confidence (0.0 - 1.0)
    speech_probability: float


class AudioMonitor:
    """
    Real-time audio monitoring with level detection and VAD
    Provides continuous monitoring of audio input for recording feedback
    """
    
    def __init__(self, buffer_size: int = 1024):
        self.pyaudio_instance = None
        self.buffer_size = buffer_size
        self.monitoring_sessions: Dict[str, Dict[str, Any]] = {}
        self.vad = None
        self._initialize_audio_system()
        self._initialize_vad()
    
    def _initialize_audio_system(self):
        """Initialize PyAudio for monitoring"""
        if pyaudio is None:
            logger.warning("PyAudio not available - audio monitoring disabled")
            return
        
        try:
            self.pyaudio_instance = pyaudio.PyAudio()
            logger.info("Audio monitoring system initialized")
        except Exception as e:
            logger.error(f"Failed to initialize audio monitoring: {e}")
            self.pyaudio_instance = None
    
    def _initialize_vad(self):
        """Initialize Voice Activity Detection"""
        if webrtcvad is None:
            logger.warning("webrtcvad not available - VAD disabled")
            return
        
        try:
            self.vad = webrtcvad.Vad(2)  # Aggressiveness level 0-3
            logger.info("Voice Activity Detection initialized")
        except Exception as e:
            logger.error(f"Failed to initialize VAD: {e}")
            self.vad = None
    
    def start_monitoring(self, device_id: Optional[str] = None, 
                        sample_rate: int = 16000, enable_vad: bool = False,
                        vad_threshold: float = 0.5) -> str:
        """
        Start real-time audio monitoring
        
        Args:
            device_id: Audio device ID (None for default)
            sample_rate: Sample rate for monitoring
            enable_vad: Enable voice activity detection
            vad_threshold: VAD sensitivity threshold
            
        Returns:
            Monitoring session ID
        """
        session_id = str(uuid.uuid4())
        
        # Create monitoring session
        session = {
            'id': session_id,
            'device_id': device_id or 'default',
            'sample_rate': sample_rate,
            'enable_vad': enable_vad,
            'vad_threshold': vad_threshold,
            'is_active': False,
            'stream': None,
            'thread': None,
            'current_level': AudioLevel(0.0, 0.0, 0.0, -60.0, False),
            'current_vad': VoiceActivity(0.0, False, 0.0, 0.0),
            'level_history': deque(maxlen=100),
            'vad_history': deque(maxlen=50),
            'callbacks': []
        }
        
        if self.pyaudio_instance is None:
            # Mock monitoring for testing
            session['is_active'] = True
            self.monitoring_sessions[session_id] = session
            logger.info(f"Mock monitoring started: {session_id}")
            return session_id
        
        try:
            # Start monitoring thread
            monitoring_thread = threading.Thread(
                target=self._monitoring_worker,
                args=(session,),
                daemon=True
            )
            
            session['thread'] = monitoring_thread
            session['is_active'] = True
            self.monitoring_sessions[session_id] = session
            
            monitoring_thread.start()
            
            logger.info(f"Audio monitoring started: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            raise RuntimeError(f"Failed to start monitoring: {e}")
    
    def _monitoring_worker(self, session: Dict[str, Any]):
        """Background monitoring worker thread"""
        try:
            device_index = None if session['device_id'] == 'default' else int(session['device_id'])
            
            # Open monitoring stream
            stream = self.pyaudio_instance.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=session['sample_rate'],
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.buffer_size
            )
            
            session['stream'] = stream
            
            while session['is_active']:
                try:
                    # Read audio data
                    data = stream.read(self.buffer_size, exception_on_overflow=False)
                    audio_array = np.frombuffer(data, dtype=np.int16)
                    
                    # Calculate audio levels
                    level = self._calculate_audio_level(audio_array)
                    session['current_level'] = level
                    session['level_history'].append(level)
                    
                    # Voice activity detection
                    if session['enable_vad'] and self.vad:
                        vad_result = self._detect_voice_activity(
                            data, session['sample_rate'], session['vad_threshold']
                        )
                        session['current_vad'] = vad_result
                        session['vad_history'].append(vad_result)
                    
                    # Call registered callbacks
                    for callback in session['callbacks']:
                        try:
                            callback(level, session.get('current_vad'))
                        except Exception as e:
                            logger.warning(f"Monitor callback error: {e}")
                    
                except Exception as e:
                    logger.warning(f"Monitoring error: {e}")
                    time.sleep(0.01)  # Brief pause before retry
                    
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            logger.error(f"Monitoring worker failed: {e}")
            session['is_active'] = False
    
    def _calculate_audio_level(self, audio_array: Any) -> AudioLevel:
        """Calculate audio level metrics from audio data"""
        timestamp = time.time()
        
        if np is None or len(audio_array) == 0:
            return AudioLevel(timestamp, 0.0, 0.0, -60.0, False)
        
        # Normalize to float
        audio_float = audio_array.astype(np.float32) / 32768.0
        
        # Calculate RMS level
        rms = np.sqrt(np.mean(audio_float**2))
        
        # Calculate peak level
        peak = np.max(np.abs(audio_float))
        
        # Convert to decibels
        db_level = 20 * np.log10(max(rms, 1e-10))  # Avoid log(0)
        
        # Detect clipping
        is_clipping = peak > 0.95
        
        return AudioLevel(
            timestamp=timestamp,
            rms_level=float(rms),
            peak_level=float(peak),
            db_level=float(db_level),
            is_clipping=is_clipping
        )
    
    def _detect_voice_activity(self, audio_data: bytes, sample_rate: int, 
                              threshold: float) -> VoiceActivity:
        """Detect voice activity in audio data"""
        timestamp = time.time()
        
        if self.vad is None:
            return VoiceActivity(timestamp, False, 0.0, 0.0)
        
        try:
            # WebRTC VAD requires specific sample rates and frame sizes
            if sample_rate not in [8000, 16000, 32000, 48000]:
                # Use simple energy-based detection as fallback
                return self._simple_voice_detection(audio_data, threshold, timestamp)
            
            # Ensure frame is correct size for VAD (10, 20, or 30ms)
            frame_duration = 20  # ms
            frame_size = int(sample_rate * frame_duration / 1000)
            
            if len(audio_data) < frame_size * 2:  # 2 bytes per sample
                return VoiceActivity(timestamp, False, 0.0, 0.0)
            
            # Take first complete frame
            frame_data = audio_data[:frame_size * 2]
            
            # VAD detection
            is_speech = self.vad.is_speech(frame_data, sample_rate)
            confidence = 0.8 if is_speech else 0.2  # WebRTC VAD doesn't provide confidence
            
            return VoiceActivity(
                timestamp=timestamp,
                is_speaking=is_speech,
                confidence=confidence,
                speech_probability=confidence
            )
            
        except Exception as e:
            logger.warning(f"VAD error: {e}")
            return self._simple_voice_detection(audio_data, threshold, timestamp)
    
    def _simple_voice_detection(self, audio_data: bytes, threshold: float, 
                               timestamp: float) -> VoiceActivity:
        """Simple energy-based voice detection fallback"""
        if np is None:
            return VoiceActivity(timestamp, False, 0.0, 0.0)
        
        try:
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            audio_float = audio_array.astype(np.float32) / 32768.0
            
            # Energy-based detection
            energy = np.mean(audio_float**2)
            is_speaking = energy > threshold
            confidence = min(energy / threshold, 1.0) if is_speaking else 0.0
            
            return VoiceActivity(
                timestamp=timestamp,
                is_speaking=is_speaking,
                confidence=confidence,
                speech_probability=energy
            )
            
        except Exception as e:
            logger.warning(f"Simple VAD error: {e}")
            return VoiceActivity(timestamp, False, 0.0, 0.0)
    
    def get_current_level(self, session_id: Optional[str] = None) -> float:
        """Get current audio level (0.0 - 1.0)"""
        if not self.monitoring_sessions:
            return 0.0
        
        if session_id is None:
            # Get from any active session
            session_id = next(iter(self.monitoring_sessions.keys()))
        
        if session_id not in self.monitoring_sessions:
            return 0.0
        
        session = self.monitoring_sessions[session_id]
        return session['current_level'].rms_level
    
    def get_voice_activity(self, session_id: Optional[str] = None) -> VoiceActivity:
        """Get current voice activity detection result"""
        if not self.monitoring_sessions:
            return VoiceActivity(time.time(), False, 0.0, 0.0)
        
        if session_id is None:
            session_id = next(iter(self.monitoring_sessions.keys()))
        
        if session_id not in self.monitoring_sessions:
            return VoiceActivity(time.time(), False, 0.0, 0.0)
        
        session = self.monitoring_sessions[session_id]
        return session['current_vad']
    
    def get_level_history(self, session_id: str, count: int = 50) -> List[AudioLevel]:
        """Get recent audio level history"""
        if session_id not in self.monitoring_sessions:
            return []
        
        session = self.monitoring_sessions[session_id]
        history = list(session['level_history'])
        return history[-count:] if count > 0 else history
    
    def add_level_callback(self, session_id: str, 
                          callback: Callable[[AudioLevel, Optional[VoiceActivity]], None]):
        """Add callback for real-time level updates"""
        if session_id in self.monitoring_sessions:
            self.monitoring_sessions[session_id]['callbacks'].append(callback)
    
    def get_monitoring_stats(self, session_id: str) -> Dict[str, Any]:
        """Get monitoring session statistics"""
        if session_id not in self.monitoring_sessions:
            raise ValueError(f"Invalid session ID: {session_id}")
        
        session = self.monitoring_sessions[session_id]
        history = session['level_history']
        
        if not history:
            return {
                'session_id': session_id,
                'is_active': session['is_active'],
                'sample_count': 0,
                'average_level': 0.0,
                'peak_level': 0.0,
                'clipping_events': 0
            }
        
        levels = [level.rms_level for level in history]
        peaks = [level.peak_level for level in history]
        clipping_count = sum(1 for level in history if level.is_clipping)
        
        return {
            'session_id': session_id,
            'is_active': session['is_active'],
            'sample_count': len(history),
            'average_level': sum(levels) / len(levels),
            'peak_level': max(peaks),
            'min_level': min(levels),
            'clipping_events': clipping_count,
            'current_level': session['current_level'].rms_level,
            'vad_enabled': session['enable_vad'],
            'is_speaking': session['current_vad'].is_speaking if session['enable_vad'] else None
        }
    
    def stop_monitoring(self, session_id: str):
        """Stop monitoring session"""
        if session_id not in self.monitoring_sessions:
            raise ValueError(f"Invalid session ID: {session_id}")
        
        session = self.monitoring_sessions[session_id]
        session['is_active'] = False
        
        # Wait for thread to finish
        if session.get('thread') and session['thread'].is_alive():
            session['thread'].join(timeout=2.0)
        
        # Clean up
        del self.monitoring_sessions[session_id]
        logger.info(f"Monitoring stopped: {session_id}")
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active monitoring session IDs"""
        return [sid for sid, session in self.monitoring_sessions.items() 
                if session['is_active']]
    
    def cleanup(self):
        """Cleanup monitoring resources"""
        # Stop all active sessions
        active_sessions = list(self.monitoring_sessions.keys())
        for session_id in active_sessions:
            try:
                self.stop_monitoring(session_id)
            except Exception as e:
                logger.warning(f"Error stopping monitoring session {session_id}: {e}")
        
        # Close PyAudio
        if self.pyaudio_instance:
            self.pyaudio_instance.terminate()
            self.pyaudio_instance = None
        
        logger.info("Audio monitoring cleanup completed")
    
    def __del__(self):
        """Destructor cleanup"""
        self.cleanup()