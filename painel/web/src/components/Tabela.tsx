import Link from "next/link";
import type { CSSProperties, ReactNode } from "react";
import { Card } from "./Card";
import Avatar from "./Avatar";
import Capa, { type TamanhoCapa } from "./Capa";
import Icone from "./Icone";

// Tabela (design-system.md §11.9 e acrescimos .k-table-wrap): k-card > região que rola SÓ PARA O LADO dentro do card
// (role="region" com nome e tabIndex, para rolar pelo teclado) > table.k-table. Linha de 56px, cabeçalho em caption,
// divisórias line, hover surface-hover. A página nunca rola para o lado; a tabela larga rola dentro do card.

export function Tabela({ rotulo, larguraMinima = 640, legenda, children }: {
  /** nome da região para o leitor de tela, ex.: "Vídeos (a tabela rola para o lado)" */
  rotulo: string;
  larguraMinima?: number;
  /** <caption> lido pelo leitor de tela */
  legenda?: string;
  children: ReactNode;
}) {
  return (
    <Card recorte>
      <div
        className="k-table-wrap"
        role="region"
        aria-label={rotulo}
        tabIndex={0}
        style={{ "--table-min": `${larguraMinima}px` } as CSSProperties}
      >
        <table className="k-table">
          {legenda && <caption className="k-sr-only">{legenda}</caption>}
          {children}
        </table>
      </div>
    </Card>
  );
}

/** Célula de vídeo (VideoRow): miniatura 56×36 (frame real quando houver; sem frame, k-thumb neutro com play),
 *  título em uma linha com reticências e a meta (slug) em mono. */
export function CelulaVideo({ titulo, meta }: { titulo: string; meta?: string }) {
  return (
    <div className="k-video">
      <span className="k-thumb" aria-hidden="true">
        <Icone nome="play" tamanho={14} />
      </span>
      <div>
        <div className="k-video-title" title={titulo}>{titulo}</div>
        {meta && <div className="k-video-meta k-mono">{meta}</div>}
      </div>
    </div>
  );
}

/** "—" com nome para o leitor de tela (célula sem dado). */
export function SemDado() {
  return <span aria-label="sem dado">—</span>;
}

/**
 * Tabela que já está dentro de um card (telas de 23/10: a fase da Produção, o ranking do Desempenho): a região que rola
 * para o lado (role="region", tabIndex) > table.k-table (densa: linha de 52px). As colunas de número alinham à direita.
 */
export function TabelaNoCard({ rotulo, min, colunas, denso = true, children }: {
  rotulo: string;
  /** largura mínima da tabela (px): abaixo dela, a tabela rola dentro do card */
  min: number;
  colunas: { t: ReactNode; dir?: boolean; chave?: string }[];
  denso?: boolean;
  children: ReactNode;
}) {
  return (
    <div className="k-table-wrap" role="region" aria-label={`${rotulo} (a tabela rola para o lado)`} tabIndex={0} style={{ "--table-min": `${min}px` } as CSSProperties}>
      <table className={`k-table${denso ? " k-table--denso" : ""}`}>
        <caption className="k-sr-only">{rotulo}</caption>
        <thead><tr>{colunas.map((c, i) => <th key={c.chave ?? i} scope="col" className={c.dir ? "k-dir" : undefined}>{c.t}</th>)}</tr></thead>
        <tbody>{children}</tbody>
      </table>
    </div>
  );
}

/** Célula de vídeo com a capa 9:16 (§15.2): capa, título numa linha (link, se houver) e a meta ou o slug embaixo. */
export function CelulaCapa({ nome, src, tamanho = "padrao", href, meta, slug, children }: {
  nome: string;
  src?: string | null;
  tamanho?: TamanhoCapa;
  href?: string;
  /** "13 out · Normal · 0:58" */
  meta?: ReactNode;
  /** o slug em mono */
  slug?: string;
  /** o que vem embaixo do slug (ex.: o chip do portão que venceu depois de publicado) */
  children?: ReactNode;
}) {
  return (
    <div className="k-video">
      <Capa src={src} nome={nome} tamanho={tamanho} />
      <div>
        {href
          ? <Link href={href} className="k-video-title" title={nome}>{nome}</Link>
          : <span className="k-video-title" title={nome}>{nome}</span>}
        {meta && <span className="k-video-meta">{meta}</span>}
        {slug && <span className="k-video-slug">{slug}</span>}
        {children}
      </div>
    </div>
  );
}

/** Célula de pessoa (ranking de consumo): retrato 28 (foto ou iniciais), o nome (link para a ficha) e a meta. */
export function CelulaPessoa({ nome, foto, href, meta }: { nome: string; foto: string | null; href?: string; meta?: ReactNode }) {
  return (
    <div className="k-video">
      <Avatar nome={nome} foto={foto} tamanho={28} />
      <div>
        {href
          ? <Link href={href} className="k-video-title" title={nome}>{nome}</Link>
          : <span className="k-video-title" title={nome}>{nome}</span>}
        {meta && <span className="k-video-meta">{meta}</span>}
      </div>
    </div>
  );
}
