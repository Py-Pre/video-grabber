# VideoGrabber Configuration Settings

import os
from typing import Dict, Any

# Download Configuration
DOWNLOAD_CONFIG = {
    'max_concurrent_downloads': 3,
    'chunk_size': 1024 * 64,  # 64KB chunks for streaming
    'timeout': 20,  # Timeout más agresivo
    'retries': 2,  # Menos reintentos para fallar rápido
    'extract_flat': False,
    'no_warnings': True,  # Activar para reducir ruido
    'quiet': True,
    'info_timeout': 15,  # Timeout específico para extracción de info
    'fragment_retries': 2,  # Reintentos de fragmentos
    'skip_unavailable_fragments': True,  # Saltar fragmentos no disponibles
}

# Video Quality Configuration  
VIDEO_CONFIG = {
    'preferred_formats': ['mp4', 'webm', 'mkv'],
    'quality_priorities': [1080, 720, 480, 360],
    'max_file_size': '1000M',  # 1GB max
    'prefer_mp4': True,
    'embed_thumbnails': True,
    'embed_metadata': True,
}

# Audio Quality Configuration
AUDIO_CONFIG = {
    'preferred_codecs': ['m4a', 'mp3', 'aac', 'flac', 'ogg'],
    'default_quality': '320',  # kbps for mp3
    'embed_artwork': True,
    'embed_metadata': True,
    'normalize_audio': False,
}

# External Tools
EXTERNAL_TOOLS = {
    'ffmpeg_path': 'ffmpeg',  # System PATH
    'aria2c_enabled': False,  # Enable for faster downloads
    'aria2c_options': {
        'max_connections': 16,
        'split': 16,
        'min_split_size': '1M'
    }
}

# Error Messages
ERROR_MESSAGES = {
    'invalid_url': 'URL no válida. Ingresa un enlace completo (ej: https://youtube.com/watch?v=abc123)',
    'video_unavailable': 'El video no está disponible. Puede ser privado o haber sido eliminado.',
    'unsupported_site': 'Esta plataforma no está soportada.',
    'download_failed': 'Error durante la descarga. Inténtalo de nuevo.',
    'format_not_available': 'El formato seleccionado no está disponible.',
    'network_error': 'Error de conexión. Verifica tu internet.',
    'file_too_large': 'El archivo es demasiado grande (máximo 1GB).',
}

# Supported Sites Pattern
SUPPORTED_SITES = [
    r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
    r'(?:https?://)?(?:www\.)?youtu\.be/[\w-]+',
    r'(?:https?://)?(?:www\.)?facebook\.com/.+/videos/\d+',
    r'(?:https?://)?(?:www\.)?vimeo\.com/\d+',
    r'(?:https?://)?(?:www\.)?tiktok\.com/.+',
    r'(?:https?://)?(?:www\.)?instagram\.com/p/[\w-]+',
]

def get_ydl_base_options() -> Dict[str, Any]:
    """Get base yt-dlp options optimized for streaming and fast extraction"""
    return {
        'quiet': DOWNLOAD_CONFIG['quiet'],
        'no_warnings': DOWNLOAD_CONFIG['no_warnings'],
        'extractaudio': False,
        'audioformat': 'mp3',
        'outtmpl': '-',  # Stream to stdout
        'logtostderr': False,
        'ignoreerrors': False,
        'retries': DOWNLOAD_CONFIG['retries'],
        'socket_timeout': DOWNLOAD_CONFIG['timeout'],
        'fragment_retries': DOWNLOAD_CONFIG['fragment_retries'],
        'skip_unavailable_fragments': DOWNLOAD_CONFIG['skip_unavailable_fragments'],
        # Optimizaciones para extracción rápida
        'extract_flat': False,
        'noplaylist': True,  # CRÍTICO: No procesar playlists completas
        'lazy_playlist': True,  # No extraer toda la playlist
        'playliststart': 1,
        'playlistend': 1,  # Solo el video actual
        'max_downloads': 1,
        'no_color': True,
        'prefer_free_formats': False,  # Priorizar formatos de buena calidad
        # Headers para evitar detección de bots
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        },
        'cookiefile': os.getenv('COOKIE_FILE', None),  # Archivo de cookies opcional
    }

def get_video_options(format_id: str) -> Dict[str, Any]:
    """Get optimized video download options"""
    base_opts = get_ydl_base_options()
    base_opts.update({
        'format': f'{format_id}+bestaudio[ext=m4a]/best[ext=mp4]/{format_id}+bestaudio/best',
        'merge_output_format': 'mp4',
        'writeinfojson': False,
        'writethumbnail': VIDEO_CONFIG['embed_thumbnails'],
        'embedthumbnail': VIDEO_CONFIG['embed_thumbnails'],
        'addmetadata': VIDEO_CONFIG['embed_metadata'],
        'postprocessors': [
            {
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            },
            {
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            },
        ] if VIDEO_CONFIG['embed_metadata'] else []
    })
    return base_opts

def get_audio_options(codec: str = 'mp3', quality: str = '320') -> Dict[str, Any]:
    """Get optimized audio extraction options"""
    base_opts = get_ydl_base_options()
    base_opts.update({
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': codec,
            'preferredquality': quality if codec == 'mp3' else None,
        }],
        'writeinfojson': False,
        'writethumbnail': AUDIO_CONFIG['embed_artwork'],
        'embedthumbnail': AUDIO_CONFIG['embed_artwork'],
        'addmetadata': AUDIO_CONFIG['embed_metadata'],
    })
    return base_opts