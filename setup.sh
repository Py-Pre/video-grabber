#!/bin/bash

# 🚀 VideoGrabber 1.0 - Setup Script (Arquitectura Optimizada)
echo "🎥 Configurando VideoGrabber 1.0 con arquitectura modular..."

# Verificar dependencias del sistema
echo "📋 Verificando dependencias del sistema..."

# Python
if command -v python3 &> /dev/null; then
    echo "✅ Python3 encontrado: $(python3 --version)"
else
    echo "❌ Python3 no encontrado. Instalando..."
    sudo apt update && sudo apt install -y python3 python3-full python3-venv python3-pip
fi

# Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version | cut -d'v' -f2)
    echo "✅ Node.js encontrado: v$NODE_VERSION"
    if [[ $(echo "$NODE_VERSION" | cut -d'.' -f1) -lt 18 ]]; then
        echo "⚠️  Se recomienda Node.js 18+ para mejor rendimiento"
    fi
else
    echo "❌ Node.js no encontrado. Por favor instala Node.js 18+"
    exit 1
fi

# ffmpeg
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg encontrado"
else
    echo "❌ FFmpeg no encontrado. Instalando..."
    sudo apt install -y ffmpeg
fi

# Configurar backend Python
echo "🐍 Configurando backend Python..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Entorno virtual creado"
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencias Python instaladas"

# Configurar frontend React
echo "⚛️ Configurando frontend React (TypeScript)..."

# Limpiar node_modules si existe para instalación fresca
if [ -d "node_modules" ]; then
    echo "🧹 Limpiando instalación anterior..."
    rm -rf node_modules package-lock.json
    rm -rf dist
fi

# Instalar dependencias
npm install
echo "✅ Dependencias Node.js instaladas"

# Solucionar vulnerabilidades automáticamente
echo "🔒 Solucionando vulnerabilidades..."
npm audit fix --force 2>/dev/null || echo "⚠️  Algunas vulnerabilidades requieren revisión manual"

# Verificar TypeScript antes del build
echo "🔍 Verificando tipos TypeScript..."
npm run type-check

# Compilar frontend para producción
echo "🔨 Compilando frontend React..."
if npm run build; then
    echo "✅ Frontend compilado en /dist"
else
    echo "❌ Error en el build"
    exit 1
fi

# Verificar archivos compilados
if [ -f "dist/index.html" ]; then
    echo "✅ Build de React generado correctamente"
else
    echo "❌ Error: No se generó index.html"
    exit 1
fi

# Activar nueva arquitectura optimizada
echo "🔧 Configurando arquitectura optimizada..."
if [ -f "main_optimized.py" ]; then
    mv main.py main_legacy.py
    mv main_optimized.py main.py
    echo "✅ Arquitectura optimizada activada"
fi

echo ""
echo "🎉 ¡Configuración completada exitosamente!"
echo ""
echo "🚀 Para iniciar la aplicación:"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "🌐 Accede a la aplicación en:"
echo "   • Aplicación React: http://localhost:8000/"
echo "   • API Docs: http://localhost:8000/docs"
echo "   • Estadísticas: http://localhost:8000/api/stats"
echo "   • Health Check: http://localhost:8000/api/health"
echo ""
echo "🛠️ Para desarrollo del frontend:"
echo "   npm run dev  # http://localhost:3000"
echo ""
echo "✨ Nuevas características:"
echo "   • Arquitectura modular optimizada"
echo "   • Gestión de descargas mejorada" 
echo "   • Procesadores especializados para video/audio"
echo "   • Sistema de monitoreo integrado"