import type { ReactNode } from "react";
import Icone, { type NomeIcone } from "./Icone";

// Estado vazio (design-system.md §11.17): contorno tracejado, sem fundo, centrado. Ícone 22px num quadrado de 48px,
// título e UMA frase dizendo o que vai aparecer aqui. Ação opcional k-btn-secondary k-btn-sm. Nunca ilustração nem emoji.

export default function Vazio({ icone = "inbox", titulo, children, acao }: {
  icone?: NomeIcone;
  titulo: string;
  /** a frase: o que vai aparecer aqui (e, se for o caso, o comando que traz o dado) */
  children?: ReactNode;
  acao?: ReactNode;
}) {
  return (
    <div className="k-empty">
      <span className="k-empty-icon" aria-hidden="true">
        <Icone nome={icone} tamanho={22} />
      </span>
      <p className="kx-empty-titulo">{titulo}</p>
      {children && <p>{children}</p>}
      {acao && <div className="kx-empty-acao">{acao}</div>}
    </div>
  );
}
