import { Card, CardCabecalho } from "@/components/Card";
import ErroBloco from "@/components/ErroBloco";
import { TabelaGemea } from "@/components/Graficos";
import Numeros from "@/components/Numeros";
import Vazio from "@/components/Vazio";
import { num } from "@/lib/formato";
import { snapshots } from "@/lib/leituras";
import { periodo } from "@/lib/perfil";

// Visão geral · Desempenho · 28 dias (telas/visao-geral.md): os três totais reais da Meta (visualizações, contas
// alcançadas, visitas ao perfil). A curva por dia da maquete é EXEMPLO: no app, até o perfil ser lido todo dia, só a frase
// — nenhuma curva inventada.

export default async function Desempenho28() {
  let s;
  try {
    s = (await snapshots()).at(-1);
  } catch {
    return <div className="k-span-12 k-xl-6"><ErroBloco oque="O desempenho de 28 dias" /></div>;
  }
  if (!s || (s.views == null && s.alcance == null && s.visitas_perfil == null)) {
    return (
      <Card como="section" pad className="k-span-12 k-xl-6" aria-label="Desempenho · 28 dias">
        <Vazio icone="desempenho" titulo="Sem números de 28 dias">Quando o scripts/perfil.py ler a conta, os totais aparecem aqui.</Vazio>
      </Card>
    );
  }
  const dias = s.janela_dias ?? 28;
  return (
    <Card como="section" pad className="k-span-12 k-xl-6" aria-labelledby="t-d28">
      <CardCabecalho titulo={<span id="t-d28">Desempenho · {dias} dias</span>} como="h2" acao={<span className="k-mono k-muted">{periodo(s)}</span>} />
      <Numeros
        solto
        itens={[
          { valor: num(s.views), rotulo: "visualizações", grande: true },
          { valor: num(s.alcance), rotulo: "contas alcançadas", grande: true },
          { valor: num(s.visitas_perfil), rotulo: "visitas ao perfil", grande: true },
        ]}
      />
      <p className="k-fonte kx-fonte-bloco">A curva por dia aparece quando o perfil for lido todo dia. Hoje a Meta só manda o total de {dias} dias.</p>
      <TabelaGemea
        rotulo={`Números do desempenho em ${dias} dias`}
        colunas={["O que existe", "Valor"]}
        linhas={[
          [`Visualizações · ${dias} dias`, num(s.views)],
          [`Contas alcançadas · ${dias} dias`, num(s.alcance)],
          [`Visitas ao perfil · ${dias} dias`, num(s.visitas_perfil)],
          ["Por dia", "ainda não chega"],
        ]}
      />
    </Card>
  );
}
