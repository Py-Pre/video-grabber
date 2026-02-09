"""URL and input validation utilities"""

import re
from typing import List, Optional
from urllib.parse import urlparse
from config.settings import SUPPORTED_SITES, ERROR_MESSAGES

def validate_url(url: str) -> tuple[bool, Optional[str]]:
    """
    Validate if input is a proper video URL
    Returns (is_valid, error_message)
    """
    if not url or not isinstance(url, str):
        return False, ERROR_MESSAGES['invalid_url']
    
    url = url.strip()
    
    # Check for common non-URL patterns
    invalid_patterns = [
        r'^python\s+main\.py$',
        r'^[a-zA-Z_][a-zA-Z0-9_]*\s*=.*$',  # Variable assignments
        r'^[a-zA-Z_][a-zA-Z0-9_]*\(.*\)$',  # Function calls  
        r'^[a-zA-Z]+\s+[a-zA-Z]+.*$',  # Commands like "python main.py"
        r'^[a-zA-Z]+$',  # Single words
        r'^\d+$',  # Just numbers
    ]
    
    for pattern in invalid_patterns:
        if re.match(pattern, url, re.IGNORECASE):
            return False, f"'{url}' {ERROR_MESSAGES['invalid_url']}"
    
    # Basic URL structure check
    if not _has_url_structure(url):
        return False, ERROR_MESSAGES['invalid_url']
    
    # Check against supported sites
    if not _is_supported_site(url):
        return False, ERROR_MESSAGES['unsupported_site']
    
    return True, None

def _has_url_structure(url: str) -> bool:
    """Check if string has basic URL structure"""
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        if url.startswith('www.') or any(domain in url.lower() for domain in ['youtube', 'youtu.be', 'facebook', 'vimeo', 'tiktok', 'instagram']):
            url = 'https://' + url
        else:
            return False
    
    try:
        parsed = urlparse(url)
        return all([parsed.scheme, parsed.netloc])
    except:
        return False

def _is_supported_site(url: str) -> bool:
    """Check if URL matches supported site patterns"""
    # Add protocol if missing for pattern matching
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    for pattern in SUPPORTED_SITES:
        if re.search(pattern, url, re.IGNORECASE):
            return True
    
    # Fallback: check for known domains
    known_domains = ['youtube.com', 'youtu.be', 'facebook.com', 'vimeo.com', 'tiktok.com', 'instagram.com']
    return any(domain in url.lower() for domain in known_domains)

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe download"""
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace quotes and other problematic chars
    filename = filename.replace('"', '').replace("'", '').replace(';', '')
    # Truncate if too long
    return filename[:200] if len(filename) > 200 else filename

def get_format_type(format_id: str, ext: str = '') -> str:
    """Determine if format is video or audio"""
    audio_formats = ['mp3', 'aac', 'flac', 'ogg', 'm4a', 'opus']
    
    if ext.lower() in audio_formats:
        return 'audio'
    
    if format_id.lower() in audio_formats:
        return 'audio'
        
    # Check if it's a known audio-only format ID
    audio_format_ids = ['249', '250', '251', '140', '139', '171']
    if format_id in audio_format_ids:
        return 'audio'
        
    return 'video'

def normalize_url(url: str) -> str:
    """Normalize URL for consistent processing"""
    url = url.strip()
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        if url.startswith('www.') or any(domain in url.lower() for domain in ['youtube', 'youtu.be', 'facebook']):
            url = 'https://' + url
    
    # Convert youtu.be URLs to youtube.com
    url = re.sub(r'https?://youtu\.be/([a-zA-Z0-9_-]+)', r'https://www.youtube.com/watch?v=\1', url)
    
    # Ensure www for youtube
    url = re.sub(r'https?://youtube\.com', 'https://www.youtube.com', url)
    
    # Clean playlist parameters from YouTube URLs
    url = clean_youtube_playlist_params(url)
    
    return url

def clean_youtube_playlist_params(url: str) -> str:
    """Remove playlist parameters from YouTube URLs to prevent playlist processing"""
    if 'youtube.com' not in url and 'youtu.be' not in url:
        return url
    
    original_url = url
    
    # Remove playlist and related parameters
    # Patterns to remove: &list=..., &index=..., &start_radio=..., &t=...
    playlist_params = [
        r'&list=[^&]*',
        r'\?list=[^&]*&?',
        r'&index=[^&]*', 
        r'&start_radio=[^&]*',
        r'&pp=[^&]*'
    ]
    
    for pattern in playlist_params:
        url = re.sub(pattern, '', url)
    
    # Clean up any trailing & or ?
    url = re.sub(r'[&?]$', '', url)
    # Fix double & 
    url = re.sub(r'&+', '&', url)
    # Fix ? followed by &
    url = re.sub(r'\?&', '?', url)
    
    # Log if URL was modified to remove playlist params
    if url != original_url:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Cleaned playlist params from URL: {original_url} -> {url}")
    
    return url