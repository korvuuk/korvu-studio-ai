import type { ReactNode } from "react";

// Dica (tooltip, design-system.md §11.16). Quem tem dica leva data-dica="linha 1" (+ data-dica-detalhe="linha 2") e é
// focável; o components/Dicas.tsx (um ouvinte só, na casca) abre a .k-tooltip.is-floating depois de 300ms de hover ou
// foco, presa a 8px das bordas da janela, e fecha ao sair, ao tocar fora e com Esc.
// A dica complementa, nunca é o único jeito de ler: o mesmo texto vai junto para o leitor de tela (.k-sr-only), e a
// dica visual fica fora dele.

/** Atributos para pôr a dica num elemento que já existe (linha de barra, fatia). Lembre do tabIndex={0}. */
export function propsDica(titulo: string, detalhe?: string) {
  return { "data-dica": titulo, "data-dica-detalhe": detalhe || undefined } as const;
}

export default function Dica({ titulo, detalhe, leitor, children }: {
  titulo: string;
  detalhe?: string;
  /** O que o leitor de tela ouve depois do conteúdo (padrão: título + detalhe). */
  leitor?: string;
  children: ReactNode;
}) {
  const falado = leitor ?? `${titulo}${detalhe ? `: ${detalhe}` : ""}`;
  return (
    <span className="kx-dica-alvo" tabIndex={0} {...propsDica(titulo, detalhe)}>
      {children}
      <span className="k-sr-only">{`, ${falado}`}</span>
    </span>
  );
}
