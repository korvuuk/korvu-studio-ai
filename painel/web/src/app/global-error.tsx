"use client";

import { Botao } from "@/components/Botao";
import EstadoPagina, { ComoResolver } from "@/components/EstadoPagina";
import { Codigo } from "@/components/Texto";
import { COMO_LIGAR, COMO_SINCRONIZAR } from "@/lib/comandos";
import "./globals.css";

// Último recurso: o erro aconteceu no próprio layout (ex.: painel/web/.env.local sem as chaves do banco). Sem a casca,
// então a página diz tudo o que fazer — no mesmo estilo do erro de página (design-system.md §12.2).
export default function ErroGeral({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  const dev = process.env.NODE_ENV === "development";
  return (
    <html lang="pt-BR">
      <body>
        <main className="k-main" id="conteudo">
          <EstadoPagina
            tipo="erro"
            icone="alert"
            titulo="O painel não abriu"
            texto="Faltou algo para o painel ler o banco. Confira, nesta ordem:"
            acoes={<Botao variante="primario" onClick={() => reset()}>Tentar de novo</Botao>}
            codigo={dev ? <>Detalhe técnico: {error.message}</> : error.digest ? <>Código do erro: {error.digest}</> : null}
          >
            <ComoResolver
              passos={[
                <><Codigo>painel/web/.env.local</Codigo> com o endereço e a chave do banco do painel (sem mostrar os valores a ninguém).</>,
                <>O banco do painel ligado: <Codigo>{COMO_LIGAR}</Codigo></>,
                <>Os dados sincronizados: <Codigo>{COMO_SINCRONIZAR}</Codigo></>,
              ]}
            />
          </EstadoPagina>
        </main>
      </body>
    </html>
  );
}
