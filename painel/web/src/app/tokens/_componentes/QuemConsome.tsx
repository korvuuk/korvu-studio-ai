import { Card, CabecalhoGrafico } from "@/components/Card";
import { ChipModelo } from "@/components/Chip";
import ErroBloco from "@/components/ErroBloco";
import { Escolha, EscolhaBotoes, EscolhaPainel } from "@/components/Escolha";
import { PosicaoRanking } from "@/components/Graficos";
import { CelulaPessoa, TabelaNoCard } from "@/components/Tabela";
import Vazio from "@/components/Vazio";
import { compacto, num, primeiraMaiuscula, usd } from "@/lib/formato";
import { fotoDoAgente } from "@/lib/retratos";
import { type LeituraTokens, lerTokens, type Pessoa } from "@/lib/tokens";

// Tokens e custos · quem mais consome. (telas/tokens-e-custos.md): Gerentes | Ranking geral. "Rodou em" = o modelo que
// aparece nos registros (precos_modelo.nome, com a versão), que pode ser diferente do configurado hoje. Tokens em
// accent-ink, custo em US$, tarefas (execuções com consumo nos 30 dias, a mesma conta da Equipe) e o custo por tarefa.
// Quem não rodou nos 30 dias: "—" e "não rodou". O nome leva à ficha.

const COLUNAS = [
  { t: "#" }, { t: "Agente" }, { t: "Rodou em" }, { t: "Tokens", dir: true }, { t: "Custo", dir: true },
  { t: "Tarefas", dir: true }, { t: "Por tarefa", dir: true },
];

function Tabela({ rotulo, pessoas, t }: { rotulo: string; pessoas: Pessoa[]; t: LeituraTokens }) {
  const custo = (v: number) => usd(v);
  const dep = (id: string) => primeiraMaiuscula(t.deps.find((d) => d.id === id)?.nome ?? id);
  return (
    <TabelaNoCard rotulo={rotulo} min={640} colunas={COLUNAS}>
      {pessoas.map((p, i) => {
        const a = p.agente;
        const rodou = p.tokens > 0;
        return (
          <tr key={a.id}>
            <td><PosicaoRanking n={i + 1} /></td>
            <td>
              <CelulaPessoa
                nome={a.nome}
                foto={fotoDoAgente(a.id)}
                href={`/equipe/${a.id}`}
                meta={`${dep(a.departamento_id)}${a.papel === "portao" ? " · portão" : ""}`}
              />
            </td>
            <td>
              {rodou && p.modelosOrdem.length > 0
                ? <span className="k-row kx-row-4">{p.modelosOrdem.map((m) => <ChipModelo key={m} modelo={m} rotulo={m} pequeno />)}</span>
                : <span className="k-muted">—</span>}
            </td>
            <td className="k-dir">{rodou ? <span className="k-n k-tokens">{compacto(p.tokens)}</span> : <span className="k-muted">—</span>}</td>
            <td className="k-dir">{rodou ? <span className="k-n">{custo(p.usd)}</span> : <span className="k-muted">—</span>}</td>
            <td className="k-dir">{rodou ? <span className="k-n">{num(p.tarefas)}</span> : <span className="k-muted">—</span>}</td>
            <td className="k-dir">
              {!rodou ? <span className="k-sub">não rodou</span>
                : p.tarefas > 0 ? <span className="k-n">{custo(p.usd / p.tarefas)}</span>
                : <span className="k-muted">—</span>}
            </td>
          </tr>
        );
      })}
    </TabelaNoCard>
  );
}

const primeiro = (nome: string) => nome.split(" ")[0];
const juntar = (xs: string[]) => (xs.length > 1 ? `${xs.slice(0, -1).join(", ")} e ${xs.at(-1)}` : xs[0] ?? "");

export default async function QuemConsome() {
  let t: LeituraTokens;
  try {
    t = await lerTokens();
  } catch {
    return <div className="k-span-12 k-xl-5 k-fim-ate-xl"><ErroBloco oque="Quem mais consome" /></div>;
  }
  if (t.ranking.length === 0) {
    return (
      <Card como="section" className="kx-card-grafico k-span-12 k-xl-5 k-fim-ate-xl" aria-labelledby="t-quem">
        <CabecalhoGrafico id="t-quem" titulo="quem mais consome." />
        <div className="kx-corpo-grafico">
          <Vazio icone="users" titulo="Ninguém rodou ainda">Quando um agente trabalhar numa sessão, ele entra no ranking com tokens, custo e tarefas.</Vazio>
        </div>
      </Card>
    );
  }
  const parados = t.gerentes.filter((p) => p.tokens === 0).map((p) => primeiro(p.agente.nome));
  return (
    <Card como="section" className="kx-card-grafico k-span-12 k-xl-5 k-fim-ate-xl" aria-labelledby="t-quem">
      <Escolha nome="quem" inicial="ger">
        <CabecalhoGrafico
          id="t-quem"
          titulo="quem mais consome."
          acao={<EscolhaBotoes grupo="quem" estilo="seg" rotulo="Quem mostrar" controla="quem-tabela" opcoes={[{ valor: "ger", rotulo: "Gerentes" }, { valor: "todos", rotulo: "Ranking geral" }]} />}
        />
        <div id="quem-tabela" className="kx-corpo-grafico">
          <EscolhaPainel grupo="quem" valores={["ger"]}>
            <Tabela rotulo="Gerentes por consumo" pessoas={t.gerentes} t={t} />
            <p className="k-fonte kx-fonte-bloco">
              {parados.length > 0 ? `${juntar(parados)} ainda não ${parados.length === 1 ? "rodou" : "rodaram"} nos 30 dias: os portões começaram em 22 out. ` : ""}
              “Rodou em” é o modelo que aparece nos registros, que pode ser diferente do configurado hoje.
            </p>
          </EscolhaPainel>
          <EscolhaPainel grupo="quem" valores={["todos"]}>
            <Tabela rotulo="Ranking geral por consumo" pessoas={t.ranking} t={t} />
            <p className="k-fonte kx-fonte-bloco">
              Tarefa = uma execução do agente nos 30 dias.{t.diretor ? ` O ${t.diretor.nome} soma as sessões e os ajudantes${t.ajudantes.length ? ` (${t.ajudantes.join(", ")})` : ""}.` : ""}
            </p>
          </EscolhaPainel>
        </div>
      </Escolha>
    </Card>
  );
}
