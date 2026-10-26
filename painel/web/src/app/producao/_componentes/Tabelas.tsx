import type { ReactNode } from "react";
import Canais, { Palavra } from "@/components/Canais";
import { CardCabecalho } from "@/components/Card";
import { Chip, ChipModo, ChipPortao, ChipVideo } from "@/components/Chip";
import LinhaPortoes, { NaoSai } from "@/components/LinhaPortoes";
import { CelulaCapa, TabelaNoCard } from "@/components/Tabela";
import { EtapasPos } from "@/components/Progresso";
import Vazio from "@/components/Vazio";
import { capa } from "@/lib/capas";
import { nomeDoPortao, resumoMotivos } from "@/lib/estados";
import {
  data, dataDoSlug, diaCurto, diasEntre, hora, minSeg, num, palavraDoCta, primeiraMaiuscula, relativo,
} from "@/lib/formato";
import { piorDoVideo, portoesDoPost, type Producao, videoBloqueado } from "@/lib/producao";

// As tabelas das 5 fases (telas/producao.md; mapa de estados × fases: design-system.md §15.1). Cada linha leva data-tags
// e data-busca para a busca da página ("Buscar conteúdo…"). Colunas que o banco ainda não dá (versão, PDF e cenas extras
// do roteiro; duração e data do pacote pronto; responsável) ficam FORA até existir o dado (handoff §8).

function Cabeca({ titulo, nota, fonte }: { titulo: string; nota: string; fonte: string }) {
  return (
    <CardCabecalho
      como="h2" titulo={titulo} nota={nota} notaAoLado linha className="kx-fase-cab"
      acao={<span className="k-fonte kx-fonte-ink2">{fonte}</span>}
    />
  );
}

function Tabela({ rotulo, min, colunas, children }: { rotulo: string; min: number; colunas: { t: string; dir?: boolean }[]; children: ReactNode }) {
  return (
    <div data-grupo-filtro="">
      <TabelaNoCard rotulo={rotulo} min={min} colunas={colunas}>{children}</TabelaNoCard>
      <p className="k-fonte kx-nada-fase" data-vazio-grupo="" hidden>Nada encontrado nesta fase. Limpe a busca ou escolha outra fase.</p>
    </div>
  );
}

function Video({ nome, slug, src, doc }: { nome: string; slug: string; src?: string | null; doc?: boolean }) {
  return <CelulaCapa nome={nome} src={src} tamanho={doc ? "doc" : "padrao"} slug={slug} />;
}

function DataHora({ iso, sub }: { iso: string | null; sub?: ReactNode }) {
  return (
    <div className="kx-pilha-mini">
      <span>{data(iso)}</span>
      <span className="k-sub">{sub ?? <span className="k-mono">{hora(iso)}</span>}</span>
    </div>
  );
}

const linha = (nome: string, slug: string) => ({ "data-tags": "todos", "data-busca": `${nome} ${slug}` });

// ── Roteiros ───────────────────────────────────────────────────────────────────────────────────────────────────────
export function Roteiros({ p, hoje }: { p: Producao; hoje: Date }) {
  const vids = p.vids.filter((v) => v.fase === "roteiros").sort((a, b) => a.slug.localeCompare(b.slug));
  return (
    <>
      <Cabeca titulo={`Roteiros · ${vids.length}`} nota="na ordem de gravação prevista" fonte="Um roteiro vira vídeo quando você grava." />
      {vids.length === 0 ? (
        <div className="kx-vazio-fase"><Vazio icone="documento" titulo="Nenhum roteiro esperando">Quando um roteiro novo for escrito, ele espera aqui até você gravar.</Vazio></div>
      ) : (
        <Tabela rotulo="Roteiros" min={1080} colunas={[{ t: "Roteiro" }, { t: "Formato" }, { t: "Versão" }, { t: "Palavra-chave" }, { t: "PDF" }, { t: "Cenas extras" }, { t: "Portão do roteiro" }, { t: "Gravação prevista" }, { t: "Atualizado" }]}>
          {vids.map((v) => {
            const [pauta, roteiro] = p.portoesDoVideo(v.slug);
            const sr = roteiro?.status ?? "pendente";
            const prevista = v.gravacao_prevista ?? dataDoSlug(v.slug);
            const r = p.roteiroDe(v.slug);
            const seguir = v.tem_roteiro && !v.cta_palavra;
            return (
              <tr key={v.slug} {...linha(v.nome, v.slug)}>
                <td><Video nome={v.nome} slug={v.slug} doc /></td>
                <td>Reels</td>
                <td>{v.roteiro_versao != null ? <span className="k-mono">v{v.roteiro_versao}</span> : <span className="k-muted">—</span>}</td>
                <td><Palavra palavra={v.tem_roteiro ? v.cta_palavra : palavraDoCta(v.cta)} ctaSeguir={seguir} /></td>
                <td>{r?.pdf ? "Pronto" : seguir ? <span className="k-sub">sem PDF (CTA seguir)</span> : <span className="k-muted" aria-label="sem PDF">—</span>}</td>
                <td>
                  {v.roteiro_extras == null ? <span className="k-muted">—</span>
                    : v.roteiro_extras === 0 ? "Nenhuma"
                    : <span className="kx-nowrap">{num(r?.extras_arquivos ?? 0)} de {num(v.roteiro_extras)}</span>}
                </td>
                <td>
                  <ChipPortao
                    status={sr}
                    pequeno
                    dica={{ titulo: `Portão do roteiro: ${primeiraMaiuscula(MAPA[sr])}`, detalhe: `Pauta: ${primeiraMaiuscula(MAPA[pauta?.status ?? "pendente"])}${resumoMotivos(roteiro?.motivos) ? ` · ${resumoMotivos(roteiro?.motivos)}` : ""}` }}
                  />
                </td>
                <td>{prevista ? <div className="kx-pilha-mini"><span>{data(`${prevista}T12:00:00Z`)}</span><span className="k-sub">{relativo(diasEntre(hoje, prevista))}</span></div> : "—"}</td>
                <td><DataHora iso={v.atualizado} /></td>
              </tr>
            );
          })}
        </Tabela>
      )}
    </>
  );
}

const MAPA: Record<string, string> = {
  aprovado: "aprovado", bloqueado: "bloqueado", escalado: "escalado", vencido: "vencido", pendente: "ainda não rodou", nao_se_aplica: "não se aplica",
};

// ── Gravados ───────────────────────────────────────────────────────────────────────────────────────────────────────
export function Gravados({ p }: { p: Producao }) {
  const vids = p.vids.filter((v) => v.fase === "gravados");
  const roteiros = p.vids.filter((v) => v.fase === "roteiros").length;
  return (
    <>
      <Cabeca titulo={`Gravados · ${vids.length}`} nota="em pós-produção" fonte="Do corte ao QA: cor, legendas, áudio e capa." />
      {vids.length === 0 ? (
        <div className="kx-vazio-fase">
          <Vazio icone="inbox" titulo="Nada em edição agora">
            {roteiros > 0 ? `Os próximos a entrar aqui são os ${roteiros} roteiros. ` : ""}Assim que você grava, o roteiro vira vídeo e fica nesta lista até o pacote ficar pronto: corte, cor, legendas, áudio, capa e QA.
          </Vazio>
        </div>
      ) : (
        <Tabela rotulo="Gravados" min={900} colunas={[{ t: "Vídeo" }, { t: "Gravado em" }, { t: "Pós-produção" }, { t: "Portão da imagem" }, { t: "Portão do corte" }, { t: "Atualizado" }]}>
          {vids.map((v) => {
            const [, , imagem, corte] = p.portoesDoVideo(v.slug);
            return (
              <tr key={v.slug} {...linha(v.nome, v.slug)}>
                <td><Video nome={v.nome} slug={v.slug} src={capa(v.slug, "videos")} /></td>
                <td><DataHora iso={v.gravacao_chegou ?? v.gravacao_ultima} sub={`${num(v.gravacao_arquivos)} ${v.gravacao_arquivos === 1 ? "arquivo" : "arquivos"}`} /></td>
                <td><EtapasPos estado={v.estado} /></td>
                <td><ChipPortao status={imagem?.status ?? "pendente"} pequeno dica={resumoMotivos(imagem?.motivos) ? { titulo: nomeDoPortao("imagem"), detalhe: resumoMotivos(imagem?.motivos) } : undefined} /></td>
                <td><ChipPortao status={corte?.status ?? "pendente"} pequeno dica={resumoMotivos(corte?.motivos) ? { titulo: nomeDoPortao("corte"), detalhe: resumoMotivos(corte?.motivos) } : undefined} /></td>
                <td><DataHora iso={v.atualizado} /></td>
              </tr>
            );
          })}
        </Tabela>
      )}
    </>
  );
}

// ── Prontos ────────────────────────────────────────────────────────────────────────────────────────────────────────
export function Prontos({ p }: { p: Producao }) {
  const vids = p.vids.filter((v) => v.fase === "prontos");
  return (
    <>
      <Cabeca titulo={`Prontos · ${vids.length}`} nota="pacotes em 05-render-pronto/" fonte="O pacote sai daqui quando você agenda no Claude Code." />
      {vids.length === 0 ? (
        <div className="kx-vazio-fase"><Vazio icone="inbox" titulo="Nenhum pacote pronto">Pacote pronto espera aqui até você agendar.</Vazio></div>
      ) : (
        <>
          <Tabela rotulo="Prontos" min={1000} colunas={[{ t: "Vídeo" }, { t: "Duração", dir: true }, { t: "Palavra-chave" }, { t: "QA" }, { t: "Pacote criado" }, { t: "Portões do vídeo" }, { t: "Observação" }]}>
            {vids.map((v) => {
              const pior = piorDoVideo(p, v.slug);
              const trava = v.trava ? primeiraMaiuscula(v.trava.motivo.split(";")[0].trim()) : null;
              const pac = p.prontoDe(v.slug);
              return (
                <tr key={v.slug} {...linha(v.nome, v.slug)}>
                  <td><Video nome={v.nome} slug={v.slug} src={capa(v.slug, "pronto", "videos")} /></td>
                  <td className="k-dir"><span className="k-mono">{minSeg(pac?.duracao)}</span></td>
                  <td><Palavra palavra={pac ? pac.cta_palavra : v.tem_roteiro ? v.cta_palavra : palavraDoCta(v.cta)} ctaSeguir={pac ? !pac.cta_palavra : v.tem_roteiro && !v.cta_palavra} /></td>
                  <td><Chip tom="aprovado" pequeno>QA aprovado</Chip></td>
                  <td><DataHora iso={pac?.criado_em ?? null} /></td>
                  <td>
                    <LinhaPortoes status={pior.status} segura={pior.status !== "aprovado" ? pior.quem : undefined} rotulo="leitor" naoSai={false} />
                  </td>
                  <td>{trava ? <span className="k-small">{trava} · <NaoSai /></span> : <span className="k-muted">—</span>}</td>
                </tr>
              );
            })}
          </Tabela>
          <p className="k-fonte kx-pe-tabela">
            Pacote pronto espera aqui até você agendar: vídeo final, capa, legendas e o PDF da palavra. Agendar move para a fila de
            publicação. Uma trava escrita à mão (&quot;não publicar&quot;) segura o pacote aqui — não é portão, por isso não é &quot;Bloqueado&quot;.
          </p>
        </>
      )}
    </>
  );
}

// ── Agendados ──────────────────────────────────────────────────────────────────────────────────────────────────────
export function Agendados({ p, hoje }: { p: Producao; hoje: Date }) {
  const posts = [...p.agendados].sort((a, b) => (a.publicar_em ?? "").localeCompare(b.publicar_em ?? ""));
  return (
    <>
      <Cabeca titulo={`Agendados · ${posts.length}`} nota="pela data de publicação" fonte="Publica sozinho no horário marcado." />
      {posts.length === 0 ? (
        <div className="kx-vazio-fase"><Vazio icone="clock" titulo="Nada na fila">Quando um pacote pronto entrar na fila, aparece aqui com a data, o canal e os portões.</Vazio></div>
      ) : (
        <Tabela rotulo="Agendados" min={980} colunas={[{ t: "Publicação" }, { t: "Data e hora" }, { t: "Onde vai sair" }, { t: "Modo" }, { t: "Palavra-chave" }, { t: "Portões" }, { t: "Estado" }]}>
          {posts.map((f) => {
            const port = portoesDoPost(p, f);
            const bloqueado = videoBloqueado(p, f.video_slug);
            return (
              <tr key={f.slug} {...linha(f.nome, f.slug)}>
                <td><Video nome={f.nome} slug={f.slug} src={capa(f.slug, "fila")} /></td>
                <td>
                  {f.publicar_em ? (
                    <div className="kx-pilha-mini">
                      <span>{diaCurto(f.publicar_em)} · <span className="k-mono">{hora(f.publicar_em)}</span></span>
                      <span className="k-sub">{relativo(diasEntre(hoje, f.publicar_em))}</span>
                    </div>
                  ) : <span className="k-muted">sem data</span>}
                </td>
                <td><Canais ativos={f.plataformas} /></td>
                <td><ChipModo trial={f.trial} /></td>
                <td><Palavra palavra={f.palavra} /></td>
                <td>
                  <LinhaPortoes status={port.status} legado={port.legado} segura={port.segura} motivos={port.motivos} rotulo="leitor" />
                </td>
                <td><ChipVideo estado={bloqueado ? "bloqueado" : "agendado"} pequeno /></td>
              </tr>
            );
          })}
        </Tabela>
      )}
    </>
  );
}

// ── Publicados ─────────────────────────────────────────────────────────────────────────────────────────────────────
export function Publicados({ p }: { p: Producao }) {
  const posts = p.publicados;
  const maior = Math.max(-1, ...posts.map((x) => x.leitura?.alcance ?? -1));
  const ultima = posts.map((x) => x.leitura?.lido_em).filter(Boolean).sort().at(-1) ?? null;
  return (
    <>
      <Cabeca titulo={`Publicados · ${posts.length}`} nota="do mais recente ao mais antigo" fonte="Clique no canal para abrir o post." />
      {posts.length === 0 ? (
        <div className="kx-vazio-fase"><Vazio icone="play" titulo="Nada publicado ainda">Quando um post sair, ele aparece aqui com o link de cada canal e as métricas.</Vazio></div>
      ) : (
        <>
          <Tabela rotulo="Publicados" min={1080} colunas={[
            { t: "Publicação" }, { t: "Publicado em" }, { t: "Modo" }, { t: "Duração", dir: true }, { t: "Alcance", dir: true },
            { t: "Visualizações", dir: true }, { t: "Curtidas", dir: true }, { t: "Salvos", dir: true }, { t: "Onde foi publicado" },
          ]}>
            {posts.map((x) => {
              const m = x.leitura;
              const leEm = x.publicado_em ? new Date(Date.parse(x.publicado_em) + 5 * 86_400_000).toISOString() : null;
              const venceu = x.video_slug ? p.portoesDoVideo(x.video_slug).find((e) => e && ["bloqueado", "escalado", "vencido"].includes(e.status)) : null;
              return (
                <tr key={x.slug} {...linha(x.nome, x.slug)}>
                  <td>
                    <CelulaCapa nome={x.nome} src={capa(x.slug, "publicados")} slug={x.slug}>
                      {/* PI40: portão do vídeo que venceu depois de publicado aparece AO LADO — o "publicado" nunca some */}
                      {venceu && <ChipPortao status={venceu.status} pequeno texto={venceu.portao} />}
                    </CelulaCapa>
                  </td>
                  <td><DataHora iso={x.publicado_em} /></td>
                  <td><ChipModo trial={x.trial} /></td>
                  <td className="k-dir"><span className="k-mono">{minSeg(x.duracao_s)}</span></td>
                  <td className="k-dir">
                    {m?.alcance != null
                      ? <span className={`k-n${m.alcance === maior ? " k-valor-foco" : ""}`}>{num(m.alcance)}</span>
                      : m ? <span className="k-muted">—</span> : <span className="k-sub kx-nowrap">lê em {data(leEm)}</span>}
                  </td>
                  <td className="k-dir">{m?.views != null ? <span className="k-n">{num(m.views)}</span> : <span className="k-muted">—</span>}</td>
                  <td className="k-dir">{m?.curtidas != null ? <span className="k-n">{num(m.curtidas)}</span> : <span className="k-muted">—</span>}</td>
                  <td className="k-dir">{m?.salvamentos != null ? <span className="k-n">{num(m.salvamentos)}</span> : <span className="k-muted">—</span>}</td>
                  <td>
                    <Canais
                      publicado
                      ativos={x.plataformas ?? []}
                      links={{ instagram: x.permalink_instagram, facebook: x.permalink_facebook }}
                    />
                  </td>
                </tr>
              );
            })}
          </Tabela>
          <p className="k-fonte kx-pe-tabela">
            {ultima ? `Última leitura de métricas em ${data(ultima)}, ${hora(ultima)}; ` : ""}a leitura completa sai 5 dias depois de cada post.
          </p>
        </>
      )}
    </>
  );
}
