FROM node:20-alpine AS frontend-builder

WORKDIR /app

COPY package*.json ./
COPY tsconfig*.json ./
COPY vite.config.ts ./
COPY tailwind.config.js ./
COPY postcss.config.js ./
COPY eslint.config.js ./
COPY index.html ./

RUN npm ci

COPY src/ ./src/
COPY public/ ./public/

RUN npm run build

FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Instalar Deno (JS runtime requerido por yt-dlp desde 2025)
RUN curl -fsSL https://deno.land/install.sh | sh
ENV DENO_INSTALL="/root/.deno"
ENV PATH="$DENO_INSTALL/bin:$PATH"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip install --upgrade yt-dlp

COPY main.py .
COPY config/ ./config/
COPY downloader/ ./downloader/
COPY utils/ ./utils/
COPY po-token-server.ts ./po-token-server.ts

COPY --from=frontend-builder /app/dist ./dist
COPY --from=frontend-builder /app/public/icon.svg ./dist/icon.svg

COPY docker-entrypoint.sh ./docker-entrypoint.sh
RUN chmod +x docker-entrypoint.sh

RUN mkdir -p downloads public/thumbnails/search

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["/app/docker-entrypoint.sh"]