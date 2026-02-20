/**
 * PO Token Server para yt-dlp
 * Basado en: https://github.com/iv-org/youtube-po-token-generator
 * Genera Proof of Origin tokens que YouTube requiere para IPs de servidores (2024+)
 * Corre en Deno en background y yt-dlp lo consulta vía --extractor-args
 */

import { Innertube, UniversalCache } from "npm:youtubei.js@13";

const PORT = parseInt(Deno.env.get("PO_TOKEN_PORT") || "10000");

let cachedToken: { visitorData: string; poToken: string; expiresAt: number } | null = null;
const TOKEN_TTL_MS = 6 * 60 * 60 * 1000; // 6 horas

async function generateToken() {
  const now = Date.now();
  if (cachedToken && cachedToken.expiresAt > now) {
    return cachedToken;
  }

  console.log("[po-token-server] Generando nuevo PO Token...");
  const yt = await Innertube.create({ cache: new UniversalCache(false) });
  const visitorData = yt.session.context.client.visitorData || "";
  const poToken = await yt.session.po_token || "";

  cachedToken = {
    visitorData,
    poToken,
    expiresAt: now + TOKEN_TTL_MS,
  };

  console.log(`[po-token-server] Token generado. Visitor: ${visitorData.slice(0, 20)}...`);
  return cachedToken;
}

Deno.serve({ port: PORT, hostname: "0.0.0.0" }, async (req) => {
  const url = new URL(req.url);

  if (url.pathname === "/token") {
    try {
      const token = await generateToken();
      return Response.json(token);
    } catch (err) {
      console.error("[po-token-server] Error generando token:", err);
      return Response.json({ error: String(err) }, { status: 500 });
    }
  }

  if (url.pathname === "/health") {
    return Response.json({ status: "ok", port: PORT });
  }

  return Response.json({ error: "Not found" }, { status: 404 });
});

console.log(`[po-token-server] Servidor corriendo en http://localhost:${PORT}`);

// Genera un token inicial al arrancar
generateToken().catch(console.error);
