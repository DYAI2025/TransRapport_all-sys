"""
TransRapport Enhanced Audio Pipeline
Complete audio processing with ASR, Diarization, and Prosody Analysis
"""

import logging
import torch
import whisper
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import json
import time

# Optional imports with fallbacks
try:
    import whisperx
    WHISPERX_AVAILABLE = True
except ImportError:
    WHISPERX_AVAILABLE = False

try:
    from pyannote.audio import Pipeline
    PYANNOTE_AVAILABLE = True
except ImportError:
    PYANNOTE_AVAILABLE = False

try:
    from .prosody import ProsodyAnalyzer
    PROSODY_AVAILABLE = True
except ImportError:
    PROSODY_AVAILABLE = False

try:
    from .capture import AudioCapture
    CAPTURE_AVAILABLE = True
except ImportError:
    CAPTURE_AVAILABLE = False

logger = logging.getLogger(__name__)

class EnhancedAudioPipeline:
    """
    Complete audio processing pipeline with:
    - Real-time audio capture
    - Speech recognition (Whisper/WhisperX)
    - Speaker diarization (pyannote.audio)
    - Prosody and emotion analysis
    - Integrated results with corrections
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        self.models = {}
        self._initialize_models()

    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for the audio pipeline"""
        return {
            'whisper': {
                'model': 'base',
                'language': 'de',
                'task': 'transcribe'
            },
            'diarization': {
                'min_speakers': 1,
                'max_speakers': 5,
                'use_whisperx': WHISPERX_AVAILABLE
            },
            'prosody': {
                'enabled': PROSODY_AVAILABLE,
                'emotion_detection': True
            },
            'capture': {
                'enabled': CAPTURE_AVAILABLE,
                'sample_rate': 16000,
                'channels': 1
            }
        }

    def _initialize_models(self):
        """Initialize all available models"""
        try:
            # Initialize Whisper
            logger.info(f"Loading Whisper model: {self.config['whisper']['model']}")
            self.models['whisper'] = whisper.load_model(self.config['whisper']['model'])

            # Initialize WhisperX if available
            if WHISPERX_AVAILABLE and self.config['diarization']['use_whisperx']:
                logger.info("Initializing WhisperX for enhanced transcription")
                # WhisperX will be initialized per audio file

            # Initialize pyannote diarization if available
            if PYANNOTE_AVAILABLE:
                logger.info("Loading pyannote diarization pipeline")
                self.models['diarization'] = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization-3.1",
                    use_auth_token=None  # Will use local model if available
                )

            # Initialize prosody analyzer if available
            if PROSODY_AVAILABLE and self.config['prosody']['enabled']:
                logger.info("Initializing prosody analyzer")
                self.models['prosody'] = ProsodyAnalyzer()

            # Initialize audio capture if available
            if CAPTURE_AVAILABLE and self.config['capture']['enabled']:
                logger.info("Initializing audio capture")
                self.models['capture'] = AudioCapture()

        except Exception as e:
            logger.error(f"Model initialization failed: {e}")
            raise

    def process_audio_file(self, audio_file: str,
                          enable_diarization: bool = True,
                          enable_prosody: bool = True) -> Dict[str, Any]:
        """
        Complete audio processing pipeline

        Args:
            audio_file: Path to audio file
            enable_diarization: Whether to perform speaker diarization
            enable_prosody: Whether to perform prosody analysis

        Returns:
            Complete processing results
        """
        start_time = time.time()
        results = {
            'metadata': {
                'audio_file': audio_file,
                'processing_start': start_time,
                'pipeline_version': '2.0.0'
            },
            'transcription': {},
            'diarization': {},
            'prosody': {},
            'integrated_results': {}
        }

        try:
            # Step 1: Speech Recognition
            logger.info("Starting speech recognition...")
            transcription_result = self._transcribe_audio(audio_file)
            results['transcription'] = transcription_result

            # Step 2: Speaker Diarization (if enabled and available)
            if enable_diarization and PYANNOTE_AVAILABLE and 'diarization' in self.models:
                logger.info("Starting speaker diarization...")
                diarization_result = self._diarize_audio(audio_file)
                results['diarization'] = diarization_result

                # Integrate transcription with diarization
                if transcription_result.get('segments'):
                    results['integrated_results'] = self._integrate_transcription_diarization(
                        transcription_result['segments'],
                        diarization_result
                    )

            # Step 3: Prosody Analysis (if enabled and available)
            if enable_prosody and PROSODY_AVAILABLE and 'prosody' in self.models:
                logger.info("Starting prosody analysis...")
                prosody_result = self.models['prosody'].analyze_audio_file(audio_file)
                results['prosody'] = prosody_result

                # Add emotion classification
                if 'prosody' in prosody_result and 'error' not in prosody_result['prosody']:
                    results['prosody']['emotion_classification'] = \
                        self.models['prosody'].analyze_emotion_dimensions(prosody_result['prosody'])

            # Step 4: Quality Assessment
            results['quality_metrics'] = self._assess_audio_quality(results)

            results['metadata']['processing_duration'] = time.time() - start_time
            results['metadata']['success'] = True

        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
            results['error'] = str(e)
            results['metadata']['success'] = False
            results['metadata']['processing_duration'] = time.time() - start_time

        return results

    def _transcribe_audio(self, audio_file: str) -> Dict[str, Any]:
        """Transcribe audio using Whisper or WhisperX"""
        try:
            if WHISPERX_AVAILABLE and self.config['diarization']['use_whisperx']:
                return self._transcribe_whisperx(audio_file)
            else:
                return self._transcribe_whisper(audio_file)
        except Exception as e:
            logger.warning(f"Transcription failed, falling back to basic Whisper: {e}")
            return self._transcribe_whisper(audio_file)

    def _transcribe_whisper(self, audio_file: str) -> Dict[str, Any]:
        """Basic Whisper transcription"""
        result = self.models['whisper'].transcribe(
            audio_file,
            language=self.config['whisper']['language'],
            task=self.config['whisper']['task']
        )

        return {
            'text': result['text'],
            'segments': result['segments'],
            'language': result['language'],
            'model': self.config['whisper']['model']
        }

    def _transcribe_whisperx(self, audio_file: str) -> Dict[str, Any]:
        """Enhanced WhisperX transcription with better alignment"""
        import whisperx

        # Load audio
        audio = whisperx.load_audio(audio_file)

        # Transcribe
        result = self.models['whisper'].transcribe(audio, language=self.config['whisper']['language'])

        # Align transcription
        model_a, metadata = whisperx.load_align_model(
            language_code=result["language"],
            device="cpu"  # Use CPU for compatibility
        )
        result = whisperx.align(
            result["segments"],
            model_a,
            metadata,
            audio,
            device="cpu"
        )

        return {
            'text': result['text'],
            'segments': result['segments'],
            'language': result['language'],
            'model': f"{self.config['whisper']['model']}+whisperx",
            'alignment': True
        }

    def _diarize_audio(self, audio_file: str) -> Dict[str, Any]:
        """Perform speaker diarization using pyannote"""
        try:
            # Run diarization
            diarization = self.models['diarization'](audio_file)

            # Extract speaker segments
            speakers = {}
            segments = []

            for turn, _, speaker in diarization.itertracks(yield_label=True):
                speaker_id = f"Speaker_{speaker}"
                if speaker_id not in speakers:
                    speakers[speaker_id] = {
                        'id': speaker_id,
                        'total_duration': 0.0,
                        'segment_count': 0
                    }

                segment = {
                    'start': turn.start,
                    'end': turn.end,
                    'duration': turn.end - turn.start,
                    'speaker': speaker_id
                }
                segments.append(segment)

                speakers[speaker_id]['total_duration'] += segment['duration']
                speakers[speaker_id]['segment_count'] += 1

            return {
                'speakers': list(speakers.values()),
                'segments': segments,
                'total_speakers': len(speakers)
            }

        except Exception as e:
            logger.error(f"Diarization failed: {e}")
            return {'error': str(e)}

    def _integrate_transcription_diarization(self, transcription_segments: List[Dict],
                                           diarization_result: Dict) -> List[Dict]:
        """Integrate transcription with speaker diarization"""
        integrated_segments = []

        for trans_seg in transcription_segments:
            # Find overlapping diarization segment
            trans_start = trans_seg['start']
            trans_end = trans_seg['end']

            best_speaker = None
            max_overlap = 0

            for dia_seg in diarization_result.get('segments', []):
                # Calculate overlap
                overlap_start = max(trans_start, dia_seg['start'])
                overlap_end = min(trans_end, dia_seg['end'])
                overlap = max(0, overlap_end - overlap_start)

                if overlap > max_overlap:
                    max_overlap = overlap
                    best_speaker = dia_seg['speaker']

            # Create integrated segment
            integrated_segment = trans_seg.copy()
            integrated_segment['speaker'] = best_speaker or 'Unknown'
            integrated_segment['confidence'] = trans_seg.get('confidence', 0.0)
            integrated_segments.append(integrated_segment)

        return integrated_segments

    def _assess_audio_quality(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall audio processing quality"""
        metrics = {
            'transcription_quality': self._assess_transcription_quality(results),
            'diarization_quality': self._assess_diarization_quality(results),
            'prosody_quality': self._assess_prosody_quality(results),
        }

        metrics['overall_quality'] = self._calculate_overall_quality(metrics)
        return metrics

    def _assess_transcription_quality(self, results: Dict[str, Any]) -> str:
        """Assess transcription quality"""
        if 'transcription' not in results or 'text' not in results['transcription']:
            return 'unknown'

        text_length = len(results['transcription']['text'].strip())
        if text_length > 100:
            return 'good'
        elif text_length > 10:
            return 'fair'
        else:
            return 'poor'

    def _assess_diarization_quality(self, results: Dict[str, Any]) -> str:
        """Assess diarization quality"""
        if 'diarization' not in results or 'speakers' not in results['diarization']:
            return 'unknown'

        speaker_count = len(results['diarization']['speakers'])
        return 'good' if speaker_count > 0 else 'none'

    def _assess_prosody_quality(self, results: Dict[str, Any]) -> str:
        """Assess prosody quality"""
        if 'prosody' not in results or 'file_info' not in results['prosody']:
            return 'unknown'
        return 'good'

    def _calculate_overall_quality(self, metrics: Dict[str, str]) -> str:
        """Calculate overall quality from individual metrics"""
        qualities = [v for v in metrics.values() if v != 'unknown']

        if not qualities:
            return 'unknown'
        elif all(q == 'good' for q in qualities):
            return 'excellent'
        elif any(q == 'good' for q in qualities):
            return 'good'
        elif any(q == 'fair' for q in qualities):
            return 'fair'
        else:
            return 'poor'

    def record_and_process(self, output_file: str, duration: int = 30,
                          enable_diarization: bool = True,
                          enable_prosody: bool = True) -> Dict[str, Any]:
        """
        Record audio and process it through the complete pipeline

        Args:
            output_file: Path to save recorded audio
            duration: Recording duration in seconds
            enable_diarization: Whether to perform diarization
            enable_prosody: Whether to perform prosody analysis

        Returns:
            Complete processing results
        """
        if not CAPTURE_AVAILABLE or 'capture' not in self.models:
            raise RuntimeError("Audio capture not available")

        try:
            # Start recording
            session_id = self.models['capture'].start_recording(
                output_file,
                sample_rate=self.config['capture']['sample_rate'],
                channels=self.config['capture']['channels']
            )

            logger.info(f"Recording started: {session_id}")

            # Wait for recording to complete
            time.sleep(duration)

            # Stop recording
            recording_result = self.models['capture'].stop_recording(session_id)
            logger.info(f"Recording completed: {recording_result}")

            if not recording_result.get('success', False):
                raise RuntimeError("Recording failed")

            # Process the recorded audio
            return self.process_audio_file(
                output_file,
                enable_diarization=enable_diarization,
                enable_prosody=enable_prosody
            )

        except Exception as e:
            logger.error(f"Record and process failed: {e}")
            return {'error': str(e)}

    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get status of all pipeline components"""
        status = {
            'whisper': 'available' if 'whisper' in self.models else 'unavailable',
            'whisperx': 'available' if WHISPERX_AVAILABLE else 'unavailable',
            'diarization': 'available' if PYANNOTE_AVAILABLE and 'diarization' in self.models else 'unavailable',
            'prosody': 'available' if PROSODY_AVAILABLE and 'prosody' in self.models else 'unavailable',
            'capture': 'available' if CAPTURE_AVAILABLE and 'capture' in self.models else 'unavailable'
        }

        return {
            'components': status,
            'config': self.config,
            'ready': all(s == 'available' for s in status.values())
        }

# Convenience functions
def process_audio_enhanced(audio_file: str) -> Dict[str, Any]:
    """
    Convenience function for enhanced audio processing

    Args:
        audio_file: Path to audio file

    Returns:
        Complete processing results
    """
    pipeline = EnhancedAudioPipeline()
    return pipeline.process_audio_file(audio_file)

def record_and_analyze(duration: int = 30, output_file: str = "recording.wav") -> Dict[str, Any]:
    """
    Convenience function for recording and analyzing audio

    Args:
        duration: Recording duration in seconds
        output_file: Output file path

    Returns:
        Complete analysis results
    """
    pipeline = EnhancedAudioPipeline()
    return pipeline.record_and_process(output_file, duration)

if __name__ == "__main__":
    # Example usage and status check
    pipeline = EnhancedAudioPipeline()
    status = pipeline.get_pipeline_status()

    print("Enhanced Audio Pipeline Status:")
    print("=" * 40)
    for component, state in status['components'].items():
        print(f"{component.capitalize():12}: {state}")

    print(f"\nPipeline Ready: {status['ready']}")

    if status['ready']:
        print("\nAvailable features:")
        print("- Real-time audio capture")
        print("- Speech recognition (Whisper)")
        print("- Speaker diarization (pyannote)")
        print("- Prosody and emotion analysis")
        print("- Integrated results with corrections")
