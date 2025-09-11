"""
TransRapport Prosody and Emotion Analysis
Enhanced audio processing with prosodic features and emotion detection
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import parselmouth
from parselmouth.praat import call
import librosa
import opensmile
from pyAudioAnalysis import audioFeatureExtraction as aF
from pyAudioAnalysis import audioBasicIO
import soundfile as sf

logger = logging.getLogger(__name__)

class ProsodyAnalyzer:
    """
    Advanced prosody analysis using multiple tools:
    - Praat (via parselmouth) for acoustic features
    - OpenSMILE for emotion recognition
    - pyAudioAnalysis for feature extraction
    """

    def __init__(self):
        self.smile = None
        self._initialize_opensmile()

    def _initialize_opensmile(self):
        """Initialize OpenSMILE for emotion analysis"""
        try:
            # Use eGeMAPS feature set for emotion recognition
            self.smile = opensmile.Smile(
                feature_set=opensmile.FeatureSet.eGeMAPSv02,
                feature_level=opensmile.FeatureLevel.Functionals,
            )
            logger.info("OpenSMILE initialized with eGeMAPS feature set")
        except Exception as e:
            logger.warning(f"OpenSMILE initialization failed: {e}")
            self.smile = None

    def analyze_audio_file(self, audio_file: str) -> Dict[str, Any]:
        """
        Comprehensive audio analysis including prosody and emotion

        Args:
            audio_file: Path to WAV file

        Returns:
            Dictionary with prosodic and emotional features
        """
        try:
            # Load audio
            audio_data, sample_rate = sf.read(audio_file)

            # Ensure mono
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)

            results = {
                'file_info': {
                    'path': audio_file,
                    'duration': len(audio_data) / sample_rate,
                    'sample_rate': sample_rate,
                    'channels': 1
                },
                'prosody': {},
                'emotion': {},
                'features': {}
            }

            # Praat-based prosody analysis
            results['prosody'] = self._analyze_prosody_praat(audio_file)

            # OpenSMILE emotion analysis
            if self.smile:
                results['emotion'] = self._analyze_emotion_opensmile(audio_file)

            # pyAudioAnalysis feature extraction
            results['features'] = self._extract_audio_features(audio_data, sample_rate)

            return results

        except Exception as e:
            logger.error(f"Audio analysis failed for {audio_file}: {e}")
            return {'error': str(e)}

    def _analyze_prosody_praat(self, audio_file: str) -> Dict[str, Any]:
        """Analyze prosody using Praat (via parselmouth)"""
        try:
            # Load sound
            sound = parselmouth.Sound(audio_file)

            # Pitch analysis
            pitch = call(sound, "To Pitch", 0.0, 75, 600)
            pitch_values = pitch.selected_array['frequency']
            pitch_values = pitch_values[pitch_values != 0]  # Remove unvoiced frames

            # Intensity analysis
            intensity = call(sound, "To Intensity", 100, 0.0, True)
            intensity_values = intensity.values[0]

            # Voice quality measures
            harmonicity = call(sound, "To Harmonicity (cc)", 0.01, 75, 0.1, 1.0)
            hnr_values = harmonicity.values[0]

            # Spectral analysis
            spectrum = call(sound, "To Spectrum", "fft")
            spectral_centroid = call(spectrum, "Get centroid", 0, 0)
            spectral_spread = call(spectrum, "Get spread", 0, 0)

            return {
                'pitch': {
                    'mean': float(np.mean(pitch_values)) if len(pitch_values) > 0 else 0,
                    'std': float(np.std(pitch_values)) if len(pitch_values) > 0 else 0,
                    'min': float(np.min(pitch_values)) if len(pitch_values) > 0 else 0,
                    'max': float(np.max(pitch_values)) if len(pitch_values) > 0 else 0,
                    'range': float(np.ptp(pitch_values)) if len(pitch_values) > 0 else 0
                },
                'intensity': {
                    'mean': float(np.mean(intensity_values)),
                    'std': float(np.std(intensity_values)),
                    'min': float(np.min(intensity_values)),
                    'max': float(np.max(intensity_values))
                },
                'voice_quality': {
                    'hnr_mean': float(np.mean(hnr_values)),
                    'hnr_std': float(np.std(hnr_values))
                },
                'spectral': {
                    'centroid': float(spectral_centroid),
                    'spread': float(spectral_spread)
                }
            }

        except Exception as e:
            logger.warning(f"Praat prosody analysis failed: {e}")
            return {'error': str(e)}

    def _analyze_emotion_opensmile(self, audio_file: str) -> Dict[str, Any]:
        """Analyze emotion using OpenSMILE"""
        try:
            if not self.smile:
                return {'error': 'OpenSMILE not initialized'}

            # Extract features
            features = self.smile.process_file(audio_file)

            # Map features to emotion dimensions
            emotion_features = {}

            # Extract relevant emotion features
            feature_names = features.columns.tolist()

            # Arousal indicators
            arousal_features = [f for f in feature_names if any(x in f.lower() for x in ['loudness', 'intensity', 'energy'])]
            if arousal_features:
                emotion_features['arousal'] = float(features[arousal_features].mean().mean())

            # Valence indicators
            valence_features = [f for f in feature_names if any(x in f.lower() for x in ['f0', 'pitch', 'slope'])]
            if valence_features:
                emotion_features['valence'] = float(features[valence_features].mean().mean())

            # Dominance indicators
            dominance_features = [f for f in feature_names if any(x in f.lower() for x in ['strength', 'power'])]
            if dominance_features:
                emotion_features['dominance'] = float(features[dominance_features].mean().mean())

            return emotion_features

        except Exception as e:
            logger.warning(f"OpenSMILE emotion analysis failed: {e}")
            return {'error': str(e)}

    def _extract_audio_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Extract comprehensive audio features using pyAudioAnalysis"""
        try:
            # Extract short-term features
            features, feature_names = aF.stFeatureExtraction(
                audio_data, sample_rate, 0.050 * sample_rate, 0.025 * sample_rate
            )

            # Calculate statistics for each feature
            feature_stats = {}
            for i, name in enumerate(feature_names):
                if len(features[i]) > 0:
                    feature_stats[name] = {
                        'mean': float(np.mean(features[i])),
                        'std': float(np.std(features[i])),
                        'min': float(np.min(features[i])),
                        'max': float(np.max(features[i])),
                        'median': float(np.median(features[i]))
                    }

            # Additional spectral features using librosa
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)[0]
            zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_data)[0]

            return {
                'pyaudioanalysis': feature_stats,
                'librosa': {
                    'spectral_centroid_mean': float(np.mean(spectral_centroids)),
                    'spectral_rolloff_mean': float(np.mean(spectral_rolloff)),
                    'zero_crossing_rate_mean': float(np.mean(zero_crossing_rate)),
                    'rms_energy': float(np.sqrt(np.mean(audio_data**2)))
                }
            }

        except Exception as e:
            logger.warning(f"Audio feature extraction failed: {e}")
            return {'error': str(e)}

    def detect_speech_segments(self, audio_file: str, threshold: float = 0.5) -> List[Tuple[float, float]]:
        """
        Detect speech segments in audio file

        Args:
            audio_file: Path to audio file
            threshold: Energy threshold for speech detection

        Returns:
            List of (start_time, end_time) tuples for speech segments
        """
        try:
            # Load audio
            audio_data, sample_rate = sf.read(audio_file)

            # Ensure mono
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)

            # Simple energy-based speech detection
            frame_length = int(0.025 * sample_rate)  # 25ms frames
            hop_length = int(0.010 * sample_rate)     # 10ms hop

            energy = librosa.feature.rms(y=audio_data, frame_length=frame_length, hop_length=hop_length)[0]

            # Find segments above threshold
            speech_frames = energy > threshold
            speech_segments = []

            start_frame = None
            for i, is_speech in enumerate(speech_frames):
                if is_speech and start_frame is None:
                    start_frame = i
                elif not is_speech and start_frame is not None:
                    start_time = start_frame * hop_length / sample_rate
                    end_time = i * hop_length / sample_rate
                    if end_time - start_time > 0.1:  # Minimum 100ms
                        speech_segments.append((start_time, end_time))
                    start_frame = None

            # Handle case where speech continues to end
            if start_frame is not None:
                start_time = start_frame * hop_length / sample_rate
                end_time = len(audio_data) / sample_rate
                if end_time - start_time > 0.1:
                    speech_segments.append((start_time, end_time))

            return speech_segments

        except Exception as e:
            logger.error(f"Speech segment detection failed: {e}")
            return []

    def analyze_emotion_dimensions(self, prosody_features: Dict[str, Any]) -> Dict[str, str]:
        """
        Classify emotion based on prosodic features

        Args:
            prosody_features: Dictionary with prosodic measurements

        Returns:
            Dictionary with emotion classifications
        """
        try:
            # Simple rule-based emotion classification
            pitch_mean = prosody_features.get('pitch', {}).get('mean', 0)
            pitch_std = prosody_features.get('pitch', {}).get('std', 0)
            intensity_mean = prosody_features.get('intensity', {}).get('mean', 0)
            intensity_std = prosody_features.get('intensity', {}).get('std', 0)

            # Arousal: High pitch variation + high intensity variation
            arousal = "high" if pitch_std > 50 and intensity_std > 5 else "low"

            # Valence: High pitch = positive, low pitch = negative
            if pitch_mean > 200:
                valence = "positive"
            elif pitch_mean < 120:
                valence = "negative"
            else:
                valence = "neutral"

            # Dominance: High intensity + stable pitch = dominant
            dominance = "high" if intensity_mean > 60 and pitch_std < 30 else "low"

            return {
                'arousal': arousal,
                'valence': valence,
                'dominance': dominance,
                'overall_emotion': self._classify_overall_emotion(arousal, valence, dominance)
            }

        except Exception as e:
            logger.warning(f"Emotion classification failed: {e}")
            return {'error': str(e)}

    def _classify_overall_emotion(self, arousal: str, valence: str, dominance: str) -> str:
        """Classify overall emotion from dimensions"""
        if arousal == "high" and valence == "positive" and dominance == "high":
            return "excited"
        elif arousal == "high" and valence == "negative" and dominance == "low":
            return "angry"
        elif arousal == "low" and valence == "negative" and dominance == "low":
            return "sad"
        elif arousal == "low" and valence == "positive" and dominance == "high":
            return "calm"
        elif arousal == "high" and valence == "neutral" and dominance == "high":
            return "confident"
        else:
            return "neutral"

# Utility functions
def analyze_audio_prosody(audio_file: str) -> Dict[str, Any]:
    """
    Convenience function for complete audio prosody analysis

    Args:
        audio_file: Path to audio file

    Returns:
        Complete analysis results
    """
    analyzer = ProsodyAnalyzer()
    results = analyzer.analyze_audio_file(audio_file)

    if 'prosody' in results and 'error' not in results['prosody']:
        results['emotion_classification'] = analyzer.analyze_emotion_dimensions(results['prosody'])

    return results

if __name__ == "__main__":
    # Example usage
    analyzer = ProsodyAnalyzer()
    print("Prosody analyzer initialized with tools:")
    print("- Praat (via parselmouth)")
    print("- OpenSMILE (eGeMAPS)")
    print("- pyAudioAnalysis")
    print("- Librosa")
