// Acha elementos cujo CONTEÚDO (texto, filhos) transborda a própria caixa. Uso: node transborda.mjs <arquivo.html> [375]
import { spawn } from "node:child_process";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";
const [arq, larg = "375"] = process.argv.slice(2);
const W = +larg;
const dir = mkdtempSync(join(tmpdir(), "transb-"));
const ch = spawn("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", ["--headless=new", "--remote-debugging-port=9334", `--user-data-dir=${dir}`, "about:blank"], { stdio: "ignore" });
const esperar = (ms) => new Promise((r) => setTimeout(r, ms));
let alvo;
for (let i = 0; i < 50; i++) { try { const l = await (await fetch("http://127.0.0.1:9334/json")).json(); alvo = l.find((x) => x.type === "page"); if (alvo) break; } catch {} await esperar(200); }
const ws = new WebSocket(alvo.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r));
let id = 0; const pend = new Map();
ws.addEventListener("message", (m) => { const d = JSON.parse(m.data); if (d.id && pend.has(d.id)) { pend.get(d.id)(d); pend.delete(d.id); } });
const cmd = (method, params = {}) => new Promise((r) => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
await cmd("Emulation.setDeviceMetricsOverride", { width: W, height: 812, deviceScaleFactor: 1, mobile: false });
await cmd("Page.enable");
await cmd("Page.navigate", { url: pathToFileURL(resolve(arq)).href });
await esperar(2500);
const r = await cmd("Runtime.evaluate", { returnByValue: true, expression: `(() => { const out = [];
  document.querySelectorAll("body, body *").forEach((e) => { const s = getComputedStyle(e); if (e.scrollWidth > e.clientWidth + 1 && s.overflowX === "visible" && e.clientWidth > 0) {
    const b = e.getBoundingClientRect(); out.push((e.tagName + "." + [...e.classList].join(".") + " client=" + e.clientWidth + " scroll=" + e.scrollWidth + " left=" + Math.round(b.left) + " txt=" + (e.textContent || "").trim().slice(0, 60)).slice(0, 200)); } });
  const r = document.createRange(); const tx = []; const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (w.nextNode()) { const n = w.currentNode; if (!n.textContent.trim()) continue; r.selectNodeContents(n); const b = r.getBoundingClientRect(); if (b.right > ${W} + 1) tx.push(Math.round(b.right) + " " + n.parentElement.tagName + "." + [...n.parentElement.classList].join(".") + ": " + n.textContent.trim().slice(0, 70)); }
  return { scroll: document.documentElement.scrollWidth, caixas: out.slice(0, 20), textos: tx.slice(0, 20) }; })()` });
console.log(JSON.stringify(r.result.result.value, null, 1));
ws.close(); ch.kill();
