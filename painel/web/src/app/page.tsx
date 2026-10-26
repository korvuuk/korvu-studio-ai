import { Suspense } from "react";
import { BotaoLink } from "@/components/Botao";
import { EsqueletoCard, EsqueletoCartoes, EsqueletoKpis } from "@/components/Esqueleto";
import { BarraPagina, MetaPagina, Secao } from "@/components/Pagina";
import { diaLongo } from "@/lib/formato";
import Desempenho28 from "./_componentes/Desempenho28";
import EquipeResumo from "./_componentes/EquipeResumo";
import NumerosDoPerfil from "./_componentes/NumerosDoPerfil";
import { ContagemDaFila, ProximasPublicacoes } from "./_componentes/ProximasPublicacoes";
import PublicoPaises from "./_componentes/PublicoPaises";
import TokensResumo from "./_componentes/TokensResumo";

// Visão geral — telas/visao-geral.md + visao-geral.html (APROVADO, área design, 23/10 21:04). Cada bloco lê os seus
// dados no próprio Suspense: esqueleto enquanto carrega, erro de bloco se a leitura falhar, vazio com a frase.

export default function VisaoGeral() {
  return (
    <>
      <BarraPagina titulo="Visão geral">
        <MetaPagina icone="calendario">{diaLongo(new Date())}</MetaPagina>
      </BarraPagina>

      <Secao rotulo="Números do perfil">
        <Suspense fallback={<EsqueletoKpis oque="os números do perfil" />}>
          <NumerosDoPerfil />
        </Suspense>
      </Secao>

      <Secao
        titulo="Próximas publicações"
        estilo="h3"
        sub={<Suspense fallback="horário de Londres"><ContagemDaFila /></Suspense>}
        acao={<BotaoLink href="/calendario" variante="fantasma" pequeno iconeFim="chevron-right">Ver calendário</BotaoLink>}
      >
        <Suspense fallback={<EsqueletoCartoes n={5} oque="as próximas publicações" />}>
          <ProximasPublicacoes />
        </Suspense>
      </Secao>

      <Secao rotulo="Desempenho, público e consumo de IA">
        <div className="k-grid">
          <Suspense fallback={<EsqueletoCard oque="o desempenho de 28 dias" className="k-span-12 k-xl-6" altura={140} />}>
            <Desempenho28 />
          </Suspense>
          <Suspense fallback={<EsqueletoCard oque="o público por país" className="k-span-6 k-xl-3" linhas={10} />}>
            <PublicoPaises />
          </Suspense>
          <Suspense fallback={<EsqueletoCard oque="o consumo de IA" className="k-span-6 k-xl-3" altura={112} />}>
            <TokensResumo />
          </Suspense>
        </div>
      </Secao>

      <Suspense fallback={<Secao titulo="Equipe" estilo="h3"><EsqueletoCartoes n={5} classe="k-agentes" oque="a equipe" /></Secao>}>
        <EquipeResumo />
      </Suspense>
    </>
  );
}
