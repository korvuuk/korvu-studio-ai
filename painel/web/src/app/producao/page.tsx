import { Suspense } from "react";
import { BotaoLink } from "@/components/Botao";
import { Card, CardCabecalho } from "@/components/Card";
import { Chip } from "@/components/Chip";
import ErroBloco from "@/components/ErroBloco";
import { Escolha, EscolhaBotoes, EscolhaPainel } from "@/components/Escolha";
import { EsqueletoCard, EsqueletoTabela } from "@/components/Esqueleto";
import { BuscaLista, FiltroLista } from "@/components/FiltroLista";
import { ListaKv } from "@/components/ListaKv";
import Nota from "@/components/Nota";
import { BarraPagina, Secao } from "@/components/Pagina";
import Vazio from "@/components/Vazio";
import * as db from "@/lib/db";
import { MAPA_PORTAO } from "@/lib/estados";
import { data, dataDoSlug, dataHora, diaCurto, hora, PORTOES } from "@/lib/formato";
import { agentes } from "@/lib/leituras";
import { FASES, lerProducao, precisamDeAtencao, type Producao } from "@/lib/producao";
import { Agendados, Gravados, Prontos, Publicados, Roteiros } from "./_componentes/Tabelas";

// Produção de conteúdo — telas/producao.md + producao.html (APROVADO, área design, 23/10 21:04); mapa de estados × fases
// no livro §15.1. A fase vem da pasta onde o trabalho está (o sincronizador traduz para o banco). O formato (Reels,
// Stories, Carrossel) ainda não existe por conteúdo: hoje tudo é Reels, e Stories/Carrossel mostram o vazio.

const ELOS = ["você grava", "pós e QA", "você agenda", "publica no horário"];

function metaDasFases(p: Producao) {
  const roteiros = p.vids.filter((v) => v.fase === "roteiros").sort((a, b) => a.slug.localeCompare(b.slug));
  const gravados = p.vids.filter((v) => v.fase === "gravados");
  const prontos = p.vids.filter((v) => v.fase === "prontos");
  const agend = [...p.agendados].sort((a, b) => (a.publicar_em ?? "").localeCompare(b.publicar_em ?? ""));
  const pubs = p.publicados;
  const antigo = roteiros[0] ? dataDoSlug(roteiros[0].slug) : null;
  const videosAg = new Set(agend.map((f) => f.video_slug ?? f.slug)).size;
  const videosPub = new Set(pubs.map((x) => x.video_slug ?? x.slug)).size;
  const melhor = [...pubs].filter((x) => x.leitura?.alcance != null).sort((a, b) => (b.leitura!.alcance ?? 0) - (a.leitura!.alcance ?? 0))[0];
  const proxima = agend.find((f) => f.publicar_em);
  return {
    roteiros: {
      n: roteiros.length, d: "Só o roteiro. Ainda não gravados.",
      m: [
        roteiros.length ? `${roteiros.filter((v) => p.roteiroDe(v.slug)?.pdf).length} com PDF` : "",
        antigo ? `o mais antigo espera desde ${data(`${antigo}T12:00:00Z`)}` : "nenhum esperando",
      ].filter(Boolean).join(" · "),
    },
    gravados: { n: gravados.length, d: "Em edição e pós-produção.", m: gravados.length ? `${gravados.length} em pós-produção` : "Nenhum em edição agora" },
    prontos: {
      n: prontos.length, d: "Pacote pronto, ainda sem data.",
      m: prontos.length === 1 ? `${prontos[0].nome}${prontos[0].trava ? ` · ${prontos[0].trava.motivo.split(";")[0].trim()}, não sai` : ""}` : prontos.length ? `${prontos.length} pacotes` : "Nenhum esperando data",
    },
    agendados: { n: agend.length, d: "Na fila, com data e hora.", m: agend.length ? `${videosAg} ${videosAg === 1 ? "vídeo" : "vídeos"}${proxima ? ` · próxima ${diaCurto(proxima.publicar_em!).toLowerCase()}, ${hora(proxima.publicar_em)}` : ""}` : "Fila vazia" },
    publicados: { n: pubs.length, d: "No ar no Instagram e no Facebook.", m: pubs.length ? `${videosPub} ${videosPub === 1 ? "vídeo" : "vídeos"}${melhor ? ` · melhor: ${melhor.nome}` : ""}` : "Nada publicado ainda" },
  };
}

async function Fases() {
  let p: Producao;
  try { p = await lerProducao(); } catch { return <ErroBloco oque="As fases da produção" />; }
  const meta = metaDasFases(p);
  if (FASES.every((f) => meta[f.id].n === 0)) return <Vazio icone="videos-portoes" titulo="Nada em produção">Quando um roteiro novo for escrito, ele aparece aqui e segue pelas fases até ser publicado.</Vazio>;
  return (
    <EscolhaBotoes
      grupo="fase"
      estilo="fases"
      rotulo="Fases da produção"
      controla="fase-tabela"
      opcoes={FASES.map((f, i) => ({ valor: f.id, rotulo: f.nome, fase: meta[f.id], elo: ELOS[i] }))}
    />
  );
}

async function TabelaDaFase() {
  let p: Producao;
  try { p = await lerProducao(); } catch { return <ErroBloco oque="A lista da fase" />; }
  const hoje = new Date();
  return (
    <>
      <EscolhaPainel grupo="fase" valores={["roteiros"]}><Roteiros p={p} hoje={hoje} /></EscolhaPainel>
      <EscolhaPainel grupo="fase" valores={["gravados"]}><Gravados p={p} /></EscolhaPainel>
      <EscolhaPainel grupo="fase" valores={["prontos"]}><Prontos p={p} /></EscolhaPainel>
      <EscolhaPainel grupo="fase" valores={["agendados"]}><Agendados p={p} hoje={hoje} /></EscolhaPainel>
      <EscolhaPainel grupo="fase" valores={["publicados"]}><Publicados p={p} /></EscolhaPainel>
    </>
  );
}

async function Atencao() {
  let lista;
  try {
    const [p, ags] = await Promise.all([lerProducao(), agentes()]);
    lista = precisamDeAtencao(p, ags);
  } catch {
    return <ErroBloco oque="Os avisos" />;
  }
  return (
    <Card como="section" className="kx-card-atencao" aria-labelledby="t-aten">
      <CardCabecalho
        como="h2" id="t-aten" titulo="Precisam de atenção" linha className="kx-card-head-4"
        acao={<Chip tom="producao" semPonto pequeno>{lista.length}<span className="k-sr-only"> avisos</span></Chip>}
      />
      {lista.length === 0 ? (
        <Nota tom="ok" titulo="Nada pede atenção agora">Quando um roteiro esperar gravação, um pronto não puder sair ou um portão parar, aparece aqui.</Nota>
      ) : (
        <div className="kx-pilha-0">
          {lista.map((a) => (
            <Nota key={a.id} tom={a.tom} icone={a.icone} titulo={a.titulo} acoes={a.acao && <BotaoLink variante="secundario" pequeno href={a.acao.href}>{a.acao.rotulo}</BotaoLink>}>
              {a.corpo}
            </Nota>
          ))}
        </div>
      )}
    </Card>
  );
}

const PALAVRA_PLURAL: Record<string, [string, string]> = {
  aprovado: ["aprovado", "aprovados"], bloqueado: ["bloqueado", "bloqueados"], escalado: ["escalado", "escalados"],
  vencido: ["vencido", "vencidos"], pendente: ["ainda não rodou", "ainda não rodaram"], nao_se_aplica: ["não se aplica", "não se aplicam"],
};

async function Portoes() {
  let estados: db.PortaoEstado[], fila: db.ItemFila[];
  try {
    const p = await lerProducao();
    estados = p.estados;
    fila = p.agendados;
  } catch {
    return <ErroBloco oque="Os portões" />;
  }
  const areas = [...PORTOES, "publicacao"] as const;
  const legado = new Set(fila.filter((f) => f.legado && !f.selado).map((f) => `06-publicar/${f.slug}`));
  const linhas = areas.map((area) => {
    const deste = estados.filter((e) => e.portao === area && (e.alvo.startsWith("videos/") || e.alvo.startsWith("06-publicar/")));
    const conta = new Map<string, number>();
    for (const e of deste) {
      const k = area === "publicacao" && legado.has(e.alvo) ? "legado" : e.status;
      conta.set(k, (conta.get(k) ?? 0) + 1);
    }
    const ordem = ["escalado", "bloqueado", "vencido", "pendente", "aprovado", "nao_se_aplica", "legado"];
    const texto = ordem.filter((k) => conta.get(k)).map((k) => {
      const n = conta.get(k)!;
      return k === "legado" ? `${n} ${MAPA_PORTAO.legado.palavra.toLowerCase()}` : `${n} ${PALAVRA_PLURAL[k][n === 1 ? 0 : 1]}`;
    }).join(" · ");
    return { area, texto: texto || "nenhum alvo" };
  });
  const semVeredicto = !estados.some((e) => (e.alvo.startsWith("videos/") || e.alvo.startsWith("06-publicar/")) && ["aprovado", "bloqueado", "escalado"].includes(e.status));
  if (estados.length === 0) return <Card como="section" pad><Vazio icone="lock" titulo="Nenhum portão no banco">Os portões aparecem aqui quando o sincronizador ler o portoes.json.</Vazio></Card>;
  return (
    <Card como="section" pad className="kx-card-portoes" aria-labelledby="t-port">
      <CardCabecalho como="h2" id="t-port" titulo="Portões" linha acao={<span className="k-mono k-muted">{areas.length} áreas</span>} />
      {semVeredicto && <p className="k-fonte kx-fonte-ink2 kx-fonte-portoes">Nenhum veredicto nos vídeos ainda: os portões começaram em 22 out.</p>}
      <ListaKv
        itens={linhas.map((l) => ({
          id: l.area,
          chave: l.area === "publicacao" ? "Publicação" : l.area.charAt(0).toUpperCase() + l.area.slice(1),
          valor: l.texto,
        }))}
      />
    </Card>
  );
}

async function Fonte() {
  const banco = await db.estadoDoBanco();
  return (
    <p className="k-fonte kx-sem-margem">
      Lido de <span className="k-mono">videos/</span>, <span className="k-mono">05-render-pronto/</span>, <span className="k-mono">06-publicar/</span> e <span className="k-mono">07-publicados/</span>
      {banco.estado === "ok" ? ` · sincronizado em ${dataHora(banco.em)}` : ""}
    </p>
  );
}

export default function Producao() {
  return (
    <FiltroLista>
      <Escolha nome="formato" inicial="todos">
        <Escolha nome="fase" inicial="roteiros" ancora opcoesValidas={FASES.map((f) => f.id)}>
          <BarraPagina titulo="Produção de conteúdo">
            <BuscaLista placeholder="Buscar conteúdo…" rotulo="Buscar conteúdo pelo nome ou slug" />
          </BarraPagina>
          <div className="k-section-head kx-filtros-linha">
            <div className="k-row kx-row-10">
              <span className="k-cap">Formato</span>
              <EscolhaBotoes
                grupo="formato"
                estilo="filtros"
                rotulo="Filtrar por formato"
                opcoes={[{ valor: "todos", rotulo: "Todos" }, { valor: "reels", rotulo: "Reels" }, { valor: "stories", rotulo: "Stories" }, { valor: "carrossel", rotulo: "Carrossel" }]}
              />
            </div>
            <Suspense fallback={null}><Fonte /></Suspense>
          </div>

          <Secao rotulo="Fases">
            <Suspense fallback={<EsqueletoCard oque="as fases" altura={118} />}><Fases /></Suspense>
          </Secao>

          <Secao rotulo="Lista da fase e avisos">
            <div className="k-grid">
              <Card como="section" recorte className="k-span-12 k-xl-9" id="fase-tabela" aria-label="Lista da fase">
                <EscolhaPainel grupo="formato" valores={["todos", "reels"]}>
                  <Suspense fallback={<EsqueletoTabela oque="a lista da fase" />}><TabelaDaFase /></Suspense>
                </EscolhaPainel>
                <EscolhaPainel grupo="formato" valores={["stories"]}>
                  <div className="kx-vazio-fase"><Vazio icone="inbox" titulo="Nenhum story ainda">Hoje a operação produz Reels. Quando houver stories, eles passam pelas mesmas fases e aparecem aqui.</Vazio></div>
                </EscolhaPainel>
                <EscolhaPainel grupo="formato" valores={["carrossel"]}>
                  <div className="kx-vazio-fase"><Vazio icone="inbox" titulo="Nenhum carrossel ainda">Hoje a operação produz Reels. Quando houver carrosséis, eles passam pelas mesmas fases e aparecem aqui.</Vazio></div>
                </EscolhaPainel>
              </Card>
              <div className="k-span-12 k-xl-3 k-lado">
                <Suspense fallback={<EsqueletoCard oque="os avisos" linhas={6} />}><Atencao /></Suspense>
                <Suspense fallback={<EsqueletoCard oque="os portões" linhas={5} />}><Portoes /></Suspense>
              </div>
            </div>
          </Secao>
        </Escolha>
      </Escolha>
    </FiltroLista>
  );
}
