import { notFound } from "next/navigation";
import type { ReactNode } from "react";
import Avatar from "@/components/Avatar";
import { Botao } from "@/components/Botao";
import { CardCabecalho } from "@/components/Card";
import CardPessoa from "@/components/CardPessoa";
import { Chip, ChipDecisao, ChipModelo, ChipPortao, ChipVideo } from "@/components/Chip";
import Dica from "@/components/Dica";
import Evento, { EventoPortao } from "@/components/Evento";
import { Barras, Legenda, Rosca, Sparkline } from "@/components/Graficos";
import GraficoLinha from "@/components/GraficoLinha";
import Icone, { type NomeIcone } from "@/components/Icone";
import { Delta, Kpi } from "@/components/Kpi";
import Logo from "@/components/Logo";
import Nota from "@/components/Nota";
import { CabecalhoPagina, Secao } from "@/components/Pagina";
import Portao from "@/components/Portao";
import { BarraProgresso, Etapas } from "@/components/Progresso";
import { CelulaVideo, Tabela } from "@/components/Tabela";
import { Codigo, Tokens } from "@/components/Texto";
import Vazio from "@/components/Vazio";
import { Bloco } from "@/components/Esqueleto";
import dadosIcones from "@/app/design/icones.json";
import * as db from "@/lib/db";
import { MAPA_PORTAO, type EstadoPortao, estadoDoVideo } from "@/lib/estados";
import { NOME_ESTADO, PORTOES, data, dataHora, estadoLimpo, num, primeiraMaiuscula, titulo, tituloVideo, usd } from "@/lib/formato";
import { fotoDoAgente } from "@/lib/retratos";
import SelecaoDemo from "./_componentes/SelecaoDemo";

// VITRINE dos componentes de src/components/ — para quem constrói e para o PORTÃO-INTERFACE compararem cada peça com a
// prévia de painel/design/previas/. NÃO é tela do Carlos: só abre com PAINEL_VITRINE=1 no ambiente do servidor
// (ex.: PAINEL_DIST=.next-trabalho PAINEL_VITRINE=1 npm run dev -- -p 3457); sem isso, 404. Dados reais do banco onde
// existem; o que não tem dado real hoje vem marcado "exemplo", como nas prévias.

function Etiqueta({ real }: { real?: boolean }) {
  return <span className="kx-etiqueta">{real ? "dados reais · banco do painel" : "exemplo · sem dado real hoje"}</span>;
}
function Bloco2({ titulo, previa, real, children }: { titulo: string; previa: string; real?: boolean; children: ReactNode }) {
  return (
    <Secao titulo={titulo} descricao={<>Prévia: <Codigo>painel/design/previas/{previa}</Codigo> {real !== undefined && <Etiqueta real={real} />}</>}>
      {children}
    </Secao>
  );
}

export default async function Sistema() {
  if (process.env.PAINEL_VITRINE !== "1") notFound();
  const [ags, deps, vids, estados, fila, snaps, mets, pubs] = await Promise.all([
    db.agentes(), db.departamentos(), db.videos(), db.portoesEstado(), db.fila(), db.snapshots(), db.metricas(), db.publicacoes(),
  ]);
  const depto = new Map(deps.map((d) => [d.id, d.nome]));
  const atual = snaps.at(-1);
  const anterior = snaps.length > 1 ? snaps.at(-2) : undefined;
  const marina = ags.find((a) => a.id === "roteirista");
  const livia = ags.find((a) => a.id === "produtor-de-material");
  // a série do Demis Hassabis: leituras confiáveis com visualizações (a 1.ª, sem números, fica fora)
  const demis = mets.filter((m) => m.slug === "2026-09-17-demis-hassabis" && !m.suspeito && m.views != null && m.dias != null);
  const ult = db.leiturasConfiaveis(mets);
  const alcances = pubs
    .map((p) => ({ p, m: ult.get(p.slug)?.m }))
    .filter((x) => x.m?.alcance != null)
    .sort((a, b) => (b.m!.alcance ?? 0) - (a.m!.alcance ?? 0));
  const papeis = ["construtor", "portao", "analista", "diretor"] as const;
  const nomePapel = { construtor: "Construtores", portao: "Portões", analista: "Analistas", diretor: "Direção" };
  const doVideo = (slug: string) => PORTOES.map((p) => estados.find((e) => e.alvo === `videos/${slug}` && e.portao === p));
  const livro = vids.find((v) => v.slug === "2026-10-23-livro-chatgpt");
  const publicados = vids.filter((v) => estadoLimpo(v.estado) === "publicado").length;

  return (
    <>
      <CabecalhoPagina
        titulo="Componentes"
        descricao="Vitrine da biblioteca src/components/ contra as prévias de painel/design/previas/. Só abre com PAINEL_VITRINE=1."
      />

      <Bloco2 titulo="Logotipo e ícones" previa="logo.html · icones.html">
        <div className="kx-pilha">
          <div className="kx-fila">
            <div className="k-card k-pad"><Logo tom="ink" altura={28} /></div>
            <div className="k-card k-pad kx-fundo-escuro"><Logo tom="ivory" altura={28} /></div>
            <div className="k-card k-pad"><Logo tom="ink" altura={16} /></div>
          </div>
          <div className="kx-fila">
            {(Object.keys(dadosIcones.icones) as NomeIcone[]).map((n) => (
              <Dica key={n} titulo={n} detalhe={(dadosIcones.rotulos as Record<string, string>)[n]}>
                <span className="k-btn k-btn-secondary k-btn-icon" aria-hidden="true"><Icone nome={n} tamanho={18} /></span>
              </Dica>
            ))}
          </div>
        </div>
      </Bloco2>

      <Bloco2 titulo="Botão" previa="botao.html">
        <div className="kx-pilha">
          <div className="kx-fila">
            <Botao variante="primario" icone="plus">Novo vídeo</Botao>
            <Botao variante="secundario">Exportar</Botao>
            <Botao variante="fantasma">Cancelar</Botao>
            <Botao variante="secundario" soIcone icone="filter" aria-label="Filtrar" />
            <Botao variante="fantasma" soIcone icone="more" tamanhoIcone={18} aria-label="Mais ações" />
            <Botao variante="escuro" icone="check">Aprovar portão</Botao>
          </div>
          <div className="kx-fila">
            <Botao variante="primario" disabled>Aprovar e agendar</Botao>
            <Botao variante="secundario" pequeno>Ver todos</Botao>
          </div>
        </div>
      </Bloco2>

      <Bloco2 titulo="Chip de estado" previa="chip.html">
        <div className="kx-pilha">
          <div>
            <p className="k-cap kx-cap-bloco">Família 1 · estado de cada portão (o mapa único)</p>
            <div className="kx-fila">
              {(Object.keys(MAPA_PORTAO) as EstadoPortao[]).map((s) => (
                <ChipPortao key={s} status={s === "legado" ? "pendente" : s} legado={s === "legado"} />
              ))}
            </div>
          </div>
          <div>
            <p className="k-cap kx-cap-bloco">Família 2 · decisão do Carlos</p>
            <div className="kx-fila"><ChipDecisao decisao="aguarda" /><ChipDecisao decisao="ajustes" /></div>
          </div>
          <div>
            <p className="k-cap kx-cap-bloco">Família 3 · estado do vídeo, em ordem</p>
            <div className="kx-fila">
              {(["bloqueado", "publicado", "agendado", "portao", "producao"] as const).map((e) => <ChipVideo key={e} estado={e} />)}
            </div>
          </div>
          <div>
            <p className="k-cap kx-cap-bloco">Modelos (com a versão) e portão</p>
            <div className="kx-fila">
              <ChipModelo modelo="sonnet" /><ChipModelo modelo="opus" /><Chip tom="portao" icone="lock">Portão</Chip>
            </div>
          </div>
        </div>
      </Bloco2>

      <Bloco2 titulo="Avatar e card de pessoa" previa="avatar.html · pessoa.html" real>
        <div className="kx-pilha">
          <div className="kx-fila">
            {marina && <Avatar nome={marina.nome} foto={fotoDoAgente(marina.id)} tamanho={72} rotulado />}
            {marina && <Avatar nome={marina.nome} foto={fotoDoAgente(marina.id)} tamanho={56} rotulado />}
            <Avatar nome="Otávio Reis" tamanho={56} rotulado />
            <Avatar nome="Lívia Rocha" tamanho={40} rotulado />
            <Avatar nome="Atlas" tamanho={32} redondo rotulado />
          </div>
          <div className="k-grid">
            {marina && (
              <div className="k-span-6">
                <CardPessoa href={`/equipe/${marina.id}`} nome={marina.nome} cargo={marina.cargo} departamento={depto.get(marina.departamento_id)} modelo={marina.modelo} foto={fotoDoAgente(marina.id)} />
              </div>
            )}
            {livia && (
              <div className="k-span-6">
                <CardPessoa
                  href={`/equipe/${livia.id}`} nome={livia.nome} cargo={livia.cargo} departamento={depto.get(livia.departamento_id)}
                  modelo={livia.modelo} foto={null}
                  metricas={[{ rotulo: "vídeos", valor: "—" }, { rotulo: "tokens", valor: "—", tokens: true }, { rotulo: "custo", valor: "—" }]}
                />
              </div>
            )}
          </div>
          <p className="k-kpi-note kx-sem-margem">
            Formatos de tokens e custo (<Etiqueta />): <Tokens valor={1284910} /> · <Tokens valor={1284910} compactar /> · {usd(12.4)} · {usd(1292)}
          </p>
        </div>
      </Bloco2>

      <Bloco2 titulo="KPI" previa="kpi.html" real>
        <div className="k-grid k-grid--tiles">
          <Kpi
            className="k-span-3" rotulo="Seguidores no Instagram" valor={num(atual?.seguidores)}
            delta={atual?.seguidores != null && anterior?.seguidores != null
              ? <Delta sentido="desce" significado="ruim" texto={num(Math.abs(atual.seguidores - anterior.seguidores))} leitor="a menos" />
              : undefined}
            nota={anterior ? `desde ${data(anterior.lido_em)}` : undefined}
          />
          <Kpi className="k-span-3" rotulo="Contas alcançadas · 28 dias" valor={num(atual?.alcance)} />
          <Kpi className="k-span-3" rotulo="Visualizações · 28 dias" valor={num(atual?.views)} />
          <Kpi
            className="k-span-3" rotulo={`Vídeo mais visto · ${demis.length ? data(demis.at(-1)!.lido_em) : "—"}`}
            valor={num(demis.at(-1)?.views)} nota="Demis Hassabis"
            extra={<Sparkline x={demis.map((m) => m.dias!)} y={demis.map((m) => m.views!)} rotulo={`Visualizações nas ${demis.length} leituras: ${demis.map((m) => num(m.views)).join(", ")}`} />}
          />
        </div>
      </Bloco2>

      <Bloco2 titulo="Linha de vídeo e progresso" previa="linha-de-video.html · progresso.html" real>
        <div className="kx-pilha">
          <Tabela rotulo="Vídeos (a tabela rola para o lado)" larguraMinima={720}>
            <thead><tr><th scope="col">Vídeo</th><th scope="col">Etapa</th><th scope="col">Progresso</th><th scope="col">Estado</th></tr></thead>
            <tbody>
              {vids.slice(0, 5).map((v) => {
                const e = estadoDoVideo(v.estado, doVideo(v.slug).map((x) => x?.status ?? "pendente"));
                return (
                  <tr key={v.slug}>
                    <td className="kx-celula-video"><CelulaVideo titulo={tituloVideo(v.slug, v.tema)} meta={v.slug} /></td>
                    <td className="k-ink2">{NOME_ESTADO[estadoLimpo(v.estado)] ?? v.estado}</td>
                    <td><Etapas estado={v.estado} bloqueado={e === "bloqueado"} /></td>
                    <td><ChipVideo estado={e} /></td>
                  </tr>
                );
              })}
            </tbody>
          </Tabela>
          <div className="k-card k-pad">
            <div className="kx-pilha">
              <BarraProgresso titulo="Vídeos publicados" feito={publicados} total={vids.length} />
              {livro && <Etapas estado={livro.estado} rotulos />}
            </div>
          </div>
        </div>
      </Bloco2>

      <Bloco2 titulo="Portão de aprovação" previa="portao.html">
        <div className="k-grid">
          {livro && (
            <div className="k-span-6">
              <p className="k-cap kx-cap-bloco">Modo Portões do vídeo <Etiqueta real /></p>
              <Portao
                titulo={tituloVideo(livro.slug, livro.tema)}
                estadoVideo={estadoDoVideo(livro.estado, doVideo(livro.slug).map((x) => x?.status ?? "pendente"))}
                criterios={PORTOES.map((p, i) => ({ portao: p, status: doVideo(livro.slug)[i]?.status ?? "pendente", motivos: doVideo(livro.slug)[i]?.motivos }))}
                posts={fila.filter((f) => f.slug.startsWith(livro.slug)).map((f) => ({
                  rotulo: `${dataHora(f.publicar_em)}${f.slug !== livro.slug ? ` · ${f.slug.slice(livro.slug.length + 1)}` : ""}`,
                  status: estados.find((e) => e.alvo === `06-publicar/${f.slug}`)?.status ?? "pendente",
                  legado: f.legado,
                }))}
              />
            </div>
          )}
          <div className="k-span-6">
            <p className="k-cap kx-cap-bloco">Modo Decisão <Etiqueta /></p>
            <Portao
              titulo="Seu primeiro agente de IA em três passos"
              estadoVideo="portao"
              criterios={PORTOES.map((p) => ({ portao: p, status: "aprovado" as const }))}
            />
          </div>
        </div>
      </Bloco2>

      <Bloco2 titulo="Evento do calendário" previa="calendario.html">
        <div className="kx-pilha">
          <div className="k-card k-pad">
            <CardCabecalho titulo="Fila de publicação" nota={<Etiqueta real />} />
            <div className="k-cal">
              {fila.map((f) => (
                <div key={f.slug} className="k-cal-day">
                  <span>{data(f.publicar_em)}</span>
                  <Evento
                    titulo={titulo(f.slug)}
                    hora={dataHora(f.publicar_em).split(", ")[1] ?? ""}
                    canais={f.plataformas}
                    portoes={{ status: estados.find((e) => e.alvo === `06-publicar/${f.slug}`)?.status ?? "pendente", legado: f.legado }}
                  />
                </div>
              ))}
            </div>
          </div>
          <div>
            <p className="k-cap kx-cap-bloco">Casos sem dado real hoje <Etiqueta /></p>
            <div className="k-cal">
              <div className="k-cal-day"><Evento titulo="Reel com a cor refeita na fila" hora="21:00" canais={["instagram"]} portoes={{ status: "vencido", segura: "imagem" }} /></div>
              <div className="k-cal-day"><Evento titulo="Reel recém-posto na fila" hora="18:30" canais={["facebook"]} portoes={{ status: "pendente", segura: "publicação" }} /></div>
              <div className="k-cal-day"><Evento titulo="Reel nos dois canais" hora="20:00" canais={["instagram", "facebook"]} portoes={{ status: "aprovado" }} /></div>
              <div className="k-cal-day"><EventoPortao titulo="Portão · publicação" texto="marcado para hoje" /></div>
            </div>
          </div>
        </div>
      </Bloco2>

      <Bloco2 titulo="Notificação, dica, busca e dropdown" previa="notificacao.html · dica.html · busca.html · dropdown.html" real>
        <div className="k-grid">
          <div className="k-card kx-recorte k-span-6">
            <Nota tom="alerta" titulo="Portão da interface vencido">Arquivos do painel mudaram depois do APROVADO.</Nota>
            <div className="kx-divisoria" />
            <Nota tom="portao" titulo="Portão da publicação ainda não rodou" naoLida>Exemplo de nota não lida.</Nota>
            <div className="kx-divisoria" />
            <Nota tom="ok" titulo="Dados do painel aprovados">Portão dos dados</Nota>
            <div className="kx-divisoria" />
            <Nota titulo="Sincronizado">Banco do painel atualizado</Nota>
          </div>
          <div className="k-span-6 kx-pilha">
            <div className="kx-fila">
              <Dica titulo="Visualizações" detalhe="quantas vezes o Reel começou a tocar (Instagram)">
                <span className="k-btn k-btn-secondary k-btn-icon k-btn-sm" aria-hidden="true"><Icone nome="info" tamanho={14} /></span>
              </Dica>
              <span className="k-kpi-note">Passe o mouse ou o Tab no botão: a dica abre em 300ms.</span>
            </div>
            <SelecaoDemo opcoes={[{ valor: "28", rotulo: "Últimos 28 dias" }]} />
            <p className="k-kpi-note kx-sem-margem">A busca está no topo (⌘K) e no menu do celular.</p>
          </div>
        </div>
      </Bloco2>

      <Bloco2 titulo="Gráficos" previa="graficos.html" real>
        <div className="k-grid">
          <div className="k-card k-pad k-span-8">
            <CardCabecalho
              titulo="Visualizações por leitura"
              nota="Demis Hassabis · dias desde a publicação"
              acao={<Legenda series={[{ nome: "Instagram", serie: 1 }, { nome: "Facebook", serie: 2 }]} />}
            />
            <GraficoLinha
              rotulo="Visualizações no Instagram e reproduções no Facebook do Reel do Demis Hassabis, por leitura"
              x={demis.map((m) => m.dias!)}
              ticksX={[0, 3, 6, 9]}
              rotulosX={[0, 3, 6, 9].map((v) => `dia ${num(v)}`)}
              pontos={demis.map((m) => `Dia ${num(m.dias)} · leitura de ${data(m.lido_em)}`)}
              series={[
                { nome: "Instagram", valores: demis.map((m) => m.views ?? 0) },
                { nome: "Facebook", valores: demis.map((m) => m.plays_fb ?? 0) },
              ]}
            />
          </div>
          <div className="k-card k-pad k-span-4">
            <CardCabecalho titulo="Alcance por vídeo" nota="última leitura confiável de cada Reel" />
            <Barras
              rotulo="Alcance por vídeo" colunaValor="Alcance"
              itens={alcances.map(({ p, m }) => ({ rotulo: primeiraMaiuscula(titulo(p.slug)), nome: tituloVideo(p.slug, p.tema), valor: m!.alcance!, dica: `${num(m!.alcance)} contas alcançadas · leitura de ${data(m!.lido_em)}` }))}
            />
          </div>
          <div className="k-card k-pad k-span-4">
            <CardCabecalho titulo="Equipe por papel" nota="quem constrói, quem audita" />
            <Rosca
              rotulo="Equipe por papel" rotuloCentro="pessoas"
              fatias={papeis.map((p, i) => ({ rotulo: nomePapel[p], valor: ags.filter((a) => a.papel === p).length, serie: (i + 1) as 1 | 2 | 3 | 4 }))}
            />
          </div>
        </div>
      </Bloco2>

      <Bloco2 titulo="Estado vazio e carregando" previa="vazio.html · carregando.html">
        <div className="k-grid">
          <div className="k-span-6">
            <Vazio titulo="Nenhum vídeo bloqueado" acao={<Botao variante="secundario" pequeno>Ver todos os vídeos</Botao>}>
              Quando um portão parar um vídeo, ele aparece aqui com o motivo.
            </Vazio>
          </div>
          <div className="k-card k-kpi k-span-3" aria-hidden="true">
            <Bloco tipo="cap" /><Bloco tipo="metric" estilo={{ marginTop: 6 }} /><Bloco tipo="line" largura="40%" estilo={{ marginTop: 6 }} />
          </div>
        </div>
      </Bloco2>
    </>
  );
}
