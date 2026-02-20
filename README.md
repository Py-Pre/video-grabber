# 🎥 VideoGrabber 1.0

**Descargador moderno de videos y audio con interfaz web intuitiva**

VideoGrabber es una aplicación web completa que permite descargar videos y audios de múltiples plataformas de manera sencilla y eficiente. Construido con tecnologías modernas para garantizar rapidez, estabilidad y una excelente experiencia de usuario.

## ✨ Características Principales

### 🚀 **Interfaz Moderna**

- **Frontend React + TypeScript**: Interfaz responsive y moderna
- **Tailwind CSS**: Diseño elegante y adaptable
- **Componentes interactivos**: Preview de videos, selección de calidad, progreso de descarga

### ⚡ **Rendimiento Optimizado**

- **FastAPI Backend**: API rápida y eficiente
- **Arquitectura modular**: Código organizado y mantenible
- **Timeouts inteligentes**: Evita cargas indefinidas (15 segundos máximo)
- **Manejo de errores**: Mensajes claros y útiles

### 🌍 **Soporte Multi-Plataforma**

- **YouTube**: Videos individuales, shorts, música
- **YouTube Music**: Audio en alta calidad
- **Otras plataformas**: Vimeo, Facebook, TikTok, Instagram
- **URLs de playlist**: Procesamiento inteligente de video individual

### 📱 **Formatos y Calidades**

- **Video**: MP4, WebM, MKV (1080p, 720p, 480p, 360p)
- **Audio**: MP3, M4A, AAC, FLAC (128k, 256k, 320k)
- **Conversión automática**: Optimización de compatibilidad
- **Metadatos**: Preservación de título, artista, thumbnail

## 🛠️ Tecnologías Utilizadas

### **Backend**

- **FastAPI**: Framework web moderno para Python
- **yt-dlp**: Motor de extracción de videos actualizado
- **Uvicorn**: Servidor ASGI de alto rendimiento
- **Asyncio**: Procesamiento asíncrono eficiente

### **Frontend**

- **React 18.3.1**: Biblioteca de UI componencial
- **TypeScript 5.7.2**: Tipado estático para JavaScript
- **Tailwind CSS 3.4.15**: Framework de utilidades CSS
- **Vite 6.0.4**: Build tool ultra-rápido
- **Axios**: Cliente HTTP para comunicación con API

### **Herramientas de Desarrollo**

- **ESLint**: Linting de código JavaScript/TypeScript
- **PostCSS**: Procesamiento de CSS
- **Autoprefixer**: Compatibilidad automática de navegadores

## 📋 Requisitos del Sistema

### **Software Necesario**

- **Python 3.8+**: Lenguaje del backend
- **Node.js 18+**: Runtime para el frontend
- **FFmpeg**: Conversión y procesamiento de medios
- **Git**: Control de versiones

### **Sistemas Operativos Soportados**

- **Linux**: Ubuntu 20.04+ (recomendado)
- **Windows**: 10/11 con WSL2
- **macOS**: 10.15+ (Catalina)

## 🚀 Instalación y Configuración

### **Instalación Automática**

```bash
# Clona el repositorio
git clone https://github.com/tu-usuario/videograbber.git
cd videograbber

# Ejecuta el script de configuración
chmod +x setup.sh
./setup.sh
```

### **Instalación Manual**

#### 1. **Configuar el Backend Python**

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

#### 2. **Configurar el Frontend React**

```bash
# Instalar dependencias de Node.js
npm install

# Compilar la aplicación
npm run build
```

#### 3. **Instalar FFmpeg**

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# CentOS/RHEL
sudo yum install ffmpeg

# macOS (con Homebrew)
brew install ffmpeg
```

## 🎯 Uso de la Aplicación

### **Iniciar el Servidor**

```bash
# Script de inicio rápido
./start.sh

# O manualmente
source venv/bin/activate
python main.py
```

### **Acceder a la Aplicación**

- **Aplicación Web**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs
- **Servidor de desarrollo**: http://localhost:3000 (opcional)

### **Descargar un Video**

1. **Abre la aplicación** en tu navegador
2. **Pega la URL** del video en el campo de entrada
3. **Selecciona el formato** y calidad deseada
4. **Haz clic en descargar** y espera a que complete

### **Ejemplos de URLs Soportadas**

```
# YouTube videos
https://www.youtube.com/watch?v=VIDEO_ID
https://youtu.be/VIDEO_ID

# YouTube con parámetros de playlist (se limpian automáticamente)
https://www.youtube.com/watch?v=VIDEO_ID&list=PLAYLIST&start_radio=1

# Otras plataformas
https://vimeo.com/123456789
https://www.facebook.com/username/videos/123456789
https://www.tiktok.com/@username/video/123456789
```

## 📁 Estructura del Proyecto

```
videograbber/
├── 🐍 Backend (Python)
│   ├── main.py                 # Servidor FastAPI principal
│   ├── requirements.txt        # Dependencias Python
│   ├── config/                 # Configuraciones
│   │   ├── __init__.py
│   │   └── settings.py         # Ajustes globales
│   ├── downloader/            # Módulos de descarga
│   │   ├── __init__.py
│   │   ├── download_manager.py # Coordinador principal
│   │   ├── video_processor.py  # Procesador de videos
│   │   └── audio_processor.py  # Procesador de audios
│   └── utils/                 # Utilidades
│       ├── __init__.py
│       └── validators.py      # Validación de URLs
├── ⚛️ Frontend (React)
│   ├── src/                   # Código fuente React
│   │   ├── components/        # Componentes UI
│   │   ├── hooks/            # Hooks personalizados
│   │   ├── types/            # Definiciones TypeScript
│   │   └── utils/            # Utilidades frontend
│   ├── public/               # Recursos estáticos
│   ├── dist/                 # Build de producción
│   ├── package.json          # Dependencias Node.js
│   └── vite.config.ts        # Configuración Vite
├── 🔧 Scripts
│   ├── setup.sh              # Configuración inicial
│   └── start.sh              # Inicio rápido
└── 📄 Documentación
    └── README.md             # Este archivo
```

## ⚙️ Configuración Avanzada

### **Variables de Entorno**

```bash
# Puerto del servidor (por defecto: 8000)
export PORT=8000

# Modo de depuración
export DEBUG=true

# Directorio de descargas
export DOWNLOAD_DIR=./downloads
```

### **Configuración de Descarga**

Edita `config/settings.py` para personalizar:

- **Timeouts**: Tiempo máximo de espera
- **Formatos preferidos**: Prioridad de calidades
- **Límites de tamaño**: Archivos máximos permitidos

## 🔍 Solución de Problemas

### **Error: "El video está tardando demasiado"**

- **Causa**: Timeout de 15 segundos excedido
- **Solución**: Verifica tu conexión a internet o intenta con otro video

### **Error: "Video no disponible"**

- **Causa**: Video privado, eliminado o restringido
- **Solución**: Verifica que el video sea público y accesible

### **Error: "FFmpeg no encontrado"**

- **Causa**: FFmpeg no instalado en el sistema
- **Solución**: `sudo apt install ffmpeg` (Ubuntu) o instalar según tu OS

### **Error: "Plataforma no soportada"**

- **Causa**: URL de sitio no compatible
- **Solución**: Usa URLs de YouTube, Vimeo, TikTok, Facebook, Instagram

## 🚀 Desarrollo

### **Ejecutar en Modo Desarrollo**

```bash
# Backend (con recarga automática)
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend (servidor de desarrollo)
npm run dev
```

### **Comandos de Desarrollo**

```bash
# Verificar tipos TypeScript
npm run type-check

# Linting y corrección
npm run lint
npm run lint:fix

# Build optimizado
npm run build
```

## 📊 API Endpoints

### **POST `/api/info`**

Obtiene información del video

```json
{
  "url": "https://youtube.com/watch?v=VIDEO_ID"
}
```

### **GET `/api/download`**

Descarga video/audio

```
GET /api/download?url=VIDEO_URL&format_id=FORMAT&format_type=video
```

### **GET `/docs`**

Documentación interactiva de la API (Swagger UI)

## 👥 Contribuir

1. **Fork** el repositorio
2. **Crea** una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. **Commit** tus cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. **Push** a la rama (`git push origin feature/nueva-funcionalidad`)
5. **Abre** un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia **MIT**. Ver archivo `LICENSE` para más detalles.

## 🆘 Soporte

Si encuentras algún problema o tienes preguntas:

1. **Revisa** la sección de solución de problemas
2. **Busca** en los issues existentes
3. **Crea** un nuevo issue con detalles del problema
4. **Incluye** logs relevantes y pasos para reproducir

## 🙏 Agradecimientos

- **yt-dlp**: Motor principal de extracción de videos
- **FastAPI**: Framework web moderno y rápido
- **React**: Biblioteca para interfaces de usuario
- **Tailwind CSS**: Framework de utilidades CSS

---

**🎬 ¡Disfruta descargando tus videos y audios favoritos con VideoGrabber 1.0!**
