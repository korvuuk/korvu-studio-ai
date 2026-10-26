"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { type ReactNode, useCallback, useEffect, useRef, useState } from "react";
import { PAGINAS, estaAtivo } from "@/lib/navegacao";
import Icone from "./Icone";
import Logo from "./Logo";

// A casca do painel (design-system.md §4 e §11.6; handoff.md §4; topo das telas aprovadas pelo Carlos em 23/10):
// - ≥ 1024px: barra lateral escura de 208px (logotipo, os 7 itens na ordem decidida, a conta no rodapé) + área com a
//   barra do app em cima (busca, avisos, "Carlos · Proprietário") e a página embaixo;
// - < 1024px: barra de topo escura (logotipo, avisos, botão "Menu"); o menu aberto é a mesma barra lateral em tela
//   cheia, com a busca em cima. Fecha com Esc (o foco volta ao botão), ao tocar num item e ao trocar de página; enquanto
//   aberto, a página de trás não rola.
// As peças com dados (contagem, busca, avisos) chegam prontas do servidor (app/layout.tsx).

export default function Casca({ buscaMenu, avisosTopo, barraApp, contagens, children }: {
  /** a busca que aparece dentro do menu, em tela estreita */
  buscaMenu: ReactNode;
  /** o sino na barra de topo escura (tela estreita) */
  avisosTopo: ReactNode;
  /** a barra do app (tela larga): busca, avisos, dono */
  barraApp: ReactNode;
  /** contagem ao lado do item do menu (href → nó com o número e a unidade para o leitor de tela) */
  contagens?: Partial<Record<string, ReactNode>>;
  children: ReactNode;
}) {
  const caminho = usePathname();
  const [aberto, setAberto] = useState(false);
  const botao = useRef<HTMLButtonElement>(null);

  const fechar = useCallback((devolverFoco: boolean) => {
    setAberto(false);
    if (devolverFoco) botao.current?.focus();
  }, []);

  // troca de página fecha o menu
  useEffect(() => setAberto(false), [caminho]);

  useEffect(() => {
    if (!aberto) return;
    const tecla = (e: KeyboardEvent) => {
      if (e.key === "Escape") fechar(true);
    };
    // de volta à tela larga, o menu deixa de existir: fecha (e libera a rolagem)
    const largo = window.matchMedia("(min-width: 1024px)");
    const mudou = () => { if (largo.matches) fechar(false); };
    document.addEventListener("keydown", tecla);
    largo.addEventListener("change", mudou);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", tecla);
      largo.removeEventListener("change", mudou);
      document.body.style.overflow = "";
    };
  }, [aberto, fechar]);

  return (
    <div className={`k-shell${aberto ? " is-menu-open" : ""}`}>
      <header className="k-topbar">
        <Link href="/" aria-label="korvu. painel — início"><Logo tom="ivory" altura={19} decorativo /></Link>
        <div className="k-topbar-fim">
          {avisosTopo}
          <button
            ref={botao}
            type="button"
            className="k-menu-btn"
            aria-expanded={aberto}
            aria-controls="menu"
            onClick={() => setAberto((a) => !a)}
          >
            {aberto ? "Fechar" : "Menu"}
            <Icone nome={aberto ? "x" : "chevron-down"} tamanho={16} />
          </button>
        </div>
      </header>

      <aside className="k-sidebar" id="menu">
        <Link className="k-sidebar-logo" href="/" aria-label="korvu. painel — início">
          <Logo tom="ivory" altura={19} decorativo />
        </Link>
        {buscaMenu}
        <nav aria-label="Menu principal" className="kx-nav">
          {PAGINAS.map((p) => {
            const ativo = estaAtivo(p.href, caminho);
            return (
              <Link
                key={p.href}
                href={p.href}
                className={`k-nav-item${ativo ? " is-active" : ""}`}
                aria-current={ativo ? "page" : undefined}
                onClick={() => setAberto(false)}
              >
                <Icone nome={p.icone} tamanho={18} />
                <span className="kx-nav-rotulo">{p.nome}</span>
                {contagens?.[p.href]}
              </Link>
            );
          })}
        </nav>
        <div className="k-sidebar-foot">
          <div className="k-sidebar-owner">@korvu_oficial<small>Instagram · Facebook</small></div>
        </div>
      </aside>

      {/* menu aberto (só em tela estreita) cobre a página: ela sai do Tab e do leitor de tela até o menu fechar */}
      <div className="k-area" inert={aberto || undefined}>
        {barraApp}
        <main className="k-main is-painel" id="conteudo" tabIndex={-1}>
          {children}
        </main>
      </div>
    </div>
  );
}
