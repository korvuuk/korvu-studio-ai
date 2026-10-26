"use client";

import { useEffect, useId, useRef, useState } from "react";
import Icone from "./Icone";

// Dropdown (design-system.md §11.15): gatilho k-select (36px) + menu k-menu flutuante 4px abaixo. Setas movem, Enter
// escolhe, Esc fecha e devolve o foco ao gatilho; selecionado em 600 com check em accent-ink. As opções de período têm
// de bater com as janelas que os dados têm (perfil: 28 dias da Meta) — quem usa passa só opções reais.

export type Opcao = { valor: string; rotulo: string; separadoAntes?: boolean };

export default function Selecao({ rotulo, opcoes, valor, aoMudar }: {
  /** nome do controle para o leitor de tela, ex.: "Período" */
  rotulo: string;
  opcoes: Opcao[];
  valor: string;
  aoMudar: (valor: string) => void;
}) {
  const id = useId();
  const [aberto, setAberto] = useState(false);
  const [ativo, setAtivo] = useState(0);
  const gatilho = useRef<HTMLButtonElement>(null);
  const lista = useRef<HTMLUListElement>(null);
  const atual = opcoes.find((o) => o.valor === valor) ?? opcoes[0];

  useEffect(() => {
    if (!aberto) return;
    lista.current?.focus();
    const fora = (e: PointerEvent) => {
      const alvo = e.target as Node;
      if (!lista.current?.contains(alvo) && !gatilho.current?.contains(alvo)) setAberto(false);
    };
    document.addEventListener("pointerdown", fora);
    return () => document.removeEventListener("pointerdown", fora);
  }, [aberto]);

  const abrir = () => {
    setAtivo(Math.max(0, opcoes.findIndex((o) => o.valor === valor)));
    setAberto(true);
  };
  const escolher = (i: number) => {
    aoMudar(opcoes[i].valor);
    setAberto(false);
    gatilho.current?.focus();
  };

  return (
    <div className="kx-selecao">
      <button
        ref={gatilho}
        type="button"
        className={`k-select${aberto ? " kx-aberto" : ""}`}
        aria-haspopup="listbox"
        aria-expanded={aberto}
        aria-controls={aberto ? `${id}-lista` : undefined}
        aria-label={`${rotulo}: ${atual?.rotulo ?? ""}`}
        onClick={() => (aberto ? setAberto(false) : abrir())}
        onKeyDown={(e) => {
          if (e.key === "ArrowDown" || e.key === "ArrowUp") {
            e.preventDefault();
            abrir();
          }
        }}
      >
        {atual?.rotulo}
        <Icone nome="chevron-down" tamanho={16} />
      </button>
      {aberto && (
        <ul
          ref={lista}
          id={`${id}-lista`}
          role="listbox"
          aria-label={rotulo}
          tabIndex={-1}
          className="k-menu kx-selecao-menu"
          aria-activedescendant={`${id}-${ativo}`}
          onKeyDown={(e) => {
            if (e.key === "ArrowDown") { e.preventDefault(); setAtivo((i) => Math.min(opcoes.length - 1, i + 1)); }
            else if (e.key === "ArrowUp") { e.preventDefault(); setAtivo((i) => Math.max(0, i - 1)); }
            else if (e.key === "Home") { e.preventDefault(); setAtivo(0); }
            else if (e.key === "End") { e.preventDefault(); setAtivo(opcoes.length - 1); }
            else if (e.key === "Enter" || e.key === " ") { e.preventDefault(); escolher(ativo); }
            else if (e.key === "Escape" || e.key === "Tab") { e.preventDefault(); setAberto(false); gatilho.current?.focus(); }
          }}
        >
          {opcoes.map((o, i) => (
            <li
              key={o.valor}
              id={`${id}-${i}`}
              role="option"
              aria-selected={o.valor === valor}
              className={[
                "k-menu-item", o.valor === valor && "is-selected", i === ativo && "is-hover",
                o.separadoAntes && "kx-com-separador",
              ].filter(Boolean).join(" ")}
              onPointerEnter={() => setAtivo(i)}
              onClick={() => escolher(i)}
            >
              {o.rotulo}
              {o.valor === valor && <span className="k-tick"><Icone nome="check" tamanho={14} /></span>}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
