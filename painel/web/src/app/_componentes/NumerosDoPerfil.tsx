import { AnelMedidor } from "@/components/Anel";
import Capa from "@/components/Capa";
import ErroBloco from "@/components/ErroBloco";
import { Delta, Kpi } from "@/components/Kpi";
import Vazio from "@/components/Vazio";
import * as db from "@/lib/db";
import { capa } from "@/lib/capas";
import { compactoPartes, data, num } from "@/lib/formato";
import { metricas, snapshots } from "@/lib/leituras";
import { diferencaAbsoluta, foraDaBolha, variacao, variacaoPP } from "@/lib/perfil";
import { lerProducao } from "@/lib/producao";

// Visão geral · os quatro números do perfil (telas/visao-geral.md): seguidores, alcance de 28 dias, fora da bolha (com o
// anel) e o melhor vídeo até agora (maior alcance da última leitura confiável, com a capa; leva ao Desempenho).

export default async function NumerosDoPerfil() {
  let snaps: db.Snapshot[], mets: db.Metrica[], pubs: Awaited<ReturnType<typeof lerProducao>>["publicados"];
  try {
    [snaps, mets, { publicados: pubs }] = await Promise.all([snapshots(), metricas(), lerProducao()]);
  } catch {
    return <ErroBloco oque="Os números do perfil" />;
  }
  const atual = snaps.at(-1);
  if (!atual) {
    return (
      <Vazio icone="users" titulo="Ainda não há leitura do perfil">
        Quando o scripts/perfil.py ler a conta pela 1.ª vez, os números aparecem aqui.
      </Vazio>
    );
  }
  const anterior = snaps.length > 1 ? snaps.at(-2) : undefined;
  const quando = anterior ? data(anterior.lido_em) : "";
  const vSeg = variacao(atual.seguidores, anterior?.seguidores, quando);
  const vAlc = variacao(atual.alcance, anterior?.alcance, quando);
  const bolha = foraDaBolha(atual);
  const vBolha = variacaoPP(atual, anterior, quando);
  const alcance = atual.alcance != null ? compactoPartes(atual.alcance) : null;

  // melhor vídeo: maior alcance na última leitura confiável (leitura suspeita nunca entra)
  const ult = db.leiturasConfiaveis(mets);
  const melhor = pubs
    .map((p) => ({ p, m: ult.get(p.slug)?.m }))
    .filter((x) => x.m?.alcance != null)
    .sort((a, b) => (b.m!.alcance ?? 0) - (a.m!.alcance ?? 0))[0];

  const delta = (v: ReturnType<typeof variacao>) =>
    v && <Delta sentido={v.sentido} significado={v.significado} texto={v.texto} leitor={v.leitor} semSeta={v.quaseIgual} />;

  return (
    <div className="k-grid k-grid--tiles">
      <Kpi
        className="k-span-3"
        rotulo="Seguidores no Instagram"
        valor={num(atual.seguidores)}
        junto
        delta={delta(vSeg)}
        nota={atual.seguidores != null && anterior?.seguidores != null ? diferencaAbsoluta(atual.seguidores, anterior.seguidores, anterior.lido_em) : undefined}
      />
      <Kpi
        className="k-span-3"
        rotulo={`Alcance · ${atual.janela_dias ?? 28} dias`}
        valor={alcance?.valor ?? "—"}
        unidade={alcance ? `${alcance.unidade}${alcance.unidade ? "" : "contas"}` : undefined}
        junto
        delta={delta(vAlc)}
        nota={atual.views != null ? `${num(atual.views)} visualizações` : undefined}
      />
      <Kpi
        className="k-span-3"
        rotulo="Alcance fora da bolha"
        valor={bolha ? num(Math.round(bolha.fracao * 100)) : "—"}
        unidade={bolha ? "%" : undefined}
        junto
        delta={delta(vBolha)}
        nota={bolha ? `${num(bolha.nao)} de ${num(bolha.total)} não seguem` : "sem a divisão seguidor × não seguidor"}
        aside={bolha && <AnelMedidor fracao={bolha.fracao} rotulo={`${num(Math.round(bolha.fracao * 100))}% do alcance vem de quem não segue a conta`} />}
      />
      {melhor ? (
        <Kpi
          className="k-span-3"
          rotulo="Melhor vídeo até agora"
          valor={num(melhor.m!.alcance)}
          unidade="alcance"
          junto
          href="/desempenho"
          rotuloLink={`Melhor vídeo até agora: ${melhor.p.nome}, ${num(melhor.m!.alcance)} de alcance. Ver o desempenho`}
          destaque={melhor.p.nome}
          nota={`${data(melhor.p.publicado_em)} · ${num(melhor.m!.views)} visualizações`}
          comCapa
          aside={<Capa src={capa(melhor.p.slug, "publicados", "videos")} nome={melhor.p.nome} tamanho="lg" />}
        />
      ) : (
        <Kpi className="k-span-3" rotulo="Melhor vídeo até agora" valor="—" nota="nenhum Reel com leitura de métricas ainda" />
      )}
    </div>
  );
}
