import { Card, CabecalhoGrafico } from "@/components/Card";
import ErroBloco from "@/components/ErroBloco";
import { BarrasComCapa, TabelaGemea } from "@/components/Graficos";
import Vazio from "@/components/Vazio";
import { capa } from "@/lib/capas";
import type { ConsumoExecucao } from "@/lib/db";
import { num, usd } from "@/lib/formato";
import { consumoExecucoes30 } from "@/lib/leituras";
import { hrefDoVideo, lerProducao, nomeCurto, type Producao } from "@/lib/producao";

// Tokens e custos · custo por vídeo. (telas/tokens-e-custos.md): o consumo dos especialistas cujo 1.º pedido cita
// videos/<slug> (view consumo, coluna video_slug), nos 30 dias; a conversa do Atlas não entra. Os 5 de maior custo, com
// a capa; o nome leva ao vídeo na Produção (Publicados, Agendados ou a fase dele).

const dinheiro = (v: number) => v.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

export default async function CustoPorVideo() {
  let linhas: ConsumoExecucao[], p: Producao;
  try {
    [linhas, p] = await Promise.all([consumoExecucoes30(), lerProducao()]);
  } catch {
    return <ErroBloco oque="O custo por vídeo" />;
  }
  const porVideo = new Map<string, { usd: number; tokens: number }>();
  for (const l of linhas) {
    if (!l.video_slug) continue;
    const v = porVideo.get(l.video_slug) ?? { usd: 0, tokens: 0 };
    v.usd += l.usd ?? 0;
    v.tokens += l.tokens;
    porVideo.set(l.video_slug, v);
  }
  const videos = [...porVideo.entries()]
    .map(([slug, v]) => ({ slug, ...v, nome: p.vids.find((x) => x.slug === slug)?.nome ?? nomeCurto(slug) }))
    .sort((a, b) => b.usd - a.usd);
  const custo = (v: number) => usd(v);
  return (
    <Card como="section" className="kx-card-grafico kx-card-pilha" aria-labelledby="t-vid">
      <CabecalhoGrafico id="t-vid" titulo="custo por vídeo." />
      {videos.length === 0 ? (
        <Vazio icone="play" titulo="Nenhum pedido citou um vídeo">Quando um especialista trabalhar com videos/&lt;slug&gt; no pedido, o custo aparece no vídeo.</Vazio>
      ) : (
        <>
          <BarrasComCapa
            rotulo="Custo por vídeo, do maior para o menor"
            itens={videos.slice(0, 5).map((v) => ({
              nome: v.nome, capa: capa(v.slug, "videos", "pronto", "publicados"), valor: v.usd, texto: custo(v.usd), href: hrefDoVideo(p, v.slug),
            }))}
          />
          <p className="k-fonte kx-fonte-pe">Só o trabalho dos agentes especialistas, pelo vídeo citado no pedido. A conversa do Atlas não entra.</p>
          <TabelaGemea
            rotulo="Custo por vídeo"
            colunas={["Vídeo", "Tokens", "Custo (US$)"]}
            linhas={videos.map((v) => [v.nome, num(v.tokens), dinheiro(v.usd)])}
          />
        </>
      )}
    </Card>
  );
}
