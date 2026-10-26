"use client";

import { usePathname } from "next/navigation";
import { useEffect, useId, useRef, useState } from "react";
import { Botao, BotaoLink } from "./Botao";
import Nota from "./Nota";

// Avisos — o sino da barra do app (design-system.md §15.2, "Avisos (popover do sino)"): a MESMA lista de "Precisam de
// atenção" da Produção de conteúdo (§15.1), calculada dos dados no servidor (lib/producao.ts). O painel só lê: não
// existe "lida/não lida"; o ponto laranja no sino quer dizer "há aviso agora". Fecha com Esc (o foco volta ao sino), ao
// tocar fora e ao trocar de página.

export type Aviso = { id: string; tom: "portao" | "alerta"; icone?: "camera" | "lock" | "alert"; titulo: string; corpo: string; acao?: { rotulo: string; href: string } };

export default function Avisos({ avisos }: {
  /** null = não deu para ler o banco; sem a prop = ainda lendo */
  avisos?: Aviso[] | null;
}) {
  const id = useId();
  const caminho = usePathname();
  const [aberto, setAberto] = useState(false);
  const caixa = useRef<HTMLDivElement>(null);
  const botao = useRef<HTMLButtonElement>(null);
  const n = avisos?.length ?? 0;

  useEffect(() => setAberto(false), [caminho]);

  useEffect(() => {
    if (!aberto) return;
    const fora = (e: PointerEvent) => {
      if (!caixa.current?.contains(e.target as Node)) setAberto(false);
    };
    const tecla = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setAberto(false);
        botao.current?.focus();
      }
    };
    document.addEventListener("pointerdown", fora);
    document.addEventListener("keydown", tecla);
    return () => {
      document.removeEventListener("pointerdown", fora);
      document.removeEventListener("keydown", tecla);
    };
  }, [aberto]);

  const nome = avisos === undefined ? "Avisos: lendo o banco" : avisos === null ? "Avisos: não deu para ler o banco" : `Avisos: ${n}`;

  return (
    <div className="kx-avisos" ref={caixa}>
      <Botao
        ref={botao}
        soIcone
        icone="bell"
        tamanhoIcone={18}
        variante="fantasma"
        aria-label={nome}
        aria-expanded={aberto}
        aria-controls={`${id}-painel`}
        className={`k-avisos${n > 0 ? " tem-aviso" : ""}`}
        onClick={() => setAberto((a) => !a)}
      />
      <div id={`${id}-painel`} className="k-menu kx-avisos-painel" role="region" aria-label="Avisos" hidden={!aberto}>
        <p className="k-card-title kx-avisos-cab">
          Avisos{avisos ? ` · ${n}` : ""}
        </p>
        {avisos === undefined ? (
          <Nota titulo="Lendo os avisos…">O que precisar da sua atenção aparece aqui.</Nota>
        ) : avisos === null ? (
          <Nota tom="alerta" titulo="Não deu para ler os avisos">
            O banco do painel não respondeu. O aviso no topo da página diz o que fazer.
          </Nota>
        ) : n === 0 ? (
          <Nota tom="ok" titulo="Nada pede atenção agora">
            Quando um roteiro esperar gravação, um pronto não puder sair ou um portão parar, aparece aqui.
          </Nota>
        ) : (
          <ul className="kx-avisos-lista kx-lista-limpa">
            {avisos.map((a) => (
              <li key={a.id}>
                <Nota
                  tom={a.tom}
                  icone={a.icone}
                  titulo={a.titulo}
                  acoes={a.acao && (
                    <BotaoLink variante="secundario" pequeno href={a.acao.href} onClick={() => setAberto(false)}>
                      {a.acao.rotulo}
                    </BotaoLink>
                  )}
                >
                  {a.corpo}
                </Nota>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
