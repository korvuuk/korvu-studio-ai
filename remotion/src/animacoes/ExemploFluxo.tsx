import { getLength } from "@remotion/paths";
import React from "react";
import { interpolate, interpolateColors, useCurrentFrame, useVideoConfig } from "remotion";
import { COR, EASING, FONTE, ROTULO, useTempo } from "../brand";
import { SelectionHighlight } from "../components/SelectionHighlight";
import { normalizar } from "../lib/texto";
import type { AnimacaoProps } from "./registry";

const ETAPAS_PADRAO = ["Prompt", "IA", "Resposta"];

/** Tamanho do desenho "de referência"; é escalado para caber na área. */
const DESENHO = { largura: 760, caixaAltura: 150, seta: 96 };

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/**
 * Exemplo: 3 caixas "Prompt → IA → Resposta".
 * Cada caixa acende quando a palavra correspondente é dita (`palavras`);
 * se a palavra não aparecer, as etapas são distribuídas no tempo do overlay.
 */
export const ExemploFluxo: React.FC<AnimacaoProps> = (props) => {
  const { palavras, largura, altura, duracaoFrames } = props;
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const tempo = useTempo();

  const etapas = Array.isArray(props.etapas)
    ? (props.etapas as unknown[]).map(String)
    : ETAPAS_PADRAO;

  // Frame de ativação de cada etapa (sincronizado com a fala).
  const ativacoes = etapas.map((etapa, i) => {
    const alvo = normalizar(etapa);
    const p = palavras.find((w) => normalizar(w.texto) === alvo);
    if (p) return Math.round((p.inicioMs / 1000) * fps);
    return Math.round(((i + 0.3) / etapas.length) * duracaoFrames);
  });

  const alturaDesenho =
    etapas.length * DESENHO.caixaAltura + (etapas.length - 1) * DESENHO.seta;
  const escala = Math.min(1, (largura * 0.9) / DESENHO.largura, (altura * 0.92) / alturaDesenho);
  const ativa = ativacoes.reduce((acc, f, i) => (frame >= f ? i : acc), -1);

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <div
        style={{
          width: DESENHO.largura,
          height: alturaDesenho,
          position: "relative",
          scale: String(escala),
          fontFamily: FONTE.familia,
        }}
      >
        {etapas.map((etapa, i) => {
          const f0 = ativacoes[i];
          const y = i * (DESENHO.caixaAltura + DESENHO.seta);
          const eAtiva = i === ativa;
          const jaPassou = i < ativa;
          const entrada = interpolate(frame, [f0, f0 + tempo.entrada], [0, 1], {
            ...clamp,
            easing: EASING.entrada,
          });
          const destaque = interpolate(frame, [f0, f0 + tempo.karaoke], [0, 1], clamp);
          return (
            <React.Fragment key={etapa + i}>
              {i > 0 ? (
                <Seta
                  y={y - DESENHO.seta}
                  progresso={interpolate(frame, [f0 - 8, f0], [0, 1], {
                    ...clamp,
                    easing: EASING.selecao,
                  })}
                />
              ) : null}
              <div
                style={{
                  position: "absolute",
                  left: 0,
                  top: y,
                  width: DESENHO.largura,
                  height: DESENHO.caixaAltura,
                  borderRadius: 22,
                  border: `2px solid ${eAtiva ? "rgba(242,242,242,0.35)" : COR.borda}`,
                  backgroundColor: eAtiva ? COR.selecao : "rgba(255,255,255,0.03)",
                  display: "flex",
                  alignItems: "center",
                  padding: "0 44px",
                  gap: 36,
                  opacity: interpolate(entrada, [0, 1], [0.28, 1]),
                  translate: `0px ${interpolate(entrada, [0, 1], [tempo.subidaPx, 0])}px`,
                }}
              >
                <span
                  style={{
                    fontSize: ROTULO.tamanho + 4,
                    fontWeight: ROTULO.peso,
                    letterSpacing: ROTULO.tracking,
                    color: COR.cinza,
                    fontVariantNumeric: "tabular-nums",
                  }}
                >
                  {String(i + 1).padStart(2, "0")}
                </span>
                <span
                  style={{
                    fontSize: 68,
                    fontWeight: 800,
                    letterSpacing: "-0.02em",
                    color: interpolateColors(
                      eAtiva || jaPassou ? destaque : 0,
                      [0, 1],
                      [COR.cinza, eAtiva ? COR.texto : "#C8C8C8"],
                    ),
                  }}
                >
                  {eAtiva ? (
                    <SelectionHighlight inicio={f0 + 2} cor="#45484D">
                      {etapa}
                    </SelectionHighlight>
                  ) : (
                    etapa
                  )}
                </span>
              </div>
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};

const Seta: React.FC<{ y: number; progresso: number }> = ({ y, progresso }) => {
  const cx = DESENHO.largura / 2;
  const haste = `M ${cx} 14 L ${cx} ${DESENHO.seta - 18}`;
  const ponta = `M ${cx - 16} ${DESENHO.seta - 34} L ${cx} ${DESENHO.seta - 16} L ${cx + 16} ${DESENHO.seta - 34}`;
  const lh = getLength(haste);
  const lp = getLength(ponta);
  const pPonta = interpolate(progresso, [0.6, 1], [0, 1], clamp);
  return (
    <svg
      width={DESENHO.largura}
      height={DESENHO.seta}
      style={{ position: "absolute", left: 0, top: y, overflow: "visible" }}
    >
      <path
        d={haste}
        stroke={COR.cinza}
        strokeWidth={4}
        strokeLinecap="round"
        fill="none"
        strokeDasharray={lh}
        strokeDashoffset={lh * (1 - interpolate(progresso, [0, 0.7], [0, 1], clamp))}
      />
      <path
        d={ponta}
        stroke={COR.cinza}
        strokeWidth={4}
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
        strokeDasharray={lp}
        strokeDashoffset={lp * (1 - pPonta)}
        opacity={pPonta > 0 ? 1 : 0}
      />
    </svg>
  );
};
