import { EscolhaBotoes } from "@/components/Escolha";
import * as acervo from "@/lib/acervo";

// Biblioteca · as abas (filtros com a contagem do banco). "Looks de cor" conta só os looks (não as duas referências);
// "Sistema" conta as ferramentas. Uma contagem que não veio do banco some (a aba continua).

const contar = async (f: () => Promise<unknown[]>) => { try { return (await f()).length; } catch { return undefined; } };

export const ABAS = ["todos", "looks", "capas", "legendas", "fontes", "anim", "sistema"];

export default async function Abas() {
  const [looks, capas, legendas, fontes, anim, sistema] = await Promise.all([
    contar(async () => (await acervo.looks()).filter((l) => l.tipo === "look")),
    contar(acervo.capaEstilos), contar(acervo.legendaEstilos),
    contar(async () => (await acervo.fontes()).filter((f) => !f.reserva)),
    contar(acervo.animacoes), contar(acervo.ferramentas),
  ]);
  return (
    <EscolhaBotoes
      grupo="bib"
      estilo="filtros"
      rotulo="Mostrar"
      controla="acervo"
      opcoes={[
        { valor: "todos", rotulo: "Tudo" },
        { valor: "looks", rotulo: "Looks de cor", n: looks },
        { valor: "capas", rotulo: "Capas", n: capas },
        { valor: "legendas", rotulo: "Legendas", n: legendas },
        { valor: "fontes", rotulo: "Fontes", n: fontes },
        { valor: "anim", rotulo: "Animações", n: anim },
        { valor: "sistema", rotulo: "Sistema", n: sistema },
      ]}
    />
  );
}
