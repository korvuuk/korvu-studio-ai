"use client";

import { useEffect, useId, useRef, useState } from "react";
import { Botao, type Variante } from "./Botao";

// Pedido ao Claude Code (design-system.md §15.2, [PROPOSTA] aprovada): o painel SÓ LÊ (decisão de 22/10). "Novo vídeo",
// "Novo conteúdo", "Agendar publicação"… abrem um popover com o comando para copiar e colar no Claude Code. Esc fecha e
// devolve o foco ao botão; tocar fora fecha.

export default function Pedido({ rotulo, titulo, comando, frase = "O painel só lê. Copie o pedido e cole no Claude Code:", variante = "primario", pequeno }: {
  rotulo: string;
  /** título do popover: "Pedir um vídeo novo" */
  titulo: string;
  comando: string;
  frase?: string;
  variante?: Variante;
  pequeno?: boolean;
}) {
  const id = useId();
  const [aberto, setAberto] = useState(false);
  const [copiado, setCopiado] = useState(false);
  const caixa = useRef<HTMLDivElement>(null);
  const botao = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!aberto) return;
    const fora = (e: PointerEvent) => { if (!caixa.current?.contains(e.target as Node)) setAberto(false); };
    const tecla = (e: KeyboardEvent) => { if (e.key === "Escape") { setAberto(false); botao.current?.focus(); } };
    document.addEventListener("pointerdown", fora);
    document.addEventListener("keydown", tecla);
    return () => { document.removeEventListener("pointerdown", fora); document.removeEventListener("keydown", tecla); };
  }, [aberto]);

  return (
    <div className={`k-pedido${aberto ? " is-aberto" : ""}`} ref={caixa}>
      <Botao
        ref={botao}
        variante={variante}
        pequeno={pequeno}
        icone="plus"
        aria-expanded={aberto}
        aria-haspopup="dialog"
        aria-controls={`${id}-pedido`}
        onClick={() => { setAberto((a) => !a); setCopiado(false); }}
      >
        {rotulo}
      </Botao>
      <div id={`${id}-pedido`} className="k-menu" role="dialog" aria-label={titulo}>
        <span className="k-pedido-t">{titulo}</span>
        <p className="k-pedido-p">{frase}</p>
        <code className="k-code">{comando}</code>
        <Botao
          variante="secundario"
          pequeno
          icone={copiado ? "check" : undefined}
          onClick={async () => {
            try { await navigator.clipboard.writeText(comando); setCopiado(true); } catch { setCopiado(false); }
          }}
        >
          {copiado ? "Pedido copiado" : "Copiar o pedido"}
        </Botao>
        <span className="k-sr-only" aria-live="polite">{copiado ? "Pedido copiado" : ""}</span>
      </div>
    </div>
  );
}
