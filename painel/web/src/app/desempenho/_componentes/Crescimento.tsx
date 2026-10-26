import { Card, CabecalhoGrafico } from "@/components/Card";
import ErroBloco from "@/components/ErroBloco";
import { TabelaGemea } from "@/components/Graficos";
import Vazio from "@/components/Vazio";
import { dataHora, num } from "@/lib/formato";
import { snapshots } from "@/lib/leituras";

// Desempenho · crescimento. (telas/desempenho.md, "Regras dos gráficos"): a curva por dia da maquete é EXEMPLO — o
// sincronizador só traz o total de 28 dias. No app, até a fonte existir: os dois totais e a frase, sem curva inventada.

export default async function Crescimento() {
  let s;
  try {
    s = (await snapshots()).at(-1);
  } catch {
    return <div className="k-span-8"><ErroBloco oque="O crescimento" /></div>;
  }
  const dias = s?.janela_dias ?? 28;
  return (
    <Card como="section" className="kx-card-grafico k-span-8" aria-labelledby="t-cres">
      <CabecalhoGrafico
        id="t-cres"
        titulo="crescimento."
        nota="visualizações e alcance por dia"
        acao={s && <span className="k-mono k-muted">{num(s.views)} visualizações · {num(s.alcance)} contas</span>}
      />
      <div className="kx-corpo-grafico">
        <Vazio icone="desempenho" titulo="Ainda não há dia a dia">
          {s
            ? <>A curva por dia aparece quando o perfil for lido todo dia. Hoje a Meta só manda o total de {dias} dias: {num(s.views)} visualizações e {num(s.alcance)} contas alcançadas.</>
            : <>Quando o scripts/perfil.py ler a conta todo dia, a curva de visualizações e alcance aparece aqui.</>}
        </Vazio>
      </div>
      {s && (
        <>
          <p className="k-fonte kx-fonte-bloco">Totais da API da Meta, {dias} dias até a leitura de {dataHora(s.lido_em)}.</p>
          <TabelaGemea
            rotulo="Crescimento em números"
            colunas={["O que existe", "Valor"]}
            linhas={[
              [`Visualizações · ${dias} dias`, num(s.views)],
              [`Alcance · ${dias} dias`, num(s.alcance)],
              ["Por dia", "ainda não chega"],
            ]}
          />
        </>
      )}
    </Card>
  );
}
