/* Comportamento das PRÉVIAS (documentação, sem rede): menu da barra de topo, dicas flutuantes e o desenho dos
   gráficos na largura real do contêiner (nada de preserveAspectRatio="none", que entorta o texto dos eixos).
   O app implementa o mesmo comportamento em React — ver painel/design/handoff.md. */
(function () {
  "use strict";
  var NS = "http://www.w3.org/2000/svg";
  var nf = new Intl.NumberFormat("pt-BR");

  function el(tag, attrs, pai) {
    var e = document.createElementNS(NS, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (pai) pai.appendChild(e);
    return e;
  }

  /* ---------- Menu da barra de topo (< 1024px) ---------- */
  function iniciarMenu() {
    document.querySelectorAll(".k-menu-btn").forEach(function (btn) {
      var casca = btn.closest(".k-shell");
      if (!casca) return;
      function pintar(aberto) {
        casca.classList.toggle("is-menu-open", aberto);
        btn.setAttribute("aria-expanded", aberto ? "true" : "false");
        btn.innerHTML = (aberto ? "Fechar" : "Menu") + window.Korvu.icon(aberto ? "x" : "chevron-down", 16);
      }
      pintar(casca.classList.contains("is-menu-open"));
      btn.addEventListener("click", function () { pintar(!casca.classList.contains("is-menu-open")); });
      document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && casca.classList.contains("is-menu-open")) { pintar(false); btn.focus(); }
      });
    });
  }

  /* ---------- Dica flutuante: [data-dica="linha 1|linha 2"] ---------- */
  var dica = null, timer = null;
  function abrirDica(alvo) {
    var partes = (alvo.getAttribute("data-dica") || "").split("|");
    if (!dica) {
      dica = document.createElement("div");
      dica.className = "k-tooltip is-floating";
      dica.setAttribute("role", "tooltip");
      document.body.appendChild(dica);
    }
    dica.innerHTML = "<b></b>" + (partes[1] ? "<small></small>" : "");
    dica.querySelector("b").textContent = partes[0];
    if (partes[1]) dica.querySelector("small").textContent = partes[1];
    dica.style.left = "0px"; dica.style.top = "0px"; dica.style.display = "inline-flex";
    var r = alvo.getBoundingClientRect(), d = dica.getBoundingClientRect();
    var vw = document.documentElement.clientWidth, M = 8;
    var x = Math.max(M, Math.min(r.left + r.width / 2 - d.width / 2, vw - d.width - M));
    var y = r.top - d.height - 10;
    if (y < M) y = r.bottom + 10;
    dica.style.left = Math.round(x) + "px";
    dica.style.top = Math.round(y) + "px";
    dica.style.setProperty("--seta-x", Math.round(r.left + r.width / 2 - x) + "px");
  }
  function fecharDica() { clearTimeout(timer); if (dica) dica.style.display = "none"; }
  function iniciarDicas() {
    document.addEventListener("pointerover", function (e) {
      var a = e.target.closest && e.target.closest("[data-dica]");
      if (!a) return;
      clearTimeout(timer);
      timer = setTimeout(function () { abrirDica(a); }, 300); /* --atraso-dica */
    });
    document.addEventListener("pointerout", function (e) {
      var a = e.target.closest && e.target.closest("[data-dica]");
      if (a && !a.contains(e.relatedTarget)) fecharDica();
    });
    document.addEventListener("focusin", function (e) {
      var a = e.target.closest && e.target.closest("[data-dica]");
      if (a) { clearTimeout(timer); timer = setTimeout(function () { abrirDica(a); }, 300); }
    });
    document.addEventListener("focusout", fecharDica);
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") fecharDica(); });
    window.addEventListener("scroll", fecharDica, { passive: true });
  }

  /* ---------- Gráfico de linha/área (2 séries no MESMO eixo) ---------- */
  function linha(svg) {
    var cfg = JSON.parse(svg.getAttribute("data-linha"));
    var W = svg.parentNode.clientWidth, H = 180, L = 34, R = 44, T = 10, B = 24;
    svg.setAttribute("width", W); svg.setAttribute("height", H); svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    var xMax = cfg.xMax, yMax = cfg.yMax;
    function X(v) { return L + (W - L - R) * v / xMax; }
    function Y(v) { return T + (H - T - B) * (1 - v / yMax); }
    cfg.yTicks.forEach(function (v) {
      el("line", { x1: L, x2: W - R, y1: Y(v), y2: Y(v), "class": "grid" }, svg);
      el("text", { x: L - 6, y: Y(v) + 3, "text-anchor": "end" }, svg).textContent = nf.format(v);
    });
    cfg.xTicks.forEach(function (v) {
      el("text", { x: X(v), y: H - 6, "text-anchor": "middle" }, svg).textContent = "dia " + nf.format(v);
    });
    var s1 = cfg.series[0], s2 = cfg.series[1];
    var p1 = cfg.x.map(function (x, i) { return X(x) + "," + Y(s1.v[i]); });
    var p2 = cfg.x.map(function (x, i) { return X(x) + "," + Y(s2.v[i]); });
    el("path", { d: "M" + X(cfg.x[0]) + "," + Y(0) + "L" + p1.join("L") + "L" + X(cfg.x[cfg.x.length - 1]) + "," + Y(0) + "Z", "class": "a1" }, svg);
    el("path", { d: "M" + p2.join("L"), "class": "s2" }, svg);
    el("path", { d: "M" + p1.join("L"), "class": "s1" }, svg);
    var n = cfg.x.length - 1;
    el("circle", { cx: X(cfg.x[n]), cy: Y(s1.v[n]), r: 4, fill: "var(--surface)", stroke: "var(--accent)", "stroke-width": 2 }, svg);
    /* rótulo direto só no fim de cada linha (texto em ink-2, nunca na cor da série) */
    el("text", { x: X(cfg.x[n]) + 8, y: Y(s1.v[n]) + 4 }, svg).textContent = nf.format(s1.v[n]);
    el("text", { x: X(cfg.x[n]) + 8, y: Y(s2.v[n]) + 4 }, svg).textContent = nf.format(s2.v[n]);
    /* camada de hover/foco: uma faixa por leitura, maior que a marca */
    var cruz = el("line", { y1: T, y2: H - B, stroke: "var(--line-strong)", "stroke-width": 1, visibility: "hidden" }, svg);
    cfg.x.forEach(function (x, i) {
      var meio = X(x), ant = i ? X(cfg.x[i - 1]) : L, prox = i < n ? X(cfg.x[i + 1]) : W - R;
      var x0 = i ? (ant + meio) / 2 : L, x1 = i < n ? (meio + prox) / 2 : W - R;
      var r = el("rect", { x: x0, y: T, width: Math.max(24, x1 - x0), height: H - T - B, fill: "transparent", tabindex: 0,
        "data-dica": cfg.rotulos[i] + "|" + s1.nome + " " + nf.format(s1.v[i]) + " · " + s2.nome + " " + nf.format(s2.v[i]),
        "aria-label": cfg.rotulos[i] + ": " + s1.nome + " " + nf.format(s1.v[i]) + ", " + s2.nome + " " + nf.format(s2.v[i]) }, svg);
      r.addEventListener("pointerenter", function () { cruz.setAttribute("x1", meio); cruz.setAttribute("x2", meio); cruz.setAttribute("visibility", "visible"); });
      r.addEventListener("focus", function () { cruz.setAttribute("x1", meio); cruz.setAttribute("x2", meio); cruz.setAttribute("visibility", "visible"); });
      r.addEventListener("pointerleave", function () { cruz.setAttribute("visibility", "hidden"); });
      r.addEventListener("blur", function () { cruz.setAttribute("visibility", "hidden"); });
    });
  }

  /* ---------- Sparkline 120×28: tendência sem eixos, ponto final marcado ---------- */
  function sparkline(svg) {
    var d = JSON.parse(svg.getAttribute("data-spark"));
    var w = +svg.getAttribute("width"), h = +svg.getAttribute("height");
    var xs = d.x, ys = d.y, xMax = xs[xs.length - 1], yMin = Math.min.apply(0, ys), yMax = Math.max.apply(0, ys);
    var pts = xs.map(function (x, i) { return [2 + (w - 4) * x / xMax, h - 3 - (ys[i] - yMin) / (yMax - yMin) * (h - 6)]; });
    el("path", { d: "M" + pts.map(function (p) { return p.join(","); }).join("L"), "class": "s1" }, svg);
    var u = pts[pts.length - 1];
    el("circle", { cx: u[0], cy: u[1], r: 2.5, "class": "f1" }, svg);
  }

  /* ---------- Rosca (donut): ≤ 4 fatias, espessura 14, total no centro, 2px de folga entre fatias ---------- */
  function rosca(svg) {
    var d = JSON.parse(svg.getAttribute("data-rosca"));
    var r = 40, c = 2 * Math.PI * r, acc = 0, total = d.fatias.reduce(function (s, f) { return s + f.v; }, 0);
    el("circle", { cx: 52, cy: 52, r: r, fill: "none", stroke: "var(--surface-sunken)", "stroke-width": 14 }, svg);
    d.fatias.forEach(function (f) {
      var q = f.v / total;
      el("circle", { cx: 52, cy: 52, r: r, fill: "none", stroke: "var(--" + f.cor + ")", "stroke-width": 14,
        "stroke-dasharray": (q * c - 2) + " " + c, "stroke-dashoffset": -acc * c, transform: "rotate(-90 52 52)" }, svg);
      acc += q;
    });
    el("text", { x: 52, y: 52, "text-anchor": "middle", style: "font:700 16px var(--font-sans);fill:var(--ink)" }, svg).textContent = nf.format(total);
    el("text", { x: 52, y: 66, "text-anchor": "middle" }, svg).textContent = d.rotulo;
  }

  function desenhar() {
    document.querySelectorAll("svg[data-linha]").forEach(linha);
  }

  document.addEventListener("DOMContentLoaded", function () {
    iniciarMenu();
    iniciarDicas();
    document.querySelectorAll("svg[data-spark]").forEach(sparkline);
    document.querySelectorAll("svg[data-rosca]").forEach(rosca);
    desenhar();
    var t;
    window.addEventListener("resize", function () { clearTimeout(t); t = setTimeout(desenhar, 100); });
  });
})();
