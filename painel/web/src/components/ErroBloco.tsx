"use client";

import { useRouter } from "next/navigation";
import { startTransition } from "react";
import { Botao } from "./Botao";
import Nota from "./Nota";

// Erro de bloco (design-system.md §12.2): uma parte da página não carregou; o resto continua valendo.
// k-card > k-note--alert + "Tentar de novo" (relê os dados do servidor).
export default function ErroBloco({ oque }: { oque?: string }) {
  const router = useRouter();
  return (
    <div className="k-card">
      <Nota
        tom="alerta"
        papel="alert"
        titulo="Não deu para carregar esta parte"
        acoes={<Botao variante="secundario" pequeno onClick={() => startTransition(() => router.refresh())}>Tentar de novo</Botao>}
      >
        {oque ? `Esta parte (${oque.charAt(0).toLocaleLowerCase("pt-BR")}${oque.slice(1)}) não veio do banco. ` : ""}O resto da página continua valendo. Se repetir, veja se o banco do painel está ligado.
      </Nota>
    </div>
  );
}
