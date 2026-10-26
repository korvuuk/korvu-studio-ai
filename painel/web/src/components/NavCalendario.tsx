"use client";

import { useRouter } from "next/navigation";
import { useTransition } from "react";
import { Botao } from "./Botao";

// Navegação do calendário (telas/calendario.md "Interações"): Hoje, ‹ ›, o título do período e Mês | Semana. O estado
// fica no endereço (?vista=semana&dia=2026-10-18): o servidor desenha o período pedido; os botões só trocam o endereço.

export default function NavCalendario({ vista, titulo, anterior, proximo, hoje }: {
  vista: "mes" | "semana";
  /** "Outubro 2026" ou "18 – 24 out 2026" */
  titulo: string;
  /** o dia (AAAA-MM-DD) do período anterior e do próximo */
  anterior: string;
  proximo: string;
  hoje: string;
}) {
  const router = useRouter();
  const [carregando, iniciar] = useTransition();
  const ir = (v: "mes" | "semana", dia: string) => iniciar(() => router.push(`/calendario?vista=${v}&dia=${dia}`, { scroll: false }));
  const unidade = vista === "mes" ? "mês" : "semana";
  return (
    <div className={`k-cal-nav${carregando ? " is-atualizando" : ""}`}>
      <Botao variante="secundario" pequeno onClick={() => ir(vista, hoje)}>Hoje</Botao>
      <Botao variante="fantasma" pequeno soIcone icone="chevron-right" aria-label={`${vista === "mes" ? "Mês" : "Semana"} anterior`} className="kx-gira" onClick={() => ir(vista, anterior)} />
      <Botao variante="fantasma" pequeno soIcone icone="chevron-right" aria-label={`Próxim${vista === "mes" ? "o" : "a"} ${unidade}`} onClick={() => ir(vista, proximo)} />
      <h2 className="k-h3" aria-live="polite">{titulo}</h2>
    </div>
  );
}

export function VistaCalendario({ vista, dia }: { vista: "mes" | "semana"; dia: string }) {
  const router = useRouter();
  const [, iniciar] = useTransition();
  const ir = (v: "mes" | "semana") => iniciar(() => router.push(`/calendario?vista=${v}&dia=${dia}`, { scroll: false }));
  return (
    <div className="k-seg is-alto" role="group" aria-label="Visualização">
      <button type="button" aria-pressed={vista === "mes"} onClick={() => ir("mes")}>Mês</button>
      <button type="button" aria-pressed={vista === "semana"} onClick={() => ir("semana")}>Semana</button>
    </div>
  );
}

