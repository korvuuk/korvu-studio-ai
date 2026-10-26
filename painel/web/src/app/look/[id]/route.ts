import { readFile, stat } from "node:fs/promises";
import { join, resolve, sep } from "node:path";
import { RAIZ } from "@/lib/capas";
import { previaDoLook } from "@/lib/db";

// Entrega a prévia de um look de cor (a foto do Carlos com aquele look), só leitura: o arquivo que o sincronizador
// gravou em looks.previa (painel/previas/looks/<id>-<hash>.jpg, feito pelo painel/sync/previas_looks.py). O endereço só
// diz o id do look (vlog, rec709, vN); o caminho vem do banco e tem de estar dentro de painel/previas/looks/ (como a
// rota de capas, PI58: nada de caminho vindo do endereço).

const PASTA = resolve(RAIZ, "painel", "previas", "looks");
const nao = () => new Response("prévia não encontrada", { status: 404 });

export async function GET(_: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  if (!/^(vlog|rec709|v[0-9]{1,3})$/.test(id)) return nao();
  let caminho: string | null;
  try {
    caminho = await previaDoLook(id);
  } catch {
    return new Response("o banco do painel não respondeu", { status: 503 });
  }
  if (!caminho || !/^painel\/previas\/looks\/[a-z0-9-]+\.jpg$/.test(caminho)) return nao();
  const arquivo = resolve(join(RAIZ, caminho));
  if (!arquivo.startsWith(PASTA + sep)) return nao();
  try {
    if (!(await stat(arquivo)).isFile()) return nao();
  } catch {
    return nao();
  }
  const corpo = await readFile(arquivo);
  return new Response(new Uint8Array(corpo), { headers: { "Content-Type": "image/jpeg", "Cache-Control": "private, max-age=300" } });
}
