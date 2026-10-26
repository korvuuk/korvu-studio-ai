import Link from "next/link";
import type { ComponentProps, ReactNode } from "react";
import Icone, { type NomeIcone } from "./Icone";

// Botão do sistema (design-system.md §11.2): 36px, raio 8, rótulo 13px/600. Primário = UMA ação principal por vista,
// texto sempre on-accent (a tinta) sobre o laranja. Secundário, fantasma e escuro (a decisão do Carlos num portão).
// Só ícone: aria-label obrigatório (o tipo não deixa compilar sem). Pequeno (28px) só em tabelas e barras densas.

export type Variante = "primario" | "secundario" | "fantasma" | "escuro";
const VARIANTE: Record<Variante, string> = {
  primario: "k-btn-primary", secundario: "k-btn-secondary", fantasma: "k-btn-ghost", escuro: "k-btn-dark",
};

type Base = {
  variante?: Variante; pequeno?: boolean; icone?: NomeIcone; tamanhoIcone?: number;
  /** ícone DEPOIS do texto ("Ver calendário ›") */
  iconeFim?: NomeIcone;
};
type Forma = { soIcone?: false } | { soIcone: true; icone: NomeIcone; "aria-label": string };

export function classesBotao({ variante = "secundario", pequeno, soIcone, extra }: {
  variante?: Variante; pequeno?: boolean; soIcone?: boolean; extra?: string;
}) {
  return ["k-btn", VARIANTE[variante], pequeno && "k-btn-sm", soIcone && "k-btn-icon", extra].filter(Boolean).join(" ");
}

export function Botao(props: Base & Forma & Omit<ComponentProps<"button">, "className"> & { className?: string }) {
  const { variante, pequeno, icone, iconeFim, tamanhoIcone, soIcone, className, children, type = "button", ...resto } = props;
  return (
    <button type={type} className={classesBotao({ variante, pequeno, soIcone, extra: className })} {...resto}>
      {icone && <Icone nome={icone} tamanho={tamanhoIcone ?? (pequeno ? 14 : 16)} />}
      {children}
      {iconeFim && <Icone nome={iconeFim} tamanho={pequeno ? 14 : 16} />}
    </button>
  );
}

export function BotaoLink(props: Base & Forma & Omit<ComponentProps<typeof Link>, "className"> & { className?: string }) {
  const { variante, pequeno, icone, iconeFim, tamanhoIcone, soIcone, className, children, ...resto } = props;
  return (
    <Link className={classesBotao({ variante, pequeno, soIcone, extra: className })} {...resto}>
      {icone && <Icone nome={icone} tamanho={tamanhoIcone ?? (pequeno ? 14 : 16)} />}
      {children}
      {iconeFim && <Icone nome={iconeFim} tamanho={pequeno ? 14 : 16} />}
    </Link>
  );
}

/** Atalho (§15.2, `.k-atalho`): a linha-link no pé de um card ("A caminho: 7 roteiros ainda sem gravação ›"). */
export function Atalho({ href, children }: { href: string; children: ReactNode }) {
  return (
    <Link className="k-atalho" href={href}>
      {children}
      <Icone nome="chevron-right" tamanho={14} />
    </Link>
  );
}
