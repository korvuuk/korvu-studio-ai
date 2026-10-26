/**
 * Captura uma animação do Claude Design (HTML com `window.seek(t)`) como vídeo, quadro a quadro.
 *
 * É o caminho do §3 da skill `animacoes-explicativas`: quando portar o export para Remotion é inviável
 * (JSX compilado no browser, 150 KB+), o determinismo vem do próprio `seek(t)` — nada de relógio real.
 *
 * Uso:
 *   node scripts/capturar_animacao.mjs <animacao.html> <saida.mp4> [--dur 39.56] [--fps 25]
 *       [--clip x,y,w,h]   recorte em px (padrão: acha sozinho o maior elemento 16:9 = o palco sem a
 *                          barra de player que o Claude Design desenha embaixo)
 *       [--warp mapa.json] [[tExport, tReal], …] — encaixa as cenas na fala (piecewise linear)
 *
 * Requer o Chrome do sistema; não instala nada (Node ≥ 22 já tem WebSocket).
 */
import { spawn, spawnSync } from "node:child_process";
import { mkdtempSync, writeFileSync, rmSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";

const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const FFMPEG = process.env.FFMPEG_BIN || "/Users/teste/bin/ffmpeg";
const PORT = 9333 + Math.floor(Math.random() * 400);

const args = process.argv.slice(2);
const opcao = (nome, padrao) => {
  const i = args.indexOf(nome);
  return i >= 0 && args[i + 1] ? args[i + 1] : padrao;
};
const posicionais = args.filter((a, i) => !a.startsWith("--") && !args[i - 1]?.startsWith("--"));
// caminho ABSOLUTO: `file://` com caminho relativo não abre nada e a página nunca expõe seek()
const ARQ = posicionais[0] ? resolve(posicionais[0]) : null;
const SAIDA = posicionais[1] ? resolve(posicionais[1]) : null;
const FPS = Number(opcao("--fps", "25"));
const esperar = (ms) => new Promise((r) => setTimeout(r, ms));

/** [[tExport, tReal], …] → tempo do export para um tempo da timeline final. */
const fazerWarp = (mapa) => (tReal) => {
  if (!mapa || mapa.length < 2) return tReal;
  for (let i = 0; i < mapa.length - 1; i++) {
    const [e0, r0] = mapa[i];
    const [e1, r1] = mapa[i + 1];
    if (tReal <= r1 || i === mapa.length - 2) {
      const f = r1 === r0 ? 0 : (tReal - r0) / (r1 - r0);
      return e0 + f * (e1 - e0);
    }
  }
  return tReal;
};

let ws, id = 0;
const pend = new Map();
const cmd = (method, params = {}) =>
  new Promise((res, rej) => {
    const n = ++id;
    pend.set(n, { res, rej });
    ws.send(JSON.stringify({ id: n, method, params }));
  });

const chrome = spawn(
  CHROME,
  ["--headless=new", `--remote-debugging-port=${PORT}`, "--disable-gpu", "--hide-scrollbars",
   "--mute-audio", "--window-size=1920,1080", "file://" + encodeURI(ARQ)],
  { stdio: "ignore" },
);
const pasta = mkdtempSync(join(tmpdir(), "anim-"));

try {
  if (!ARQ || !SAIDA) throw new Error("uso: capturar_animacao.mjs <html> <saida.mp4> [--dur s] [--fps n]");
  let alvo = null;
  for (let i = 0; i < 40 && !alvo; i++) {
    await esperar(250);
    try {
      const lista = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
      alvo = (lista.find((t) => t.type === "page") || {}).webSocketDebuggerUrl || null;
    } catch {}
  }
  if (!alvo) throw new Error("Chrome não abriu (alvo de página não encontrado)");
  ws = new WebSocket(alvo);
  await new Promise((r) => (ws.onopen = r));
  ws.onmessage = (e) => {
    const m = JSON.parse(e.data);
    const p = pend.get(m.id);
    if (p) {
      pend.delete(m.id);
      m.error ? p.rej(new Error(JSON.stringify(m.error))) : p.res(m.result);
    }
  };
  await cmd("Page.enable");
  await cmd("Runtime.enable");
  await cmd("Emulation.setDeviceMetricsOverride", { width: 1920, height: 1080, deviceScaleFactor: 1, mobile: false });

  // espera a página montar (o export compila JSX no browser) e descobre o palco 16:9
  const info = await cmd("Runtime.evaluate", {
    returnByValue: true, awaitPromise: true, expression: `
    (async () => {
      for (let i = 0; i < 120 && typeof window.seek !== "function"; i++) await new Promise(r => setTimeout(r, 100));
      const caixas = [...document.querySelectorAll("div")].map(e => {
        const r = e.getBoundingClientRect();
        return { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) };
      }).filter(r => r.w >= 600 && r.h >= 300 && Math.abs(r.w / r.h - 16 / 9) < 0.04
        // o container do tamanho da janela contém a barra de player que o Claude Design desenha embaixo:
        // ele também é 16:9 quando a viewport é 16:9, então tem de ficar de fora da escolha
        && !(r.w >= innerWidth - 2 && r.h >= innerHeight - 2));
      caixas.sort((a, b) => b.w * b.h - a.w * a.h);
      return { temSeek: typeof window.seek === "function", duracao: window.DURACAO, palco: caixas[0] || null };
    })()` });
  const { temSeek, duracao, palco } = info.result.value;
  if (!temSeek) throw new Error("a página não expõe window.seek(t) — sem isso a captura não é determinística");

  const DUR = Number(opcao("--dur", String(duracao || 0)));
  if (!DUR) throw new Error("duração desconhecida: passe --dur <segundos>");
  const recorteArg = opcao("--clip", null);
  const clip = recorteArg
    ? Object.fromEntries(["x", "y", "width", "height"].map((k, i) => [k, Number(recorteArg.split(",")[i])]))
    : palco
      ? { x: palco.x, y: palco.y, width: palco.w, height: palco.h }
      : { x: 0, y: 0, width: 1920, height: 1080 };
  clip.scale = 1;
  const mapaArq = opcao("--warp", null);
  const warp = fazerWarp(mapaArq ? JSON.parse(readFileSync(mapaArq, "utf8")) : null);

  const total = Math.round(DUR * FPS);
  console.log(`palco ${clip.width}×${clip.height} em (${clip.x},${clip.y}) · ${total} quadros a ${FPS} fps` +
              (mapaArq ? " · com encaixe na fala" : ""));
  await cmd("Runtime.evaluate", { expression: "window.PAUSED = true;" });
  for (let i = 0; i < total; i++) {
    const t = warp(i / FPS);
    await cmd("Runtime.evaluate", { expression: `window.seek(${t.toFixed(4)})`, awaitPromise: true });
    const shot = await cmd("Page.captureScreenshot", { format: "png", clip, captureBeyondViewport: false });
    writeFileSync(join(pasta, String(i).padStart(5, "0") + ".png"), Buffer.from(shot.data, "base64"));
    if (i % 100 === 0) console.log(`  ${i}/${total}`);
  }

  const r = spawnSync(FFMPEG, ["-y", "-loglevel", "error", "-framerate", String(FPS),
    "-i", join(pasta, "%05d.png"), "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p",
    "-vf", "scale=1920:-2", SAIDA], { stdio: "inherit" });
  if (r.status !== 0) throw new Error("ffmpeg falhou ao montar o vídeo");
  console.log(`pronto: ${SAIDA} (${(total / FPS).toFixed(2)}s)`);
} catch (e) {
  console.error("ERRO:", e.message);
  process.exitCode = 1;
} finally {
  try { ws?.close(); } catch {}
  chrome.kill();
  rmSync(pasta, { recursive: true, force: true });
}
