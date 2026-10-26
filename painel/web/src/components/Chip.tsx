import type { ElementType, ReactNode } from "react";
import type { StatusPortao } from "@/lib/db";
import {
  MAPA_DECISAO, MAPA_PORTAO, MAPA_VIDEO, type Decisao, type EstadoVideo, type TomChip,
} from "@/lib/estados";
import { nomeModelo } from "@/lib/formato";
import Dica from "./Dica";
import Icone, { type NomeIcone } from "./Icone";

// Chip de estado (design-system.md §11.3): 24px, pill, SEMPRE com palavra. Os três mapas (portão, decisão do Carlos,
// vídeo) vivem em lib/estados.ts — aqui só o desenho. Dentro de um critério riscado (.k-check), use como="small".

const TOM: Record<TomChip, string> = {
  aprovado: "k-chip--aprovado", producao: "k-chip--producao", bloqueado: "k-chip--bloqueado",
  agendado: "k-chip--agendado", publicado: "k-chip--publicado", portao: "k-chip--portao",
};

export function Chip({ tom, semPonto, icone, como: Tag = "span", pequeno, children }: {
  tom: TomChip | "modo"; semPonto?: boolean; icone?: NomeIcone; como?: ElementType;
  /** 20px (.is-sm): tabelas e cartões das telas */
  pequeno?: boolean;
  children: ReactNode;
}) {
  const cor = tom === "modo" ? "k-chip--modo" : TOM[tom];
  return (
    <Tag className={`k-chip ${cor}${semPonto ? " no-dot" : ""}${pequeno ? " is-sm" : ""}`}>
      {icone && <Icone nome={icone} tamanho={12} />}
      {children}
    </Tag>
  );
}

/**
 * Família 1 — o estado de UM portão (o mapa único). `legado` (fila.legado) vence o status do banco.
 * Com `dica`, o chip ganha foco e a dica com o motivo (o leitor de tela ouve o mesmo texto).
 */
export function ChipPortao({ status, legado, como, dica, pequeno, texto }: {
  status: StatusPortao;
  legado?: boolean;
  como?: ElementType;
  dica?: { titulo: string; detalhe?: string };
  pequeno?: boolean;
  /** palavra do mapa + complemento ("Ainda não rodou · roteiro e mais 2") */
  texto?: string;
}) {
  const m = MAPA_PORTAO[legado ? "legado" : status];
  const chip = <Chip tom={m.tom} semPonto={m.semPonto} como={como} pequeno={pequeno}>{texto ? `${m.palavra} · ${texto}` : m.palavra}</Chip>;
  if (!dica) return chip;
  return <Dica titulo={dica.titulo} detalhe={dica.detalhe} leitor={dica.detalhe ? `${dica.titulo}: ${dica.detalhe}` : dica.titulo}>{chip}</Dica>;
}

/** Família 3 — o estado do vídeo (calculado em lib/estados.ts → estadoDoVideo, em ordem). */
export function ChipVideo({ estado, pequeno }: { estado: EstadoVideo; pequeno?: boolean }) {
  const m = MAPA_VIDEO[estado];
  return <Chip tom={m.tom} icone={m.icone} pequeno={pequeno}>{m.palavra}</Chip>;
}

/** Modo de publicação (§15.2): Normal = chip neutro sem ponto; Trial Reel = contorno (não é o chip de modelo de IA). */
export function ChipModo({ trial }: { trial: string | null | undefined }) {
  return trial
    ? <Chip tom="modo" pequeno>Trial Reel</Chip>
    : <Chip tom="agendado" semPonto pequeno>Normal</Chip>;
}

/** Família 2 — a decisão do Carlos no card do portão (modo Decisão): só "Aguarda" ou "Ajustes". */
export function ChipDecisao({ decisao }: { decisao: Decisao }) {
  return <Chip tom="portao">{MAPA_DECISAO[decisao]}</Chip>;
}

/** Modelo de IA com a versão (decisão de 23/10): Opus em tinta sólida (o mais caro pesa mais), Sonnet em contorno. */
export function ChipModelo({ modelo, pequeno, rotulo }: {
  /** apelido do agente (opus, sonnet) ou nome do modelo dos registros ("Opus 5.5") */
  modelo: string;
  pequeno?: boolean;
  /** rótulo pronto (ex.: precos_modelo.nome); sem ele, o apelido vira "Opus 5.5" por lib/formato */
  rotulo?: string;
}) {
  // sólido = os modelos mais caros (Opus e Fable, como a maquete "Rodou em"); contorno = Sonnet
  const opus = /^(claude-)?(opus|fable)/i.test(modelo.trim());
  return <span className={`k-chip ${opus ? "k-chip--opus" : "k-chip--model"}${pequeno ? " is-sm" : ""}`}>{rotulo ?? nomeModelo(modelo)}</span>;
}

/** O modelo que RODOU (decisão de 24/10, `.k-modelo-mix` / `.k-modelo-nada`): o chip do principal; com mais de um, "94 % · +1"
 *  embaixo, a lista no title e no leitor de tela; sem registro nos 30 dias, "ainda não rodou". */
export type ModeloRodouDados = { principal: { modelo: string; nome: string; pct: number }; outros: { nome: string; pct: number }[] } | null;
const pctModelo = (p: number) => `${Math.round(p)}\u00a0%`;
export function ModeloRodou({ rodou }: { rodou: ModeloRodouDados }) {
  if (!rodou) return <span className="k-modelo-nada">ainda não rodou</span>;
  const chip = <ChipModelo modelo={rodou.principal.modelo} rotulo={rodou.principal.nome} pequeno />;
  if (!rodou.outros.length) return chip;
  const lista = [`${rodou.principal.nome} ${pctModelo(rodou.principal.pct)}`, ...rodou.outros.map((o) => `${o.nome} ${pctModelo(o.pct)}`)];
  return (
    <span className="k-modelo-mix" title={`Rodou em ${lista.join(" · ")}`}>
      {chip}
      <small>{pctModelo(rodou.principal.pct)} · +{rodou.outros.length}<span className="k-sr-only"> (também {lista.slice(1).join(", ")})</span></small>
    </span>
  );
}
