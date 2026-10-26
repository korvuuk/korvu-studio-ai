import { Video } from "@remotion/media";
import React, { useMemo } from "react";
import {
  AbsoluteFill,
  type CalculateMetadataFunction,
  Freeze,
  Img,
  interpolate,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { acharAnimacao } from "../animacoes/registry";
import {
  AREA_SEGURA,
  CARD,
  COR,
  FONTE,
  LAYOUTS,
  LEGENDA,
  ROTULO,
  SOMBRA_TEXTO,
  SPLIT,
  TELA_CHEIA,
  TEMPO,
  useTempo,
  VIDEO,
  ZOOM,
} from "../brand";
import { Cartela } from "../components/Cartela";
import { CtaPalavra } from "../components/CtaPalavra";
import { FundoGrade } from "../components/FundoGrade";
import { Legendas } from "../components/Legendas";
import { Titulo } from "../components/Titulo";
import { normalizar, segParaFrame } from "../lib/texto";
import type {
  LegendaCaption,
  Overlay,
  OverlayAnimacao,
  OverlayExtra,
  OverlayTela,
  OverlayTexto,
  PalavraAnimacao,
  ReelProps,
  TituloConfig,
} from "../lib/tipos";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// ---------------------------------------------------------------------------
// calculateMetadata: fps de `props.fps` (reel-props.json, = edl.json.fps / FPS_PROJETO; padrão VIDEO.fps)
// e duração a partir de `duracaoSeg`; `arquivoProps` opcional (caminho relativo a public/,
// ex.: "_render/<slug>/reel-props.json"). Com a CLI use `--props=/caminho/reel-props.json`.
// ---------------------------------------------------------------------------
export const calcularMetadataReel: CalculateMetadataFunction<ReelProps> = async ({
  props,
  abortSignal,
}) => {
  let p: ReelProps = props;
  if (props.arquivoProps) {
    const resp = await fetch(staticFile(props.arquivoProps), { signal: abortSignal });
    if (!resp.ok) {
      throw new Error(`Não consegui ler ${props.arquivoProps} (HTTP ${resp.status})`);
    }
    const json = (await resp.json()) as Partial<ReelProps>;
    p = { ...props, ...json, arquivoProps: props.arquivoProps };
  }
  const fps = typeof p.fps === "number" && p.fps > 0 ? p.fps : VIDEO.fps;
  const normalizado: ReelProps = {
    ...p,
    fps,
    legendas: p.legendas ?? [],
    overlays: p.overlays ?? [],
    segmentos: p.segmentos ?? [],
    titulo: p.titulo ?? null,
    cta: p.cta ?? null,
  };
  return {
    fps,
    // -0.001: duracaoSeg já está na grade de frames (evita 1 frame a mais por arredondamento)
    durationInFrames: Math.max(1, Math.ceil(normalizado.duracaoSeg * fps - 0.001)),
    props: normalizado,
  };
};

/** Janela do título do hook (s). */
const janelaDoTitulo = (
  titulo: TituloConfig,
  legendas: LegendaCaption[],
): { inicio: number; fim: number } => {
  const inicio = titulo.inicio ?? 0;
  if (titulo.fim != null) return { inicio, fim: titulo.fim };
  const primeira = legendas[0]?.linha;
  const daLinha = primeira ? legendas.filter((c) => c.linha === primeira) : [];
  if (daLinha.length > 0) {
    const fim = daLinha[daLinha.length - 1].endMs / 1000 + 0.4;
    return { inicio, fim: Math.min(4.5, Math.max(2.5, fim)) };
  }
  return { inicio, fim: inicio + TEMPO.tituloPadraoSeg };
};

const chaveOverlay = (o: Overlay): string => (o.tipo === "extra" ? o.extra : o.linha);

const ehSplit = (o: Overlay): boolean =>
  (o.tipo === "tela" || o.tipo === "animacao" || o.tipo === "extra") && o.modo === "split";

/** Extra `full` com `enquadrar`: preenche a tela e entra/sai em corte seco. */
const ehEnquadrado = (o: Overlay): boolean =>
  o.tipo === "extra" &&
  !o.faltando &&
  ((o.modo === "full" && Boolean(o.enquadrar) && Boolean(o.src)) ||
    (o.modo === "solo" && Boolean(o.src)) ||
    (o.modo === "pilha" && (o.pilha?.length ?? 0) > 0));

/** Curva suave (smoothstep): usada nas entradas e saídas do split. */
const suave = (x: number): number => (x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x));

/**
 * Faixas CONTÍNUAS de split: overlays encostados (ou com um buraco menor que a transição) viram UMA faixa.
 *
 * 2026-09-19 (Carlos): "o meu vídeo sobe e desce num milésimo de segundo". A conta antiga descia até zero no
 * fim de CADA overlay, então entre dois extras encostados o Carlos saltava para tela cheia por um frame e
 * voltava. Agora só se desce quando a metade de cima fica mesmo vazia.
 */
const faixasDeSplit = (overlays: Overlay[], dur: number): Array<[number, number]> => {
  const iv = overlays
    .filter(ehSplit)
    .map((o) => [o.saida_inicio, o.saida_fim] as [number, number])
    .sort((a, b) => a[0] - b[0]);
  const out: Array<[number, number]> = [];
  for (const [a, b] of iv) {
    const ult = out[out.length - 1];
    if (ult && a - ult[1] <= dur) ult[1] = Math.max(ult[1], b);
    else out.push([a, b]);
  }
  return out;
};

/** 0 = Carlos em tela cheia · 1 = split montado. Sobe e desce só nas bordas de cada FAIXA contínua. */
const progressoDoSplit = (overlays: Overlay[], t: number, dur: number): number => {
  let p = 0;
  // faixa encostada num extra que cobre a tela (full enquadrado / solo / pilha): sem rampa desse lado — o Carlos
  // não volta à tela cheia por 0,2 s antes do corte seco (QA Fei-Fei v3, 17/10)
  const cobertos = overlays.filter(ehEnquadrado);
  for (const [a, b] of faixasDeSplit(overlays, dur)) {
    if (t < a - dur || t > b) continue;
    const secoIn = cobertos.some((o) => Math.abs(o.saida_fim - a) < 0.05);
    const secoOut = cobertos.some((o) => Math.abs(o.saida_inicio - b) < 0.05);
    const pIn = secoIn ? (t >= a ? 1 : 0) : suave((t - a) / dur);
    const pOut = secoOut ? 1 : suave((b - t) / dur);
    p = Math.max(p, Math.min(pIn, pOut, 1));
  }
  return p;
};

// ---------------------------------------------------------------------------
// Composição principal
// ---------------------------------------------------------------------------
export const Reel: React.FC<ReelProps> = ({
  video,
  legendas,
  overlays,
  segmentos,
  titulo,
  cta = null,
  legendaPosicao = "baixo",
  zoomNoCorte = false,
  mostrarFaltando = true,
  mostrarLegendas = true,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  const janela = useMemo(
    () => (titulo ? janelaDoTitulo(titulo, legendas) : null),
    [titulo, legendas],
  );

  // Com título no hook, o texto do hook já está no título.
  const overlaysVisiveis = useMemo(
    () =>
      overlays.filter(
        (o) =>
          !(o.tipo === "texto" && janela && o.saida_inicio < janela.fim && o.saida_fim > janela.inicio) &&
          // render final: extra que falta simplesmente não entra (nada de etiqueta por cima do vídeo)
          !(!mostrarFaltando && o.tipo === "extra" && o.faltando),
      ),
    [overlays, janela, mostrarFaltando],
  );

  // Legendas somem durante o título do hook e durante cartelas de texto em
  // tela cheia (o texto já está na tela). `legendas: true` no overlay força.
  const legendasVisiveis = useMemo(() => {
    const ocultar: Array<[number, number]> = [];
    if (titulo && janela && titulo.ocultarLegendas !== false) {
      ocultar.push([janela.inicio, janela.fim]);
    }
    // CTA em cartão: a palavra já está ENORME na tela — as legendas dessas palavras somem (sem duplicar).
    if (cta && cta.fim > cta.inicio) ocultar.push([cta.inicio, cta.fim]);
    for (const o of overlaysVisiveis) {
      if (o.tipo === "texto" && o.modo === "cartela" && o.legendas !== true) {
        ocultar.push([o.saida_inicio, o.saida_fim]);
      }
      // Cartão de tela de computador no peito (21/10): ocupa a faixa da legenda (y 920–1250) e já mostra o comando
      // digitado — a legenda some enquanto ele está na tela.
      if (o.tipo === "extra" && o.modo === "card") {
        ocultar.push([o.saida_inicio, o.saida_fim]);
      }
    }
    if (ocultar.length === 0) return legendas;
    // Só some a palavra que cabe inteira na janela (palavra que "vaza" do fim continua).
    return legendas.filter(
      (c) => !ocultar.some(([a, b]) => c.startMs >= a * 1000 && c.endMs <= b * 1000),
    );
  }, [legendas, titulo, janela, overlaysVisiveis, cta]);

  const segmento = segmentos.find((s) => t >= s.saidaInicio && t < s.saidaFim) ?? null;
  // Zoom aplicado UMA vez: com zoomNoCorte o punch-in já está no vídeo (render_corte) — aqui não entra de novo.
  const punch = !zoomNoCorte && segmento?.zoom?.tipo === "punch" ? segmento.zoom : null;
  const zoom = punch ? punch.escala : 1;
  const origemZoom = punch?.origem ?? ZOOM.origem;
  const transicaoSeg = LAYOUTS.split.transicaoFrames / fps;
  const progressoSplit = progressoDoSplit(overlaysVisiveis, t, transicaoSeg);

  // No split o Carlos fica no painel de BAIXO e a legenda em y≈1150 caía em cima do rosto: ela sobe para
  // logo abaixo da divisória, acompanhando o mesmo deslize da câmera.
  const centroPadrao = legendaPosicao === "centro" ? LEGENDA.centroYCentro : LEGENDA.centroYBaixo;
  const centroLegenda = centroPadrao + (LAYOUTS.split.centroLegenda - centroPadrao) * progressoSplit;

  return (
    <AbsoluteFill style={{ backgroundColor: COR.fundo }}>
      <Camera video={video} zoom={zoom} origem={origemZoom} progresso={progressoSplit} />

      {overlaysVisiveis.map((o, i) => {
        const from = segParaFrame(o.saida_inicio, fps);
        const duracao = Math.max(1, segParaFrame(o.saida_fim, fps) - from);
        // encosta no vizinho? então nada de fade desse lado — corte seco, sem sobreposição
        const col = overlaysVisiveis.filter((x) => ehSplit(x) || ehEnquadrado(x));
        const ant = col.filter((x) => x !== o && x.saida_fim <= o.saida_inicio + 1e-6).pop();
        const prox = col.find((x) => x !== o && x.saida_inicio >= o.saida_fim - 1e-6);
        // extra enquadrado em tela cheia (faixa contínua, Hinton v2): corte seco sempre — nada de "entra e sai";
        // split encostado num extra de tela cheia também entra/sai seco desse lado (QA Fei-Fei v3, 17/10)
        const seco = ehEnquadrado(o);
        const entra = !seco && !(ehSplit(o) && ant && o.saida_inicio - ant.saida_fim <= transicaoSeg);
        const sai = !seco && !(ehSplit(o) && prox && prox.saida_inicio - o.saida_fim <= transicaoSeg);
        return (
          <Sequence
            key={`${chaveOverlay(o)}-${o.tipo}-${i}`}
            name={`${o.tipo} ${chaveOverlay(o)}`}
            from={from}
            durationInFrames={duracao}
            premountFor={fps}
          >
            <Transicao duracao={duracao} entra={entra} sai={sai}>
              <OverlayView
                overlay={o}
                legendas={legendas}
                duracaoFrames={duracao}
                mostrarFaltando={mostrarFaltando}
                veu={mostrarLegendas}
              />
            </Transicao>
          </Sequence>
        );
      })}

      {titulo && janela ? (
        <Sequence
          name="Título do hook"
          from={segParaFrame(janela.inicio, fps)}
          durationInFrames={Math.max(1, segParaFrame(janela.fim - janela.inicio, fps))}
          premountFor={fps}
        >
          <TituloHook
            titulo={titulo}
            legendas={legendas}
            inicioSeg={janela.inicio}
            duracao={Math.max(1, segParaFrame(janela.fim - janela.inicio, fps))}
          />
        </Sequence>
      ) : null}

      {mostrarLegendas ? <Legendas legendas={legendasVisiveis} centroY={centroLegenda} /> : null}

      {cta && cta.fim > cta.inicio ? (
        <Sequence
          name={`CTA ${cta.palavra}`}
          from={segParaFrame(cta.inicio, fps)}
          durationInFrames={Math.max(1, segParaFrame(cta.fim, fps) - segParaFrame(cta.inicio, fps))}
          premountFor={fps}
        >
          <CtaPalavra
            palavra={cta.palavra}
            topo={cta.topo ?? "comenta"}
            rodape={cta.rodape === undefined ? null : cta.rodape}
            duracao={Math.max(1, segParaFrame(cta.fim, fps) - segParaFrame(cta.inicio, fps))}
          />
        </Sequence>
      ) : null}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// Câmera (sempre montada; no split desliza para o painel de BAIXO, recortada no rosto)
// ---------------------------------------------------------------------------
const Camera: React.FC<{ video: string | null; zoom: number; origem: string; progresso: number }> = ({
  video,
  zoom,
  origem,
  progresso,
}) => {
  // progresso 0 → tela cheia · 1 → painel de baixo. Tudo interpolado: a troca é um deslize, não um corte.
  const topo = SPLIT.topoCamera * progresso;
  const altura = VIDEO.altura - topo;
  const alvoY = Math.min(0, Math.max(altura - VIDEO.altura, altura / 2 - SPLIT.focoY * VIDEO.altura));
  const deslocY = alvoY * progresso;
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        top: topo,
        width: VIDEO.largura,
        height: altura,
        overflow: "hidden",
      }}
    >
      <div
        style={{
          position: "absolute",
          left: 0,
          top: deslocY,
          width: VIDEO.largura,
          height: VIDEO.altura,
          scale: zoom,
          transformOrigin: origem,
        }}
      >
        {video ? (
          <Video
            src={staticFile(video)}
            objectFit="cover"
            style={{ width: "100%", height: "100%" }}
          />
        ) : (
          <FundoDemo />
        )}
      </div>
    </div>
  );
};

/** Substitui a câmera quando `video` é null (demo sem mídia). */
const FundoDemo: React.FC = () => (
  <AbsoluteFill
    style={{
      background: `radial-gradient(120% 70% at 50% 38%, #545A63 0%, ${COR.demoFundo} 45%, #23262B 100%)`,
    }}
  >
    <div
      style={{
        position: "absolute",
        top: 190,
        left: 0,
        right: 0,
        textAlign: "center",
        fontFamily: FONTE.familia,
        fontSize: ROTULO.tamanho,
        fontWeight: ROTULO.peso,
        letterSpacing: ROTULO.tracking,
        color: "rgba(242,242,242,0.35)",
      }}
    >
      DEMO · SEM VÍDEO
    </div>
  </AbsoluteFill>
);

/**
 * Fade de entrada/saída do overlay. `fundir` desliga o fade do lado que ENCOSTA noutro overlay:
 * dois extras seguidos faziam fade-out e fade-in ao mesmo tempo e apareciam SOBREPOSTOS
 * (o Carlos viu a imagem dele fantasma por cima do documentário, 2026-09-19). Encostados = corte seco.
 */
const Transicao: React.FC<{
  duracao: number;
  entra?: boolean;
  sai?: boolean;
  children: React.ReactNode;
}> = ({ duracao, entra = true, sai = true, children }) => {
  const frame = useCurrentFrame();
  const tempo = useTempo();
  const f = Math.min(tempo.saida, Math.floor(duracao / 3));
  // Calculado à mão, sem `interpolate`: desligar um dos lados deixava dois pontos iguais no inputRange
  // ("must be strictly monotonically increasing") e o render MORRIA — sem isto o Remotion falha inteiro.
  let opacidade = 1;
  if (f >= 1) {
    if (entra && frame < f) opacidade = frame / f;
    else if (sai && frame > duracao - f) opacidade = Math.max(0, (duracao - frame) / f);
  }
  return <AbsoluteFill style={{ opacity: opacidade }}>{children}</AbsoluteFill>;
};

// ---------------------------------------------------------------------------
// Overlays
// ---------------------------------------------------------------------------
const OverlayView: React.FC<{
  overlay: Overlay;
  legendas: LegendaCaption[];
  duracaoFrames: number;
  mostrarFaltando: boolean;
  /** 21/10: o véu escuro de baixo existe só para a legenda ler sobre imagem clara — sem legenda, sem véu (o Carlos viu
   *  uma "sombra preta" no pé das imagens no livro-chatgpt). */
  veu?: boolean;
}> = ({ overlay, legendas, duracaoFrames, mostrarFaltando, veu = true }) => {
  switch (overlay.tipo) {
    case "texto":
      return <TextoOverlay overlay={overlay} />;
    case "tela":
      return <TelaOverlay overlay={overlay} />;
    case "animacao":
      return (
        <AnimacaoOverlay
          overlay={overlay}
          legendas={legendas}
          duracaoFrames={duracaoFrames}
          mostrarFaltando={mostrarFaltando}
        />
      );
    case "extra":
      return (
        <ExtraOverlay
          overlay={overlay}
          legendas={legendas}
          duracaoFrames={duracaoFrames}
          mostrarFaltando={mostrarFaltando}
          veu={veu}
        />
      );
    default:
      return null;
  }
};

const TextoOverlay: React.FC<{ overlay: OverlayTexto }> = ({ overlay }) => {
  if (overlay.modo === "cartela") {
    return (
      <Cartela
        nivel1={overlay.contexto}
        nivel2={overlay.texto}
        cinza={overlay.cinza ?? 0}
        selecao={overlay.selecao ?? null}
        rabisco={overlay.rabisco}
      />
    );
  }
  // Texto sobre o vídeo, no topo da zona segura, com véu escuro para leitura.
  return (
    <AbsoluteFill>
      <AbsoluteFill
        style={{
          background: "linear-gradient(180deg, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0) 45%)",
        }}
      />
      <Titulo
        contexto={overlay.contexto}
        impacto={overlay.texto}
        cinza={overlay.cinza ?? 0}
        selecao={overlay.selecao ?? null}
        rabisco={overlay.rabisco}
        posicao="topo"
        tamanhoImpacto={112}
      />
    </AbsoluteFill>
  );
};

/** Fundo do painel do extra — EM CIMA (o Carlos fica embaixo). */
const PainelExtra: React.FC = () => (
  <div
    style={{
      position: "absolute",
      left: 0,
      right: 0,
      top: 0,
      height: SPLIT.topoCamera,
      borderBottom: `1px solid ${COR.borda}`,
    }}
  >
    <FundoGrade />
  </div>
);

/** Legado: gravação de tela vinda de EDL antiga (`tipo: "tela"`). */
const TelaOverlay: React.FC<{ overlay: OverlayTela }> = ({ overlay }) => {
  const { fps } = useVideoConfig();
  const caixa = overlay.modo === "split" ? SPLIT.caixaSuperior : TELA_CHEIA.caixa;
  const fw = overlay.fonteLargura ?? VIDEO.largura;
  const fh = overlay.fonteAltura ?? VIDEO.altura;
  const rec = overlay.recorte ?? { x: 0, y: 0, largura: fw, altura: fh };
  const s = Math.min(caixa.largura / rec.largura, caixa.altura / rec.altura);
  const w = rec.largura * s;
  const h = rec.altura * s;
  return (
    <AbsoluteFill>
      {overlay.modo === "split" ? <PainelExtra /> : <FundoGrade />}
      <div
        style={{
          position: "absolute",
          left: caixa.x + (caixa.largura - w) / 2,
          top: caixa.y + (caixa.altura - h) / 2,
          width: w,
          height: h,
          overflow: "hidden",
          borderRadius: 18,
          outline: `1px solid ${COR.borda}`,
        }}
      >
        <div
          style={{
            position: "absolute",
            left: -rec.x * s,
            top: -rec.y * s,
            width: fw * s,
            height: fh * s,
          }}
        >
          <Video
            src={staticFile(overlay.src)}
            trimBefore={Math.round(overlay.in * fps)}
            muted
            objectFit="fill"
            style={{ width: "100%", height: "100%" }}
          />
        </div>
      </div>
    </AbsoluteFill>
  );
};

const palavrasDoOverlay = (
  legendas: LegendaCaption[],
  inicio: number,
  fim: number,
): PalavraAnimacao[] =>
  legendas
    .filter((c) => c.startMs >= inicio * 1000 && c.startMs < fim * 1000)
    .map((c) => ({
      texto: c.text.trim(),
      inicioMs: c.startMs - inicio * 1000,
      fimMs: c.endMs - inicio * 1000,
      destaque: Boolean(c.destaque),
    }));

const AnimacaoOverlay: React.FC<{
  overlay: OverlayAnimacao;
  legendas: LegendaCaption[];
  duracaoFrames: number;
  mostrarFaltando?: boolean;
}> = ({ overlay, legendas, duracaoFrames, mostrarFaltando = true }) => {
  const frame = useCurrentFrame();
  const Componente = acharAnimacao(overlay.componente, overlay.id);
  const palavras = useMemo(
    () => palavrasDoOverlay(legendas, overlay.saida_inicio, overlay.saida_fim),
    [legendas, overlay.saida_inicio, overlay.saida_fim],
  );

  // render final: animação que ainda não existe simplesmente não entra (sem cartaz "pendente")
  if (!Componente && !mostrarFaltando) return null;

  if (!Componente && overlay.modo === "full") {
    return (
      <Cartela
        rotulo={`Animação ${overlay.id} · pendente`}
        nivel1={overlay.descricao ?? "(sem descrição)"}
        selecao={null}
      />
    );
  }

  const conteudo = (largura: number, altura: number): React.ReactNode =>
    Componente ? (
      <Componente
        {...(overlay.props ?? {})}
        palavras={palavras}
        largura={largura}
        altura={altura}
        modo={overlay.modo}
        descricao={overlay.descricao}
        duracaoFrames={duracaoFrames}
      />
    ) : (
      <Pendente id={overlay.id} descricao={overlay.descricao} />
    );

  if (overlay.modo === "full") {
    return (
      <FundoGrade>
        <div
          style={{
            position: "absolute",
            left: 0,
            top: AREA_SEGURA.y,
            width: VIDEO.largura,
            height: AREA_SEGURA.altura,
          }}
        >
          {conteudo(VIDEO.largura, AREA_SEGURA.altura)}
        </div>
      </FundoGrade>
    );
  }

  if (overlay.modo === "split") {
    const c = SPLIT.caixaSuperior;
    return (
      <AbsoluteFill>
        <PainelExtra />
        <div
          style={{ position: "absolute", left: c.x, top: c.y, width: c.largura, height: c.altura }}
        >
          {conteudo(c.largura, c.altura)}
        </div>
      </AbsoluteFill>
    );
  }

  // card
  const entrada = interpolate(frame, [0, LAYOUTS.card.entradaFrames], [0.96, 1], clamp);
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ backgroundColor: `rgba(0,0,0,${CARD.escurecerVideo})` }} />
      <div
        style={{
          position: "absolute",
          left: (VIDEO.largura - CARD.largura) / 2,
          top: CARD.centroY - CARD.altura / 2,
          width: CARD.largura,
          height: CARD.altura,
          borderRadius: CARD.raio,
          overflow: "hidden",
          outline: `1px solid ${COR.borda}`,
          scale: entrada,
        }}
      >
        <FundoGrade largura={CARD.largura} />
        {conteudo(CARD.largura, CARD.altura)}
      </div>
    </AbsoluteFill>
  );
};

/** Placeholder de animação ainda não criada (split / card). */
const Pendente: React.FC<{ id: string; descricao?: string | null }> = ({ id, descricao }) => (
  <div
    style={{
      position: "absolute",
      inset: 0,
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      gap: 24,
      padding: "0 60px",
      textAlign: "center",
      fontFamily: FONTE.familia,
    }}
  >
    <div
      style={{
        fontSize: ROTULO.tamanho,
        fontWeight: ROTULO.peso,
        letterSpacing: ROTULO.tracking,
        color: COR.cinza,
        textTransform: "uppercase",
      }}
    >
      Animação {id} · pendente
    </div>
    <div style={{ fontSize: 46, fontWeight: 500, lineHeight: 1.2, color: COR.texto }}>
      {descricao ?? "(sem descrição)"}
    </div>
  </div>
);

// ---------------------------------------------------------------------------
// Cenas extras (B-roll): split | full | card — medidas em LAYOUTS (brand.ts)
// ---------------------------------------------------------------------------
type Ajuste = "contain" | "cover" | "fill";

const ehImagem = (src: string): boolean => /\.(png|jpe?g|webp|gif)$/i.test(src);

const ExtraOverlay: React.FC<{
  overlay: OverlayExtra;
  legendas: LegendaCaption[];
  duracaoFrames: number;
  mostrarFaltando?: boolean;
  veu?: boolean;
}> = ({ overlay, legendas, duracaoFrames, mostrarFaltando = true, veu = true }) => {
  // animação (componente do registry): reaproveita o layout das animações
  if (!overlay.faltando && overlay.extra_tipo === "animacao" && !overlay.src) {
    const anim: OverlayAnimacao = {
      tipo: "animacao",
      linha: overlay.linhas?.[0] ?? overlay.extra,
      modo: overlay.modo === "pilha" || overlay.modo === "solo" ? "full" : overlay.modo,
      id: overlay.extra,
      componente: overlay.componente ?? overlay.extra,
      descricao: overlay.descricao ?? null,
      props: overlay.props,
      saida_inicio: overlay.saida_inicio,
      saida_fim: overlay.saida_fim,
    };
    return (
      <AnimacaoOverlay
        overlay={anim}
        legendas={legendas}
        duracaoFrames={duracaoFrames}
        mostrarFaltando={mostrarFaltando}
      />
    );
  }
  return <ExtraMidia overlay={overlay} duracaoFrames={duracaoFrames} veu={veu} />;
};

const ExtraMidia: React.FC<{ overlay: OverlayExtra; duracaoFrames: number; veu?: boolean }> = ({
  overlay,
  duracaoFrames,
  veu = true,
}) => {
  const frame = useCurrentFrame();
  const ajuste: Ajuste = LAYOUTS.ajuste[overlay.extra_tipo] ?? "contain";
  const faltando = Boolean(overlay.faltando) || !overlay.src;
  const midia = (fit: Ajuste): React.ReactNode =>
    faltando || !overlay.src ? (
      <Faltando overlay={overlay} />
    ) : ehImagem(overlay.src) ? (
      <ImagemKenBurns src={overlay.src} ajuste={fit} duracaoFrames={duracaoFrames} />
    ) : (
      <VideoExtra
        src={overlay.src}
        inicio={overlay.in ?? 0}
        fim={overlay.out ?? null}
        som={Boolean(overlay.som)}
        ajuste={fit}
        duracaoFrames={duracaoFrames}
      />
    );
  const cr = LAYOUTS.credito;
  const alturaCredito = cr.tamanho * 1.3;

  if (overlay.modo === "split") {
    const c = LAYOUTS.split.caixaExtra;
    // entra deslizando de cima, junto com a câmera que desce
    const desliza = (1 - suave(frame / LAYOUTS.split.transicaoFrames)) * -36;
    return (
      <AbsoluteFill>
        <PainelExtra />
        <div
          style={{
            position: "absolute",
            left: c.x,
            top: c.y,
            width: c.largura,
            height: c.altura,
            overflow: "hidden",
            borderRadius: LAYOUTS.split.raio,
            translate: `0px ${desliza}px`,
          }}
        >
          {midia(ajuste)}
        </div>
        {/* no topo da caixa: embaixo encostava na legenda, que no split fica logo abaixo da divisória (Hinton, 15/10) */}
        {/* rodapé da caixa (17/10: crédito nunca no topo, sobre o rosto) */}
        <Credito
          texto={overlay.credito}
          x={AREA_SEGURA.x}
          y={c.y + c.altura - cr.margem - alturaCredito}
        />
      </AbsoluteFill>
    );
  }

  if (overlay.modo === "solo" && !faltando && overlay.src) {
    // a imagem INTEIRA, sozinha sobre preto, acima da legenda (modelo do Carlos, 17/10): nada de zoom que corta
    const so = LAYOUTS.solo;
    const W = overlay.fonteLargura ?? VIDEO.largura;
    const H = overlay.fonteAltura ?? VIDEO.altura;
    const a = overlay.enquadrar?.area ?? { x: 0, y: 0, largura: W, altura: H };
    const escala = Math.min(VIDEO.largura / a.largura, so.alturaMax / a.altura);
    const largura = Math.round(a.largura * escala);
    const altura = Math.round(a.altura * escala);
    const p = Math.min(1, Math.max(0, frame / Math.max(1, duracaoFrames - 1)));
    const kb = 1 + (so.kenBurns - 1) * p;
    const caixa = { largura, altura, x: Math.round((VIDEO.largura - largura) / 2), y: so.baseY - altura };
    return (
      <AbsoluteFill style={{ backgroundColor: so.fundo }}>
        <div
          style={{
            position: "absolute",
            left: caixa.x,
            top: caixa.y,
            width: caixa.largura,
            height: caixa.altura,
            overflow: "hidden",
            scale: kb,
          }}
        >
          <div
            style={{
              position: "absolute",
              left: -a.x * escala,
              top: -a.y * escala,
              width: W * escala,
              height: H * escala,
            }}
          >
            {ehImagem(overlay.src) ? (
              <Img src={staticFile(overlay.src)} style={{ width: "100%", height: "100%", objectFit: "fill" }} />
            ) : (
              <VideoExtra
                src={overlay.src}
                inicio={overlay.in ?? 0}
                fim={overlay.out ?? null}
                som={Boolean(overlay.som)}
                ajuste="fill"
                duracaoFrames={duracaoFrames}
              />
            )}
          </div>
        </div>
        <Credito texto={overlay.credito} x={AREA_SEGURA.x} y={cr.rodapeY} />
      </AbsoluteFill>
    );
  }

  if (overlay.modo === "pilha" && overlay.pilha && overlay.pilha.length > 0) {
    // 2–3 faixas empilhadas (topo / meio / base), cada uma com o seu enquadramento — pedido do Carlos (17/10):
    // a imagem deitada aparece quase inteira em vez de virar um zoom que corta o rosto/o assunto
    const en = LAYOUTS.enquadrado;
    const n = overlay.pilha.length;
    const vao = LAYOUTS.pilha.vao;
    const alturaFaixa = (VIDEO.altura - vao * (n - 1)) / n;
    const janela = { largura: VIDEO.largura, altura: alturaFaixa };
    const creditos = Array.from(
      new Set(overlay.pilha.map((m) => m.credito ?? overlay.credito).filter((c): c is string => Boolean(c))),
    ).join(" · ");
    return (
      <AbsoluteFill style={{ backgroundColor: COR.fundo }}>
        {overlay.pilha.map((m, i) => (
          <div
            key={`${overlay.extra}-faixa-${i}`}
            style={{
              position: "absolute",
              left: 0,
              top: i * (alturaFaixa + vao),
              width: VIDEO.largura,
              height: alturaFaixa,
              overflow: "hidden",
            }}
          >
            {m.src ? (
              <MidiaEnquadrada overlay={m} duracaoFrames={duracaoFrames} janela={janela} />
            ) : (
              <Faltando overlay={overlay} />
            )}
          </div>
        ))}
        {veu ? <AbsoluteFill style={{ background: en.veuBaixo }} /> : null}
        <Credito texto={creditos || null} x={AREA_SEGURA.x} y={cr.rodapeY} />
      </AbsoluteFill>
    );
  }

  if (overlay.modo === "full" && overlay.enquadrar && !faltando && overlay.src) {
    // preenche 1080×1920 (cover da área útil) + Ken Burns/pan; sem FundoGrade, sem caixa, sem blur
    const en = LAYOUTS.enquadrado;
    return (
      <AbsoluteFill style={{ backgroundColor: COR.fundo }}>
        <MidiaEnquadrada overlay={overlay} duracaoFrames={duracaoFrames} />
        {veu ? <AbsoluteFill style={{ background: en.veuBaixo }} /> : null}
        <Credito texto={overlay.credito} x={AREA_SEGURA.x} y={cr.rodapeY} />
      </AbsoluteFill>
    );
  }

  if (overlay.modo === "full") {
    const w = overlay.fonteLargura ?? 0;
    const h = overlay.fonteAltura ?? 0;
    const cobre = !faltando && w > 0 && h / w >= LAYOUTS.full.proporcaoCobre;
    const c = LAYOUTS.full.caixa;
    return (
      <AbsoluteFill>
        <FundoGrade />
        {cobre ? (
          <AbsoluteFill>{midia("cover")}</AbsoluteFill>
        ) : (
          <div
            style={{
              position: "absolute",
              left: c.x,
              top: c.y,
              width: c.largura,
              height: c.altura,
              overflow: "hidden",
              borderRadius: LAYOUTS.full.raio,
            }}
          >
            {midia(ajuste)}
          </div>
        )}
        <Credito texto={overlay.credito} x={AREA_SEGURA.x} y={cr.fullTopo} />
      </AbsoluteFill>
    );
  }

  // card
  const k = LAYOUTS.card;
  const entrada = interpolate(frame, [0, k.entradaFrames], [0.96, 1], clamp);
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ backgroundColor: `rgba(0,0,0,${k.escurecerPrincipal})` }} />
      <div
        style={{
          position: "absolute",
          left: (VIDEO.largura - k.largura) / 2,
          top: k.centroY - k.altura / 2,
          width: k.largura,
          height: k.altura,
          borderRadius: k.raio,
          overflow: "hidden",
          outline: `1px solid ${COR.borda}`,
          boxShadow: k.sombra,
          backgroundColor: COR.fundo,
          scale: entrada,
        }}
      >
        {midia(ajuste)}
        <Credito texto={overlay.credito} x={cr.margem} y={k.altura - cr.margem - alturaCredito} />
      </div>
    </AbsoluteFill>
  );
};

/** Vídeo do extra: toca [in, out] e, se acabar antes do overlay, segura o último quadro. */
const VideoExtra: React.FC<{
  src: string;
  inicio: number;
  fim: number | null;
  som: boolean;
  ajuste: Ajuste;
  duracaoFrames: number;
}> = ({ src, inicio, fim, som, ajuste, duracaoFrames }) => {
  const { fps } = useVideoConfig();
  const trimBefore = Math.max(0, Math.round(inicio * fps));
  const tocar =
    fim == null
      ? duracaoFrames
      : Math.max(1, Math.min(duracaoFrames, Math.round((fim - inicio) * fps)));
  const video = (mudo: boolean): React.ReactNode => (
    <Video
      src={staticFile(src)}
      trimBefore={trimBefore}
      muted={mudo}
      objectFit={ajuste}
      style={{ width: "100%", height: "100%" }}
    />
  );
  if (tocar >= duracaoFrames) return <>{video(!som)}</>;
  return (
    <>
      <Sequence durationInFrames={tocar} name="extra (tocando)">
        {video(!som)}
      </Sequence>
      <Sequence from={tocar} name="extra (último quadro)">
        <Freeze frame={tocar - 1}>{video(true)}</Freeze>
      </Sequence>
    </>
  );
};

/** Imagem com movimento lento (Ken Burns). */
const ImagemKenBurns: React.FC<{ src: string; ajuste: Ajuste; duracaoFrames: number }> = ({
  src,
  ajuste,
  duracaoFrames,
}) => {
  const frame = useCurrentFrame();
  const kb = LAYOUTS.kenBurns;
  const escala = interpolate(frame, [0, Math.max(1, duracaoFrames)], [kb.escalaInicial, kb.escalaFinal], clamp);
  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <Img
        src={staticFile(src)}
        style={{ width: "100%", height: "100%", objectFit: ajuste, scale: escala }}
      />
    </AbsoluteFill>
  );
};

/** Ease-in-out senoidal: o pan começa e termina devagar (sem tranco no corte seco). */
const easeSeno = (x: number): number => (x <= 0 ? 0 : x >= 1 ? 1 : 0.5 - 0.5 * Math.cos(Math.PI * x));

/**
 * Mídia do extra enquadrada em tela cheia (`overlay.enquadrar`). A cada quadro:
 *   escala = cover(área útil → 1080×1920) × zoom × KenBurns(1 → kenBurns, linear);
 *   foco   = (x,y) → (xFim,yFim) com ease;
 *   a janela visível é PRESA dentro da área útil → nunca aparece barra preta, legenda queimada ou fundo.
 * A fonte inteira é desenhada (fill) num div deslocado; o que está fora do quadro fica cortado.
 */
type MidiaEnquadravel = Pick<
  OverlayExtra,
  "src" | "in" | "out" | "som" | "enquadrar" | "fonteLargura" | "fonteAltura"
>;

const MidiaEnquadrada: React.FC<{
  overlay: MidiaEnquadravel;
  duracaoFrames: number;
  /** Janela de destino (px). Padrão: a tela inteira; no modo `pilha`, uma faixa. */
  janela?: { largura: number; altura: number };
}> = ({ overlay, duracaoFrames, janela = { largura: VIDEO.largura, altura: VIDEO.altura } }) => {
  const frame = useCurrentFrame();
  const e = overlay.enquadrar ?? {};
  const W = overlay.fonteLargura ?? VIDEO.largura;
  const H = overlay.fonteAltura ?? VIDEO.altura;
  const a = e.area ?? { x: 0, y: 0, largura: W, altura: H };
  const p = Math.min(1, Math.max(0, frame / Math.max(1, duracaoFrames - 1)));
  const kb = 1 + ((e.kenBurns ?? LAYOUTS.enquadrado.kenBurns) - 1) * p;
  const cover = Math.max(janela.largura / a.largura, janela.altura / a.altura);
  const s = cover * Math.max(1, e.zoom ?? 1) * kb;
  const vw = janela.largura / s; // janela visível em px da fonte
  const vh = janela.altura / s;
  const q = easeSeno(p);
  const fx = (e.x ?? 0.5) + ((e.xFim ?? e.x ?? 0.5) - (e.x ?? 0.5)) * q;
  const fy = (e.y ?? 0.5) + ((e.yFim ?? e.y ?? 0.5) - (e.y ?? 0.5)) * q;
  const prender = (c: number, ini: number, tam: number, janela: number): number =>
    Math.min(ini + tam - janela / 2, Math.max(ini + janela / 2, c));
  const cx = prender(a.x + fx * a.largura, a.x, a.largura, vw);
  const cy = prender(a.y + fy * a.altura, a.y, a.altura, vh);
  const caixa: React.CSSProperties = {
    position: "absolute",
    left: -(cx - vw / 2) * s,
    top: -(cy - vh / 2) * s,
    width: W * s,
    height: H * s,
  };
  const src = overlay.src ?? "";
  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <div style={caixa}>
        {ehImagem(src) ? (
          <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "fill" }} />
        ) : (
          <VideoExtra
            src={src}
            inicio={overlay.in ?? 0}
            fim={overlay.out ?? null}
            som={Boolean(overlay.som)}
            ajuste="fill"
            duracaoFrames={duracaoFrames}
          />
        )}
      </div>
    </AbsoluteFill>
  );
};

/** "Fonte: X" — pequeno, dentro da zona segura. */
const Credito: React.FC<{ texto?: string | null; x: number; y: number }> = ({ texto, x, y }) => {
  // 19/10 (Carlos): crédito só na descrição do post — nunca dentro do vídeo
  if (!LAYOUTS.credito.mostrar) return null;
  if (!texto) return null;
  const t = /^fonte\s*:/i.test(texto) ? texto : `Fonte: ${texto}`;
  return (
    <div
      style={{
        position: "absolute",
        // o padding do fundo não desloca o texto: a caixa recua o mesmo tanto
        left: x - LAYOUTS.credito.padX,
        top: y - LAYOUTS.credito.padY,
        padding: `${LAYOUTS.credito.padY}px ${LAYOUTS.credito.padX}px`,
        borderRadius: LAYOUTS.credito.raio,
        backgroundColor: LAYOUTS.credito.fundo,
        fontFamily: FONTE.familia,
        fontSize: LAYOUTS.credito.tamanho,
        fontWeight: LAYOUTS.credito.peso,
        color: LAYOUTS.credito.cor,
        textShadow: SOMBRA_TEXTO,
        whiteSpace: "nowrap",
      }}
    >
      {t}
    </div>
  );
};

/** Extra sem arquivo/componente: bem visível no render (o QA reprova até chegar). */
const Faltando: React.FC<{ overlay: OverlayExtra }> = ({ overlay }) => (
  <AbsoluteFill
    style={{
      backgroundColor: LAYOUTS.faltando.fundo,
      border: `4px dashed ${LAYOUTS.faltando.borda}`,
      borderRadius: 18,
      alignItems: "center",
      justifyContent: "center",
      gap: 18,
      padding: "0 48px",
      textAlign: "center",
      fontFamily: FONTE.familia,
    }}
  >
    <div style={{ fontSize: 54, fontWeight: 800, color: LAYOUTS.faltando.borda }}>
      EXTRA {overlay.extra} FALTANDO
    </div>
    {overlay.descricao ? (
      <div style={{ fontSize: 34, fontWeight: 500, lineHeight: 1.25, color: COR.texto }}>
        {overlay.descricao}
      </div>
    ) : null}
    <div
      style={{
        fontSize: ROTULO.tamanho,
        fontWeight: ROTULO.peso,
        letterSpacing: ROTULO.tracking,
        color: COR.cinza,
        textTransform: "uppercase",
      }}
    >
      {overlay.extra_tipo} · {overlay.modo}
    </div>
  </AbsoluteFill>
);

// ---------------------------------------------------------------------------
// Título do hook (sobre o vídeo, com véu escuro)
// ---------------------------------------------------------------------------
const TituloHook: React.FC<{
  titulo: TituloConfig;
  legendas: LegendaCaption[];
  inicioSeg: number;
  duracao: number;
}> = ({ titulo, legendas, inicioSeg, duracao }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const posicao = titulo.posicao ?? "baixo";

  // O rabisco começa quando a palavra-chave é dita (se ela estiver na fala).
  const dita = titulo.rabisco
    ? legendas.find(
        (c) =>
          normalizar(c.text) === normalizar(titulo.rabisco ?? "") &&
          c.startMs >= inicioSeg * 1000,
      )
    : undefined;
  const inicioRabisco = dita ? Math.round((dita.startMs / 1000 - inicioSeg) * fps) : null;

  const veu =
    posicao === "topo"
      ? "linear-gradient(180deg, rgba(0,0,0,0.62) 0%, rgba(0,0,0,0.3) 35%, rgba(0,0,0,0) 60%)"
      : posicao === "baixo"
        ? "linear-gradient(0deg, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.45) 40%, rgba(0,0,0,0) 72%)"
        : "rgba(0,0,0,0.35)";

  return (
    <AbsoluteFill
      style={{ opacity: interpolate(frame, [duracao - 5, duracao], [1, 0], clamp) }}
    >
      <AbsoluteFill
        style={{ background: veu, opacity: interpolate(frame, [0, 6], [0, 1], clamp) }}
      />
      <Titulo
        contexto={titulo.contexto}
        impacto={titulo.impacto}
        cinza={titulo.cinza}
        rabisco={titulo.rabisco}
        selecao={titulo.selecao}
        corRabisco={titulo.corRabisco}
        posicao={posicao}
        inicioRabisco={inicioRabisco}
      />
    </AbsoluteFill>
  );
};
