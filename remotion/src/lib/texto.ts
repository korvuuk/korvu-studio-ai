/** Utilidades de texto (comparação sem acento/pontuação). */

export const normalizar = (s: string): string =>
  s
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, "");

export const separarPalavras = (s: string): string[] =>
  s.trim().split(/\s+/).filter(Boolean);

/**
 * Procura a sequência de palavras `alvo` dentro de `palavras`.
 * Devolve [início, fimExclusivo] ou null.
 */
export const acharSequencia = (
  palavras: string[],
  alvo: string | null | undefined,
): [number, number] | null => {
  if (!alvo) return null;
  const a = separarPalavras(alvo).map(normalizar).filter(Boolean);
  if (a.length === 0) return null;
  const p = palavras.map(normalizar);
  for (let i = 0; i + a.length <= p.length; i++) {
    let ok = true;
    for (let j = 0; j < a.length; j++) {
      if (p[i + j] !== a[j]) {
        ok = false;
        break;
      }
    }
    if (ok) return [i, i + a.length];
  }
  return null;
};

/** Índice da última ocorrência de `alvo` (uma palavra) em `palavras`. */
export const acharPalavra = (
  palavras: string[],
  alvo: string | null | undefined,
): number => {
  if (!alvo) return -1;
  const n = normalizar(alvo);
  for (let i = palavras.length - 1; i >= 0; i--) {
    if (normalizar(palavras[i]) === n) return i;
  }
  return -1;
};

export const msParaFrame = (ms: number, fps: number): number =>
  Math.round((ms / 1000) * fps);

export const segParaFrame = (s: number, fps: number): number =>
  Math.round(s * fps);
