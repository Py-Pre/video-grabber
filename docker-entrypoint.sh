#!/bin/bash
# NO usar set -e — si Deno falla el app debe seguir corriendo igual

echo '🔄 Actualizando yt-dlp...'
pip install --upgrade yt-dlp --quiet && echo '✅ yt-dlp listo' || echo '⚠️ Usando version instalada'

echo '🔑 Iniciando PO Token Server...'
deno run --allow-net --allow-env --allow-read --allow-write=/tmp /app/po-token-server.ts &
PO_TOKEN_PID=\$!
echo \"✅ PO Token Server PID: \$PO_TOKEN_PID\"

echo '⏳ Esperando PO Token Server...'
for i in \$(seq 1 15); do
  if curl -sf http://127.0.0.1:10000/health > /dev/null 2>&1; then
    echo '✅ PO Token Server listo'
    break
  fi
  if [ \$i -eq 15 ]; then
    echo '⚠️ PO Token Server no respondio, continuando...'
  fi
  sleep 2
done

echo '🚀 Iniciando VideoGrabber puerto 8000...'
exec uvicorn main:app --host 0.0.0.0 --port 8000 --workers \${WORKERS:-2}
