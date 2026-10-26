import ErroBloco from "@/components/ErroBloco";
import { Delta, KpiLinha } from "@/components/Kpi";
import Vazio from "@/components/Vazio";
import type { Snapshot } from "@/lib/db";
import { compactoPartes, data, num } from "@/lib/formato";
import { snapshots } from "@/lib/leituras";
import { diferencaAbsoluta, variacao } from "@/lib/perfil";

// Desempenho · os quatro números (telas/desempenho.md): a última leitura do perfil contra a anterior, com o delta (a cor
// segue o significado: cair é ruim) e o valor de antes. "Toques no link" da maquete não está no banco — fica de fora.

type Campo = "seguidores" | "views" | "alcance" | "visitas_perfil";
const NUMEROS: { campo: Campo; rotulo: string }[] = [
  { campo: "seguidores", rotulo: "Seguidores" },
  { campo: "views", rotulo: "Visualizações" },
  { campo: "alcance", rotulo: "Contas alcançadas" },
  { campo: "visitas_perfil", rotulo: "Visitas ao perfil" },
];

export default async function Numeros() {
  let snaps: Snapshot[];
  try {
    snaps = await snapshots();
  } catch {
    return <ErroBloco oque="Os números do perfil" />;
  }
  const atual = snaps.at(-1);
  if (!atual) {
    return (
      <Vazio icone="eye" titulo="Ainda não há leitura do perfil">
        Quando o scripts/perfil.py ler a conta, seguidores, visualizações, alcance e visitas aparecem aqui, comparados com a leitura anterior.
      </Vazio>
    );
  }
  const ant = snaps.length > 1 ? snaps.at(-2) : undefined;
  const quando = ant ? data(ant.lido_em) : "";
  return (
    <div className="k-grid k-grid--tiles">
      {NUMEROS.map(({ campo, rotulo }) => {
        const v = atual[campo];
        const a = ant?.[campo];
        const d = variacao(v, a, quando);
        const partes = v != null ? compactoPartes(v) : null;
        const nota = v != null && a != null
          ? campo === "seguidores" ? diferencaAbsoluta(v, a, ant!.lido_em) : `eram ${num(a)}`
          : ant ? `sem o número de ${quando}` : "1.ª leitura do perfil";
        return (
          <KpiLinha
            key={campo}
            className="k-span-3"
            rotulo={rotulo}
            valor={partes?.valor ?? "—"}
            unidade={partes?.unidade || undefined}
            delta={d ? <Delta sentido={d.sentido} significado={d.significado} texto={d.texto} leitor={d.leitor} semSeta={d.quaseIgual} /> : undefined}
            nota={nota}
          />
        );
      })}
    </div>
  );
}
