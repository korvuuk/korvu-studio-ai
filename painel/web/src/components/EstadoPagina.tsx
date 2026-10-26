import type { ReactNode } from "react";
import Icone, { type NomeIcone } from "./Icone";

// Estado de página (design-system.md §12.2 e §12.3): erro (alert sobre danger-soft, role="alert") e não encontrado
// (search), dentro da casca. O texto diz o que aconteceu + por quê + como resolver; ação "Tentar de novo".

export default function EstadoPagina({ tipo = "neutro", icone, titulo, texto, children, acoes, codigo }: {
  tipo?: "erro" | "neutro";
  icone: NomeIcone;
  titulo: string;
  texto?: ReactNode;
  /** "Como resolver" e o que mais a página precisar */
  children?: ReactNode;
  acoes?: ReactNode;
  /** código técnico do erro, em mono apagado */
  codigo?: ReactNode;
}) {
  return (
    <div className={`k-state${tipo === "erro" ? " k-state--erro" : ""}`} role={tipo === "erro" ? "alert" : undefined}>
      <span className="k-state-icon" aria-hidden="true">
        <Icone nome={icone} tamanho={22} />
      </span>
      <h1 className="k-h1">{titulo}</h1>
      {texto && <p className="k-state-text">{texto}</p>}
      {children}
      {acoes && <div className="k-state-actions">{acoes}</div>}
      {codigo && <p className="k-mono k-muted kx-sem-margem">{codigo}</p>}
    </div>
  );
}

/** Card "Como resolver" com os passos numerados (.k-passos) — os comandos vão em <code className="k-code">. */
export function ComoResolver({ passos }: { passos: ReactNode[] }) {
  return (
    <div className="k-card k-pad kx-largura-toda">
      <p className="k-cap kx-cap-bloco">Como resolver</p>
      <ol className="k-passos">
        {passos.map((p, i) => (
          <li key={i}><span>{p}</span></li>
        ))}
      </ol>
    </div>
  );
}
