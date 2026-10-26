import Image from "next/image";
import Link from "next/link";
import type { StatusPortao } from "@/lib/db";
import Capa from "./Capa";
import { propsDica } from "./Dica";
import { nomeDosCanais } from "./Evento";
import Icone from "./Icone";
import LinhaPortoes from "./LinhaPortoes";

// Peças do Calendário (design-system.md §11.12 e §15.2: Mês, Semana, vaga, legenda; sem gravação desde 24/10). O evento é o link para a
// publicação na Produção. A barra da esquerda é o canal (Instagram = accent, Instagram + Facebook = ink, Facebook =
// chart-5) E o canal vai escrito. Publicado = fundo surface-hover. Em todo post da fila, a linha de portões (o que o
// publicar.py confere; legado vence). Horário, título e canais quebram em até 2 linhas — nunca reticências (o title fica
// de apoio).

export type EventoCal = {
  href: string;
  nome: string;
  /** "19:00" */
  hora: string;
  canais: string[];
  publicado: boolean;
  capa: string | null;
  /** só posts da fila */
  portoes?: { status: StatusPortao; legado: boolean; segura?: string };
  /** a linha a mais da Semana: "40 de alcance · Trial", "Normal · palavra AULA", "métricas em 27 out" */
  extra?: string;
};

function canal(canais: string[]) {
  const c = canais.map((x) => x.toLowerCase());
  if (c.length === 1 && c[0] === "instagram") return " k-event--ig";
  if (c.length === 1 && c[0] === "facebook") return " k-event--fb";
  return "";
}

export function EventoMes({ e }: { e: EventoCal }) {
  const estado = e.publicado ? "Publicado" : "Agendado";
  const titulo = `${e.hora} · ${e.nome} · ${nomeDosCanais(e.canais).replace(" + ", " · ")} · ${estado}`;
  return (
    <Link
      href={e.href}
      className={`k-event k-event--mes${canal(e.canais)}${e.publicado ? " is-publicado" : ""}`}
      title={titulo}
      {...propsDica(`${e.hora} · ${e.nome}`, `${nomeDosCanais(e.canais)} · ${estado}`)}
    >
      <div className="k-event-linha">
        <Capa src={e.capa} nome={e.nome} tamanho="xs" />
        <div className="k-event-txt">
          <span><b className="k-mono">{e.hora}</b> · {estado}</span>
          <b>{e.nome}</b>
          <span>{nomeDosCanais(e.canais).replace(" + ", " · ")}</span>
        </div>
      </div>
      {e.portoes && <LinhaPortoes status={e.portoes.status} legado={e.portoes.legado} segura={e.portoes.segura} rotulo="icone" />}
    </Link>
  );
}

export function EventoSemana({ e }: { e: EventoCal }) {
  const estado = e.publicado ? "Publicado" : "Agendado";
  return (
    <Link href={e.href} className={`k-event k-event--semana${canal(e.canais)}${e.publicado ? " is-publicado" : ""}`}>
      {e.capa ? <Image src={e.capa} alt={`Capa de ${e.nome}`} width={300} height={533} sizes="200px" /> : null}
      <span><b className="k-mono">{e.hora}</b> · {estado}</span>
      <b>{e.nome}</b>
      <span>{nomeDosCanais(e.canais).replace(" + ", " · ")}</span>
      {e.extra && <span>{e.extra}</span>}
      {e.portoes && <LinhaPortoes status={e.portoes.status} legado={e.portoes.legado} segura={e.portoes.segura} />}
    </Link>
  );
}

/** Vaga livre (§15.2, `.k-vaga`): dia de vaga do calendario.md, de hoje em diante, sem post — tracejado com a hora. */
export function VagaLivre({ hora }: { hora: string }) {
  return (
    <span className="k-vaga">
      <span>Vaga livre</span>
      <span className="k-mono">{hora}</span>
    </span>
  );
}

/** A legenda do calendário: canal pela cor da barra, publicado pelo fundo, portões pelo cadeado. */
export function LegendaCalendario() {
  return (
    <div className="k-cal-legenda">
      <span><i style={{ background: "var(--accent)" }} aria-hidden="true" />Instagram</span>
      <span><i style={{ background: "var(--ink)" }} aria-hidden="true" />Instagram e Facebook</span>
      <span><i className="is-contorno" aria-hidden="true" />Publicado</span>
      <span><i className="is-tracejado" aria-hidden="true" />Vaga livre</span>
      <span><Icone nome="lock" tamanho={13} />Portões</span>
    </div>
  );
}
