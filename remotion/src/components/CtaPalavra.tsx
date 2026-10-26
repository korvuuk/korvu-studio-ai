/**
 * CTA final em cartão grande (decisão do Carlos, 14/10): "comenta" em cima, a PALAVRA gigante no meio, uma linha
 * pequena embaixo. Visual editorial de 21/10 (`00-marca/design-system/korvu-editorial.md`): cartão de papel sem
 * canto nem sombra, palavra em minúsculas SEM ponto (Bricolage Grotesque 800, acento) — sem carimbo
 * (Carlos, 21/10: "vai ficar muito poluído"; só o cartão e o texto). Edição, não muda o roteiro.
 *
 * Usado dentro de uma <Sequence> que começa no "comenta" falado: o frame 0 aqui = início da janela.
 * Tokens (cores, tamanhos, posição, tempos) em `brand.ts` → `CTA` / `CTA_COR` / `EDITORIAL`.
 */
import React, { useMemo } from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { AREA_SEGURA, CTA, CTA_COR, EASING, EDITORIAL, FONTE, useFontesProntas, VIDEO } from "../brand";
import { larguraTexto } from "../lib/medidas";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

export type CtaPalavraProps = {
  palavra: string;
  topo?: string | null;
  rodape?: string | null;
  /** Duração da janela (frames) — para a saída. */
  duracao: number;
  /** Estado final sem animação (stills de conferência). */
  estatico?: boolean;
};

export const CtaPalavra: React.FC<CtaPalavraProps> = ({
  palavra,
  topo = "comenta",
  rodape,
  duracao,
  estatico = false,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const prontas = useFontesProntas();

  // Sem ponto depois da palavra (Carlos, 21/10): "aula." pode fazer a pessoa comentar com o ponto ou achar que faz parte.
  const textoPalavra = palavra.trim().toLowerCase();
  const larguraCartao = Math.min(CTA.larguraCartao, AREA_SEGURA.largura);
  const larguraUtil = larguraCartao - CTA.padding.x * 2;

  // Maior tamanho (≤ tamanhoMax) em que a palavra cabe na largura útil do cartão.
  const tamanho = useMemo(() => {
    if (!prontas) return CTA.tamanhoMin;
    for (let t = CTA.tamanhoMax; t > CTA.tamanhoMin; t -= 2) {
      const w = larguraTexto(textoPalavra, t, { peso: CTA.peso, tracking: CTA.tracking, familia: FONTE.display });
      if (w <= larguraUtil) return t;
    }
    return CTA.tamanhoMin;
  }, [prontas, textoPalavra, larguraUtil]);

  // Rodapé longo encolhe para caber no cartão (nunca abaixo de 28 px).
  const tamanhoRodape = useMemo(() => {
    if (!prontas || !rodape) return CTA.rodape.tamanho;
    for (let t = CTA.rodape.tamanho; t > 28; t -= 1) {
      const w = larguraTexto(rodape, t, { peso: CTA.rodape.peso, tracking: "0", familia: FONTE.texto });
      if (w <= larguraUtil) return t;
    }
    return 28;
  }, [prontas, rodape, larguraUtil]);

  const f = estatico ? 10_000 : frame;
  // Cartão sobe e aparece; a palavra entra com mola curta (sem bounce exagerado).
  const opacCartao = interpolate(f, [0, 4], [0, 1], clamp);
  const subida = interpolate(f, [0, 6], [24, 0], { ...clamp, easing: EASING.entrada });
  const mola = estatico
    ? 1
    : spring({ frame: f - 2, fps, durationInFrames: CTA.entradaFrames, config: { damping: 13, stiffness: 200, mass: 0.6 } });
  const escala = interpolate(mola, [0, 1], [0.6, 1]);
  const opacRodape = interpolate(f, [CTA.entradaFrames - 1, CTA.entradaFrames + 5], [0, 1], clamp);
  const saida = estatico ? 1 : interpolate(frame, [duracao - CTA.saidaFrames, duracao], [1, 0], clamp);

  if (!prontas) return null;

  // Centrado na área útil (x 65–960), não no quadro: a borda direita fica longe dos botões do app.
  const esquerda = AREA_SEGURA.x + (AREA_SEGURA.largura - larguraCartao) / 2;

  return (
    <AbsoluteFill style={{ opacity: saida, pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          left: esquerda,
          width: larguraCartao,
          bottom: VIDEO.altura - CTA.baseY,
          background: EDITORIAL.papel,
          padding: `${CTA.padding.topo}px ${CTA.padding.x}px ${CTA.padding.base}px`,
          opacity: opacCartao,
          transform: `translateY(${subida}px)`,
        }}
      >
        {topo ? (
          <div
            style={{
              fontFamily: FONTE.texto,
              fontSize: CTA.topo.tamanho,
              fontWeight: CTA.topo.peso,
              color: CTA.topo.cor,
              lineHeight: 1.1,
            }}
          >
            {topo}
          </div>
        ) : null}
        <div
          style={{
            fontFamily: FONTE.display,
            fontSize: tamanho,
            fontWeight: CTA.peso,
            letterSpacing: CTA.tracking,
            lineHeight: CTA.entrelinha,
            color: CTA_COR,
            whiteSpace: "nowrap",
            margin: "6px 0 0 -0.04em",
            transform: `scale(${escala})`,
            transformOrigin: "0% 70%",
          }}
        >
          {textoPalavra}
        </div>
        {rodape ? (
          <div style={{ opacity: opacRodape }}>
            <div style={{ height: CTA.fio.espessura, background: CTA.fio.cor, margin: "20px 0 14px" }} />
            <div
              style={{
                fontFamily: FONTE.texto,
                fontSize: tamanhoRodape,
                fontWeight: CTA.rodape.peso,
                color: CTA.rodape.cor,
                lineHeight: 1.2,
                whiteSpace: "nowrap",
              }}
            >
              {rodape}
            </div>
          </div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};
