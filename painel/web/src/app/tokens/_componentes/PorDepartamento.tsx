import { Card, CabecalhoGrafico } from "@/components/Card";
import ErroBloco from "@/components/ErroBloco";
import { BarrasLargas, TabelaGemea } from "@/components/Graficos";
import Destaque from "@/components/Destaque";
import Vazio from "@/components/Vazio";
import { compacto, num, pct1, usd } from "@/lib/formato";
import { type LeituraTokens, lerTokens } from "@/lib/tokens";

// Tokens e custos · por departamento. (telas/tokens-e-custos.md): barras finas largas com tokens (accent-ink), custo em
// US$ e a parte dos tokens; o destaque diz quanto o 1.º departamento responde dos tokens e do custo e quanto fica com o
// roteiro. A direção é o Atlas (a sessão principal e os ajudantes dele).

const pctInteiro = (v: number, t: number) => (t > 0 ? `${num(Math.round((v / t) * 100))}%` : "—");
const dinheiro = (v: number) => v.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
// artigo do nome do departamento na frase ("O roteiro", "A direção")
const ARTIGO: Record<string, string> = { roteiro: "O" };

export default async function PorDepartamento() {
  let t: LeituraTokens;
  try {
    t = await lerTokens();
  } catch {
    return <div className="k-span-6 k-xl-4"><ErroBloco oque="O consumo por departamento" /></div>;
  }
  const cab = <CabecalhoGrafico id="t-dep" titulo="por departamento." acao={<span className="k-kpi-note">tokens · custo · %</span>} />;
  if (t.total.tokens === 0) {
    return (
      <Card como="section" className="kx-card-grafico k-span-6 k-xl-4" aria-labelledby="t-dep">
        {cab}
        <div className="kx-corpo-grafico">
          <Vazio icone="cpu" titulo="Sem consumo para dividir">Quando houver consumo, ele aparece dividido por modelo e por departamento.</Vazio>
        </div>
      </Card>
    );
  }
  const { tokens, usd: totalUsd } = t.total;
  const custo = (v: number) => usd(v);
  const deps = t.departamentos;
  const topo = deps[0];
  const nomeBase = (id: string) => (t.deps.find((d) => d.id === id)?.nome ?? id).toLowerCase();
  const quem = topo.id === t.diretor?.departamento_id && t.diretor
    ? `${ARTIGO[topo.id] ?? "A"} ${nomeBase(topo.id)} (o ${t.diretor.nome} conversando com você e coordenando a equipe)`
    : `${ARTIGO[topo.id] ?? "A"} ${nomeBase(topo.id)}`;
  const roteiro = deps.find((d) => d.id === "roteiro");
  const frase = `${quem} responde por ${pctInteiro(topo.tokens, tokens)} dos tokens e ${pctInteiro(topo.usd, totalUsd)} do custo.`
    + (roteiro && roteiro.id !== topo.id ? ` O roteiro fica com ${pctInteiro(roteiro.tokens, tokens)}.` : "");
  return (
    <Card como="section" className="kx-card-grafico k-span-6 k-xl-4" aria-labelledby="t-dep">
      {cab}
      <BarrasLargas
        rotulo="Consumo por departamento: tokens, custo e parte dos tokens"
        itens={deps.map((d) => ({
          rotulo: d.nome, valor: d.tokens, tokens: compacto(d.tokens), custo: custo(d.usd), parte: pct1((d.tokens / tokens) * 100),
          dica: `${num(d.tokens)} tokens · ${custo(d.usd)} · ${pct1((d.tokens / tokens) * 100)} dos tokens · ${pct1(totalUsd > 0 ? (d.usd / totalUsd) * 100 : 0)} do custo`,
        }))}
      />
      <Destaque className="kx-destaque-pe">{frase}</Destaque>
      <TabelaGemea
        rotulo="Consumo por departamento"
        colunas={["Departamento", "Tokens", "Custo (US$)"]}
        linhas={deps.map((d) => [d.nome, num(d.tokens), dinheiro(d.usd)])}
      />
    </Card>
  );
}
