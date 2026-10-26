import { ETAPAS, etapaDoEstado } from "@/lib/formato";

// Progresso (design-system.md §11.10). Etapas: um segmento por etapa de produção (Roteiro · Gravação · Edição · Revisão ·
// Publicar), os 12 estados do projeto mapeados em lib/formato.ts. Feita = ink, atual = laranja, bloqueada = vermelho,
// futura vazia. role="img" + aria-label "Etapa 4 de 5: Revisão" (as futuras ficam a 1,13:1 do card).

export function Etapas({ estado, bloqueado, rotulos }: {
  estado: string | null | undefined;
  /** o vídeo está Bloqueado (algum portão pede ação): a etapa atual fica vermelha */
  bloqueado?: boolean;
  /** rótulos das 5 etapas acima dos segmentos (a atual em accent-ink) */
  rotulos?: boolean;
}) {
  const atual = etapaDoEstado(estado);
  if (atual === null) return <span className="k-ink2">Etapa desconhecida</span>;
  const todas = atual >= ETAPAS.length;
  const texto = todas
    ? `Todas as ${ETAPAS.length} etapas feitas`
    : `Etapa ${atual + 1} de ${ETAPAS.length}: ${ETAPAS[atual]}${bloqueado ? ", bloqueada" : ""}`;
  return (
    <div className="kx-etapas">
      {rotulos && (
        <div className="k-steps-labels k-cap" aria-hidden="true">
          {ETAPAS.map((nome, i) => <span key={nome} className={i === atual ? "is-now" : undefined}>{nome}</span>)}
        </div>
      )}
      <div className="k-steps" role="img" aria-label={texto}>
        {ETAPAS.map((nome, i) => (
          <i key={nome} className={todas || i < atual ? "on" : i === atual ? (bloqueado ? "blocked" : "now") : undefined} />
        ))}
      </div>
    </div>
  );
}

/** Barra de progresso — sempre com o número ao lado ("3 de 12 · 25%"). */
export function BarraProgresso({ titulo, feito, total, tom }: {
  titulo: string; feito: number; total: number; tom?: "feito" | "bloqueado";
}) {
  const pct = total > 0 ? Math.round((feito / total) * 100) : 0;
  const classe = tom === "feito" ? " is-done" : tom === "bloqueado" ? " is-blocked" : "";
  return (
    <div className="kx-progresso">
      <div className="kx-progresso-cab">
        <b>{titulo}</b>
        <span className="k-num k-ink2">{feito} de {total} · {pct}%</span>
      </div>
      <div className={`k-progress${classe}`} role="img" aria-label={`${titulo}: ${feito} de ${total}, ${pct}%`}>
        <span style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

/** As etapas da pós-produção (Produção · Gravados): Corte → Cor → Gráficos → Áudio → Capa → QA, pelo status.json.estado. */
export const ETAPAS_POS = ["Corte", "Cor", "Gráficos", "Áudio", "Capa", "QA"] as const;
const POS_DO_ESTADO: Record<string, number> = { gravacao: 0, edicao: 0, edl_aprovada: 0, revisao: 0, cor: 1, legendas: 2, capa: 4, qa: 5 };

export function EtapasPos({ estado }: { estado: string | null | undefined }) {
  const e = (estado ?? "").replace(/\s*\(.*\)$/, "").trim();
  const atual = POS_DO_ESTADO[e];
  if (atual == null) return <span className="k-ink2">—</span>;
  return (
    <div className="k-steps kx-etapas-pos" role="img" aria-label={`Pós-produção: etapa ${atual + 1} de ${ETAPAS_POS.length}, ${ETAPAS_POS[atual]}`}>
      {ETAPAS_POS.map((n, i) => <i key={n} className={i < atual ? "on" : i === atual ? "now" : undefined} />)}
    </div>
  );
}
