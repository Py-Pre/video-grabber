#!/bin/bash

# 🚀 VideoGrabber 1.0 - Script de Inicio Rápido
echo "🎥 Iniciando VideoGrabber 1.0..."

# Verificar si el entorno virtual existe
if [ ! -d "venv" ]; then
    echo "❌ Entorno virtual no encontrado. Ejecuta primero: bash setup.sh"
    exit 1
fi

# Activar entorno virtual Python
echo "🐍 Activando entorno virtual Python..."
source venv/bin/activate

# Actualizar yt-dlp para evitar errores con sitios
echo "🔄 Actualizando yt-dlp..."
pip install --upgrade yt-dlp

# Verificar dependencias Python
if ! python -c "import fastapi, uvicorn, yt_dlp" 2>/dev/null; then
    echo "❌ Dependencias Python faltantes. Instalando..."
    pip install -r requirements.txt
fi

# Verificar dependencias Node.js
if [ ! -d "node_modules" ] || [ ! -f "node_modules/.package-lock.json" ]; then
    echo "📦 Instalando dependencias Node.js..."
    npm install
fi

# Compilar frontend si no existe dist/
if [ ! -f "dist/index.html" ]; then
    echo "🔨 Compilando frontend React..."
    npm run build
fi

# Crear directorios necesarios
mkdir -p downloads

# Verificar ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg no encontrado. Algunas conversiones pueden fallar."
    echo "   Instala con: sudo apt install ffmpeg"
fi

echo ""
echo "🎉 ¡Todo listo! Iniciando servidor..."
echo "🌐 Aplicación disponible en: http://localhost:8000/"
echo "📚 API Docs en: http://localhost:8000/docs"
echo ""
echo "💡 Optimizaciones aplicadas:"
echo "   • Timeout de 15s para extracción de info"
echo "   • Manejo mejorado de errores"
echo "   • yt-dlp actualizado a última versión"
echo ""
echo "🛑 Para detener: Ctrl+C"
echo ""

# Iniciar servidor FastAPI
python main.py