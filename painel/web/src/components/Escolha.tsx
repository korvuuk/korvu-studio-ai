"use client";

import { createContext, type ReactNode, useContext, useEffect, useMemo, useState } from "react";
import Icone from "./Icone";

// Escolha em partes — a mesma troca de vista do Alternador (filtro, segmentado, fases; design-system.md §15.2), para
// quando os botões e os painéis ficam em lugares diferentes da página (Produção: as fases em cima, a tabela da fase dentro
// do card ao lado dos avisos; o formato por fora de tudo). Várias escolhas podem se aninhar: cada uma tem um `nome`.

type Grupo = { valor: string; inicial: string; escolher: (v: string) => void };
const Ctx = createContext<Record<string, Grupo>>({});

export function Escolha({ nome, inicial, ancora, opcoesValidas, children }: {
  nome: string;
  inicial: string;
  /** a escolha acompanha o #endereço (/producao#prontos) */
  ancora?: boolean;
  /** os valores que o #endereço pode escolher */
  opcoesValidas?: string[];
  children: ReactNode;
}) {
  const pai = useContext(Ctx);
  const [valor, setValor] = useState(inicial);
  const validas = opcoesValidas?.join(" ");

  useEffect(() => {
    if (!ancora) return;
    const ler = () => {
      const h = decodeURIComponent(window.location.hash.slice(1));
      if (validas?.split(" ").includes(h)) setValor(h);
    };
    ler();
    window.addEventListener("hashchange", ler);
    return () => window.removeEventListener("hashchange", ler);
  }, [ancora, validas]);

  const valorCtx = useMemo(() => ({
    ...pai,
    [nome]: { valor, inicial, escolher: (v: string) => { setValor(v); if (ancora) history.replaceState(null, "", `#${v}`); } },
  }), [pai, nome, valor, inicial, ancora]);
  return <Ctx.Provider value={valorCtx}>{children}</Ctx.Provider>;
}

export type OpcaoEscolha = {
  valor: string;
  rotulo: ReactNode;
  n?: number;
  fase?: { n: ReactNode; d?: ReactNode; m?: ReactNode };
  /** Fases: o elo depois deste cartão ("você grava") */
  elo?: string;
};

/**
 * Botões e painéis podem chegar depois (dentro de um Suspense) e hidratar quando a escolha já mudou (o #endereço é lido
 * logo no começo). Para o HTML do servidor e o do navegador baterem, cada parte hidrata com a escolha INICIAL e só depois
 * passa a seguir a escolha atual.
 */
function useValor(grupo: string): Grupo | undefined {
  const g = useContext(Ctx)[grupo];
  const [hidratado, setHidratado] = useState(false);
  useEffect(() => setHidratado(true), []);
  return g && (hidratado ? g : { ...g, valor: g.inicial });
}

export function EscolhaBotoes({ grupo, estilo, rotulo, opcoes, controla }: {
  grupo: string;
  estilo: "filtros" | "seg" | "fases";
  rotulo: string;
  opcoes: OpcaoEscolha[];
  /** id do bloco que os botões trocam (aria-controls) */
  controla?: string;
}) {
  const g = useValor(grupo);
  const botoes = opcoes.flatMap((o, i) => {
    const pressionado = g?.valor === o.valor;
    if (estilo === "fases") {
      return [
        <button key={o.valor} type="button" className="k-fase" aria-pressed={pressionado} aria-controls={controla} onClick={() => g?.escolher(o.valor)}>
          <span className="k-cap">{o.rotulo}</span>
          <span className="k-fase-n">{o.fase?.n}</span>
          {o.fase?.d && <span className="k-fase-d">{o.fase.d}</span>}
          {o.fase?.m && <span className="k-fase-m">{o.fase.m}</span>}
        </button>,
        ...(i < opcoes.length - 1 ? [
          <div key={`${o.valor}-elo`} className="k-fase-elo" aria-hidden="true">
            <Icone nome="seta-direita" tamanho={16} />
            {o.elo && <span>{o.elo}</span>}
          </div>,
        ] : []),
      ];
    }
    return [
      <button key={o.valor} type="button" className={estilo === "filtros" ? "k-filtro" : undefined} aria-pressed={pressionado} aria-controls={controla} onClick={() => g?.escolher(o.valor)}>
        {o.rotulo}
        {o.n != null && estilo === "filtros" && <span className="k-filtro-n">{o.n}</span>}
      </button>,
    ];
  });
  const classe = estilo === "filtros" ? "k-filtros" : estilo === "fases" ? "k-fases" : "k-seg";
  return <div className={classe} role="group" aria-label={rotulo}>{botoes}</div>;
}

/** O painel aparece quando a escolha do `grupo` é um dos `valores`. */
export function EscolhaPainel({ grupo, valores, como: Tag = "div", className, children }: {
  grupo: string; valores: string[];
  /** "span" quando o painel fica dentro de uma linha de texto (a frase do cabeçalho que troca com a escolha) */
  como?: "div" | "span";
  className?: string;
  children: ReactNode;
}) {
  const g = useValor(grupo);
  return <Tag className={className} hidden={!g || !valores.includes(g.valor)}>{children}</Tag>;
}
