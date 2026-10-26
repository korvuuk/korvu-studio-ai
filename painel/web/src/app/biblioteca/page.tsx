import { Suspense } from "react";
import { Escolha, EscolhaBotoes, EscolhaPainel } from "@/components/Escolha";
import { EsqueletoCard, EsqueletoCartoes } from "@/components/Esqueleto";
import { BarraPagina, Secao } from "@/components/Pagina";
import Abas, { ABAS } from "./_componentes/Abas";
import { Animacoes, Capas, Fontes, Legendas, Looks, Sistema } from "./_componentes/Acervo";
import { Armazenamento, SistemaLado } from "./_componentes/Lado";

// Biblioteca — o ACERVO DE ESTILOS (telas/biblioteca.md + .html, design aprovado em 25/10; decisão do Carlos de 24/10):
// looks de cor na foto dele, capas, legendas, fontes, animações e, só na aba própria, o Sistema; ao lado, Armazenamento
// e Sistema. Sem título visível (o h1 fica para o leitor de tela). As abas trocam o que aparece sem recarregar; "Tudo"
// mostra todos menos o Sistema. Cada bloco lê no próprio Suspense (esqueleto, erro de bloco, vazio com a frase).

const OPCOES_BASE = [
  { valor: "todos", rotulo: "Tudo" }, { valor: "looks", rotulo: "Looks de cor" }, { valor: "capas", rotulo: "Capas" },
  { valor: "legendas", rotulo: "Legendas" }, { valor: "fontes", rotulo: "Fontes" }, { valor: "anim", rotulo: "Animações" },
  { valor: "sistema", rotulo: "Sistema" },
];

export default function Biblioteca() {
  return (
    <Escolha nome="bib" inicial="todos" opcoesValidas={ABAS}>
      <BarraPagina titulo="Biblioteca" />
      <div className="kx-abas">
        <Suspense fallback={<EscolhaBotoes grupo="bib" estilo="filtros" rotulo="Mostrar" controla="acervo" opcoes={OPCOES_BASE} />}>
          <Abas />
        </Suspense>
      </div>
      <Secao rotulo="Acervo de estilos">
        <div className="k-grid">
          <div className="k-span-12 k-xl-9" id="acervo">
            <EscolhaPainel grupo="bib" valores={["todos", "looks"]} className="k-acervo-sec">
              <Suspense fallback={<EsqueletoCartoes n={5} classe="k-looks" oque="os looks de cor" />}><Looks /></Suspense>
            </EscolhaPainel>
            <EscolhaPainel grupo="bib" valores={["todos", "capas", "legendas"]} className="k-acervo-par">
              <EscolhaPainel grupo="bib" valores={["todos", "capas"]} className="k-acervo-5">
                <Suspense fallback={<EsqueletoCard oque="os estilos de capa" altura={200} />}><Capas /></Suspense>
              </EscolhaPainel>
              <EscolhaPainel grupo="bib" valores={["todos", "legendas"]} className="k-acervo-4">
                <Suspense fallback={<EsqueletoCard oque="os estilos de legenda" altura={200} />}><Legendas /></Suspense>
              </EscolhaPainel>
            </EscolhaPainel>
            <EscolhaPainel grupo="bib" valores={["todos", "fontes", "anim"]} className="k-acervo-par">
              <EscolhaPainel grupo="bib" valores={["todos", "fontes"]} className="k-acervo-5">
                <Suspense fallback={<EsqueletoCartoes n={4} classe="k-tipos" oque="as fontes" />}><Fontes /></Suspense>
              </EscolhaPainel>
              <EscolhaPainel grupo="bib" valores={["todos", "anim"]} className="k-acervo-4">
                <Suspense fallback={<EsqueletoCard oque="as animações" linhas={3} />}><Animacoes /></Suspense>
              </EscolhaPainel>
            </EscolhaPainel>
            <EscolhaPainel grupo="bib" valores={["sistema"]} className="k-acervo-sec">
              <Suspense fallback={<EsqueletoCartoes n={3} classe="k-sis-modelos" oque="o sistema" />}><Sistema /></Suspense>
            </EscolhaPainel>
          </div>
          <div className="k-span-12 k-xl-3 k-lado">
            <Suspense fallback={<EsqueletoCard oque="o armazenamento" linhas={5} />}><Armazenamento /></Suspense>
            <Suspense fallback={<EsqueletoCard oque="o sistema" linhas={8} />}><SistemaLado /></Suspense>
          </div>
        </div>
      </Secao>
    </Escolha>
  );
}
