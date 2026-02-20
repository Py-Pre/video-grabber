"""Centralized download manager with optimized architecture"""

import asyncio
import logging
from typing import Dict, Any, AsyncGenerator, Optional
from downloader.video_processor import VideoProcessor
from downloader.audio_processor import AudioProcessor
from utils.validators import validate_url, normalize_url, sanitize_filename

logger = logging.getLogger(__name__)

class DownloadManager:
    """
    Centralized manager for all download operations
    Inspired by Seal's modular architecture
    """
    
    def __init__(self):
        self.video_processor = VideoProcessor()
        self.audio_processor = AudioProcessor()
        self.active_sessions = {}
        self.session_counter = 0
    
    async def get_video_info(self, url: str) -> Dict[str, Any]:
        """
        Extract comprehensive video information
        Combines video and audio format discovery
        """
        # Validate URL first
        is_valid, error_msg = validate_url(url)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Normalize URL for consistent processing
        normalized_url = normalize_url(url)
        
        try:
            # Extract video formats
            video_info = await self.video_processor.extract_video_info(normalized_url)
            
            # Extract audio formats
            audio_info = await self.audio_processor.extract_audio_info(normalized_url)
            
            # Combine formats
            all_formats = video_info['formats'] + audio_info['formats']
            
            # Return comprehensive info
            return {
                'title': video_info['title'],
                'thumbnail': video_info['thumbnail'],
                'duration': video_info['duration'],
                'formats': all_formats,
                'original_url': normalized_url,
                'uploader': video_info.get('uploader', ''),
                'view_count': video_info.get('view_count'),
                'upload_date': video_info.get('upload_date'),
                'artist': audio_info.get('artist', ''),
                'album': audio_info.get('album', ''),
                'total_formats': len(all_formats)
            }
            
        except Exception as e:
            logger.error(f"Failed to extract info for {normalized_url}: {str(e)}")
            
            # Enhanced error messages
            if "Video unavailable" in str(e):
                raise ValueError("El video no está disponible. Puede ser privado o haber sido eliminado.")
            elif "Unsupported URL" in str(e):
                raise ValueError("Esta plataforma no está soportada o el enlace no es válido.")
            elif "network" in str(e).lower():
                raise ValueError("Error de conexión. Verifica tu internet.")
            else:
                raise ValueError(f"Error al procesar el enlace: {str(e)}")
    
    async def download_content(
        self, 
        url: str, 
        format_id: str, 
        format_type: str = 'video'
    ) -> AsyncGenerator[bytes, None]:
        """
        Unified download interface for both video and audio
        Returns async generator for streaming response
        """
        self.session_counter += 1
        session_id = f"session_{self.session_counter}"
        
        try:
            # Validate inputs
            is_valid, error_msg = validate_url(url)
            if not is_valid:
                raise ValueError(error_msg)
            
            normalized_url = normalize_url(url)
            
            # Get title for filename
            title = await self._get_title_for_download(normalized_url)
            safe_title = sanitize_filename(title)
            
            # Register session
            self.active_sessions[session_id] = {
                'type': format_type,
                'url': normalized_url,
                'format': format_id,
                'title': safe_title,
                'status': 'downloading'
            }
            
            logger.info(f"Starting download session {session_id}: {safe_title} ({format_type}/{format_id})")
            
            # Route to appropriate processor
            if format_type == 'audio':
                async for chunk in self.audio_processor.download_audio(normalized_url, format_id, safe_title):
                    yield chunk
            else:
                async for chunk in self.video_processor.download_video(normalized_url, format_id, safe_title):
                    yield chunk
            
            # Update session status
            self.active_sessions[session_id]['status'] = 'completed'
            logger.info(f"Download session {session_id} completed successfully")
            
        except Exception as e:
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['status'] = 'failed'
                self.active_sessions[session_id]['error'] = str(e)
            
            logger.error(f"Download session {session_id} failed: {str(e)}")
            raise
        
        finally:
            # Cleanup session after delay
            asyncio.create_task(self._cleanup_session(session_id, delay=300))  # 5 minutes
    
    async def _get_title_for_download(self, url: str) -> str:
        """Quick title extraction for download naming"""
        try:
            import yt_dlp
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                return info.get('title', 'download')
        except:
            return 'download'
    
    async def _cleanup_session(self, session_id: str, delay: int = 300):
        """Clean up session after delay"""
        await asyncio.sleep(delay)
        self.active_sessions.pop(session_id, None)
        logger.info(f"Cleaned up session: {session_id}")
    
    def get_media_type_and_filename(self, format_id: str, format_type: str, title: str) -> tuple[str, str]:
        """Get appropriate media type and filename for HTTP response"""
        safe_title = sanitize_filename(title)
        
        if format_type == 'audio':
            media_type = self.audio_processor.get_media_type(format_id)
            filename = f"{safe_title}.{format_id}"
        else:
            media_type = "video/mp4"
            filename = f"{safe_title}.mp4"
        
        return media_type, filename
    
    def get_download_stats(self) -> Dict[str, Any]:
        """Get comprehensive download statistics"""
        video_downloads = self.video_processor.get_active_downloads()
        audio_downloads = self.audio_processor.get_active_downloads()
        
        return {
            'active_sessions': len(self.active_sessions),
            'video_downloads': len(video_downloads),
            'audio_downloads': len(audio_downloads),
            'total_active': len(video_downloads) + len(audio_downloads),
            'sessions': self.active_sessions.copy(),
            'video_details': video_downloads,
            'audio_details': audio_downloads,
        }
    
    async def cancel_download(self, session_id: str) -> bool:
        """Cancel specific download session"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            
            # Attempt to cancel with appropriate processor
            if session['type'] == 'audio':
                success = await self.audio_processor.cancel_download(session_id)
            else:
                success = await self.video_processor.cancel_download(session_id)
            
            if success:
                self.active_sessions[session_id]['status'] = 'cancelled'
                logger.info(f"Successfully cancelled session: {session_id}")
            
            return success
        
        return False
    
    async def health_check(self) -> Dict[str, Any]:
        """System health check for monitoring"""
        try:
            # Test yt-dlp availability
            import yt_dlp
            
            # Test FFmpeg availability
            import subprocess
            ffmpeg_available = subprocess.run(['ffmpeg', '-version'], 
                                            capture_output=True, timeout=5).returncode == 0
            
            stats = self.get_download_stats()
            
            return {
                'status': 'healthy',
                'yt_dlp_available': True,
                'ffmpeg_available': ffmpeg_available,
                'active_downloads': stats['total_active'],
                'system_load': 'normal' if stats['total_active'] < 5 else 'high',
                'memory_usage': 'optimal',  # Could implement actual memory monitoring
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                'status': 'degraded',
                'error': str(e),
                'yt_dlp_available': False,
                'ffmpeg_available': False,
            }