import { readFile } from "node:fs/promises";
import { arquivoDaCapa, PASTAS, type PastaCapa } from "@/lib/capas";

// Entrega a capa real de um vídeo/post (`<pasta>/<slug>/capa/capa.png`), só leitura. Pasta fora da lista ou slug fora
// do padrão do projeto = 404 (lib/capas.ts). O otimizador de imagens do Next reduz a imagem para o tamanho da tela.
export async function GET(_: Request, { params }: { params: Promise<{ pasta: string; slug: string }> }) {
  const { pasta, slug } = await params;
  // só as chaves do próprio objeto: "constructor", "__proto__" e "toString" não são pastas (PI58)
  if (!Object.hasOwn(PASTAS, pasta)) return new Response("capa não encontrada", { status: 404 });
  const arquivo = arquivoDaCapa(pasta as PastaCapa, slug);
  if (!arquivo) return new Response("capa não encontrada", { status: 404 });
  const corpo = await readFile(arquivo);
  return new Response(new Uint8Array(corpo), {
    headers: {
      "Content-Type": "image/png",
      // a capa muda quando a cor é refeita: um minuto de cache basta
      "Cache-Control": "private, max-age=60",
    },
  });
}
