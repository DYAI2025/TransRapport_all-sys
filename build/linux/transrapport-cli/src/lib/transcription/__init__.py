"""
Transcription Library for TransRapport Offline Desktop
Whisper ASR integration with speaker diarization
"""

from .whisper_service import WhisperService
from .whisperx_service import WhisperXService
from .language_detection import LanguageDetection
from .pipeline import TranscriptionPipeline

__all__ = ['WhisperService', 'WhisperXService', 'LanguageDetection', 'TranscriptionPipeline']