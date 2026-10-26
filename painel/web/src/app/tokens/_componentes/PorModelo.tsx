import { AnelPartes, LegendaPartesKv } from "@/components/Anel";
import { Card, CabecalhoGrafico } from "@/components/Card";
import ErroBloco from "@/components/ErroBloco";
import { TabelaGemea } from "@/components/Graficos";
import Vazio from "@/components/Vazio";
import { compacto, num, usd } from "@/lib/formato";
import { type LeituraTokens, lerTokens } from "@/lib/tokens";

// Tokens e custos · por modelo. (telas/tokens-e-custos.md): rosca de até 3 fatias (chart-1…3, partes de um todo), o
// total no centro em accent; cada modelo com a versão (precos_modelo.nome), a parte dos tokens e o custo em US$ com a
// parte do custo. A frase do pé aponta o modelo que pesa mais no custo do que nos tokens, se houver.

const pctInteiro = (v: number, t: number) => (t > 0 ? `${num(Math.round((v / t) * 100))}%` : "—");
const dinheiro = (v: number) => v.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

export default async function PorModelo() {
  let t: LeituraTokens;
  try {
    t = await lerTokens();
  } catch {
    return <div className="k-span-4"><ErroBloco oque="O consumo por modelo" /></div>;
  }
  const cab = <CabecalhoGrafico id="t-mod" titulo="por modelo." />;
  if (t.total.tokens === 0) {
    return (
      <Card como="section" className="kx-card-grafico k-span-4" aria-labelledby="t-mod">
        {cab}
        <div className="kx-corpo-grafico">
          <Vazio icone="cpu" titulo="Sem consumo para dividir">Quando houver consumo, ele aparece dividido por modelo e por departamento.</Vazio>
        </div>
      </Card>
    );
  }
  const { tokens, usd: totalUsd } = t.total;
  const custo = (v: number) => usd(v);
  const fatias = t.modelos.slice(0, 3);
  // o modelo cuja parte no custo é bem maior que a parte nos tokens (ex.: 5 % dos tokens e 15 % do custo)
  const pesa = [...t.modelos]
    .filter((m) => m.tokens > 0 && totalUsd > 0)
    .map((m) => ({ m, r: (m.usd / totalUsd) / (m.tokens / tokens) }))
    .sort((a, b) => b.r - a.r)[0];
  const frase = pesa && pesa.r >= 1.5 && t.modelos.length > 1
    ? `O ${pesa.m.nome} é ${pctInteiro(pesa.m.tokens, tokens)} dos tokens e ${pctInteiro(pesa.m.usd, totalUsd)} do custo. `
    : "";
  return (
    <Card como="section" className="kx-card-grafico k-span-4" aria-labelledby="t-mod">
      {cab}
      <div className="kx-modelos">
        <AnelPartes
          tamanho={140}
          espessura={18}
          rotulo={`Tokens por modelo: ${fatias.map((m) => `${m.nome} ${pctInteiro(m.tokens, tokens)}`).join(", ")}`}
          partes={fatias.map((m, i) => ({ rotulo: m.nome, valor: m.tokens, serie: (i + 1) as 1 | 2 | 3 }))}
          centro={<><span className="k-num k-tokens is-grande kx-anel-total">{compacto(tokens)}</span><span className="k-cap kx-anel-cap">tokens</span></>}
        />
        <LegendaPartesKv
          itens={fatias.map((m, i) => ({
            rotulo: m.nome,
            serie: (i + 1) as 1 | 2 | 3,
            tokens: `${pctInteiro(m.tokens, tokens)} dos tokens`,
            custo: `${custo(m.usd)} · ${pctInteiro(m.usd, totalUsd)} do custo`,
          }))}
        />
      </div>
      <p className="k-fonte kx-pe-card">{frase}ElevenLabs (transcrição e música) fica de fora: ainda sem medição.</p>
      <TabelaGemea
        rotulo="Tokens por modelo"
        colunas={["Modelo", "Tokens", "Custo (US$)"]}
        linhas={t.modelos.map((m) => [m.nome, num(m.tokens), dinheiro(m.usd)])}
      />
    </Card>
  );
}
