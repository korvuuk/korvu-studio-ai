import { fitText } from "@remotion/layout-utils";
import React, { useMemo } from "react";
import {
  AbsoluteFill,
  interpolate,
  interpolateColors,
  Sequence,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { AREA_TEXTO, EASING, FONTE, LEGENDA, useFontesProntas, useTempo } from "../brand";
import { montarPaginas, type PaginaLegenda, type TokenLegenda } from "../lib/paginas";
import type { LegendaCaption } from "../lib/tipos";
import { msParaFrame } from "../lib/texto";

type Props = {
  legendas: LegendaCaption[];
  /** Centro vertical do bloco (px). Padrão y≈1170 (acima da UI). */
  centroY?: number;
  combinarMs?: number;
};

/** Legendas estilo "seleção": entram no ritmo da fala, karaokê cinza→branco. */
export const Legendas: React.FC<Props> = ({
  legendas,
  centroY = LEGENDA.centroYBaixo,
  combinarMs = LEGENDA.combinarMs,
}) => {
  const { fps } = useVideoConfig();
  const prontas = useFontesProntas();
  const paginas = useMemo(
    () => montarPaginas(legendas, combinarMs, LEGENDA.maxPalavras),
    [legendas, combinarMs],
  );

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {paginas.map((pg, i) => {
        const prox = paginas[i + 1];
        const from = msParaFrame(pg.inicioMs, fps);
        const fimMs = Math.min(prox ? prox.inicioMs : Infinity, pg.fimMs + LEGENDA.seguraMs);
        const duracao = msParaFrame(fimMs, fps) - from;
        if (duracao <= 0) return null;
        return (
          <Sequence
            key={`${pg.inicioMs}-${i}`}
            name={`Legenda: ${pg.texto}`}
            from={from}
            durationInFrames={duracao}
            premountFor={fps}
          >
            <Pagina pagina={pg} duracao={duracao} centroY={centroY} prontas={prontas} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};

type Linha = { destaque: boolean; tokens: Array<TokenLegenda & { indice: number }> };

const agruparLinhas = (tokens: TokenLegenda[]): Linha[] => {
  const linhas: Linha[] = [];
  tokens.forEach((t, indice) => {
    const ultima = linhas[linhas.length - 1];
    if (ultima && ultima.destaque === t.destaque) {
      ultima.tokens.push({ ...t, indice });
    } else {
      linhas.push({ destaque: t.destaque, tokens: [{ ...t, indice }] });
    }
  });
  return linhas;
};

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

const Pagina: React.FC<{
  pagina: PaginaLegenda;
  duracao: number;
  centroY: number;
  prontas: boolean;
}> = ({ pagina, duracao, centroY, prontas }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const tempo = useTempo();
  const linhas = agruparLinhas(pagina.tokens);
  const paraFrame = (ms: number): number => ((ms - pagina.inicioMs) / 1000) * fps;

  return (
    <div
      style={{
        position: "absolute",
        left: AREA_TEXTO.centroX - AREA_TEXTO.larguraMax / 2,
        width: AREA_TEXTO.larguraMax,
        top: centroY,
        translate: "0px -50%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 6,
        fontFamily: FONTE.familia,
        textShadow: LEGENDA.sombra,
        textAlign: "center",
        opacity: interpolate(frame, [duracao - tempo.saida, duracao], [1, 0], clamp),
      }}
    >
      {linhas.map((linha, li) => {
        const textoLinha = linha.tokens.map((t) => t.texto).join(" ");
        const tamanho = linha.destaque
          ? prontas
            ? Math.min(
                LEGENDA.tamanhoDestaque,
                fitText({
                  text: textoLinha,
                  withinWidth: AREA_TEXTO.larguraMax,
                  fontFamily: FONTE.familia,
                  fontWeight: LEGENDA.pesoDestaque,
                  letterSpacing: "-0.02em",
                }).fontSize,
              )
            : LEGENDA.tamanhoDestaque
          : LEGENDA.tamanho;
        return (
          <div
            key={li}
            style={{
              display: "flex",
              flexWrap: "wrap",
              justifyContent: "center",
              columnGap: "0.26em",
              fontSize: tamanho,
              fontWeight: linha.destaque ? LEGENDA.pesoDestaque : LEGENDA.peso,
              lineHeight: linha.destaque ? 0.98 : LEGENDA.entrelinha,
              letterSpacing: linha.destaque ? "-0.02em" : LEGENDA.tracking,
            }}
          >
            {linha.tokens.map((t) => {
              const f0 = paraFrame(t.inicioMs);
              const proximo = pagina.tokens[t.indice + 1];
              // a palavra fica "acesa" até a próxima começar (ou até o fim da página)
              const fAtivoFim = proximo ? paraFrame(proximo.inicioMs) : duracao + 1;
              const entrada = interpolate(frame, [f0, f0 + tempo.entrada], [0, 1], {
                ...clamp,
                easing: EASING.entrada,
              });
              const acende = interpolate(frame, [f0, f0 + tempo.karaoke], [0, 1], clamp);
              const apaga = t.destaque
                ? 0
                : interpolate(frame, [fAtivoFim, fAtivoFim + tempo.karaoke], [0, 1], clamp);
              return (
                <span
                  key={t.indice}
                  style={{
                    display: "inline-block",
                    opacity: entrada,
                    translate: `0px ${(1 - entrada) * tempo.subidaPx}px`,
                    color: interpolateColors(acende * (1 - apaga), [0, 1], [
                      LEGENDA.corInativa,
                      LEGENDA.corAtiva,
                    ]),
                  }}
                >
                  {t.texto}
                </span>
              );
            })}
          </div>
        );
      })}
    </div>
  );
};
