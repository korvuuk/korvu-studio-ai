#!/usr/bin/env bash
# Fotografa telas no Chrome sem janela com EMULAÇÃO DE DISPOSITIVO (CDP Emulation.setDeviceMetricsOverride):
# 1440 px (computador) e 375 px (celular: mobile:true + toque), PÁGINA INTEIRA, medindo innerWidth e scrollWidth de
# cada uma. É como quem constrói e o portão de interface OLHAM a tela de verdade (CLAUDE.md regra 10;
# docs/gauntlet.md, seção do painel). Não usa --window-size: o Chrome sem janela não abre abaixo de 500 px, e o "375"
# antigo era uma página de 500 recortada (PORTÃO-INTERFACE, 22/10).
#
#   bash painel/capturar.sh <pasta de saída> [rota…]          rotas do painel (sem rota: as páginas principais)
#   bash painel/capturar.sh <pasta> --arquivo "painel/design/telas/inicio.html"   maquete local (caminho com espaço ok)
#   bash painel/capturar.sh <pasta> --url https://exemplo.com/pagina              link externo
#   opções: --larguras 1440,375 · --escala 2 (PNG em alta densidade) · --fatias (também corta a página em pedaços
#           da altura de uma tela, para ler no detalhe)
#
# Saída: <nome>-<innerWidth medido>.png (página inteira), <nome>-<largura>-pN.png (com --fatias) e medidas.txt.
# Falha (código 1): se o innerWidth medido não for a largura pedida (para na hora: a foto não seria daquela largura)
# ou se alguma página tiver rolagem lateral (scrollWidth > innerWidth; acusa depois de fotografar tudo, dizendo o
# elemento que passa da borda). Rotas usam o app em PAINEL_URL (padrão http://localhost:3456, o preview "painel").
# Requer o Chrome do sistema e Node ≥ 22 (WebSocket nativo); não instala nada.
set -euo pipefail
command -v node >/dev/null || { echo "precisa do Node ≥ 22 (WebSocket nativo)" >&2; exit 1; }
exec node --input-type=module - "$@" <<'JS'
import { spawn } from "node:child_process";
import { appendFileSync, existsSync, mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { basename, extname, join, relative, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const CHROME = process.env.CHROME_BIN || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const BASE = (process.env.PAINEL_URL || "http://localhost:3456").replace(/\/$/, "");
const PADRAO = ["/", "/equipe", "/equipe/portao-imagem", "/equipe/contratar", "/videos", "/desempenho"];
const ALTURA_TELA = { 1440: 900, 375: 812 }; // altura da janela emulada (a foto é da página inteira)
const MAX_ALTURA = 16000; // limite de textura do Chrome; acima disso a foto usa captureBeyondViewport
const USO = "uso: bash painel/capturar.sh <pasta de saída> [rota…] [--arquivo <html>]… [--url <link>]… " +
  "[--larguras 1440,375] [--escala 1] [--fatias]";
const esperar = (ms) => new Promise((r) => setTimeout(r, ms));
const falhar = (msg) => { console.error(msg); process.exit(1); };
const limpar = (t) => t.normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^\w.-]+/g, "-")
  .replace(/^-+|-+$/g, "").toLowerCase() || "pagina";

// ── argumentos ──
const args = process.argv.slice(2);
let saida = null, larguras = [1440, 375], escala = 1, fatias = false;
const rotas = [], extras = [];
for (let i = 0; i < args.length; i++) {
  const a = args[i];
  if (["--arquivo", "--url", "--larguras", "--escala"].includes(a)) {
    const v = args[++i];
    if (v == null || v === "") falhar(`${a} pede um valor\n${USO}`);
    if (a === "--arquivo") {
      const abs = resolve(v);
      if (!existsSync(abs)) falhar(`arquivo não encontrado: ${abs}`);
      extras.push({ rotulo: relative(process.cwd(), abs) || abs, url: pathToFileURL(abs).href,
        nome: limpar(basename(abs, extname(abs))) });
    } else if (a === "--url") {
      let u;
      try { u = new URL(v); } catch { falhar(`link inválido: ${v}`); }
      if (!/^https?:$/.test(u.protocol)) falhar(`--url aceita só http(s): ${v}`);
      extras.push({ rotulo: u.href, url: u.href, nome: limpar(u.hostname + u.pathname) });
    } else if (a === "--larguras") {
      larguras = v.split(",").map((x) => Number(x.trim()));
      if (larguras.some((n) => !Number.isInteger(n) || n < 200 || n > 4000)) falhar(`--larguras inválidas: ${v}`);
    } else {
      escala = Number(v);
      if (!(escala >= 1 && escala <= 3)) falhar(`--escala entre 1 e 3: ${v}`);
    }
  } else if (a === "--fatias") fatias = true;
  else if (a === "-h" || a === "--help") { console.log(USO); process.exit(0); }
  else if (a.startsWith("--")) falhar(`opção desconhecida: ${a}\n${USO}`);
  else if (saida === null) saida = resolve(a);
  else rotas.push(a.startsWith("/") ? a : `/${a}`);
}
if (!saida) falhar(USO);
if (!rotas.length && !extras.length) rotas.push(...PADRAO);
if (rotas.length) {
  try { await fetch(`${BASE}/`, { signal: AbortSignal.timeout(60000) }); }
  catch { falhar(`o painel não responde em ${BASE} — suba com o preview "painel" (ou indique PAINEL_URL=…)`); }
}
const alvos = [
  ...rotas.map((r) => ({ rotulo: r, url: BASE + r, nome: r === "/" ? "inicio" : limpar(r.replace(/^\//, "").replace(/\//g, "-")) })),
  ...extras,
];
if (!existsSync(CHROME)) falhar(`Chrome não encontrado em ${CHROME} (indique CHROME_BIN=…)`);
mkdirSync(saida, { recursive: true });
const MEDIDAS = join(saida, "medidas.txt");
writeFileSync(MEDIDAS, `# capturar.sh · ${new Date().toISOString()}\n# alvo\tlargura pedida\tinnerWidth\tscrollWidth\taltura\tHTTP\tpng\tpassa da borda\n`);

// ── Chrome sem janela, perfil temporário próprio (nunca o do Carlos) ──
const PORTA = 9400 + Math.floor(Math.random() * 500);
const perfil = mkdtempSync(join(tmpdir(), "capturar-painel-"));
const chrome = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${PORTA}`, `--user-data-dir=${perfil}`,
  "--disable-gpu", "--hide-scrollbars", "--mute-audio", "--no-first-run", "--no-default-browser-check",
  "about:blank"], { stdio: "ignore" });
let ws = null, seq = 0;
const pend = new Map(), ouvintes = new Map();
const fechouChrome = new Promise((res) => chrome.once("exit", res));
const encerrar = async () => {
  try { ws?.close(); } catch {}
  chrome.kill();
  await Promise.race([fechouChrome, esperar(5000)]); // o Chrome ainda grava no perfil enquanto fecha
  try { rmSync(perfil, { recursive: true, force: true, maxRetries: 5, retryDelay: 200 }); } catch {}
};
process.on("SIGINT", async () => { await encerrar(); process.exit(130); });

const cmd = (method, params = {}) => new Promise((res, rej) => {
  const n = ++seq;
  pend.set(n, { res, rej, method });
  ws.send(JSON.stringify({ id: n, method, params }));
});
const evento = (nome, ms) => new Promise((res, rej) => {
  const t = setTimeout(() => { ouvintes.delete(nome); rej(new Error(`${nome} não chegou em ${ms / 1000} s`)); }, ms);
  ouvintes.set(nome, (p) => { clearTimeout(t); ouvintes.delete(nome); res(p); });
});
const avaliar = async (expression) => {
  const r = await cmd("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
  if (r.exceptionDetails) throw new Error(`erro na página: ${r.exceptionDetails.exception?.description ?? r.exceptionDetails.text}`);
  return r.result.value;
};

// Mede a página: larguras, altura e os elementos que passam da borda da janela fora de um contêiner com rolagem ou
// recorte próprio (uma tabela larga dentro de overflow-x-auto é permitida; um texto que empurra a página, não).
const MEDIR = `(() => {
  const de = document.documentElement, vw = innerWidth;
  const contido = (el) => { for (let p = el.parentElement; p && p !== de; p = p.parentElement) {
    if (/(auto|scroll|hidden|clip)/.test(getComputedStyle(p).overflowX)) return true; } return false; };
  const fora = [];
  for (const el of document.body.querySelectorAll("*")) {
    const r = el.getBoundingClientRect();
    if (!r.width && !r.height) continue;
    if (r.right <= vw + 0.5 && r.left >= -0.5) continue;
    if (contido(el)) continue;
    const nome = el.tagName.toLowerCase() + (typeof el.className === "string" && el.className.trim()
      ? "." + el.className.trim().split(/\\s+/).slice(0, 3).join(".") : "");
    fora.push(nome + " [" + Math.round(r.left) + "…" + Math.round(r.right) + "] " +
      JSON.stringify((el.textContent || "").trim().slice(0, 40)));
  }
  return { innerWidth: vw, scrollWidth: Math.max(de.scrollWidth, document.body.scrollWidth),
    altura: Math.ceil(Math.max(de.scrollHeight, document.body.scrollHeight)), fora: fora.slice(0, 4), nFora: fora.length };
})()`;

const problemas = [];
try {
  let alvoWs = null;
  for (let i = 0; i < 60 && !alvoWs; i++) {
    await esperar(250);
    try {
      const lista = await (await fetch(`http://127.0.0.1:${PORTA}/json/list`)).json();
      alvoWs = lista.find((t) => t.type === "page")?.webSocketDebuggerUrl ?? null;
    } catch {}
  }
  if (!alvoWs) throw new Error("o Chrome não abriu (nenhuma página no DevTools)");
  ws = new WebSocket(alvoWs);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = () => rej(new Error("WebSocket do Chrome falhou")); });
  let statusDoc = null;
  ws.onmessage = (e) => {
    const m = JSON.parse(e.data);
    if (m.id && pend.has(m.id)) {
      const p = pend.get(m.id); pend.delete(m.id);
      m.error ? p.rej(new Error(`${p.method}: ${JSON.stringify(m.error)}`)) : p.res(m.result);
    } else if (m.method) {
      if (m.method === "Network.responseReceived" && m.params.type === "Document") statusDoc = m.params.response.status;
      ouvintes.get(m.method)?.(m.params);
    }
  };
  await cmd("Page.enable");
  await cmd("Runtime.enable");
  await cmd("Network.enable");

  for (const alvo of alvos) {
    for (const largura of larguras) {
      const movel = largura < 768;
      const alturaTela = ALTURA_TELA[largura] ?? Math.round(largura * (movel ? 2.165 : 0.625));
      const metricas = (height) => cmd("Emulation.setDeviceMetricsOverride", { width: largura, height,
        deviceScaleFactor: escala, mobile: movel, screenWidth: largura, screenHeight: Math.max(height, alturaTela) });
      await metricas(alturaTela);
      await cmd("Emulation.setTouchEmulationEnabled", movel ? { enabled: true, maxTouchPoints: 5 } : { enabled: false });
      statusDoc = null;
      const carregou = evento("Page.loadEventFired", 60000);
      const nav = await cmd("Page.navigate", { url: alvo.url });
      if (nav.errorText) throw new Error(`não abriu ${alvo.url}: ${nav.errorText}`);
      await carregou;
      await avaliar("(async () => { await document.fonts.ready; await new Promise(r => setTimeout(r, 500)); return 1; })()");
      const med = await avaliar(MEDIR);
      if (med.innerWidth !== largura) {
        throw new Error(`${alvo.rotulo}: pedi ${largura} px e a página abriu com innerWidth ${med.innerWidth} — ` +
          "a foto não seria desta largura; nada foi gravado para ela");
      }
      // página inteira: a janela emulada cresce até a altura do conteúdo (sem recortar em altura fixa)
      const altura = Math.max(alturaTela, med.altura);
      const cabe = altura <= MAX_ALTURA;
      if (cabe) { await metricas(altura); await esperar(250); }
      const png = join(saida, `${alvo.nome}-${med.innerWidth}.png`);
      const foto = await cmd("Page.captureScreenshot", { format: "png", captureBeyondViewport: !cabe,
        clip: { x: 0, y: 0, width: largura, height: altura, scale: 1 } });
      writeFileSync(png, Buffer.from(foto.data, "base64"));
      const pedacos = [];
      if (fatias) {
        for (let y = 0, k = 1; y < altura; y += alturaTela, k++) {
          const f = await cmd("Page.captureScreenshot", { format: "png", captureBeyondViewport: !cabe,
            clip: { x: 0, y, width: largura, height: Math.min(alturaTela, altura - y), scale: 1 } });
          const arq = join(saida, `${alvo.nome}-${med.innerWidth}-p${k}.png`);
          writeFileSync(arq, Buffer.from(f.data, "base64"));
          pedacos.push(arq);
        }
      }
      const rolagem = med.scrollWidth > med.innerWidth;
      const linha = `${rolagem ? "✗" : "✓"} ${alvo.rotulo} · ${largura} px: innerWidth ${med.innerWidth} · ` +
        `scrollWidth ${med.scrollWidth} · altura ${med.altura} px · HTTP ${statusDoc ?? "—"} → ${png}` +
        (pedacos.length ? ` (+${pedacos.length} fatias)` : "") +
        (rolagem ? `\n    ROLAGEM LATERAL: a página passa da janela em ${med.scrollWidth - med.innerWidth} px` : "") +
        (med.nFora ? `\n    passa da borda (${med.nFora}): ${med.fora.join(" · ")}` : "");
      console.log(linha);
      appendFileSync(MEDIDAS, [alvo.rotulo, largura, med.innerWidth, med.scrollWidth, med.altura, statusDoc ?? "—",
        png, med.nFora ? med.fora.join(" · ") : ""].join("\t") + "\n");
      if (rolagem) problemas.push(`${alvo.rotulo} a ${largura} px: scrollWidth ${med.scrollWidth} > innerWidth ${med.innerWidth}`);
    }
  }
} catch (e) {
  console.error(`ERRO: ${e.message}`);
  process.exitCode = 1;
} finally {
  await encerrar();
}
if (problemas.length) {
  console.error(`\n✗ rolagem lateral em ${problemas.length} captura(s):\n  ${problemas.join("\n  ")}`);
  process.exitCode = 1;
}
JS
