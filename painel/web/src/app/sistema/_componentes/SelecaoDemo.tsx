"use client";

import { useState } from "react";
import Selecao, { type Opcao } from "@/components/Selecao";

// Só para a vitrine: o dropdown com estado próprio. A única janela real dos dados do perfil é a de 28 dias da Meta.
export default function SelecaoDemo({ opcoes }: { opcoes: Opcao[] }) {
  const [valor, setValor] = useState(opcoes[0]?.valor ?? "");
  return <Selecao rotulo="Período" opcoes={opcoes} valor={valor} aoMudar={setValor} />;
}
