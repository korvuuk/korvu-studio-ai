import type { ReactNode } from "react";
import { compacto, num } from "@/lib/formato";
import Icone from "./Icone";

// Peças de texto do painel que o design system define como regra mas não como componente:
// - BlocoCodigo: "copie e cole" (k-card k-pad + <pre class="k-mono">, quebra de linha ligada — handoff.md §5);
// - Codigo: comando ou ID no meio do texto (.k-code, Geist Mono);
// - ListaDados: pares rótulo → valor (ficha de uma pessoa);
// - Ressalva: aviso curto numa célula (ícone de alerta + palavras; nunca só a cor);
// - Tokens: contagem de tokens em destaque laranja (decisão do Carlos, 23/10 — accent-ink em texto pequeno).

export function Codigo({ children }: { children: ReactNode }) {
  return <code className="k-code">{children}</code>;
}

export function BlocoCodigo({ rotulo, children }: { rotulo?: string; children: string }) {
  return (
    <figure className="kx-sem-margem">
      {rotulo && <figcaption className="k-cap kx-cap-bloco">{rotulo}</figcaption>}
      <div className="k-card k-pad">
        <pre className="k-mono kx-pre">{children}</pre>
      </div>
    </figure>
  );
}

export function ListaDados({ itens }: { itens: { rotulo: string; valor: ReactNode }[] }) {
  return (
    <dl className="kx-dados">
      {itens.map((i) => (
        <div key={i.rotulo}>
          <dt className="k-cap">{i.rotulo}</dt>
          <dd>{i.valor}</dd>
        </div>
      ))}
    </dl>
  );
}

export function Ressalva({ children }: { children: ReactNode }) {
  return (
    <span className="kx-ressalva">
      <Icone nome="alert" tamanho={14} />
      <span>{children}</span>
    </span>
  );
}

/** "1.284.910 tokens" (exato) ou "1,3M tokens" (compacto); grande = número ≥ 24px, em accent. */
export function Tokens({ valor, compactar, grande }: { valor: number; compactar?: boolean; grande?: boolean }) {
  return (
    <span className={`k-tokens${grande ? " is-grande" : ""}`}>
      {compactar ? compacto(valor) : num(valor)} tokens
    </span>
  );
}
