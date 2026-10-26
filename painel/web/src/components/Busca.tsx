"use client";

import { useRouter } from "next/navigation";
import { useEffect, useId, useMemo, useRef, useState } from "react";
import Icone from "./Icone";

// Busca global (design-system.md §11.14 e §15.2; telas/visao-geral.md "Interações"): campo k-search, ⌘K / Ctrl+K leva o
// foco até ela. Procura vídeos (nome curto e slug), pessoas (nome e função), portões e páginas que o servidor mandou —
// só nomes e endereços; o navegador nunca fala com o banco. Resultado num k-menu, em grupos; setas movem, Enter abre,
// Esc limpa e fecha. Sem nada: "Nada com '…' no painel."

export type TipoBusca = "Vídeo" | "Pessoa" | "Portão" | "Página";
export type ItemBusca = {
  tipo: TipoBusca;
  rotulo: string;
  /** o que aparece apagado à direita (função, fase, slug…) */
  detalhe?: string;
  href: string;
  /** texto extra que também casa com a busca (id, slug, departamento…) */
  termos?: string;
};

const GRUPOS: { tipo: TipoBusca; nome: string }[] = [
  { tipo: "Vídeo", nome: "Vídeos" }, { tipo: "Pessoa", nome: "Pessoas" }, { tipo: "Portão", nome: "Portões" },
  { tipo: "Página", nome: "Páginas" },
];
const POR_GRUPO = 4;
const normal = (t: string) => t.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();

export default function Busca({ itens }: { itens: ItemBusca[] }) {
  const id = useId();
  const router = useRouter();
  const campo = useRef<HTMLInputElement>(null);
  const caixa = useRef<HTMLDivElement>(null);
  const [texto, setTexto] = useState("");
  const [aberto, setAberto] = useState(false);
  const [ativo, setAtivo] = useState(0);
  const [focado, setFocado] = useState(false);

  const indice = useMemo(
    () => itens.map((it) => ({ it, chave: normal(`${it.rotulo} ${it.detalhe ?? ""} ${it.termos ?? ""}`), nome: normal(it.rotulo) })),
    [itens],
  );
  // até 4 por grupo, na ordem dos grupos; dentro do grupo, quem começa com o que foi digitado vem primeiro
  const grupos = useMemo(() => {
    const palavras = normal(texto).split(/\s+/).filter(Boolean);
    if (palavras.length === 0) return [];
    const achados = indice
      .map((x, i) => ({ ...x, i }))
      .filter(({ chave }) => palavras.every((p) => chave.includes(p)))
      .sort((a, b) => Number(!a.nome.startsWith(palavras[0])) - Number(!b.nome.startsWith(palavras[0])) || a.i - b.i);
    return GRUPOS.map((g) => ({ ...g, itens: achados.filter((a) => a.it.tipo === g.tipo).slice(0, POR_GRUPO).map((a) => a.it) }))
      .filter((g) => g.itens.length > 0);
  }, [indice, texto]);
  const planos = grupos.flatMap((g) => g.itens);

  // ⌘K / Ctrl+K: foca a busca que está à vista (a da barra do app no computador, a do menu no celular)
  useEffect(() => {
    const atalho = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        const el = campo.current;
        if (!el || el.getClientRects().length === 0) return;
        e.preventDefault();
        el.focus();
        el.select();
      }
    };
    document.addEventListener("keydown", atalho);
    return () => document.removeEventListener("keydown", atalho);
  }, []);

  useEffect(() => {
    if (!aberto) return;
    const fora = (e: PointerEvent) => {
      if (!caixa.current?.contains(e.target as Node)) setAberto(false);
    };
    document.addEventListener("pointerdown", fora);
    return () => document.removeEventListener("pointerdown", fora);
  }, [aberto]);

  const ir = (it: ItemBusca) => {
    setAberto(false);
    setTexto("");
    campo.current?.blur();
    router.push(it.href);
  };

  const mostrar = aberto && texto.trim().length > 0;
  const lista = `${id}-resultados`;
  const temLista = mostrar && planos.length > 0;
  let k = -1;

  return (
    <div className="kx-busca" ref={caixa}>
      <label className="k-search">
        <Icone nome="search" tamanho={16} />
        <input
          ref={campo}
          type="search"
          role="combobox"
          aria-label="Buscar vídeos, pessoas da equipe, portões e páginas"
          aria-autocomplete="list"
          aria-expanded={temLista}
          aria-controls={temLista ? lista : undefined}
          aria-activedescendant={temLista ? `${id}-${ativo}` : undefined}
          placeholder="Buscar vídeos, agentes, portões…"
          autoComplete="off"
          spellCheck={false}
          value={texto}
          onChange={(e) => { setTexto(e.target.value); setAtivo(0); setAberto(true); }}
          onFocus={() => { setFocado(true); setAberto(true); }}
          onBlur={() => setFocado(false)}
          onKeyDown={(e) => {
            if (e.key === "ArrowDown") { e.preventDefault(); setAberto(true); setAtivo((i) => Math.min(planos.length - 1, i + 1)); }
            else if (e.key === "ArrowUp") { e.preventDefault(); setAtivo((i) => Math.max(0, i - 1)); }
            else if (e.key === "Enter" && temLista && planos[ativo]) { e.preventDefault(); ir(planos[ativo]); }
            else if (e.key === "Escape") {
              if (texto) { e.preventDefault(); setTexto(""); setAberto(false); }
              else campo.current?.blur();
            }
          }}
        />
        <span className="k-kbd kx-so-teclado" aria-hidden="true">{focado ? "esc" : "⌘K"}</span>
      </label>
      {mostrar && (
        <div className="k-menu kx-busca-pop">
          {planos.length > 0 ? (
            <div id={lista} role="listbox" aria-label="Resultados da busca">
              {grupos.map((g) => (
                <div key={g.tipo} role="group" aria-labelledby={`${id}-g-${g.tipo}`}>
                  <p id={`${id}-g-${g.tipo}`} role="presentation" className="k-cap kx-busca-grupo">{g.nome}</p>
                  {g.itens.map((it) => {
                    k += 1;
                    const i = k;
                    return (
                      <div
                        key={`${it.tipo}-${it.href}-${it.rotulo}`}
                        id={`${id}-${i}`}
                        role="option"
                        aria-selected={i === ativo}
                        className={`k-menu-item${i === ativo ? " is-hover" : ""}`}
                        onPointerEnter={() => setAtivo(i)}
                        onPointerDown={(e) => e.preventDefault()}
                        onClick={() => ir(it)}
                      >
                        <span className="kx-busca-rotulo">{it.rotulo}</span>
                        {it.detalhe && <span className="kx-busca-detalhe">{it.detalhe}</span>}
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          ) : (
            <p className="kx-busca-vazio">Nada com “{texto.trim()}” no painel.</p>
          )}
        </div>
      )}
      <span className="k-sr-only" aria-live="polite">
        {mostrar ? (planos.length ? `${planos.length} resultado${planos.length > 1 ? "s" : ""}` : "Nada encontrado") : ""}
      </span>
    </div>
  );
}
