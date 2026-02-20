"""
VideoGrabber 1.0 - Modern Video/Audio Downloader
Optimized architecture inspired by Seal
"""

import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
from typing import Optional
from pydantic import BaseModel, field_validator
import os

# Import our modular architecture
from downloader import DownloadManager
from utils.validators import validate_url
from config import ERROR_MESSAGES

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure downloads directory exists
os.makedirs("downloads", exist_ok=True)

# Initialize download manager
download_manager = DownloadManager()

# Pydantic models
class VideoInfoRequest(BaseModel):
    url: str
    
    @field_validator('url')
    @classmethod
    def validate_url_format(cls, v):
        """Validate URL format using centralized validator"""
        is_valid, error_msg = validate_url(v)
        if not is_valid:
            raise ValueError(error_msg)
        return v.strip()

class VideoFormat(BaseModel):
    format_id: str
    ext: str
    quality: str
    file_size: Optional[str] = None
    type: str  # "video" or "audio"
    
    @field_validator('file_size', mode='before')
    @classmethod
    def validate_file_size(cls, v):
        """Convert file_size from int to string if needed"""
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return str(v)
        return str(v) if v else None

class VideoInfo(BaseModel):
    title: str
    thumbnail: Optional[str] = None
    duration: Optional[int] = None
    formats: list[VideoFormat]
    original_url: str

# FastAPI app configuration
app = FastAPI(
    title="VideoGrabber API", 
    version="1.0.0",
    description="API moderna y optimizada para descargar videos y audio"
)

# CORS middleware — lee los orígenes desde variable de entorno en producción
_raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000")
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount only /assets — montar "/" como StaticFiles bloquea los POST a /api/*
if os.path.exists("dist"):
    app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")


@app.get("/")
async def serve_app():
    """Serve the React application"""
    if os.path.exists("dist/index.html"):
        return FileResponse("dist/index.html")
    return {"message": "VideoGrabber 1.0 API", "docs": "/docs"}


@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Catch-all: sirve index.html para rutas del SPA (React Router)"""
    # No interceptar rutas de la API
    if full_path.startswith("api/") or full_path.startswith("assets/"):
        raise HTTPException(status_code=404, detail="Not found")
    index_path = "dist/index.html"
    if os.path.exists(index_path):
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="Frontend not built")


@app.post("/api/info")
async def get_video_info(request: VideoInfoRequest):
    """
    Extract video information using optimized download manager with timeout
    """
    try:
        # Añadir timeout para toda la operación
        info = await asyncio.wait_for(
            download_manager.get_video_info(request.url),
            timeout=25  # 25 segundos máximo
        )
        return VideoInfo(**info)
        
    except asyncio.TimeoutError:
        logger.warning(f"Timeout processing URL: {request.url}")
        raise HTTPException(
            status_code=408, 
            detail="El video está tardando demasiado en procesar. Intenta con otro enlace."
        )
        
    except ValueError as e:
        # User input errors
        logger.warning(f"Invalid input for {request.url}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        # System errors with helpful messages
        error_msg = str(e)
        
        if "Video unavailable" in error_msg or "no está disponible" in error_msg:
            error_msg = ERROR_MESSAGES['video_unavailable']
        elif "Unsupported URL" in error_msg or "no está soportada" in error_msg:
            error_msg = ERROR_MESSAGES['unsupported_site']
        elif "network" in error_msg.lower() or "conexión" in error_msg.lower():
            error_msg = ERROR_MESSAGES['network_error']
        elif "timeout" in error_msg.lower() or "tardando" in error_msg.lower():
            error_msg = "El video está tardando demasiado en cargar. Verifica tu conexión o intenta con otro enlace."
        
        logger.error(f"Error extracting info: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)


@app.get("/api/download")
async def download_video(url: str, format_id: str, format_type: str = "video"):
    """
    Download video/audio with optimized streaming
    """
    try:
        # Validate inputs
        is_valid, error_msg = validate_url(url)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Get title for filename
        import yt_dlp
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'download')
        
        # Get media type and filename
        media_type, filename = download_manager.get_media_type_and_filename(
            format_id, format_type, title
        )
        
        # Stream the download
        return StreamingResponse(
            download_manager.download_content(url, format_id, format_type),
            media_type=media_type,
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Cache-Control': 'no-cache',
            }
        )
        
    except Exception as e:
        logger.error(f"Download failed: {str(e)}")
        
        # Enhanced error handling
        if "format not available" in str(e).lower():
            error_msg = ERROR_MESSAGES['format_not_available']
        elif "file too large" in str(e).lower():
            error_msg = ERROR_MESSAGES['file_too_large']
        else:
            error_msg = ERROR_MESSAGES['download_failed']
        
        raise HTTPException(status_code=400, detail=error_msg)


@app.get("/api/stats")
async def get_download_stats():
    """Get current download statistics"""
    try:
        stats = download_manager.get_download_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return {"error": "Unable to retrieve stats"}


@app.get("/api/health")
async def health_check():
    """System health check endpoint"""
    try:
        health = await download_manager.health_check()
        return health
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}


@app.delete("/api/download/{session_id}")
async def cancel_download(session_id: str):
    """Cancel active download session"""
    try:
        success = await download_manager.cancel_download(session_id)
        if success:
            return {"message": f"Download {session_id} cancelled successfully"}
        else:
            return {"error": f"Download {session_id} not found or already completed"}
    except Exception as e:
        logger.error(f"Error cancelling download {session_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting VideoGrabber 1.0 with optimized architecture")
    uvicorn.run(app, host="0.0.0.0", port=8000)