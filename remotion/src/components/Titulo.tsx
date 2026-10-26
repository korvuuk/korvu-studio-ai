import React, { useMemo } from "react";
import { interpolate, useCurrentFrame } from "remotion";
import {
  AREA_SEGURA,
  AREA_TEXTO,
  COR,
  EASING,
  FONTE,
  NIVEL1,
  NIVEL2,
  SOMBRA_TEXTO,
  useTempo,
  useFontesProntas,
} from "../brand";
import { larguraTexto, tamanhoQueCabe } from "../lib/medidas";
import { acharPalavra, acharSequencia, separarPalavras } from "../lib/texto";
import { Scribble } from "./Scribble";
import { SelectionHighlight } from "./SelectionHighlight";

export type TituloProps = {
  /** Nível 1 (setup). */
  contexto?: string | null;
  /** Nível 2 (impacto). */
  impacto?: string | null;
  /** Quantas palavras iniciais do impacto ficam cinza. */
  cinza?: number;
  /** Palavra do impacto sublinhada com o rabisco. */
  rabisco?: string | null;
  /** Palavra do impacto em serifa itálica (assinatura da referência de capa). Só na capa. */
  serifa?: string | null;
  /** Palavras do contexto com realce de seleção. `undefined` = últimas 2; `null` = nenhuma. */
  selecao?: string | null;
  corRabisco?: string | null;
  posicao?: "topo" | "centro" | "baixo";
  /** Limites verticais do bloco (padrão: zona segura 270–1250). */
  area?: { topo: number; base: number };
  tamanhoImpacto?: number;
  tamanhoContexto?: number;
  /** Frame local em que a palavra do rabisco é dita (o traço nunca começa antes da palavra aparecer). */
  inicioRabisco?: number | null;
  /** Estado final sem animação (capa / stills). */
  estatico?: boolean;
  sombra?: boolean;
  sementeRabisco?: string;
};

const PONTUACAO_FINAL = /[.,;:!?…"”')\]]+$/;

/** Título do hook: contexto (nível 1 + seleção) + impacto (nível 2) + rabisco. */
export const Titulo: React.FC<TituloProps> = ({
  contexto,
  impacto,
  cinza = 0,
  rabisco,
  serifa,
  selecao,
  corRabisco,
  posicao = "centro",
  area = { topo: AREA_SEGURA.y, base: AREA_SEGURA.limiteY },
  tamanhoImpacto = NIVEL2.tamanho,
  tamanhoContexto = NIVEL1.tamanho,
  inicioRabisco = null,
  estatico = false,
  sombra = true,
  sementeRabisco,
}) => {
  const frame = useCurrentFrame();
  const tempo = useTempo();
  const prontas = useFontesProntas();

  const palavrasCtx = useMemo(() => separarPalavras(contexto ?? ""), [contexto]);
  const palavrasImp = useMemo(() => separarPalavras(impacto ?? ""), [impacto]);

  const faixaSelecao: [number, number] | null =
    selecao === undefined
      ? palavrasCtx.length >= 2
        ? [palavrasCtx.length - 2, palavrasCtx.length]
        : null
      : acharSequencia(palavrasCtx, selecao);
  const idxRabisco = acharPalavra(palavrasImp, rabisco);
  const idxSerifa = acharPalavra(palavrasImp, serifa);

  const tamanho = useMemo(
    () =>
      prontas
        ? tamanhoQueCabe({
            palavras: palavrasImp,
            larguraMax: AREA_TEXTO.larguraMax,
            // frases de impacto longas (>4 palavras) podem usar 3 linhas: com 2 o texto era cortado
            // (o "isso" de "Antes de pedir, conte isso" sumiu no 1.º render real, 2026-09-16)
            maxLinhas: palavrasImp.length > 4 ? NIVEL2.maxLinhas + 1 : NIVEL2.maxLinhas,
            tamanhoMax: tamanhoImpacto,
            tamanhoMin: NIVEL2.tamanhoMin,
            peso: NIVEL2.peso,
            tracking: NIVEL2.tracking,
          })
        : tamanhoImpacto,
    [prontas, palavrasImp, tamanhoImpacto],
  );
  const larguraRabisco =
    prontas && idxRabisco >= 0
      ? larguraTexto(palavrasImp[idxRabisco].replace(PONTUACAO_FINAL, ""), tamanho, NIVEL2)
      : 0;

  // --- linha do tempo (frames locais) ---
  const nC = palavrasCtx.length;
  const inicioSelecao = nC * 2 + 4;
  const inicioImpacto = nC > 0 ? nC * 2 + 8 : 0;
  const aparece = (j: number): number => inicioImpacto + j * tempo.escalonamentoPalavra;
  const minimoRabisco = idxRabisco >= 0 ? aparece(idxRabisco) + tempo.entrada : 0;
  const inicioTraco =
    inicioRabisco !== null
      ? Math.max(inicioRabisco, minimoRabisco)
      : aparece(Math.max(0, palavrasImp.length - 1)) + tempo.entrada + 4;

  const entrada = (f0: number): number =>
    estatico
      ? 1
      : interpolate(frame, [f0, f0 + tempo.entrada], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: EASING.entrada,
        });

  const palavra = (texto: string, f0: number, style?: React.CSSProperties): React.ReactNode => {
    const e = entrada(f0);
    return (
      <span
        style={{
          display: "inline-block",
          opacity: e,
          translate: `0px ${(1 - e) * tempo.subidaPx}px`,
          ...style,
        }}
      >
        {texto}
      </span>
    );
  };

  const juntar = (nos: React.ReactNode[]): React.ReactNode[] =>
    nos.flatMap((n, i) => (i === 0 ? [n] : [" ", n]));

  // --- contexto (nível 1) ---
  const blocoContexto: React.ReactNode[] = [];
  if (nC > 0) {
    const [si, sf] = faixaSelecao ?? [-1, -1];
    const antes = palavrasCtx.slice(0, Math.max(0, si === -1 ? nC : si));
    antes.forEach((w, i) => blocoContexto.push(<React.Fragment key={`a${i}`}>{palavra(w, i * 2)}</React.Fragment>));
    if (si >= 0) {
      const selecionadas = palavrasCtx.slice(si, sf).map((w, k) => (
        <React.Fragment key={`s${k}`}>{palavra(w, (si + k) * 2)}</React.Fragment>
      ));
      blocoContexto.push(
        <SelectionHighlight
          key="selecao"
          inicio={inicioSelecao}
          progresso={estatico ? 1 : undefined}
        >
          {juntar(selecionadas)}
        </SelectionHighlight>,
      );
      palavrasCtx.slice(sf).forEach((w, k) =>
        blocoContexto.push(<React.Fragment key={`d${k}`}>{palavra(w, (sf + k) * 2)}</React.Fragment>),
      );
    }
  }

  const justify =
    posicao === "topo" ? "flex-start" : posicao === "baixo" ? "flex-end" : "center";

  return (
    <div
      style={{
        position: "absolute",
        left: AREA_TEXTO.centroX - AREA_TEXTO.larguraMax / 2,
        width: AREA_TEXTO.larguraMax,
        top: area.topo,
        height: area.base - area.topo,
        display: "flex",
        flexDirection: "column",
        justifyContent: justify,
        alignItems: "center",
        textAlign: "center",
        fontFamily: FONTE.familia,
        textShadow: sombra ? SOMBRA_TEXTO : undefined,
      }}
    >
      {nC > 0 ? (
        <div
          style={{
            fontSize: tamanhoContexto,
            fontWeight: NIVEL1.peso,
            lineHeight: NIVEL1.entrelinha,
            letterSpacing: NIVEL1.tracking,
            color: COR.texto,
            marginBottom: palavrasImp.length > 0 ? NIVEL1.espacoAbaixo : 0,
          }}
        >
          {juntar(blocoContexto)}
        </div>
      ) : null}
      {palavrasImp.length > 0 ? (
        <div
          style={{
            fontSize: tamanho,
            fontWeight: NIVEL2.peso,
            lineHeight: NIVEL2.entrelinha,
            letterSpacing: NIVEL2.tracking,
            // espaço para o rabisco não sair do bloco
            paddingBottom: idxRabisco >= 0 ? tamanho * 0.22 : 0,
          }}
        >
          {juntar(
            palavrasImp.map((w, j) => (
              <span
                key={j}
                style={{
                  display: "inline-block",
                  position: "relative",
                  color: j < cinza ? COR.cinza : COR.texto,
                  // serifa itálica: mesmo corpo do resto (a medição de largura é feita na sans;
                  // aumentar aqui estouraria a linha)
                  ...(j === idxSerifa
                    ? { fontFamily: FONTE.serifa, fontStyle: "italic", fontWeight: 500, letterSpacing: 0 }
                    : null),
                }}
              >
                {palavra(w, aparece(j))}
                {j === idxRabisco && larguraRabisco > 0 ? (
                  <Scribble
                    largura={larguraRabisco * 1.06}
                    altura={Math.max(24, tamanho * 0.28)}
                    espessura={Math.max(7, tamanho * 0.1)}
                    cor={corRabisco === "acento" ? COR.acento : (corRabisco ?? COR.rabisco)}
                    inicio={inicioTraco}
                    progresso={estatico ? 1 : undefined}
                    semente={sementeRabisco ?? `${impacto}-${rabisco}`}
                    style={{
                      position: "absolute",
                      left: -larguraRabisco * 0.03,
                      top: tamanho * 0.8,
                      rotate: "-1.5deg",
                    }}
                  />
                ) : null}
              </span>
            )),
          )}
        </div>
      ) : null}
    </div>
  );
};
