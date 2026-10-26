import "server-only";
import { cache } from "react";
import { type ConsumoMembro, consumoPorMembro } from "./consumo";
import type { Agente, Departamento } from "./db";
import { gerentes, primeiraMaiuscula } from "./formato";
import { agentes, consumo30, departamentos, execucoes30, janela } from "./leituras";

// Tokens e custos (telas/tokens-e-custos.md): tudo sai do banco — consumo_diario (tokens e US$ por dia, modelo, pessoa e
// departamento) e execucoes_custo (tarefas). Tokens = entrada + cache gravado + saída (a
// coluna `tokens` do banco); o cache LIDO fica fora do total e aparece à parte. Custo em US$ (preço de tabela da API,
// precos_modelo), mostrado em US$ sem câmbio (decisão de 24/10). Janela: os últimos 30 dias em Londres, hoje incluído — a mesma da Visão
// geral e da Equipe, para o número ser o mesmo nas três telas.

export type Parte = { id: string; nome: string; tokens: number; usd: number };
export type Dia = { dia: string; tokens: number; usd: number };
export type Pessoa = ConsumoMembro & { agente: Agente; modelosOrdem: string[] };

const somar = <K extends string>(mapa: Map<K, Parte>, id: K, nome: string, tokens: number, usd: number) => {
  const p = mapa.get(id) ?? { id, nome, tokens: 0, usd: 0 };
  p.tokens += tokens;
  p.usd += usd;
  mapa.set(id, p);
};

export const lerTokens = cache(async () => {
  const [linhas, execs, ags, deps] = await Promise.all([consumo30(), execucoes30(), agentes(), departamentos()]);
  const j = janela(30);

  // por dia: os 30 dias da janela, dia sem sessão = 0
  const dias: Dia[] = Array.from({ length: j.dias }, (_, i) => ({
    dia: new Date(Date.parse(`${j.de}T00:00:00Z`) + i * 86_400_000).toISOString().slice(0, 10), tokens: 0, usd: 0,
  }));
  const indice = new Map(dias.map((d, i) => [d.dia, i]));

  const modelos = new Map<string, Parte>();
  const porDep = new Map<string, Parte>();
  const nomeDep = new Map(deps.map((d) => [d.id, d]));
  const diretor = ags.find((a) => a.papel === "diretor");
  // modelos de cada pessoa por tokens (o "Rodou em" na ordem do que mais rodou)
  const modeloPessoa = new Map<string, Map<string, number>>();
  let tokens = 0, usd = 0, cacheLido = 0;

  for (const l of linhas) {
    const u = l.usd ?? 0;
    tokens += l.tokens;
    usd += u;
    cacheLido += l.cache_lido;
    const i = indice.get(l.dia.slice(0, 10));
    if (i != null) { dias[i].tokens += l.tokens; dias[i].usd += u; }
    const nomeModelo = l.modelo_nome ?? l.modelo;
    somar(modelos, nomeModelo, nomeModelo, l.tokens, u);
    if (l.departamento_id) {
      const d = nomeDep.get(l.departamento_id);
      const nome = primeiraMaiuscula(d?.nome ?? l.departamento_id);
      somar(porDep, l.departamento_id, l.departamento_id === diretor?.departamento_id && diretor ? `${nome} (${diretor.nome})` : nome, l.tokens, u);
    }
    if (l.membro_id && l.tokens > 0) {
      const m = modeloPessoa.get(l.membro_id) ?? new Map<string, number>();
      m.set(nomeModelo, (m.get(nomeModelo) ?? 0) + l.tokens);
      modeloPessoa.set(l.membro_id, m);
    }
  }

  const consumo = consumoPorMembro(linhas, execs);
  const pessoas: Pessoa[] = ags.map((a) => {
    const c = consumo.get(a.id) ?? { tokens: 0, usd: 0, tarefas: 0, modelos: new Set<string>() };
    const ordem = [...(modeloPessoa.get(a.id) ?? new Map<string, number>()).entries()].sort((x, y) => y[1] - x[1]).map(([m]) => m);
    return { ...c, agente: a, modelosOrdem: ordem };
  });
  const ids = new Set(gerentes().map((g) => g.agente));
  const ordenar = (ps: Pessoa[]) => [...ps].sort((a, b) => b.tokens - a.tokens || a.agente.nome.localeCompare(b.agente.nome, "pt-BR"));
  // ajudantes do Atlas (general-purpose, Explore…) que rodaram na janela: a nota da tabela diz quem soma no Atlas
  const ajudantes = [...new Set(execs.filter((e) => e.membro_id === diretor?.id && e.tipo === "subagente" && e.tarefa && e.agente_tipo).map((e) => e.agente_tipo!))];

  return {
    janela: j,
    total: { tokens, usd, cacheLido },
    dias,
    modelos: [...modelos.values()].sort((a, b) => b.tokens - a.tokens),
    departamentos: [...porDep.values()].sort((a, b) => b.tokens - a.tokens),
    deps: deps as Departamento[],
    diretor,
    agentes: ags,
    pessoas,
    gerentes: ordenar(pessoas.filter((p) => p.agente.papel === "diretor" || ids.has(p.agente.id))),
    ranking: ordenar(pessoas.filter((p) => p.tokens > 0)),
    trabalharam: pessoas.filter((p) => p.tokens > 0).length,
    ajudantes,
  };
});

export type LeituraTokens = Awaited<ReturnType<typeof lerTokens>>;
