import "server-only";
import { cache } from "react";
import * as db from "./db";
import { diaEmLondres } from "./formato";

// Leituras do banco usadas por mais de um bloco da mesma página: `cache` do React faz cada uma ir ao banco uma vez por
// pedido, mesmo com os blocos em Suspense separados.

export const agentes = cache(db.agentes);
export const departamentos = cache(db.departamentos);
export const snapshots = cache(db.snapshots);
export const metricas = cache(db.metricas);
export const demografia = cache((lido: string) => db.demografia(lido));
export const precos = cache(db.precos);
/** A última sincronização (a "leitura" escrita no topo das telas de números). */
export const sincronizacao = cache(db.estadoDoBanco);


/** Janela de consumo de IA: os últimos `dias` dias em Londres, hoje incluído. */
export function janela(dias: number, agora = new Date()) {
  const ate = diaEmLondres(agora);
  const de = new Date(Date.parse(`${ate}T00:00:00Z`) - (dias - 1) * 86_400_000).toISOString().slice(0, 10);
  return { de, ate, dias };
}

/** Consumo por dia, modelo e pessoa nos últimos 30 dias (view consumo_diario). */
export const consumo30 = cache(async () => db.consumoDesde(janela(30).de));
/** Consumo por execução nos últimos 30 dias (view consumo): o custo por vídeo. */
export const consumoExecucoes30 = cache(async () => db.consumoExecucoesDesde(janela(30).de));
/** Execuções que começaram nos últimos 30 dias (view execucoes_custo), para contar tarefas. */
export const execucoes30 = cache(async () => db.execucoesDesde(`${janela(30).de}T00:00:00Z`));


/** O modelo que rodou (decisão de 24/10): o principal pelos tokens dos 30 dias e os outros; null = ainda não rodou. */
export type ModeloRodou = { principal: { modelo: string; nome: string; pct: number }; outros: { nome: string; pct: number }[] };
export const modelosRodados = cache(async (): Promise<Map<string, ModeloRodou | null>> => {
  const linhas = await db.modeloPorAgente();
  const out = new Map<string, ModeloRodou | null>();
  const porAgente = new Map<string, db.ModeloPorAgente[]>();
  for (const l of linhas) porAgente.set(l.agente_id, [...(porAgente.get(l.agente_id) ?? []), l]);
  for (const [id, ls] of porAgente) {
    const rodou = ls.filter((l) => l.modelo && l.tokens > 0).sort((a, b) => b.tokens - a.tokens);
    if (!rodou.length) { out.set(id, null); continue; }
    const nome = (l: db.ModeloPorAgente) => l.modelo_nome ?? l.modelo!;
    out.set(id, {
      principal: { modelo: rodou[0].modelo!, nome: nome(rodou[0]), pct: rodou[0].pct_tokens ?? 100 },
      outros: rodou.slice(1).map((l) => ({ nome: nome(l), pct: l.pct_tokens ?? 0 })),
    });
  }
  return out;
});
