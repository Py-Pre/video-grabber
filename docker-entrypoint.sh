#!/bin/bash
set -e

echo "🔄 Actualizando yt-dlp a la última versión..."
pip install --upgrade yt-dlp --quiet
echo "✅ yt-dlp $(yt-dlp --version) listo"

echo "� Iniciando PO Token Server (Deno)..."
deno run \
  --allow-net \
  --allow-env \
  --allow-read \  --allow-write=/tmp \  /app/po-token-server.ts &
PO_TOKEN_PID=$!
echo "✅ PO Token Server corriendo (PID: $PO_TOKEN_PID)"

# Esperar a que el servidor de tokens esté listo
echo "⏳ Esperando al PO Token Server..."
for i in $(seq 1 15); do
  if curl -sf http://localhost:10000/health > /dev/null 2>&1; then
    echo "✅ PO Token Server listo"
    break
  fi
  sleep 2
done

echo "�🚀 Iniciando VideoGrabber..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --workers ${WORKERS:-2}
