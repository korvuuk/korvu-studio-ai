import { Suspense } from "react";
import { EventoMes, EventoSemana, LegendaCalendario, VagaLivre, type EventoCal } from "@/components/Calendario";
import { Card, CardCabecalho } from "@/components/Card";
import ErroBloco from "@/components/ErroBloco";
import { EsqueletoCard } from "@/components/Esqueleto";
import NavCalendario, { VistaCalendario } from "@/components/NavCalendario";
import { BarraPagina, Secao } from "@/components/Pagina";
import Vazio from "@/components/Vazio";
import { Atalho, BotaoLink } from "@/components/Botao";
import { ListaKvGrande } from "@/components/ListaKv";
import { capa } from "@/lib/capas";
import { data, diaEmLondres, hora, num } from "@/lib/formato";
import * as db from "@/lib/db";
import { lerProducao, portoesDoPost, type Producao } from "@/lib/producao";

// Calendário editorial — telas/calendario.md + calendario.html (APROVADO, área design, 23/10 21:04). Mês (6 semanas a
// partir do domingo) e Semana (7 colunas com a capa grande), pelo endereço (?vista=semana&dia=AAAA-MM-DD). Hora de
// Londres (o publicar.py agenda nela). VAGAS: calendario_vagas (o bloco vagas_semanais do _controle/calendario.md, hora
// local no fuso dele, Europe/London por padrão) — vaga livre = dia de vaga de hoje em diante sem post; na Semana, a vaga
// passada sem post vira nota. Fora até o banco ter o dado: os MELHORES HORÁRIOS (print do app).

const MESES = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"];
const SEM = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"];
const MES_CURTO = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];

const somar = (dia: string, n: number) => new Date(Date.parse(`${dia}T12:00:00Z`) + n * 86_400_000).toISOString().slice(0, 10);
const semana = (dia: string) => new Date(`${dia}T12:00:00Z`).getUTCDay();
const rotulo = (dia: string) => `${SEM[semana(dia)]} ${Number(dia.slice(8))} ${MES_CURTO[Number(dia.slice(5, 7)) - 1]}`;

type Dia = { dia: string; eventos: EventoCal[] };

const NOME_DIA = ["", "segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"];
/** As vagas de um dia (dia ISO 1 = segunda … 7 = domingo), "21:00"; o fuso só aparece se não for o de Londres. */
function vagasDoDia(vagas: db.VagaCalendario[], dia: string): string[] {
  const iso = semana(dia) === 0 ? 7 : semana(dia);
  return vagas.filter((v) => v.dia_semana === iso)
    .map((v) => `${v.hora.slice(0, 5)}${v.fuso && v.fuso !== "Europe/London" ? ` (${v.fuso})` : ""}`);
}
async function lerVagas(): Promise<db.VagaCalendario[]> {
  try { return await db.calendarioVagas(); } catch { return []; } // sem vagas o calendário continua valendo
}

function eventosPorDia(p: Producao): Map<string, Dia> {
  const dias = new Map<string, Dia>();
  const de = (d: string) => {
    let x = dias.get(d);
    if (!x) dias.set(d, (x = { dia: d, eventos: [] }));
    return x;
  };
  for (const x of p.publicados) {
    if (!x.publicado_em) continue;
    const m = x.leitura;
    de(diaEmLondres(x.publicado_em)).eventos.push({
      href: "/producao#publicados", nome: x.nome, hora: hora(x.publicado_em), canais: x.plataformas ?? ["instagram"], publicado: true,
      capa: capa(x.slug, "publicados"),
      extra: m?.alcance != null ? `${num(m.alcance)} de alcance · ${x.trial ? "Trial" : "Normal"}`
        : `métricas em ${data(new Date(Date.parse(x.publicado_em) + 5 * 86_400_000).toISOString())}`,
    });
  }
  for (const f of p.agendados) {
    if (!f.publicar_em) continue;
    de(diaEmLondres(f.publicar_em)).eventos.push({
      href: "/producao#agendados", nome: f.nome, hora: hora(f.publicar_em), canais: f.plataformas, publicado: false,
      capa: capa(f.slug, "fila"), portoes: portoesDoPost(p, f),
      extra: `${f.trial ? "Trial Reel" : "Normal"}${f.palavra ? ` · palavra ${f.palavra}` : ""}`,
    });
  }
  for (const d of dias.values()) d.eventos.sort((a, b) => a.hora.localeCompare(b.hora));
  return dias;
}

async function Mes({ dia, hojeDia }: { dia: string; hojeDia: string }) {
  let p: Producao;
  try { p = await lerProducao(); } catch { return <ErroBloco oque="O calendário" />; }
  const vagas = await lerVagas();
  const dias = eventosPorDia(p);
  const primeiro = `${dia.slice(0, 7)}-01`;
  const inicio = somar(primeiro, -semana(primeiro));
  const celulas = Array.from({ length: 42 }, (_, i) => somar(inicio, i));
  const mes = dia.slice(0, 7);
  const algoNoMes = celulas.some((d) => d.startsWith(mes) && dias.get(d) && dias.get(d)!.eventos.length);
  return (
    <>
      <div className="k-mes-cab" aria-hidden="true">{SEM.map((s) => <span key={s} className="k-cap">{s}</span>)}</div>
      <div className="k-mes">
        {celulas.map((d) => {
          const x = dias.get(d);
          const hoje = d === hojeDia;
          const livres = d >= hojeDia && !x?.eventos.length ? vagasDoDia(vagas, d) : [];
          const vazio = !hoje && !x?.eventos.length && !livres.length;
          const classes = ["k-mes-dia", !d.startsWith(mes) && "is-fora", d < hojeDia && "is-passado", hoje && "is-hoje", vazio && "is-vazio"].filter(Boolean).join(" ");
          return (
            <div key={d} className={classes}>
              <span className="k-mes-n" aria-current={hoje ? "date" : undefined}>{d.endsWith("-01") ? `1 ${MES_CURTO[Number(d.slice(5, 7)) - 1]}` : Number(d.slice(8))}</span>
              <span className="k-mes-dl">{rotulo(d)}{hoje ? " · hoje" : ""}</span>
              {hoje && !x?.eventos.length && <span className="k-mes-dl k-mes-nada">Nada programado.</span>}
              {x?.eventos.map((e) => <EventoMes key={`${e.hora}-${e.nome}`} e={e} />)}
              {livres.map((h) => <VagaLivre key={h} hora={h} />)}
            </div>
          );
        })}
      </div>
      {!algoNoMes && (
        <div className="kx-vazio-fase">
          <Vazio icone="calendario" titulo="Nada programado neste mês" acao={<BotaoLink href="/producao" variante="secundario" pequeno>Ver produção</BotaoLink>}>
            Quando houver post agendado ou publicado, aparece no dia. As vagas livres das próximas semanas aparecem tracejadas.
          </Vazio>
        </div>
      )}
    </>
  );
}

async function Semana({ dia, hojeDia }: { dia: string; hojeDia: string }) {
  let p: Producao;
  try { p = await lerProducao(); } catch { return <ErroBloco oque="O calendário" />; }
  const vagas = await lerVagas();
  const dias = eventosPorDia(p);
  const inicio = somar(dia, -semana(dia));
  return (
    <div className="k-semana">
      {Array.from({ length: 7 }, (_, i) => somar(inicio, i)).map((d) => {
        const x = dias.get(d);
        const hoje = d === hojeDia;
        const semPost = !x?.eventos.length;
        const vagasDia = semPost ? vagasDoDia(vagas, d) : [];
        const perdida = vagasDia.length > 0 && d < hojeDia;
        const iso = semana(d) === 0 ? 7 : semana(d);
        return (
          <div key={d} className={`k-semana-dia${hoje ? " is-hoje" : ""}`}>
            <div className="k-semana-cab">
              <span className="k-mes-n">{SEM[semana(d)]} {Number(d.slice(8))}</span>
              <span className="k-semana-nota">{hoje ? "hoje" : perdida ? "vaga sem post" : ""}</span>
            </div>
            {x?.eventos.map((e) => <EventoSemana key={`${e.hora}-${e.nome}`} e={e} />)}
            {semPost && (perdida
              ? <span className="k-semana-vazio">A vaga de {NOME_DIA[iso]} {vagasDia.join(" e ")} ficou livre.</span>
              : vagasDia.length && !hoje ? vagasDia.map((h) => <VagaLivre key={h} hora={h} />)
              : <span className="k-semana-vazio">Nada programado.</span>)}
            {hoje && semPost && vagasDia.map((h) => <VagaLivre key={h} hora={h} />)}
          </div>
        );
      })}
    </div>
  );
}

async function Fila() {
  let p: Producao;
  try { p = await lerProducao(); } catch { return <ErroBloco oque="A fila" />; }
  const posts = p.agendados.filter((f) => f.publicar_em);
  const port = posts.map((f) => portoesDoPost(p, f));
  const prontos = port.filter((x) => x.legado || x.status === "aprovado").length;
  const aguardando = port.length - prontos;
  const legado = port.filter((x) => x.legado).length;
  const semHorario = p.vids.filter((v) => v.fase === "prontos");
  const semHorarioSaem = semHorario.filter((v) => !v.trava);
  const roteiros = p.vids.filter((v) => v.fase === "roteiros").length;
  if (posts.length === 0 && semHorario.length === 0) {
    return <Card como="section" pad><Vazio icone="clock" titulo="Fila vazia">Quando um pacote pronto for agendado, ele aparece aqui e no dia do calendário.</Vazio></Card>;
  }
  return (
    <Card como="section" className="kx-card-fila" aria-labelledby="t-fila">
      <CardCabecalho como="h2" id="t-fila" titulo="Fila" linha acao={<span className="k-mono k-muted">06-publicar/</span>} />
      <ListaKvGrande
        className="kx-kv-topo"
        itens={[
          { titulo: "Pronto para publicar", frase: "agendadas, saem sozinhas no horário", n: prontos },
          {
            titulo: "Aguardando portão",
            frase: aguardando ? "um portão ainda segura o post" : legado === posts.length && legado > 0 ? `as ${legado} da fila são legado: publicam sem selo` : "nenhum post esperando portão",
            n: aguardando,
          },
          {
            titulo: "Sem horário",
            frase: semHorarioSaem.length
              ? `${semHorarioSaem.length} ${semHorarioSaem.length === 1 ? "pacote pronto espera" : "pacotes prontos esperam"} data`
              : semHorario.length ? `o único pronto (${semHorario[0].nome}) tem trava e não sai` : "nenhum pacote pronto esperando data",
            n: semHorarioSaem.length,
          },
        ]}
      />
      {roteiros > 0 && (
        <Atalho href="/producao#roteiros">A caminho: {roteiros} {roteiros === 1 ? "roteiro" : "roteiros"} ainda sem gravação</Atalho>
      )}
    </Card>
  );
}

function MelhoresHorarios() {
  return (
    <Card como="section" className="kx-card-fila" aria-labelledby="t-hor">
      <CardCabecalho como="h2" id="t-hor" titulo="Melhores horários" linha acao={<span className="k-kpi-note">atividade de quem segue</span>} />
      <div className="kx-vazio-fase">
        <Vazio icone="clock" titulo="Sem print de horários">
          A atividade de quem segue por horário vem de um print do app do Instagram, que ainda não chega ao banco do painel. Quando chegar, as faixas de 3 horas aparecem aqui.
        </Vazio>
      </div>
    </Card>
  );
}

export default async function Calendario({ searchParams }: { searchParams: Promise<{ vista?: string; dia?: string }> }) {
  const sp = await searchParams;
  const vista = sp.vista === "semana" ? "semana" : "mes";
  const hojeDia = diaEmLondres(new Date());
  const dia = sp.dia && /^\d{4}-\d{2}-\d{2}$/.test(sp.dia) ? sp.dia : hojeDia;
  const inicioSemana = somar(dia, -semana(dia));
  const fimSemana = somar(inicioSemana, 6);
  const titulo = vista === "mes"
    ? `${MESES[Number(dia.slice(5, 7)) - 1]} ${dia.slice(0, 4)}`
    : `${Number(inicioSemana.slice(8))}${inicioSemana.slice(5, 7) !== fimSemana.slice(5, 7) ? ` ${MES_CURTO[Number(inicioSemana.slice(5, 7)) - 1]}` : ""} – ${Number(fimSemana.slice(8))} ${MES_CURTO[Number(fimSemana.slice(5, 7)) - 1]} ${fimSemana.slice(0, 4)}`;
  const anterior = vista === "mes" ? somar(`${dia.slice(0, 7)}-01`, -1).slice(0, 7) + "-01" : somar(dia, -7);
  const proximo = vista === "mes" ? somar(`${dia.slice(0, 7)}-28`, 7).slice(0, 7) + "-01" : somar(dia, 7);

  return (
    <>
      <BarraPagina titulo="Calendário" />
      <div className="k-cal-topo kx-cal-topo">
        <NavCalendario vista={vista} titulo={titulo} anterior={anterior} proximo={proximo} hoje={hojeDia} />
        <div className="k-row kx-row-20">
          <LegendaCalendario />
          <VistaCalendario vista={vista} dia={dia} />
        </div>
      </div>
      <Secao rotulo="Calendário e fila">
        <div className="k-grid">
          <Card como="section" recorte className="k-span-12 k-xxl-9" aria-label={`Calendário: ${titulo}`}>
            <Suspense key={`${vista}-${dia}`} fallback={<EsqueletoCard oque="o calendário" altura={520} />}>
              {vista === "mes" ? <Mes dia={dia} hojeDia={hojeDia} /> : <Semana dia={dia} hojeDia={hojeDia} />}
            </Suspense>
          </Card>
          <div className="k-span-12 k-xxl-3 k-lado k-lado--xxl">
            <Suspense fallback={<EsqueletoCard oque="a fila" linhas={3} />}><Fila /></Suspense>
            <MelhoresHorarios />
          </div>
        </div>
      </Secao>
    </>
  );
}
