import { dataHora } from "@/lib/formato";
import { snapshots } from "@/lib/leituras";
import { periodo } from "@/lib/perfil";

// O período escrito no topo (telas/desempenho.md, "Do artboard para a maquete"): a Meta só dá a janela de 28 dias, então
// não há seletor — só "Últimos 28 dias · 25 set – 22 out · leitura de 22 out, 14:00".

export default async function Periodo() {
  let s;
  try {
    s = (await snapshots()).at(-1);
  } catch {
    return <>Últimos 28 dias</>;
  }
  if (!s) return <>Últimos 28 dias · ainda sem leitura do perfil</>;
  return <>Últimos {s.janela_dias ?? 28} dias · {periodo(s)} · leitura de {dataHora(s.lido_em)}</>;
}
