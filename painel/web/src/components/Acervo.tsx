import Image from "next/image";
import type { ReactNode } from "react";
import Icone from "./Icone";

// Acervo de estilos (design-system.md §15.2, Biblioteca de 24/10): cabeçalho de bloco, etiqueta, cartão de look, estilo
// de capa, estilo de legenda, fonte, animação, modelo e ferramenta do Sistema. Os cartões NÃO são links nem botões: o
// painel só informa (decisão de 24/10) — nenhuma ação de escolher look ou capa aqui.

export type TomEtiqueta = "uso" | "alt" | "ref" | "arq" | "tipo";

export function Etiqueta({ tom, children }: { tom: TomEtiqueta; children: ReactNode }) {
  return <span className={`k-etiqueta k-etiqueta--${tom}`}>{children}</span>;
}

/** Título do bloco ("looks de cor.") com a frase curta ao lado. */
export function CabecalhoAcervo({ id, titulo, frase }: { id: string; titulo: string; frase?: ReactNode }) {
  return (
    <div className="k-acervo-head">
      <h2 id={id}>{titulo}</h2>
      {frase && <span>{frase}</span>}
    </div>
  );
}

export function CartaoLook({ nome, meta, desc, foto, etiqueta, emUso, prioridade }: {
  nome: string;
  meta?: ReactNode;
  desc?: ReactNode;
  /** a foto do Carlos com o look (rota /look/<id>); null = sem prévia */
  foto: string | null;
  etiqueta?: { tom: TomEtiqueta; texto: string };
  emUso?: boolean;
  /** na primeira dobra: a foto carrega já (PI77) */
  prioridade?: boolean;
}) {
  return (
    <article className={`k-card k-look${emUso ? " is-uso" : ""}`}>
      <div className="k-look-foto">
        {foto
          ? <Image src={foto} alt={`Carlos com ${nome}`} fill sizes="(max-width: 639px) 50vw, 240px" style={{ objectPosition: "50% 30%" }} priority={prioridade} />
          : <span className="kx-look-sem"><Icone nome="eye" tamanho={22} /><span className="k-sr-only">sem prévia</span></span>}
        {etiqueta && <Etiqueta tom={etiqueta.tom}>{etiqueta.texto}</Etiqueta>}
      </div>
      <div className="k-estilo-corpo">
        <span className="k-estilo-nome">{nome}</span>
        {meta && <span className="k-estilo-meta">{meta}</span>}
        {desc && <span className="k-estilo-desc">{desc}</span>}
      </div>
    </article>
  );
}

/** Um estilo de capa com as capas reais em que ele foi usado (9:16). */
export function CapaEstilo({ nome, desc, meta, capas }: {
  nome: string;
  desc: string;
  meta?: ReactNode;
  capas: { src: string; alt: string }[];
}) {
  return (
    <div className="k-capa-estilo">
      {capas.map((c) => <Image key={c.src} src={c.src} alt={c.alt} width={160} height={284} sizes="80px" style={{ height: "auto" }} />)}
      <div className="k-estilo-corpo">
        <span className="k-estilo-nome">{nome}</span>
        <span className="k-estilo-desc">{desc}</span>
        {meta && <span className="k-estilo-meta">{meta}</span>}
      </div>
    </div>
  );
}

export function LegendaEstilo({ nome, desc, meta, amostra, alt }: { nome: string; desc: string; meta?: ReactNode; amostra: string | null; alt: string }) {
  return (
    <div className="k-card k-legenda-estilo">
      {amostra ? <Image src={amostra} alt={alt} width={224} height={398} sizes="112px" style={{ height: "auto" }} /> : <span className="kx-legenda-sem" aria-hidden="true" />}
      <div className="k-estilo-corpo">
        <span className="k-estilo-nome">{nome}</span>
        <span className="k-estilo-desc">{desc}</span>
        {meta && <span className="k-estilo-meta">{meta}</span>}
      </div>
    </div>
  );
}

/** Uma família: o "Aa" desenhado (imagem, o painel só carrega a Geist), o nome e onde é usada. */
export function CartaoFonte({ familia, uso, amostra }: { familia: string; uso: string; amostra: string | null }) {
  return (
    <div className="k-card k-tipo">
      {amostra ? <Image src={amostra} alt={`Aa em ${familia}`} width={192} height={96} sizes="96px" /> : <span className="kx-tipo-aa" aria-hidden="true">Aa</span>}
      <span className="k-estilo-nome">{familia}</span>
      <span className="k-estilo-desc">{uso}</span>
    </div>
  );
}

export function LinhaAnimacao({ nome, meta, renderizada }: { nome: string; meta: string; renderizada: boolean }) {
  return (
    <div className="k-anim">
      <span className="k-anim-i"><Icone nome="play" tamanho={16} /></span>
      <div className="kx-pilha-mini">
        <span className="k-anim-nome">{nome}</span>
        <span className="k-estilo-meta">{meta}</span>
      </div>
      <Etiqueta tom={renderizada ? "uso" : "alt"}>{renderizada ? "Renderizada" : "Roteirizada"}</Etiqueta>
    </div>
  );
}

/** Aba Sistema · um modelo de IA: nome, etiqueta, % dos tokens (accent-ink 24 px) e a frase do biblioteca.yaml. */
export function SisModelo({ nome, pct, desc }: { nome: string; pct: string; desc: string | null }) {
  return (
    <div className="k-card k-sis-modelo">
      <div className="k-sis-modelo-topo">
        <span className="k-estilo-nome">{nome}</span>
        <Etiqueta tom="tipo">Modelo de IA</Etiqueta>
      </div>
      <span className="k-sis-modelo-pct">{pct}</span>
      {desc && <span className="k-estilo-desc">{desc}</span>}
    </div>
  );
}

/** Aba Sistema · uma ferramenta: nome · etiqueta do tipo · o que faz aqui. */
export function SisFerramenta({ nome, tipo, desc }: { nome: string; tipo: string; desc: string }) {
  return (
    <div className="k-sis">
      <span className="k-estilo-nome">{nome}</span>
      <span><Etiqueta tom="tipo">{tipo}</Etiqueta></span>
      <span className="k-estilo-desc">{desc}</span>
    </div>
  );
}

/** A legenda do Armazenamento: cor, nome e o valor. */
export function LegendaArmazem({ itens }: { itens: { nome: string; valor: string; serie: 1 | 2 | 3 }[] }) {
  return (
    <ul className="k-armazem-leg">
      {itens.map((it) => (
        <li key={it.nome}>
          <i aria-hidden="true" style={{ background: `var(--chart-${it.serie})` }} />
          <span>{it.nome}</span>
          <span className="k-estilo-meta">{it.valor}</span>
        </li>
      ))}
    </ul>
  );
}
