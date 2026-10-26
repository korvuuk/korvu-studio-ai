"use client";

import { useLayoutEffect, useRef, useState } from "react";
import { compacto, compactoPartes, dolares, num } from "@/lib/formato";
import { propsDica } from "./Dica";
import { TabelaGemea } from "./Graficos";

// Linha / área (design-system.md §11.18): evolução no tempo. Série em foco chart-1 2px + área a 14%; comparação chart-2
// tracejada 1,5px; grade chart-grid; eixos 10px ink-2; UM eixo só. Desenhado na LARGURA MEDIDA do contêiner (nada de
// preserveAspectRatio="none", que entorta o texto dos eixos). Rótulo direto só no fim de cada linha, em ink-2.
// Hover E foco: uma faixa por leitura, maior que a marca, com a dica do valor exato e a linha de mira.

export type SerieLinha = { nome: string; valores: number[] };

const H = 180, T = 14, B = 24;

/** Passo "redondo" para 3 faixas no eixo y (0, 3M, 6M, 9M): o teto fica logo acima do maior valor. */
function passo(max: number) {
  if (max <= 0) return 1;
  const bruto = max / 3;
  const e = 10 ** Math.floor(Math.log10(bruto));
  const m = bruto / e;
  return ([1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10].find((c) => m <= c) ?? 10) * e;
}

// Só DADOS nas props (o servidor não pode mandar funções para um componente do navegador): os rótulos do eixo x vêm
// prontos, um para cada marca de `ticksX`; o formato dos números vem pelo NOME (pt-BR, lib/formato).
const FORMATOS = {
  /** "1.741" */
  num: { eixo: num, exato: num, curto: num },
  /** tokens: eixo "8M", rótulo "8,4M"; dica com o número inteiro */
  compacto: { eixo: (v: number) => { const p = compactoPartes(v); return `${p.valor.replace(/,0$/, "")}${p.unidade}`; }, exato: num, curto: compacto },
  /** custo em US$ (sem câmbio, decisão de 24/10): eixo "US$ 150"; dica e rótulo "US$ 86,63" */
  dolares: { eixo: (v: number) => dolares(v), exato: (v: number) => dolares(v, 2), curto: (v: number) => dolares(v, 2) },
} as const;

export default function GraficoLinha({ rotulo, x, ticksX, rotulosX, pontos, series, formato = "num", pico, semTabela }: {
  /** nome do gráfico para o leitor de tela e a tabela gêmea */
  rotulo: string;
  x: number[];
  ticksX: number[];
  /** texto de cada marca do eixo x, na mesma ordem de `ticksX` (ex.: "dia 3") */
  rotulosX: string[];
  /** rótulo de cada leitura (1.ª linha da dica e 1.ª coluna da tabela) */
  pontos: string[];
  /** 1 ou 2 séries no MESMO eixo: a 1.ª em foco (chart-1), a 2.ª comparação (chart-2) */
  series: SerieLinha[];
  formato?: keyof typeof FORMATOS;
  /** marca o maior ponto da 1.ª série com o rótulo "23 out · 8,4M" (no lugar do rótulo do fim da linha) */
  pico?: boolean;
  /** a tabela gêmea fica com quem chama (ex.: uma tabela só para Tokens e Custo, em US$) */
  semTabela?: boolean;
}) {
  const caixa = useRef<HTMLDivElement>(null);
  const [W, setW] = useState(0);
  const [mira, setMira] = useState<number | null>(null);

  useLayoutEffect(() => {
    const el = caixa.current;
    if (!el) return;
    const medir = () => setW(Math.round(el.clientWidth));
    medir();
    const ro = new ResizeObserver(medir);
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const f = FORMATOS[formato];
  const usadas = series.slice(0, 2);
  const p = passo(Math.max(0, ...usadas.flatMap((s) => s.valores)));
  const yTicks = [0, p, 2 * p, 3 * p];
  const yMax = 3 * p;
  // margem esquerda do tamanho do maior rótulo do eixo (10px: ~6px por caractere); à direita, o rótulo do fim da linha
  const L = 10 + 6 * Math.max(...yTicks.map((v) => f.eixo(v).length));
  const R = pico ? 12 : 44;
  const xMin = Math.min(...x, ...ticksX);
  const xMax = Math.max(...x, ...ticksX);
  const X = (v: number) => L + ((W - L - R) * (v - xMin)) / (xMax - xMin || 1);
  const Y = (v: number) => T + (H - T - B) * (1 - v / yMax);
  const n = x.length - 1;
  const caminho = (vs: number[]) => `M${x.map((xi, i) => `${X(xi).toFixed(1)},${Y(vs[i]).toFixed(1)}`).join("L")}`;
  const textoPonto = (i: number) => usadas.map((s) => `${s.nome} ${f.exato(s.valores[i])}`).join(" · ");
  const iPico = pico && usadas[0] ? usadas[0].valores.indexOf(Math.max(...usadas[0].valores)) : -1;
  const ancoraPico = iPico < 0 ? "middle" : X(x[iPico]) > W * 0.8 ? "end" : X(x[iPico]) < W * 0.2 ? "start" : "middle";

  return (
    <div className="kx-grafico">
      <div ref={caixa} className="kx-linha">
        {W > 0 && n >= 0 && (
          <svg className="k-chart" width={W} height={H} viewBox={`0 0 ${W} ${H}`} role="img"
            aria-label={`${rotulo}; os números estão na tabela "Ver os números"`}>
            {yTicks.map((v) => (
              <g key={v}>
                <line className="grid" x1={L} x2={W - R} y1={Y(v)} y2={Y(v)} />
                <text x={L - 6} y={Y(v) + 3} textAnchor="end">{f.eixo(v)}</text>
              </g>
            ))}
            {/* nas pontas, o rótulo se alinha para dentro (não corta "23 out" na borda do gráfico) */}
            {ticksX.map((v, i) => (
              <text key={v} x={X(v)} y={H - 6} textAnchor={v === xMin ? "start" : v === xMax ? "end" : "middle"}>{rotulosX[i] ?? num(v)}</text>
            ))}
            {usadas[0] && (
              <path className="a1" d={`${caminho(usadas[0].valores)}L${X(x[n]).toFixed(1)},${Y(0)}L${X(x[0]).toFixed(1)},${Y(0)}Z`} />
            )}
            {usadas[1] && <path className="s2" d={caminho(usadas[1].valores)} />}
            {usadas[0] && <path className="s1" d={caminho(usadas[0].valores)} />}
            {!pico && usadas[0] && <circle className="kx-linha-fim" cx={X(x[n])} cy={Y(usadas[0].valores[n])} r={4} />}
            {!pico && usadas.map((s) => (
              <text key={s.nome} x={X(x[n]) + 8} y={Y(s.valores[n]) + 4}>{f.curto(s.valores[n])}</text>
            ))}
            {iPico >= 0 && (
              <g aria-hidden="true">
                <circle className="kx-linha-fim" cx={X(x[iPico])} cy={Y(usadas[0].valores[iPico])} r={4} />
                <text className="kx-linha-pico" x={X(x[iPico])} y={Math.max(10, Y(usadas[0].valores[iPico]) - 9)} textAnchor={ancoraPico}>
                  {pontos[iPico]} · {f.curto(usadas[0].valores[iPico])}
                </text>
              </g>
            )}
            {mira !== null && <line className="kx-linha-mira" x1={X(x[mira])} x2={X(x[mira])} y1={T} y2={H - B} />}
            {x.map((xi, i) => {
              const meio = X(xi);
              const x0 = i ? (X(x[i - 1]) + meio) / 2 : L;
              const x1 = i < n ? (meio + X(x[i + 1])) / 2 : W - R;
              return (
                <rect
                  key={i}
                  className="kx-linha-alvo"
                  x={x0}
                  y={T}
                  width={Math.max(24, x1 - x0)}
                  height={H - T - B}
                  tabIndex={0}
                  aria-label={`${pontos[i]}: ${textoPonto(i)}`}
                  {...propsDica(pontos[i], textoPonto(i))}
                  onPointerEnter={() => setMira(i)}
                  onPointerLeave={() => setMira(null)}
                  onFocus={() => setMira(i)}
                  onBlur={() => setMira(null)}
                />
              );
            })}
          </svg>
        )}
      </div>
      {!semTabela && (
        <TabelaGemea
          rotulo={rotulo}
          colunas={["Leitura", ...usadas.map((s) => s.nome)]}
          linhas={x.map((_, i) => [pontos[i], ...usadas.map((s) => f.exato(s.valores[i]))])}
        />
      )}
    </div>
  );
}
