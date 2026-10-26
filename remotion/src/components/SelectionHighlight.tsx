import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { COR, EASING, useTempo } from "../brand";

type Props = {
  children: React.ReactNode;
  /** Frame (local) em que o "arraste" começa. */
  inicio?: number;
  duracao?: number;
  /** Força o progresso (0–1), ex.: capa estática. */
  progresso?: number;
  cor?: string;
  corAlca?: string;
  padX?: number;
  padY?: number;
};

const LINHA_ALCA = 2;
const BOLINHA = 8;

/**
 * Realce de "texto selecionado": caixa escura que cresce da esquerda para a
 * direita como um cursor arrastando, com alças (linha 2 px + bolinha 8 px)
 * no início (bolinha em cima) e no fim (bolinha em baixo).
 */
export const SelectionHighlight: React.FC<Props> = ({
  children,
  inicio = 0,
  duracao: duracaoProp,
  progresso,
  cor = COR.selecao,
  corAlca = COR.alca,
  padX = 8,
  padY = 3,
}) => {
  const frame = useCurrentFrame();
  const tempo = useTempo();
  const duracao = duracaoProp ?? tempo.selecao;
  const p =
    progresso ??
    interpolate(frame, [inicio, inicio + duracao], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: EASING.selecao,
    });
  const opacidadeAlcas =
    progresso !== undefined
      ? p > 0
        ? 1
        : 0
      : interpolate(frame, [inicio - 2, inicio + 1], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
  const larguraTotal = `(100% + ${2 * padX}px)`;

  const alca = (lado: "inicio" | "fim"): React.ReactNode => (
    <span
      aria-hidden
      style={{
        position: "absolute",
        top: -padY - 1,
        bottom: -padY - 1,
        left:
          lado === "inicio"
            ? -padX - LINHA_ALCA / 2
            : `calc(${p} * ${larguraTotal} - ${padX + LINHA_ALCA / 2}px)`,
        width: LINHA_ALCA,
        backgroundColor: corAlca,
        opacity: opacidadeAlcas,
      }}
    >
      <span
        style={{
          position: "absolute",
          left: LINHA_ALCA / 2 - BOLINHA / 2,
          width: BOLINHA,
          height: BOLINHA,
          borderRadius: BOLINHA / 2,
          backgroundColor: corAlca,
          ...(lado === "inicio" ? { top: -BOLINHA + 1 } : { bottom: -BOLINHA + 1 }),
        }}
      />
    </span>
  );

  return (
    <span
      style={{ position: "relative", display: "inline-block", whiteSpace: "nowrap" }}
    >
      <span
        aria-hidden
        style={{
          position: "absolute",
          left: -padX,
          top: -padY,
          bottom: -padY,
          width: `calc(${p} * ${larguraTotal})`,
          backgroundColor: cor,
          borderRadius: 3,
        }}
      />
      {alca("inicio")}
      {alca("fim")}
      <span style={{ position: "relative" }}>{children}</span>
    </span>
  );
};
