import React from "react";
import { AbsoluteFill } from "remotion";
import { COR, GRADE, VIDEO } from "../brand";

type Props = {
  cor?: string;
  colunas?: number;
  largura?: number;
  style?: React.CSSProperties;
  children?: React.ReactNode;
};

/** Fundo quase preto com linhas verticais finas de grade. */
export const FundoGrade: React.FC<Props> = ({
  cor = COR.fundo,
  colunas = GRADE.colunas,
  largura = VIDEO.largura,
  style,
  children,
}) => {
  return (
    <AbsoluteFill style={{ backgroundColor: cor, ...style }}>
      {Array.from({ length: colunas - 1 }, (_, i) => (
        <div
          key={i}
          style={{
            position: "absolute",
            top: 0,
            bottom: 0,
            left: Math.round(((i + 1) * largura) / colunas),
            width: GRADE.espessura,
            backgroundColor: COR.linhaGrade,
          }}
        />
      ))}
      {children}
    </AbsoluteFill>
  );
};
