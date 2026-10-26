"use client";

import { type ReactNode, useEffect, useId, useState } from "react";
import { CardCabecalho } from "./Card";
import Icone from "./Icone";

// Troca de vista no mesmo bloco (design-system.md §15.2): Filtro em pílula (.k-filtro), Controle segmentado (.k-seg) e
// Fases da produção (.k-fase + .k-fase-elo). Os painéis vêm prontos do servidor; o navegador só mostra o escolhido
// (os outros ficam com `hidden`). Botões com aria-pressed e aria-controls. Com `ancora`, a escolha acompanha o #endereço
// (ex.: /producao#prontos, que os avisos usam).

export type OpcaoAlternador = {
  valor: string;
  rotulo: ReactNode;
  /** contagem do filtro (mono, ink-3) */
  n?: number;
  /** Fases: o número grande, a descrição e a meta do cartão */
  fase?: { cap: string; n: ReactNode; d?: ReactNode; m?: ReactNode };
  /** Fases: o elo DEPOIS deste cartão ("você grava") */
  elo?: string;
};

export default function Alternador({ estilo, rotulo, opcoes, paineis, inicial, ancora, cabeca }: {
  estilo: "filtros" | "seg" | "seg-alto" | "fases";
  /** nome do grupo para o leitor de tela: "Filtrar por departamento" */
  rotulo: string;
  opcoes: OpcaoAlternador[];
  paineis: Record<string, ReactNode>;
  inicial?: string;
  ancora?: boolean;
  /** cabeçalho do card acima dos botões: o título (h2, com o id para o aria-labelledby do card) e, à direita, o que troca
   *  com a escolha (ex.: "3.202 contas") */
  cabeca?: { titulo: ReactNode; id?: string; porValor?: Record<string, ReactNode> };
}) {
  const id = useId();
  const [valor, setValor] = useState(inicial ?? opcoes[0]?.valor);

  useEffect(() => {
    if (!ancora) return;
    const ler = () => {
      const h = decodeURIComponent(window.location.hash.slice(1));
      if (opcoes.some((o) => o.valor === h)) setValor(h);
    };
    ler();
    window.addEventListener("hashchange", ler);
    return () => window.removeEventListener("hashchange", ler);
  }, [ancora, opcoes]);

  const escolher = (v: string) => {
    setValor(v);
    if (ancora) history.replaceState(null, "", `#${v}`);
  };
  const painelId = (v: string) => `${id}-${v}`;

  const botoes = opcoes.map((o, i) => {
    const pressionado = o.valor === valor;
    if (estilo === "fases") {
      return [
        <button key={o.valor} type="button" className="k-fase" aria-pressed={pressionado} aria-controls={painelId(o.valor)} onClick={() => escolher(o.valor)}>
          <span className="k-cap">{o.fase?.cap ?? o.rotulo}</span>
          <span className="k-fase-n">{o.fase?.n}</span>
          {o.fase?.d && <span className="k-fase-d">{o.fase.d}</span>}
          {o.fase?.m && <span className="k-fase-m">{o.fase.m}</span>}
        </button>,
        // a grade das fases tem uma coluna de elo entre cada par de cartões: o elo existe sempre, mesmo sem texto
        i < opcoes.length - 1 ? (
          <div key={`${o.valor}-elo`} className="k-fase-elo" aria-hidden="true">
            <Icone nome="seta-direita" tamanho={16} />
            {o.elo && <span>{o.elo}</span>}
          </div>
        ) : null,
      ];
    }
    const classe = estilo === "filtros" ? "k-filtro" : undefined;
    return (
      <button key={o.valor} type="button" className={classe} aria-pressed={pressionado} aria-controls={painelId(o.valor)} onClick={() => escolher(o.valor)}>
        {o.rotulo}
        {o.n != null && estilo === "filtros" && <span className="k-filtro-n">{o.n}</span>}
      </button>
    );
  });

  const grupo = estilo === "filtros" ? "k-filtros" : estilo === "fases" ? "k-fases" : `k-seg is-largo${estilo === "seg-alto" ? " is-alto" : ""}`;
  return (
    <>
      {cabeca && <CardCabecalho como="h2" id={cabeca.id} titulo={cabeca.titulo} acao={cabeca.porValor?.[valor ?? ""]} />}
      <div className={`${grupo} kx-alternador-${estilo}`} role="group" aria-label={rotulo}>{botoes}</div>
      {opcoes.map((o) => (
        <div key={o.valor} id={painelId(o.valor)} hidden={o.valor !== valor} className="kx-painel">
          {paineis[o.valor]}
        </div>
      ))}
    </>
  );
}
