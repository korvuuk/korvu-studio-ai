import type { Snapshot } from "./db";
import { data, num } from "./formato";

// Números do perfil (telas/visao-geral.md e telas/desempenho.md): a última leitura do perfil_snapshots contra a anterior.
// A cor do delta segue o significado: para seguidores, alcance, visualizações e visitas, subir é bom.

export type Variacao = {
  /** "11,1%", "−0,1%", "3,4 p.p." */
  texto: string;
  sentido: "sobe" | "desce" | "igual";
  significado: "bom" | "ruim" | "neutro";
  /** "a mais que em 16 out" */
  leitor: string;
  /** quase igual: sem seta, cinza */
  quaseIgual: boolean;
};

const fmt = (n: number, casas = 1) => n.toLocaleString("pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas });

/** Variação percentual de `de` para `para`; abaixo de 0,5 % fica "quase igual" (cinza, sem seta), como a maquete. */
export function variacao(para: number | null | undefined, de: number | null | undefined, quando: string): Variacao | null {
  if (para == null || de == null || de === 0) return null;
  const pct = ((para - de) / de) * 100;
  const quaseIgual = Math.abs(pct) < 0.5;
  const sentido = pct > 0 ? "sobe" : pct < 0 ? "desce" : "igual";
  return {
    texto: `${pct < 0 ? "−" : ""}${fmt(Math.abs(pct))}%`,
    sentido,
    significado: quaseIgual ? "neutro" : pct > 0 ? "bom" : "ruim",
    leitor: quaseIgual ? `quase igual a ${quando}` : pct > 0 ? `a mais que em ${quando}` : `a menos que em ${quando}`,
    quaseIgual,
  };
}

/** Parte do alcance que não segue a página (0–1), ou null sem a divisão. */
export const foraDaBolha = (s: Snapshot | undefined) => {
  const n = s?.alcance_nao_seguidores ?? 0;
  const t = n + (s?.alcance_seguidores ?? 0);
  return t > 0 ? { fracao: n / t, nao: n, total: t } : null;
};

/** Variação em pontos percentuais da parte fora da bolha. */
export function variacaoPP(atual: Snapshot | undefined, anterior: Snapshot | undefined, quando: string): Variacao | null {
  const a = foraDaBolha(atual);
  const b = foraDaBolha(anterior);
  if (!a || !b) return null;
  const pp = (a.fracao - b.fracao) * 100;
  const quaseIgual = Math.abs(pp) < 0.5;
  return {
    texto: `${pp < 0 ? "−" : ""}${fmt(Math.abs(pp))} p.p.`,
    sentido: pp > 0 ? "sobe" : pp < 0 ? "desce" : "igual",
    significado: quaseIgual ? "neutro" : pp > 0 ? "bom" : "ruim",
    leitor: quaseIgual ? `quase igual a ${quando}` : pp > 0 ? `a mais que em ${quando}` : `a menos que em ${quando}`,
    quaseIgual,
  };
}

/** "−3 vs. leitura de 16 out" */
export const diferencaAbsoluta = (para: number, de: number, lido: string) =>
  `${para - de > 0 ? "+" : para - de < 0 ? "−" : ""}${num(Math.abs(para - de))} vs. leitura de ${data(lido)}`;

/** Período da janela de 28 dias da Meta que termina na leitura: "25 set – 22 out". */
export function periodo(s: Snapshot): string {
  const dias = s.janela_dias ?? 28;
  const fim = new Date(s.lido_em);
  const ini = new Date(fim.getTime() - (dias - 1) * 86_400_000);
  return `${data(ini.toISOString())} – ${data(s.lido_em)}`;
}
