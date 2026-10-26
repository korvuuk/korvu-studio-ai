import "server-only";
import { cache } from "react";
import type { Aviso } from "@/components/Avisos";
import type { ItemBusca } from "@/components/Busca";
import * as db from "./db";
import { nomeDoPortao } from "./estados";
import { AGENTE_DO_PORTAO, primeiraMaiuscula } from "./formato";
import { PAGINAS } from "./navegacao";
import { FASES, lerProducao, precisamDeAtencao } from "./producao";

// O que a casca mostra em TODA página (contagem da equipe, busca, avisos), lido uma vez por pedido. Se o banco não
// responde, a casca não cai: devolve null e cada peça mostra o seu "sem leitura" (o aviso do topo diz o que fazer).

const ler = cache(async () => {
  try {
    const [agentes, departamentos, producao] = await Promise.all([db.agentes(), db.departamentos(), lerProducao()]);
    return { agentes, departamentos, producao };
  } catch {
    return null;
  }
});

export async function contagemDaEquipe(): Promise<number | null> {
  const d = await ler();
  return d && d.agentes.length > 0 ? d.agentes.length : null;
}

const paginas: ItemBusca[] = PAGINAS.map((p) => ({ tipo: "Página", rotulo: p.nome, href: p.href }));

/** Vídeos (nome curto, fase e slug), pessoas (nome e função), portões e páginas. Só nome e endereço vão ao navegador. */
export async function itensDaBusca(): Promise<ItemBusca[]> {
  const d = await ler();
  if (!d) return paginas;
  const depto = new Map(d.departamentos.map((x) => [x.id, x.nome]));
  const pessoas: ItemBusca[] = d.agentes.map((a) => ({
    tipo: "Pessoa", rotulo: a.nome, detalhe: primeiraMaiuscula(a.cargo.split(" · ")[0]), href: `/equipe/${a.id}`,
    termos: `${a.id} ${a.cargo} ${depto.get(a.departamento_id) ?? ""}`,
  }));
  const nomeFase = new Map(FASES.map((f) => [f.id, f.nome]));
  const p = d.producao;
  const videos: ItemBusca[] = [
    ...p.vids.filter((v) => v.fase).map((v) => ({
      tipo: "Vídeo" as const, rotulo: v.nome, detalhe: nomeFase.get(v.fase!), href: `/producao#${v.fase}`, termos: `${v.slug} ${v.tema ?? ""}`,
    })),
    ...p.agendados.map((f) => ({ tipo: "Vídeo" as const, rotulo: f.nome, detalhe: "Agendado", href: "/producao#agendados", termos: f.slug })),
    ...p.publicados.map((f) => ({ tipo: "Vídeo" as const, rotulo: f.nome, detalhe: "Publicado", href: "/producao#publicados", termos: `${f.slug} ${f.tema ?? ""}` })),
  ];
  const nome = new Map(d.agentes.map((a) => [a.id, a.nome]));
  const portoes: ItemBusca[] = Object.entries(AGENTE_DO_PORTAO).map(([portao, agente]) => ({
    tipo: "Portão", rotulo: nomeDoPortao(portao), detalhe: nome.get(agente), href: `/equipe/${agente}`, termos: portao,
  }));
  return [...videos, ...pessoas, ...portoes, ...paginas];
}

/** "Precisam de atenção" (lib/producao.ts): a lista do sino; null = não deu para ler o banco. */
export async function avisosDaCasca(): Promise<Aviso[] | null> {
  const d = await ler();
  if (!d) return null;
  return precisamDeAtencao(d.producao, d.agentes);
}
