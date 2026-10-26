import { Suspense } from "react";
import { Departamento, Direcao, LinhaPessoa } from "@/components/Equipe";
import ErroBloco from "@/components/ErroBloco";
import { EsqueletoCard, EsqueletoKpis } from "@/components/Esqueleto";
import { BuscaLista, FiltroLista, FiltrosLista } from "@/components/FiltroLista";
import { KpiLinha } from "@/components/Kpi";
import { BarraPagina, Secao } from "@/components/Pagina";
import Vazio from "@/components/Vazio";
import { type ConsumoMembro, consumoPorMembro, custo, tokensCurto } from "@/lib/consumo";
import type { Agente, Departamento as Depto } from "@/lib/db";
import { num, primeiraMaiuscula, usdPartes } from "@/lib/formato";
import { agentes, consumo30, departamentos, execucoes30, type ModeloRodou, modelosRodados } from "@/lib/leituras";
import { fotoDoAgente } from "@/lib/retratos";

// Equipe — telas/equipe.md + equipe.html (APROVADO, área design, 23/10 21:04). Filtros (Todos · Portões · Opus 5.5 ·
// Sonnet 5.5) e a busca escondem as linhas que não passam. O filtro "Ativos", a coluna Status e a legenda do status são
// EXEMPLO na maquete (não há dado de presença): ficam fora até existir.

const funcao = (cargo: string) => primeiraMaiuscula(cargo.split(" · ")[0]);
/** "gerente de pesquisa · portão da pauta" → "Portão da pauta"; "portão dos dados" → "Portão dos dados". */
const portaoDe = (a: Agente) => (a.papel === "portao" ? primeiraMaiuscula(a.cargo.split(" · ").at(-1)) : null);

type Dados = { ags: Agente[]; deps: Depto[]; consumo: Map<string, ConsumoMembro> | null; rodou: Map<string, ModeloRodou | null> | null };

async function ler(): Promise<Dados> {
  const [ags, deps] = await Promise.all([agentes(), departamentos()]);
  // o consumo vem de outra parte do banco: se faltar, a equipe aparece e o consumo mostra "—"
  let consumo: Map<string, ConsumoMembro> | null = null;
  try {
    const [linhas, execs] = await Promise.all([consumo30(), execucoes30()]);
    consumo = consumoPorMembro(linhas, execs);
  } catch {
    consumo = null;
  }
  // o modelo que RODOU (modelo_por_agente, decisão de 24/10); sem a leitura, a coluna fica vazia (nunca um "não rodou" falso)
  let rodou: Map<string, ModeloRodou | null> | null = null;
  try { rodou = await modelosRodados(); } catch { rodou = null; }
  return { ags, deps, consumo, rodou };
}

/** "Opus 5.5" → "m-opus-5-5": a etiqueta do filtro (data-tags separa por espaço). */
const tagModelo = (nome: string) => `m-${nome.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/-$/, "")}`;

/** O modelo principal que rodou, pelo modelo_nome da view ("Opus 5.5"); "naorodou"; "" sem a leitura (PI76). */
function familiaRodou(d: Dados, id: string): string {
  if (!d.rodou) return "";
  const r = d.rodou.get(id);
  return r ? tagModelo(r.principal.nome) : "naorodou";
}
/** Os modelos principais que rodaram, do mais comum ao menos, com quantos agentes cada. */
function modelosPrincipais(d: Dados): { nome: string; n: number }[] {
  const conta = new Map<string, number>();
  for (const a of d.ags) { const r = d.rodou?.get(a.id); if (r) conta.set(r.principal.nome, (conta.get(r.principal.nome) ?? 0) + 1); }
  return [...conta.entries()].map(([nome, n]) => ({ nome, n })).sort((a, b) => b.n - a.n || a.nome.localeCompare(b.nome));
}
const rodouDe = (d: Dados, id: string) => (d.rodou ? d.rodou.get(id) ?? null : undefined);

function tags(d: Dados, a: Agente) {
  return ["todos", a.papel === "portao" ? "portoes" : "", familiaRodou(d, a.id)].filter(Boolean).join(" ");
}

async function NumerosDaEquipe() {
  let d: Dados;
  try { d = await ler(); } catch { return <ErroBloco oque="Os números da equipe" />; }
  if (d.ags.length === 0) return <Vazio icone="equipe" titulo="Equipe ainda não sincronizada">A equipe vem de .claude/agents/ e painel/equipe.yaml, pelo sincronizador.</Vazio>;
  const areas = d.deps.filter((x) => x.id !== "direcao");
  const porModelo = (m: string) => d.ags.filter((a) => familiaRodou(d, a.id) === m).length;
  const portoes = d.ags.filter((a) => a.papel === "portao");
  const gerentes = new Set(areas.map((x) => x.gerente_id));
  const outros = portoes.filter((a) => !gerentes.has(a.id));
  let tokens = 0, usd = 0;
  for (const c of d.consumo?.values() ?? []) { tokens += c.tokens; usd += c.usd; }
  return (
    <div className="k-grid k-grid--tiles">
      <KpiLinha
        className="k-span-3"
        rotulo="Agentes"
        valor={num(d.ags.length)}
        nota={d.rodou
          ? `rodaram em ${modelosPrincipais(d).map((m) => `${m.nome}: ${m.n}`).join(" · ")} · ainda não: ${porModelo("naorodou")}`
          : "o modelo que rodou não veio do banco"}
      />
      <KpiLinha className="k-span-3" rotulo="Departamentos" valor={num(areas.length)} nota="mais a direção" />
      <KpiLinha
        className="k-span-3"
        rotulo="Portões"
        valor={num(portoes.length)}
        nota={`um gerente por departamento${outros.length ? ` + ${outros.map((a) => (portaoDe(a) ?? "").replace(/^Portão d[aoe]s? /, "")).join(", ")}` : ""}`}
      />
      {d.consumo ? (
        <KpiLinha
          className="k-span-3"
          rotulo="Tokens · 30 dias"
          valor={tokensCurto(tokens).replace(/[KM]$/, "")}
          unidade={/[KM]$/.test(tokensCurto(tokens)) ? tokensCurto(tokens).slice(-1) : undefined}
          tokens
          href="/tokens"
          nota={`${custo(usd, 0)} equivalente na API, preço de tabela`}
        />
      ) : (
        <KpiLinha className="k-span-3" rotulo="Tokens · 30 dias" valor="—" nota="o consumo não veio do banco" />
      )}
    </div>
  );
}

function consumoDa(d: Dados, id: string) {
  const c = d.consumo?.get(id);
  return c && c.tokens > 0 ? { tokens: tokensCurto(c.tokens), custo: custo(c.usd) } : null;
}

async function Pessoas() {
  let d: Dados;
  try { d = await ler(); } catch { return <ErroBloco oque="A equipe" />; }
  if (d.ags.length === 0) return null;
  const porId = new Map(d.ags.map((a) => [a.id, a]));
  const diretor = d.ags.find((a) => a.papel === "diretor");
  const areas = d.deps.filter((x) => x.id !== "direcao").sort((a, b) => a.ordem - b.ordem);
  const cDir = diretor ? d.consumo?.get(diretor.id) : undefined;

  return (
    <>
      {diretor && (
        <Secao rotulo="Direção">
          <Direcao
            href={`/equipe/${diretor.id}`}
            nome={diretor.nome}
            cargo={funcao(diretor.cargo)}
            resumo={diretor.resumo}
            foto={fotoDoAgente(diretor.id)}
            rodou={rodouDe(d, diretor.id)}
            tags={tags(d, diretor)}
            busca={`${diretor.nome} ${diretor.cargo}`}
            numeros={[
              { rotulo: "Tarefas · 30 dias", valor: cDir ? num(cDir.tarefas) : "—" },
              { rotulo: "Tokens · 30 dias", valor: cDir ? tokensCurto(cDir.tokens) : "—", tokens: true },
              {
                rotulo: "Custo estimado",
                valor: cDir ? usdPartes(cDir.usd).valor : "—",
                prefixo: cDir ? "US$" : undefined,
              },
              ...(cDir && cDir.modelos.size > 0 ? [{ rotulo: "Rodou em", modelos: [...cDir.modelos] }] : []),
            ]}
          />
        </Secao>
      )}
      <Secao rotulo="Departamentos">
        <div className="k-deptos">
          {areas.map((dep) => {
            const gerente = dep.gerente_id ? porId.get(dep.gerente_id) : undefined;
            const time = d.ags.filter((a) => a.departamento_id === dep.id && a.id !== gerente?.id).sort((a, b) => a.nome.localeCompare(b.nome, "pt-BR"));
            const pessoas = [...(gerente ? [gerente] : []), ...time];
            let tk = 0, usd = 0;
            for (const p of pessoas) { const c = d.consumo?.get(p.id); if (c) { tk += c.tokens; usd += c.usd; } }
            return (
              <Departamento
                key={dep.id}
                nome={primeiraMaiuscula(dep.nome)}
                quantos={pessoas.length}
                soma={d.consumo && tk > 0 ? { tokens: tokensCurto(tk), custo: custo(usd) } : null}
              >
                {pessoas.length === 0 ? (
                  <li><Vazio icone="equipe" titulo="Ninguém neste departamento" /></li>
                ) : pessoas.map((a) => (
                  <LinhaPessoa
                    key={a.id}
                    href={`/equipe/${a.id}`}
                    nome={a.nome}
                    funcao={funcao(a.cargo)}
                    portao={portaoDe(a)}
                    foto={fotoDoAgente(a.id)}
                    rodou={rodouDe(d, a.id)}
                    consumo={consumoDa(d, a.id)}
                    tarefas={d.consumo?.get(a.id)?.tarefas || null}
                    gerente={a.id === gerente?.id}
                    tags={tags(d, a)}
                    busca={`${a.nome} ${a.cargo}`}
                  />
                ))}
              </Departamento>
            );
          })}
        </div>
      </Secao>
    </>
  );
}

async function Filtros() {
  let d: Dados;
  try { d = await ler(); } catch { return null; }
  const n = (m: string) => d.ags.filter((a) => familiaRodou(d, a.id) === m).length;
  return (
    <div className="k-section-head kx-filtros-linha">
      <FiltrosLista
        rotulo="Filtrar agentes"
        opcoes={[
          { valor: "todos", rotulo: "Todos", n: d.ags.length },
          { valor: "portoes", rotulo: "Portões", n: d.ags.filter((a) => a.papel === "portao").length },
          ...(d.rodou ? [
            ...modelosPrincipais(d).map((m) => ({ valor: tagModelo(m.nome), rotulo: m.nome, n: m.n })),
            { valor: "naorodou", rotulo: "Ainda não rodou", n: n("naorodou") },
          ] : []),
        ]}
      />
      <p className="k-fonte kx-sem-margem">
        modelo, consumo e tarefas: 30 dias, registros do Claude Code (o modelo é o que rodou) · custo em US$, preço de tabela da API
      </p>
    </div>
  );
}

export default function Equipe() {
  return (
    <FiltroLista>
      <BarraPagina titulo="Equipe">
        <BuscaLista placeholder="Buscar agente…" rotulo="Buscar agente por nome ou função" />
      </BarraPagina>
      <Secao rotulo="Filtros e números da equipe">
        <Suspense fallback={null}><Filtros /></Suspense>
        <Suspense fallback={<EsqueletoKpis oque="os números da equipe" />}><NumerosDaEquipe /></Suspense>
      </Secao>
      <Suspense fallback={<Secao rotulo="Equipe"><EsqueletoCard oque="a equipe" linhas={8} /></Secao>}>
        <Pessoas />
      </Suspense>
    </FiltroLista>
  );
}

