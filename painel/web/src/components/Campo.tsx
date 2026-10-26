import type { ComponentProps } from "react";
import Icone from "./Icone";

// Campos de formulário. O design system só desenhou a busca (k-search) e o gatilho do dropdown (k-select); o formulário
// de "Contratar" precisa de texto, texto longo e escolha. Mesma roupa da busca: 36px, raio 8, surface, borda
// line-strong, foco = borda ink + halo de 3px accent-soft. Rótulo em caption acima, sempre ligado ao campo.
// (Acréscimo do front-end — vai à designer-de-produto para entrar no livro.)

type Base = { rotulo: string };

export function CampoTexto({ rotulo, ...resto }: Base & ComponentProps<"input">) {
  return (
    <label className="kx-campo">
      <span className="k-cap">{rotulo}</span>
      <input className="kx-entrada" {...resto} />
    </label>
  );
}

export function CampoTextoLongo({ rotulo, rows = 3, ...resto }: Base & ComponentProps<"textarea">) {
  return (
    <label className="kx-campo">
      <span className="k-cap">{rotulo}</span>
      <textarea className="kx-entrada" rows={rows} {...resto} />
    </label>
  );
}

export function CampoEscolha({ rotulo, opcoes, ...resto }: Base & { opcoes: { valor: string; rotulo: string }[] } & ComponentProps<"select">) {
  return (
    <label className="kx-campo">
      <span className="k-cap">{rotulo}</span>
      <span className="kx-escolha">
        <select className="kx-entrada" {...resto}>
          {opcoes.map((o) => <option key={o.valor} value={o.valor}>{o.rotulo}</option>)}
        </select>
        <Icone nome="chevron-down" tamanho={16} />
      </span>
    </label>
  );
}
