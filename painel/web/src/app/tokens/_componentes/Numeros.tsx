import ErroBloco from "@/components/ErroBloco";
import { KpiLinha } from "@/components/Kpi";
import Vazio from "@/components/Vazio";
import { compactoPartes, num, porExtenso, usdPartes } from "@/lib/formato";
import { type LeituraTokens, lerTokens } from "@/lib/tokens";

// Tokens e custos · os quatro números (telas/tokens-e-custos.md): tokens (accent, decisão de 23/10) com o cache lido à
// parte, custo estimado em US$ (preço de tabela da API, sem câmbio: decisão de 24/10), agentes (quantos trabalharam nos
// 30 dias) e o custo médio entre quem trabalhou.

export default async function Numeros() {
  let t: LeituraTokens;
  try {
    t = await lerTokens();
  } catch {
    return <ErroBloco oque="Os números de consumo" />;
  }
  if (t.total.tokens === 0) {
    return (
      <Vazio icone="tokens-custos" titulo="Nenhuma sessão nos últimos 30 dias">
        Quando o Claude Code rodar neste projeto, os tokens e o custo equivalente aparecem aqui.
      </Vazio>
    );
  }
  const tk = compactoPartes(t.total.tokens);
  const n = t.trabalharam;
  const medio = n > 0 ? t.total.usd / n : null;
  return (
    <div className="k-grid k-grid--tiles">
      <KpiLinha
        className="k-span-3"
        rotulo="Tokens utilizados"
        valor={tk.valor}
        unidade={tk.unidade || undefined}
        tokens
        nota={t.total.cacheLido > 0 ? `+ ${porExtenso(t.total.cacheLido)} lidos do cache` : "nenhum token lido do cache"}
      />
      <KpiLinha
        className="k-span-3"
        rotulo="Custo estimado"
        prefixo="US$"
        valor={usdPartes(t.total.usd, 0).valor}
        nota="equivalente na API, preço de tabela"
      />
      <KpiLinha
        className="k-span-3"
        rotulo="Agentes"
        valor={num(t.agentes.length)}
        nota={`${num(n)} ${n === 1 ? "trabalhou" : "trabalharam"} nos 30 dias`}
      />
      <KpiLinha
        className="k-span-3"
        rotulo="Custo médio por agente"
        prefixo="US$"
        valor={medio != null ? usdPartes(medio, 2).valor : "—"}
        nota={n > 0 ? `entre ${n === 1 ? "o 1 que trabalhou" : `os ${num(n)} que trabalharam`}` : "ninguém trabalhou nos 30 dias"}
      />
    </div>
  );
}
