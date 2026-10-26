/**
 * Tokens da marca Korvu (PROVISÓRIOS).
 *
 * TUDO o que é visual (cores, fontes, tamanhos, tempos, zonas seguras,
 * easings) vive aqui. Quando o design system (`00-marca/design-system/`)
 * for confirmado, só este arquivo deve mudar.
 *
 * Referência: `00-marca/referencias/legendas/estilo-selecao.md`.
 */
import { loadFont as loadBricolage } from "@remotion/google-fonts/BricolageGrotesque";
import { loadFont as loadGeist } from "@remotion/google-fonts/Geist";
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadInterTight } from "@remotion/google-fonts/InterTight";
import { loadFont as loadPlayfair } from "@remotion/google-fonts/PlayfairDisplay";
import { useEffect, useMemo, useState } from "react";
import { Easing, useDelayRender, useVideoConfig } from "remotion";

// ---------------------------------------------------------------------------
// Fontes
// ---------------------------------------------------------------------------
const geist = loadGeist("normal", {
  weights: ["400", "500", "600", "700", "800", "900"],
  subsets: ["latin", "latin-ext"],
});
const interTight = loadInterTight("normal", {
  weights: ["500", "800"],
  subsets: ["latin", "latin-ext"],
});

// Serifa itálica: só para UMA palavra da capa (contraste da referência
// `00-marca/referencias/capas/estilo-editorial-escuro.md`). Nunca em legenda.
const playfair = loadPlayfair("italic", {
  weights: ["400", "500"],
  subsets: ["latin", "latin-ext"],
});

// Design system editorial (Carlos, 21/10 — `00-marca/design-system/korvu-editorial.md`): título em Bricolage
// Grotesque 800, minúsculas, ponto final; texto em Inter. Usado no CTA; legendas e títulos ainda em Geist.
const bricolage = loadBricolage("normal", { weights: ["800"], subsets: ["latin", "latin-ext"] });
const inter = loadInter("normal", { weights: ["500", "600"], subsets: ["latin", "latin-ext"] });

export const FONTE = {
  /** Título editorial (Bricolage Grotesque 800). */
  display: `${bricolage.fontFamily}, "Helvetica Neue", Arial, sans-serif`,
  /** Texto editorial (Inter). */
  texto: `${inter.fontFamily}, "Helvetica Neue", Arial, sans-serif`,
  /** Pilha completa: Geist → Inter Tight → sistema. */
  familia: `${geist.fontFamily}, ${interTight.fontFamily}, "Helvetica Neue", Arial, sans-serif`,
  principal: geist.fontFamily,
  /** Serifa da capa (Playfair Display itálico). */
  serifa: `${playfair.fontFamily}, Georgia, "Times New Roman", serif`,
} as const;

const fontesCarregadas = Promise.all([
  bricolage.waitUntilDone(),
  inter.waitUntilDone(),
  geist.waitUntilDone(),
  interTight.waitUntilDone(),
  playfair.waitUntilDone(),
]);

/**
 * Bloqueia o render até as fontes carregarem e devolve `true` quando prontas.
 * Necessário antes de medir texto (`@remotion/layout-utils`).
 */
export const useFontesProntas = (): boolean => {
  const [prontas, setProntas] = useState(false);
  const { delayRender, continueRender, cancelRender } = useDelayRender();
  const [handle] = useState(() => delayRender("Carregando fontes da marca"));

  useEffect(() => {
    let ativo = true;
    fontesCarregadas
      .then(() => {
        if (ativo) setProntas(true);
        continueRender(handle);
      })
      .catch((err: unknown) => cancelRender(err));
    return () => {
      ativo = false;
    };
  }, [cancelRender, continueRender, handle]);

  return prontas;
};

// ---------------------------------------------------------------------------
// Cores
// ---------------------------------------------------------------------------
/** Alinhado ao design system Korvu (`00-marca/design-system/korvu-video.md`). */
export const COR = {
  fundo: "#0D0D0D",
  texto: "#F2F2F2",
  cinza: "#9B9B9B",
  selecao: "#2E3033",
  alca: "#F2F2F2",
  rabisco: "#A0A0A0",
  acento: "#E85002",
  roxo: "#C108D1",
  nude: "#D9C3AB",
  vidro: "rgba(255, 255, 255, 0.04)",
  vidroBorda: "rgba(255, 255, 255, 0.09)",
  acentoFundo: "rgba(232, 80, 2, 0.12)",
  acentoBorda: "rgba(232, 80, 2, 0.25)",
  linhaGrade: "rgba(255, 255, 255, 0.05)",
  borda: "rgba(255, 255, 255, 0.10)",
  /** Fundo do demo (substitui o vídeo da câmera). */
  demoFundo: "#3A3F47",
} as const;

// ---------------------------------------------------------------------------
// Vídeo e zonas seguras (1080×1920)
// ---------------------------------------------------------------------------
/**
 * `fps` = padrão do projeto (FPS_PROJETO, Lumix S5IIX a 25p). O fps real de cada render vem de
 * `reel-props.json.fps` via `calculateMetadata` — nunca misturar 25/30 (judder).
 */
export const VIDEO = { largura: 1080, altura: 1920, fps: 25 } as const;

export const SAFE = { topo: 270, base: 670, esquerda: 65, direita: 120 } as const;

/** Retângulo livre de UI do Instagram. */
export const AREA_SEGURA = {
  x: SAFE.esquerda,
  y: SAFE.topo,
  largura: VIDEO.largura - SAFE.esquerda - SAFE.direita, // 895
  altura: VIDEO.altura - SAFE.topo - SAFE.base, // 980
  limiteY: VIDEO.altura - SAFE.base, // 1250
} as const;

/**
 * Texto centrado no quadro (x=540) com largura simétrica que respeita
 * as duas margens: 540 - 420 = 120 ≥ 65 (esq) e 540 + 420 = 960 ≤ 960 (dir).
 */
export const AREA_TEXTO = {
  centroX: VIDEO.largura / 2,
  larguraMax: 840,
} as const;

export const GRADE = { colunas: 6, espessura: 1 } as const;

// ---------------------------------------------------------------------------
// Tipografia (níveis do estilo "Texto Selecionado")
// ---------------------------------------------------------------------------
export const NIVEL1 = {
  tamanho: 50,
  peso: 500,
  entrelinha: 1.22,
  tracking: "-0.01em",
  espacoAbaixo: 30,
} as const;

export const NIVEL2 = {
  tamanho: 136,
  tamanhoMin: 84,
  peso: 800,
  entrelinha: 0.95,
  tracking: "-0.02em",
  maxLinhas: 2,
} as const;

export const ROTULO = {
  tamanho: 26,
  peso: 600,
  tracking: "0.14em",
} as const;

export const LEGENDA = {
  // 2026-09-16: +20% a pedido do Carlos (no 1.º vídeo real as legendas ficaram pequenas para Reels)
  tamanho: 78,
  peso: 700,
  entrelinha: 1.12,
  tracking: "-0.01em",
  /** Palavra com `destaque: true` sobe para o nível "impacto". */
  tamanhoDestaque: 132,
  pesoDestaque: 800,
  /** 21/10 (livro-chatgpt, QA): sombra dupla — a legenda cai sobre infográficos claros em tela cheia. */
  sombra: "0 2px 6px rgba(0, 0, 0, 0.85), 0 0 22px rgba(0, 0, 0, 0.65)",
  /** Palavras já ditas / ainda não ditas na página (karaokê). */
  corInativa: COR.cinza,
  corAtiva: COR.texto,
  /** Centro vertical padrão. 1150 com texto de 78 px: bloco de 2 linhas cabe acima da UI (limite y 1250). */
  centroYBaixo: 1150,
  /** Terço médio (quando o rosto permitir). */
  centroYCentro: 960,
  combinarMs: 900,
  maxPalavras: 4,
  /** Quanto a página fica na tela depois da última palavra (se não houver próxima). */
  seguraMs: 350,
} as const;

// ---------------------------------------------------------------------------
// Animação
// ---------------------------------------------------------------------------
export const EASING = {
  /** cubic-bezier(.2,.8,.2,1) — seleção "arrastada". */
  selecao: Easing.bezier(0.2, 0.8, 0.2, 1),
  entrada: Easing.bezier(0.16, 1, 0.3, 1),
  saida: Easing.bezier(0.7, 0, 0.84, 0),
  rabisco: Easing.bezier(0.45, 0.05, 0.25, 1),
} as const;

/**
 * Durações das animações em SEGUNDOS (independentes do fps). Nos componentes use `useTempo()`,
 * que devolve em frames no fps da composição (a 30 fps dá os valores antigos: 6/4/12/15/4/3).
 */
export const TEMPO_SEG = {
  entrada: 0.2,
  karaoke: 4 / 30,
  selecao: 0.4,
  rabisco: 0.5,
  saida: 4 / 30,
  escalonamentoPalavra: 0.1,
} as const;

export type Tempo = {
  entrada: number;
  karaoke: number;
  selecao: number;
  rabisco: number;
  saida: number;
  escalonamentoPalavra: number;
  /** Deslocamento (px) da entrada das palavras. */
  subidaPx: number;
  /** Duração padrão do título do hook (s) se não houver `titulo.fim`. */
  tituloPadraoSeg: number;
};

export const tempoEmFrames = (fps: number): Tempo => {
  const f = (s: number): number => Math.max(1, Math.round(s * fps));
  return {
    entrada: f(TEMPO_SEG.entrada),
    karaoke: f(TEMPO_SEG.karaoke),
    selecao: f(TEMPO_SEG.selecao),
    rabisco: f(TEMPO_SEG.rabisco),
    saida: f(TEMPO_SEG.saida),
    escalonamentoPalavra: f(TEMPO_SEG.escalonamentoPalavra),
    subidaPx: 12,
    tituloPadraoSeg: 3,
  };
};

/** Tokens de tempo em frames no fps da composição atual. */
export const useTempo = (): Tempo => {
  const { fps } = useVideoConfig();
  return useMemo(() => tempoEmFrames(fps), [fps]);
};

/** Compat: tokens em frames no fps padrão. Prefira `useTempo()` (fps real). */
export const TEMPO: Tempo = tempoEmFrames(VIDEO.fps);

// ---------------------------------------------------------------------------
// Layouts
// ---------------------------------------------------------------------------
/**
 * Layouts PRINCIPAL + CENAS EXTRAS (ver `00-marca/layouts.md`). PROVISÓRIO: quando chegar o modelo do
 * Carlos, mude só este objeto. Medidas em px no quadro 1080×1920; tempos em frames são mínimos.
 */
export const LAYOUTS = {
  /**
   * Cena extra DEITADA (formato YouTube 16:9): **extra em cima, Carlos embaixo** — regra do Carlos
   * (2026-09-17, com screenshots de referência). O painel de cima usa a largura toda; o de baixo
   * recorta o rosto. Extra em pé não usa split: vai para `full` (tela cheia).
   */
  split: {
    /**
     * Altura do painel do extra (em cima). O Carlos ocupa daqui até o fim do quadro.
     * 2026-10-02 (Carlos): era 878 com o extra em y 270 — sobrava uma FAIXA PRETA de 270 px no topo ("fica muito
     * amador"). Agora o extra encosta no topo (0–608) e o Carlos ganha 270 px (608–1920).
     */
    alturaExtra: 608,
    /** Fração da altura do vídeo principal que fica no centro do painel de baixo (rosto). */
    focoY: 0.36,
    /** Mídia do extra: largura cheia, 16:9, encostada no topo (0 + 608 = 608). Sem faixa preta. */
    caixaExtra: { x: 0, y: 0, largura: 1080, altura: 608 },
    raio: 0,
    /**
     * Centro do bloco de legendas NO SPLIT: logo abaixo da divisória. Em y≈1150 (posição normal) a legenda
     * caía em cima do rosto, porque no split o painel do Carlos vai de 878 a 1920 — visto no 1.º render
     * com animação (2026-09-17).
     */
    centroLegenda: 715,   // 2026-10-02: divisória subiu de 878 para 608 → legenda sobe junto (era 985)
    /** Entrada/saída do split: a câmera desliza em vez de saltar. */
    transicaoFrames: 10,
  },
  /** Extra em tela cheia (voz continua; legendas por cima). */
  full: {
    /** Extra com altura/largura ≥ isto cobre a tela toda; mais "deitado" fica contido na caixa. */
    proporcaoCobre: 1.5,
    caixa: { x: 40, y: 250, largura: 1000, altura: 1180 },
    raio: 18,
  },
  /** Extra num cartão arredondado sobre o Carlos. */
  card: {
    // 21/10 (livro-chatgpt, Carlos): o cartão fica NO PEITO, abaixo do rosto (queixo ≈ y 900), nunca sobre a cara —
    // 1000×330 com o pé em 1250 (limite da zona segura de baixo). As legendas somem enquanto há cartão (Reel.tsx).
    // Antes: 900×820 centrado em 680 (cobria o rosto).
    largura: 1000,
    altura: 330,
    centroY: 1085,
    raio: 24,
    escurecerPrincipal: 0.2,
    sombra: "0 24px 60px rgba(0, 0, 0, 0.45)",
    /** Frames da entrada (escala 0.96 → 1). */
    entradaFrames: 8,
  },
  /** Como a mídia do extra se ajusta à caixa, por tipo de extra. */
  ajuste: {
    tela: "contain",
    print: "contain",
    imagem: "cover",
    video: "contain",
    camera: "cover",
    animacao: "contain",
  },
  /** Movimento lento das imagens (Ken Burns): escala do início → fim do overlay. */
  kenBurns: { escalaInicial: 1.0, escalaFinal: 1.08 },
  /**
   * Extra `full` com `enquadrar` (Hinton v2, 15/10 — "faixa contínua em tela cheia"): a mídia preenche 1080×1920,
   * Ken Burns em foto E vídeo, corte seco na entrada/saída. Os véus são degradês leves (não viram faixa): o de baixo
   * fica atrás da legenda (centro y≈1150), o de cima atrás do crédito.
   */
  enquadrado: {
    kenBurns: 1.1,
    // 21/10 (livro-chatgpt, QA): véu mais fundo na faixa da legenda (y≈1060–1240) — os resultados do ChatGPT são
    // quase brancos e a palavra ainda não dita (cinza) sumia. Continua degradê, não vira faixa.
    veuBaixo:
      "linear-gradient(180deg, rgba(0,0,0,0) 42%, rgba(0,0,0,0.55) 52%, rgba(0,0,0,0.78) 58%, rgba(0,0,0,0.78) 66%, rgba(0,0,0,0.45) 76%, rgba(0,0,0,0.15) 100%)",
    veuTopo: "linear-gradient(180deg, rgba(0,0,0,0.30) 0%, rgba(0,0,0,0.12) 14%, rgba(0,0,0,0) 22%)",
  },
  /** Extras em PILHA (Fei-Fei v2, 17/10): 2–4 faixas empilhadas; `vao` = fresta escura entre as faixas (px). */
  pilha: { vao: 6 },
  /**
   * Extra SOLO (Fei-Fei v3, 17/10 — modelo do Carlos): a mídia inteira (contain) numa caixa de 1080 de largura, sobre
   * fundo preto, com a base em `baseY` (acima da legenda, que fica em y≈1150) e altura máxima `alturaMax`.
   */
  /* kenBurns 1.08 (19/10): "toda imagem em movimento, sempre" — nada estático, nem no solo */
  solo: { baseY: 1000, alturaMax: 700, fundo: "#000000", kenBurns: 1.08 },
  /**
   * "Fonte: X" dos extras de terceiros. **Desde 19/10 (Carlos) NÃO aparece no vídeo**: "polui a imagem, não fica
   * profissional" — os créditos vão só na descrição do post (publicador). `mostrar: false` desliga o `Credito` em
   * todos os modos; as posições abaixo ficam para o dia em que ele quiser de volta.
   */
  credito: {
    mostrar: false,
    tamanho: 24,
    peso: 600,
    cor: "rgba(242, 242, 242, 0.92)",
    /** Fundo escuro suave atrás do texto: sobre foto clara só a sombra não bastava (Hinton v3, 15/10). */
    fundo: "rgba(0, 0, 0, 0.45)",
    padX: 10,
    padY: 4,
    raio: 8,
    margem: 16,
    /** Posição no modo full (a mídia cobre a tela; fica logo abaixo da UI do topo). */
    fullTopo: 290,
    /**
     * RODAPÉ (Carlos, 17/10): o crédito dos extras em tela cheia / solo / pilha fica embaixo da legenda, nunca no
     * topo sobre o rosto. Linha pequena logo abaixo da zona da legenda (base 1236); acima da UI inferior do Instagram.
     */
    rodapeY: 1262,
  },
  /** Placeholder de extra faltando (visível no render; o QA reprova). */
  faltando: {
    borda: "rgba(255, 122, 53, 0.9)",
    fundo: "rgba(17, 17, 17, 0.88)",
  },
} as const;

export type ModoExtra = "split" | "full" | "card";

/** Compat (layouts antigos tela/animação) — derivados de LAYOUTS. */
export const SPLIT = {
  /** Onde começa o painel do Carlos (= altura do painel do extra, que fica EM CIMA). */
  topoCamera: LAYOUTS.split.alturaExtra,
  focoY: LAYOUTS.split.focoY,
  caixaSuperior: LAYOUTS.split.caixaExtra,
} as const;

/** Formato da mídia do extra: deitado (≥ isto) divide a tela; em pé ocupa a tela toda. */
export const LIMIAR_HORIZONTAL = 1.2;

export const TELA_CHEIA = {
  caixa: LAYOUTS.full.caixa,
} as const;

export const CARD = {
  largura: LAYOUTS.card.largura,
  altura: LAYOUTS.card.altura,
  centroY: LAYOUTS.card.centroY,
  raio: LAYOUTS.card.raio,
  escurecerVideo: LAYOUTS.card.escurecerPrincipal,
} as const;

export const ZOOM = {
  /** Origem do punch-in (rosto no terço superior). */
  origem: "50% 38%",
} as const;

export const CAPA = {
  /** Recorte central 3:4 que aparece na grade do perfil. */
  recorte: { y: 240, altura: 1440 },
  margem: 90,
  tamanhoImpacto: 150,
} as const;

export const SOMBRA_TEXTO = LEGENDA.sombra;

// ---------------------------------------------------------------------------
// Editorial (21/10) — papel, tinta e UM acento. Fonte única: 00-marca/design-system/korvu-editorial.md
// ---------------------------------------------------------------------------
export const EDITORIAL = {
  papel: "#E7E4D9",
  papel2: "#DCD8CB",
  tinta: "#111111",
  tinta2: "#5A5852",
  acento: COR.acento, // #E85002 — o laranja aprovado no CTA em 14/10
} as const;

// ---------------------------------------------------------------------------
// CTA final — cartão editorial: "comenta" + palavra em minúsculas SEM ponto (Carlos, 14/10 → visual de 21/10)
// ---------------------------------------------------------------------------
/** Cor da PALAVRA do CTA = acento da marca (só esta linha muda se um dia trocar). */
export const CTA_COR: string = EDITORIAL.acento;

/**
 * Cartão do CTA (componente `CtaPalavra`). Carlos em tela cheia no CTA (regra 6): o cartão fica entre o queixo e o
 * limite de baixo da zona segura (y 1250) — a boca dele, em y≈770–820 no enquadramento padrão, fica livre.
 * Molde editorial de 21/10: cartão de papel sem canto/sombra, palavra Bricolage 800 no acento, sem carimbo (Carlos, 21/10).
 */
export const CTA = {
  /** Base do cartão. ≤ AREA_SEGURA.limiteY (1250). */
  baseY: AREA_SEGURA.limiteY - 14,
  /** Largura máxima do cartão (centrado em x=540; a borda direita fica longe dos botões do app). */
  larguraCartao: 860,
  padding: { x: 44, topo: 30, base: 32 },
  /** Teto do tamanho da palavra (palavras curtas, ex. "IA", não viram um muro). */
  /** 190: com 230 o cartão subia até a boca do Carlos (still do Hinton, 21/10). */
  tamanhoMax: 190,
  tamanhoMin: 96,
  peso: 800,
  tracking: "-0.035em",
  entrelinha: 0.86,
  /** Linha de cima ("comenta"). */
  topo: { tamanho: 42, peso: 500, cor: EDITORIAL.tinta },
  /** Linha de baixo ("que eu te mando no direct"). */
  rodape: { tamanho: 32, peso: 500, cor: EDITORIAL.tinta },
  rodapePadrao: "que eu te mando no direct",
  /** Fio de 2 px entre a palavra e o rodapé. */
  fio: { espessura: 2, cor: EDITORIAL.tinta },
  /** Entrada (frames): o cartão sobe e aparece; a palavra entra com mola curta. */
  entradaFrames: 7,
  saidaFrames: 4,
  /** Quanto o cartão fica depois do fim da fala do CTA (s) — o gerar_props já soma isto ao `fim`. */
  seguraSeg: 0.5,
} as const;
