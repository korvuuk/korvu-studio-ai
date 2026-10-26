import type { ConsumoDia, ExecucaoCusto } from "./db";
import { compacto, usd } from "./formato";

// Consumo de IA por pessoa (registros do Claude Code, sincronizados nas views consumo_diario e execucoes_custo): tokens,
// custo em US$ (preço de tabela da API) e tarefas (execuções com consumo) nos últimos 30 dias. O custo aparece em
// US$, a moeda da tabela da Anthropic, sem câmbio (decisão de 24/10).

export type ConsumoMembro = { tokens: number; usd: number; tarefas: number; modelos: Set<string> };

export function consumoPorMembro(linhas: ConsumoDia[], execs: ExecucaoCusto[]): Map<string, ConsumoMembro> {
  const out = new Map<string, ConsumoMembro>();
  const de = (id: string) => {
    let m = out.get(id);
    if (!m) out.set(id, (m = { tokens: 0, usd: 0, tarefas: 0, modelos: new Set() }));
    return m;
  };
  for (const l of linhas) {
    if (!l.membro_id) continue;
    const m = de(l.membro_id);
    m.tokens += l.tokens;
    m.usd += l.usd ?? 0;
    if (l.tokens > 0) m.modelos.add(l.modelo_nome ?? l.modelo);
  }
  for (const e of execs) if (e.membro_id && e.tarefa) de(e.membro_id).tarefas += 1;
  return out;
}

/** "US$ 16,60" — o custo em dólar, sem câmbio (decisão de 24/10). */
export const custo = (valor: number, casas?: number) => usd(valor, casas);

/** "23,5M" — tokens compactos para as linhas e os cartões. */
export const tokensCurto = (n: number) => compacto(n);
