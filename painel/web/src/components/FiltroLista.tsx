"use client";

import { createContext, type ReactNode, useContext, useEffect, useMemo, useRef, useState } from "react";
import { Botao } from "./Botao";
import Icone from "./Icone";
import Vazio from "./Vazio";

// Filtro e busca de uma lista que veio pronta do servidor (Equipe e Produção: as "Interações" de cada tela). Cada item
// filtrável leva data-tags ("todos portoes opus") e data-busca (o texto); o grupo que fica vazio (data-grupo-filtro)
// some; sem nenhum resultado aparece o vazio "Ninguém com esse filtro" + "Limpar filtros". Os itens que não passam são
// ESCONDIDOS (nunca apagados com opacidade, que derruba o contraste).

type Estado = { filtro: string; setFiltro: (v: string) => void; busca: string; setBusca: (v: string) => void };
const Ctx = createContext<Estado | null>(null);
const normal = (t: string) => t.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();

export function FiltroLista({ children, vazio = "Ninguém com esse filtro" }: { children: ReactNode; vazio?: string }) {
  const [filtro, setFiltro] = useState("todos");
  const [busca, setBusca] = useState("");
  const [nada, setNada] = useState(false);
  const raiz = useRef<HTMLDivElement>(null);
  const estado = useMemo(() => ({ filtro, setFiltro, busca, setBusca }), [filtro, busca]);

  useEffect(() => {
    const el = raiz.current;
    if (!el) return;
    const palavras = normal(busca).split(/\s+/).filter(Boolean);
    const filtrando = filtro !== "todos" || palavras.length > 0;
    let algum = false;
    for (const item of el.querySelectorAll<HTMLElement>("[data-tags]")) {
      const passa = (filtro === "todos" || (item.dataset.tags ?? "").split(" ").includes(filtro))
        && palavras.every((p) => normal(item.dataset.busca ?? "").includes(p));
      item.hidden = !passa;
      if (passa) algum = true;
    }
    let comVazioProprio = false;
    for (const g of el.querySelectorAll<HTMLElement>("[data-grupo-filtro]")) {
      const visivel = Boolean(g.querySelector("[data-tags]:not([hidden])"));
      // grupo com aviso próprio (tabela da fase): mostra "Nada encontrado nesta fase" em vez de sumir
      const proprio = g.querySelector<HTMLElement>("[data-vazio-grupo]");
      if (proprio) {
        comVazioProprio = true;
        proprio.hidden = visivel || !filtrando;
      } else {
        g.hidden = !visivel;
      }
    }
    // "Ninguém com esse filtro" só quando HÁ filtro ou busca: lista vazia de verdade (banco vazio ou fora do ar) já tem
    // o vazio ou o erro do próprio bloco, e "Limpar filtros" ali não faria nada
    setNada(!algum && !comVazioProprio && filtrando);
  }, [filtro, busca]);

  return (
    <Ctx.Provider value={estado}>
      <div ref={raiz} className="kx-filtro-lista">
        {children}
        {nada && (
          <Vazio
            icone="filter"
            titulo={vazio}
            acao={<Botao variante="secundario" pequeno onClick={() => { setFiltro("todos"); setBusca(""); }}>Limpar filtros</Botao>}
          >
            Nenhum item passa pelo filtro e pela busca escolhidos.
          </Vazio>
        )}
      </div>
    </Ctx.Provider>
  );
}

/** Campo de busca da lista (k-search). */
export function BuscaLista({ placeholder, rotulo }: { placeholder: string; rotulo: string }) {
  const ctx = useContext(Ctx);
  return (
    <label className="k-search kx-busca-lista">
      <Icone nome="search" tamanho={16} />
      <input
        type="search"
        placeholder={placeholder}
        aria-label={rotulo}
        value={ctx?.busca ?? ""}
        onChange={(e) => ctx?.setBusca(e.target.value)}
        onKeyDown={(e) => { if (e.key === "Escape") ctx?.setBusca(""); }}
      />
    </label>
  );
}

/** Os filtros em pílula da lista, com a contagem. */
export function FiltrosLista({ rotulo, opcoes }: { rotulo: string; opcoes: { valor: string; rotulo: string; n?: number }[] }) {
  const ctx = useContext(Ctx);
  return (
    <div className="k-filtros" role="group" aria-label={rotulo}>
      {opcoes.map((o) => (
        <button key={o.valor} type="button" className="k-filtro" aria-pressed={ctx?.filtro === o.valor} onClick={() => ctx?.setFiltro(o.valor)}>
          {o.rotulo}
          {o.n != null && <span className="k-filtro-n">{o.n}</span>}
        </button>
      ))}
    </div>
  );
}
