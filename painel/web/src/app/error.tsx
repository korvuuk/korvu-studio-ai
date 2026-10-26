"use client";

import { useRouter } from "next/navigation";
import { startTransition } from "react";
import { Botao } from "@/components/Botao";
import EstadoPagina, { ComoResolver } from "@/components/EstadoPagina";
import { Codigo } from "@/components/Texto";
import { COMO_LIGAR, COMO_SINCRONIZAR } from "@/lib/comandos";

// Erro de página (design-system.md §12.2), dentro da casca: a barra lateral continua e o aviso do topo diz se o banco
// está fora do ar ou nunca sincronizou. Em produção o Next esconde a mensagem do servidor; os passos valem para os dois
// casos. "Tentar de novo" relê os dados do servidor (router.refresh) e remonta a página (reset).
export default function Erro({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  const router = useRouter();
  const fora = /fora do ar|fetch failed|ECONNREFUSED/i.test(error.message);
  const dev = process.env.NODE_ENV === "development";
  return (
    <EstadoPagina
      tipo="erro"
      icone="alert"
      titulo="Não deu para ler os dados"
      texto={fora
        ? "O banco do painel não respondeu. Isso costuma acontecer depois de reiniciar o Mac, quando o Docker ainda não subiu."
        : "O painel não conseguiu ler o banco. O aviso no topo da página diz se o banco está fora do ar ou se nunca foi sincronizado."}
      acoes={
        <Botao variante="primario" onClick={() => startTransition(() => { router.refresh(); reset(); })}>
          Tentar de novo
        </Botao>
      }
      codigo={dev ? <>Detalhe técnico: {error.message}</> : error.digest ? <>Código do erro (aparece no terminal do painel): {error.digest}</> : null}
    >
      <ComoResolver
        passos={[
          <>Abra o Docker e ligue o banco do painel: <Codigo>{COMO_LIGAR}</Codigo></>,
          <>Sincronize os arquivos com o banco: <Codigo>{COMO_SINCRONIZAR}</Codigo></>,
          <>Tente de novo.</>,
        ]}
      />
    </EstadoPagina>
  );
}
