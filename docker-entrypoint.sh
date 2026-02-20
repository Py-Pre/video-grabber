#!/bin/bash
# NO usar set -e — si Deno falla el app debe seguir corriendo igual

echo '🔄 Actualizando yt-dlp...'
pip install --upgrade yt-dlp --quiet && echo '✅ yt-dlp listo' || echo '⚠️ Usando version instalada'

echo '🔑 Iniciando PO Token Server...'
deno run --allow-net --allow-env --allow-read --allow-write=/tmp /app/po-token-server.ts &
PO_TOKEN_PID=$!
echo " ✅ PO Token Server PID: \
