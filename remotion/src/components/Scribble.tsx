import { getLength } from "@remotion/paths";
import React, { useId, useMemo } from "react";
import { interpolate, random, useCurrentFrame } from "remotion";
import { COR, EASING, useTempo } from "../brand";

type Props = {
  /** Largura do sublinhado (≈ largura da palavra). */
  largura: number;
  altura?: number;
  cor?: string;
  espessura?: number;
  /** Frame (local) em que o traço começa a ser desenhado. */
  inicio?: number;
  duracao?: number;
  /** Força o progresso (0–1), ex.: capa estática. */
  progresso?: number;
  /** Mesma semente → mesmo desenho (determinístico). */
  semente?: string | number;
  rabicho?: boolean;
  style?: React.CSSProperties;
};

type Ponto = readonly [number, number];

const fmt = (n: number): string => n.toFixed(2);

/** Catmull-Rom → Bézier cúbica (curva suave passando pelos pontos). */
const curvaSuave = (pts: Ponto[]): string => {
  let d = `M ${fmt(pts[0][0])} ${fmt(pts[0][1])}`;
  for (let i = 0; i < pts.length - 1; i++) {
    const p0 = pts[i - 1] ?? pts[i];
    const p1 = pts[i];
    const p2 = pts[i + 1];
    const p3 = pts[i + 2] ?? p2;
    const c1x = p1[0] + (p2[0] - p0[0]) / 6;
    const c1y = p1[1] + (p2[1] - p0[1]) / 6;
    const c2x = p2[0] - (p3[0] - p1[0]) / 6;
    const c2y = p2[1] - (p3[1] - p1[1]) / 6;
    d += ` C ${fmt(c1x)} ${fmt(c1y)}, ${fmt(c2x)} ${fmt(c2y)}, ${fmt(p2[0])} ${fmt(p2[1])}`;
  }
  return d;
};

type Traco = {
  d: string;
  comprimento: number;
  espessura: number;
  opacidade: number;
  atraso: number;
};

/** Camadas do "pincel seco": principal + 2 passadas mais finas e deslocadas. */
const CAMADAS = [
  { x0: -0.03, x1: 1.02, dy: 0, esp: 1, opac: 1, atraso: 0 },
  { x0: 0.02, x1: 0.95, dy: -0.2, esp: 0.5, opac: 0.85, atraso: 0.12 },
  { x0: 0.07, x1: 0.88, dy: 0.2, esp: 0.38, opac: 0.7, atraso: 0.22 },
] as const;

const gerarTracos = (
  largura: number,
  altura: number,
  espessura: number,
  semente: string | number,
  rabicho: boolean,
): Traco[] => {
  const baseY = altura * 0.5;
  const subida = altura * 0.22; // sobe levemente para a direita
  return CAMADAS.map((c, idx) => {
    const n = 7;
    const pts: Ponto[] = [];
    for (let i = 0; i < n; i++) {
      const u = i / (n - 1);
      const jx = (random(`${semente}-x-${idx}-${i}`) - 0.5) * largura * 0.03;
      const jy = (random(`${semente}-y-${idx}-${i}`) - 0.5) * altura * 0.22;
      const barriga = Math.sin(u * Math.PI) * altura * 0.1;
      pts.push([
        largura * (c.x0 + (c.x1 - c.x0) * u) + (i === 0 || i === n - 1 ? 0 : jx),
        baseY + c.dy * altura + barriga - subida * (u - 0.5) + jy,
      ]);
    }
    if (rabicho && idx === 0) {
      // "rabicho": o pincel volta para a esquerda e para baixo no fim
      const [xe, ye] = pts[pts.length - 1];
      pts.push([xe - largura * 0.05, ye + altura * 0.3]);
      pts.push([xe - largura * 0.22, ye + altura * 0.48]);
    }
    const d = curvaSuave(pts);
    return {
      d,
      comprimento: getLength(d),
      espessura: espessura * c.esp,
      opacidade: c.opac,
      atraso: c.atraso,
    };
  });
};

/**
 * Sublinhado desenhado à mão (pincel seco) com animação de traço
 * (`strokeDashoffset`). Determinístico pela `semente`.
 */
export const Scribble: React.FC<Props> = ({
  largura,
  altura = Math.min(56, Math.max(24, largura * 0.11)),
  cor = COR.rabisco,
  espessura = Math.min(16, Math.max(6, altura * 0.3)),
  inicio = 0,
  duracao: duracaoProp,
  progresso,
  semente = "rabisco",
  rabicho = true,
  style,
}) => {
  const frame = useCurrentFrame();
  const tempo = useTempo();
  const duracao = duracaoProp ?? tempo.rabisco;
  const idFiltro = `seco-${useId().replace(/[^a-zA-Z0-9_-]/g, "")}`;
  const tracos = useMemo(
    () => gerarTracos(largura, altura, espessura, semente, rabicho),
    [largura, altura, espessura, semente, rabicho],
  );
  const semNum = Math.floor(random(`${semente}-filtro`) * 1000);

  const p =
    progresso ??
    interpolate(frame, [inicio, inicio + duracao], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });

  return (
    <svg
      width={largura}
      height={altura}
      viewBox={`0 0 ${largura} ${altura}`}
      style={{ overflow: "visible", pointerEvents: "none", ...style }}
    >
      <defs>
        <filter
          id={idFiltro}
          x="-20%"
          y="-80%"
          width="140%"
          height="260%"
          colorInterpolationFilters="sRGB"
        >
          {/* estrias horizontais (cerdas secas) */}
          <feTurbulence
            type="fractalNoise"
            baseFrequency="0.012 0.42"
            numOctaves={2}
            seed={semNum}
            result="ruido"
          />
          <feColorMatrix
            in="ruido"
            type="matrix"
            values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -2.6 0 0 0 2.25"
            result="mascara"
          />
          <feComposite in="SourceGraphic" in2="mascara" operator="in" result="seco" />
          {/* borda irregular */}
          <feTurbulence
            type="fractalNoise"
            baseFrequency="0.06"
            numOctaves={1}
            seed={semNum + 1}
            result="ruido2"
          />
          <feDisplacementMap
            in="seco"
            in2="ruido2"
            scale={3}
            xChannelSelector="R"
            yChannelSelector="G"
          />
        </filter>
      </defs>
      <g filter={`url(#${idFiltro})`}>
        {tracos.map((t, i) => {
          const pi = interpolate(p, [t.atraso, t.atraso + 0.78], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: EASING.rabisco,
          });
          return (
            <path
              key={i}
              d={t.d}
              fill="none"
              stroke={cor}
              strokeWidth={t.espessura}
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeOpacity={t.opacidade}
              strokeDasharray={t.comprimento}
              strokeDashoffset={t.comprimento * (1 - pi)}
              opacity={pi > 0 ? 1 : 0}
            />
          );
        })}
      </g>
    </svg>
  );
};
