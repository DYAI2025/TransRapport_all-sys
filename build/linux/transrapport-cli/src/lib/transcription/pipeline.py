"""
Transcription Pipeline Orchestration
Coordinates Whisper ASR, speaker diarization, and language detection
"""

import time
import uuid
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

from .whisper_service import WhisperService
from .whisperx_service import WhisperXService, DiarizationResult
from .language_detection import LanguageDetection

logger = logging.getLogger(__name__)


class PipelineStage(Enum):
    """Pipeline processing stages"""
    INITIALIZED = "initialized"
    LANGUAGE_DETECTION = "language_detection"
    TRANSCRIPTION = "transcription"
    SPEAKER_DIARIZATION = "speaker_diarization"
    POST_PROCESSING = "post_processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PipelineProgress:
    """Pipeline processing progress"""
    stage: PipelineStage
    progress_percent: float
    estimated_remaining: float
    current_operation: str
    stage_details: Dict[str, Any]


@dataclass
class PipelineResult:
    """Complete pipeline processing result"""
    session_id: str
    audio_file: str
    diarization_result: DiarizationResult
    language_detection: Dict[str, Any]
    processing_time: float
    pipeline_stages: List[str]
    quality_metrics: Dict[str, Any]


class TranscriptionPipeline:
    """
    Comprehensive transcription pipeline orchestrator
    Manages the complete workflow from audio to diarized transcript
    """
    
    def __init__(self):
        self.whisper_service = WhisperService()
        self.whisperx_service = WhisperXService(enable_diarization=True)
        self.language_detector = LanguageDetection()
        self.active_pipelines: Dict[str, Dict[str, Any]] = {}
        
        logger.info("TranscriptionPipeline initialized")
    
    def start_pipeline(self, audio_file: str, options: Optional[Dict[str, Any]] = None) -> str:
        """
        Start complete transcription pipeline
        
        Args:
            audio_file: Path to audio file
            options: Pipeline processing options
            
        Returns:
            Pipeline session ID for tracking progress
        """
        session_id = str(uuid.uuid4())
        
        # Default pipeline options
        pipeline_options = {
            'auto_detect_language': True,
            'enable_speaker_diarization': True,
            'min_speakers': 2,
            'max_speakers': 6,
            'whisper_model': 'large-v3',
            'language': None,
            'generate_speaker_profiles': True,
            'quality_assessment': True
        }
        
        if options:
            pipeline_options.update(options)
        
        # Initialize pipeline session
        pipeline_session = {
            'session_id': session_id,
            'audio_file': audio_file,
            'options': pipeline_options,
            'stage': PipelineStage.INITIALIZED,
            'progress': 0.0,
            'start_time': time.time(),
            'stage_results': {},
            'result': None,
            'error': None,
            'callbacks': []
        }
        
        self.active_pipelines[session_id] = pipeline_session
        
        logger.info(f"Pipeline started: {session_id} for {audio_file}")
        return session_id
    
    def process_pipeline(self, session_id: str, 
                        progress_callback: Optional[Callable[[PipelineProgress], None]] = None) -> PipelineResult:
        """
        Execute complete pipeline processing
        
        Args:
            session_id: Pipeline session ID
            progress_callback: Optional callback for progress updates
            
        Returns:
            Complete pipeline result
        """
        if session_id not in self.active_pipelines:
            raise ValueError(f"Invalid pipeline session: {session_id}")
        
        session = self.active_pipelines[session_id]
        
        if progress_callback:
            session['callbacks'].append(progress_callback)
        
        try:
            # Stage 1: Language Detection (if enabled)
            if session['options']['auto_detect_language'] and not session['options']['language']:
                self._update_pipeline_stage(session, PipelineStage.LANGUAGE_DETECTION, 10.0)
                session['stage_results']['language_detection'] = self._detect_language(session)
            
            # Stage 2: Transcription
            self._update_pipeline_stage(session, PipelineStage.TRANSCRIPTION, 30.0)
            session['stage_results']['transcription'] = self._transcribe_audio(session)
            
            # Stage 3: Speaker Diarization (if enabled)
            if session['options']['enable_speaker_diarization']:
                self._update_pipeline_stage(session, PipelineStage.SPEAKER_DIARIZATION, 70.0)
                session['stage_results']['diarization'] = self._perform_diarization(session)
            else:
                # Create single-speaker result
                session['stage_results']['diarization'] = self._create_single_speaker_result(
                    session['stage_results']['transcription']
                )
            
            # Stage 4: Post-processing
            self._update_pipeline_stage(session, PipelineStage.POST_PROCESSING, 90.0)
            session['stage_results']['post_processing'] = self._post_process_results(session)
            
            # Complete pipeline
            self._update_pipeline_stage(session, PipelineStage.COMPLETED, 100.0)
            
            # Create final result
            result = self._create_pipeline_result(session)
            session['result'] = result
            
            logger.info(f"Pipeline completed: {session_id} in {result.processing_time:.1f}s")
            return result
            
        except Exception as e:
            logger.error(f"Pipeline failed: {session_id} - {e}")
            session['error'] = str(e)
            session['stage'] = PipelineStage.FAILED
            raise RuntimeError(f"Pipeline processing failed: {e}")
    
    def _update_pipeline_stage(self, session: Dict[str, Any], stage: PipelineStage, progress: float):
        """Update pipeline stage and notify callbacks"""
        session['stage'] = stage
        session['progress'] = progress
        
        # Calculate estimated remaining time
        elapsed = time.time() - session['start_time']
        if progress > 0:
            estimated_total = elapsed * (100.0 / progress)
            estimated_remaining = max(0, estimated_total - elapsed)
        else:
            estimated_remaining = 0.0
        
        # Create progress update
        progress_update = PipelineProgress(
            stage=stage,
            progress_percent=progress,
            estimated_remaining=estimated_remaining,
            current_operation=self._get_stage_description(stage),
            stage_details=session.get('stage_results', {})
        )
        
        # Notify callbacks
        for callback in session['callbacks']:
            try:
                callback(progress_update)
            except Exception as e:
                logger.warning(f"Progress callback error: {e}")
    
    def _get_stage_description(self, stage: PipelineStage) -> str:
        """Get human-readable stage description"""
        descriptions = {
            PipelineStage.INITIALIZED: "Initializing pipeline",
            PipelineStage.LANGUAGE_DETECTION: "Detecting audio language",
            PipelineStage.TRANSCRIPTION: "Transcribing audio with Whisper",
            PipelineStage.SPEAKER_DIARIZATION: "Identifying speakers",
            PipelineStage.POST_PROCESSING: "Finalizing results",
            PipelineStage.COMPLETED: "Processing complete",
            PipelineStage.FAILED: "Processing failed"
        }
        return descriptions.get(stage, "Unknown stage")
    
    def _detect_language(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Perform language detection stage"""
        audio_file = session['audio_file']
        
        try:
            detection_result = self.language_detector.detect_language(audio_file)
            
            # Update language option if detected with high confidence
            if detection_result['confidence'] >= 0.7:
                session['options']['language'] = detection_result['language']
                logger.info(f"Auto-detected language: {detection_result['language']} "
                           f"(confidence: {detection_result['confidence']:.2f})")
            
            return detection_result
            
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            # Fallback to English
            session['options']['language'] = 'en'
            return {
                'language': 'en',
                'confidence': 0.5,
                'language_name': 'English',
                'alternatives': [],
                'fallback': True
            }
    
    def _transcribe_audio(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Perform transcription stage"""
        audio_file = session['audio_file']
        language = session['options']['language']
        model_size = session['options']['whisper_model']
        
        # Configure Whisper service if needed
        if self.whisper_service.model_size != model_size:
            self.whisper_service = WhisperService(model_size)
        
        # Transcribe audio
        transcription_result = self.whisper_service.transcribe(
            audio_file=audio_file,
            language=language,
            options={
                'word_timestamps': True,
                'temperature': 0.0  # Deterministic output
            }
        )
        
        return {
            'transcription': transcription_result,
            'model_used': model_size,
            'language_used': language
        }
    
    def _perform_diarization(self, session: Dict[str, Any]) -> DiarizationResult:
        """Perform speaker diarization stage"""
        audio_file = session['audio_file']
        language = session['options']['language']
        min_speakers = session['options']['min_speakers']
        max_speakers = session['options']['max_speakers']
        generate_profiles = session['options']['generate_speaker_profiles']
        
        # Perform diarization with WhisperX
        diarization_result = self.whisperx_service.transcribe_with_diarization(
            audio_file=audio_file,
            language=language,
            min_speakers=min_speakers,
            max_speakers=max_speakers,
            generate_profiles=generate_profiles
        )
        
        return diarization_result
    
    def _create_single_speaker_result(self, transcription_stage: Dict[str, Any]) -> DiarizationResult:
        """Create single-speaker diarization result when diarization is disabled"""
        from .whisperx_service import SpeakerProfile, DiarizationSegment
        
        transcription = transcription_stage['transcription']
        
        # Create single speaker
        single_speaker = SpeakerProfile(
            id="SINGLE_SPEAKER",
            label="SINGLE_SPEAKER",
            speaking_time=transcription.duration,
            segment_count=len(transcription.segments),
            average_confidence=sum(seg.confidence for seg in transcription.segments) / len(transcription.segments) if transcription.segments else 0.0
        )
        
        # Convert transcription segments to diarization segments
        diarization_segments = []
        for i, seg in enumerate(transcription.segments):
            diarization_segments.append(DiarizationSegment(
                id=f"seg_{i}",
                start=seg.start,
                end=seg.end,
                speaker="SINGLE_SPEAKER",
                text=seg.text,
                confidence=seg.confidence
            ))
        
        return DiarizationResult(
            transcript=transcription.text,
            speakers=[single_speaker],
            segments=diarization_segments,
            diarization_info={
                'num_speakers': 1,
                'diarization_enabled': False,
                'single_speaker_mode': True
            }
        )
    
    def _post_process_results(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process and validate results"""
        diarization_result = session['stage_results']['diarization']
        
        # Calculate quality metrics
        quality_metrics = self._calculate_quality_metrics(session)
        
        # Validate result completeness
        validation_result = self._validate_pipeline_result(session)
        
        return {
            'quality_metrics': quality_metrics,
            'validation': validation_result,
            'post_processing_applied': ['quality_assessment', 'result_validation']
        }
    
    def _calculate_quality_metrics(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall processing quality metrics"""
        diarization_result = session['stage_results']['diarization']
        
        # Basic quality metrics
        metrics = {
            'total_segments': len(diarization_result.segments),
            'total_speakers': len(diarization_result.speakers),
            'total_duration': max(seg.end for seg in diarization_result.segments) if diarization_result.segments else 0.0,
            'average_confidence': sum(seg.confidence for seg in diarization_result.segments) / len(diarization_result.segments) if diarization_result.segments else 0.0
        }
        
        # Speaking time distribution
        speaker_times = {}
        for segment in diarization_result.segments:
            duration = segment.end - segment.start
            speaker_times[segment.speaker] = speaker_times.get(segment.speaker, 0.0) + duration
        
        metrics['speaker_distribution'] = speaker_times
        
        # Balance score (how evenly distributed speaking time is)
        if len(speaker_times) > 1:
            times = list(speaker_times.values())
            mean_time = sum(times) / len(times)
            variance = sum((t - mean_time) ** 2 for t in times) / len(times)
            balance_score = 1.0 - (variance / (mean_time ** 2)) if mean_time > 0 else 0.0
            metrics['speaker_balance_score'] = max(0.0, min(1.0, balance_score))
        
        # Language detection confidence (if available)
        if 'language_detection' in session['stage_results']:
            metrics['language_detection_confidence'] = session['stage_results']['language_detection']['confidence']
        
        return metrics
    
    def _validate_pipeline_result(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Validate pipeline result quality and completeness"""
        diarization_result = session['stage_results']['diarization']
        
        validation = {
            'is_valid': True,
            'warnings': [],
            'recommendations': []
        }
        
        # Check transcript completeness
        if not diarization_result.transcript or len(diarization_result.transcript.strip()) < 10:
            validation['warnings'].append("Very short or empty transcript")
            validation['is_valid'] = False
        
        # Check segment count
        if len(diarization_result.segments) == 0:
            validation['warnings'].append("No transcript segments found")
            validation['is_valid'] = False
        elif len(diarization_result.segments) < 2:
            validation['warnings'].append("Very few transcript segments - audio may be very short")
        
        # Check speaker detection
        if session['options']['enable_speaker_diarization']:
            if len(diarization_result.speakers) < session['options']['min_speakers']:
                validation['warnings'].append(f"Fewer speakers detected than minimum ({session['options']['min_speakers']})")
                validation['recommendations'].append("Verify audio has multiple speakers")
            
            if len(diarization_result.speakers) > session['options']['max_speakers']:
                validation['warnings'].append(f"More speakers detected than expected ({session['options']['max_speakers']})")
                validation['recommendations'].append("Consider adjusting max_speakers setting")
        
        # Check average confidence
        avg_confidence = sum(seg.confidence for seg in diarization_result.segments) / len(diarization_result.segments) if diarization_result.segments else 0.0
        if avg_confidence < 0.7:
            validation['warnings'].append("Low average confidence in transcription")
            validation['recommendations'].append("Check audio quality and language settings")
        
        return validation
    
    def _create_pipeline_result(self, session: Dict[str, Any]) -> PipelineResult:
        """Create final pipeline result"""
        processing_time = time.time() - session['start_time']
        
        return PipelineResult(
            session_id=session['session_id'],
            audio_file=session['audio_file'],
            diarization_result=session['stage_results']['diarization'],
            language_detection=session['stage_results'].get('language_detection', {}),
            processing_time=processing_time,
            pipeline_stages=list(session['stage_results'].keys()),
            quality_metrics=session['stage_results']['post_processing']['quality_metrics']
        )
    
    def get_pipeline_progress(self, session_id: str) -> PipelineProgress:
        """Get current pipeline progress"""
        if session_id not in self.active_pipelines:
            raise ValueError(f"Invalid pipeline session: {session_id}")
        
        session = self.active_pipelines[session_id]
        
        # Calculate current progress
        elapsed = time.time() - session['start_time']
        estimated_remaining = 0.0
        
        if session['progress'] > 0:
            estimated_total = elapsed * (100.0 / session['progress'])
            estimated_remaining = max(0, estimated_total - elapsed)
        
        return PipelineProgress(
            stage=session['stage'],
            progress_percent=session['progress'],
            estimated_remaining=estimated_remaining,
            current_operation=self._get_stage_description(session['stage']),
            stage_details=session.get('stage_results', {})
        )
    
    def cancel_pipeline(self, session_id: str):
        """Cancel active pipeline processing"""
        if session_id in self.active_pipelines:
            session = self.active_pipelines[session_id]
            session['stage'] = PipelineStage.FAILED
            session['error'] = "Pipeline cancelled by user"
            logger.info(f"Pipeline cancelled: {session_id}")
    
    def cleanup_pipeline(self, session_id: str):
        """Cleanup pipeline session resources"""
        if session_id in self.active_pipelines:
            del self.active_pipelines[session_id]
            logger.info(f"Pipeline session cleaned up: {session_id}")
    
    def get_active_pipelines(self) -> List[str]:
        """Get list of active pipeline session IDs"""
        return list(self.active_pipelines.keys())
    
    def cleanup_all(self):
        """Cleanup all resources"""
        self.whisper_service.cleanup()
        self.whisperx_service.cleanup()
        self.language_detector.cleanup()
        self.active_pipelines.clear()
        
        logger.info("TranscriptionPipeline cleanup completed")
    
    def __del__(self):
        """Destructor cleanup"""
        self.cleanup_all()