/**
 * Caption[] → páginas de 2–4 palavras (lógica pura, sem fontes/React —
 * pode ser testada com `node` direto).
 */
import { createTikTokStyleCaptions, type Caption } from "@remotion/captions";
import type { LegendaCaption } from "./tipos";

export type TokenLegenda = {
  texto: string;
  inicioMs: number;
  fimMs: number;
  destaque: boolean;
};

export type PaginaLegenda = {
  inicioMs: number;
  fimMs: number;
  tokens: TokenLegenda[];
  texto: string;
};

const FIM_DE_FRASE = /[.!?…]["”')]*$/;

/** Divide uma página longa em pedaços equilibrados (ex.: 5 → 3+2). */
const dividir = (tokens: TokenLegenda[], max: number): TokenLegenda[][] => {
  if (tokens.length <= max) return [tokens];
  const n = Math.ceil(tokens.length / max);
  const base = Math.floor(tokens.length / n);
  let resto = tokens.length % n;
  const out: TokenLegenda[][] = [];
  let i = 0;
  while (i < tokens.length) {
    const tam = base + (resto > 0 ? 1 : 0);
    resto = Math.max(0, resto - 1);
    out.push(tokens.slice(i, i + tam));
    i += tam;
  }
  return out;
};

/**
 * Quebra obrigatória na troca de linha do roteiro e no fim de frase;
 * o resto é agrupado pelo `createTikTokStyleCaptions`.
 */
export const montarPaginas = (
  legendas: LegendaCaption[],
  combinarMs: number,
  maxPalavras: number,
): PaginaLegenda[] => {
  const validas = legendas.filter((c) => c.text.trim() !== "");
  const preparadas: Caption[] = validas.map((c, i) => {
    const prox = validas[i + 1];
    const quebra =
      Boolean(c.pageBreakAfter) ||
      !prox ||
      (prox.linha !== undefined && prox.linha !== c.linha) ||
      FIM_DE_FRASE.test(c.text.trim());
    return {
      text: c.text.startsWith(" ") ? c.text : ` ${c.text}`,
      startMs: c.startMs,
      endMs: c.endMs,
      timestampMs: c.timestampMs,
      confidence: c.confidence,
      ...(quebra ? { pageBreakAfter: true } : {}),
    };
  });
  const { pages } = createTikTokStyleCaptions({
    captions: preparadas,
    combineTokensWithinMilliseconds: combinarMs,
  });

  // Os tokens saem 1:1 e na mesma ordem das legendas não vazias.
  let k = 0;
  const paginas: PaginaLegenda[] = [];
  for (const pg of pages) {
    const tokens: TokenLegenda[] = pg.tokens.map((t) => {
      const origem = validas[k++];
      return {
        texto: t.text.trim(),
        inicioMs: t.fromMs,
        fimMs: t.toMs,
        destaque: Boolean(origem?.destaque),
      };
    });
    for (const grupo of dividir(tokens, maxPalavras)) {
      if (grupo.length === 0) continue;
      paginas.push({
        inicioMs: grupo[0].inicioMs,
        fimMs: grupo[grupo.length - 1].fimMs,
        tokens: grupo,
        texto: grupo.map((g) => g.texto).join(" "),
      });
    }
  }

  // Página órfã (1 palavra curta) junta-se à vizinha: no 1.º vídeo real aparecia um "e" sozinho na tela.
  // Só quando a vizinha é da MESMA linha do roteiro, cabe em maxPalavras e está colada no tempo (≤ 400 ms).
  // 2026-09-16: 400 ms / maxPalavras não bastaram — o "e" da L09 ficava sozinho (vizinhas cheias e a mais de
  // 400 ms). Palavra curta pode ultrapassar maxPalavras em 1 e juntar-se até 900 ms de distância.
  const COLADO_MS = 900;
  const orfa = (p: PaginaLegenda): boolean =>
    p.tokens.length === 1 && p.tokens[0].texto.replace(/[^\p{L}\p{N}]/gu, "").length <= 3;
  for (let i = 0; i < paginas.length; i++) {
    if (!orfa(paginas[i])) continue;
    const ant = paginas[i - 1];
    const prox = paginas[i + 1];
    const cabeAnt = ant && ant.tokens.length <= maxPalavras && paginas[i].inicioMs - ant.fimMs <= COLADO_MS;
    const cabeProx = prox && prox.tokens.length <= maxPalavras && prox.inicioMs - paginas[i].fimMs <= COLADO_MS;
    const alvo = cabeProx && (!cabeAnt || prox.inicioMs - paginas[i].fimMs < paginas[i].inicioMs - ant.fimMs)
      ? prox
      : cabeAnt
        ? ant
        : null;
    if (!alvo) continue;
    const juntos = alvo === prox ? [...paginas[i].tokens, ...alvo.tokens] : [...alvo.tokens, ...paginas[i].tokens];
    alvo.tokens = juntos;
    alvo.inicioMs = juntos[0].inicioMs;
    alvo.fimMs = juntos[juntos.length - 1].fimMs;
    alvo.texto = juntos.map((g) => g.texto).join(" ");
    paginas.splice(i, 1);
    i--;
  }
  return paginas;
};
