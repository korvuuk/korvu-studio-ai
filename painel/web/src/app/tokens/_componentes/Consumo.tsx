import type { ReactNode } from "react";
import { Card, CabecalhoGrafico } from "@/components/Card";
import ErroBloco from "@/components/ErroBloco";
import { Escolha, EscolhaBotoes, EscolhaPainel } from "@/components/Escolha";
import GraficoLinha from "@/components/GraficoLinha";
import { TabelaGemea } from "@/components/Graficos";
import Vazio from "@/components/Vazio";
import type { PrecoModelo } from "@/lib/db";
import { compacto, data, num, usd } from "@/lib/formato";
import { precos as lerPrecos } from "@/lib/leituras";
import { type LeituraTokens, lerTokens } from "@/lib/tokens";

// Tokens e custos · consumo. (telas/tokens-e-custos.md): os 30 dias, um ponto por dia (dia sem sessão = 0), Tokens |
// Custo no segmentado (troca a série e a frase), o pico marcado ("23 out · 8,4M"), dica por dia (hover e foco) e UMA
// tabela gêmea com tokens e US$. A nota diz a conta: preço de tabela da API (precos_modelo), em US$ sem câmbio.

const dinheiro = (v: number) => v.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const preco = (p: PrecoModelo) => `${p.nome} US$ ${num(p.entrada)}/${num(p.saida)}`;

export default async function Consumo() {
  let t: LeituraTokens, tabela: PrecoModelo[];
  try {
    [t, tabela] = await Promise.all([lerTokens(), lerPrecos()]);
  } catch {
    return <div className="k-span-8"><ErroBloco oque="O consumo por dia" /></div>;
  }
  const cab = (junto?: ReactNode, acao?: ReactNode) => (
    <CabecalhoGrafico id="t-cons" titulo="consumo." junto={junto} acao={acao} />
  );
  if (t.total.tokens === 0) {
    return (
      <Card como="section" className="kx-card-grafico k-span-8" aria-labelledby="t-cons">
        {cab()}
        <div className="kx-corpo-grafico">
          <Vazio icone="desempenho" titulo="Nenhum dia com consumo">Cada dia com sessão do Claude Code vira um ponto; dia sem sessão fica em zero.</Vazio>
        </div>
      </Card>
    );
  }
  const n = t.dias.length - 1;
  const ticks = [0, Math.round(n / 3), Math.round((2 * n) / 3), n];
  const rotuloDia = (dia: string) => data(`${dia}T12:00:00Z`);
  const pontos = t.dias.map((d) => rotuloDia(d.dia));
  const x = t.dias.map((_, i) => i);
  // os preços dos modelos que rodaram na janela, na ordem de quem mais consumiu (a mesma do "por modelo.")
  const tabelaPrecos = t.modelos.flatMap((m) => tabela.filter((p) => p.nome === m.nome).map(preco)).join(", ");
  const total = usd(t.total.usd, 0);

  return (
    <Card como="section" className="kx-card-grafico k-span-8" aria-labelledby="t-cons">
      <Escolha nome="medida" inicial="tk">
        {cab(
          <>
            <EscolhaPainel grupo="medida" valores={["tk"]} como="span" className="k-kpi-note">tokens por dia · {compacto(t.total.tokens)} em {t.janela.dias} dias</EscolhaPainel>
            <EscolhaPainel grupo="medida" valores={["us"]} como="span" className="k-kpi-note">custo por dia · {total} em {t.janela.dias} dias</EscolhaPainel>
          </>,
          <EscolhaBotoes grupo="medida" estilo="seg" rotulo="Medida do gráfico" controla="consumo-grafico" opcoes={[{ valor: "tk", rotulo: "Tokens" }, { valor: "us", rotulo: "Custo" }]} />,
        )}
        <div id="consumo-grafico" className="kx-corpo-grafico">
          <EscolhaPainel grupo="medida" valores={["tk"]}>
            <GraficoLinha
              rotulo={`Tokens por dia nos últimos ${t.janela.dias} dias`}
              x={x} ticksX={ticks} rotulosX={ticks.map((i) => pontos[i])} pontos={pontos}
              series={[{ nome: "Tokens", valores: t.dias.map((d) => d.tokens) }]}
              formato="compacto" pico semTabela
            />
          </EscolhaPainel>
          <EscolhaPainel grupo="medida" valores={["us"]}>
            <GraficoLinha
              rotulo={`Custo por dia nos últimos ${t.janela.dias} dias`}
              x={x} ticksX={ticks} rotulosX={ticks.map((i) => pontos[i])} pontos={pontos}
              series={[{ nome: "Custo", valores: t.dias.map((d) => d.usd) }]}
              formato="dolares" pico semTabela
            />
          </EscolhaPainel>
        </div>
      </Escolha>
      <p className="k-fonte kx-fonte-bloco">
        Sessões do Claude Code neste Mac, nesta pasta. Dia em zero = nenhuma sessão registrada. Custo = preço de tabela da
        API em dólar ({tabelaPrecos} por milhão de tokens de entrada/saída); com
        assinatura, a fatura é outra.
      </p>
      <TabelaGemea
        rotulo="Consumo por dia"
        colunas={["Dia", "Tokens", "Custo (US$)"]}
        linhas={t.dias.filter((d) => d.tokens > 0 || d.usd > 0).map((d) => [
          rotuloDia(d.dia), num(d.tokens), dinheiro(d.usd),
        ])}
      />
    </Card>
  );
}
