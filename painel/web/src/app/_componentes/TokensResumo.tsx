import { AnelPartes, LegendaPartes } from "@/components/Anel";
import { BotaoLink } from "@/components/Botao";
import { Card, CardCabecalho } from "@/components/Card";
import ErroBloco from "@/components/ErroBloco";
import { TabelaGemea } from "@/components/Graficos";
import Vazio from "@/components/Vazio";
import { compacto, num, usdPartes } from "@/lib/formato";
import { consumo30 } from "@/lib/leituras";

// Visão geral · Tokens e custos · 30 dias (telas/visao-geral.md): o consumo de IA dos registros do Claude Code, que o
// sincronizador grava no banco (consumo_diario). Rosca por modelo (até 3 fatias, total no centro em accent), as partes
// em accent-ink, e o custo estimado em US$, preço de tabela da API, sem câmbio (decisão de 24/10).

export default async function TokensResumo() {
  let linhas;
  try {
    linhas = await consumo30();
  } catch {
    return <div className="k-span-6 k-xl-3"><ErroBloco oque="O consumo de IA" /></div>;
  }
  const porModelo = new Map<string, { tokens: number; usd: number }>();
  for (const l of linhas) {
    const k = l.modelo_nome ?? l.modelo;
    const atual = porModelo.get(k) ?? { tokens: 0, usd: 0 };
    porModelo.set(k, { tokens: atual.tokens + l.tokens, usd: atual.usd + (l.usd ?? 0) });
  }
  const modelos = [...porModelo.entries()].map(([nome, v]) => ({ nome, ...v })).sort((a, b) => b.tokens - a.tokens);
  const total = modelos.reduce((s, m) => s + m.tokens, 0);
  const usd = modelos.reduce((s, m) => s + m.usd, 0);

  if (total === 0) {
    return (
      <Card como="section" pad className="k-span-6 k-xl-3" aria-label="Tokens e custos · 30 dias">
        <Vazio icone="tokens-custos" titulo="Nenhuma sessão nos últimos 30 dias">Quando o Claude Code trabalhar no projeto, o consumo aparece aqui.</Vazio>
      </Card>
    );
  }
  const parte = (t: number) => `${num(Math.round((t / total) * 100))}%`;
  const fatias = modelos.slice(0, 3);
  return (
    <Card como="section" pad className="k-span-6 k-xl-3 kx-coluna" aria-labelledby="t-tok">
      <CardCabecalho
        titulo={<span id="t-tok">Tokens e custos · 30 dias</span>}
        como="h2"
        acao={<BotaoLink href="/tokens" variante="fantasma" pequeno soIcone icone="chevron-right" aria-label="Ver tokens e custos" />}
      />
      <div className="kx-tokens-resumo">
        <AnelPartes
          rotulo={`Tokens por modelo: ${fatias.map((m) => `${m.nome} ${parte(m.tokens)}`).join(", ")}`}
          partes={fatias.map((m, i) => ({ rotulo: m.nome, valor: m.tokens, serie: (i + 1) as 1 | 2 | 3 }))}
          centro={<><span className="k-num k-tokens is-grande kx-anel-total">{compacto(total)}</span><span className="k-cap">tokens</span></>}
        />
        <LegendaPartes tokens itens={fatias.map((m, i) => ({ rotulo: m.nome, texto: parte(m.tokens), serie: (i + 1) as 1 | 2 | 3 }))} />
      </div>
      <div className="kx-custo-pe">
        <div className="kx-pilha-mini">
          <span className="k-cap">Custo estimado</span>
          <span className="k-kpi-note">
            equivalente na API · 30 dias · preço de tabela
          </span>
        </div>
        <span className="k-num k-metric-l">
          <small className="kx-moeda">US$</small>{usdPartes(usd, 0).valor}
        </span>
      </div>
      <TabelaGemea
        rotulo="Tokens por modelo"
        colunas={["Modelo", "Tokens", "Custo (US$)"]}
        linhas={modelos.map((m) => [m.nome, num(m.tokens), m.usd.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })])}
      />
    </Card>
  );
}
