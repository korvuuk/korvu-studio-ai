import "server-only";
import { readdirSync } from "node:fs";
import { join } from "node:path";
import { cache } from "react";

// Retrato de agente = foto realista (decisão do Carlos, 23/10). As fotos ficam em public/equipe/<id>.jpg, 512×512, com o
// id de painel/equipe.yaml; quem não tem foto mostra as iniciais (componente Avatar). O painel olha a pasta a cada
// pedido (uma leitura por página): foto nova aparece sem reiniciar nada.
const PASTA = join(process.cwd(), "public", "equipe");
const EXTENSOES = ["jpg", "webp", "png"];

const arquivos = cache((): Set<string> => {
  try {
    return new Set(readdirSync(PASTA));
  } catch {
    return new Set();
  }
});

/** "/equipe/roteirista.jpg" ou null (sem foto → iniciais). */
export function fotoDoAgente(id: string): string | null {
  const nomes = arquivos();
  const ext = EXTENSOES.find((e) => nomes.has(`${id}.${e}`));
  return ext ? `/equipe/${id}.${ext}` : null;
}
