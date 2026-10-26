import { Suspense } from "react";
import { EsqueletoCard, EsqueletoKpis } from "@/components/Esqueleto";
import { BarraPagina, MetaPagina, Secao } from "@/components/Pagina";
import Crescimento from "./_componentes/Crescimento";
import ForaDaBolha from "./_componentes/ForaDaBolha";
import Numeros from "./_componentes/Numeros";
import Periodo from "./_componentes/Periodo";
import Publico from "./_componentes/Publico";
import Ranking from "./_componentes/Ranking";

// Desempenho — telas/desempenho.md + desempenho.html (APROVADO, área design, 23/10 21:04). Cada bloco lê os seus dados
// no próprio Suspense: esqueleto enquanto carrega, erro de bloco se a leitura falhar, vazio com a frase do que fazer.
// Fontes: perfil_snapshots (números, crescimento, fora da bolha), perfil_demografia (países), metricas + publicacoes
// (ranking). Leitura `suspeito` nunca entra em gráfico, ranking nem conta.

export default function Desempenho() {
  return (
    <>
      <BarraPagina titulo="Desempenho">
        <MetaPagina icone="calendario">
          <Suspense fallback="Últimos 28 dias">
            <Periodo />
          </Suspense>
        </MetaPagina>
      </BarraPagina>

      <Secao rotulo="Números do perfil">
        <Suspense fallback={<EsqueletoKpis oque="os números do perfil" />}>
          <Numeros />
        </Suspense>
      </Secao>

      <Secao rotulo="Crescimento e alcance fora da bolha">
        <div className="k-grid">
          <Suspense fallback={<EsqueletoCard oque="o crescimento" className="k-span-8" altura={220} />}>
            <Crescimento />
          </Suspense>
          <Suspense fallback={<EsqueletoCard oque="o alcance fora da bolha" className="k-span-4" altura={220} />}>
            <ForaDaBolha />
          </Suspense>
        </div>
      </Secao>

      <Secao rotulo="Público e conteúdo que funciona">
        <div className="k-grid">
          <Suspense fallback={<EsqueletoCard oque="o público por país" className="k-span-12 k-xl-5" linhas={10} />}>
            <Publico />
          </Suspense>
          <Suspense fallback={<EsqueletoCard oque="o ranking dos Reels" className="k-span-12 k-xl-7" linhas={4} />}>
            <Ranking />
          </Suspense>
        </div>
      </Secao>
    </>
  );
}
