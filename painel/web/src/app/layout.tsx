import type { Metadata } from "next";
import { cache, Suspense } from "react";
import Avisos from "@/components/Avisos";
import BarraApp from "@/components/BarraApp";
import Busca from "@/components/Busca";
import { Card } from "@/components/Card";
import Casca from "@/components/Casca";
import Dicas from "@/components/Dicas";
import Nota from "@/components/Nota";
import { Codigo } from "@/components/Texto";
import { avisosDaCasca, contagemDaEquipe, itensDaBusca } from "@/lib/casca";
import { COMO_LIGAR, COMO_SINCRONIZAR, estadoDoBanco } from "@/lib/db";
import { dataHora } from "@/lib/formato";
import { PAGINAS } from "@/lib/navegacao";
import "./globals.css";

// As fontes (Geist e Geist Mono, OFL) vêm do @font-face local de ./design/tokens.css — nada do Google.
export const metadata: Metadata = { title: "korvu. painel", description: "Equipe, produção, portões e desempenho do CONTENT AI" };
export const dynamic = "force-dynamic";

// ── peças da casca que dependem do banco: cada uma no seu Suspense, para a casca e o esqueleto da página não esperarem ──

async function ContagemEquipe() {
  const n = await contagemDaEquipe();
  if (n === null) return null;
  return <span className="k-nav-count">{n}<span className="k-sr-only"> pessoas</span></span>;
}

const buscaSoPaginas = PAGINAS.map((p) => ({ tipo: "Página" as const, rotulo: p.nome, href: p.href }));
async function BuscaComDados() {
  return <Busca itens={await itensDaBusca()} />;
}

async function AvisosComDados() {
  return <Avisos avisos={await avisosDaCasca()} />;
}

const lerBanco = cache(estadoDoBanco); // uma consulta por pedido, para o aviso do topo e o rodapé

/** Banco fora do ar ou nunca sincronizado: nota de alerta no topo da página, antes do h1 (design-system.md §12.5). */
async function AvisoDoBanco() {
  const banco = await lerBanco();
  if (banco.estado === "ok") return null;
  const nota = {
    nunca: { titulo: "O banco do painel nunca foi sincronizado", corpo: <>Traga os arquivos do projeto para o banco: <Codigo>{COMO_SINCRONIZAR}</Codigo></> },
    fora: { titulo: "O banco do painel está fora do ar", corpo: <>Acontece depois de reiniciar o Mac, quando o Docker ainda não subiu. Ligue com <Codigo>{COMO_LIGAR}</Codigo></> },
    erro: { titulo: "O banco do painel respondeu com erro", corpo: <>{banco.estado === "erro" ? banco.detalhe : ""}. Rode <Codigo>{COMO_SINCRONIZAR}</Codigo> e veja o erro no terminal.</> },
  }[banco.estado];
  return (
    <Card className="kx-aviso-banco">
      <Nota tom="alerta" titulo={nota.titulo} papel="alert">{nota.corpo}</Nota>
    </Card>
  );
}

/** Tudo certo: uma linha discreta no rodapé da área principal (design-system.md §12.5). */
async function Rodape() {
  const banco = await lerBanco();
  return (
    <footer className="k-fonte kx-rodape">
      @korvu_oficial{banco.estado === "ok" ? ` · sincronizado em ${dataHora(banco.em)}` : ""} · o painel só lê os arquivos do projeto
    </footer>
  );
}

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>
        <a className="k-skip" href="#conteudo">Pular para o conteúdo</a>
        <Casca
          contagens={{ "/equipe": <Suspense fallback={null}><ContagemEquipe /></Suspense> }}
          buscaMenu={<Suspense fallback={<Busca itens={buscaSoPaginas} />}><BuscaComDados /></Suspense>}
          avisosTopo={<Suspense fallback={<Avisos />}><AvisosComDados /></Suspense>}
          barraApp={
            <BarraApp
              busca={<Suspense fallback={<Busca itens={buscaSoPaginas} />}><BuscaComDados /></Suspense>}
              avisos={<Suspense fallback={<Avisos />}><AvisosComDados /></Suspense>}
            />
          }
        >
          <Suspense fallback={null}><AvisoDoBanco /></Suspense>
          {children}
          <Suspense fallback={<footer className="k-fonte kx-rodape">@korvu_oficial · o painel só lê os arquivos do projeto</footer>}>
            <Rodape />
          </Suspense>
        </Casca>
        <Dicas />
      </body>
    </html>
  );
}
