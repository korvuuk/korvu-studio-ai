import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { AREA_SEGURA, CAPA, COR, VIDEO } from "../brand";
import { FundoGrade } from "../components/FundoGrade";
import { Titulo } from "../components/Titulo";

export type CapaProps = {
  /** Frame de fundo, relativo a `remotion/public`. `null` = fundo com grade. */
  frame: string | null;
  contexto?: string | null;
  impacto: string;
  cinza: number;
  rabisco?: string | null;
  /** Palavra do impacto em serifa itálica (assinatura da referência editorial). */
  serifa?: string | null;
  selecao?: string | null;
  /** Onde o texto fica dentro do recorte 3:4. */
  posicao: "topo" | "base";
  corRabisco?: string | null;
  /** Escurecimento geral do frame (0–1). */
  escurecer?: number;
  /** Tamanho do título (px). Padrão CAPA.tamanhoImpacto. Menor = o bloco sobe menos sobre o rosto. */
  tamanhoTitulo?: number | null;
  /**
   * Desloca a foto na vertical (px; negativo = sobe). 2026-10-08: em close (mão no queixo) o título preso à zona
   * segura (y≈1250) caía no queixo; subir a foto tira o queixo de trás do texto sem mexer na zona segura.
   */
  deslocarFrameY?: number;
};

const ZONA = {
  topo: CAPA.recorte.y + CAPA.margem,
  // O bloco termina na zona segura do Instagram (y≈1250): mais abaixo, o @ e a legenda do Reel entram por cima
  // do texto (visto nas 1.as capas reais, 2026-09-16).
  base: Math.min(CAPA.recorte.y + CAPA.recorte.altura - CAPA.margem, AREA_SEGURA.limiteY),
};

/** Conteúdo da capa em 1080×1920 (reutilizado pela prévia da grade). */
const CapaConteudo: React.FC<CapaProps> = ({
  frame,
  contexto,
  impacto,
  cinza,
  rabisco,
  serifa = null,
  selecao = null,
  posicao,
  corRabisco,
  escurecer = 0.12,
  tamanhoTitulo = null,
  deslocarFrameY = 0,
}) => {
  const veu =
    posicao === "topo"
      ? "linear-gradient(180deg, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0.55) 28%, rgba(0,0,0,0) 58%)"
      : "linear-gradient(0deg, rgba(0,0,0,0.82) 0%, rgba(0,0,0,0.55) 30%, rgba(0,0,0,0) 60%)";
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        top: 0,
        width: VIDEO.largura,
        height: VIDEO.altura,
        overflow: "hidden",
        backgroundColor: COR.fundo,
      }}
    >
      {frame ? (
        <Img
          src={staticFile(frame)}
          style={{
            position: "absolute",
            left: 0,
            top: deslocarFrameY,
            width: "100%",
            height: VIDEO.altura - Math.min(0, deslocarFrameY),
            objectFit: "cover",
            objectPosition: "50% 0%",
          }}
        />
      ) : (
        <FundoGrade />
      )}
      <AbsoluteFill style={{ backgroundColor: `rgba(0,0,0,${escurecer})` }} />
      <AbsoluteFill style={{ background: veu }} />
      <Titulo
        estatico
        contexto={contexto}
        impacto={impacto}
        cinza={cinza}
        rabisco={rabisco}
        serifa={serifa}
        selecao={selecao}
        corRabisco={corRabisco}
        posicao={posicao === "topo" ? "topo" : "baixo"}
        area={ZONA}
        tamanhoImpacto={tamanhoTitulo ?? CAPA.tamanhoImpacto}
        sementeRabisco={`capa-${impacto}`}
      />
    </div>
  );
};

/** Capa 1080×1920 (texto dentro do recorte central 1080×1440). */
export const Capa: React.FC<CapaProps> = (props) => <CapaConteudo {...props} />;

/** Prévia do recorte 3:4 que aparece na grade do perfil (1080×1440). */
export const CapaGrade: React.FC<CapaProps> = (props) => (
  <AbsoluteFill style={{ overflow: "hidden", backgroundColor: COR.fundo }}>
    <div style={{ position: "absolute", left: 0, top: -CAPA.recorte.y, width: VIDEO.largura, height: VIDEO.altura }}>
      <CapaConteudo {...props} />
    </div>
  </AbsoluteFill>
);
