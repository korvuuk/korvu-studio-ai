"use client";

import { useEffect } from "react";

// Um ouvinte só para a página inteira (montado na casca): abre a dica de qualquer elemento com data-dica — chips de
// portão, linhas de barra, fatias — que continuam sendo HTML do servidor. Uma .k-tooltip.is-floating por página,
// position:fixed, acima do elemento (abaixo se não couber), presa a 8px das bordas da janela, com a seta apontando
// para o elemento (--seta-x). Abre 300ms depois do mouse, do toque ou do Tab; fecha ao sair, ao tocar fora e com Esc
// (WCAG 1.4.13). Mantém a regra do S0 de 22/10: nada escondido alarga a página (fechada = display:none).

const MARGEM = 8; // distância mínima das bordas da janela
const VAO = 10; // entre a dica e o elemento (seta de 8px girada)
const ATRASO = 300; // --atraso-dica

const limitar = (v: number, min: number, max: number) => Math.max(min, Math.min(v, max));

export default function Dicas() {
  useEffect(() => {
    const dica = document.createElement("div");
    dica.className = "k-tooltip is-floating";
    // O texto da dica já está no elemento para o leitor de tela (.k-sr-only): a caixa visual fica fora dele.
    dica.setAttribute("aria-hidden", "true");
    dica.style.display = "none";
    const linha1 = document.createElement("b");
    const linha2 = document.createElement("small");
    dica.append(linha1, linha2);
    document.body.appendChild(dica);

    let alvo: HTMLElement | null = null;
    let espera = 0;
    let quadro = 0;

    const fechar = () => {
      window.clearTimeout(espera);
      espera = 0;
      alvo = null;
      dica.style.display = "none";
    };

    const posicionar = () => {
      if (!alvo) return;
      const r = alvo.getBoundingClientRect();
      const vw = document.documentElement.clientWidth;
      const vh = document.documentElement.clientHeight;
      if (r.bottom < 0 || r.top > vh || (r.width === 0 && r.height === 0)) return fechar(); // saiu da tela
      dica.style.left = "0px";
      dica.style.top = "0px";
      const d = dica.getBoundingClientRect();
      const x = limitar(r.left + r.width / 2 - d.width / 2, MARGEM, vw - d.width - MARGEM);
      let y = r.top - d.height - VAO;
      const abaixo = y < MARGEM;
      if (abaixo) y = r.bottom + VAO;
      y = limitar(y, MARGEM, vh - d.height - MARGEM);
      dica.classList.toggle("is-abaixo", abaixo);
      dica.style.left = `${Math.round(x)}px`;
      dica.style.top = `${Math.round(y)}px`;
      dica.style.setProperty("--seta-x", `${Math.round(limitar(r.left + r.width / 2 - x, 10, d.width - 10))}px`);
    };

    const abrir = (el: HTMLElement) => {
      alvo = el;
      linha1.textContent = el.dataset.dica ?? "";
      const detalhe = el.dataset.dicaDetalhe;
      linha2.textContent = detalhe ?? "";
      linha2.hidden = !detalhe;
      dica.style.display = "inline-flex";
      posicionar();
    };

    const agendar = (el: HTMLElement) => {
      if (alvo === el) return;
      window.clearTimeout(espera);
      if (alvo) dica.style.display = "none";
      alvo = null;
      espera = window.setTimeout(() => abrir(el), ATRASO);
    };

    const de = (t: EventTarget | null) => (t instanceof Element ? t.closest<HTMLElement>("[data-dica]") : null);

    const sobre = (e: PointerEvent) => {
      const el = de(e.target);
      if (el) agendar(el);
    };
    const saiu = (e: PointerEvent) => {
      const el = de(e.target);
      if (!el) return;
      const para = e.relatedTarget;
      if (para instanceof Node && el.contains(para)) return;
      if (document.activeElement === el) return; // continua aberta enquanto o foco do teclado estiver nele
      fechar();
    };
    const foco = (e: FocusEvent) => {
      const el = de(e.target);
      if (el) agendar(el);
    };
    const desfoco = (e: FocusEvent) => {
      const el = de(e.target);
      if (el && (alvo === el || espera)) fechar();
    };
    const toque = (e: PointerEvent) => {
      if (!de(e.target)) fechar(); // tocar fora fecha
    };
    const tecla = (e: KeyboardEvent) => {
      if (e.key === "Escape") fechar();
    };
    const reposicionar = () => {
      if (!alvo) return;
      cancelAnimationFrame(quadro);
      quadro = requestAnimationFrame(posicionar);
    };

    document.addEventListener("pointerover", sobre);
    document.addEventListener("pointerout", saiu);
    document.addEventListener("pointerdown", toque);
    document.addEventListener("focusin", foco);
    document.addEventListener("focusout", desfoco);
    document.addEventListener("keydown", tecla);
    window.addEventListener("scroll", reposicionar, true);
    window.addEventListener("resize", reposicionar);
    return () => {
      document.removeEventListener("pointerover", sobre);
      document.removeEventListener("pointerout", saiu);
      document.removeEventListener("pointerdown", toque);
      document.removeEventListener("focusin", foco);
      document.removeEventListener("focusout", desfoco);
      document.removeEventListener("keydown", tecla);
      window.removeEventListener("scroll", reposicionar, true);
      window.removeEventListener("resize", reposicionar);
      window.clearTimeout(espera);
      cancelAnimationFrame(quadro);
      dica.remove();
    };
  }, []);
  return null;
}
