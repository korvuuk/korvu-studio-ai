import Alternador from "@/components/Alternador";
import { Card } from "@/components/Card";
import ErroBloco from "@/components/ErroBloco";
import { BarrasFinas, TabelaGemea } from "@/components/Graficos";
import Vazio from "@/components/Vazio";
import type { Demografia } from "@/lib/db";
import { num, pais } from "@/lib/formato";
import { demografia, snapshots } from "@/lib/leituras";

// Visão geral · Público · Top 10 países (telas/visao-geral.md): perfil_demografia da última leitura, país do código ISO
// em PT-BR. Barra = % do total do público com país; a 1.ª em chart-1. "Quem segue | Quem os vídeos alcançam" troca a
// lista e a base. É DADO, não definição de público (decisão de 21/10).

const pct = (v: number, t: number) => `${((v / t) * 100).toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 })}%`;

function Lista({ dem, publico, nome }: { dem: Demografia[]; publico: string; nome: string }) {
  const linhas = dem.filter((d) => d.publico === publico && d.dimensao === "country").sort((a, b) => b.valor - a.valor);
  const total = linhas.reduce((s, d) => s + d.valor, 0);
  if (total === 0) {
    return <Vazio icone="users" titulo="Sem dados de país">A Meta só mostra o país a partir de 100 contas.</Vazio>;
  }
  const top = linhas.slice(0, 10);
  return (
    <div className="kx-pilha-curta">
      <BarrasFinas
        rotulo={`${nome}: top 10 países`}
        itens={top.map((d) => ({ rotulo: pais(d.chave), valor: d.valor, texto: pct(d.valor, total), dica: `${num(d.valor)} contas · ${pct(d.valor, total)}` }))}
      />
      <TabelaGemea
        rotulo={`${nome}: contas por país`}
        colunas={["País", "Contas", "Parte"]}
        linhas={top.map((d) => [pais(d.chave), num(d.valor), pct(d.valor, total)])}
      />
    </div>
  );
}

const totalDe = (dem: Demografia[], publico: string) =>
  dem.filter((d) => d.publico === publico && d.dimensao === "country").reduce((s, d) => s + d.valor, 0);

export default async function PublicoPaises() {
  let dem: Demografia[] = [];
  try {
    const s = (await snapshots()).at(-1);
    if (s) dem = await demografia(s.lido_em);
  } catch {
    return <div className="k-span-6 k-xl-3"><ErroBloco oque="O público por país" /></div>;
  }
  return (
    <Card como="section" pad className="k-span-6 k-xl-3" aria-labelledby="t-pub">
      <Alternador
        cabeca={{
          titulo: "Público · Top 10 países",
          id: "t-pub",
          porValor: {
            segue: <span className="k-mono k-muted">{num(totalDe(dem, "seguidores"))} contas</span>,
            alcance: <span className="k-mono k-muted">{num(totalDe(dem, "alcancados"))} contas</span>,
          },
        }}
        estilo="seg"
        rotulo="Qual público"
        opcoes={[{ valor: "segue", rotulo: "Quem segue" }, { valor: "alcance", rotulo: "Quem os vídeos alcançam" }]}
        paineis={{
          segue: <Lista dem={dem} publico="seguidores" nome="Quem segue" />,
          alcance: <Lista dem={dem} publico="alcancados" nome="Quem os vídeos alcançam" />,
        }}
      />
    </Card>
  );
}
