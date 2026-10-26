import { Card, CabecalhoGrafico } from "@/components/Card";
import Dica from "@/components/Dica";
import ErroBloco from "@/components/ErroBloco";
import { Medidor, PosicaoRanking } from "@/components/Graficos";
import Destaque from "@/components/Destaque";
import { CelulaCapa, TabelaNoCard } from "@/components/Tabela";
import Vazio from "@/components/Vazio";
import { capa } from "@/lib/capas";
import { data, diasEntre, minSeg, num, pct1, seg } from "@/lib/formato";
import { lerProducao, type PostPublicado } from "@/lib/producao";

// Desempenho · conteúdo que funciona. (telas/desempenho.md): ranking por alcance da ÚLTIMA LEITURA CONFIÁVEL de cada Reel
// (leitura `suspeito` nunca entra: vale a anterior, com a data dela escrita na linha). Top 3 com fundo surface-hover e a
// posição escrita. % assistido = tempo médio ÷ duração (medidor de 0 a 100 %); engajamento = interações ÷ alcance.
// Fora da maquete, por não estar no banco: a coluna "Não seguidores" por Reel (a API não separa por post; vinha dos
// prints do app) — o destaque usa o alcance, que está no banco.

const LEITURA_DEPOIS_DIAS = 5; // scripts/metricas.py (launchd 09:30) lê o Reel 5 dias depois de publicar

type Linha = { p: PostPublicado; m: NonNullable<PostPublicado["leitura"]> };

const interacoes = (m: Linha["m"]) =>
  [m.curtidas, m.comentarios, m.salvamentos, m.compartilhamentos].reduce<number>((s, x) => s + (x ?? 0), 0);
const assistido = (l: Linha) =>
  l.m.pct_assistido ?? (l.m.tempo_medio_s != null && l.p.duracao_s ? (l.m.tempo_medio_s / l.p.duracao_s) * 100 : null);

/** Os Reels que ainda não entram, escritos no cabeçalho: "Livro ChatGPT A entra em 27 out". */
function foraDoRanking(pubs: PostPublicado[], hoje: Date): string[] {
  return pubs.flatMap((p) => {
    if (!p.leitura && p.descartadas.length === 0) {
      if (!p.publicado_em) return [`${p.nome} ainda sem leitura`];
      const quando = new Date(Date.parse(p.publicado_em) + LEITURA_DEPOIS_DIAS * 86_400_000);
      return [diasEntre(hoje, quando) >= 0 ? `${p.nome} entra em ${data(quando.toISOString())}` : `${p.nome} ainda sem leitura`];
    }
    if (!p.leitura) return [`${p.nome} fora: só leituras descartadas`];
    if (p.leitura.alcance == null) return [`${p.nome} fora: a leitura não trouxe o alcance`];
    return [];
  });
}

/** O destaque com o que está no banco: o alcance dos Reels normais × o dos Trials (contas somadas por Reel). */
function destaque(linhas: Linha[]): string | null {
  const normais = linhas.filter((l) => !l.p.trial);
  const trials = linhas.filter((l) => l.p.trial);
  if (!normais.length || !trials.length) return null;
  const soma = (ls: Linha[]) => ls.reduce((s, l) => s + (l.m.alcance ?? 0), 0);
  const a = normais.length === 1
    ? `O único Reel normal, ${normais[0].p.nome}, alcançou ${num(soma(normais))} contas.`
    : `Os ${normais.length} Reels normais somam ${num(soma(normais))} contas alcançadas.`;
  const b = trials.length === 1
    ? ` O único Trial, ${trials[0].p.nome}, alcançou ${num(soma(trials))}.`
    : ` Os ${trials.length} Trials somados alcançaram ${num(soma(trials))}.`;
  return a + b;
}

export default async function Ranking() {
  let pubs: PostPublicado[];
  try {
    ({ publicados: pubs } = await lerProducao());
  } catch {
    return <div className="k-span-12 k-xl-7"><ErroBloco oque="O ranking dos Reels" /></div>;
  }
  const linhas: Linha[] = pubs
    .filter((p): p is PostPublicado & { leitura: Linha["m"] } => p.leitura?.alcance != null)
    .map((p) => ({ p, m: p.leitura }))
    .sort((a, b) => (b.m.alcance ?? 0) - (a.m.alcance ?? 0) || (b.m.views ?? 0) - (a.m.views ?? 0));
  const fora = foraDoRanking(pubs, new Date());
  const frase = destaque(linhas);

  return (
    <Card como="section" className="kx-card-grafico k-span-12 k-xl-7" aria-labelledby="t-rank">
      <CabecalhoGrafico
        id="t-rank"
        titulo="conteúdo que funciona."
        nota="ranking por alcance · Reels com leitura"
        acao={fora.length > 0 && <span className="k-kpi-note">{fora.join(" · ")}</span>}
      />
      {linhas.length === 0 ? (
        <div className="kx-corpo-grafico">
          <Vazio icone="play" titulo="Nenhum Reel com leitura ainda">
            A 1.ª leitura sai {LEITURA_DEPOIS_DIAS} dias depois de cada post (scripts/metricas.py); os Reels lidos aparecem aqui, do maior alcance para o menor.
          </Vazio>
        </div>
      ) : (
        <>
          <div className="kx-corpo-grafico">
            <TabelaNoCard
              rotulo="Ranking dos Reels por alcance"
              min={720}
              colunas={[
                { t: "#" }, { t: "Vídeo" }, { t: "Views", dir: true }, { t: "Alcance", dir: true },
                { t: "% assistido" }, { t: "Engajamento", dir: true }, { t: "Seg. ganhos", dir: true },
              ]}
            >
              {linhas.map((l, i) => {
                const pa = assistido(l);
                const inter = interacoes(l.m);
                const alc = l.m.alcance ?? 0;
                const descartada = l.p.descartadas[0];
                return (
                  <tr key={l.p.slug} className={i < 3 ? "is-top" : undefined}>
                    <td><PosicaoRanking n={i + 1} /></td>
                    <td>
                      <CelulaCapa
                        nome={l.p.nome}
                        src={capa(l.p.slug, "publicados", "videos")}
                        tamanho="sm"
                        href="/producao#publicados"
                        meta={`${data(l.p.publicado_em)} · ${l.p.trial ? "Trial" : "Normal"} · ${minSeg(l.p.duracao_s)}`}
                      />
                    </td>
                    <td className="k-dir"><span className="k-n">{num(l.m.views)}</span></td>
                    <td className="k-dir"><span className={`k-n${i === 0 ? " k-valor-foco" : ""}`}>{num(l.m.alcance)}</span></td>
                    <td>
                      <Medidor
                        pct={pa}
                        dica={{
                          titulo: "Tempo médio assistido ÷ duração",
                          detalhe: `${seg(l.m.tempo_medio_s)} de ${minSeg(l.p.duracao_s)}${descartada ? ` · leitura de ${data(l.m.lido_em)}; a de ${data(descartada.lido_em)} ficou de fora (número impossível da API)` : ""}`,
                        }}
                      />
                      {descartada && <span className="k-sub">leitura de {data(l.m.lido_em)}</span>}
                    </td>
                    <td className="k-dir">
                      <span className="k-n">{alc > 0 ? pct1((inter / alc) * 100) : "—"}</span>
                      <span className="k-sub">{num(inter)} {inter === 1 ? "interação" : "interações"}</span>
                    </td>
                    <td className="k-dir">
                      <Dica titulo="A API da Meta não informa seguidores ganhos por Reel" leitor="não informado: a API da Meta não dá seguidores ganhos por Reel">
                        <span className="k-n k-muted">n/d</span>
                      </Dica>
                    </td>
                  </tr>
                );
              })}
            </TabelaNoCard>
          </div>
          {frase && (
            <Destaque
              className="kx-destaque-pe"
              meta="Última leitura confiável de cada Reel · alcance somado Reel a Reel (a mesma conta pode contar mais de uma vez) · % assistido = tempo médio ÷ duração · seguidores ganhos: a API não informa por Reel"
            >
              {frase}
            </Destaque>
          )}
        </>
      )}
    </Card>
  );
}
