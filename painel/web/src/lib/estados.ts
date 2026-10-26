// Os três mapas de estado do design system (design-system.md §11.3) — UM lugar só. Toda tela que mostra o estado de um
// portão, de um vídeo ou a decisão do Carlos passa por aqui; nunca dois desenhos para o mesmo estado.
// Só tipos do db.ts (apagados na compilação): este módulo também roda no navegador.
import type { PortaoEstado, StatusPortao } from "./db";
import type { NomeIcone } from "@/components/Icone";
import { NOME_PORTAO, dataHora, estadoLimpo, titulo } from "./formato";

export type TomChip = "aprovado" | "producao" | "bloqueado" | "agendado" | "publicado" | "portao";

/** Família 1 — estado de cada portão do GAUNTLET (o mapa único). "legado" = fila.legado, vence o "pendente" do banco. */
export type EstadoPortao = StatusPortao | "legado";
export const MAPA_PORTAO: Record<EstadoPortao, { tom: TomChip; palavra: string; semPonto?: boolean }> = {
  aprovado: { tom: "aprovado", palavra: "Aprovado" },
  bloqueado: { tom: "bloqueado", palavra: "Bloqueado" },
  escalado: { tom: "bloqueado", palavra: "Escalado" },
  vencido: { tom: "bloqueado", palavra: "Vencido" },
  pendente: { tom: "agendado", palavra: "Ainda não rodou" },
  nao_se_aplica: { tom: "agendado", palavra: "Não se aplica", semPonto: true },
  legado: { tom: "agendado", palavra: "Legado · sem selo", semPonto: true },
};

/** Vermelho só para o que pede ação (a palavra diferencia os três). */
export const PEDE_ACAO: readonly StatusPortao[] = ["bloqueado", "escalado", "vencido"];
export const pedeAcao = (s: StatusPortao) => PEDE_ACAO.includes(s);

/** Família 2 — decisão do Carlos (só no card do portão, modo Decisão). "Aprovado" não existe aqui: aprovar = agendar. */
export type Decisao = "aguarda" | "ajustes";
export const MAPA_DECISAO: Record<Decisao, string> = { aguarda: "Aguarda", ajustes: "Ajustes" };

/** Família 3 — estado do vídeo, lido EM ORDEM (vale a primeira linha verdadeira). */
export type EstadoVideo = "bloqueado" | "publicado" | "agendado" | "portao" | "producao";
export const MAPA_VIDEO: Record<EstadoVideo, { tom: TomChip; palavra: string; icone?: NomeIcone }> = {
  bloqueado: { tom: "bloqueado", palavra: "Bloqueado" },
  publicado: { tom: "publicado", palavra: "Publicado" },
  agendado: { tom: "agendado", palavra: "Agendado" },
  portao: { tom: "portao", palavra: "Portão", icone: "lock" },
  producao: { tom: "producao", palavra: "Em produção" },
};

/**
 * Estado do vídeo a partir do status.json e dos 4 portões do vídeo (pauta, roteiro, imagem, corte — portão sem linha no
 * banco conta como "pendente"):
 * 1. Bloqueado — algum portão bloqueado, escalado ou vencido (vem antes de Publicado e Agendado);
 * 2. Publicado; 3. Agendado; 4. Portão — todos os que se aplicam aprovaram e falta a decisão do Carlos; 5. Em produção.
 */
export function estadoDoVideo(estado: string | null | undefined, portoes: StatusPortao[]): EstadoVideo {
  if (portoes.some(pedeAcao)) return "bloqueado";
  const e = estadoLimpo(estado);
  if (e === "publicado") return "publicado";
  if (e === "agendado") return "agendado";
  const aplicam = portoes.filter((s) => s !== "nao_se_aplica");
  if (aplicam.length > 0 && aplicam.every((s) => s === "aprovado")) return "portao";
  return "producao";
}

const ARTIGO: Record<string, string> = {
  pauta: "da", roteiro: "do", imagem: "da", corte: "do", publicacao: "da", design: "do", interface: "da", dados: "dos",
};
/** "Portão da interface" */
export const nomeDoPortao = (portao: string) => `Portão ${ARTIGO[portao] ?? "de"} ${NOME_PORTAO[portao] ?? portao}`;

/**
 * O motivo de um portão em uma linha curta, para dica e aviso. "mudou depois do APROVADO: a, b, c" (a lista inteira dos
 * arquivos) vira "3 arquivos mudaram depois do APROVADO"; o resto passa como veio, cortado em 180 caracteres.
 */
export function resumoMotivos(motivos: string[] | null | undefined): string {
  if (!motivos?.length) return "";
  const partes = motivos.map((m) => {
    const vencido = /^mudou depois do APROVADO:\s*(.+)$/i.exec(m.trim());
    // "BLOQUEADO em 2026-10-23T20:44:48+01:00 (S0 0 · S1 6)" → "BLOQUEADO em 23 out, 20:44 (S0 0 · S1 6)"
    if (!vencido) return m.trim().replace(/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:\d{2})?/g, (iso) => dataHora(iso));
    const n = vencido[1].split(",").filter((x) => x.trim()).length;
    return `${n} ${n === 1 ? "arquivo mudou" : "arquivos mudaram"} depois do APROVADO`;
  });
  const texto = partes.join("; ");
  return texto.length > 180 ? `${texto.slice(0, 179).trimEnd()}…` : texto;
}

/** O que o portão audita, em palavras: "o painel", o título do vídeo ou "post …" da fila. */
export function alvoLegivel(e: Pick<PortaoEstado, "alvo" | "slug">, temaDoVideo?: (slug: string) => string | undefined): string {
  if (e.alvo === "painel") return "o painel";
  if (e.alvo.startsWith("06-publicar/")) return `post ${titulo(e.slug)}`;
  return temaDoVideo?.(e.slug) ?? titulo(e.slug);
}

/** Onde o Carlos vê o detalhe de um portão no painel. */
export function hrefDoAlvo(e: Pick<PortaoEstado, "alvo" | "slug" | "agente">): string {
  if (e.alvo.startsWith("videos/")) return `/producao#v-${e.slug}`;
  if (e.alvo.startsWith("06-publicar/")) return "/producao#fila";
  return `/equipe/${e.agente}`;
}
