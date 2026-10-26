import Alternador from "@/components/Alternador";
import { BotaoLink } from "@/components/Botao";
import CartaoAgente from "@/components/CartaoAgente";
import ErroBloco from "@/components/ErroBloco";
import { Secao } from "@/components/Pagina";
import Vazio from "@/components/Vazio";
import type { Agente, Departamento } from "@/lib/db";
import { primeiraMaiuscula } from "@/lib/formato";
import { agentes, departamentos, modelosRodados } from "@/lib/leituras";
import type { ModeloRodouDados } from "@/components/Chip";
import { fotoDoAgente } from "@/lib/retratos";

// Visão geral · Equipe (telas/visao-geral.md): filtros por departamento e até 5 cartões com foto. "Todos" mostra o Atlas
// e os 4 primeiros gerentes; cada departamento, até 5 pessoas, o gerente primeiro. O status "Trabalhando agora / Em
// espera" é EXEMPLO na maquete (não há dado de presença): aqui não aparece.

const funcao = (cargo: string) => primeiraMaiuscula(cargo.split(" · ")[0]);

function Cartoes({ pessoas, depto, rodou }: { pessoas: Agente[]; depto: Map<string, string>; rodou: Map<string, ModeloRodouDados> }) {
  if (pessoas.length === 0) {
    return (
      <Vazio icone="equipe" titulo="Ninguém neste departamento">
        Quando alguém entrar neste departamento, aparece aqui.
      </Vazio>
    );
  }
  return (
    <div className="k-agentes">
      {pessoas.map((a) => (
        <CartaoAgente
          key={a.id}
          href={`/equipe/${a.id}`}
          nome={a.nome}
          funcao={funcao(a.cargo)}
          departamento={primeiraMaiuscula(depto.get(a.departamento_id))}
          foto={fotoDoAgente(a.id)}
          portao={a.papel === "portao"}
          rodou={rodou.has(a.id) ? rodou.get(a.id)! : undefined}
        />
      ))}
    </div>
  );
}

export default async function EquipeResumo() {
  let ags: Agente[], deps: Departamento[];
  let rodou = new Map<string, ModeloRodouDados>();
  try {
    [ags, deps] = await Promise.all([agentes(), departamentos()]);
    try { rodou = await modelosRodados(); } catch { /* sem a leitura, o cartão fica sem modelo (nunca um "não rodou" falso) */ }
  } catch {
    return <Secao titulo="Equipe" estilo="h3" id="equipe"><ErroBloco oque="A equipe" /></Secao>;
  }
  const depto = new Map(deps.map((d) => [d.id, d.nome]));
  const porId = new Map(ags.map((a) => [a.id, a]));
  const areas = deps.filter((d) => d.id !== "direcao").sort((a, b) => a.ordem - b.ordem);
  const diretor = ags.find((a) => a.papel === "diretor");
  const gerentes = areas.map((d) => (d.gerente_id ? porId.get(d.gerente_id) : undefined)).filter((a): a is Agente => Boolean(a));
  const doDepto = (id: string) => {
    const d = areas.find((x) => x.id === id);
    const g = d?.gerente_id ? porId.get(d.gerente_id) : undefined;
    const resto = ags.filter((a) => a.departamento_id === id && a.id !== g?.id);
    return [...(g ? [g] : []), ...resto].slice(0, 5);
  };
  const todos = [...(diretor ? [diretor] : []), ...gerentes].slice(0, 5);

  return (
    <Secao
      titulo="Equipe"
      estilo="h3"
      id="equipe"
      sub={`${ags.length} pessoas em ${areas.length} departamentos e a direção`}
      acao={
        <BotaoLink href="/equipe" variante="fantasma" iconeFim="chevron-right">Ver equipe completa</BotaoLink>
      }
    >
      {ags.length === 0 ? (
        <Vazio icone="equipe" titulo="Equipe ainda não sincronizada">A equipe vem de .claude/agents/ e painel/equipe.yaml, pelo sincronizador.</Vazio>
      ) : (
        <Alternador
          estilo="filtros"
          rotulo="Filtrar por departamento"
          opcoes={[{ valor: "todos", rotulo: "Todos" }, ...areas.map((d) => ({ valor: d.id, rotulo: primeiraMaiuscula(d.nome) }))]}
          paineis={Object.fromEntries([
            ["todos", <Cartoes rodou={rodou} key="todos" pessoas={todos} depto={depto} />],
            ...areas.map((d) => [d.id, <Cartoes rodou={rodou} key={d.id} pessoas={doDepto(d.id)} depto={depto} />]),
          ])}
        />
      )}
    </Secao>
  );
}
