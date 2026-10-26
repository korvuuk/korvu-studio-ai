import type { ReactNode } from "react";
import Avatar from "./Avatar";

// Barra do app (topo das telas que o Carlos aprovou em 23/10, Main.dc.html): busca à esquerda; avisos, um fio e o dono
// à direita. Só em tela larga (≥ 1024px); na estreita, a busca vai para o menu e o sino para a barra de topo.
// O dono não é botão: não há login nem conta para trocar (design-system.md §1) — só diz de quem é o painel.

export function Dono() {
  return (
    <div className="k-dono">
      <Avatar nome="Carlos Mendes" tamanho={32} redondo />
      <span>
        <span className="k-dono-nome">Carlos</span>
        <span className="k-dono-papel">Proprietário</span>
      </span>
    </div>
  );
}

export default function BarraApp({ busca, avisos }: { busca: ReactNode; avisos: ReactNode }) {
  return (
    <header className="k-appbar">
      {busca}
      <div className="k-appbar-fim">
        {avisos}
        <span className="k-appbar-sep" aria-hidden="true" />
        <Dono />
      </div>
    </header>
  );
}
