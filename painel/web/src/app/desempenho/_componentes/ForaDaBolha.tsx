import { AnelMedidor } from "@/components/Anel";
import { Card, CabecalhoGrafico } from "@/components/Card";
import ErroBloco from "@/components/ErroBloco";
import { AmostraSerie, TabelaGemea } from "@/components/Graficos";
import Vazio from "@/components/Vazio";
import type { Snapshot } from "@/lib/db";
import { data, diasEntre, intervaloCurto, num } from "@/lib/formato";
import { snapshots } from "@/lib/leituras";
import { foraDaBolha } from "@/lib/perfil";
import { lerProducao } from "@/lib/producao";

// Desempenho · fora da bolha. (telas/desempenho.md): anel-medidor de UMA proporção (não seguidores em chart-1 sobre o
// trilho; dataviz: 2 fatias = um número), a legenda com as contas, e o pé com a mudança entre as duas leituras e quantos
// Trials estavam no ar até a leitura nova (publicacoes.trial preenchido = Trial).

export default async function ForaDaBolha() {
  let snaps: Snapshot[], pubs;
  try {
    [snaps, { publicados: pubs }] = await Promise.all([snapshots(), lerProducao()]);
  } catch {
    return <div className="k-span-4"><ErroBloco oque="O alcance fora da bolha" /></div>;
  }
  const atual = snaps.at(-1);
  const ant = snaps.length > 1 ? snaps.at(-2) : undefined;
  const bolha = foraDaBolha(atual);
  const cab = <CabecalhoGrafico id="t-bolha" titulo="fora da bolha." nota="quem os conteúdos alcançaram" />;
  if (!atual || !bolha) {
    return (
      <Card como="section" className="kx-card-grafico k-span-4" aria-labelledby="t-bolha">
        {cab}
        <div className="kx-corpo-grafico">
          <Vazio icone="users" titulo="Sem divisão seguidor × não seguidor">
            A Meta separa quem segue de quem não segue na janela de 28 dias; quando vier, aparece aqui.{atual ? ` (A leitura de ${data(atual.lido_em)} não trouxe essa divisão.)` : ""}
          </Vazio>
        </div>
      </Card>
    );
  }
  const pNao = Math.round(bolha.fracao * 100);
  const seguidores = bolha.total - bolha.nao;
  const antes = foraDaBolha(ant);
  const saldo = antes ? bolha.nao - antes.nao : null;
  const trials = pubs.filter((p) => p.trial && p.publicado_em && Date.parse(p.publicado_em) <= Date.parse(atual.lido_em)).length;
  const dias = ant ? diasEntre(ant.lido_em, atual.lido_em) : 0;
  return (
    <Card como="section" className="kx-card-grafico k-span-4" aria-labelledby="t-bolha">
      {cab}
      <div className="kx-bolha">
        <AnelMedidor
          fracao={bolha.fracao}
          tamanho={150}
          espessura={18}
          rotulo={`${pNao}% de quem os conteúdos alcançaram não segue a conta`}
          centro={
            <>
              <span className="k-num k-tokens is-grande kx-anel-total kx-anel-maior" aria-hidden="true">{pNao}%</span>
              <span className="k-kpi-note kx-fonte-ink2" aria-hidden="true">não seguidores</span>
            </>
          }
        />
        <div className="kx-bolha-legenda">
          <div>
            <AmostraSerie serie={1} rotulo="Não seguidores" />
            <span className="k-metric-l">{num(bolha.nao)} <small className="k-kpi-note">{pNao}%</small></span>
          </div>
          <div>
            <AmostraSerie serie="trilho" rotulo="Seguidores" />
            <span className="k-metric-l">{num(seguidores)} <small className="k-kpi-note">{100 - pNao}%</small></span>
          </div>
        </div>
      </div>
      {ant && antes && saldo != null && (
        <div className="kx-pe-card">
          <span className="k-kpi-note kx-fonte-ink2">
            Em {dias} {dias === 1 ? "dia" : "dias"} ({intervaloCurto(ant.lido_em, atual.lido_em)}){trials > 0 ? `, com ${trials} ${trials === 1 ? "Trial" : "Trials"} no ar` : ""}
          </span>
          <span className={`k-num kx-saldo${saldo > 0 ? " is-bom" : saldo < 0 ? " is-ruim" : ""}`}>
            {saldo > 0 ? "+" : saldo < 0 ? "−" : ""}{num(Math.abs(saldo))} não seguidores
          </span>
        </div>
      )}
      <TabelaGemea
        rotulo="Fora da bolha em números"
        colunas={ant && antes ? ["Quem foi alcançado", data(ant.lido_em), data(atual.lido_em)] : ["Quem foi alcançado", data(atual.lido_em)]}
        linhas={ant && antes
          ? [["Não seguidores", num(antes.nao), num(bolha.nao)], ["Seguidores", num(antes.total - antes.nao), num(seguidores)]]
          : [["Não seguidores", num(bolha.nao)], ["Seguidores", num(seguidores)]]}
      />
    </Card>
  );
}
