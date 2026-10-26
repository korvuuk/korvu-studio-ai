// Acha elementos cujo CONTEÚDO (texto, filhos) transborda a própria caixa. Uso: node transborda.mjs <arquivo.html> [375]
import { spawn } from "node:child_process";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";
const [arq, larg = "375"] = process.argv.slice(2);
const W = +larg;
const dir = mkdtempSync(join(tmpdir(), "amostra-"));
const ch = spawn("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", ["--headless=new", "--remote-debugging-port=9337", `--user-data-dir=${dir}`, "about:blank"], { stdio: "ignore" });
const esperar = (ms) => new Promise((r) => setTimeout(r, ms));
let alvo;
for (let i = 0; i < 50; i++) { try { const l = await (await fetch("http://127.0.0.1:9337/json")).json(); alvo = l.find((x) => x.type === "page"); if (alvo) break; } catch {} await esperar(200); }
const ws = new WebSocket(alvo.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r));
let id = 0; const pend = new Map();
ws.addEventListener("message", (m) => { const d = JSON.parse(m.data); if (d.id && pend.has(d.id)) { pend.get(d.id)(d); pend.delete(d.id); } });
const cmd = (method, params = {}) => new Promise((r) => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
await cmd("Emulation.setDeviceMetricsOverride", { width: W, height: 812, deviceScaleFactor: 1, mobile: false });
await cmd("Page.enable");
await cmd("Page.navigate", { url: pathToFileURL(resolve(arq)).href });
await esperar(2500);
// Fotografa cada amostra (fontes e legenda) em 2x. Uso: node amostras.mjs amostras.html <pasta-de-saida>
import { writeFileSync } from "node:fs";
const out = process.argv[4];
await cmd("Emulation.setDeviceMetricsOverride", { width: W, height: 812, deviceScaleFactor: 2, mobile: false });
await cmd("Page.navigate", { url: pathToFileURL(resolve(arq)).href });
await esperar(4000);
const fontes = await cmd("Runtime.evaluate", { returnByValue: true, awaitPromise: true, expression: "document.fonts.ready.then(() => [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family + ' ' + f.weight + ' ' + f.style))" });
console.log("fontes carregadas:", JSON.stringify(fontes.result.result.value));
for (const [id, nome] of [["geist", "fonte-geist"], ["bricolage", "fonte-bricolage-grotesque"], ["inter", "fonte-inter"], ["playfair", "fonte-playfair-display"], ["legenda", "legenda-texto-selecionado"]]) {
  const r = await cmd("Runtime.evaluate", { returnByValue: true, expression: `(() => { const b = document.getElementById("${id}").getBoundingClientRect(); return {x:b.x,y:b.y,w:b.width,h:b.height}; })()` });
  const b = r.result.result.value;
  const s = await cmd("Page.captureScreenshot", { format: "png", clip: { x: b.x, y: b.y, width: b.w, height: b.h, scale: 1 } });
  writeFileSync(`${out}/${nome}.png`, Buffer.from(s.result.data, "base64"));
  console.log(nome, Math.round(b.w), "x", Math.round(b.h));
}
ws.close(); ch.kill();
