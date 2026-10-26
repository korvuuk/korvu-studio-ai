import type { ReactNode } from "react";

// Lista chave-valor (design-system.md §15.2, `.k-kv`): uma linha por item, a chave à esquerda e o valor à direita, com
// fio entre as linhas. A grande (`.k-kv--grande`) é a da Fila do Calendário: título, a frase embaixo e o número grande
// (zero em ink-3, mas sempre escrito).

export function ListaKv({ itens, mono, className }: {
  itens: { chave: ReactNode; valor: ReactNode; id?: string }[];
  /** valores em mono (tamanhos, contagens) */
  mono?: boolean;
  className?: string;
}) {
  return (
    <ul className={["k-kv", className].filter(Boolean).join(" ")}>
      {itens.map((it, i) => (
        <li key={it.id ?? i}>
          <span>{it.chave}</span>
          <span className={`k-kv-v${mono ? " k-mono" : ""}`}>{it.valor}</span>
        </li>
      ))}
    </ul>
  );
}

export function ListaKvGrande({ itens, className }: { itens: { titulo: string; frase: ReactNode; n: number }[]; className?: string }) {
  return (
    <ul className={["k-kv k-kv--grande", className].filter(Boolean).join(" ")}>
      {itens.map((it) => (
        <li key={it.titulo}>
          <span className="k-kv-t"><b>{it.titulo}</b><small>{it.frase}</small></span>
          <span className={`k-kv-n${it.n ? "" : " is-zero"}`}>{it.n}</span>
        </li>
      ))}
    </ul>
  );
}
