import ErroBloco from "@/components/ErroBloco";
import { Kpi } from "@/components/Kpi";
import { usd, usdPartes } from "@/lib/formato";
import { type LeituraTokens, lerTokens } from "@/lib/tokens";

// Tokens e custos · Projeção mensal (telas/tokens-e-custos.md, decisão de 24/10): a média diária dos últimos 30 dias
// (dia sem sessão = 0) × 30, em US$. É estimativa e vitrine — a mensalidade já está paga —, por isso sem delta.

const DIAS_RITMO = 30;

export default async function Projecao() {
  let t: LeituraTokens;
  try {
    t = await lerTokens();
  } catch {
    return <ErroBloco oque="A projeção mensal" />;
  }
  const dias = t.dias.slice(-DIAS_RITMO);
  const total = dias.reduce((s, d) => s + d.usd, 0);
  const media = total / DIAS_RITMO;
  if (total === 0) {
    return (
      <Kpi
        className="kx-projecao"
        rotulo="Projeção mensal"
        valor="—"
        nota={`Sem consumo nos últimos ${DIAS_RITMO} dias para projetar.`}
      />
    );
  }
  return (
    <Kpi
      className="kx-projecao"
      rotulo="Projeção mensal"
      prefixo="US$"
      valor={usdPartes(media * 30, 0).valor}
      nota={`média dos últimos ${DIAS_RITMO} dias (${usd(media)} por dia, dias sem sessão contam como zero) × 30. É estimativa: a mensalidade já está paga.`}
    />
  );
}
