/* Comportamento das MAQUETES (documentação, sem rede). O app faz o mesmo em React — ver painel/design/handoff.md.
   - [data-grupo][data-valor]: botões que trocam a vista (aria-pressed). Painéis [data-de="grupo"][data-valor="a b"]
     aparecem quando o valor escolhido está na lista.
   - [data-filtra="grupo"][data-tags="a b"]: linhas que um filtro esconde ("todos" mostra tudo); [data-busca="grupo"]
     filtra as mesmas linhas pelo texto. Cartão [data-filtra-pai] some quando não sobra linha.
   - .k-pedido: abre/fecha o pedido ao Claude Code; [data-copiar] copia o comando.
   - svg[data-curva]: gráfico de linha desenhado na largura real do card (nada de preserveAspectRatio="none").
   Menu da barra de topo e dicas ([data-dica]) vêm de previas/previa.js. */
(function () {
  "use strict";
  var NS = "http://www.w3.org/2000/svg";
  var nf = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 2 });
  var estado = {};

  function el(tag, attrs, pai) {
    var e = document.createElementNS(NS, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (pai) pai.appendChild(e);
    return e;
  }

  function semAcento(s) { return (s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase(); }

  function filtrar(grupo) {
    var v = estado[grupo] || "todos", q = semAcento(estado["busca:" + grupo] || "").trim();
    document.querySelectorAll('[data-filtra="' + grupo + '"]').forEach(function (l) {
      var tags = (l.getAttribute("data-tags") || "").split(" ");
      var ok = (v === "todos" || tags.indexOf(v) !== -1) && (!q || semAcento(l.textContent).indexOf(q) !== -1);
      l.hidden = !ok;
    });
    document.querySelectorAll('[data-filtra-pai="' + grupo + '"]').forEach(function (p) {
      p.hidden = !p.querySelector('[data-filtra="' + grupo + '"]:not([hidden])');
    });
    document.querySelectorAll('[data-filtra-vazio="' + grupo + '"]').forEach(function (p) {
      p.hidden = !!document.querySelector('[data-filtra="' + grupo + '"]:not([hidden])');
    });
  }

  function aplicar(grupo, valor) {
    estado[grupo] = valor;
    document.querySelectorAll('[data-grupo="' + grupo + '"]').forEach(function (b) {
      b.setAttribute("aria-pressed", b.getAttribute("data-valor") === valor ? "true" : "false");
    });
    document.querySelectorAll('[data-de="' + grupo + '"]').forEach(function (p) {
      p.hidden = (p.getAttribute("data-valor") || "").split(" ").indexOf(valor) === -1;
    });
    filtrar(grupo);
    desenhar();
  }

  /* ---------- Linha (1 ou 2 séries no MESMO eixo), marcos nas datas reais, faixa de hover/foco por dia ---------- */
  function curva(svg) {
    var W = svg.parentNode.clientWidth;
    if (!W) return;
    var c = JSON.parse(svg.getAttribute("data-curva"));
    var H = +(svg.getAttribute("data-altura") || 180), L = 40, R = 12, T = 22, B = 22;
    svg.setAttribute("width", W); svg.setAttribute("height", H); svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    var n = c.rotulos.length - 1;
    function X(i) { return L + (W - L - R) * i / n; }
    function Y(v) { return T + (H - T - B) * (1 - v / c.yMax); }
    c.yTicks.forEach(function (v, k) {
      el("line", { x1: L, x2: W - R, y1: Y(v), y2: Y(v), "class": "grid" }, svg);
      el("text", { x: L - 8, y: Y(v) + 3, "text-anchor": "end" }, svg).textContent = c.yRotulos ? c.yRotulos[k] : nf.format(v);
    });
    c.xTicks.forEach(function (i, k) {
      var a = k === 0 ? "start" : (k === c.xTicks.length - 1 ? "end" : "middle");
      el("text", { x: X(i), y: H - 4, "text-anchor": a }, svg).textContent = c.rotulosEixo[k];
    });
    c.series.forEach(function (s, k) {
      var pts = s.v.map(function (v, i) { return X(i) + "," + Y(v); });
      if (s.area) el("path", { d: "M" + X(0) + "," + Y(0) + "L" + pts.join("L") + "L" + X(n) + "," + Y(0) + "Z", "class": "a1" }, svg);
      el("path", { d: "M" + pts.join("L"), fill: "none", stroke: "var(--" + s.cor + ")", "stroke-width": k === 0 ? 2 : 1.5,
        "stroke-linejoin": "round", "stroke-linecap": "round" }, svg);
    });
    (c.marcos || []).forEach(function (m) {
      var v = c.series[0].v[m.i];
      el("circle", { cx: X(m.i), cy: Y(v), r: 3.5, "stroke-width": 2, style: "fill:var(--surface);stroke:var(--chart-1)" }, svg);
      if (m.rotulo) {
        var a = X(m.i) > W * 0.6 ? "end" : "start";
        el("text", { x: X(m.i) + (a === "end" ? -8 : 8), y: Math.max(12, Y(v) - 8), "text-anchor": a,
          style: "font-weight:600;fill:var(--ink)" }, svg).textContent = m.rotulo;
      }
    });
    var u = c.series[0].v[n];
    el("circle", { cx: X(n), cy: Y(u), r: 4, "stroke-width": 2, style: "fill:var(--chart-1);stroke:var(--surface)" }, svg);
    var cruz = el("line", { y1: T, y2: H - B, stroke: "var(--line-strong)", "stroke-width": 1, visibility: "hidden" }, svg);
    c.rotulos.forEach(function (r, i) {
      var x0 = i ? (X(i - 1) + X(i)) / 2 : L, x1 = i < n ? (X(i) + X(i + 1)) / 2 : W - R;
      var txt = c.series.map(function (s) { return s.nome + " " + (s.fmt ? s.fmt[i] : nf.format(s.v[i])); }).join(" · ");
      var hit = el("rect", { x: x0, y: T, width: Math.max(1, x1 - x0), height: H - T - B, fill: "transparent", tabindex: 0,
        "data-dica": r + "|" + txt, "aria-label": r + ": " + txt }, svg);
      function liga() { cruz.setAttribute("x1", X(i)); cruz.setAttribute("x2", X(i)); cruz.setAttribute("visibility", "visible"); }
      function desliga() { cruz.setAttribute("visibility", "hidden"); }
      hit.addEventListener("pointerenter", liga); hit.addEventListener("focus", liga);
      hit.addEventListener("pointerleave", desliga); hit.addEventListener("blur", desliga);
    });
  }

  function desenhar() { document.querySelectorAll("svg[data-curva]").forEach(curva); }

  document.addEventListener("click", function (e) {
    var b = e.target.closest("[data-grupo]");
    if (b) aplicar(b.getAttribute("data-grupo"), b.getAttribute("data-valor"));
    var abre = e.target.closest("[data-pedido]");
    document.querySelectorAll(".k-pedido.is-aberto").forEach(function (p) {
      if (!abre || p !== abre.closest(".k-pedido")) {
        p.classList.remove("is-aberto");
        var t = p.querySelector("[data-pedido]"); if (t) t.setAttribute("aria-expanded", "false");
      }
    });
    if (abre) {
      var p = abre.closest(".k-pedido"), aberto = p.classList.toggle("is-aberto");
      abre.setAttribute("aria-expanded", aberto ? "true" : "false");
    }
    var cp = e.target.closest("[data-copiar]");
    if (cp && navigator.clipboard) {
      navigator.clipboard.writeText(cp.getAttribute("data-copiar")).then(function () { cp.textContent = "Copiado"; });
    }
  });
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    document.querySelectorAll(".k-pedido.is-aberto").forEach(function (p) {
      p.classList.remove("is-aberto");
      var t = p.querySelector("[data-pedido]"); if (t) { t.setAttribute("aria-expanded", "false"); t.focus(); }
    });
  });
  document.addEventListener("input", function (e) {
    var g = e.target.getAttribute && e.target.getAttribute("data-busca");
    if (g) { estado["busca:" + g] = e.target.value; filtrar(g); }
  });

  document.addEventListener("DOMContentLoaded", function () {
    var grupos = {};
    document.querySelectorAll('[data-grupo][aria-pressed="true"]').forEach(function (b) { grupos[b.getAttribute("data-grupo")] = b.getAttribute("data-valor"); });
    Object.keys(grupos).forEach(function (g) { aplicar(g, grupos[g]); });
    desenhar();
    var t;
    window.addEventListener("resize", function () { clearTimeout(t); t = setTimeout(desenhar, 100); });
  });
})();
