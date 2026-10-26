import "server-only";
import { createClient } from "@supabase/supabase-js";
import { COMO_LIGAR } from "./comandos";

// Só no servidor: o banco do painel é um espelho dos arquivos do projeto (painel/sync/sincronizar.py).
const url = process.env.SUPABASE_URL;
const chave = process.env.SUPABASE_SERVICE_ROLE_KEY;
if (!url || !chave) {
  throw new Error("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY em falta (painel/web/.env.local)");
}
const db = createClient(url, chave, { auth: { persistSession: false } });

export type Departamento = { id: string; nome: string; ordem: number; descricao: string; gerente_id: string | null };
export type Agente = {
  id: string; nome: string; cargo: string; departamento_id: string;
  papel: "diretor" | "portao" | "construtor" | "analista";
  resumo: string; personalidade: string | null; descricao: string | null; modelo: string | null;
  ferramentas: string[]; skills: string[]; comandos: string[];
  fiscalizado_por: string | null; fiscaliza: string[]; retrato: string | null; arquivo: string | null;
};
export type Video = {
  slug: string; tema: string | null; pilar: string | null; estrutura: string | null; cta: string | null;
  estado: string | null; atualizado: string | null;
  historico: { estado?: string; em?: string; data?: string; nota?: string }[];
  // fase (sincronizar.py, 23/10): gravação em brutos/principal/ e pacote com QA PASS em 05-render-pronto/
  gravado: boolean; gravacao_arquivos: number; gravacao_bytes: number; gravacao_ultima: string | null;
  gravacao_chegou: string | null; gravacao_data_suspeita: boolean; pronto: boolean;
  // roteiro (sincronizar.py, 24/10: roteiro.json); cta_palavra NULL com roteiro = CTA sem palavra (seguir)
  tem_roteiro: boolean; roteiro_versao: number | null; cta_palavra: string | null; roteiro_extras: number | null;
  gravacao_prevista: string | null;
};
/** Produção · Roteiros (view videos_producao): o roteiro e o que a Biblioteca já conta (cenas extras, PDF). */
export type VideoProducao = { slug: string; extras_arquivos: number; pdf: boolean; pdf_caminho: string | null };
/** Prontos (05-render-pronto/<slug>/pacote.json). */
export type Pronto = { slug: string; video_slug: string; qa: string | null; duracao: number | null; criado_em: string | null; cta_palavra: string | null };
/** Vagas semanais do _controle/calendario.md (dia ISO 1 = segunda … 7 = domingo; hora local no fuso). */
export type VagaCalendario = { dia_semana: number; dia: string; hora: string; fuso: string };
export type StatusPortao = "aprovado" | "vencido" | "bloqueado" | "escalado" | "pendente" | "nao_se_aplica";
export type PortaoEstado = {
  alvo: string; slug: string; portao: string; agente: string; status: StatusPortao; motivos: string[]; volta: number;
};
export type Veredicto = {
  alvo: string; ordem: number; slug: string; portao: string; agente: string; resultado: string; impressao: string; em: string;
  volta: number; s0: number; s1: number; s2: number; relatorio: string | null; nota: string | null;
};
export type ItemFila = {
  slug: string; publicar_em: string | null; plataformas: string[]; estado: string | null; trial: string | null;
  palavra: string | null; legado: boolean; confirmar: boolean | null;
  // PI39 (23/10): de onde o post veio, se o pacote tem selo e o que o conferir_pacote do publicar.py acusa ([] = sai)
  origem: string | null; selado: boolean; erros_gauntlet: string[]; video_slug: string | null;
};
export type Publicacao = {
  slug: string; publicado_em: string | null; tema: string | null; pilar: string | null; palavra: string | null;
  duracao_s: number | null; trial: string | null; permalink_instagram: string | null; permalink_facebook: string | null;
  video_slug: string | null; plataformas: string[] | null; estado: string | null;
};
/** Trava escrita à mão ("não publicar"), de _controle/nao-publicar.json. */
export type NaoPublicar = { slug: string; video_slug: string; motivo: string; desde: string };
/** Consumo de IA por dia, modelo e pessoa (registros do Claude Code, view consumo_diario). */
export type ConsumoDia = {
  dia: string; modelo: string; modelo_nome: string | null; tipo: string | null; agente_tipo: string | null;
  membro_id: string | null; departamento_id: string | null; execucoes: number; respostas: number; tokens: number;
  usd: number | null;
  /** tokens lidos do cache: fora do total de tokens (custo baixo, mostrado à parte) */
  cache_lido: number;
};
/** Consumo de UMA execução num dia e num modelo (view consumo), com o vídeo citado no 1.º pedido do subagente. */
export type ConsumoExecucao = {
  arquivo: string; dia: string; modelo: string; modelo_nome: string | null; membro_id: string | null;
  departamento_id: string | null; video_slug: string | null; tokens: number; usd: number | null;
};
/** Uma execução (sessão ou subagente) com o custo somado (view execucoes_custo). */
export type ExecucaoCusto = {
  arquivo: string; tipo: string | null; agente_tipo: string | null; membro_id: string | null; departamento_id: string | null;
  video_slug: string | null; inicio: string | null; fim: string | null; tarefa: boolean; respostas: number; tokens: number;
  usd: number | null;
};
export type Metrica = {
  slug: string; lido_em: string; dias: number | null; views: number | null; alcance: number | null;
  tempo_medio_s: number | null; pct_assistido: number | null; curtidas: number | null; comentarios: number | null;
  salvamentos: number | null; compartilhamentos: number | null; plays_fb: number | null;
  tempo_medio_fb_s: number | null; palavra_comentarios: number | null; palavra_directs: number | null; suspeito: boolean;
};
export type Snapshot = {
  lido_em: string; seguidores: number | null; seguindo: number | null; posts: number | null; janela_dias: number | null;
  alcance: number | null; views: number | null; contas_engajadas: number | null; interacoes: number | null;
  visitas_perfil: number | null; alcance_seguidores: number | null; alcance_nao_seguidores: number | null;
  fb_seguidores: number | null;
};
export type Demografia = { lido_em: string; publico: string; dimensao: string; chave: string; valor: number };

/** Falha de conexão (Supabase do painel desligado, Docker parado) × outro erro do banco. */
function foraDoAr(e: { message?: string; details?: string; code?: string }): boolean {
  const texto = `${e.message ?? ""} ${e.details ?? ""}`;
  return /fetch failed|ECONNREFUSED|ECONNRESET|ENOTFOUND|socket|network|upstream|no available server/i.test(texto)
    || /^5\d\d$/.test(e.code ?? "");
}

export { COMO_LIGAR, COMO_SINCRONIZAR } from "./comandos";

/**
 * Linhas por pedido. O banco do painel devolve NO MÁXIMO `max_rows` linhas por pedido (1.000, em
 * painel/supabase/config.toml) e corta o resto calado: HTTP 200, sem erro. Por isso nenhuma leitura confia num pedido
 * só — `todos()` pergunta quantas linhas a tabela tem e pede página por página até ter todas.
 */
const POR_PAGINA = 1000;

function erroDoBanco(tabela: string, e: { message?: string; details?: string; code?: string }): Error {
  if (foraDoAr(e)) return new Error(`o banco do painel está fora do ar (${tabela}) — ligue com: ${COMO_LIGAR}`);
  return new Error(`${tabela}: ${e.message ?? "erro do banco"}`);
}

/**
 * Todas as linhas de uma tabela (ou só as que batem com `filtro`), na ordem pedida.
 *
 * - `ordem` tem de terminar na chave primária da tabela: paginar sem uma ordem única repete ou pula linhas.
 * - Cada página vem com a contagem exata do banco (`count: "exact"`) e o pedido seguinte começa onde a leitura parou,
 *   então serve para qualquer `max_rows`, mesmo menor que `POR_PAGINA`.
 * - Se a contagem muda no meio (o sincronizador apaga e regrava a tabela inteira), lê tudo de novo uma vez.
 * - Se mesmo assim vierem menos linhas do que o banco diz ter, LANÇA: a página cai na tela de erro, em vez de mostrar
 *   um número que falta pedaço.
 */
type Filtro = { coluna: string; valor: string; op?: "eq" | "gte" };

async function todos<T>(tabela: string, ordem: string[], filtro?: Filtro): Promise<T[]> {
  for (let tentativa = 1; tentativa <= 2; tentativa++) {
    const linhas: T[] = [];
    let total: number | null = null;
    let mudou = false;
    // O Next guarda a resposta de um fetch GET idêntico dentro do mesmo render (request memoization do React): sem um
    // `signal` próprio, a releitura receberia as MESMAS respostas da 1.ª tentativa, sem ir ao banco.
    const releitura = tentativa > 1 ? new AbortController().signal : undefined;
    while (total === null || linhas.length < total) {
      let q = db.from(tabela).select("*", { count: "exact" });
      if (filtro) q = filtro.op === "gte" ? q.gte(filtro.coluna, filtro.valor) : q.eq(filtro.coluna, filtro.valor);
      for (const c of ordem) q = q.order(c, { ascending: true });
      let pedido = q.range(linhas.length, linhas.length + POR_PAGINA - 1);
      if (releitura) pedido = pedido.abortSignal(releitura);
      const { data, error, count } = await pedido;
      if (error) {
        // PGRST103 = pedi um pedaço além do fim: a tabela encolheu entre um pedido e outro (sincronização no meio)
        if (error.code === "PGRST103" && total !== null) { mudou = true; break; }
        throw erroDoBanco(tabela, error);
      }
      if (count == null) throw new Error(`${tabela}: o banco não disse quantas linhas tem; não dá para saber se veio tudo`);
      if (total !== null && count !== total) { mudou = true; break; }
      total = count;
      if (!data || data.length === 0) break; // o banco diz que há mais linhas, mas não as devolve
      linhas.push(...(data as T[]));
    }
    if (mudou) continue;
    if (linhas.length !== total) {
      throw new Error(`${tabela}: o banco tem ${total} linhas e devolveu ${linhas.length} — a página não mostra dados pela metade`);
    }
    return linhas;
  }
  throw new Error(`${tabela}: a tabela mudou duas vezes durante a leitura (o sincronizador estava rodando) — tente de novo`);
}

// Ordem = a da tela + a chave primária no fim (painel/supabase/migrations/20261022190000_inicial.sql).
export const departamentos = () => todos<Departamento>("departamentos", ["ordem", "id"]);
export const agentes = () => todos<Agente>("agentes", ["nome", "id"]);
export const videos = () => todos<Video>("videos", ["slug"]);
export const portoesEstado = () => todos<PortaoEstado>("portoes_estado", ["alvo", "portao"]);
/** Veredictos em ordem de tempo. A paginação vai pela chave da tabela (alvo, ordem; PD24) e a ordem de tempo é feita aqui. */
// ── Biblioteca = acervo de estilos (migrações 20261024215907 e 20261024233631): espelho de arquivos do projeto ───────
export type Look = {
  id: string; ordem: number; tipo: "referencia" | "base" | "look"; nome: string | null; descricao: string | null; papel: "em_uso" | "alternativa" | "arquivado" | null;
  aprovada: boolean | null; criado_em: string | null; cube: string | null; rosto_ire: number | null; rosto_ire_em: string | null;
  previa: string | null;
};
export type CapaEstilo = { id: string; ordem: number; nome: string; descricao: string; em_uso: boolean };
export type CapaExemplo = { estilo_id: string; ordem: number; slug: string; pasta: string | null; caminho: string | null; video_slug: string | null };
export type LegendaEstilo = { id: string; ordem: number; nome: string; descricao: string; em_uso: boolean };
export type Fonte = { familia: string; ordem: number; uso: string; reserva: boolean };
export type Ferramenta = { nome: string; ordem: number; tipo: string; descricao: string; versao: string | null };
export type SistemaModelo = { modelo: string; modelo_nome: string | null; tokens: number; pct_tokens: number | null; descricao: string | null };
export type Animacao = { id: string; video_slug: string; codigo: string; titulo: string | null; modo: "full" | "split" | "card" | null; duracao_s: number | null; renderizada: boolean };
export type SistemaContagens = { agentes: number; habilidades: number; comandos: number };
/** Só o Mac (decisão de 25/10: o painel não mostra o HD externo; os campos hd_* não são lidos). */
export type Armazenamento = { gravacoes_mac_bytes: number; material_mac_bytes: number; material_mac_arquivos: number; mac_bytes: number };
export const looks = async () => (await todos<Look>("looks", ["ordem"])).map((l) => ({ ...l, rosto_ire: l.rosto_ire == null ? null : Number(l.rosto_ire) }));
export const capaEstilos = () => todos<CapaEstilo>("capa_estilos", ["ordem"]);
export const capaExemplos = () => todos<CapaExemplo>("capa_estilos_exemplos", ["estilo_id", "ordem"]);
export const legendaEstilos = () => todos<LegendaEstilo>("legenda_estilos", ["ordem"]);
export const fontes = () => todos<Fonte>("fontes", ["ordem"]);
export const ferramentas = () => todos<Ferramenta>("sistema_ferramentas", ["ordem"]);
export const sistemaModelos = async () =>
  (await todos<SistemaModelo>("sistema_modelos", ["modelo"])).map((m) => ({ ...m, tokens: Number(m.tokens), pct_tokens: m.pct_tokens == null ? null : Number(m.pct_tokens) }));
export const animacoes = async () => (await todos<Animacao>("animacoes", ["id"])).map((a) => ({ ...a, duracao_s: a.duracao_s == null ? null : Number(a.duracao_s) }));
export const sistemaContagens = async () => (await todos<SistemaContagens>("sistema_contagens", ["unico"]))[0] ?? null;
export async function armazenamento(): Promise<Armazenamento | null> {
  const { data, error } = await db.from("armazenamento").select("gravacoes_mac_bytes, material_mac_bytes, material_mac_arquivos, mac_bytes").maybeSingle();
  if (error) throw erroDoBanco("armazenamento", error);
  if (!data) return null;
  const n = (v: unknown) => Number(v ?? 0);
  return { gravacoes_mac_bytes: n(data.gravacoes_mac_bytes), material_mac_bytes: n(data.material_mac_bytes),
    material_mac_arquivos: n(data.material_mac_arquivos), mac_bytes: n(data.mac_bytes) };
}
/** A prévia de UM look (para a rota que entrega a imagem); null = sem prévia. */
export async function previaDoLook(id: string): Promise<string | null> {
  const { data, error } = await db.from("looks").select("previa").eq("id", id).maybeSingle();
  if (error) throw erroDoBanco("looks", error);
  return (data?.previa as string | null | undefined) ?? null;
}

/** O modelo que RODOU, por agente × modelo nos 30 dias UTC (view modelo_por_agente; modelo NULL = não rodou). */
export type ModeloPorAgente = { agente_id: string; modelo: string | null; modelo_nome: string | null; tokens: number; pct_tokens: number | null };
export const modeloPorAgente = async () =>
  (await todos<ModeloPorAgente>("modelo_por_agente", ["agente_id", "modelo"]))
    .map((m) => ({ ...m, tokens: Number(m.tokens), pct_tokens: m.pct_tokens == null ? null : Number(m.pct_tokens) }));
export const videosProducao = async () =>
  (await todos<VideoProducao>("videos_producao", ["slug"])).map((v) => ({ ...v, extras_arquivos: Number(v.extras_arquivos) }));
export const prontos = async () =>
  (await todos<Pronto>("prontos", ["slug"])).map((p) => ({ ...p, duracao: p.duracao == null ? null : Number(p.duracao) }));
export const calendarioVagas = () => todos<VagaCalendario>("calendario_vagas", ["dia_semana", "hora"]);
export const veredictos = async () =>
  (await todos<Veredicto>("veredictos", ["alvo", "ordem"]))
    .sort((a, b) => Date.parse(a.em) - Date.parse(b.em) || a.alvo.localeCompare(b.alvo) || a.ordem - b.ordem);
export const fila = () => todos<ItemFila>("fila", ["publicar_em", "slug"]);
export const publicacoes = () => todos<Publicacao>("publicacoes", ["publicado_em", "slug"]);
export const metricas = () => todos<Metrica>("metricas", ["lido_em", "slug"]);
export const snapshots = () => todos<Snapshot>("perfil_snapshots", ["lido_em"]);
export const naoPublicar = () => todos<NaoPublicar>("nao_publicar", ["slug"]);
/** Preço de tabela da API por modelo (US$ por milhão de tokens), com o nome e a versão ("Opus 5.5"). */
export type PrecoModelo = { modelo: string; nome: string; entrada: number; saida: number; cache_lido: number; cache_gravado_5m: number; cache_gravado_1h: number };
export const precos = async () =>
  (await todos<PrecoModelo>("precos_modelo", ["modelo"])).map((p) => ({
    ...p, entrada: Number(p.entrada), saida: Number(p.saida), cache_lido: Number(p.cache_lido),
    cache_gravado_5m: Number(p.cache_gravado_5m), cache_gravado_1h: Number(p.cache_gravado_1h),
  }));
/**
 * Consumo por dia desde `desde` (AAAA-MM-DD, inclusive). A view não tem chave: a ordem usa todas as colunas do
 * agrupamento, que juntas são únicas, para a paginação não repetir nem pular linha.
 */
export const consumoDesde = async (desde: string) =>
  (await todos<ConsumoDia>("consumo_diario", ["dia", "modelo", "tipo", "agente_tipo", "membro_id", "departamento_id"],
    { coluna: "dia", valor: desde, op: "gte" }))
    .map((c) => ({ ...c, tokens: Number(c.tokens), cache_lido: Number(c.cache_lido ?? 0), usd: c.usd == null ? null : Number(c.usd) }));
/**
 * Consumo por execução, dia e modelo desde `desde` (view consumo; a chave é a de uso_execucao: arquivo, dia, modelo).
 * Serve ao "custo por vídeo" (consumo_diario não tem o vídeo).
 */
export const consumoExecucoesDesde = async (desde: string) =>
  (await todos<ConsumoExecucao>("consumo", ["arquivo", "dia", "modelo"], { coluna: "dia", valor: desde, op: "gte" }))
    .map((c) => ({ ...c, tokens: Number(c.tokens), usd: c.usd == null ? null : Number(c.usd) }));
/** Execuções que começaram desde `desde` (ISO), com o custo. */
export const execucoesDesde = async (desde: string) =>
  (await todos<ExecucaoCusto>("execucoes_custo", ["inicio", "arquivo"], { coluna: "inicio", valor: desde, op: "gte" }))
    .map((e) => ({ ...e, tokens: Number(e.tokens), usd: e.usd == null ? null : Number(e.usd) }));
/**
 * Público de UMA foto do perfil (a tela só mostra a mais nova). Nunca a tabela inteira: cada foto soma ~180 linhas,
 * e ler todas as fotos para usar uma só era o que estourava o limite do banco.
 */
export const demografia = (lido_em: string) =>
  todos<Demografia>("perfil_demografia", ["publico", "dimensao", "chave"], { coluna: "lido_em", valor: lido_em });

export type EstadoBanco =
  | { estado: "ok"; em: string }
  | { estado: "nunca" } // o banco responde, mas o sincronizador nunca rodou nele
  | { estado: "fora" } // o banco não responde
  | { estado: "erro"; detalhe: string }; // responde com erro (ex.: tabela em falta = migração não aplicada)

/** Última sincronização, distinguindo "banco fora do ar" de "nunca sincronizado". Nunca lança. */
export async function estadoDoBanco(): Promise<EstadoBanco> {
  try {
    const { data, error } = await db.from("sincronizacoes").select("em").order("em", { ascending: false }).limit(1);
    if (error) return foraDoAr(error) ? { estado: "fora" } : { estado: "erro", detalhe: error.message };
    const em = data?.[0]?.em as string | undefined;
    return em ? { estado: "ok", em } : { estado: "nunca" };
  } catch {
    return { estado: "fora" };
  }
}

export async function agente(id: string): Promise<Agente | null> {
  const { data, error } = await db.from("agentes").select("*").eq("id", id).maybeSingle();
  // erro de banco nunca vira "esta pessoa não existe" (404): vai para a tela de erro com o que fazer
  if (error) {
    if (foraDoAr(error)) throw new Error(`o banco do painel está fora do ar (agentes) — ligue com: ${COMO_LIGAR}`);
    throw new Error(`agentes: ${error.message}`);
  }
  return (data as Agente) ?? null;
}

/** Leitura de um vídeo para a tela: a mais recente NÃO suspeita e, se houver, as suspeitas mais novas que ela. */
export type LeituraConfiavel = {
  m: Metrica | undefined; // a usada em tabela, gráfico e média (undefined = só há leituras suspeitas)
  descartadas: Metrica[]; // leituras suspeitas mais recentes que `m`, da mais nova para a mais velha
};

/**
 * A última leitura confiável de cada vídeo publicado. Leitura com `suspeito = true` (número impossível vindo da API,
 * ex.: tempo médio maior que a duração) nunca entra em gráfico nem em média: fica a anterior, com a data dela, e a
 * descartada é avisada na linha.
 */
export function leiturasConfiaveis(ms: Metrica[]): Map<string, LeituraConfiavel> {
  const porSlug = new Map<string, Metrica[]>();
  for (const x of ms) porSlug.set(x.slug, [...(porSlug.get(x.slug) ?? []), x]);
  const out = new Map<string, LeituraConfiavel>();
  for (const [slug, lista] of porSlug) {
    const ordem = [...lista].sort((a, b) => (a.lido_em < b.lido_em ? 1 : a.lido_em > b.lido_em ? -1 : 0));
    const i = ordem.findIndex((x) => !x.suspeito);
    out.set(slug, { m: i >= 0 ? ordem[i] : undefined, descartadas: i >= 0 ? ordem.slice(0, i) : ordem });
  }
  return out;
}
