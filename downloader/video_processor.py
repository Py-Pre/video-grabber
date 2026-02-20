"""Specialized video processing and download manager"""

import asyncio
import subprocess
import logging
from typing import AsyncGenerator, List, Dict, Any, Optional
import yt_dlp
import os
from config.settings import get_video_options, VIDEO_CONFIG
from utils.validators import sanitize_filename

logger = logging.getLogger(__name__)

class VideoProcessor:
    """Handles video-specific downloading and processing"""
    
    def __init__(self):
        self.active_downloads = {}
        self.download_counter = 0
    
    def _extract_info_sync(self, url: str, ydl_opts: dict) -> Dict[str, Any]:
        """Synchronous extraction helper for asyncio executor"""
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)

    async def extract_video_info(self, url: str) -> Dict[str, Any]:
        """Extract video information optimized for video formats with fast timeout"""
        from config.settings import get_ydl_base_options, DOWNLOAD_CONFIG
        from utils.validators import normalize_url
        
        # Normalizar URL para evitar problemas con playlists
        clean_url = normalize_url(url)
        logger.info(f"Processing URL: {clean_url}")
        
        # Opciones optimizadas para extracción rápida
        ydl_opts = get_ydl_base_options()
        ydl_opts.update({
            'format': 'worst',  # Formato más rápido para info
            'socket_timeout': DOWNLOAD_CONFIG['info_timeout'],
            'extract_flat': False,
            'noplaylist': True,  # CRÍTICO: No procesar playlists
            'lazy_playlist': True,
            'playlistend': 1,  # Solo el primer video
            'playliststart': 1,  # Solo el primer video
            'no_warnings': True,
            'quiet': True,
            'skip_download': True,  # Solo extraer info
            'age_limit': None,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'writethumbnail': False,  # No descargar thumbnail en esta fase
            'writeinfojson': False,
        })
        
        try:
            # Usar asyncio.wait_for para timeout estricto
            loop = asyncio.get_event_loop()
            info = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self._extract_info_sync(clean_url, ydl_opts)
                ),
                timeout=DOWNLOAD_CONFIG['info_timeout'] + 5  # 5 segundos extra de margen
            )
            
            # Process and filter video formats
            video_formats = []
            if info.get('formats'):
                video_formats = await self._process_video_formats(info['formats'])
            
            # Handle thumbnail preview
            thumbnail_url = info.get('thumbnail')
            
            return {
                'title': sanitize_filename(info.get('title', 'download')),
                'thumbnail': thumbnail_url,  # Use original thumbnail URL
                'duration': info.get('duration'),
                'formats': video_formats,
                'original_url': url,
                'uploader': info.get('uploader', ''),
                'view_count': info.get('view_count'),
                'upload_date': info.get('upload_date'),
            }
                
        except asyncio.TimeoutError:
            logger.error(f"Timeout extracting info from: {url}")
            raise Exception("El video está tardando demasiado en cargar. Intenta con otro enlace o verifica tu conexión.")
        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            if "Video unavailable" in error_msg or "Private video" in error_msg:
                raise Exception("El video no está disponible, es privado o fue eliminado.")
            elif "Unsupported URL" in error_msg:
                raise Exception("Esta plataforma no está soportada o el enlace no es válido.")
            elif "network" in error_msg.lower() or "timeout" in error_msg.lower():
                raise Exception("Error de conexión. Verifica tu internet e intenta de nuevo.")
            elif "Sign in to confirm" in error_msg or "bot" in error_msg.lower():
                raise Exception("YouTube requiere verificación anti-bot. Intenta con otro video o usa un enlace diferente.")
            else:
                raise Exception(f"Error al procesar el video: {error_msg}")
        except Exception as e:
            logger.error(f"Video info extraction failed: {str(e)}")
            raise Exception(f"Error inesperado al procesar el enlace: {str(e)}")
    
    async def _process_video_formats(self, formats: List[Dict]) -> List[Dict]:
        """Process and optimize video format list"""
        video_formats = []
        seen_qualities = set()
        
        for f in formats:
            if not f:
                continue
                
            ext = f.get('ext', '')
            vcodec = f.get('vcodec', 'none')
            acodec = f.get('acodec', 'none')  
            
            # Only video formats with good compatibility
            if (vcodec != 'none' and 
                ext in VIDEO_CONFIG['preferred_formats'] and
                vcodec != 'av01'):  # Skip AV1 for compatibility
                
                quality = f.get('height', 0)
                if quality and quality not in seen_qualities:
                    seen_qualities.add(quality)
                    
                    quality_str = f"{quality}p"
                    if f.get('fps') and f.get('fps') > 30:
                        quality_str += f" ({f.get('fps')}fps)"
                    
                    # Prioritize MP4 formats
                    format_priority = 0
                    if ext == 'mp4':
                        format_priority = 1
                    elif 'mp4' in f.get('format_note', '').lower():
                        format_priority = 0.8
                    
                    file_size = f.get('filesize_approx') or f.get('filesize')
                    
                    video_formats.append({
                        'format_id': f['format_id'],
                        'ext': 'mp4',  # Normalize to mp4
                        'quality': quality_str,
                        'file_size': str(file_size) if file_size else None,
                        'type': 'video',
                        'vcodec': vcodec,
                        'acodec': acodec,
                        'priority': format_priority,
                        'original_ext': ext,
                    })
        
        # Sort by quality (high to low) and format priority
        video_formats.sort(
            key=lambda x: (x.get('priority', 0), int(x['quality'].split('p')[0]) if x['quality'].endswith('p') else 0),
            reverse=True
        )
        
        # Remove duplicates and limit to reasonable amount
        unique_formats = []
        seen_heights = set()
        
        for fmt in video_formats:
            height = int(fmt['quality'].split('p')[0]) if fmt['quality'].endswith('p') else 0
            if height not in seen_heights and len(unique_formats) < 8:
                seen_heights.add(height)
                # Clean up format for response
                clean_format = {
                    'format_id': fmt['format_id'],
                    'ext': fmt['ext'],
                    'quality': fmt['quality'],
                    'file_size': fmt['file_size'],
                    'type': fmt['type'],
                }
                unique_formats.append(clean_format)
        
        return unique_formats
    
    async def download_video(self, url: str, format_id: str, title: str) -> AsyncGenerator[bytes, None]:
        """Stream video download with optimized settings"""
        self.download_counter += 1
        download_id = f"video_{self.download_counter}"
        
        try:
            self.active_downloads[download_id] = {'type': 'video', 'url': url, 'format': format_id}
            
            # Build optimized command
            cmd = [
                'yt-dlp',
                '-f', self._get_video_format_string(format_id),
                '--merge-output-format', 'mp4',
                '--embed-thumbnail',
                '--add-metadata',
                '--no-playlist',
                '--newline',
                '-o', '-',  # Output to stdout
                url
            ]
            
            logger.info(f"Starting video download: {download_id} - {title}")
            
            # Stream the download
            async for chunk in self._stream_subprocess(cmd, download_id):
                yield chunk
                
        except Exception as e:
            logger.error(f"Video download failed for {download_id}: {str(e)}")
            raise
        finally:
            self.active_downloads.pop(download_id, None)
            logger.info(f"Video download completed: {download_id}")
    
    def _get_video_format_string(self, format_id: str) -> str:
        """Get optimized format string for video download"""
        # Enhanced format selection for better compatibility
        return f'{format_id}+bestaudio[ext=m4a]/best[ext=mp4]/{format_id}+bestaudio/best'
    
    async def _stream_subprocess(self, cmd: List[str], download_id: str) -> AsyncGenerator[bytes, None]:
        """Stream subprocess output with proper error handling"""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                limit=1024*1024*10  # 10MB buffer
            )
            
            chunk_size = VIDEO_CONFIG.get('chunk_size', 1024 * 64)
            
            while True:
                chunk = await process.stdout.read(chunk_size)
                if not chunk:
                    break
                yield chunk
            
            # Wait for process completion
            return_code = await process.wait()
            
            if return_code != 0:
                stderr = await process.stderr.read()
                error_msg = stderr.decode('utf-8', errors='ignore')
                logger.error(f"Download process failed for {download_id}: {error_msg}")
                raise RuntimeError(f"Download failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"Stream subprocess error for {download_id}: {str(e)}")
            raise
    
    def get_active_downloads(self) -> Dict:
        """Get information about currently active downloads"""
        return self.active_downloads.copy()
    
    async def cancel_download(self, download_id: str) -> bool:
        """Cancel an active download"""
        if download_id in self.active_downloads:
            # Implementation for canceling specific download
            # This would require tracking process objects
            logger.info(f"Cancelling download: {download_id}")
            return True
        return False