"""Specialized audio processing and extraction manager"""

import asyncio
import subprocess
import logging
from typing import AsyncGenerator, List, Dict, Any, Optional
import yt_dlp
from config.settings import get_audio_options, AUDIO_CONFIG
from utils.validators import sanitize_filename, get_format_type

logger = logging.getLogger(__name__)

class AudioProcessor:
    """Handles audio-specific downloading and processing"""
    
    def __init__(self):
        self.active_downloads = {}
        self.download_counter = 0
        self.supported_codecs = ['mp3', 'aac', 'flac', 'ogg', 'm4a']
    
    async def extract_audio_info(self, url: str) -> Dict[str, Any]:
        """Extract audio information optimized for audio formats"""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'listformats': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Process audio formats
                audio_formats = await self._process_audio_formats(info.get('formats', []))
                
                return {
                    'title': sanitize_filename(info.get('title', 'download')),
                    'thumbnail': info.get('thumbnail'),
                    'duration': info.get('duration'),
                    'formats': audio_formats,
                    'original_url': url,
                    'uploader': info.get('uploader', ''),
                    'artist': info.get('artist') or info.get('uploader', ''),
                    'album': info.get('album', ''),
                }
        except Exception as e:
            logger.error(f"Audio info extraction failed: {str(e)}")
            raise
    
    async def _process_audio_formats(self, formats: List[Dict]) -> List[Dict]:
        """Process and optimize audio format list"""
        audio_formats = []
        seen_qualities = set()
        
        # Process available audio-only formats
        for f in formats:
            if not f:
                continue
                
            ext = f.get('ext', '')
            vcodec = f.get('vcodec', 'none')
            acodec = f.get('acodec', 'none')
            
            # Audio-only formats 
            if acodec != 'none' and vcodec == 'none':
                abr = f.get('abr', 0) or f.get('tbr', 0)
                quality_key = f"{abr}_{ext}"
                
                if quality_key not in seen_qualities and abr:
                    seen_qualities.add(quality_key)
                    quality_str = f"{abr}kbps"
                    
                    file_size = f.get('filesize_approx') or f.get('filesize')
                    
                    # Determine best codec mapping
                    target_codec = self._map_to_supported_codec(ext, acodec)
                    
                    audio_formats.append({
                        'format_id': f['format_id'],
                        'ext': target_codec,
                        'quality': quality_str,
                        'file_size': str(file_size) if file_size else None,
                        'type': 'audio',
                        'acodec': acodec,
                        'abr': abr,
                        'original_ext': ext,
                    })
        
        # Add standard audio extraction options
        standard_formats = [
            {'format_id': 'mp3', 'ext': 'mp3', 'quality': '320kbps', 'type': 'audio'},
            {'format_id': 'aac', 'ext': 'aac', 'quality': '256kbps', 'type': 'audio'}, 
            {'format_id': 'm4a', 'ext': 'm4a', 'quality': '256kbps', 'type': 'audio'},
            {'format_id': 'flac', 'ext': 'flac', 'quality': 'Lossless', 'type': 'audio'},
            {'format_id': 'ogg', 'ext': 'ogg', 'quality': '192kbps', 'type': 'audio'},
        ]
        
        # Sort by bitrate (high to low)
        audio_formats.sort(key=lambda x: x.get('abr', 0), reverse=True)
        
        # Combine and deduplicate
        all_formats = audio_formats + standard_formats
        unique_formats = []
        seen_codecs = set()
        
        for fmt in all_formats:
            codec = fmt['ext']
            if codec not in seen_codecs:
                seen_codecs.add(codec)
                # Clean format for response
                clean_format = {
                    'format_id': fmt['format_id'],
                    'ext': fmt['ext'],
                    'quality': fmt['quality'],
                    'file_size': fmt.get('file_size'),
                    'type': fmt['type'],
                }
                unique_formats.append(clean_format)
        
        return unique_formats[:8]  # Limit to 8 formats
    
    def _map_to_supported_codec(self, ext: str, acodec: str) -> str:
        """Map format to best supported codec"""
        if ext in self.supported_codecs:
            return ext
        
        # Map common codecs to supported formats  
        codec_mapping = {
            'mp4a': 'm4a',
            'opus': 'ogg', 
            'vorbis': 'ogg',
            'mp4a.40.2': 'aac',
            'mp4a.40.5': 'aac',
        }
        
        return codec_mapping.get(acodec, 'm4a')  # Default to m4a
    
    async def download_audio(self, url: str, format_id: str, title: str) -> AsyncGenerator[bytes, None]:
        """Stream audio download with optimized extraction"""
        self.download_counter += 1
        download_id = f"audio_{self.download_counter}"
        
        try:
            self.active_downloads[download_id] = {'type': 'audio', 'url': url, 'format': format_id}
            
            # Build optimized command for different format types
            if format_id in self.supported_codecs:
                cmd = self._build_extraction_command(url, format_id)
            else:
                cmd = self._build_direct_download_command(url, format_id)
            
            logger.info(f"Starting audio download: {download_id} - {title} ({format_id})")
            
            # Stream the download
            async for chunk in self._stream_subprocess(cmd, download_id):
                yield chunk
                
        except Exception as e:
            logger.error(f"Audio download failed for {download_id}: {str(e)}")
            raise
        finally:
            self.active_downloads.pop(download_id, None)
            logger.info(f"Audio download completed: {download_id}")
    
    def _build_extraction_command(self, url: str, codec: str) -> List[str]:
        """Build command for audio extraction to specific codec"""
        quality_map = {
            'mp3': '320',
            'aac': '256', 
            'm4a': '256',
            'flac': '0',  # Best quality
            'ogg': '192'
        }
        
        cmd = [
            'yt-dlp',
            '--extract-audio',
            '--audio-format', codec,
            '--audio-quality', quality_map.get(codec, '320'),
            '--embed-thumbnail' if AUDIO_CONFIG['embed_artwork'] else '--no-embed-thumbnail',
            '--add-metadata' if AUDIO_CONFIG['embed_metadata'] else '--no-add-metadata',
            '--no-playlist',
            '--newline',
            '-o', '-',
            url
        ]
        
        return cmd
    
    def _build_direct_download_command(self, url: str, format_id: str) -> List[str]:
        """Build command for direct format download with conversion"""
        cmd = [
            'yt-dlp',
            '-f', format_id,
            '--extract-audio',
            '--audio-format', 'm4a',  # Convert to m4a for compatibility
            '--audio-quality', '256',
            '--embed-thumbnail' if AUDIO_CONFIG['embed_artwork'] else '--no-embed-thumbnail',
            '--add-metadata' if AUDIO_CONFIG['embed_metadata'] else '--no-add-metadata',
            '--no-playlist',
            '--newline',
            '-o', '-',
            url
        ]
        
        return cmd
    
    async def _stream_subprocess(self, cmd: List[str], download_id: str) -> AsyncGenerator[bytes, None]:
        """Stream subprocess output with error handling"""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                limit=1024*1024*5  # 5MB buffer for audio
            )
            
            chunk_size = AUDIO_CONFIG.get('chunk_size', 1024 * 32)  # Smaller chunks for audio
            
            while True:
                chunk = await process.stdout.read(chunk_size)
                if not chunk:
                    break
                yield chunk
            
            return_code = await process.wait()
            
            if return_code != 0:
                stderr = await process.stderr.read()
                error_msg = stderr.decode('utf-8', errors='ignore')
                logger.error(f"Audio download process failed for {download_id}: {error_msg}")
                raise RuntimeError(f"Audio download failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"Audio stream subprocess error for {download_id}: {str(e)}")
            raise
    
    def get_media_type(self, format_id: str) -> str:
        """Get appropriate media type for HTTP response"""
        media_types = {
            'mp3': 'audio/mpeg',
            'aac': 'audio/aac',
            'm4a': 'audio/mp4', 
            'flac': 'audio/flac',
            'ogg': 'audio/ogg',
        }
        return media_types.get(format_id, 'audio/mp4')
    
    def get_active_downloads(self) -> Dict:
        """Get information about currently active downloads"""
        return self.active_downloads.copy()
    
    async def cancel_download(self, download_id: str) -> bool:
        """Cancel an active download"""
        if download_id in self.active_downloads:
            logger.info(f"Cancelling audio download: {download_id}")
            return True
        return False