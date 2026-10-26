/**
 * Dados de exemplo (sem mídia externa) para a composição `DemoLegendas`.
 * Gera legendas determinísticas a partir de um mini-roteiro.
 * `*palavra*` = destaque (vira nível "impacto" na legenda).
 */
import { VIDEO } from "../brand";
import type { LegendaCaption, Overlay, ReelProps, Segmento } from "../lib/tipos";

type LinhaDemo = { id: string; fala: string };

const LINHAS: LinhaDemo[] = [
  { id: "L01", fala: "Você tá usando o *ChatGPT* *errado.*" },
  { id: "L02", fala: "A maioria escreve uma frase e espera *mágica.*" },
  { id: "L03", fala: "O segredo é dar *contexto.*" },
  { id: "L04", fala: "O prompt entra, a IA pensa e a resposta sai." },
  { id: "L05", fala: "Prompt bom, resposta *boa.*" },
  { id: "L06", fala: "Te mostro três modelos que eu uso." },
  { id: "L07", fala: "Comenta *PROMPT* que eu te mando." },
];

type Janela = { inicio: number; fim: number };

const gerar = (): {
  legendas: LegendaCaption[];
  janelas: Record<string, Janela>;
  duracao: number;
} => {
  const legendas: LegendaCaption[] = [];
  const janelas: Record<string, Janela> = {};
  let t = 0.2;
  for (const linha of LINHAS) {
    const inicioLinha = t;
    for (const bruto of linha.fala.split(" ")) {
      const destaque = bruto.startsWith("*");
      const texto = bruto.replace(/\*/g, "");
      const dur = 0.16 + 0.034 * texto.length;
      const startMs = Math.round(t * 1000);
      const endMs = Math.round((t + dur) * 1000);
      legendas.push({
        text: ` ${texto}`,
        startMs,
        endMs,
        timestampMs: Math.round((startMs + endMs) / 2),
        confidence: 1,
        linha: linha.id,
        destaque,
      });
      t += dur + 0.05;
    }
    janelas[linha.id] = { inicio: inicioLinha, fim: t };
    t += 0.45; // pausa depois da linha
  }
  return { legendas, janelas, duracao: Math.ceil((t + 0.4) * 10) / 10 };
};

const { legendas, janelas, duracao } = gerar();
const r2 = (n: number): number => Math.round(n * 100) / 100;

const overlays: Overlay[] = [
  {
    linha: "L04",
    tipo: "animacao",
    modo: "split",
    id: "L04",
    componente: "ExemploFluxo",
    descricao: "Prompt → IA → Resposta",
    saida_inicio: r2(janelas.L04.inicio - 0.2),
    saida_fim: r2(janelas.L04.fim + 0.3),
  },
  {
    linha: "L05",
    tipo: "texto",
    modo: "cartela",
    contexto: "Regra de ouro:",
    selecao: "ouro",
    texto: "Prompt bom, resposta boa.",
    cinza: 2,
    rabisco: "boa",
    saida_inicio: r2(janelas.L05.inicio - 0.1),
    saida_fim: r2(janelas.L05.fim + 0.35),
  },
  {
    linha: "L06",
    tipo: "animacao",
    modo: "full",
    id: "L06",
    descricao: "Três cards lado a lado com os modelos: Papel, Tarefa e Formato.",
    saida_inicio: r2(janelas.L06.inicio - 0.1),
    saida_fim: r2(janelas.L06.fim + 0.3),
  },
];

const segmentos: Segmento[] = LINHAS.map((l, i) => ({
  saidaInicio: i === 0 ? 0 : r2(janelas[l.id].inicio - 0.2),
  saidaFim: r2(i === LINHAS.length - 1 ? duracao : janelas[LINHAS[i + 1].id].inicio - 0.2),
  zoom: i % 2 === 1 ? { tipo: "punch", escala: 1.12 } : null,
  layout: l.id === "L04" ? "split" : "full",
}));

export const DEMO_PROPS: ReelProps = {
  video: null,
  duracaoSeg: duracao,
  fps: VIDEO.fps,
  legendas,
  overlays,
  segmentos,
  titulo: {
    contexto: "Se você usa o ChatGPT assim,",
    impacto: "tá jogando tempo fora.",
    cinza: 3,
    rabisco: "fora",
    selecao: "ChatGPT assim",
    fim: r2(janelas.L01.fim + 0.3),
    posicao: "baixo",
  },
  estiloLegenda: "selecao",
  legendaPosicao: "baixo",
  arquivoProps: null,
};
