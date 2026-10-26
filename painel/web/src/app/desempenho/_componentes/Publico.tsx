import { Card, CabecalhoGrafico, CardCabecalho } from "@/components/Card";
import ErroBloco from "@/components/ErroBloco";
import { BarrasFinas, TabelaGemea } from "@/components/Graficos";
import Vazio from "@/components/Vazio";
import type { Demografia } from "@/lib/db";
import { num, pais, pct1 } from "@/lib/formato";
import { demografia, snapshots } from "@/lib/leituras";

// Desempenho · de onde vem o público. (telas/desempenho.md): duas listas de barras finas (top 10 países de quem segue e
// de quem os vídeos alcançam), valor em contas; a 1.ª de cada lista em chart-1. A frase do pé diz só o que os dados
// dizem (posição e parte do 1.º país de quem segue nas duas listas) — nunca define público por país (decisão de 21/10).

type Linha = { chave: string; valor: number };
const ordenar = (dem: Demografia[], publico: string): Linha[] =>
  dem.filter((d) => d.publico === publico && d.dimensao === "country").sort((a, b) => b.valor - a.valor);
const soma = (ls: Linha[]) => ls.reduce((s, d) => s + d.valor, 0);

function Lista({ titulo, linhas }: { titulo: string; linhas: Linha[] }) {
  const total = soma(linhas);
  return (
    <div>
      <CardCabecalho titulo={titulo} pequeno linha acao={<span className="k-mono k-muted">{num(total)} com país</span>} />
      {total === 0 ? (
        <Vazio icone="users" titulo="Sem dados de país">A Meta só mostra países a partir de 100 contas.</Vazio>
      ) : (
        <BarrasFinas
          rotulo={`${titulo}: top 10 países, em contas`}
          itens={linhas.slice(0, 10).map((d) => ({ rotulo: pais(d.chave), valor: d.valor, texto: num(d.valor), dica: `${num(d.valor)} contas · ${pct1((d.valor / total) * 100)}` }))}
        />
      )}
    </div>
  );
}

/** "o 1.º país de quem segue (Guiné-Bissau, 54,4%) é o 4.º de quem foi alcançado (5,8%)" — só posição e parte. */
function frase(seg: Linha[], alc: Linha[]): string | null {
  const tSeg = soma(seg);
  const tAlc = soma(alc);
  if (!tSeg || !tAlc) return null;
  const primeiro = seg[0];
  const nome = pais(primeiro.chave);
  const inicio = `o 1.º país de quem segue (${nome}, ${pct1((primeiro.valor / tSeg) * 100)})`;
  const i = alc.findIndex((d) => d.chave === primeiro.chave);
  if (i < 0) return `Quem segue e quem os vídeos alcançam vêm de lugares diferentes: ${inicio} não aparece entre os países de quem foi alcançado.`;
  const parte = pct1((alc[i].valor / tAlc) * 100);
  if (i === 0) return `${inicio.charAt(0).toUpperCase()}${inicio.slice(1)} também é o 1.º de quem foi alcançado (${parte}).`;
  return `Quem segue e quem os vídeos alcançam vêm de lugares diferentes: ${inicio} é o ${i + 1}.º de quem foi alcançado (${parte}).`;
}

export default async function Publico() {
  let dem: Demografia[] = [];
  try {
    const s = (await snapshots()).at(-1);
    if (s) dem = await demografia(s.lido_em);
  } catch {
    return <div className="k-span-12 k-xl-5"><ErroBloco oque="O público por país" /></div>;
  }
  const seg = ordenar(dem, "seguidores");
  const alc = ordenar(dem, "alcancados");
  const texto = frase(seg, alc);
  const tSeg = soma(seg);
  const tAlc = soma(alc);
  // a tabela gêmea: os países das duas listas, com as contas e a parte em cada público
  const chaves = [...new Set([...seg.slice(0, 10), ...alc.slice(0, 10)].map((d) => d.chave))];
  const valor = (ls: Linha[], c: string) => ls.find((d) => d.chave === c)?.valor ?? 0;
  return (
    <Card como="section" className="kx-card-grafico k-span-12 k-xl-5" aria-labelledby="t-pais">
      <CabecalhoGrafico id="t-pais" titulo="de onde vem o público." />
      {tSeg === 0 && tAlc === 0 ? (
        <div className="kx-corpo-grafico">
          <Vazio icone="users" titulo="Sem dados de país">A Meta só mostra países a partir de 100 contas; quando houver, as duas listas aparecem aqui.</Vazio>
        </div>
      ) : (
        <div className="kx-paises">
          <Lista titulo="Quem segue" linhas={seg} />
          <Lista titulo="Quem os vídeos alcançam" linhas={alc} />
        </div>
      )}
      {texto && <p className="k-fonte kx-fonte-pe">{texto}</p>}
      {chaves.length > 0 && (
        <TabelaGemea
          rotulo="Público por país em números"
          colunas={["País", "Quem segue", "Parte", "Quem os vídeos alcançam", "Parte"]}
          linhas={chaves.map((c) => [
            pais(c),
            num(valor(seg, c)), tSeg ? pct1((valor(seg, c) / tSeg) * 100) : "—",
            num(valor(alc, c)), tAlc ? pct1((valor(alc, c) / tAlc) * 100) : "—",
          ])}
        />
      )}
    </Card>
  );
}
