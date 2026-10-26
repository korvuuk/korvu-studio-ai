// Carregando (design-system.md §12.1, prévia carregando.html): blocos em surface-sunken no LUGAR EXATO do conteúdo,
// dentro dos mesmos k-card / k-kpi / k-table da página, para nada pular quando os dados chegam. Só uma respiração lenta
// de opacidade, e nenhuma com prefers-reduced-motion (acrescimos.css). Blocos aria-hidden; o contêiner leva
// role="status" + "Carregando os dados do painel…" para o leitor de tela. Nunca um spinner de página inteira.

import type { CSSProperties } from "react";

type Tipo = "h1" | "cap" | "line" | "title" | "metric" | "chip" | "avatar" | "thumb";

export function Bloco({ tipo, largura, estilo }: { tipo?: Tipo; largura?: string; estilo?: CSSProperties }) {
  return (
    <span
      aria-hidden="true"
      className={`k-skel${tipo ? ` k-skel-${tipo}` : ""}`}
      style={largura ? { width: largura, ...estilo } : estilo}
    />
  );
}

function KpiEsqueleto() {
  return (
    <div className="k-card k-kpi k-span-3" aria-hidden="true">
      <Bloco tipo="cap" />
      <Bloco tipo="metric" estilo={{ marginTop: 6 }} />
      <Bloco tipo="line" largura="40%" estilo={{ marginTop: 6 }} />
    </div>
  );
}

function LinhaEsqueleto() {
  return (
    <tr>
      <td>
        <div className="k-video">
          <Bloco tipo="thumb" />
          <div className="kx-cresce">
            <Bloco tipo="line" largura="70%" />
            <Bloco tipo="line" largura="40%" estilo={{ marginTop: 6, height: 11 }} />
          </div>
        </div>
      </td>
      <td><Bloco tipo="line" largura="60%" /></td>
      <td><Bloco tipo="chip" /></td>
    </tr>
  );
}

/** O esqueleto de uma página do painel: título, uma linha de 4 KPIs e uma tabela. */
export default function Esqueleto() {
  return (
    <div role="status" aria-live="polite">
      <span className="k-sr-only">Carregando os dados do painel…</span>
      <header className="k-page-head" aria-hidden="true">
        <Bloco tipo="h1" />
      </header>
      <section className="k-section" aria-hidden="true">
        <div className="k-grid k-grid--tiles">
          {[0, 1, 2, 3].map((i) => <KpiEsqueleto key={i} />)}
        </div>
      </section>
      <section className="k-section" aria-hidden="true">
        <div className="k-card kx-recorte">
          <div className="k-table-wrap" style={{ "--table-min": "640px" } as CSSProperties}>
            <table className="k-table">
              <thead>
                <tr>
                  <th><Bloco tipo="cap" /></th>
                  <th><Bloco tipo="cap" largura="56px" /></th>
                  <th><Bloco tipo="cap" largura="56px" /></th>
                </tr>
              </thead>
              <tbody>
                {[0, 1, 2, 3].map((i) => <LinhaEsqueleto key={i} />)}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </div>
  );
}

// ── Esqueletos por bloco (telas de 23/10: cada bloco carrega no seu Suspense) ──────────────────────────────────────

function Carregando({ oque, children, className }: { oque: string; children: React.ReactNode; className?: string }) {
  return (
    <div role="status" className={className}>
      <span className="k-sr-only">{`Carregando ${oque}…`}</span>
      {children}
    </div>
  );
}

/** Linha de KPIs: n cartões com rótulo, valor e rodapé. */
export function EsqueletoKpis({ n = 4, oque = "os números" }: { n?: number; oque?: string }) {
  return (
    <Carregando oque={oque} className="k-grid k-grid--tiles">
      {Array.from({ length: n }, (_, i) => (
        <div key={i} className={`k-card k-kpi ${n === 3 ? "k-span-4" : "k-span-3"}`} aria-hidden="true">
          <Bloco tipo="cap" />
          <Bloco tipo="metric" estilo={{ marginTop: 6 }} />
          <Bloco tipo="line" largura="40%" estilo={{ marginTop: 6 }} />
        </div>
      ))}
    </Carregando>
  );
}

/** Cartões com capa ou foto (publicações, agentes): `classe` = a grade do bloco (k-posts, k-agentes). */
export function EsqueletoCartoes({ n = 5, classe = "k-posts", oque = "os cartões" }: { n?: number; classe?: string; oque?: string }) {
  return (
    <Carregando oque={oque} className={classe}>
      {Array.from({ length: n }, (_, i) => (
        <div key={i} className="k-card k-post" aria-hidden="true">
          <Bloco tipo="thumb" estilo={{ width: 36, height: 64 }} />
          <div className="k-post-corpo">
            <Bloco tipo="cap" largura="60%" />
            <Bloco tipo="line" largura="80%" />
            <Bloco tipo="line" largura="50%" />
          </div>
        </div>
      ))}
    </Carregando>
  );
}

/** Um cartão de gráfico ou lista: título, subtítulo e o corpo (n linhas ou uma área). */
export function EsqueletoCard({ linhas = 0, altura = 180, oque = "esta parte", className }: {
  linhas?: number; altura?: number; oque?: string; className?: string;
}) {
  return (
    <Carregando oque={oque} className={["k-card k-pad", className].filter(Boolean).join(" ")}>
      <div aria-hidden="true">
        <Bloco tipo="title" largura="45%" />
        <Bloco tipo="line" largura="30%" estilo={{ marginTop: 8 }} />
        {linhas > 0 ? (
          <div className="kx-pilha-curta" style={{ marginTop: 16 }}>
            {Array.from({ length: linhas }, (_, i) => <Bloco key={i} tipo="line" largura={`${90 - i * 7}%`} />)}
          </div>
        ) : (
          <Bloco estilo={{ marginTop: 16, height: altura, width: "100%" }} />
        )}
      </div>
    </Carregando>
  );
}

/** Tabela dentro de card: cabeçalho e n linhas com capa. */
export function EsqueletoTabela({ linhas = 4, oque = "a tabela" }: { linhas?: number; oque?: string }) {
  return (
    <Carregando oque={oque} className="k-card kx-recorte">
      <table className="k-table" aria-hidden="true">
        <thead><tr><th><Bloco tipo="cap" /></th><th><Bloco tipo="cap" largura="56px" /></th><th><Bloco tipo="cap" largura="56px" /></th></tr></thead>
        <tbody>
          {Array.from({ length: linhas }, (_, i) => <LinhaEsqueleto key={i} />)}
        </tbody>
      </table>
    </Carregando>
  );
}
