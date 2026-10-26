import type { CSSProperties, ReactNode } from "react";
import Link from "next/link";
import { num } from "@/lib/formato";
import Capa from "./Capa";
import { propsDica } from "./Dica";
import Vazio from "./Vazio";

// Gráficos (design-system.md §11.18) — SVG/HTML desenhados no servidor com chart-1…chart-5, NESTA ordem
// (laranja → preto → taupe → areia → ardósia); verde e vermelho nunca como série. Todo gráfico tem: nome para o leitor
// de tela, valor exato na dica (hover E foco) e a tabela gêmea "Ver os números". Texto nunca na cor da série.
// Leitura marcada `suspeito` não entra: quem chama passa só leituras confiáveis (db.leiturasConfiaveis).
// Validador da skill dataviz (23/10, sobre a superfície `surface`): laranja × preto separam bem para daltonismo (ΔE 39,5) e passam
// 3:1 contra o card; o preto "reprova" em croma/claridade por ser neutro — é a cor decidida pelo Carlos ("não alterar").
// O gráfico de linha mede a largura no navegador: components/GraficoLinha.tsx.

export type Serie = 1 | 2 | 3 | 4 | 5;
const corDa = (s: Serie) => `var(--chart-${s})`;

/** Os números de um gráfico em tabela (WCAG e dataviz): fechada por padrão. */
export function TabelaGemea({ rotulo, colunas, linhas }: {
  rotulo: string;
  colunas: string[];
  linhas: ReactNode[][];
}) {
  return (
    <details className="k-details">
      <summary className="k-btn k-btn-ghost k-btn-sm">Ver os números</summary>
      <div
        className="k-table-wrap"
        role="region"
        aria-label={`Números: ${rotulo}`}
        tabIndex={0}
        style={{ "--table-min": "280px" } as CSSProperties}
      >
        <table className="k-table">
          <caption className="k-sr-only">{rotulo}</caption>
          <thead>
            <tr>{colunas.map((c, k) => <th key={`${c}-${k}`} scope="col" className={k > 0 ? "k-dir" : undefined}>{c}</th>)}</tr>
          </thead>
          <tbody>
            {linhas.map((l, i) => (
              <tr key={i}>{l.map((c, k) => <td key={k} className={k > 0 ? "k-dir k-num" : undefined}>{c}</td>)}</tr>
            ))}
          </tbody>
        </table>
      </div>
    </details>
  );
}

export type ItemBarra = {
  /** rótulo na barra — quebra em 2 linhas, nunca reticências (encurte antes, ex.: formato.cidade) */
  rotulo: string;
  valor: number;
  /** nome inteiro, para a dica e a tabela (padrão: o rótulo) */
  nome?: string;
  /** 2.ª linha da dica (padrão: o valor exato) */
  dica?: string;
};

/**
 * Barras horizontais (ranking): trilho surface-sunken, barra em destaque chart-1 (a maior, se ninguém disser outra),
 * as demais chart-2, valor tabular à direita. Cada linha é focável e tem dica com o número exato.
 */
export function Barras({ rotulo, itens, formato = num, destaque, vazio, colunaValor = "Valor" }: {
  /** o que o gráfico mostra (nome da lista e da tabela gêmea) */
  rotulo: string;
  itens: ItemBarra[];
  formato?: (n: number) => string;
  /** índice da barra em laranja; padrão = a de maior valor */
  destaque?: number;
  vazio?: { titulo: string; frase?: ReactNode };
  colunaValor?: string;
}) {
  if (itens.length === 0) {
    return <Vazio icone="desempenho" titulo={vazio?.titulo ?? "Sem dados nesta leitura"}>{vazio?.frase}</Vazio>;
  }
  const max = Math.max(1, ...itens.map((i) => i.valor));
  const iDestaque = destaque ?? itens.reduce((m, it, i, arr) => (it.valor > arr[m].valor ? i : m), 0);
  return (
    <div className="kx-grafico">
      <ul className="kx-barras" aria-label={rotulo}>
        {itens.map((it, i) => (
          <li key={`${it.rotulo}-${i}`} className="k-bar-row" tabIndex={0} {...propsDica(it.nome ?? it.rotulo, it.dica ?? num(it.valor))}>
            <span>{it.rotulo}</span>
            <span className="k-bar-track" aria-hidden="true">
              <i className={`k-bar-fill${i === iDestaque ? " is-focus" : ""}`} style={{ width: `${(it.valor / max) * 100}%` }} />
            </span>
            <b className="k-bar-value">{formato(it.valor)}</b>
          </li>
        ))}
      </ul>
      <TabelaGemea
        rotulo={rotulo}
        colunas={["", colunaValor]}
        linhas={itens.map((it) => [it.nome ?? it.rotulo, num(it.valor)])}
      />
    </div>
  );
}

/** Barra curta dentro de uma célula de tabela (o número vai ao lado, escrito). */
export function BarraNaCelula({ valor, max, children }: { valor: number; max: number; children: ReactNode }) {
  return (
    <span className="kx-barra-celula">
      <span className="k-bar-track" aria-hidden="true">
        <i className="k-bar-fill is-focus" style={{ width: `${(valor / Math.max(1, max)) * 100}%` }} />
      </span>
      {children}
    </span>
  );
}

export type Fatia = { rotulo: string; valor: number; serie: Serie; dica?: string };

/**
 * Rosca (partes de um todo, NO MÁXIMO 4 fatias): espessura 14, total no centro, 2px de folga entre fatias, legenda ao
 * lado com o valor (identidade nunca só pela cor) e a tabela gêmea.
 */
export function Rosca({ rotulo, fatias, rotuloCentro, formato = num }: {
  rotulo: string;
  fatias: Fatia[];
  rotuloCentro: string;
  formato?: (n: number) => string;
}) {
  const usadas = fatias.slice(0, 4);
  const total = usadas.reduce((s, f) => s + f.valor, 0);
  const R = 40;
  const C = 2 * Math.PI * R;
  let acumulado = 0;
  const descricao = `${rotulo}: ${usadas.map((f) => `${f.rotulo} ${formato(f.valor)}`).join(", ")}; total ${formato(total)}`;
  return (
    <div className="kx-grafico">
      <div className="kx-rosca">
        <svg className="k-chart" width={104} height={104} viewBox="0 0 104 104" role="img" aria-label={descricao}>
          <circle cx={52} cy={52} r={R} fill="none" className="kx-rosca-trilho" strokeWidth={14} />
          {total > 0 && usadas.map((f) => {
            const q = f.valor / total;
            const arco = (
              <circle
                key={f.rotulo}
                cx={52}
                cy={52}
                r={R}
                fill="none"
                stroke={corDa(f.serie)}
                strokeWidth={14}
                strokeDasharray={`${Math.max(0, q * C - (usadas.length > 1 ? 2 : 0))} ${C}`}
                strokeDashoffset={-acumulado * C}
                transform="rotate(-90 52 52)"
                {...propsDica(f.rotulo, f.dica ?? `${num(f.valor)} de ${num(total)}`)}
              />
            );
            acumulado += q;
            return arco;
          })}
          <text x={52} y={52} textAnchor="middle" className="kx-rosca-total">{formato(total)}</text>
          <text x={52} y={66} textAnchor="middle">{rotuloCentro}</text>
        </svg>
        <ul className="kx-rosca-legenda">
          {usadas.map((f) => (
            <li key={f.rotulo} tabIndex={0} {...propsDica(f.rotulo, f.dica ?? `${num(f.valor)} de ${num(total)}`)}>
              <i aria-hidden="true" style={{ background: corDa(f.serie) }} />
              {f.rotulo}
              <b className="k-num">{formato(f.valor)}</b>
            </li>
          ))}
        </ul>
      </div>
      <TabelaGemea
        rotulo={rotulo}
        colunas={["", "Valor", "Parte"]}
        linhas={usadas.map((f) => [
          f.rotulo, num(f.valor), total > 0 ? `${((f.valor / total) * 100).toLocaleString("pt-BR", { maximumFractionDigits: 1 })}%` : "—",
        ])}
      />
    </div>
  );
}

/** Sparkline 120×28 dentro de KPI: tendência sem eixos, ponto final marcado. Precisa de 2+ pontos. */
export function Sparkline({ x, y, rotulo, largura = 120, altura = 28 }: {
  x: number[]; y: number[]; rotulo: string; largura?: number; altura?: number;
}) {
  if (x.length < 2 || x.length !== y.length) return null;
  const x0 = x[0];
  const xMax = x[x.length - 1] - x0 || 1;
  const yMin = Math.min(...y);
  const yMax = Math.max(...y);
  const faixa = yMax - yMin || 1;
  const pts = x.map((xi, i) => [
    2 + ((largura - 4) * (xi - x0)) / xMax,
    yMax === yMin ? altura / 2 : altura - 3 - ((y[i] - yMin) / faixa) * (altura - 6),
  ]);
  const ultimo = pts[pts.length - 1];
  return (
    <svg className="k-chart" width={largura} height={altura} viewBox={`0 0 ${largura} ${altura}`} role="img" aria-label={rotulo}>
      <path className="s1" d={`M${pts.map((p) => p.map((v) => v.toFixed(1)).join(",")).join("L")}`} />
      <circle className="f1" cx={ultimo[0]} cy={ultimo[1]} r={2.5} />
    </svg>
  );
}

/** Legenda de 2+ séries (texto em ink-2, nunca na cor da série). */
export function Legenda({ series }: { series: { nome: string; serie: Serie }[] }) {
  return (
    <div className="k-legend">
      {series.map((s) => (
        <span key={s.nome}><i aria-hidden="true" style={{ background: corDa(s.serie) }} />{s.nome}</span>
      ))}
    </div>
  );
}

export type ItemBarraFina = {
  rotulo: string;
  /** o número que dá o comprimento da barra */
  valor: number;
  /** o que aparece à direita (já formatado: "54,4%", "1.741", "US$ 12,40") */
  texto: string;
  /** 2.ª linha da dica (padrão: o texto) */
  dica?: string;
};

/**
 * Barras finas (design-system.md §15.2, `.k-bar-row--fino`): trilho de 6px, valor em mono à direita; a 1.ª barra em
 * chart-1 (destaque), as demais chart-2. Cada linha é focável e tem a dica com o número; os números completos ficam na
 * tabela gêmea de quem chama (às vezes uma tabela serve a duas listas, como no Público).
 */
export function BarrasFinas({ rotulo, itens, destaque = 0, tokens }: {
  rotulo: string;
  itens: ItemBarraFina[];
  destaque?: number;
  /** o valor é contagem de tokens: accent-ink (decisão de 23/10) */
  tokens?: boolean;
}) {
  const max = Math.max(1, ...itens.map((i) => i.valor));
  return (
    <ul className="k-barras kx-lista-limpa" aria-label={rotulo}>
      {itens.map((it, i) => (
        <li key={`${it.rotulo}-${i}`} className="k-bar-row k-bar-row--fino" tabIndex={0} {...propsDica(it.rotulo, it.dica ?? it.texto)}>
          <span title={it.rotulo}>{it.rotulo}</span>
          <span className="k-bar-track" aria-hidden="true">
            <span className={`k-bar-fill${i === destaque ? " is-focus" : ""}`} style={{ width: `${(it.valor / max) * 100}%` }} />
          </span>
          <span className={`k-bar-value${tokens ? " k-tokens" : ""}`}>{it.texto}</span>
        </li>
      ))}
    </ul>
  );
}

/**
 * Medidor de % (design-system.md §15.2, `.k-medidor`): escala de 0 a 100 %, o valor sempre escrito; a conta vai na dica
 * (hover e foco) e também para o leitor de tela. Sem valor válido: trilho vazio e "—".
 */
export function Medidor({ pct, dica }: { pct: number | null; dica?: { titulo: string; detalhe?: string } }) {
  const texto = pct == null ? null : `${pct.toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 })}%`;
  return (
    <span className="k-medidor" tabIndex={dica ? 0 : undefined} {...(dica ? propsDica(dica.titulo, dica.detalhe) : {})}>
      <span className="k-medidor-trilho" aria-hidden="true">
        {pct != null && <span style={{ width: `${Math.max(0, Math.min(100, pct))}%` }} />}
      </span>
      {texto ? <span className="k-n">{texto}</span> : <span className="k-n k-muted"><span aria-hidden="true">—</span><span className="k-sr-only">sem valor válido</span></span>}
      {dica && <span className="k-sr-only">{`, ${dica.titulo}${dica.detalhe ? `: ${dica.detalhe}` : ""}`}</span>}
    </span>
  );
}

/** Posição no ranking: escrita no círculo; o 1.º em accent com texto on-accent (nada só por cor). */
export function PosicaoRanking({ n }: { n: number }) {
  return <span className={`k-rank-pos${n <= 3 ? ` is-${n}` : ""}`}>{n}<span className="k-sr-only">.º</span></span>;
}

/** Amostra de cor de uma legenda solta (fora do k-legend): a série ou o trilho (surface-sunken com contorno). */
export function AmostraSerie({ serie, rotulo }: { serie: Serie | "trilho"; rotulo: ReactNode }) {
  return (
    <span className="k-legend">
      <span>
        <i aria-hidden="true" className={serie === "trilho" ? "kx-amostra-trilho" : undefined} style={serie === "trilho" ? undefined : { background: corDa(serie) }} />
        {rotulo}
      </span>
    </span>
  );
}

/**
 * Barras finas largas (§15.2, `.k-bar-row--larga`): nome, barra e três números (tokens em accent-ink, custo, parte).
 * Abaixo de 640 px, a barra desce para baixo do nome e a parte sai (fica na tabela gêmea de quem chama).
 */
export function BarrasLargas({ rotulo, itens, destaque = 0 }: {
  rotulo: string;
  itens: { rotulo: string; valor: number; tokens: string; custo: string; parte: string; dica?: string }[];
  destaque?: number;
}) {
  const max = Math.max(1, ...itens.map((i) => i.valor));
  return (
    <ul className="k-barras kx-lista-limpa kx-barras-largas" aria-label={rotulo}>
      {itens.map((it, i) => (
        <li key={`${it.rotulo}-${i}`} className="k-bar-row k-bar-row--fino k-bar-row--larga" tabIndex={0} {...propsDica(it.rotulo, it.dica ?? `${it.tokens} tokens · ${it.custo} · ${it.parte}`)}>
          <span title={it.rotulo}>{it.rotulo}</span>
          <span className="k-bar-track" aria-hidden="true">
            <span className={`k-bar-fill${i === destaque ? " is-focus" : ""}`} style={{ width: `${(it.valor / max) * 100}%` }} />
          </span>
          <span className="k-bar-value k-tokens">{it.tokens}<span className="k-sr-only"> tokens</span></span>
          <span className="k-bar-value">{it.custo}</span>
          <span className="k-bar-value">{it.parte}</span>
        </li>
      ))}
    </ul>
  );
}

/** Barras com a capa (custo por vídeo): capa sm, nome e valor numa linha, a barra embaixo; a 1.ª em chart-1. */
export function BarrasComCapa({ rotulo, itens }: {
  rotulo: string;
  itens: { nome: string; capa: string | null; valor: number; texto: string; href?: string; dica?: string }[];
}) {
  const max = Math.max(1, ...itens.map((i) => i.valor));
  return (
    <ul className="kx-lista-limpa kx-barras-capa" aria-label={rotulo}>
      {itens.map((it, i) => (
        <li key={`${it.nome}-${i}`} className="k-video kx-barra-capa">
          <Capa src={it.capa} nome={it.nome} tamanho="sm" />
          <div className="kx-barra-capa-corpo">
            <span className="k-row kx-barra-capa-linha">
              {it.href
                ? <Link href={it.href} className="k-video-title" title={it.nome}>{it.nome}</Link>
                : <span className="k-video-title" title={it.nome}>{it.nome}</span>}
              <span className="k-mono">{it.texto}</span>
            </span>
            <span className="k-bar-track" aria-hidden="true">
              <span className={`k-bar-fill${i === 0 ? " is-focus" : ""}`} style={{ width: `${(it.valor / max) * 100}%` }} />
            </span>
          </div>
        </li>
      ))}
    </ul>
  );
}

/**
 * Barra empilhada (§15.2, `.k-empilhada`): partes de um todo numa linha de 8px, chart-1…3 nesta ordem, 2px de folga e
 * no mínimo 2px por parte (uma parte minúscula ainda aparece). Os números ficam escritos na lista ao lado (quem chama).
 */
export function BarraEmpilhada({ rotulo, partes }: { rotulo: string; partes: { valor: number; serie: Serie }[] }) {
  const total = partes.reduce((s, p) => s + p.valor, 0);
  return (
    <div className="k-empilhada" role="img" aria-label={rotulo}>
      {total > 0 && partes.filter((p) => p.valor > 0).map((p, i) => (
        <span key={i} style={{ width: `${(p.valor / total) * 100}%`, background: corDa(p.serie), minWidth: 2 }} />
      ))}
    </div>
  );
}
