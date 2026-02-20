#!/bin/bash
set -e

echo "🔄 Actualizando yt-dlp a la última versión..."
pip install --upgrade yt-dlp --quiet
echo "✅ yt-dlp $(yt-dlp --version) listo"

echo "🚀 Iniciando VideoGrabber..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --workers ${WORKERS:-2}
