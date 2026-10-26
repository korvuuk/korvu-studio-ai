/**
 * Tipos dos dados que chegam ao Remotion.
 * Espelham `docs/contratos.md` §4 (overlays), §6 (legendas) e §7 (reel-props.json).
 */
import type { Caption } from "@remotion/captions";

/** §6 — `Caption` do @remotion/captions + extras do estúdio. */
export type LegendaCaption = Caption & {
  linha?: string;
  destaque?: boolean;
};

/** Punch-in do segmento (EDL antiga). `origem` = ponto fixo do zoom (rosto, "x% y%"). */
export type Zoom = { tipo: "punch"; escala: number; origem?: string } | null;

export type Layout = "full" | "split";

export type Segmento = {
  saidaInicio: number;
  saidaFim: number;
  zoom: Zoom;
  layout: Layout;
};

/** Retângulo do conteúdo útil dentro da fonte (px da fonte). */
export type Recorte = { x: number; y: number; largura: number; altura: number };

type OverlayBase = {
  saida_inicio: number;
  saida_fim: number;
};

export type OverlayTexto = OverlayBase & {
  tipo: "texto";
  linha: string;
  texto: string;
  /** `tela` (padrão) = texto sobre o vídeo; `cartela` = card em tela cheia. */
  modo?: "tela" | "cartela";
  contexto?: string | null;
  cinza?: number;
  rabisco?: string | null;
  selecao?: string | null;
  /** Em `cartela`, as legendas somem por padrão; `true` mantém. */
  legendas?: boolean;
};

/** Legado (EDLs antigas): gravação de tela. Hoje vira `tipo: "extra"`. */
export type OverlayTela = OverlayBase & {
  tipo: "tela";
  linha: string;
  fonte?: string;
  /** Caminho relativo a `remotion/public` (ex.: `_render/<slug>/fontes/tela-01.mp4`). */
  src: string;
  in: number;
  out: number;
  modo: "split" | "full";
  /** Área útil da gravação dentro do quadro com `pad` (px). */
  recorte?: Recorte | null;
  fonteLargura?: number;
  fonteAltura?: number;
};

/** Legado (EDLs antigas): animação por linha. Hoje vira `tipo: "extra"` com `extra_tipo: "animacao"`. */
export type OverlayAnimacao = OverlayBase & {
  tipo: "animacao";
  linha: string;
  modo: "full" | "split" | "card";
  /** Chave no registry (`animacoes/registry.ts`). */
  id: string;
  /** Opcional: nome do componente no registry, se diferente do `id`. */
  componente?: string | null;
  descricao?: string | null;
  props?: Record<string, unknown>;
};

export type TipoExtra = "tela" | "print" | "imagem" | "video" | "animacao" | "camera";

/**
 * Enquadramento do extra em TELA CHEIA (modo `full`) — opção explícita por overlay (Hinton v2, 15/10).
 * Com `enquadrar`, a mídia (foto OU vídeo, horizontal ou vertical) PREENCHE o quadro 1080×1920 (cover, sem caixa,
 * sem fundo de grade, sem blur), recortada dentro de `area`, com Ken Burns sempre e pan opcional.
 * Sem `enquadrar`, o modo `full` continua como antes (vertical cobre, deitado vai para a caixa).
 */
export type Enquadrar = {
  /** Foco horizontal/vertical (0–1, fração da `area`) que fica no centro do quadro. Padrão 0.5 / 0.5. */
  x?: number;
  y?: number;
  /** Zoom inicial sobre o "cover" da `area` (≥ 1). Padrão 1. */
  zoom?: number;
  /** Pan: foco no FIM do overlay (o foco anda de x,y → xFim,yFim). Ausente = parado. */
  xFim?: number;
  yFim?: number;
  /** Fator do Ken Burns ao longo do overlay (1.00 → kenBurns). Padrão LAYOUTS.enquadrado.kenBurns (1.10). */
  kenBurns?: number;
  /**
   * Área útil da fonte (px da fonte): o recorte NUNCA sai dela. Serve para tirar barras pretas (4:3 dentro de 16:9),
   * legenda queimada no rodapé, tarja de TV e logos de canto. Padrão = a fonte inteira.
   */
  area?: Recorte | null;
};

/** Uma faixa do modo `pilha`: a mesma mídia/enquadramento de um extra `full`, só que dentro da faixa. */
export type PilhaItem = {
  id?: string;
  arquivo?: string | null;
  src?: string | null;
  extra_tipo?: TipoExtra;
  in?: number;
  out?: number;
  som?: boolean;
  credito?: string | null;
  enquadrar?: Enquadrar | null;
  fonteLargura?: number;
  fonteAltura?: number;
};

/** §4 — cena extra (B-roll) por cima do vídeo principal. */
export type OverlayExtra = OverlayBase & {
  tipo: "extra";
  linhas: string[];
  linha?: string;
  extra: string;
  extra_tipo: TipoExtra;
  /** Caminho relativo à pasta do vídeo (`edicao/extras/E01.mp4`). */
  arquivo?: string | null;
  /** Caminho relativo a `remotion/public` (escrito pelo gerar_props.py). */
  src?: string | null;
  modo: "split" | "full" | "card" | "pilha" | "solo";
  /**
   * Modo `pilha` (Fei-Fei v2, 17/10 — pedido do Carlos): 2–3 mídias EMPILHADAS na vertical, uma por faixa (topo /
   * meio / base), cada uma com o seu `enquadrar` dentro da faixa 1080×(1920/n). A imagem deitada aparece quase
   * inteira em vez de virar um zoom que corta. Corte seco, crédito único no topo (os créditos das faixas juntos).
   */
  pilha?: PilhaItem[] | null;
  /**
   * Modo `solo` (Fei-Fei v3, 17/10 — modelo do Carlos): a imagem deitada INTEIRA, sozinha no meio da tela preta,
   * sem zoom, com a legenda logo abaixo — para imagem de leitura (esquema, gráfico, jornal, nomes). `enquadrar.area`
   * ainda recorta a fonte (barras, logos); foco/zoom/pan são ignorados.
   */
  /** Trecho do próprio extra (s). Se `out - in` < duração do overlay, segura o último quadro. */
  in?: number;
  out?: number;
  som?: boolean;
  credito?: string | null;
  /** Chave no registry para `extra_tipo: "animacao"` (ex.: "<slug>/E02"). */
  componente?: string | null;
  descricao?: string | null;
  /** Sem arquivo/componente: placeholder "EXTRA Exx FALTANDO" (o QA reprova). */
  faltando?: boolean;
  fonteLargura?: number;
  fonteAltura?: number;
  /** Só no modo `full`: preenche a tela com foco/zoom/pan + Ken Burns (ver `Enquadrar`). Corte seco nas bordas. */
  enquadrar?: Enquadrar | null;
  props?: Record<string, unknown>;
};

export type Overlay = OverlayTexto | OverlayTela | OverlayAnimacao | OverlayExtra;

/** §7 `titulo`. Campos além do contrato são opcionais. */
export type TituloConfig = {
  contexto: string;
  impacto: string;
  /** Quantas palavras iniciais do impacto ficam cinza. */
  cinza: number;
  /** Palavra do impacto que recebe o rabisco. */
  rabisco?: string | null;
  /** Palavras do contexto com realce de seleção (padrão: últimas 2). */
  selecao?: string | null;
  corRabisco?: string | null;
  /** Janela na timeline (s). Padrão: 0 → fim da 1.ª linha (≈3 s). */
  inicio?: number | null;
  fim?: number | null;
  posicao?: "topo" | "centro" | "baixo";
  /** Esconde as legendas enquanto o título está na tela (padrão true). */
  ocultarLegendas?: boolean;
  origem?: string;
};

/**
 * §7 `cta` — cartão "comenta" + PALAVRA gigante (decisão de 14/10). Escrito pelo `gerar_props.py`
 * (`derivar_cta`): `inicio` = palavra "comenta" dita na linha de seção `cta`; `fim` = fim dessa linha + 0,5 s.
 */
export type CtaConfig = {
  /** `roteiro.json.cta_palavra` (MAIÚSCULAS, sem acento). */
  palavra: string;
  /** Janela na timeline (s). */
  inicio: number;
  fim: number;
  /** Linha de cima (padrão "comenta"). */
  topo?: string | null;
  /** Linha pequena de baixo (fim da fala do CTA ou "que eu te mando no direct"). `null` = sem linha. */
  rodape?: string | null;
  linha?: string | null;
  origem?: string;
};

export type ReelProps = {
  /** Relativo a `remotion/public`. `null` = fundo sólido (demo). */
  video: string | null;
  duracaoSeg: number;
  /** fps do projeto (edl.json.fps / FPS_PROJETO). Ausente = `VIDEO.fps` (25). */
  fps?: number;
  legendas: LegendaCaption[];
  overlays: Overlay[];
  segmentos: Segmento[];
  /** true = o plano de zoom já está no vídeo (render_corte, edl.json zoom_no_corte): o Reel NÃO aplica zoom. */
  zoomNoCorte?: boolean;
  titulo: TituloConfig | null;
  /** CTA de palavra-chave em cartão grande (some com as legendas das palavras dentro da janela). */
  cta?: CtaConfig | null;
  /**
   * `false` no render FINAL: extras que faltam somem do vídeo em vez de virar a etiqueta
   * "EXTRA Exx FALTANDO" (regra do Carlos, 2026-09-17: o vídeo final sai cru, sem etiqueta).
   * O QA continua reprovando enquanto o extra não chegar.
   */
  mostrarFaltando?: boolean;
  /** 21/10: `false` = sem legenda karaokê (formato rápido de comandos); título do hook e CTA continuam. */
  mostrarLegendas?: boolean;
  estiloLegenda: "selecao";
  /** `baixo` (y≈1170, padrão) ou `centro` (terço médio). */
  legendaPosicao?: "baixo" | "centro";
  /** Caminho (relativo a `public/`) de um reel-props.json a carregar no Studio. */
  arquivoProps?: string | null;
};

/** Palavra entregue às animações, com tempos relativos ao início do overlay. */
export type PalavraAnimacao = {
  texto: string;
  inicioMs: number;
  fimMs: number;
  destaque: boolean;
};
