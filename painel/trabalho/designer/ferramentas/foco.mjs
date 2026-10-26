// Acha elementos cujo CONTEÚDO (texto, filhos) transborda a própria caixa. Uso: node transborda.mjs <arquivo.html> [375]
import { spawn } from "node:child_process";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";
const [arq, larg = "375"] = process.argv.slice(2);
const W = +larg;
const dir = mkdtempSync(join(tmpdir(), "foco-"));
const ch = spawn("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", ["--headless=new", "--remote-debugging-port=9336", `--user-data-dir=${dir}`, "about:blank"], { stdio: "ignore" });
const esperar = (ms) => new Promise((r) => setTimeout(r, ms));
let alvo;
for (let i = 0; i < 50; i++) { try { const l = await (await fetch("http://127.0.0.1:9336/json")).json(); alvo = l.find((x) => x.type === "page"); if (alvo) break; } catch {} await esperar(200); }
const ws = new WebSocket(alvo.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r));
let id = 0; const pend = new Map();
ws.addEventListener("message", (m) => { const d = JSON.parse(m.data); if (d.id && pend.has(d.id)) { pend.get(d.id)(d); pend.delete(d.id); } });
const cmd = (method, params = {}) => new Promise((r) => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
await cmd("Emulation.setDeviceMetricsOverride", { width: W, height: 812, deviceScaleFactor: 1, mobile: false });
await cmd("Page.enable");
await cmd("Page.navigate", { url: pathToFileURL(resolve(arq)).href });
await esperar(2500);
// Foco pelo teclado (Tab) e a cor do anel em cada fundo. Uso: node foco.mjs <arquivo.html> [largura]
await cmd("Runtime.evaluate", { expression: "document.activeElement && document.activeElement.blur()" });
const saida = {};
for (let i = 0; i < 60; i++) {
  await cmd("Input.dispatchKeyEvent", { type: "keyDown", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
  await cmd("Input.dispatchKeyEvent", { type: "keyUp", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
  const r = await cmd("Runtime.evaluate", { returnByValue: true, expression: `(() => { const e = document.activeElement; if (!e) return null; const s = getComputedStyle(e);
    const onde = e.closest(".k-sidebar") ? "barra lateral" : e.closest(".k-topbar") ? "barra de topo" : "área clara";
    return (s.outlineStyle === "none" ? (e.tagName + "." + [...e.classList].join(".") + "[" + (e.getAttribute("aria-label")||e.placeholder||"").slice(0,30) + "] ") : "") + onde + " | " + s.outlineStyle + " " + s.outlineWidth + " " + s.outlineColor + " | visível=" + e.matches(":focus-visible"); })()` });
  const v = r.result.result.value; if (v) saida[v] = (saida[v] || 0) + 1;
}
console.log(JSON.stringify(saida, null, 1));
ws.close(); ch.kill();
