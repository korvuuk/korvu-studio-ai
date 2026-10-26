import { Etiqueta, LegendaArmazem } from "@/components/Acervo";
import { Card, CardCabecalho } from "@/components/Card";
import ErroBloco from "@/components/ErroBloco";
import { BarraEmpilhada, TabelaGemea } from "@/components/Graficos";
import { ListaKv } from "@/components/ListaKv";
import Vazio from "@/components/Vazio";
import * as acervo from "@/lib/acervo";
import { num } from "@/lib/formato";

// Biblioteca · lateral (telas/biblioteca.md): Armazenamento (só o Mac — decisão de 25/10: o painel não mostra o HD
// externo —, view armazenamento; GB decimais como o Finder) e Sistema (os modelos dos 30 dias, as ferramentas e as contagens de .claude/). Os dois aparecem em todas as
// abas.

const gb = (b: number, casas = 1) => (b / 1e9).toLocaleString("pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas });

export async function Armazenamento() {
  let a;
  try { a = await acervo.armazenamento(); } catch { return <ErroBloco oque="O armazenamento" />; }
  const cab = <CardCabecalho como="h2" id="t-arm" titulo="Armazenamento" linha />;
  if (!a || a.mac_bytes === 0) {
    return <Card como="section" pad className="k-armazem" aria-labelledby="t-arm">{cab}<div className="kx-corpo-grafico"><Vazio icone="inbox" titulo="Sem leitura do disco">Quando o sincronizador ler as pastas dos vídeos, o espaço no Mac aparece aqui.</Vazio></div></Card>;
  }
  const partes = [
    { nome: "Gravações da câmera", bytes: a.gravacoes_mac_bytes, serie: 1 as const },
    { nome: "Material e cenas extras", bytes: a.material_mac_bytes, serie: 2 as const },
  ];
  const total = partes.reduce((s, x) => s + x.bytes, 0);
  const pct = (b: number) => `${((b / total) * 100).toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 })}%`;
  return (
    <Card como="section" pad className="k-armazem" aria-labelledby="t-arm">
      {cab}
      <div className="k-armazem-n"><b>{gb(a.mac_bytes)}</b><span>GB no Mac</span></div>
      <BarraEmpilhada rotulo={partes.map((x) => `${x.nome} ${gb(x.bytes)} GB`).join(", ")} partes={partes.map((x) => ({ valor: x.bytes, serie: x.serie }))} />
      <LegendaArmazem itens={partes.map((x) => ({ nome: x.nome, valor: `${gb(x.bytes)}\u00a0GB`, serie: x.serie }))} />
      <TabelaGemea
        rotulo="Armazenamento"
        colunas={["Onde", "GB", "% do total"]}
        linhas={partes.map((x) => [x.nome, gb(x.bytes, 2), pct(x.bytes)])}
      />
    </Card>
  );
}

export async function SistemaLado() {
  let modelos, fs, c;
  try { [modelos, fs, c] = await Promise.all([acervo.sistemaModelos(), acervo.ferramentas(), acervo.sistemaContagens()]); } catch { return <ErroBloco oque="O sistema" />; }
  const ordem = [...modelos].sort((a, b) => (b.pct_tokens ?? 0) - (a.pct_tokens ?? 0));
  const pct = (v: number | null) => `${(v ?? 0).toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 })} %`;
  return (
    <Card como="section" pad className="k-sistema kx-coluna" aria-labelledby="t-sis">
      <CardCabecalho como="h2" id="t-sis" titulo="Sistema" linha acao={<span className="k-kpi-note">o que faz o estúdio rodar</span>} />
      <span className="k-sistema-sub">Modelos de IA · tokens dos últimos 30 dias</span>
      {ordem.length === 0 ? <Vazio icone="cpu" titulo="Sem consumo para mostrar">Quando o Claude Code rodar, a parte de cada modelo aparece aqui.</Vazio> : (
        <ListaKv itens={ordem.map((m, i) => ({ id: m.modelo, chave: m.modelo_nome ?? m.modelo, valor: <span className={i === 0 ? "kx-meta-lider" : "k-estilo-meta kx-meta-ink"}>{pct(m.pct_tokens)}</span> }))} />
      )}
      {fs.length > 0 && (
        <>
          <span className="k-sistema-sub">Ferramentas · a aba Sistema explica cada uma</span>
          <ListaKv itens={fs.map((f) => ({ id: f.nome, chave: f.nome, valor: <Etiqueta tom="tipo">{f.tipo}</Etiqueta> }))} />
        </>
      )}
      {c && <p className="k-fonte kx-fonte-bloco">{num(c.agentes)} agentes (mais o Atlas) · {num(c.habilidades)} habilidades · {num(c.comandos)} comandos</p>}
    </Card>
  );
}
