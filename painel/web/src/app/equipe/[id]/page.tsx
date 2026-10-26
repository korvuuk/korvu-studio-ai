import Link from "next/link";
import { notFound } from "next/navigation";
import Avatar from "@/components/Avatar";
import { BotaoLink } from "@/components/Botao";
import { ChipModelo, ChipPortao } from "@/components/Chip";
import { CabecalhoPagina, Secao } from "@/components/Pagina";
import { Tabela } from "@/components/Tabela";
import { Codigo, ListaDados } from "@/components/Texto";
import Vazio from "@/components/Vazio";
import * as db from "@/lib/db";
import { alvoLegivel, resumoMotivos } from "@/lib/estados";
import {
  dataHora, listaPortoes, NOME_PORTAO, portoesDoAgente, primeiraMaiuscula, tituloVideo,
} from "@/lib/formato";
import { fotoDoAgente } from "@/lib/retratos";

// Ficha de uma pessoa da equipe — a mesma informação de antes, nas peças do sistema e com a foto (ou as iniciais).

const PAPEL: Record<string, string> = {
  diretor: "Diretor", portao: "Portão (gerente)", construtor: "Construtor", analista: "Analista",
};

/** O veredicto gravado ("APROVADO", "BLOQUEADO", "ESCALADO") no chip do mapa único; outro texto aparece como veio. */
function Veredicto({ resultado }: { resultado: string }) {
  const v = resultado.trim().toLowerCase();
  if (v === "aprovado" || v === "bloqueado" || v === "escalado") return <ChipPortao status={v} />;
  return <span>{resultado}</span>;
}

export default async function Ficha({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const [a, ags, deps, estados, vs, vids] = await Promise.all([
    db.agente(id), db.agentes(), db.departamentos(), db.portoesEstado(), db.veredictos(), db.videos(),
  ]);
  if (!a) notFound();
  const nome = new Map(ags.map((x) => [x.id, x]));
  const dep = deps.find((d) => d.id === a.departamento_id);
  const tema = new Map(vids.map((v) => [v.slug, tituloVideo(v.slug, v.tema)]));
  // todos os portões deste agente (o portao-interface audita dois: design e interface do painel)
  const portoes = portoesDoAgente(a.id);
  const meusEstados = estados.filter((e) => portoes.includes(e.portao) && e.status !== "nao_se_aplica");
  const meusVeredictos = vs.filter((v) => portoes.includes(v.portao)).reverse().slice(0, 12);
  const fiscal = a.fiscalizado_por ? nome.get(a.fiscalizado_por) : undefined;
  const fiscalizados = a.fiscaliza.map((f) => nome.get(f)).filter((x): x is db.Agente => Boolean(x));

  const dados = [
    { rotulo: "Papel", valor: PAPEL[a.papel] ?? a.papel },
    { rotulo: "O que faz", valor: <span className="k-ink2">{a.descricao ?? "—"}</span> },
    { rotulo: "Modelo", valor: a.modelo ? <ChipModelo modelo={a.modelo} /> : "—" },
    {
      rotulo: "Skills",
      valor: a.skills.length
        ? <span className="kx-codigos">{a.skills.map((s) => <Codigo key={s}>{s}</Codigo>)}</span>
        : <span className="k-ink2">Usa scripts do projeto, nenhuma skill própria</span>,
    },
    {
      rotulo: "Comandos",
      valor: a.comandos.length ? <span className="kx-codigos">{a.comandos.map((c) => <Codigo key={c}>/{c}</Codigo>)}</span> : "—",
    },
    { rotulo: "Ferramentas", valor: <span className="k-ink2">{a.ferramentas.join(" · ") || "—"}</span> },
    ...(fiscal ? [{
      rotulo: "O trabalho passa por",
      valor: <Link className="k-link" href={`/equipe/${fiscal.id}`}>{fiscal.nome} — {fiscal.cargo}</Link>,
    }] : []),
    ...(fiscalizados.length ? [{
      rotulo: "Fiscaliza",
      valor: (
        <span className="kx-codigos">
          {fiscalizados.map((f, i) => (
            <span key={f.id}>
              <Link className="k-link" href={`/equipe/${f.id}`}>{f.nome}</Link>
              <span className="k-ink2"> · {f.cargo}{i < fiscalizados.length - 1 ? ";" : ""}</span>
            </span>
          ))}
        </span>
      ),
    }] : []),
    ...(portoes.length ? [{ rotulo: portoes.length > 1 ? "Portões" : "Portão", valor: primeiraMaiuscula(listaPortoes(portoes)) }] : []),
    ...(a.arquivo ? [{ rotulo: "Arquivo", valor: <Codigo>{a.arquivo}</Codigo> }] : []),
  ];

  return (
    <>
      <div className="mb-6">
        <BotaoLink href="/equipe" variante="fantasma" pequeno className="-ml-2.5">Voltar para a equipe</BotaoLink>
      </div>
      <div className="flex flex-wrap items-start gap-6">
        <Avatar nome={a.nome} foto={fotoDoAgente(a.id)} tamanho={120} />
        <div className="min-w-0 flex-1">
          <CabecalhoPagina
            sobretitulo={primeiraMaiuscula(dep?.nome)}
            titulo={a.nome}
            descricao={<>{primeiraMaiuscula(a.cargo)}. {a.resumo}{a.personalidade ? <><br />{a.personalidade}</> : null}</>}
          />
        </div>
      </div>

      <Secao titulo="A função">
        <div className="k-card k-pad"><ListaDados itens={dados} /></div>
      </Secao>

      {portoes.length > 0 && (
        <Secao
          titulo="O que passa por aqui"
          descricao={`Estado ${portoes.length > 1 ? `dos portões ${listaPortoes(portoes)}` : `do portão ${listaPortoes(portoes)}`} em cada alvo: vídeos, fila de publicação ou o próprio painel.`}
        >
          {meusEstados.length === 0 ? (
            <Vazio icone="lock" titulo="Nenhum alvo com este portão ainda">
              Quando um vídeo, um post ou o painel passar por este portão, o estado aparece aqui.
            </Vazio>
          ) : (
            <Tabela rotulo="Estado do portão em cada alvo (a tabela rola para o lado)" larguraMinima={560}>
              <thead>
                <tr>
                  <th scope="col">Alvo</th>
                  {portoes.length > 1 && <th scope="col">Portão</th>}
                  <th scope="col">Estado</th>
                  <th scope="col">Volta</th>
                </tr>
              </thead>
              <tbody>
                {meusEstados.map((e) => (
                  <tr key={e.alvo + e.portao}>
                    <td>{alvoLegivel(e, (s) => tema.get(s))}</td>
                    {portoes.length > 1 && <td>{primeiraMaiuscula(NOME_PORTAO[e.portao] ?? e.portao)}</td>}
                    <td>
                      <ChipPortao
                        status={e.status}
                        dica={resumoMotivos(e.motivos) ? { titulo: primeiraMaiuscula(NOME_PORTAO[e.portao] ?? e.portao), detalhe: resumoMotivos(e.motivos) } : undefined}
                      />
                    </td>
                    <td className="k-num k-ink2">{e.volta > 0 ? e.volta : "—"}</td>
                  </tr>
                ))}
              </tbody>
            </Tabela>
          )}
        </Secao>
      )}

      {portoes.length > 0 && (
        <Secao titulo="Veredictos recentes" descricao="Os 12 mais novos deste portão.">
          {meusVeredictos.length === 0 ? (
            <Vazio icone="clock" titulo="Nenhum veredicto ainda">
              Este portão ainda não deu nenhum veredicto — o GAUNTLET entrou em 22/10.
            </Vazio>
          ) : (
            <Tabela rotulo="Veredictos recentes (a tabela rola para o lado)" larguraMinima={720}>
              <thead>
                <tr>
                  <th scope="col">Quando</th><th scope="col">Veredicto</th><th scope="col">Alvo</th>
                  <th scope="col">Volta</th><th scope="col">S0 · S1 · S2</th>
                </tr>
              </thead>
              <tbody>
                {meusVeredictos.map((v) => (
                  <tr key={`${v.alvo}#${v.ordem}`}>
                    <td className="k-num k-ink2">{dataHora(v.em)}</td>
                    <td><Veredicto resultado={v.resultado} /></td>
                    <td>
                      {portoes.length > 1 ? `${primeiraMaiuscula(NOME_PORTAO[v.portao] ?? v.portao)} · ` : ""}
                      {alvoLegivel(v, (s) => tema.get(s))}
                    </td>
                    <td className="k-num">{v.volta}</td>
                    <td className="k-num k-ink2">{v.s0} · {v.s1} · {v.s2}</td>
                  </tr>
                ))}
              </tbody>
            </Tabela>
          )}
        </Secao>
      )}
    </>
  );
}
