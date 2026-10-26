import "server-only";
import { statSync } from "node:fs";
import { join, resolve } from "node:path";

// Capas dos vídeos e posts (design-system.md §15.2, "Capa 9:16"): a capa real é o `capa/capa.png` que o pipeline já
// grava em cada pasta. O painel só LÊ o arquivo (nunca escreve): o servidor confere se ele existe e a rota
// app/capa/[pasta]/[slug] o entrega ao navegador, que recebe uma versão reduzida pelo otimizador de imagens do Next.
// Raiz do projeto: a mesma do sincronizador (PAINEL_PROJETO, senão CONTENT_AI_ROOT, senão dois níveis acima de painel/web).

export const RAIZ = resolve(process.env.PAINEL_PROJETO || process.env.CONTENT_AI_ROOT || join(process.cwd(), "..", ".."));

/** As pastas que têm capa, pelo nome curto usado na rota. */
export const PASTAS = {
  fila: "06-publicar",
  publicados: "07-publicados",
  pronto: "05-render-pronto",
  videos: "videos",
} as const;
export type PastaCapa = keyof typeof PASTAS;

/** Slug do projeto (AAAA-MM-DD-palavras): nada de "..", barra ou espaço chega ao sistema de arquivos. */
export const slugValido = (slug: string) => /^\d{4}-\d{2}-\d{2}-[a-z0-9-]+$/.test(slug);

export function arquivoDaCapa(pasta: PastaCapa, slug: string): string | null {
  if (!slugValido(slug) || !Object.hasOwn(PASTAS, pasta)) return null;
  const f = join(RAIZ, PASTAS[pasta], slug, "capa", "capa.png");
  try {
    return statSync(f).isFile() ? f : null;
  } catch {
    return null;
  }
}

/** Endereço da capa para a tela, tentando as pastas na ordem dada; null = sem capa (a tela mostra o quadro neutro). */
export function capa(slug: string, ...pastas: PastaCapa[]): string | null {
  for (const p of pastas) if (arquivoDaCapa(p, slug)) return `/capa/${p}/${slug}`;
  return null;
}
