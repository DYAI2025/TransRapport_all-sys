"""
Audio Processor Service
Audio format conversion and preprocessing for Whisper compatibility
"""

import os
import tempfile
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

try:
    import librosa
    import soundfile as sf
    import numpy as np
    from scipy import signal
except ImportError:
    librosa = None
    sf = None
    np = None
    signal = None

logger = logging.getLogger(__name__)


@dataclass
class ProcessingOptions:
    """Audio processing configuration"""
    target_sample_rate: int = 16000
    target_channels: int = 1
    normalize: bool = True
    remove_silence: bool = False
    noise_reduction: bool = False
    high_pass_filter: bool = True
    high_pass_cutoff: float = 80.0  # Hz


@dataclass 
class ProcessingResult:
    """Audio processing result"""
    output_path: str
    original_duration: float
    processed_duration: float
    original_sample_rate: int
    processed_sample_rate: int
    original_channels: int
    processed_channels: int
    processing_applied: List[str]
    quality_improvements: Dict[str, float]


class AudioProcessor:
    """
    Audio preprocessing and format conversion service
    Optimizes audio files for Whisper transcription accuracy
    """
    
    def __init__(self, temp_dir: Optional[str] = None):
        self.temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.gettempdir()) / "transrapport_audio"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        if librosa is None:
            logger.warning("librosa not available - limited audio processing")
    
    def process_for_transcription(self, input_path: str, 
                                output_path: Optional[str] = None,
                                options: Optional[ProcessingOptions] = None) -> ProcessingResult:
        """
        Process audio file for optimal transcription quality
        
        Args:
            input_path: Input audio file path
            output_path: Output file path (auto-generated if None)
            options: Processing options
            
        Returns:
            ProcessingResult with processing details
        """
        if options is None:
            options = ProcessingOptions()
        
        input_path = Path(input_path)
        if output_path is None:
            output_path = self.temp_dir / f"{input_path.stem}_processed.wav"
        else:
            output_path = Path(output_path)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if librosa is None:
            # Fallback: just copy file if no processing available
            logger.warning("Limited processing - copying file")
            output_path.write_bytes(input_path.read_bytes())
            return ProcessingResult(
                output_path=str(output_path),
                original_duration=0.0,
                processed_duration=0.0,
                original_sample_rate=16000,
                processed_sample_rate=16000,
                original_channels=1,
                processed_channels=1,
                processing_applied=["file_copy"],
                quality_improvements={}
            )
        
        try:
            # Load original audio
            y_orig, sr_orig = librosa.load(str(input_path), sr=None, mono=False)
            
            # Handle channel structure
            if y_orig.ndim == 1:
                channels_orig = 1
                duration_orig = len(y_orig) / sr_orig
            else:
                channels_orig = y_orig.shape[0] 
                duration_orig = y_orig.shape[1] / sr_orig
            
            logger.info(f"Processing audio: {input_path} ({duration_orig:.1f}s, {sr_orig}Hz, {channels_orig}ch)")
            
            # Apply processing pipeline
            y_processed, sr_processed, applied_processing = self._apply_processing_pipeline(
                y_orig, sr_orig, options
            )
            
            # Save processed audio
            sf.write(str(output_path), y_processed, sr_processed)
            
            # Calculate quality improvements
            quality_improvements = self._calculate_quality_improvements(
                y_orig, y_processed, sr_orig, sr_processed
            )
            
            result = ProcessingResult(
                output_path=str(output_path),
                original_duration=duration_orig,
                processed_duration=len(y_processed) / sr_processed,
                original_sample_rate=sr_orig,
                processed_sample_rate=sr_processed,
                original_channels=channels_orig,
                processed_channels=1,  # Always output mono
                processing_applied=applied_processing,
                quality_improvements=quality_improvements
            )
            
            logger.info(f"Audio processing completed: {len(applied_processing)} operations applied")
            return result
            
        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
            raise RuntimeError(f"Failed to process audio: {e}")
    
    def _apply_processing_pipeline(self, y: Any, sr: int, 
                                 options: ProcessingOptions) -> Tuple[Any, int, List[str]]:
        """Apply audio processing pipeline"""
        applied_operations = []
        
        # Convert to mono if needed
        if y.ndim > 1:
            if options.target_channels == 1:
                y = np.mean(y, axis=0)  # Convert to mono by averaging channels
                applied_operations.append("stereo_to_mono")
        
        # Resample if needed
        if sr != options.target_sample_rate:
            y = librosa.resample(y, orig_sr=sr, target_sr=options.target_sample_rate)
            sr = options.target_sample_rate
            applied_operations.append(f"resample_to_{sr}Hz")
        
        # High-pass filter to remove low-frequency noise
        if options.high_pass_filter:
            y = self._apply_high_pass_filter(y, sr, options.high_pass_cutoff)
            applied_operations.append(f"highpass_{options.high_pass_cutoff}Hz")
        
        # Normalize audio levels
        if options.normalize:
            y = self._normalize_audio(y)
            applied_operations.append("normalize")
        
        # Noise reduction (simple spectral subtraction)
        if options.noise_reduction:
            y = self._reduce_noise(y, sr)
            applied_operations.append("noise_reduction")
        
        # Remove silence (trim quiet sections)
        if options.remove_silence:
            y = self._trim_silence(y, sr)
            applied_operations.append("trim_silence")
        
        return y, sr, applied_operations
    
    def _apply_high_pass_filter(self, y: Any, sr: int, cutoff: float) -> Any:
        """Apply high-pass filter to remove low-frequency noise"""
        if signal is None:
            logger.warning("scipy.signal not available - skipping high-pass filter")
            return y
        
        try:
            # Design high-pass filter
            nyquist = sr / 2
            normalized_cutoff = cutoff / nyquist
            b, a = signal.butter(4, normalized_cutoff, btype='high')
            
            # Apply filter
            y_filtered = signal.filtfilt(b, a, y)
            return y_filtered.astype(np.float32)
            
        except Exception as e:
            logger.warning(f"High-pass filter failed: {e}")
            return y
    
    def _normalize_audio(self, y: Any, target_level: float = 0.9) -> Any:
        """Normalize audio to target level"""
        if len(y) == 0:
            return y
        
        # Find peak level
        peak = np.max(np.abs(y))
        
        if peak > 0:
            # Scale to target level
            y_normalized = y * (target_level / peak)
            return y_normalized.astype(np.float32)
        
        return y
    
    def _reduce_noise(self, y: Any, sr: int) -> Any:
        """Simple spectral subtraction noise reduction"""
        try:
            # Estimate noise from first 0.5 seconds
            noise_duration = min(int(0.5 * sr), len(y) // 4)
            noise_sample = y[:noise_duration]
            
            # Calculate noise spectrum
            noise_fft = np.fft.rfft(noise_sample)
            noise_magnitude = np.abs(noise_fft)
            noise_power = noise_magnitude ** 2
            
            # Process in overlapping windows
            window_size = 2048
            hop_size = window_size // 2
            
            if len(y) < window_size:
                return y  # Too short for processing
            
            y_denoised = np.zeros_like(y)
            
            for i in range(0, len(y) - window_size, hop_size):
                # Extract window
                window = y[i:i + window_size]
                
                # FFT
                window_fft = np.fft.rfft(window)
                window_magnitude = np.abs(window_fft)
                window_phase = np.angle(window_fft)
                
                # Spectral subtraction
                # Ensure arrays are same size
                min_len = min(len(window_magnitude), len(noise_magnitude))
                enhanced_magnitude = window_magnitude[:min_len] - 0.5 * noise_magnitude[:min_len]
                enhanced_magnitude = np.maximum(enhanced_magnitude, 0.1 * window_magnitude[:min_len])
                
                # Reconstruct signal
                if len(enhanced_magnitude) < len(window_fft):
                    # Pad if necessary
                    enhanced_magnitude = np.pad(enhanced_magnitude, 
                                              (0, len(window_fft) - len(enhanced_magnitude)))
                
                enhanced_fft = enhanced_magnitude * np.exp(1j * window_phase)
                enhanced_window = np.fft.irfft(enhanced_fft, n=window_size)
                
                # Overlap-add
                y_denoised[i:i + window_size] += enhanced_window
            
            return y_denoised.astype(np.float32)
            
        except Exception as e:
            logger.warning(f"Noise reduction failed: {e}")
            return y
    
    def _trim_silence(self, y: Any, sr: int, 
                     threshold_db: float = -40.0) -> Any:
        """Trim silence from beginning and end"""
        try:
            # Use librosa's trim function
            y_trimmed, _ = librosa.effects.trim(y, top_db=-threshold_db)
            return y_trimmed
            
        except Exception as e:
            logger.warning(f"Silence trimming failed: {e}")
            return y
    
    def _calculate_quality_improvements(self, y_orig: Any, y_proc: Any,
                                      sr_orig: int, sr_proc: int) -> Dict[str, float]:
        """Calculate quality improvement metrics"""
        improvements = {}
        
        try:
            # Signal-to-noise ratio improvement (simplified)
            if len(y_orig) > 0 and len(y_proc) > 0:
                # Estimate SNR based on signal variance
                signal_var_orig = np.var(y_orig)
                signal_var_proc = np.var(y_proc)
                
                if signal_var_orig > 0:
                    snr_improvement = 10 * np.log10(signal_var_proc / signal_var_orig)
                    improvements['snr_improvement_db'] = float(snr_improvement)
            
            # Dynamic range improvement
            if len(y_orig) > 0 and len(y_proc) > 0:
                dynamic_range_orig = np.max(y_orig) - np.min(y_orig)
                dynamic_range_proc = np.max(y_proc) - np.min(y_proc)
                
                if dynamic_range_orig > 0:
                    dr_improvement = dynamic_range_proc / dynamic_range_orig
                    improvements['dynamic_range_ratio'] = float(dr_improvement)
            
            # Frequency response improvement (sample rate change)
            if sr_proc != sr_orig:
                improvements['frequency_range_hz'] = float(sr_proc / 2)  # Nyquist frequency
            
            # Duration change (silence removal, etc.)
            duration_orig = len(y_orig) / sr_orig if sr_orig > 0 else 0
            duration_proc = len(y_proc) / sr_proc if sr_proc > 0 else 0
            
            if duration_orig > 0:
                improvements['duration_reduction_ratio'] = float(duration_proc / duration_orig)
            
        except Exception as e:
            logger.warning(f"Quality metric calculation failed: {e}")
        
        return improvements
    
    def batch_process(self, input_paths: List[str], output_dir: str,
                     options: Optional[ProcessingOptions] = None) -> Dict[str, ProcessingResult]:
        """Process multiple audio files"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {}
        
        for input_path in input_paths:
            try:
                input_path_obj = Path(input_path)
                output_path = output_dir / f"{input_path_obj.stem}_processed.wav"
                
                result = self.process_for_transcription(input_path, str(output_path), options)
                results[input_path] = result
                
            except Exception as e:
                logger.error(f"Failed to process {input_path}: {e}")
                results[input_path] = ProcessingResult(
                    output_path="",
                    original_duration=0.0,
                    processed_duration=0.0,
                    original_sample_rate=0,
                    processed_sample_rate=0,
                    original_channels=0,
                    processed_channels=0,
                    processing_applied=[],
                    quality_improvements={'error': str(e)}
                )
        
        return results
    
    def get_optimal_processing_options(self, input_path: str) -> ProcessingOptions:
        """Recommend optimal processing options based on audio analysis"""
        if librosa is None:
            return ProcessingOptions()
        
        try:
            # Analyze input audio
            y, sr = librosa.load(input_path, sr=None, mono=False)
            
            # Default options
            options = ProcessingOptions()
            
            # Adjust based on analysis
            if sr < 16000:
                options.target_sample_rate = 16000  # Upsample for better quality
            elif sr > 48000:
                options.target_sample_rate = 16000  # Downsample to save processing
            else:
                options.target_sample_rate = sr  # Keep original if reasonable
            
            # Enable noise reduction for noisy audio
            if y.ndim == 1:
                noise_level = np.std(y[:int(0.5 * sr)]) if len(y) > int(0.5 * sr) else 0
                signal_level = np.std(y)
                
                if signal_level > 0 and noise_level / signal_level > 0.3:
                    options.noise_reduction = True
            
            # Enable silence removal for long audio
            duration = len(y) / sr if y.ndim == 1 else y.shape[1] / sr
            if duration > 300:  # 5 minutes
                options.remove_silence = True
            
            return options
            
        except Exception as e:
            logger.warning(f"Could not analyze audio for optimization: {e}")
            return ProcessingOptions()
    
    def validate_processing_result(self, result: ProcessingResult) -> Dict[str, Any]:
        """Validate processing result quality"""
        validation = {
            'is_valid': True,
            'warnings': [],
            'recommendations': []
        }
        
        # Check if file exists
        if not Path(result.output_path).exists():
            validation['is_valid'] = False
            validation['warnings'].append("Output file does not exist")
            return validation
        
        # Check duration change
        if result.processed_duration < result.original_duration * 0.5:
            validation['warnings'].append("Significant duration reduction - may have removed too much content")
        
        # Check sample rate
        if result.processed_sample_rate < 16000:
            validation['warnings'].append("Sample rate below optimal for transcription (16kHz)")
            validation['recommendations'].append("Consider upsampling to 16kHz")
        
        # Check for successful processing
        if not result.processing_applied:
            validation['warnings'].append("No processing operations were applied")
        
        # Check quality improvements
        if 'error' in result.quality_improvements:
            validation['is_valid'] = False
            validation['warnings'].append("Processing error occurred")
        
        return validation
    
    def cleanup_temp_files(self):
        """Clean up temporary processing files"""
        try:
            for temp_file in self.temp_dir.glob("*"):
                if temp_file.is_file():
                    temp_file.unlink()
            logger.info("Cleaned up temporary processing files")
        except Exception as e:
            logger.warning(f"Failed to cleanup temp files: {e}")