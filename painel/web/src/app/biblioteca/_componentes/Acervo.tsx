import { statSync } from "node:fs";
import { join } from "node:path";
import {
  CabecalhoAcervo, CapaEstilo, CartaoFonte, CartaoLook, LegendaEstilo, LinhaAnimacao, SisFerramenta, SisModelo, type TomEtiqueta,
} from "@/components/Acervo";
import ErroBloco from "@/components/ErroBloco";
import Vazio from "@/components/Vazio";
import * as acervo from "@/lib/acervo";
import { capa, type PastaCapa } from "@/lib/capas";
import type { Look } from "@/lib/db";
import { data, dataDoSlug } from "@/lib/formato";
import { lerProducao, nomeCurto } from "@/lib/producao";

// Biblioteca · os blocos do acervo (telas/biblioteca.md): looks de cor, capas, legendas, fontes, animações e a aba
// Sistema. Tudo do banco (espelho de painel/biblioteca.yaml, 00-marca/cor/ e videos/*/animacoes/); as imagens fixas
// (o "Aa" das fontes e a amostra da legenda) são as da maquete aprovada, em public/biblioteca/. Cada bloco tem o vazio e o
// erro dele; o carregando é o esqueleto do Suspense na página.

/** "18 set" com espaço que não quebra (PI73). */
const dia = (iso: string | null) => data(iso && /^\d{4}-\d{2}-\d{2}$/.test(iso) ? `${iso}T12:00:00Z` : iso).replace(" ", " ");
const um = (n: number, casas = 1) => n.toLocaleString("pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas });
const existe = (publico: string) => {
  try { return statSync(join(process.cwd(), "public", publico)).isFile(); } catch { return false; }
};
const slug = (t: string) => t.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

// ── looks de cor ──────────────────────────────────────────────────────────────────────────────────────────────────
const ETIQUETA_PAPEL: Record<NonNullable<Look["papel"]>, { tom: TomEtiqueta; texto: string }> = {
  em_uso: { tom: "uso", texto: "Em uso" }, alternativa: { tom: "alt", texto: "Alternativa" }, arquivado: { tom: "arq", texto: "Arquivado" },
};
const base = (cube: string | null) => (cube ?? "").split("/").at(-1) ?? "";

function cartaoDoLook(l: Look) {
  const prioridade = true; // os 5 looks ficam na primeira dobra
  const foto = l.previa ? `/look/${l.id}` : null;
  if (l.tipo === "referencia") {
    return <CartaoLook key={l.id} nome={l.nome ?? "Original da câmera"} meta="V-Log, sem conversão" desc={l.descricao ?? undefined} foto={foto} etiqueta={{ tom: "ref", texto: "Referência" }} prioridade={prioridade} />;
  }
  if (l.tipo === "base") {
    return <CartaoLook key={l.id} nome={l.nome ?? "Só a conversão"} meta={`Rec.709 · ${base(l.cube)}`} desc={l.descricao ?? undefined} foto={foto} etiqueta={{ tom: "ref", texto: "Base" }} prioridade={prioridade} />;
  }
  const meta = l.rosto_ire != null
    ? `rosto ${um(l.rosto_ire)} IRE · medido em ${dia(l.rosto_ire_em)}`
    : [base(l.cube).replace(/\.cube$/, ""), l.criado_em ? dia(l.criado_em) : ""].filter(Boolean).join(" · ");
  return (
    <CartaoLook
      key={l.id}
      nome={l.nome ?? `Look ${l.id}`}
      meta={meta}
      desc={l.descricao ?? undefined}
      foto={foto}
      etiqueta={l.papel ? ETIQUETA_PAPEL[l.papel] : undefined}
      emUso={l.papel === "em_uso"}
      prioridade={prioridade}
    />
  );
}

export async function Looks() {
  let ls: Look[];
  try { ls = await acervo.looks(); } catch { return <ErroBloco oque="Os looks de cor" />; }
  return (
    <section aria-labelledby="t-looks">
      <CabecalhoAcervo id="t-looks" titulo="looks de cor." frase="a sua imagem com cada look · o mesmo quadro da gravação, sem outra correção" />
      {ls.length === 0
        ? <Vazio icone="eye" titulo="Nenhum look registrado">Cada look novo (.cube + .json em 00-marca/cor/luts/) aparece aqui, aplicado à sua foto.</Vazio>
        : <div className="k-looks">{ls.map((l) => cartaoDoLook(l))}</div>}
    </section>
  );
}

// ── capas ─────────────────────────────────────────────────────────────────────────────────────────────────────────
const PASTA_DA_CAPA: Record<string, PastaCapa> = { "07-publicados": "publicados", "06-publicar": "fila", "05-render-pronto": "pronto" };

export async function Capas() {
  let estilos, exemplos, p;
  try { [estilos, exemplos, p] = await Promise.all([acervo.capaEstilos(), acervo.capaExemplos(), lerProducao()]); } catch { return <ErroBloco oque="Os estilos de capa" />; }
  const nomeDoVideo = (s: string | null) => (s ? p.vids.find((v) => v.slug === s)?.nome ?? nomeCurto(s) : "");
  return (
    <section aria-labelledby="t-capas">
      <CabecalhoAcervo id="t-capas" titulo="capas." frase={`${estilos.length} ${estilos.length === 1 ? "estilo" : "estilos"}, sempre com a sua foto`} />
      {estilos.length === 0 ? <Vazio icone="eye" titulo="Nenhum estilo de capa">Um estilo novo no painel/biblioteca.yaml aparece aqui, com as capas em que foi usado.</Vazio> : (
        <div className="k-card k-capas-estilos">
          {estilos.map((e) => {
            const ex = exemplos.filter((x) => x.estilo_id === e.id).sort((a, b) => a.ordem - b.ordem);
            const capas = ex.flatMap((x) => {
              const pasta = x.pasta ? PASTA_DA_CAPA[x.pasta] : undefined;
              const src = pasta ? capa(x.slug, pasta) : null;
              const post = [...p.publicados, ...p.agendados].find((y) => y.slug === x.slug)?.nome;
              return src ? [{ src, alt: `Capa de ${post ?? nomeDoVideo(x.video_slug ?? x.slug)}` }] : [];
            });
            const datas = ex.map((x) => dataDoSlug(x.slug)).filter((d): d is string => Boolean(d)).sort();
            const video = nomeDoVideo(ex[0]?.video_slug ?? null);
            const meta = e.em_uso
              ? (datas[0] ? `em uso desde ${dia(datas[0])}` : "em uso")
              : [datas[0] ? `usado em ${dia(datas[0])}` : "", video].filter(Boolean).join(" · ");
            return <CapaEstilo key={e.id} nome={e.nome} desc={e.descricao} meta={meta || undefined} capas={capas} />;
          })}
        </div>
      )}
    </section>
  );
}

// ── legendas ──────────────────────────────────────────────────────────────────────────────────────────────────────
export async function Legendas() {
  let estilos;
  try { estilos = await acervo.legendaEstilos(); } catch { return <ErroBloco oque="Os estilos de legenda" />; }
  return (
    <section aria-labelledby="t-leg">
      <CabecalhoAcervo id="t-leg" titulo="legendas." frase={`${estilos.length} ${estilos.length === 1 ? "estilo" : "estilos"}`} />
      {estilos.length === 0 ? <Vazio icone="eye" titulo="Nenhum estilo de legenda">Um estilo novo no painel/biblioteca.yaml aparece aqui, com a amostra.</Vazio>
        : estilos.map((e) => {
          const amostra = `/biblioteca/legenda-${e.id}.png`;
          return (
            <LegendaEstilo
              key={e.id} nome={e.nome} desc={e.descricao} meta={e.em_uso ? "em todos os Reels" : undefined}
              amostra={existe(amostra) ? amostra : null} alt={`Amostra do estilo ${e.nome}`}
            />
          );
        })}
    </section>
  );
}

// ── fontes ────────────────────────────────────────────────────────────────────────────────────────────────────────
export async function Fontes() {
  let fs;
  try { fs = (await acervo.fontes()).filter((f) => !f.reserva); } catch { return <ErroBloco oque="As fontes" />; }
  return (
    <section aria-labelledby="t-fontes">
      <CabecalhoAcervo id="t-fontes" titulo="fontes." frase={`${fs.length} ${fs.length === 1 ? "família" : "famílias"} em uso`} />
      {fs.length === 0 ? <Vazio icone="eye" titulo="Nenhuma fonte registrada">As famílias do painel/biblioteca.yaml aparecem aqui, com onde cada uma é usada.</Vazio> : (
        <div className="k-tipos">
          {fs.map((f) => {
            const amostra = `/biblioteca/fonte-${slug(f.familia)}.png`;
            return <CartaoFonte key={f.familia} familia={f.familia} uso={f.uso} amostra={existe(amostra) ? amostra : null} />;
          })}
        </div>
      )}
    </section>
  );
}

// ── animações ─────────────────────────────────────────────────────────────────────────────────────────────────────
const MODO: Record<string, string> = { split: "metade de cima", full: "tela cheia", card: "cartão" };

export async function Animacoes() {
  let as, p;
  try { [as, p] = await Promise.all([acervo.animacoes(), lerProducao()]); } catch { return <ErroBloco oque="As animações" />; }
  const nomeDoVideo = (s: string) => p.vids.find((v) => v.slug === s)?.nome ?? nomeCurto(s);
  return (
    <section aria-labelledby="t-anim">
      <CabecalhoAcervo id="t-anim" titulo="animações." frase="estilos para os próximos vídeos" />
      {as.length === 0 ? <Vazio icone="play" titulo="Nenhuma animação ainda">Cada brief em videos/&lt;slug&gt;/animacoes/ aparece aqui, roteirizada ou renderizada.</Vazio> : (
        <div className="k-card k-anims">
          {as.map((a) => (
            <LinhaAnimacao
              key={a.id}
              nome={a.titulo ?? a.codigo}
              meta={[a.modo ? MODO[a.modo] : "", a.duracao_s != null ? `${um(a.duracao_s)} s` : "", nomeDoVideo(a.video_slug)].filter(Boolean).join(" · ")}
              renderizada={a.renderizada}
            />
          ))}
        </div>
      )}
    </section>
  );
}

// ── aba Sistema ───────────────────────────────────────────────────────────────────────────────────────────────────
export async function Sistema() {
  let modelos, fs;
  try { [modelos, fs] = await Promise.all([acervo.sistemaModelos(), acervo.ferramentas()]); } catch { return <ErroBloco oque="O sistema" />; }
  const ordem = [...modelos].sort((a, b) => (b.pct_tokens ?? 0) - (a.pct_tokens ?? 0));
  return (
    <section aria-labelledby="t-sis-aba">
      <CabecalhoAcervo id="t-sis-aba" titulo="sistema." frase="o que cada peça é e o que faz neste estúdio · para quem chegar pelo GitHub" />
      {ordem.length === 0 ? <Vazio icone="cpu" titulo="Nenhum modelo rodou nos 30 dias">Quando o Claude Code rodar, cada modelo aparece aqui com a parte dos tokens.</Vazio> : (
        <div className="k-sis-modelos">
          {ordem.map((m) => <SisModelo key={m.modelo} nome={m.modelo_nome ?? m.modelo} pct={`${um(m.pct_tokens ?? 0)} %`} desc={m.descricao} />)}
        </div>
      )}
      {fs.length === 0 ? <div className="kx-corpo-grafico"><Vazio icone="settings" titulo="Nenhuma ferramenta descrita">As ferramentas do painel/biblioteca.yaml aparecem aqui, cada uma com o que faz.</Vazio></div> : (
        <div className="k-card k-sis-lista">
          {fs.map((f) => <SisFerramenta key={f.nome} nome={f.nome} tipo={f.tipo} desc={f.descricao} />)}
        </div>
      )}
    </section>
  );
}
