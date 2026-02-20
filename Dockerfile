# Multi-stage build for optimal size
FROM node:20-alpine AS frontend-builder

WORKDIR /app

# Copy frontend dependencies
COPY package*.json ./
COPY tsconfig*.json ./
COPY vite.config.ts ./
COPY tailwind.config.js ./
COPY postcss.config.js ./
COPY eslint.config.js ./
COPY index.html ./

# Install dependencies
RUN npm ci

# Copy source code
COPY src/ ./src/
COPY public/ ./public/

# Build frontend
RUN npm run build

# Final production image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip install --upgrade yt-dlp

# Copy backend code
COPY main.py .
COPY config/ ./config/
COPY downloader/ ./downloader/
COPY utils/ ./utils/
COPY cookies.txt ./cookies.txt

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/dist ./dist
COPY --from=frontend-builder /app/public/icon.svg ./dist/icon.svg

# Copy entrypoint script
COPY docker-entrypoint.sh ./docker-entrypoint.sh
RUN chmod +x docker-entrypoint.sh

# Create downloads directory
RUN mkdir -p downloads public/thumbnails/search

# Expose port
EXPOSE 8000

# Health check — dar 60s de margen para que yt-dlp se actualice al arrancar
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

# Run application via entrypoint (actualiza yt-dlp en cada inicio)
CMD ["/app/docker-entrypoint.sh"]