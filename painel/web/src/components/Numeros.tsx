import type { ReactNode } from "react";

// Números lado a lado (design-system.md §15.2, `.k-stats` / `.k-stat`): valor em 20px (24px com `grande`) e o rótulo
// embaixo; divisória `line` entre eles. `solto` = sem divisória antes do primeiro (totais da Visão geral). Tokens em
// accent-ink (decisão de 23/10); dinheiro com o símbolo em <small>.

export type Numero = { rotulo: ReactNode; valor: ReactNode; grande?: boolean; tokens?: boolean; prefixo?: string };

export default function Numeros({ itens, solto }: { itens: Numero[]; solto?: boolean }) {
  return (
    <div className={`k-stats${solto ? " is-solto" : ""}`}>
      {itens.map((n, i) => (
        <div key={i} className="k-stat">
          <span className={["k-stat-v", n.grande && "is-grande", n.tokens && "k-tokens"].filter(Boolean).join(" ")}>
            {n.prefixo && <small>{n.prefixo}</small>}
            {n.valor}
          </span>
          <span className="k-stat-r">{n.rotulo}</span>
        </div>
      ))}
    </div>
  );
}

