import { data, dataHora } from "@/lib/formato";
import { janela, sincronizacao } from "@/lib/leituras";

// O período escrito no topo (telas/tokens-e-custos.md): sem seletor (só existe a janela calculada), com a hora da
// leitura (a última sincronização) e a moeda (US$, preço de tabela da API).

export default async function Meta() {
  const j = janela(30);
  const periodo = `${data(`${j.de}T12:00:00Z`)} – ${data(`${j.ate}T12:00:00Z`)}`;
  let banco;
  try {
    banco = await sincronizacao();
  } catch {
    return <>{periodo} · registros das sessões do Claude Code</>;
  }
  return (
    <>
      {periodo} · registros das sessões do Claude Code{banco.estado === "ok" ? ` · leitura de ${dataHora(banco.em)}` : ""}
      {" · "}custo em US$, preço de tabela da API
    </>
  );
}
