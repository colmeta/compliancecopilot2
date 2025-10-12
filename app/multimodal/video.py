# ==============================================================================
# app/multimodal/video.py
# Video Processing System - The Visual Intelligence
# ==============================================================================
"""
This module provides video processing capabilities including frame extraction,
audio transcription, scene detection, and content analysis.
"""

import os
import io
import logging
import tempfile
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
import base64

# Video processing imports
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

try:
    from moviepy.editor import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

try:
    from scenedetect import VideoManager, SceneManager
    from scenedetect.detectors import ContentDetector
    SCENEDETECT_AVAILABLE = True
except ImportError:
    SCENEDETECT_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

from .audio import AudioOrchestrator
from .vision import VisionOrchestrator
from config import Config

logger = logging.getLogger(__name__)

# ==============================================================================
# DATA STRUCTURES
# ==============================================================================

@dataclass
class VideoInfo:
    """Video file information."""
    duration: float
    fps: float
    width: int
    height: int
    format: str
    size_bytes: int
    has_audio: bool
    has_video: bool

@dataclass
class VideoFrame:
    """Extracted video frame."""
    frame_number: int
    timestamp: float
    image_data: bytes
    confidence: float
    scene_id: Optional[int] = None

@dataclass
class SceneInfo:
    """Video scene information."""
    scene_id: int
    start_time: float
    end_time: float
    duration: float
    key_frame: Optional[VideoFrame] = None
    description: Optional[str] = None

@dataclass
class VideoAnalysisResult:
    """Result of video analysis."""
    video_info: VideoInfo
    scenes: List[SceneInfo]
    key_frames: List[VideoFrame]
    audio_transcription: Optional[str] = None
    visual_text: Optional[str] = None
    metadata: Dict[str, Any] = None

# ==============================================================================
# VIDEO PROCESSOR
# ==============================================================================

class VideoProcessor:
    """
    Main video processing class that handles frame extraction, scene detection,
    and content analysis.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize sub-processors
        self.audio_orchestrator = AudioOrchestrator(self.config.get('audio', {}))
        self.vision_orchestrator = VisionOrchestrator(self.config.get('vision', {}))
        
        # Configuration
        self.max_frames = self.config.get('max_frames', 50)
        self.scene_threshold = self.config.get('scene_threshold', 30.0)
        self.frame_quality = self.config.get('frame_quality', 0.8)
    
    def process_video(self, video_data: bytes, user_tier: str = 'free', 
                     metadata: Dict[str, Any] = None) -> VideoAnalysisResult:
        """
        Process video and extract key information.
        
        Args:
            video_data: Raw video bytes
            user_tier: User's subscription tier
            metadata: Additional metadata
            
        Returns:
            VideoAnalysisResult
        """
        metadata = metadata or {}
        
        try:
            # Get video information
            video_info = self._get_video_info(video_data)
            
            # Extract key frames
            key_frames = self._extract_key_frames(video_data, video_info)
            
            # Detect scenes
            scenes = self._detect_scenes(video_data, video_info)
            
            # Extract audio and transcribe
            audio_transcription = self._extract_and_transcribe_audio(
                video_data, user_tier, metadata
            )
            
            # Extract visual text from key frames
            visual_text = self._extract_visual_text(key_frames, user_tier, metadata)
            
            return VideoAnalysisResult(
                video_info=video_info,
                scenes=scenes,
                key_frames=key_frames,
                audio_transcription=audio_transcription,
                visual_text=visual_text,
                metadata={
                    'processing_config': self.config,
                    'user_tier': user_tier,
                    **metadata
                }
            )
        
        except Exception as e:
            self.logger.error(f"Video processing failed: {e}")
            raise
    
    def _get_video_info(self, video_data: bytes) -> VideoInfo:
        """Get information about the video."""
        if not MOVIEPY_AVAILABLE:
            raise RuntimeError("MoviePy not available - install moviepy")
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                temp_file.write(video_data)
                temp_file.flush()
                
                # Load video
                video = VideoFileClip(temp_file.name)
                
                return VideoInfo(
                    duration=video.duration,
                    fps=video.fps,
                    width=video.w,
                    height=video.h,
                    format='mp4',  # Assume MP4 for now
                    size_bytes=len(video_data),
                    has_audio=video.audio is not None,
                    has_video=True
                )
        
        except Exception as e:
            self.logger.error(f"Failed to get video info: {e}")
            raise
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file.name)
            except:
                pass
    
    def _extract_key_frames(self, video_data: bytes, video_info: VideoInfo) -> List[VideoFrame]:
        """Extract key frames from video."""
        if not OPENCV_AVAILABLE:
            self.logger.warning("OpenCV not available - skipping frame extraction")
            return []
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                temp_file.write(video_data)
                temp_file.flush()
                
                # Open video
                cap = cv2.VideoCapture(temp_file.name)
                
                if not cap.isOpened():
                    raise RuntimeError("Failed to open video")
                
                frames = []
                frame_count = 0
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                
                # Calculate frame interval
                frame_interval = max(1, total_frames // self.max_frames)
                
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # Extract frame at intervals
                    if frame_count % frame_interval == 0:
                        # Convert frame to bytes
                        success, buffer = cv2.imencode('.jpg', frame, 
                                                    [cv2.IMWRITE_JPEG_QUALITY, 85])
                        if success:
                            image_data = buffer.tobytes()
                            
                            # Calculate timestamp
                            timestamp = frame_count / fps
                            
                            frames.append(VideoFrame(
                                frame_number=frame_count,
                                timestamp=timestamp,
                                image_data=image_data,
                                confidence=1.0
                            ))
                    
                    frame_count += 1
                
                cap.release()
                return frames
        
        except Exception as e:
            self.logger.error(f"Frame extraction failed: {e}")
            return []
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file.name)
            except:
                pass
    
    def _detect_scenes(self, video_data: bytes, video_info: VideoInfo) -> List[SceneInfo]:
        """Detect scenes in the video."""
        if not SCENEDETECT_AVAILABLE:
            self.logger.warning("SceneDetect not available - skipping scene detection")
            return []
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                temp_file.write(video_data)
                temp_file.flush()
                
                # Initialize scene detection
                video_manager = VideoManager([temp_file.name])
                scene_manager = SceneManager()
                scene_manager.add_detector(ContentDetector(threshold=self.scene_threshold))
                
                # Detect scenes
                video_manager.start()
                scene_manager.detect_scenes(frame_source=video_manager)
                scene_list = scene_manager.get_scene_list()
                
                # Convert to SceneInfo objects
                scenes = []
                for i, (start_time, end_time) in enumerate(scene_list):
                    scenes.append(SceneInfo(
                        scene_id=i,
                        start_time=start_time.get_seconds(),
                        end_time=end_time.get_seconds(),
                        duration=end_time.get_seconds() - start_time.get_seconds()
                    ))
                
                video_manager.release()
                return scenes
        
        except Exception as e:
            self.logger.error(f"Scene detection failed: {e}")
            return []
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file.name)
            except:
                pass
    
    def _extract_and_transcribe_audio(self, video_data: bytes, user_tier: str, 
                                    metadata: Dict[str, Any]) -> Optional[str]:
        """Extract audio from video and transcribe it."""
        if not MOVIEPY_AVAILABLE:
            return None
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                temp_file.write(video_data)
                temp_file.flush()
                
                # Load video
                video = VideoFileClip(temp_file.name)
                
                if not video.audio:
                    return None
                
                # Extract audio
                audio = video.audio
                
                # Create temporary audio file
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as audio_file:
                    audio.write_audiofile(audio_file.name, verbose=False, logger=None)
                    
                    # Read audio data
                    with open(audio_file.name, 'rb') as f:
                        audio_data = f.read()
                    
                    # Transcribe audio
                    result = self.audio_orchestrator.transcribe(
                        audio_data, user_tier, metadata
                    )
                    
                    return result.text
        
        except Exception as e:
            self.logger.error(f"Audio extraction/transcription failed: {e}")
            return None
        finally:
            # Clean up temp files
            try:
                os.unlink(temp_file.name)
                if 'audio_file' in locals():
                    os.unlink(audio_file.name)
            except:
                pass
    
    def _extract_visual_text(self, key_frames: List[VideoFrame], user_tier: str, 
                           metadata: Dict[str, Any]) -> str:
        """Extract text from key frames using OCR."""
        if not key_frames:
            return ""
        
        try:
            all_text = []
            
            for frame in key_frames:
                # Run OCR on frame
                result = self.vision_orchestrator.extract_text(
                    frame.image_data, user_tier, metadata
                )
                
                if result.text.strip():
                    all_text.append(f"[Frame {frame.frame_number} @ {frame.timestamp:.1f}s]: {result.text}")
            
            return "\n".join(all_text)
        
        except Exception as e:
            self.logger.error(f"Visual text extraction failed: {e}")
            return ""

# ==============================================================================
# VIDEO ANALYZER
# ==============================================================================

class VideoAnalyzer:
    """
    Advanced video analysis class that provides insights and summaries.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.processor = VideoProcessor(self.config)
    
    def analyze_video(self, video_data: bytes, user_tier: str = 'free', 
                     metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Perform comprehensive video analysis.
        
        Args:
            video_data: Raw video bytes
            user_tier: User's subscription tier
            metadata: Additional metadata
            
        Returns:
            Analysis results
        """
        metadata = metadata or {}
        
        try:
            # Process video
            result = self.processor.process_video(video_data, user_tier, metadata)
            
            # Generate analysis
            analysis = {
                'video_info': {
                    'duration': result.video_info.duration,
                    'fps': result.video_info.fps,
                    'resolution': f"{result.video_info.width}x{result.video_info.height}",
                    'size_mb': result.video_info.size_bytes / (1024 * 1024),
                    'has_audio': result.video_info.has_audio,
                    'has_video': result.video_info.has_video
                },
                'content_summary': {
                    'total_scenes': len(result.scenes),
                    'key_frames_extracted': len(result.key_frames),
                    'has_audio_transcription': bool(result.audio_transcription),
                    'has_visual_text': bool(result.visual_text)
                },
                'scenes': [
                    {
                        'id': scene.scene_id,
                        'start_time': scene.start_time,
                        'end_time': scene.end_time,
                        'duration': scene.duration
                    }
                    for scene in result.scenes
                ],
                'key_frames': [
                    {
                        'frame_number': frame.frame_number,
                        'timestamp': frame.timestamp,
                        'confidence': frame.confidence
                    }
                    for frame in result.key_frames
                ],
                'transcriptions': {
                    'audio': result.audio_transcription,
                    'visual': result.visual_text
                },
                'metadata': result.metadata
            }
            
            return analysis
        
        except Exception as e:
            self.logger.error(f"Video analysis failed: {e}")
            raise
    
    def generate_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate a text summary of the video analysis."""
        try:
            summary_parts = []
            
            # Basic info
            video_info = analysis['video_info']
            summary_parts.append(f"Video: {video_info['duration']:.1f}s, {video_info['resolution']}, {video_info['size_mb']:.1f}MB")
            
            # Content summary
            content = analysis['content_summary']
            summary_parts.append(f"Content: {content['total_scenes']} scenes, {content['key_frames_extracted']} key frames")
            
            # Transcriptions
            transcriptions = analysis['transcriptions']
            if transcriptions['audio']:
                summary_parts.append(f"Audio transcription: {len(transcriptions['audio'])} characters")
            if transcriptions['visual']:
                summary_parts.append(f"Visual text: {len(transcriptions['visual'])} characters")
            
            return "\n".join(summary_parts)
        
        except Exception as e:
            self.logger.error(f"Summary generation failed: {e}")
            return "Video analysis completed"

# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def validate_video_data(video_data: bytes) -> Dict[str, Any]:
    """
    Validate video data and return information.
    
    Args:
        video_data: Raw video bytes
        
    Returns:
        Validation result with video info
    """
    if not video_data:
        return {'valid': False, 'error': 'No video data provided'}
    
    if len(video_data) < 1000:  # Less than 1KB
        return {'valid': False, 'error': 'Video data too small'}
    
    try:
        # Try to get video info
        processor = VideoProcessor()
        video_info = processor._get_video_info(video_data)
        
        return {
            'valid': True,
            'video_info': video_info,
            'size_bytes': len(video_data)
        }
    
    except Exception as e:
        return {'valid': False, 'error': f'Invalid video data: {e}'}

def extract_thumbnail(video_data: bytes, timestamp: float = 0.0) -> bytes:
    """
    Extract a thumbnail from video at specified timestamp.
    
    Args:
        video_data: Raw video bytes
        timestamp: Timestamp in seconds
        
    Returns:
        Thumbnail image bytes
    """
    if not MOVIEPY_AVAILABLE:
        raise RuntimeError("MoviePy not available - install moviepy")
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            temp_file.write(video_data)
            temp_file.flush()
            
            # Load video
            video = VideoFileClip(temp_file.name)
            
            # Get frame at timestamp
            frame = video.get_frame(timestamp)
            
            # Convert to PIL Image
            from PIL import Image
            image = Image.fromarray(frame)
            
            # Convert to bytes
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='JPEG')
            return img_buffer.getvalue()
    
    except Exception as e:
        logger.error(f"Thumbnail extraction failed: {e}")
        raise
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_file.name)
        except:
            pass

def get_video_duration(video_data: bytes) -> float:
    """
    Get video duration in seconds.
    
    Args:
        video_data: Raw video bytes
        
    Returns:
        Duration in seconds
    """
    if not MOVIEPY_AVAILABLE:
        raise RuntimeError("MoviePy not available - install moviepy")
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            temp_file.write(video_data)
            temp_file.flush()
            
            # Load video
            video = VideoFileClip(temp_file.name)
            duration = video.duration
            video.close()
            
            return duration
    
    except Exception as e:
        logger.error(f"Duration extraction failed: {e}")
        raise
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_file.name)
        except:
            pass

