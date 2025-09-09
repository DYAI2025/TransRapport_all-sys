"""
Audio Import Service
Import and validate audio files for transcription processing
"""

import os
import wave
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

try:
    import librosa
    import soundfile as sf
    import numpy as np
except ImportError:
    librosa = None
    sf = None
    np = None

logger = logging.getLogger(__name__)


@dataclass
class AudioFileInfo:
    """Audio file information"""
    file_path: str
    format: str
    duration: float
    sample_rate: int
    channels: int
    file_size: int
    bit_depth: Optional[int] = None
    is_valid: bool = True
    validation_errors: List[str] = None


class AudioImport:
    """
    Audio file import and validation service
    Supports multiple formats and conversion for Whisper compatibility
    """
    
    SUPPORTED_FORMATS = {'.wav', '.mp3', '.flac', '.m4a', '.ogg', '.aac'}
    WHISPER_SAMPLE_RATE = 16000
    WHISPER_CHANNELS = 1
    
    def __init__(self):
        self.temp_dir = Path("temp/audio_import")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def import_audio_file(self, file_path: str, validate: bool = True) -> AudioFileInfo:
        """
        Import and validate audio file
        
        Args:
            file_path: Path to audio file
            validate: Whether to perform validation
            
        Returns:
            AudioFileInfo with file details and validation results
        """
        file_path = Path(file_path)
        
        # Basic file checks
        if not file_path.exists():
            return AudioFileInfo(
                file_path=str(file_path),
                format="",
                duration=0.0,
                sample_rate=0,
                channels=0,
                file_size=0,
                is_valid=False,
                validation_errors=["File does not exist"]
            )
        
        # Check file extension
        if file_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            return AudioFileInfo(
                file_path=str(file_path),
                format=file_path.suffix.lower(),
                duration=0.0,
                sample_rate=0,
                channels=0,
                file_size=file_path.stat().st_size,
                is_valid=False,
                validation_errors=[f"Unsupported format: {file_path.suffix}"]
            )
        
        try:
            # Get basic file info
            file_info = self._get_file_info(file_path)
            
            if validate:
                file_info.validation_errors = self._validate_audio_file(file_info)
                file_info.is_valid = len(file_info.validation_errors) == 0
            
            logger.info(f"Imported audio file: {file_path} ({file_info.duration:.1f}s)")
            return file_info
            
        except Exception as e:
            logger.error(f"Failed to import audio file {file_path}: {e}")
            return AudioFileInfo(
                file_path=str(file_path),
                format=file_path.suffix.lower(),
                duration=0.0,
                sample_rate=0,
                channels=0,
                file_size=file_path.stat().st_size,
                is_valid=False,
                validation_errors=[f"Import error: {e}"]
            )
    
    def _get_file_info(self, file_path: Path) -> AudioFileInfo:
        """Get detailed audio file information"""
        if librosa is None:
            # Fallback to wave for WAV files
            if file_path.suffix.lower() == '.wav':
                return self._get_wav_info(file_path)
            else:
                # Mock info for other formats when librosa not available
                return AudioFileInfo(
                    file_path=str(file_path),
                    format=file_path.suffix.lower(),
                    duration=60.0,  # Mock duration
                    sample_rate=44100,
                    channels=2,
                    file_size=file_path.stat().st_size,
                    bit_depth=16
                )
        
        try:
            # Use librosa for comprehensive format support
            y, sr = librosa.load(str(file_path), sr=None, mono=False)
            
            # Handle channel detection
            if y.ndim == 1:
                channels = 1
                duration = len(y) / sr
            else:
                channels = y.shape[0]
                duration = y.shape[1] / sr
            
            return AudioFileInfo(
                file_path=str(file_path),
                format=file_path.suffix.lower(),
                duration=duration,
                sample_rate=sr,
                channels=channels,
                file_size=file_path.stat().st_size,
                bit_depth=None  # librosa doesn't provide bit depth
            )
            
        except Exception as e:
            logger.warning(f"Librosa failed for {file_path}, trying fallback: {e}")
            # Fallback to wave for WAV files
            if file_path.suffix.lower() == '.wav':
                return self._get_wav_info(file_path)
            else:
                raise
    
    def _get_wav_info(self, file_path: Path) -> AudioFileInfo:
        """Get WAV file info using wave module"""
        try:
            with wave.open(str(file_path), 'rb') as wf:
                return AudioFileInfo(
                    file_path=str(file_path),
                    format='.wav',
                    duration=wf.getnframes() / wf.getframerate(),
                    sample_rate=wf.getframerate(),
                    channels=wf.getnchannels(),
                    file_size=file_path.stat().st_size,
                    bit_depth=wf.getsampwidth() * 8
                )
        except Exception as e:
            raise ValueError(f"Invalid WAV file: {e}")
    
    def _validate_audio_file(self, file_info: AudioFileInfo) -> List[str]:
        """Validate audio file for transcription suitability"""
        errors = []
        
        # Duration checks
        if file_info.duration < 1.0:
            errors.append("Audio too short (< 1 second)")
        elif file_info.duration > 7200:  # 2 hours
            errors.append("Audio too long (> 2 hours) - may impact performance")
        
        # Sample rate checks
        if file_info.sample_rate < 8000:
            errors.append("Sample rate too low (< 8kHz)")
        elif file_info.sample_rate > 48000:
            errors.append("Sample rate unusually high (> 48kHz)")
        
        # Channel checks
        if file_info.channels > 2:
            errors.append(f"Too many channels ({file_info.channels}) - stereo or mono recommended")
        
        # File size checks
        if file_info.file_size < 1000:  # 1KB
            errors.append("File size too small - possibly corrupted")
        elif file_info.file_size > 1e9:  # 1GB
            errors.append("File size very large (> 1GB) - may impact processing")
        
        return errors
    
    def convert_for_whisper(self, file_path: str, output_path: Optional[str] = None) -> str:
        """
        Convert audio file to Whisper-optimal format (16kHz, mono, WAV)
        
        Args:
            file_path: Input audio file path
            output_path: Output file path (auto-generated if None)
            
        Returns:
            Path to converted file
        """
        input_path = Path(file_path)
        
        if output_path is None:
            output_path = self.temp_dir / f"{input_path.stem}_whisper.wav"
        else:
            output_path = Path(output_path)
        
        # Create output directory
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if librosa is None:
            # Simple WAV-to-WAV conversion if needed
            if input_path.suffix.lower() == '.wav':
                file_info = self.import_audio_file(file_path)
                if (file_info.sample_rate == self.WHISPER_SAMPLE_RATE and 
                    file_info.channels == self.WHISPER_CHANNELS):
                    # Already in correct format
                    return file_path
                else:
                    # Need conversion but librosa not available
                    logger.warning("Audio conversion needed but librosa not available")
                    return file_path
            else:
                raise RuntimeError("Cannot convert non-WAV files without librosa")
        
        try:
            # Load audio with librosa
            y, sr = librosa.load(str(input_path), sr=self.WHISPER_SAMPLE_RATE, mono=True)
            
            # Save as WAV
            sf.write(str(output_path), y, self.WHISPER_SAMPLE_RATE)
            
            logger.info(f"Converted audio: {input_path} -> {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Audio conversion failed: {e}")
            raise RuntimeError(f"Failed to convert audio: {e}")
    
    def batch_import(self, file_paths: List[str], validate: bool = True) -> Dict[str, AudioFileInfo]:
        """Import multiple audio files"""
        results = {}
        
        for file_path in file_paths:
            try:
                results[file_path] = self.import_audio_file(file_path, validate)
            except Exception as e:
                logger.error(f"Failed to import {file_path}: {e}")
                results[file_path] = AudioFileInfo(
                    file_path=file_path,
                    format="",
                    duration=0.0,
                    sample_rate=0,
                    channels=0,
                    file_size=0,
                    is_valid=False,
                    validation_errors=[f"Import failed: {e}"]
                )
        
        return results
    
    def get_quality_assessment(self, file_path: str) -> Dict[str, Any]:
        """Assess audio quality for transcription"""
        file_info = self.import_audio_file(file_path)
        
        if not file_info.is_valid:
            return {
                'overall_quality': 'poor',
                'transcription_suitability': 'unsuitable',
                'issues': file_info.validation_errors,
                'recommendations': ['Fix validation errors before proceeding']
            }
        
        # Quality scoring
        quality_score = 0.0
        issues = []
        recommendations = []
        
        # Sample rate scoring
        if file_info.sample_rate >= 16000:
            quality_score += 30
        elif file_info.sample_rate >= 8000:
            quality_score += 15
            issues.append("Sample rate below optimal (16kHz)")
            recommendations.append("Consider upsampling to 16kHz")
        else:
            issues.append("Sample rate too low for good transcription")
            recommendations.append("Upsample to at least 16kHz")
        
        # Channel scoring
        if file_info.channels == 1:
            quality_score += 20
        elif file_info.channels == 2:
            quality_score += 15
            recommendations.append("Consider converting to mono for better performance")
        else:
            issues.append("Multi-channel audio may impact transcription")
            recommendations.append("Convert to mono")
        
        # Duration scoring
        if 10 <= file_info.duration <= 3600:  # 10 seconds to 1 hour
            quality_score += 30
        elif file_info.duration < 10:
            issues.append("Very short audio may have lower accuracy")
        elif file_info.duration > 3600:
            issues.append("Long audio files may impact processing time")
            recommendations.append("Consider splitting into shorter segments")
        
        # Format scoring
        if file_info.format in ['.wav', '.flac']:
            quality_score += 20
        elif file_info.format in ['.mp3', '.m4a']:
            quality_score += 10
            issues.append("Compressed format may impact quality")
        
        # Overall assessment
        if quality_score >= 80:
            overall_quality = 'excellent'
            suitability = 'optimal'
        elif quality_score >= 60:
            overall_quality = 'good'
            suitability = 'suitable'
        elif quality_score >= 40:
            overall_quality = 'fair'
            suitability = 'acceptable'
        else:
            overall_quality = 'poor'
            suitability = 'problematic'
        
        return {
            'overall_quality': overall_quality,
            'transcription_suitability': suitability,
            'quality_score': quality_score,
            'issues': issues,
            'recommendations': recommendations,
            'file_info': file_info.to_dict() if hasattr(file_info, 'to_dict') else file_info.__dict__
        }
    
    def cleanup_temp_files(self):
        """Clean up temporary conversion files"""
        try:
            for temp_file in self.temp_dir.glob("*"):
                if temp_file.is_file():
                    temp_file.unlink()
            logger.info("Cleaned up temporary audio files")
        except Exception as e:
            logger.warning(f"Failed to cleanup temp files: {e}")
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported audio formats"""
        return sorted(list(self.SUPPORTED_FORMATS))