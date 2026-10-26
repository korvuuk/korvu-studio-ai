import Link from "next/link";
import type { ReactNode } from "react";
import Icone from "./Icone";

// KPI (design-system.md §11.5 e §15.2): rótulo em caption → valor 40px/700 tabular (unidade K, M, %, "contas" em
// <small>; US$ antes do valor em <small class="k-prefixo">) → rodapé com o delta + contexto. A COR do delta segue o
// significado, não a direção (seguidor perdido é vermelho, custo subindo é vermelho). Peça ao lado (anel ou capa):
// `aside`, e só o rótulo e o valor dão lugar a ela. O cartão inteiro pode ser link (`href`).

export type Sentido = "sobe" | "desce" | "igual";
export type Significado = "bom" | "ruim" | "neutro";

const COR: Record<Significado, string> = { bom: "k-delta--up", ruim: "k-delta--down", neutro: "k-delta--flat" };

/** Delta: seta (ícone, aria-hidden) + número + palavra para o leitor de tela ("11,1%" + " a mais que em 16 out"). */
export function Delta({ sentido, significado, texto, leitor, semSeta }: {
  sentido: Sentido; significado: Significado; texto: string; leitor: string;
  /** "−0,1%" quase igual: o número basta, sem seta */
  semSeta?: boolean;
}) {
  return (
    <span className={`k-delta ${COR[significado]}`}>
      {!semSeta && sentido !== "igual" && <Icone nome={sentido === "sobe" ? "arrow-up" : "arrow-down"} tamanho={12} traco={2} />}
      {texto}
      <span className="k-sr-only">{` ${leitor}`}</span>
    </span>
  );
}

export function Kpi({ rotulo, valor, unidade, prefixo, delta, destaque, nota, extra, aside, comCapa, href, rotuloLink, junto, deltaAoLado, className }: {
  rotulo: string;
  /** O número já formatado (lib/formato: num, compactoPartes). "—" quando não há dado. */
  valor: string;
  unidade?: string;
  prefixo?: string;
  delta?: ReactNode;
  /** nome em negrito no rodapé, numa linha só dele (ex.: o vídeo do "Melhor vídeo até agora") */
  destaque?: ReactNode;
  nota?: ReactNode;
  /** sparkline ou outra peça pequena no rodapé, à direita */
  extra?: ReactNode;
  /** anel ou capa ao lado do valor (.has-aside) */
  aside?: ReactNode;
  /** a peça ao lado é uma capa alta (103px): o rodapé também dá lugar a ela */
  comCapa?: boolean;
  href?: string;
  /** nome do link para o leitor de tela, quando o cartão é link */
  rotuloLink?: string;
  /** rodapé com o delta e o contexto juntos à esquerda (telas de 23/10) */
  junto?: boolean;
  /** o delta na linha do valor, à direita, e a nota embaixo (Tokens e custos · Projeção mensal) */
  deltaAoLado?: boolean;
  className?: string;
}) {
  const semDado = valor === "—";
  const classes = ["k-card k-kpi", aside && "has-aside", comCapa && "k-kpi--capa", href && "is-interactive", className]
    .filter(Boolean).join(" ");
  const numero = (
    <div className="k-kpi-value">
      {prefixo && !semDado && <small className="k-prefixo">{prefixo}</small>}
      {semDado ? <span aria-label="sem dado">—</span> : valor}
      {unidade && !semDado && <small>{unidade}</small>}
    </div>
  );
  if (deltaAoLado) {
    return (
      <div className={classes}>
        <span className="k-cap">{rotulo}</span>
        <div className="k-row kx-kpi-valor-lado">{numero}{delta}</div>
        {nota && <span className="k-kpi-note">{nota}</span>}
      </div>
    );
  }
  const conteudo = (
    <>
      <span className="k-cap">{rotulo}</span>
      {numero}
      {(delta || destaque || nota || extra) && (
        <div className={`k-kpi-foot${junto ? " kx-kpi-foot-junto" : ""}`}>
          {destaque && <b className="kx-kpi-nome">{destaque}</b>}
          {delta}
          {nota && <span className="k-kpi-note">{nota}</span>}
          {extra}
        </div>
      )}
      {aside && <span className="k-kpi-aside">{aside}</span>}
    </>
  );
  if (href) return <Link href={href} className={classes} aria-label={rotuloLink}>{conteudo}</Link>;
  return <div className={classes}>{conteudo}</div>;
}

/**
 * KPI em linha (design-system.md §15.2, `.k-kpi--linha`): valor de 36px com o contexto ao lado (≥ 1600) ou embaixo
 * (< 1600). Tokens em accent (número grande, decisão de 23/10). O cartão pode ser link.
 */
export function KpiLinha({ rotulo, valor, unidade, prefixo, delta, nota, tokens, href, className }: {
  rotulo: string;
  valor: string;
  unidade?: string;
  /** "US$" antes do valor, em <small class="k-prefixo"> */
  prefixo?: string;
  /** delta ao lado do valor: com ele, o delta e a nota vão juntos em .k-kpi-lado (Desempenho) */
  delta?: ReactNode;
  nota?: ReactNode;
  tokens?: boolean;
  href?: string;
  className?: string;
}) {
  const classes = ["k-card k-kpi k-kpi--linha", href && "is-interactive", className].filter(Boolean).join(" ");
  const conteudo = (
    <>
      <span className="k-cap">{rotulo}</span>
      <div className="k-kpi-linha">
        <span className={`k-kpi-value${tokens ? " k-tokens is-grande" : ""}`}>
          {prefixo && valor !== "—" && <small className="k-prefixo">{prefixo}</small>}
          {valor}
          {unidade && <small>{unidade}</small>}
        </span>
        {delta ? (
          <span className="k-kpi-lado">{delta}{nota && <span className="k-kpi-note">{nota}</span>}</span>
        ) : nota && <span className="k-kpi-note">{nota}</span>}
      </div>
    </>
  );
  return href ? <Link href={href} className={classes}>{conteudo}</Link> : <div className={classes}>{conteudo}</div>;
}
