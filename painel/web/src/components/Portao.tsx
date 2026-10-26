import type { StatusPortao } from "@/lib/db";
import { type Decisao, type EstadoVideo, resumoMotivos } from "@/lib/estados";
import { NOME_PORTAO } from "@/lib/formato";
import { Card } from "./Card";
import { ChipDecisao, ChipPortao, ChipVideo } from "./Chip";
import Icone from "./Icone";

// Portão de aprovação (ApprovalGate, design-system.md §11.11) — dois modos, um componente:
// - Decisão: só quando TODOS os portões que se aplicam ao vídeo aprovaram e o vídeo ainda não está agendado nem
//   publicado (estado do vídeo = "portao"). Chip da decisão do Carlos (Aguarda/Ajustes); sem ações
//   (24/10: o painel só informa).
// - Portões do vídeo: qualquer outro caso, só leitura, chip do estado do vídeo; abaixo, "Posts na fila", fora da conta.
// Critérios = os portões, cada um com o chip do mapa único; a caixa é aria-hidden e o estado vai ESCRITO no chip.

export type CriterioPortao = { portao: string; status: StatusPortao; motivos?: string[] };
export type PostNaFila = { rotulo: string; status: StatusPortao; legado?: boolean };

const nomeCriterio = (p: string) => {
  const n = NOME_PORTAO[p] ?? p;
  return n.charAt(0).toUpperCase() + n.slice(1);
};

export default function Portao({ titulo, criterios, estadoVideo, decisao = "aguarda", posts }: {
  titulo: string;
  criterios: CriterioPortao[];
  estadoVideo: EstadoVideo;
  decisao?: Decisao;
  posts?: PostNaFila[];
}) {
  const aprovados = criterios.filter((c) => c.status === "aprovado").length;
  const total = criterios.length;
  const modoDecisao = estadoVideo === "portao";
  return (
    <Card className="k-gate">
      <div className="k-gate-head">
        <span className="k-gate-icon" aria-hidden="true"><Icone nome="lock" tamanho={18} /></span>
        <div>
          <div className="k-cap k-gate-step">
            {modoDecisao
              ? `${aprovados} de ${total} portões aprovados · sua decisão`
              : `Portões do vídeo · ${aprovados} de ${total} aprovados`}
          </div>
          <b className="k-gate-title" title={titulo}>{titulo}</b>
        </div>
        {modoDecisao ? <ChipDecisao decisao={decisao} /> : <ChipVideo estado={estadoVideo} />}
      </div>

      <ul className="k-gate-checks kx-lista-limpa">
        {criterios.map((c) => {
          const feito = c.status === "aprovado";
          const motivo = resumoMotivos(c.motivos);
          return (
            <li key={c.portao} className={`k-check${feito ? " is-on" : ""}`}>
              <b aria-hidden="true">{feito && <Icone nome="check" tamanho={12} />}</b>
              <span>{nomeCriterio(c.portao)}</span>
              <ChipPortao
                status={c.status}
                como="small"
                dica={motivo ? { titulo: nomeCriterio(c.portao), detalhe: motivo } : undefined}
              />
            </li>
          );
        })}
      </ul>

      {/* sem botões (decisão de 24/10, PI69: o painel só informa) — a decisão é dada no Claude Code */}
      {modoDecisao && <p className="k-kpi-note kx-sem-margem">A decisão é sua, dada no Claude Code: o painel só mostra.</p>}

      {!modoDecisao && posts && posts.length > 0 && (
        <>
          <div className="k-cap k-gate-step">Posts na fila · {posts.length} · fora da conta dos {total}</div>
          <ul className="k-gate-checks kx-lista-limpa">
            {posts.map((p) => (
              <li key={p.rotulo} className="k-check">
                <span>{p.rotulo}</span>
                <ChipPortao status={p.status} legado={p.legado} como="small" />
              </li>
            ))}
          </ul>
        </>
      )}
    </Card>
  );
}
