import { Suspense } from "react";
import { EsqueletoCard, EsqueletoKpis } from "@/components/Esqueleto";
import { BarraPagina, MetaPagina, Secao } from "@/components/Pagina";
import Consumo from "./_componentes/Consumo";
import CustoPorVideo from "./_componentes/CustoPorVideo";
import Meta from "./_componentes/Meta";
import Numeros from "./_componentes/Numeros";
import PorDepartamento from "./_componentes/PorDepartamento";
import PorModelo from "./_componentes/PorModelo";
import Projecao from "./_componentes/Projecao";
import QuemConsome from "./_componentes/QuemConsome";

// Tokens e custos — telas/tokens-e-custos.md + tokens-e-custos.html (APROVADO, área design, 23/10 21:04; dados liberados
// pelo PORTÃO-DADOS às 21:28). Tudo do banco: consumo_diario, consumo, execucoes_custo, e precos_modelo — o número
// é o do banco na hora da leitura, não o retrato da maquete. Custo em US$, sem câmbio (24/10); modelo sempre com
// a versão. A 1440, "quem mais consome" desce para o fim na largura toda (k-fim-ate-xl); a partir de 1600, 4 + 5 + 3.

export default function Tokens() {
  return (
    <>
      <BarraPagina titulo="Tokens e custos">
        <MetaPagina icone="calendario">
          <Suspense fallback="Últimos 30 dias · registros das sessões do Claude Code">
            <Meta />
          </Suspense>
        </MetaPagina>
      </BarraPagina>

      <Secao rotulo="Números do consumo">
        <Suspense fallback={<EsqueletoKpis oque="os números do consumo" />}>
          <Numeros />
        </Suspense>
      </Secao>

      <Secao rotulo="Consumo por dia e por modelo">
        <div className="k-grid">
          <Suspense fallback={<EsqueletoCard oque="o consumo por dia" className="k-span-8" altura={260} />}>
            <Consumo />
          </Suspense>
          <Suspense fallback={<EsqueletoCard oque="o consumo por modelo" className="k-span-4" altura={260} />}>
            <PorModelo />
          </Suspense>
        </div>
      </Secao>

      <Secao rotulo="Departamentos, agentes e vídeos">
        <div className="k-grid">
          <Suspense fallback={<EsqueletoCard oque="o consumo por departamento" className="k-span-6 k-xl-4" linhas={7} />}>
            <PorDepartamento />
          </Suspense>
          <Suspense fallback={<EsqueletoCard oque="quem mais consome" className="k-span-12 k-xl-5 k-fim-ate-xl" linhas={8} />}>
            <QuemConsome />
          </Suspense>
          <div className="k-span-6 k-xl-3 k-pilha">
            <Suspense fallback={<EsqueletoCard oque="o custo por vídeo" linhas={5} />}>
              <CustoPorVideo />
            </Suspense>
            <Suspense fallback={<EsqueletoCard oque="a projeção mensal" altura={96} />}>
              <Projecao />
            </Suspense>
          </div>
        </div>
      </Secao>
    </>
  );
}
