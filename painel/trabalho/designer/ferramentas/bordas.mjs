// Lista controles com borda line-strong (#928874) e o fundo efetivo atrás deles. Uso: node bordas.mjs <arquivo.html> [1440]
import { spawn } from "node:child_process";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";
const [arq, larg = "1440"] = process.argv.slice(2);
const W = +larg;
const dir = mkdtempSync(join(tmpdir(), "bordas-"));
const ch = spawn("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", ["--headless=new", "--remote-debugging-port=9335", `--user-data-dir=${dir}`, "about:blank"], { stdio: "ignore" });
const esperar = (ms) => new Promise((r) => setTimeout(r, ms));
let alvo;
for (let i = 0; i < 50; i++) { try { const l = await (await fetch("http://127.0.0.1:9335/json")).json(); alvo = l.find((x) => x.type === "page"); if (alvo) break; } catch {} await esperar(200); }
const ws = new WebSocket(alvo.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r));
let id = 0; const pend = new Map();
ws.addEventListener("message", (m) => { const d = JSON.parse(m.data); if (d.id && pend.has(d.id)) { pend.get(d.id)(d); pend.delete(d.id); } });
const cmd = (method, params = {}) => new Promise((r) => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
await cmd("Emulation.setDeviceMetricsOverride", { width: W, height: 900, deviceScaleFactor: 1, mobile: false });
await cmd("Page.enable");
await cmd("Page.navigate", { url: pathToFileURL(resolve(arq)).href });
await esperar(2500);
const r = await cmd("Runtime.evaluate", { returnByValue: true, expression: `(() => {
  const ALVO = "rgb(146, 136, 116)"; const res = {};
  const fundo = (e) => { let p = e.parentElement; while (p) { const b = getComputedStyle(p).backgroundColor; if (b && b !== "rgba(0, 0, 0, 0)" && b !== "transparent") return b; p = p.parentElement; } return "rgb(245, 242, 232)"; };
  document.querySelectorAll("body *").forEach((e) => { const s = getComputedStyle(e); if (e.offsetParent === null && s.position !== "fixed") return;
    const lados = ["Top","Right","Bottom","Left"].filter((l) => s["border" + l + "Style"] !== "none" && parseFloat(s["border" + l + "Width"]) > 0 && s["border" + l + "Color"] === ALVO);
    if (!lados.length) return; const proprio = s.backgroundColor; const atras = (proprio !== "rgba(0, 0, 0, 0)") ? proprio : fundo(e);
    const k = (e.className && typeof e.className === "string" ? e.className.split(" ").slice(0, 2).join(".") : e.tagName) + " | dentro " + atras + " | atrás " + fundo(e);
    res[k] = (res[k] || 0) + 1; });
  return res; })()` });
console.log(JSON.stringify(r.result.result.value, null, 1));
ws.close(); ch.kill();
