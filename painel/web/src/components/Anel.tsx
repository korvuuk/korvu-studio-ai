import type { ReactNode } from "react";

// Anel (design-system.md §15.2, `.k-anel`): trilho surface-sunken e o valor em chart-1, girado para começar no alto.
// - AnelMedidor: UMA proporção (fora da bolha: 60 % de quem foi alcançado não segue). Não é rosca de 2 fatias (dataviz).
// - AnelPartes: partes de um todo (≤ 4 fatias, chart-1…4 nesta ordem, 2px de folga), com o total no centro.

export function AnelMedidor({ fracao, rotulo, tamanho = 64, espessura = 8, centro }: {
  /** 0–1 */
  fracao: number;
  /** a frase lida pelo leitor de tela: "60% do alcance vem de quem não segue a conta" */
  rotulo: string;
  tamanho?: number;
  espessura?: number;
  /** o número no centro (HTML por cima do SVG) */
  centro?: ReactNode;
}) {
  const c = tamanho / 2;
  const r = c - espessura / 2 - 1;
  const C = 2 * Math.PI * r;
  const f = Math.max(0, Math.min(1, fracao));
  const svg = (
    <svg className="k-anel" viewBox={`0 0 ${tamanho} ${tamanho}`} width={tamanho} height={tamanho} role="img" aria-label={rotulo}>
      <circle className="trilho" cx={c} cy={c} r={r} fill="none" strokeWidth={espessura} />
      <circle className="valor" cx={c} cy={c} r={r} fill="none" strokeWidth={espessura} strokeDasharray={`${(f * C).toFixed(2)} ${C.toFixed(2)}`} />
    </svg>
  );
  if (!centro) return svg;
  return (
    <div className="kx-anel-partes" style={{ width: tamanho, height: tamanho }}>
      {svg}
      <div className="kx-anel-centro">{centro}</div>
    </div>
  );
}

export type ParteAnel = { rotulo: string; valor: number; serie: 1 | 2 | 3 | 4 };

export function AnelPartes({ partes, rotulo, centro, tamanho = 112, espessura = 14 }: {
  partes: ParteAnel[];
  /** "Tokens por modelo: Opus 5.5 83%, Sonnet 5.5 12%, Fable 5.1 5%" */
  rotulo: string;
  /** o total no centro (HTML por cima do SVG, como na maquete) */
  centro?: ReactNode;
  tamanho?: number;
  espessura?: number;
}) {
  const c = tamanho / 2;
  const r = c - espessura / 2;
  const C = 2 * Math.PI * r;
  const usadas = partes.slice(0, 4).filter((p) => p.valor > 0);
  const total = usadas.reduce((s, p) => s + p.valor, 0);
  let acumulado = 0;
  return (
    <div className="kx-anel-partes" style={{ width: tamanho, height: tamanho }}>
      <svg className="k-anel" viewBox={`0 0 ${tamanho} ${tamanho}`} width={tamanho} height={tamanho} role="img" aria-label={rotulo}>
        <circle className="trilho" cx={c} cy={c} r={r} fill="none" strokeWidth={espessura} />
        {total > 0 && usadas.map((p) => {
          const q = p.valor / total;
          const arco = (
            <circle
              key={p.rotulo}
              cx={c} cy={c} r={r} fill="none" strokeWidth={espessura}
              stroke={`var(--chart-${p.serie})`}
              strokeDasharray={`${Math.max(0, q * C - (usadas.length > 1 ? 2 : 0)).toFixed(2)} ${C.toFixed(2)}`}
              strokeDashoffset={(-acumulado * C).toFixed(2)}
            />
          );
          acumulado += q;
          return arco;
        })}
      </svg>
      {centro && <div className="kx-anel-centro">{centro}</div>}
    </div>
  );
}

/** Legenda das partes ao lado do anel: amostra da cor (chart-N), o nome em mono e a parte; tokens em accent-ink. */
export function LegendaPartes({ itens, tokens }: { itens: { rotulo: string; texto: string; serie: 1 | 2 | 3 | 4 }[]; tokens?: boolean }) {
  return (
    <ul className="kx-lista-limpa kx-legenda-partes">
      {itens.map((p) => (
        <li key={p.rotulo}>
          <i aria-hidden="true" style={{ background: `var(--chart-${p.serie})` }} />
          <span className="k-mono kx-cresce">{p.rotulo}</span>
          <span className={`k-mono${tokens ? " k-tokens" : ""}`}>{p.texto}</span>
        </li>
      ))}
    </ul>
  );
}

/**
 * Legenda das partes em lista chave-valor (`.k-kv`, Tokens e custos · por modelo): amostra + nome em mono à esquerda;
 * à direita, a parte dos tokens (accent-ink) e, embaixo, o custo e a parte do custo.
 */
export function LegendaPartesKv({ itens }: { itens: { rotulo: string; serie: 1 | 2 | 3 | 4; tokens: string; custo: string }[] }) {
  return (
    <ul className="k-kv">
      {itens.map((p) => (
        <li key={p.rotulo}>
          <span className="k-row kx-row-8">
            <i aria-hidden="true" className="kx-amostra" style={{ background: `var(--chart-${p.serie})` }} />
            <span className="k-mono">{p.rotulo}</span>
          </span>
          <span className="k-kv-v">
            <span className="k-mono k-tokens">{p.tokens}</span>
            <br />
            <span className="k-mono">{p.custo}</span>
          </span>
        </li>
      ))}
    </ul>
  );
}
