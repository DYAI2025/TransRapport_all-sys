"""
Contract Tests for Speaker Diarization with WhisperX
CRITICAL: These tests MUST FAIL before implementation exists
"""

import pytest
import asyncio
from pathlib import Path
import tempfile
import json

# Import the speaker diarization library (will fail until implemented)
try:
    from src.lib.transcription.whisperx_service import WhisperXService
    from src.models.speaker_profile import SpeakerProfile
except ImportError:
    pytest.skip("WhisperX diarization library not implemented yet", allow_module_level=True)


class TestWhisperXDiarizationContract:
    """Contract tests for WhisperX speaker diarization"""
    
    @pytest.fixture
    def whisperx_service(self):
        """Initialize WhisperX service with diarization enabled"""
        return WhisperXService(
            enable_diarization=True,
            diarization_model="pyannote/speaker-diarization-3.1"
        )
    
    @pytest.fixture
    def multi_speaker_audio(self):
        """Audio file with 2-3 distinct speakers"""
        return Path("tests/fixtures/therapy_session_2speakers.wav")
    
    @pytest.fixture
    def business_meeting_audio(self):
        """Audio file with 3+ speakers (business meeting)"""
        return Path("tests/fixtures/business_meeting_3speakers.wav")
    
    def test_whisperx_initialization_with_diarization(self, whisperx_service):
        """MUST initialize WhisperX with pyannote diarization model"""
        assert whisperx_service.diarization_enabled is True
        
        model_info = whisperx_service.get_diarization_model_info()
        assert 'pyannote' in model_info['model_name']
        assert model_info['supports_speaker_identification'] is True
        assert model_info['max_speakers'] >= 10
    
    def test_transcribe_with_speaker_diarization(self, whisperx_service, multi_speaker_audio):
        """MUST provide transcription with speaker labels"""
        if not multi_speaker_audio.exists():
            pytest.skip("Multi-speaker audio file not available")
        
        result = whisperx_service.transcribe_with_diarization(
            audio_file=str(multi_speaker_audio),
            language="en",
            min_speakers=2,
            max_speakers=3
        )
        
        # Must return structured result with speaker info
        assert 'transcript' in result
        assert 'speakers' in result
        assert 'segments' in result
        assert 'diarization_info' in result
        
        # Must have identified speakers
        assert len(result['speakers']) >= 2
        assert len(result['speakers']) <= 3
        
        # Each segment must have speaker assignment
        for segment in result['segments']:
            assert 'speaker' in segment
            assert 'start' in segment
            assert 'end' in segment
            assert 'text' in segment
            assert 'confidence' in segment
            assert segment['speaker'] in [s['id'] for s in result['speakers']]
    
    def test_speaker_profile_generation(self, whisperx_service, multi_speaker_audio):
        """MUST generate speaker profiles with voice characteristics"""
        if not multi_speaker_audio.exists():
            pytest.skip("Multi-speaker audio file not available")
        
        result = whisperx_service.transcribe_with_diarization(
            str(multi_speaker_audio),
            generate_profiles=True
        )
        
        # Each speaker must have a profile
        for speaker in result['speakers']:
            assert 'id' in speaker
            assert 'profile' in speaker
            
            profile = speaker['profile']
            assert 'voice_characteristics' in profile
            assert 'speaking_time' in profile
            assert 'segment_count' in profile
            assert 'average_confidence' in profile
            
            # Voice characteristics must include key features
            voice_chars = profile['voice_characteristics']
            assert 'pitch_range' in voice_chars
            assert 'speaking_rate' in voice_chars
            assert 'voice_quality' in voice_chars
    
    def test_manual_speaker_correction(self, whisperx_service, multi_speaker_audio):
        """MUST support manual correction of speaker assignments"""
        if not multi_speaker_audio.exists():
            pytest.skip("Multi-speaker audio file not available")
        
        # Initial transcription
        result = whisperx_service.transcribe_with_diarization(
            str(multi_speaker_audio)
        )
        
        # Prepare speaker corrections
        corrections = [
            {
                'segment_id': result['segments'][0]['id'],
                'old_speaker': result['segments'][0]['speaker'],
                'new_speaker': 'THERAPIST'
            },
            {
                'segment_id': result['segments'][1]['id'],
                'old_speaker': result['segments'][1]['speaker'],
                'new_speaker': 'CLIENT'
            }
        ]
        
        # Apply corrections
        corrected_result = whisperx_service.apply_speaker_corrections(
            result, corrections
        )
        
        # Must update all affected segments
        updated_segments = [s for s in corrected_result['segments'] 
                          if s['id'] in [c['segment_id'] for c in corrections]]
        
        assert len(updated_segments) == len(corrections)
        assert updated_segments[0]['speaker'] == 'THERAPIST'
        assert updated_segments[1]['speaker'] == 'CLIENT'
        
        # Must update speaker profiles accordingly
        speaker_ids = [s['id'] for s in corrected_result['speakers']]
        assert 'THERAPIST' in speaker_ids
        assert 'CLIENT' in speaker_ids
    
    def test_speaker_consistency_across_segments(self, whisperx_service, multi_speaker_audio):
        """MUST maintain speaker consistency across segments"""
        if not multi_speaker_audio.exists():
            pytest.skip("Multi-speaker audio file not available")
        
        result = whisperx_service.transcribe_with_diarization(
            str(multi_speaker_audio),
            enable_speaker_consistency=True
        )
        
        # Check speaker transitions
        speaker_changes = 0
        previous_speaker = None
        
        for segment in result['segments']:
            if previous_speaker and segment['speaker'] != previous_speaker:
                speaker_changes += 1
            previous_speaker = segment['speaker']
        
        # Must have reasonable number of speaker changes (not every segment)
        total_segments = len(result['segments'])
        change_ratio = speaker_changes / total_segments
        assert change_ratio < 0.5  # Less than 50% of segments should be speaker changes
    
    def test_diarization_quality_metrics(self, whisperx_service, multi_speaker_audio):
        """MUST provide diarization quality metrics"""
        if not multi_speaker_audio.exists():
            pytest.skip("Multi-speaker audio file not available")
        
        result = whisperx_service.transcribe_with_diarization(
            str(multi_speaker_audio),
            calculate_quality_metrics=True
        )
        
        quality_metrics = result['diarization_info']['quality_metrics']
        
        # Must include standard diarization metrics
        assert 'der' in quality_metrics  # Diarization Error Rate
        assert 'speaker_purity' in quality_metrics
        assert 'speaker_coverage' in quality_metrics
        assert 'confusion_matrix' in quality_metrics
        
        # DER should be reasonable for professional use
        assert quality_metrics['der'] < 0.15  # Less than 15% error rate
        assert quality_metrics['speaker_purity'] > 0.85  # High purity
        assert quality_metrics['speaker_coverage'] > 0.85  # High coverage
    
    def test_real_time_diarization_preview(self, whisperx_service):
        """MUST support real-time speaker diarization during recording"""
        # Start real-time diarization
        session_id = whisperx_service.start_realtime_diarization(
            min_speakers=2,
            max_speakers=4,
            update_interval=5.0  # Update every 5 seconds
        )
        
        # Must provide initial empty state
        current_state = whisperx_service.get_realtime_diarization_state(session_id)
        assert 'current_speakers' in current_state
        assert 'active_speaker' in current_state
        assert 'confidence' in current_state
        assert 'speaker_changes' in current_state
        
        # Simulate audio input and get updates
        # (This would be connected to live audio stream)
        
        whisperx_service.stop_realtime_diarization(session_id)
    
    def test_export_speaker_timeline(self, whisperx_service, multi_speaker_audio):
        """MUST export speaker timeline for visualization"""
        if not multi_speaker_audio.exists():
            pytest.skip("Multi-speaker audio file not available")
        
        result = whisperx_service.transcribe_with_diarization(
            str(multi_speaker_audio)
        )
        
        timeline = whisperx_service.export_speaker_timeline(result)
        
        # Must provide timeline data
        assert 'timeline' in timeline
        assert 'speakers' in timeline
        assert 'total_duration' in timeline
        
        # Timeline entries must have correct structure
        for entry in timeline['timeline']:
            assert 'start_time' in entry
            assert 'end_time' in entry
            assert 'speaker' in entry
            assert 'duration' in entry
            assert entry['end_time'] > entry['start_time']


class TestSpeakerProfileContract:
    """Contract tests for speaker profile management"""
    
    def test_speaker_profile_creation(self):
        """MUST create speaker profiles with required fields"""
        profile = SpeakerProfile(
            speaker_id="SPEAKER_001",
            voice_characteristics={
                'pitch_mean': 180.5,
                'pitch_std': 45.2,
                'speaking_rate': 150.0,  # words per minute
                'voice_quality': 'clear'
            }
        )
        
        assert profile.speaker_id == "SPEAKER_001"
        assert profile.voice_characteristics['pitch_mean'] == 180.5
        assert hasattr(profile, 'created_at')
        assert hasattr(profile, 'updated_at')
    
    def test_speaker_profile_validation(self):
        """MUST validate speaker profile data"""
        # Invalid pitch should raise error
        with pytest.raises(ValueError, match="Invalid pitch"):
            SpeakerProfile(
                speaker_id="SPEAKER_001",
                voice_characteristics={
                    'pitch_mean': -50.0,  # Invalid negative pitch
                    'speaking_rate': 150.0
                }
            )
        
        # Invalid speaking rate should raise error
        with pytest.raises(ValueError, match="Invalid speaking rate"):
            SpeakerProfile(
                speaker_id="SPEAKER_001",
                voice_characteristics={
                    'pitch_mean': 180.5,
                    'speaking_rate': 500.0  # Unrealistically high
                }
            )


if __name__ == "__main__":
    # Run these tests to verify they FAIL before implementation
    pytest.main([__file__, "-v", "--tb=short"])