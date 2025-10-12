# ==============================================================================
# app/multimodal/audio.py
# Audio Transcription System - The Voice Intelligence
# ==============================================================================
"""
This module provides audio transcription capabilities using multiple services.
Includes Whisper (free), Google Speech-to-Text, and AssemblyAI with intelligent failover.
"""

import os
import io
import logging
import tempfile
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from dataclasses import dataclass
import base64

# Audio processing imports
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    from google.cloud import speech
    GOOGLE_SPEECH_AVAILABLE = True
except ImportError:
    GOOGLE_SPEECH_AVAILABLE = False

try:
    import assemblyai as aai
    ASSEMBLYAI_AVAILABLE = True
except ImportError:
    ASSEMBLYAI_AVAILABLE = False

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

from config import Config

logger = logging.getLogger(__name__)

# ==============================================================================
# DATA STRUCTURES
# ==============================================================================

@dataclass
class TranscriptionResult:
    """Result of audio transcription."""
    text: str
    confidence: float
    language: str
    duration: float
    service_used: str
    metadata: Dict[str, Any]
    segments: Optional[List[Dict[str, Any]]] = None

@dataclass
class AudioInfo:
    """Audio file information."""
    duration: float
    sample_rate: int
    channels: int
    format: str
    size_bytes: int

# ==============================================================================
# BASE TRANSCRIBER CLASS
# ==============================================================================

class BaseTranscriber(ABC):
    """Base class for all transcription services."""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    def transcribe(self, audio_data: bytes, metadata: Dict[str, Any] = None) -> TranscriptionResult:
        """
        Transcribe audio data to text.
        
        Args:
            audio_data: Raw audio bytes
            metadata: Additional metadata
            
        Returns:
            TranscriptionResult
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the service is available."""
        pass
    
    def get_audio_info(self, audio_data: bytes) -> AudioInfo:
        """Get information about audio data."""
        if not PYDUB_AVAILABLE:
            return AudioInfo(0, 0, 0, "unknown", len(audio_data))
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file.flush()
                
                # Load audio
                audio = AudioSegment.from_file(temp_file.name)
                
                return AudioInfo(
                    duration=len(audio) / 1000.0,  # Convert to seconds
                    sample_rate=audio.frame_rate,
                    channels=audio.channels,
                    format=audio.frame_rate,
                    size_bytes=len(audio_data)
                )
        except Exception as e:
            self.logger.error(f"Failed to get audio info: {e}")
            return AudioInfo(0, 0, 0, "unknown", len(audio_data))
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file.name)
            except:
                pass

# ==============================================================================
# WHISPER TRANSCRIBER (FREE)
# ==============================================================================

class WhisperTranscriber(BaseTranscriber):
    """
    OpenAI Whisper transcriber - Free, local processing.
    Best for: Free tier users, privacy-conscious users, offline processing.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("whisper", config)
        self.model_size = self.config.get('model_size', 'base')
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load Whisper model."""
        if not WHISPER_AVAILABLE:
            self.logger.warning("Whisper not available - install openai-whisper")
            return
        
        try:
            self.model = whisper.load_model(self.model_size)
            self.logger.info(f"Loaded Whisper model: {self.model_size}")
        except Exception as e:
            self.logger.error(f"Failed to load Whisper model: {e}")
            self.model = None
    
    def is_available(self) -> bool:
        """Check if Whisper is available."""
        return WHISPER_AVAILABLE and self.model is not None
    
    def transcribe(self, audio_data: bytes, metadata: Dict[str, Any] = None) -> TranscriptionResult:
        """Transcribe audio using Whisper."""
        if not self.is_available():
            raise RuntimeError("Whisper is not available")
        
        metadata = metadata or {}
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file.flush()
                
                # Transcribe
                result = self.model.transcribe(
                    temp_file.name,
                    language=metadata.get('language'),
                    task=metadata.get('task', 'transcribe')
                )
                
                # Extract segments if available
                segments = []
                if hasattr(result, 'segments'):
                    for segment in result.segments:
                        segments.append({
                            'start': segment.get('start', 0),
                            'end': segment.get('end', 0),
                            'text': segment.get('text', ''),
                            'confidence': segment.get('no_speech_prob', 0)
                        })
                
                return TranscriptionResult(
                    text=result.get('text', ''),
                    confidence=1.0 - result.get('no_speech_prob', 0.1),
                    language=result.get('language', 'unknown'),
                    duration=metadata.get('duration', 0),
                    service_used=self.name,
                    metadata={
                        'model_size': self.model_size,
                        'no_speech_prob': result.get('no_speech_prob', 0)
                    },
                    segments=segments
                )
        
        except Exception as e:
            self.logger.error(f"Whisper transcription failed: {e}")
            raise
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file.name)
            except:
                pass

# ==============================================================================
# GOOGLE SPEECH TRANSCRIBER (PAID)
# ==============================================================================

class GoogleSpeechTranscriber(BaseTranscriber):
    """
    Google Cloud Speech-to-Text transcriber - Paid, high accuracy.
    Best for: Pro/Enterprise users, high accuracy requirements, multiple languages.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("google_speech", config)
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Google Speech client."""
        if not GOOGLE_SPEECH_AVAILABLE:
            self.logger.warning("Google Speech not available - install google-cloud-speech")
            return
        
        if not Config.GOOGLE_SPEECH_API_KEY:
            self.logger.warning("Google Speech API key not configured")
            return
        
        try:
            # Set credentials
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = Config.GOOGLE_SPEECH_API_KEY
            self.client = speech.SpeechClient()
            self.logger.info("Initialized Google Speech client")
        except Exception as e:
            self.logger.error(f"Failed to initialize Google Speech client: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Google Speech is available."""
        return GOOGLE_SPEECH_AVAILABLE and self.client is not None
    
    def transcribe(self, audio_data: bytes, metadata: Dict[str, Any] = None) -> TranscriptionResult:
        """Transcribe audio using Google Speech-to-Text."""
        if not self.is_available():
            raise RuntimeError("Google Speech is not available")
        
        metadata = metadata or {}
        
        try:
            # Configure audio
            audio = speech.RecognitionAudio(content=audio_data)
            
            # Configure recognition
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=metadata.get('sample_rate', 16000),
                language_code=metadata.get('language', 'en-US'),
                enable_automatic_punctuation=True,
                enable_word_time_offsets=True,
                model='latest_long' if metadata.get('long_audio', False) else 'latest_short'
            )
            
            # Perform transcription
            response = self.client.recognize(config=config, audio=audio)
            
            # Process results
            text_parts = []
            segments = []
            total_confidence = 0
            
            for result in response.results:
                alternative = result.alternatives[0]
                text_parts.append(alternative.transcript)
                total_confidence += alternative.confidence
                
                # Extract word-level timing
                if hasattr(alternative, 'words'):
                    for word in alternative.words:
                        segments.append({
                            'start': word.start_time.total_seconds(),
                            'end': word.end_time.total_seconds(),
                            'text': word.word,
                            'confidence': alternative.confidence
                        })
            
            return TranscriptionResult(
                text=' '.join(text_parts),
                confidence=total_confidence / len(response.results) if response.results else 0,
                language=config.language_code,
                duration=metadata.get('duration', 0),
                service_used=self.name,
                metadata={
                    'results_count': len(response.results),
                    'model': config.model
                },
                segments=segments
            )
        
        except Exception as e:
            self.logger.error(f"Google Speech transcription failed: {e}")
            raise

# ==============================================================================
# ASSEMBLYAI TRANSCRIBER (PAID)
# ==============================================================================

class AssemblyAITranscriber(BaseTranscriber):
    """
    AssemblyAI transcriber - Paid, specialized features.
    Best for: Enterprise users, specialized audio types, advanced features.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("assemblyai", config)
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize AssemblyAI client."""
        if not ASSEMBLYAI_AVAILABLE:
            self.logger.warning("AssemblyAI not available - install assemblyai")
            return
        
        if not Config.ASSEMBLYAI_API_KEY:
            self.logger.warning("AssemblyAI API key not configured")
            return
        
        try:
            aai.settings.api_key = Config.ASSEMBLYAI_API_KEY
            self.client = aai.Transcriber()
            self.logger.info("Initialized AssemblyAI client")
        except Exception as e:
            self.logger.error(f"Failed to initialize AssemblyAI client: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if AssemblyAI is available."""
        return ASSEMBLYAI_AVAILABLE and self.client is not None
    
    def transcribe(self, audio_data: bytes, metadata: Dict[str, Any] = None) -> TranscriptionResult:
        """Transcribe audio using AssemblyAI."""
        if not self.is_available():
            raise RuntimeError("AssemblyAI is not available")
        
        metadata = metadata or {}
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file.flush()
                
                # Configure transcription
                config = aai.TranscriptionConfig(
                    language_code=metadata.get('language', 'en'),
                    punctuate=True,
                    format_text=True,
                    speaker_labels=metadata.get('speaker_labels', False),
                    sentiment_analysis=metadata.get('sentiment_analysis', False),
                    entity_detection=metadata.get('entity_detection', False)
                )
                
                # Transcribe
                transcript = self.client.transcribe(temp_file.name, config=config)
                
                # Wait for completion
                while transcript.status not in [aai.TranscriptStatus.completed, aai.TranscriptStatus.error]:
                    transcript = self.client.get_transcript(transcript.id)
                
                if transcript.status == aai.TranscriptStatus.error:
                    raise RuntimeError(f"AssemblyAI transcription failed: {transcript.error}")
                
                # Extract segments
                segments = []
                if hasattr(transcript, 'utterances'):
                    for utterance in transcript.utterances:
                        segments.append({
                            'start': utterance.start / 1000.0,  # Convert to seconds
                            'end': utterance.end / 1000.0,
                            'text': utterance.text,
                            'confidence': utterance.confidence,
                            'speaker': utterance.speaker
                        })
                
                return TranscriptionResult(
                    text=transcript.text,
                    confidence=transcript.confidence,
                    language=config.language_code,
                    duration=metadata.get('duration', 0),
                    service_used=self.name,
                    metadata={
                        'transcript_id': transcript.id,
                        'sentiment': getattr(transcript, 'sentiment_analysis_results', None),
                        'entities': getattr(transcript, 'entities', None)
                    },
                    segments=segments
                )
        
        except Exception as e:
            self.logger.error(f"AssemblyAI transcription failed: {e}")
            raise
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file.name)
            except:
                pass

# ==============================================================================
# AUDIO ORCHESTRATOR
# ==============================================================================

class AudioOrchestrator:
    """
    Orchestrates different transcription services with intelligent selection.
    Handles failover, tier-based access, and service optimization.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize transcriber services
        self.transcribers = {
            'whisper': WhisperTranscriber(self.config.get('whisper', {})),
            'google_speech': GoogleSpeechTranscriber(self.config.get('google_speech', {})),
            'assemblyai': AssemblyAITranscriber(self.config.get('assemblyai', {}))
        }
        
        # Service priority order (best to worst)
        self.service_priority = ['assemblyai', 'google_speech', 'whisper']
    
    def transcribe(self, audio_data: bytes, user_tier: str = 'free', 
                   metadata: Dict[str, Any] = None) -> TranscriptionResult:
        """
        Transcribe audio using the best available service for the user's tier.
        
        Args:
            audio_data: Raw audio bytes
            user_tier: User's subscription tier
            metadata: Additional metadata
            
        Returns:
            TranscriptionResult
        """
        metadata = metadata or {}
        
        # Get available services for user tier
        available_services = self._get_available_services(user_tier)
        
        if not available_services:
            raise RuntimeError("No transcription services available for your tier")
        
        # Try services in priority order
        last_error = None
        
        for service_name in available_services:
            if service_name not in self.transcribers:
                continue
            
            transcriber = self.transcribers[service_name]
            
            if not transcriber.is_available():
                self.logger.warning(f"Service {service_name} is not available")
                continue
            
            try:
                self.logger.info(f"Attempting transcription with {service_name}")
                result = transcriber.transcribe(audio_data, metadata)
                
                # Add orchestration metadata
                result.metadata['orchestration'] = {
                    'services_tried': [service_name],
                    'user_tier': user_tier,
                    'selected_service': service_name
                }
                
                return result
            
            except Exception as e:
                self.logger.error(f"Transcription failed with {service_name}: {e}")
                last_error = e
                continue
        
        # All services failed
        raise RuntimeError(f"All transcription services failed. Last error: {last_error}")
    
    def _get_available_services(self, user_tier: str) -> List[str]:
        """Get list of available services for user tier."""
        from app.tiers import get_available_services
        
        available_services = get_available_services(user_tier, 'audio_transcription')
        
        if not available_services:
            return []
        
        if 'all' in available_services:
            # All services available
            return self.service_priority
        
        # Filter by available services
        tier_services = []
        for service in self.service_priority:
            if service in available_services or service == 'whisper':  # Whisper always available
                tier_services.append(service)
        
        return tier_services
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about available services."""
        info = {}
        
        for name, transcriber in self.transcribers.items():
            info[name] = {
                'available': transcriber.is_available(),
                'name': transcriber.name,
                'config': transcriber.config
            }
        
        return info
    
    def get_audio_info(self, audio_data: bytes) -> AudioInfo:
        """Get information about audio data."""
        # Use Whisper transcriber for audio info (it has the most comprehensive support)
        if 'whisper' in self.transcribers:
            return self.transcribers['whisper'].get_audio_info(audio_data)
        else:
            return AudioInfo(0, 0, 0, "unknown", len(audio_data))

# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def convert_audio_format(audio_data: bytes, target_format: str = 'wav') -> bytes:
    """
    Convert audio data to target format.
    
    Args:
        audio_data: Raw audio bytes
        target_format: Target format (wav, mp3, etc.)
        
    Returns:
        Converted audio bytes
    """
    if not PYDUB_AVAILABLE:
        return audio_data
    
    try:
        # Create temporary input file
        with tempfile.NamedTemporaryFile(suffix='.tmp', delete=False) as input_file:
            input_file.write(audio_data)
            input_file.flush()
            
            # Load and convert
            audio = AudioSegment.from_file(input_file.name)
            
            # Create temporary output file
            with tempfile.NamedTemporaryFile(suffix=f'.{target_format}', delete=False) as output_file:
                audio.export(output_file.name, format=target_format)
                
                # Read converted data
                with open(output_file.name, 'rb') as f:
                    converted_data = f.read()
                
                # Clean up
                os.unlink(output_file.name)
                os.unlink(input_file.name)
                
                return converted_data
    
    except Exception as e:
        logger.error(f"Audio conversion failed: {e}")
        return audio_data

def detect_audio_language(audio_data: bytes) -> str:
    """
    Detect the language of audio data.
    
    Args:
        audio_data: Raw audio bytes
        
    Returns:
        Detected language code
    """
    # This is a simplified implementation
    # In practice, you might use a language detection service
    
    # For now, return a default
    return 'en'

def validate_audio_data(audio_data: bytes) -> Dict[str, Any]:
    """
    Validate audio data and return information.
    
    Args:
        audio_data: Raw audio bytes
        
    Returns:
        Validation result with audio info
    """
    if not audio_data:
        return {'valid': False, 'error': 'No audio data provided'}
    
    if len(audio_data) < 1000:  # Less than 1KB
        return {'valid': False, 'error': 'Audio data too small'}
    
    # Get audio info
    orchestrator = AudioOrchestrator()
    audio_info = orchestrator.get_audio_info(audio_data)
    
    return {
        'valid': True,
        'audio_info': audio_info,
        'size_bytes': len(audio_data)
    }

