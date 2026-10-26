import "server-only";
import { cache } from "react";
import * as db from "./db";
import { PEDE_ACAO, resumoMotivos } from "./estados";
import { dataDoSlug, diaCurto, diaEmLondres, diasEntre, PORTOES, relativo } from "./formato";

// Produção de conteúdo — as 5 fases e o mapa de estados (design-system.md §15.1). A fase vem da pasta onde o trabalho
// está, que o sincronizador já traduziu para o banco (23/10):
//   Roteiros   → vídeo sem gravação (videos.gravado = false)
//   Gravados   → vídeo gravado que ainda não tem pacote (nem pronto, nem na fila, nem publicado)
//   Prontos    → vídeo com pacote QA PASS (videos.pronto) que ainda não entrou na fila nem saiu
//   Agendados  → cada post da fila (06-publicar/)
//   Publicados → cada post de 07-publicados/ (publicacoes)
// Roteiros, Gravados e Prontos contam vídeos; Agendados e Publicados contam posts.

export type Fase = "roteiros" | "gravados" | "prontos" | "agendados" | "publicados";
export const FASES: { id: Fase; nome: string }[] = [
  { id: "roteiros", nome: "Roteiros" },
  { id: "gravados", nome: "Gravados" },
  { id: "prontos", nome: "Prontos" },
  { id: "agendados", nome: "Agendados" },
  { id: "publicados", nome: "Publicados" },
];

// ── nome curto ─────────────────────────────────────────────────────────────────────────────────────────────────────
// O banco não tem título curto (handoff §8): ele sai do slug sem a data. Perfil (pilar "perfil") é nome de pessoa →
// cada palavra com maiúscula; o resto, só a primeira. Variante do post (r2, a, l01c) vai no fim.
// Grafia fixa de palavras do slug: siglas, acentos e NOMES PRÓPRIOS que o tema não traz (o "Jacob Coxon" do
// 2026-09-17-jacob-coxon é notícia, não perfil, e o tema não escreve o nome). O título curto de verdade é dado do backend
// (handoff.md §8); até lá, nome de pessoa fora do pilar "perfil" entra aqui.
const GRAFIA: Record<string, string> = { chatgpt: "ChatGPT", ia: "IA", negocio: "negócio", l01c: "L01C", coxon: "Coxon" };
const palavra = (p: string, nome: boolean, primeira: boolean) => {
  if (GRAFIA[p]) return GRAFIA[p];
  return nome || primeira ? p.charAt(0).toUpperCase() + p.slice(1) : p;
};
/**
 * A grafia que o próprio tema usa para as palavras do slug, quando elas aparecem juntas e com maiúscula (nome próprio):
 * "fei-fei-li" + "Quem é Fei-Fei Li: …" → "Fei-Fei Li". Sem nome próprio no tema, null (vale a regra do slug).
 */
function grafiaDoTema(palavras: string[], temas: (string | null | undefined)[]): string | null {
  if (!palavras.length) return null;
  const miolo = palavras.map((p) => p.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("[-\\s]?");
  const padrao = new RegExp(`(?<![\\p{L}\\p{N}])${miolo}(?![\\p{L}\\p{N}])`, "iu");
  for (const t of temas) {
    const m = t ? padrao.exec(t) : null;
    if (m && /^\p{Lu}/u.test(m[0])) return m[0];
  }
  return null;
}

export function nomeCurto(slug: string, opcoes: { perfil?: boolean; videoSlug?: string | null; temas?: (string | null | undefined)[] } = {}): string {
  const base = opcoes.videoSlug && slug.startsWith(`${opcoes.videoSlug}-`) ? opcoes.videoSlug : slug;
  const resto = base === slug ? "" : slug.slice(base.length + 1);
  const palavras = base.replace(/^\d{4}-\d{2}-\d{2}-/, "").split("-").filter(Boolean);
  const nome = grafiaDoTema(palavras, opcoes.temas ?? []) ?? palavras.map((p, i) => palavra(p, Boolean(opcoes.perfil), i === 0)).join(" ");
  const variante = resto.split("-").filter(Boolean).map((p) => (/^r\d+$/.test(p) ? p : p.toUpperCase())).join(" ");
  return variante ? `${nome} ${variante}` : nome;
}

// ── leitura ────────────────────────────────────────────────────────────────────────────────────────────────────────

export type VideoFase = db.Video & { fase: "roteiros" | "gravados" | "prontos" | null; nome: string; trava: db.NaoPublicar | null };
export type PostFila = db.ItemFila & { nome: string; video: db.Video | null };
export type PostPublicado = db.Publicacao & { nome: string; video: db.Video | null; leitura: db.Metrica | undefined; descartadas: db.Metrica[] };

export const lerProducao = cache(async () => {
  const [videos, fila, pubs, estados, travas, mets, producao, prontosDb] = await Promise.all([
    db.videos(), db.fila(), db.publicacoes(), db.portoesEstado(), db.naoPublicar(), db.metricas(), db.videosProducao(), db.prontos(),
  ]);
  const roteiroDe = new Map(producao.map((x) => [x.slug, x]));
  const prontoDe = new Map(prontosDb.map((x) => [x.video_slug, x]));
  const porSlug = new Map(videos.map((v) => [v.slug, v]));
  const perfil = (v: db.Video | null | undefined) => v?.pilar === "perfil";
  const naFila = new Set(fila.map((f) => f.video_slug).filter(Boolean));
  const publicado = new Set(pubs.map((p) => p.video_slug).filter(Boolean));
  const trava = new Map(travas.map((t) => [t.video_slug, t]));
  const ult = db.leiturasConfiaveis(mets);

  // os temas de um vídeo (o do roteiro e os dos posts dele): é deles que sai a grafia do nome próprio
  const temasDe = (videoSlug: string | null | undefined, ...mais: (string | null | undefined)[]) => [
    ...mais, videoSlug ? porSlug.get(videoSlug)?.tema : null,
    ...pubs.filter((p) => videoSlug && (p.video_slug === videoSlug || p.slug === videoSlug)).map((p) => p.tema),
  ];

  const vids: VideoFase[] = videos.map((v) => {
    const temPacote = v.pronto || naFila.has(v.slug) || publicado.has(v.slug);
    const fase = !v.gravado ? "roteiros" : !temPacote ? "gravados" : v.pronto && !naFila.has(v.slug) && !publicado.has(v.slug) ? "prontos" : null;
    return { ...v, fase, nome: nomeCurto(v.slug, { perfil: perfil(v), temas: temasDe(v.slug) }), trava: trava.get(v.slug) ?? null };
  });
  const agendados: PostFila[] = fila
    .filter((f) => f.estado !== "publicado")
    .map((f) => {
      const video = f.video_slug ? porSlug.get(f.video_slug) ?? null : null;
      return { ...f, nome: nomeCurto(f.slug, { perfil: perfil(video), videoSlug: f.video_slug, temas: temasDe(f.video_slug) }), video };
    });
  const publicados: PostPublicado[] = pubs.map((p) => {
    const video = p.video_slug ? porSlug.get(p.video_slug) ?? null : null;
    const l = ult.get(p.slug);
    return {
      ...p, nome: nomeCurto(p.slug, { perfil: perfil(video) || p.pilar === "perfil", videoSlug: p.video_slug, temas: temasDe(p.video_slug, p.tema) }), video,
      leitura: l?.m, descartadas: l?.descartadas ?? [],
    };
  }).sort((a, b) => (b.publicado_em ?? "").localeCompare(a.publicado_em ?? ""));

  /** Os 4 portões de um vídeo (pauta, roteiro, imagem, corte); sem linha no banco = "pendente". */
  const portoesDoVideo = (slug: string) =>
    PORTOES.map((p) => estados.find((e) => e.alvo === `videos/${slug}` && e.portao === p) ?? null);
  const portaoDaFila = (slug: string) => estados.find((e) => e.alvo === `06-publicar/${slug}` && e.portao === "publicacao") ?? null;

  return {
    vids, agendados, publicados, estados, portoesDoVideo, portaoDaFila, porSlug, mets,
    /** cenas extras e PDF do vídeo (videos_producao) */
    roteiroDe: (slug: string) => roteiroDe.get(slug) ?? null,
    /** o pacote pronto do vídeo (prontos), se houver */
    prontoDe: (slug: string) => prontoDe.get(slug) ?? null,
  };
});

export type Producao = Awaited<ReturnType<typeof lerProducao>>;

/** Onde um vídeo está na Produção: Publicados, Agendados ou a fase dele (o painel não tem ficha de vídeo). */
export function hrefDoVideo(p: Producao, slug: string): string {
  if (p.publicados.some((x) => x.video_slug === slug || x.slug === slug)) return "/producao#publicados";
  if (p.agendados.some((x) => x.video_slug === slug)) return "/producao#agendados";
  const fase = p.vids.find((v) => v.slug === slug)?.fase;
  return fase ? `/producao#${fase}` : "/producao";
}


// ── portões de um post da fila: o que o publicar.py confere (design-system.md §11.12) ──────────────────────────────
const PIOR: db.StatusPortao[] = ["escalado", "bloqueado", "vencido", "pendente", "nao_se_aplica"];
const NOME: Record<string, string> = { pauta: "pauta", roteiro: "roteiro", imagem: "imagem", corte: "corte", publicacao: "publicação" };

export type PortoesDoPost = { status: db.StatusPortao; legado: boolean; segura?: string; motivos: string[] };

const STATUS_DA_PALAVRA: Record<string, db.StatusPortao> = {
  PENDENTE: "pendente", VENCIDO: "vencido", BLOQUEADO: "bloqueado", ESCALADO: "escalado", APROVADO: "aprovado",
  NAO_SE_APLICA: "nao_se_aplica",
};

/**
 * Uma mensagem do conferir_pacote (scripts/portoes.py, gravada pelo sincronizador em fila.erros_gauntlet) → o portão e
 * o estado que ela quer dizer. Formatos (o publicar.py usa as mesmas frases):
 * - "portão publicacao (portao-publicacao) PENDENTE: …" e "origem videos/x: portão roteiro (…) VENCIDO: …";
 * - "origem videos/x: portão imagem: não há arquivos da área (…)" → não se aplica, mas é exigido;
 * - "capa/capa.png: trocado depois do selo — … portão imagem aprovou" e "… o portão imagem da origem já não aprova …"
 *   → vencido (o arquivo mudou depois da aprovação);
 * - "pacote sem selo GAUNTLET …" / "origem do selo sem livro de veredictos" → ainda não rodou (o selo não existe);
 * - qualquer outra ("falta pacote.json", "não consegui conferir os portões") → bloqueado, que é o que o publicar.py faz.
 */
export function lerErroGauntlet(msg: string): { portao: string; status: db.StatusPortao } {
  const comEstado = /portão (\w+) \([^)]*\) ([A-Z_]+)/.exec(msg);
  if (comEstado) return { portao: comEstado[1], status: STATUS_DA_PALAVRA[comEstado[2]] ?? "bloqueado" };
  const semArquivos = /portão (\w+): não há arquivos da área/.exec(msg);
  if (semArquivos) return { portao: semArquivos[1], status: "nao_se_aplica" };
  const trocado = /portão (\w+)(?: da origem)? (?:aprovou|já não aprova)/.exec(msg);
  if (trocado) return { portao: trocado[1], status: "vencido" };
  if (/sem selo GAUNTLET/.test(msg)) return { portao: "selo", status: "pendente" };
  if (/origem do selo/.test(msg)) return { portao: "origem", status: "pendente" };
  if (/pacote\.json/.test(msg)) return { portao: "pacote", status: "bloqueado" };
  return { portao: "conferência", status: "bloqueado" };
}

/**
 * A linha "Portões:" de um post (handoff.md §5 e design-system.md §11.12): a resposta do próprio publicar.py, gravada
 * pelo sincronizador em `fila.erros_gauntlet` (o conferir_pacote, com as mesmas mensagens). Legado SEM selo vence
 * (publica sem olhar portão). Fora disso: nenhuma mensagem = "Aprovado" (o post sai); senão o PIOR estado entre as
 * mensagens (Escalado > Bloqueado > Vencido > Ainda não rodou > Não se aplica) e quem segura ("imagem e mais 1"), com
 * "não sai". Arquivo trocado depois do selo entra aqui — o banco agora sabe.
 */
export function portoesDoPost(_p: Producao, post: db.ItemFila): PortoesDoPost {
  const motivos = Array.isArray(post.erros_gauntlet) ? post.erros_gauntlet : [];
  // legado sem selo só vence se o publicar.py não acusar nada: "falta pacote.json" num legado também não sai (PI64)
  if (post.legado && !post.selado && motivos.length === 0) return { status: "pendente", legado: true, motivos };
  if (motivos.length === 0) return { status: "aprovado", legado: false, motivos };
  const lidos = motivos.map(lerErroGauntlet);
  for (const estado of PIOR) {
    const quem = [...new Set(lidos.filter((x) => x.status === estado).map((x) => NOME[x.portao] ?? x.portao))];
    if (quem.length === 0) continue;
    return { status: estado, legado: false, segura: `${quem[0]}${quem.length > 1 ? ` e mais ${quem.length - 1}` : ""}`, motivos };
  }
  // só "aprovado" nas mensagens não acontece (o conferir_pacote só lista o que segura); por garantia, segura
  return { status: "bloqueado", legado: false, segura: "conferência", motivos };
}

/** O pior dos portões de um vídeo, com o nome ("roteiro e mais 2"); tudo aprovado = "aprovado". */
export function piorDoVideo(p: Producao, slug: string): { status: db.StatusPortao; quem?: string } {
  const lista = PORTOES.map((portao, i) => ({ portao, status: p.portoesDoVideo(slug)[i]?.status ?? ("pendente" as db.StatusPortao) }));
  for (const estado of PIOR) {
    const quem = lista.filter((x) => x.status === estado);
    if (quem.length === 0) continue;
    if (estado === "nao_se_aplica" && quem.length < lista.length) continue;
    return { status: estado, quem: `${NOME[quem[0].portao]}${quem.length > 1 ? ` e mais ${quem.length - 1}` : ""}` };
  }
  return { status: "aprovado" };
}

/** Algum portão do vídeo pede ação (bloqueado, escalado, vencido)? Vale antes de Publicado e Agendado. */
export const videoBloqueado = (p: Producao, slug: string | null) =>
  Boolean(slug) && p.portoesDoVideo(slug as string).some((e) => e && PEDE_ACAO.includes(e.status));

// ── Precisam de atenção (= a lista do sino) ────────────────────────────────────────────────────────────────────────

export type Atencao = { id: string; tom: "portao" | "alerta"; icone?: "camera" | "lock" | "alert"; titulo: string; corpo: string; acao?: { rotulo: string; href: string } };

/**
 * Os avisos do §15.1, calculados dos dados, um por regra que vale agora: roteiros esperando gravação (o mais antigo e o
 * próximo), pronto que não sai (trava manual), portão do roteiro que ainda não rodou e qualquer portão bloqueado,
 * escalado ou vencido. Sem "não lida": o painel não guarda o que você viu.
 */
export function precisamDeAtencao(p: Producao, agentes: db.Agente[], hoje = new Date()): Atencao[] {
  const out: Atencao[] = [];
  const roteiros = p.vids.filter((v) => v.fase === "roteiros");
  if (roteiros.length > 0) {
    const porData = roteiros.filter((v) => dataDoSlug(v.slug)).sort((a, b) => a.slug.localeCompare(b.slug));
    const antigo = porData[0];
    const hojeDia = diaEmLondres(hoje);
    const proximo = porData.find((v) => (dataDoSlug(v.slug) ?? "") >= hojeDia);
    const partes = [];
    if (antigo) partes.push(`O mais antigo, ${antigo.nome}, espera desde ${diaCurto(dataDoSlug(antigo.slug)!).replace(/^\S+ /, "")}.`);
    if (proximo && proximo !== antigo) partes.push(`${proximo.nome} está previsto para ${relativo(diasEntre(hoje, dataDoSlug(proximo.slug)!))}.`);
    out.push({
      id: "roteiros", tom: "portao", icone: "camera",
      titulo: `${roteiros.length} ${roteiros.length === 1 ? "roteiro esperando" : "roteiros esperando"} gravação`,
      corpo: partes.join(" "), acao: { rotulo: "Ver roteiros", href: "/producao#roteiros" },
    });
  }
  for (const v of p.vids.filter((x) => x.fase === "prontos" && x.trava)) {
    out.push({
      id: `trava-${v.slug}`, tom: "alerta", titulo: "Pronto, mas não vai ao ar",
      corpo: `${v.nome} está pronto, mas tem a trava "${v.trava!.motivo}" (desde ${diaCurto(v.trava!.desde).replace(/^\S+ /, "")}): não sai.`,
      acao: { rotulo: "Ver prontos", href: "/producao#prontos" },
    });
  }
  const semRoteiro = roteiros.filter((v) => (p.portoesDoVideo(v.slug)[1]?.status ?? "pendente") === "pendente");
  if (semRoteiro.length > 0) {
    const revisor = agentes.find((a) => a.id === "revisor-de-roteiro")?.nome;
    const quem = revisor ? `O ${revisor} revisa cada um antes da gravação.` : "O portão revisa cada um antes da gravação.";
    out.push({
      id: "portao-roteiro", tom: "portao", titulo: "Portão do roteiro ainda não rodou",
      corpo: semRoteiro.length === roteiros.length && roteiros.length > 1
        ? `Nenhum dos ${roteiros.length} roteiros passou pelo portão do roteiro ainda. ${quem}`
        : `${semRoteiro.length} ${semRoteiro.length === 1 ? "roteiro ainda sem" : "roteiros ainda sem"} o veredicto do portão do roteiro. ${quem}`,
      acao: { rotulo: "Ver roteiros", href: "/producao#roteiros" },
    });
  }
  const nomeAgente = new Map(agentes.map((a) => [a.id, a.nome]));
  for (const e of p.estados.filter((x) => PEDE_ACAO.includes(x.status))) {
    const alvo = e.alvo === "painel" ? "o painel" : e.alvo.startsWith("06-publicar/") ? `post ${nomeCurto(e.slug)}` : p.porSlug.get(e.slug) ? p.vids.find((v) => v.slug === e.slug)?.nome ?? e.slug : e.slug;
    const palavra = e.status === "bloqueado" ? "bloqueado" : e.status === "escalado" ? "escalado" : "vencido";
    out.push({
      id: `${e.alvo}:${e.portao}`, tom: "alerta",
      titulo: `Portão ${e.portao === "publicacao" ? "da publicação" : e.portao === "dados" ? "dos dados" : ["pauta", "imagem", "interface"].includes(e.portao) ? `da ${e.portao}` : `do ${e.portao}`} ${palavra}`,
      corpo: [alvo, nomeAgente.get(e.agente), resumoMotivos(e.motivos)].filter(Boolean).join(" · "),
      acao: e.alvo === "painel" ? { rotulo: "Ver o portão", href: `/equipe/${e.agente}` } : { rotulo: "Ver na produção", href: "/producao" },
    });
  }
  return out;
}
