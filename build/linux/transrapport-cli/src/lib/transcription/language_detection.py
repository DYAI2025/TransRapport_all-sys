"""
Language Detection Service
Automatic language detection for optimal transcription setup
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

try:
    import whisper
    import librosa
    import numpy as np
except ImportError:
    whisper = None
    librosa = None
    np = None

logger = logging.getLogger(__name__)


class LanguageDetection:
    """
    Automatic language detection for audio files
    Uses Whisper's built-in language detection capabilities
    """
    
    COMMON_LANGUAGES = {
        'en': 'English',
        'de': 'German', 
        'es': 'Spanish',
        'fr': 'French',
        'it': 'Italian',
        'pt': 'Portuguese',
        'nl': 'Dutch',
        'ru': 'Russian',
        'zh': 'Chinese',
        'ja': 'Japanese',
        'ko': 'Korean'
    }
    
    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self.model = None
        self.model_loaded = False
        
        logger.info(f"Language detection initialized with {model_size} model")
    
    def _load_model(self):
        """Load Whisper model for language detection"""
        if self.model_loaded:
            return
        
        if whisper is None:
            logger.warning("Whisper not available - using mock language detection")
            self.model_loaded = True
            return
        
        try:
            logger.info(f"Loading Whisper model for language detection: {self.model_size}")
            self.model = whisper.load_model(self.model_size)
            self.model_loaded = True
            logger.info("Language detection model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load language detection model: {e}")
            self.model = None
            self.model_loaded = True
    
    def detect_language(self, audio_file: str, sample_duration: float = 30.0) -> Dict[str, Any]:
        """
        Detect language from audio file
        
        Args:
            audio_file: Path to audio file
            sample_duration: Duration of audio sample to analyze (seconds)
            
        Returns:
            Language detection result with confidence and alternatives
        """
        if not Path(audio_file).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file}")
        
        self._load_model()
        
        if self.model is None:
            # Mock detection for testing
            return self._mock_language_detection(audio_file)
        
        try:
            logger.info(f"Detecting language: {audio_file}")
            
            # Load audio sample
            audio = whisper.load_audio(audio_file)
            
            # Use first N seconds for detection
            if len(audio) > int(sample_duration * whisper.audio.SAMPLE_RATE):
                audio = audio[:int(sample_duration * whisper.audio.SAMPLE_RATE)]
            
            # Pad or trim to 30 seconds for Whisper
            audio = whisper.pad_or_trim(audio)
            
            # Generate mel spectrogram
            mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
            
            # Detect language
            _, probs = self.model.detect_language(mel)
            
            # Sort languages by probability
            language_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
            
            detected_language = language_probs[0][0]
            confidence = language_probs[0][1]
            
            # Get top alternatives
            alternatives = [
                {
                    'language': lang,
                    'confidence': float(prob),
                    'language_name': self.COMMON_LANGUAGES.get(lang, lang.upper())
                }
                for lang, prob in language_probs[1:6]  # Top 5 alternatives
            ]
            
            result = {
                'language': detected_language,
                'confidence': float(confidence),
                'language_name': self.COMMON_LANGUAGES.get(detected_language, detected_language.upper()),
                'alternatives': alternatives,
                'sample_duration': sample_duration
            }
            
            logger.info(f"Language detected: {detected_language} (confidence: {confidence:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            raise RuntimeError(f"Language detection failed: {e}")
    
    def _mock_language_detection(self, audio_file: str) -> Dict[str, Any]:
        """Mock language detection for testing"""
        # Simple filename-based detection for testing
        filename = Path(audio_file).stem.lower()
        
        if any(word in filename for word in ['german', 'deutsch', 'de']):
            detected_lang = 'de'
        elif any(word in filename for word in ['spanish', 'espanol', 'es']):
            detected_lang = 'es'
        elif any(word in filename for word in ['french', 'francais', 'fr']):
            detected_lang = 'fr'
        else:
            detected_lang = 'en'  # Default to English
        
        return {
            'language': detected_lang,
            'confidence': 0.85,
            'language_name': self.COMMON_LANGUAGES.get(detected_lang, 'English'),
            'alternatives': [
                {'language': 'en', 'confidence': 0.15, 'language_name': 'English'},
                {'language': 'de', 'confidence': 0.10, 'language_name': 'German'}
            ],
            'sample_duration': 30.0
        }
    
    def batch_detect_languages(self, audio_files: List[str]) -> Dict[str, Dict[str, Any]]:
        """Detect languages for multiple audio files"""
        results = {}
        
        for audio_file in audio_files:
            try:
                results[audio_file] = self.detect_language(audio_file)
            except Exception as e:
                logger.error(f"Failed to detect language for {audio_file}: {e}")
                results[audio_file] = {
                    'language': 'unknown',
                    'confidence': 0.0,
                    'language_name': 'Unknown',
                    'alternatives': [],
                    'error': str(e)
                }
        
        return results
    
    def validate_language_support(self, language_code: str) -> Dict[str, Any]:
        """Validate if language is supported by Whisper"""
        # Whisper supported languages (major ones)
        supported_languages = {
            'af', 'am', 'ar', 'as', 'az', 'ba', 'be', 'bg', 'bn', 'bo', 'br', 'bs',
            'ca', 'cs', 'cy', 'da', 'de', 'el', 'en', 'es', 'et', 'eu', 'fa', 'fi',
            'fo', 'fr', 'gl', 'gu', 'ha', 'haw', 'he', 'hi', 'hr', 'ht', 'hu', 'hy',
            'id', 'is', 'it', 'ja', 'jw', 'ka', 'kk', 'km', 'kn', 'ko', 'la', 'lb',
            'ln', 'lo', 'lt', 'lv', 'mg', 'mi', 'mk', 'ml', 'mn', 'mr', 'ms', 'mt',
            'my', 'ne', 'nl', 'nn', 'no', 'oc', 'pa', 'pl', 'ps', 'pt', 'ro', 'ru',
            'sa', 'sd', 'si', 'sk', 'sl', 'sn', 'so', 'sq', 'sr', 'su', 'sv', 'sw',
            'ta', 'te', 'tg', 'th', 'tk', 'tl', 'tr', 'tt', 'uk', 'ur', 'uz', 'vi',
            'yi', 'yo', 'yue', 'zh'
        }
        
        is_supported = language_code in supported_languages
        
        return {
            'language_code': language_code,
            'is_supported': is_supported,
            'language_name': self.COMMON_LANGUAGES.get(language_code, language_code.upper()),
            'transcription_quality': 'high' if language_code in ['en', 'de', 'es', 'fr'] else 'medium' if is_supported else 'unsupported'
        }
    
    def get_language_recommendations(self, detected_results: Dict[str, Any]) -> Dict[str, Any]:
        """Get recommendations based on detected language"""
        language = detected_results['language']
        confidence = detected_results['confidence']
        
        recommendations = {
            'use_detected_language': confidence >= 0.7,
            'suggested_action': '',
            'alternative_options': [],
            'quality_expectations': {}
        }
        
        if confidence >= 0.9:
            recommendations['suggested_action'] = f"High confidence detection - use {language}"
            recommendations['quality_expectations'] = {
                'transcription_accuracy': 'high',
                'processing_speed': 'optimal'
            }
        elif confidence >= 0.7:
            recommendations['suggested_action'] = f"Good confidence - use {language} but verify"
            recommendations['quality_expectations'] = {
                'transcription_accuracy': 'good',
                'processing_speed': 'good'
            }
            recommendations['alternative_options'] = [
                alt['language'] for alt in detected_results['alternatives'][:2]
            ]
        elif confidence >= 0.5:
            recommendations['suggested_action'] = "Low confidence - consider manual language selection"
            recommendations['quality_expectations'] = {
                'transcription_accuracy': 'uncertain',
                'processing_speed': 'may be slow'
            }
            recommendations['alternative_options'] = [
                alt['language'] for alt in detected_results['alternatives'][:3]
            ]
        else:
            recommendations['suggested_action'] = "Very low confidence - recommend manual selection"
            recommendations['use_detected_language'] = False
            recommendations['quality_expectations'] = {
                'transcription_accuracy': 'poor if wrong language',
                'processing_speed': 'may be very slow'
            }
        
        return recommendations
    
    def get_supported_languages_list(self) -> List[Dict[str, str]]:
        """Get list of all supported languages with names"""
        return [
            {'code': code, 'name': name}
            for code, name in self.COMMON_LANGUAGES.items()
        ]
    
    def cleanup(self):
        """Cleanup resources"""
        if self.model is not None:
            del self.model
            self.model = None
        
        logger.info("Language detection cleanup completed")
    
    def __del__(self):
        """Destructor cleanup"""
        self.cleanup()