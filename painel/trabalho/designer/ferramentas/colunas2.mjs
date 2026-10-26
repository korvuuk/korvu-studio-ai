// Acha os elementos que passam da largura pedida (emulação de celular via CDP). Uso: node largos.mjs <arquivo.html> [375]
import { spawn } from "node:child_process";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";
const [arq, larg = "375"] = process.argv.slice(2);
const W = +larg;
const dir = mkdtempSync(join(tmpdir(), "largos-"));
const ch = spawn("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", ["--headless=new", "--remote-debugging-port=9333", `--user-data-dir=${dir}`, "about:blank"], { stdio: "ignore" });
const esperar = (ms) => new Promise((r) => setTimeout(r, ms));
let alvo;
for (let i = 0; i < 50; i++) { try { const l = await (await fetch("http://127.0.0.1:9333/json")).json(); alvo = l.find((x) => x.type === "page"); if (alvo) break; } catch {} await esperar(200); }
const ws = new WebSocket(alvo.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r));
let id = 0; const pend = new Map();
ws.addEventListener("message", (m) => { const d = JSON.parse(m.data); if (d.id && pend.has(d.id)) { pend.get(d.id)(d); pend.delete(d.id); } });
const cmd = (method, params = {}) => new Promise((r) => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
await cmd("Emulation.setDeviceMetricsOverride", { width: W, height: 812, deviceScaleFactor: 1, mobile: W < 500 });
await cmd("Page.enable");
await cmd("Page.navigate", { url: pathToFileURL(resolve(arq)).href });
await esperar(2500);
const r = await cmd("Runtime.evaluate", { returnByValue: true, expression: `(() => { const larg=[0,0,0,0,0,0,0]; document.querySelectorAll(".k-pessoa-linha").forEach(l=>[...l.children].forEach((c,i)=>{ if(i<7) larg[i]=Math.max(larg[i], c.scrollWidth); })); const nomesMax=Math.max(...[...document.querySelectorAll(".k-pessoa-nome")].map(e=>{const r=document.createRange(); r.selectNodeContents(e); return Math.ceil(r.getBoundingClientRect().width);})); const nomeMin=Math.min(...[...document.querySelectorAll(".k-pessoa-nome")].map(e=>e.clientWidth)); return {inner: innerWidth, larguraMaxPorColuna: larg, nomeMaisLongo: nomesMax, colunaNomeMenor: nomeMin}; const xs=new Set([...document.querySelectorAll(".k-depto")].map(e=>Math.round(e.getBoundingClientRect().left))); const nome=[...document.querySelectorAll(".k-pessoa-nome")].map(e=>Math.round(e.getBoundingClientRect().width)); return {inner: innerWidth, colunas: xs.size, menorNome: Math.min(...nome)}; const out = []; const W = ${W}; const process_all = true;
  document.querySelectorAll("body *").forEach((e) => { const b = e.getBoundingClientRect(); if (b.width > 0 && b.right > W + 1) {
    let p = e.parentElement, dentro = false; while (p) { const s = getComputedStyle(p); if (s.overflowX === "auto" || s.overflowX === "scroll" || s.overflowX === "hidden") { const pb = p.getBoundingClientRect(); if (pb.right <= W + 1) { dentro = true; break; } } p = p.parentElement; }
    if (!dentro || process_all) out.push((e.tagName + "." + [...e.classList].join(".") + " w=" + Math.round(b.width) + " right=" + Math.round(b.right)).slice(0, 160)); } });
  const t = [...document.querySelectorAll("table")].map((tb) => { const ch = []; let p = tb.parentElement; while (p && p !== document.body) { const s = getComputedStyle(p); ch.push(p.tagName + "." + [...p.classList].join(".") + "[" + s.overflowX + "," + Math.round(p.getBoundingClientRect().width) + "," + s.display + "]"); p = p.parentElement; } return ch.slice(0, 6).join(" < "); });
  return { tabelas: t.slice(0, 8), inner: innerWidth, scroll: document.documentElement.scrollWidth, n: out.length, primeiros: out.slice(0, 25) }; })()` });
console.log(JSON.stringify(r.result.result.value, null, 1));
ws.close(); ch.kill();
