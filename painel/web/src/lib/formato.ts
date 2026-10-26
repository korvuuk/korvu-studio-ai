const nf = new Intl.NumberFormat("pt-BR");
const regioes = new Intl.DisplayNames(["pt-BR"], { type: "region" });

export const num = (n: number | null | undefined) => (n == null ? "—" : nf.format(n));
export const pct = (n: number | null | undefined, casas = 1) =>
  n == null ? "—" : `${n.toLocaleString("pt-BR", { maximumFractionDigits: casas })}%`;
export const seg = (n: number | null | undefined) =>
  n == null ? "—" : `${Number(n).toLocaleString("pt-BR", { maximumFractionDigits: 1 })} s`;

// sempre uma casa no K e no M ("2,0M", "954,4K"), como as maquetes de 23/10
const umaCasa = (x: number) => x.toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });

/**
 * Número compacto do KPI (design-system.md §1): até 9.999 o número inteiro com ponto ("3.631"); de 10.000 em diante,
 * uma casa com K ou M ("482,6K", "12,8M"). A unidade vem separada para o KPI desenhá-la em <small>. Na dica e na
 * tabela vai sempre o número exato (`num`).
 */
export function compactoPartes(n: number): { valor: string; unidade: "" | "K" | "M" } {
  const abs = Math.abs(n);
  if (abs >= 999_950) return { valor: umaCasa(n / 1_000_000), unidade: "M" }; // 999.950 arredondaria para "1.000K"
  if (abs >= 10_000) return { valor: umaCasa(n / 1_000), unidade: "K" };
  return { valor: nf.format(n), unidade: "" };
}

export function compacto(n: number): string {
  const { valor, unidade } = compactoPartes(n);
  return `${valor}${unidade}`;
}

/**
 * Custo de IA em US$, a moeda da tabela da Anthropic, sem câmbio (decisão do Carlos de 24/10, que substitui a das libras):
 * "US$ 12,40", "US$ 1.292". Abaixo de US$ 1.000 com centavos; dali para cima, inteiro. `usdPartes` serve ao KPI (o
 * "US$" vai em <small class="k-prefixo">).
 */
export function usdPartes(valor: number, casas?: number): { simbolo: "US$"; valor: string } {
  const c = casas ?? (Math.abs(valor) < 1000 ? 2 : 0);
  return { simbolo: "US$", valor: valor.toLocaleString("pt-BR", { minimumFractionDigits: c, maximumFractionDigits: c }) };
}
/** "US$ 12,40" — espaço inseparável entre o símbolo e o valor (moeda e número nunca se separam). */
export const usd = (valor: number | null | undefined, casas?: number) =>
  valor == null ? "—" : `US$\u00a0${usdPartes(valor, casas).valor}`;
/** "US$ 532" — inteiro por padrão (totais da nota). */
export const dolares = (valor: number | null | undefined, casas = 0) => usd(valor, casas);

const UF: Record<string, string> = {
  acre: "AC", alagoas: "AL", amapa: "AP", amazonas: "AM", bahia: "BA", ceara: "CE", "distrito federal": "DF",
  "federal district": "DF", "espirito santo": "ES", goias: "GO", maranhao: "MA", "mato grosso": "MT",
  "mato grosso do sul": "MS", "minas gerais": "MG", para: "PA", paraiba: "PB", parana: "PR", pernambuco: "PE",
  piaui: "PI", "rio de janeiro": "RJ", "rio grande do norte": "RN", "rio grande do sul": "RS", rondonia: "RO",
  roraima: "RR", "santa catarina": "SC", "sao paulo": "SP", sergipe: "SE", tocantins: "TO",
};
const semAcento = (t: string) => t.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();

/**
 * Nome curto de cidade para rótulo de gráfico, sem reticências: "Juiz de Fora, Minas Gerais" → "Juiz de Fora · MG",
 * "London, England" → "London · England", "Luanda, Luanda Province" → "Luanda". O nome inteiro fica na dica.
 */
export function cidade(chave: string): string {
  const [nome, ...resto] = chave.split(",").map((t) => t.trim());
  if (!resto.length) return nome;
  const inteira = resto.join(", ").replace(/\s*\((state|estado)\)$/i, "").trim();
  const regiao = inteira.replace(/\s+(province|district|region|governorate|county|prefecture)$/i, "").trim();
  const uf = UF[semAcento(inteira)] ?? UF[semAcento(regiao)];
  if (uf) return `${nome} · ${uf}`;
  if (!regiao || semAcento(regiao) === semAcento(nome)) return nome;
  return `${nome} · ${regiao}`;
}

export function pais(codigo: string): string {
  try {
    return regioes.of(codigo) ?? codigo;
  } catch {
    return codigo;
  }
}

// Datas e horas no fuso do estúdio, no formato do design system (§1): "22 out", "22 out, 18:30".
const TZ = "Europe/London";
const MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];
const partesData = new Intl.DateTimeFormat("pt-BR", {
  timeZone: TZ, day: "numeric", month: "numeric", year: "numeric", hour: "2-digit", minute: "2-digit", hourCycle: "h23",
});
function emLondres(iso: string) {
  const p = Object.fromEntries(partesData.formatToParts(new Date(iso)).map((x) => [x.type, x.value]));
  return { dia: String(Number(p.day)), mes: MESES[Number(p.month) - 1], hora: `${p.hour}:${p.minute}` }; // "1 nov", nunca "01 nov"
}
export const data = (iso: string | null) => {
  if (!iso) return "—";
  const d = emLondres(iso);
  return `${d.dia} ${d.mes}`;
};
export const dataHora = (iso: string | null) => {
  if (!iso) return "—";
  const d = emLondres(iso);
  return `${d.dia} ${d.mes}, ${d.hora}`;
};
/** "19:00" no horário de Londres (o mesmo do publicar.py). */
export const hora = (iso: string | null) => (iso ? emLondres(iso).hora : "—");

const SEMANA = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"];
const SEMANA_LONGA = ["Domingo", "Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado"];
const partesDia = new Intl.DateTimeFormat("en-CA", { timeZone: TZ, year: "numeric", month: "2-digit", day: "2-digit" });
/** "2026-10-24": o dia de calendário em Londres (para comparar dias sem cair no fuso do servidor). */
export const diaEmLondres = (iso: string | Date) => partesDia.format(typeof iso === "string" ? new Date(iso) : iso);
const diaDaSemana = (dia: string) => new Date(`${dia}T12:00:00Z`).getUTCDay();
/** "Sáb 24 out" (a partir de um dia AAAA-MM-DD ou de um instante, no horário de Londres). */
export const diaCurto = (iso: string) => {
  const dia = /^\d{4}-\d{2}-\d{2}$/.test(iso) ? iso : diaEmLondres(iso);
  return `${SEMANA[diaDaSemana(dia)]} ${Number(dia.slice(8, 10))} ${MESES[Number(dia.slice(5, 7)) - 1]}`;
};
/** "Sexta-feira, 23 out 2026" — a data de hoje no topo da Visão geral. */
export const diaLongo = (agora: Date) => {
  const dia = diaEmLondres(agora);
  return `${SEMANA_LONGA[diaDaSemana(dia)]}, ${Number(dia.slice(8, 10))} ${MESES[Number(dia.slice(5, 7)) - 1]} ${dia.slice(0, 4)}`;
};
/** Dias de calendário (em Londres) de `de` até `ate`: 1 = amanhã, -3 = há 3 dias. */
export const diasEntre = (de: string | Date, ate: string | Date) => {
  const a = Date.parse(`${typeof de === "string" && /^\d{4}-\d{2}-\d{2}$/.test(de) ? de : diaEmLondres(de)}T00:00:00Z`);
  const b = Date.parse(`${typeof ate === "string" && /^\d{4}-\d{2}-\d{2}$/.test(ate) ? ate : diaEmLondres(ate)}T00:00:00Z`);
  return Math.round((b - a) / 86_400_000);
};
/** "hoje", "amanhã", "em 4 dias", "ontem", "há 36 dias". */
export const relativo = (dias: number) =>
  dias === 0 ? "hoje" : dias === 1 ? "amanhã" : dias === -1 ? "ontem" : dias > 0 ? `em ${dias} dias` : `há ${-dias} dias`;
/** A data prevista de gravação vem no slug (CLAUDE.md: AAAA-MM-DD-palavra). */
export const dataDoSlug = (slug: string) => /^(\d{4}-\d{2}-\d{2})-/.exec(slug)?.[1] ?? null;

/** "2026-10-23-livro-chatgpt-l01c-a" → "livro chatgpt l01c a" */
export const titulo = (slug: string) => slug.replace(/^\d{4}-\d{2}-\d{2}-/, "").replace(/-/g, " ");

/**
 * Título de um vídeo para a tela. O banco não tem um título limpo (handoff.md §8): `videos.tema` traz o título e,
 * depois de " — ", notas internas. Vale o que vem antes do travessão; sem tema, o slug legível.
 */
export const tituloVideo = (slug: string, tema: string | null | undefined) =>
  tema?.split(" — ")[0]?.trim() || titulo(slug);

/** Só a primeira letra maiúscula (design-system.md §1): o banco guarda cargo e departamento em minúsculas. */
export const primeiraMaiuscula = (t: string | null | undefined) => (t ? t.charAt(0).toLocaleUpperCase("pt-BR") + t.slice(1) : "");

/** Iniciais do avatar (design-system.md §11.7): "Marina Costa" → "MC"; nome de uma palavra só, as duas primeiras letras. */
export function iniciais(nome: string): string {
  const palavras = nome.trim().split(/\s+/).filter(Boolean);
  if (palavras.length === 0) return "?";
  if (palavras.length === 1) return palavras[0].slice(0, 2).toUpperCase();
  return (palavras[0][0] + palavras[palavras.length - 1][0]).toUpperCase();
}

/**
 * Modelo de IA sempre com a versão (decisão do Carlos, 23/10: "Opus 5.5", nunca só "opus"). Os agentes guardam o apelido
 * (`model: opus` em .claude/agents/*.md); a versão é a que os registros das sessões do Claude Code deste projeto
 * mostram em 23/10 (`claude-opus-5-5`, `claude-sonnet-5-5`). Mudou o modelo do Claude Code, muda aqui.
 * Apelido sem versão conhecida aparece como veio, sem inventar número.
 */
export const MODELOS: Record<string, string> = { opus: "Opus 5.5", sonnet: "Sonnet 5.5", fable: "Fable 5.1" };
export const nomeModelo = (modelo: string) => MODELOS[modelo.trim().toLowerCase()] ?? modelo;

export const PORTOES = ["pauta", "roteiro", "imagem", "corte"] as const;
export const NOME_PORTAO: Record<string, string> = {
  pauta: "pauta", roteiro: "roteiro", imagem: "imagem", corte: "corte", publicacao: "publicação",
  design: "design", interface: "interface", dados: "dados",
};
/** Portão → agente que o audita (docs/gauntlet.md). Um agente pode auditar mais de um: o portao-interface faz
 *  design e interface do painel. */
export const AGENTE_DO_PORTAO: Record<string, string> = {
  pauta: "portao-pauta", roteiro: "revisor-de-roteiro", imagem: "portao-imagem", corte: "revisor-de-video",
  publicacao: "portao-publicacao", design: "portao-interface", interface: "portao-interface", dados: "portao-dados",
};

/** Os gerentes, cada um UMA vez, com os portões que auditam (na ordem do GAUNTLET). */
export function gerentes(): { agente: string; portoes: string[] }[] {
  const out = new Map<string, string[]>();
  for (const [p, ag] of Object.entries(AGENTE_DO_PORTAO)) out.set(ag, [...(out.get(ag) ?? []), p]);
  return [...out.entries()].map(([agente, portoes]) => ({ agente, portoes }));
}

/** Os portões que um agente audita ([] se não é portão). */
export const portoesDoAgente = (id: string) =>
  Object.entries(AGENTE_DO_PORTAO).filter(([, ag]) => ag === id).map(([p]) => p);

/** "design e interface" */
export const listaPortoes = (ps: string[]) => {
  const nomes = ps.map((p) => NOME_PORTAO[p] ?? p);
  return nomes.length > 1 ? `${nomes.slice(0, -1).join(", ")} e ${nomes.at(-1)}` : (nomes[0] ?? "");
};

// Estados do pipeline na ordem do CLAUDE.md.
export const ESTADOS = [
  "roteiro", "gravacao", "edicao", "edl_aprovada", "revisao", "cor", "legendas", "capa", "qa", "pronto", "agendado",
  "publicado",
];

/** "edicao (refazendo a L03)" → "edicao": o status.json às vezes traz uma nota entre parênteses. */
export const estadoLimpo = (estado: string | null | undefined) => (estado ?? "").replace(/\s*\(.*\)$/, "").trim();

export const NOME_ESTADO: Record<string, string> = {
  roteiro: "Roteiro", gravacao: "Gravação", edicao: "Edição", edl_aprovada: "EDL aprovada", revisao: "Revisão",
  cor: "Cor", legendas: "Legendas", capa: "Capa", qa: "QA", pronto: "Pronto", agendado: "Agendado", publicado: "Publicado",
};

/** As 5 etapas do componente de progresso (design-system.md §11.10). */
export const ETAPAS = ["Roteiro", "Gravação", "Edição", "Revisão", "Publicar"] as const;
const ETAPA_DO_ESTADO: Record<string, number> = {
  roteiro: 0, gravacao: 1, edicao: 2, edl_aprovada: 2, revisao: 3, cor: 3, legendas: 3, capa: 3, qa: 3, pronto: 4,
  agendado: 4, publicado: 5,
};
/** Os 12 estados nas 5 etapas: índice da etapa atual (0–4), 5 = todas feitas, null = estado que o painel não conhece. */
export const etapaDoEstado = (estado: string | null | undefined): number | null =>
  ETAPA_DO_ESTADO[estadoLimpo(estado)] ?? null;

/** "0:49", "2:48" — duração de um vídeo em minutos:segundos. */
export const minSeg = (s: number | null | undefined) => {
  if (s == null) return "—";
  const t = Math.round(Number(s));
  return `${Math.floor(t / 60)}:${String(t % 60).padStart(2, "0")}`;
};
/** "PROMPT" é palavra-chave; "seguir" (CTA de seguir) não é: só palavra em maiúsculas conta. */
export const palavraDoCta = (cta: string | null | undefined) => (cta && /^[A-ZÀ-Ú0-9]+$/.test(cta.trim()) ? cta.trim() : null);

/** "16 → 22 out" (mesmo mês) ou "28 set → 3 out": dois instantes no horário de Londres. */
export const intervaloCurto = (de: string, ate: string) => {
  const a = data(de).split(" ");
  const b = data(ate);
  return a[1] === b.split(" ")[1] ? `${a[0]} → ${b}` : `${data(de)} → ${b}`;
};
/** "5,9%" — sempre uma casa (porcentagens de tabela: % assistido, engajamento). */
export const pct1 = (n: number) => `${n.toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 })}%`;
/** "1,8 bilhão", "37,5 milhões" — número grande por extenso, para frases ("+ 1,8 bilhão lidos do cache"). */
export const porExtenso = (n: number) => {
  const um = (x: number) => x.toLocaleString("pt-BR", { maximumFractionDigits: 1 });
  if (Math.abs(n) >= 999_950_000) { const v = n / 1e9; return `${um(v)} ${Math.abs(v) < 2 ? "bilhão" : "bilhões"}`; }
  if (Math.abs(n) >= 999_950) { const v = n / 1e6; return `${um(v)} ${Math.abs(v) < 2 ? "milhão" : "milhões"}`; }
  return num(n);
};

/**
 * Tamanho de arquivo em unidades DECIMAIS, como o Finder (1 GB = 10⁹ bytes; telas/biblioteca.md: uma unidade só):
 * "351 KB", "3,1 MB", "185 MB", "4,65 GB", "216,2 GB". `partes` separa o número da unidade (o número grande do card).
 */
export function bytesPartes(n: number): { valor: string; unidade: "B" | "KB" | "MB" | "GB" } {
  const f = (v: number, casas: number) => v.toLocaleString("pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas });
  if (n < 1e3) return { valor: f(n, 0), unidade: "B" };
  if (n < 999_500) return { valor: f(Math.max(1, Math.round(n / 1e3)), 0), unidade: "KB" }; // 999,5 KB já é "1,0 MB"
  if (n < 999_500_000) { const v = n / 1e6; return { valor: f(v, v < 9.95 ? 1 : 0), unidade: "MB" }; }
  const v = n / 1e9;
  return { valor: f(v, v < 100 ? 2 : 1), unidade: "GB" };
}
export const bytesCurto = (n: number) => { const p = bytesPartes(n); return `${p.valor} ${p.unidade}`; };
