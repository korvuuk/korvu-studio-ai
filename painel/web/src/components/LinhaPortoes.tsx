import type { StatusPortao } from "@/lib/db";
import { ChipPortao } from "./Chip";
import Icone from "./Icone";

// Linha "Portões:" (design-system.md §11.12, `.k-event-portao`): o chip do mapa único com o PIOR estado do que segura o
// post ou o vídeo e, quando algo segura, "‹portão› · não sai" com o "não sai" em danger (nunca só a cor: está escrito).
// Legado sem selo vence ("Legado · sem selo") e nunca é "não sai". O rótulo "Portões:" é visível (Semana), vira cadeado
// (Mês, sem espaço) ou fica só para o leitor de tela (tabela, onde a coluna já se chama Portões). Na tabela, a dica do
// chip traz as mensagens do publicar.py (fila.erros_gauntlet); dentro do evento do calendário, que já é link, não.

/** "não sai" em danger (§11.12): o que segura o post, sempre escrito. */
export function NaoSai() {
  return <span className="k-segura">não sai</span>;
}

export default function LinhaPortoes({ status, legado, segura, motivos, rotulo = "visivel", naoSai = true }: {
  status: StatusPortao;
  legado?: boolean;
  /** o portão que segura ("imagem e mais 1"); sem ele, não há "não sai" */
  segura?: string;
  /** as mensagens do publicar.py, para a dica (só na tabela) */
  motivos?: string[];
  rotulo?: "visivel" | "icone" | "leitor";
  /** Prontos: o pior portão do vídeo com o nome, sem "não sai" (o pacote ainda não está na fila) */
  naoSai?: boolean;
}) {
  const naTabela = rotulo === "leitor";
  return (
    <div className={`k-event-portao${rotulo === "icone" ? " is-compacto" : ""}`}>
      {rotulo === "icone" ? <><Icone nome="lock" tamanho={12} /><span className="k-sr-only">Portões:</span></>
        : naTabela ? <span className="k-sr-only">Portões:</span> : <span>Portões:</span>}
      <ChipPortao
        status={status}
        legado={legado}
        pequeno
        dica={naTabela && motivos && motivos.length > 0 ? { titulo: "O que o publicar.py confere", detalhe: motivos.join(" · ") } : undefined}
      />
      {segura && !legado && (naoSai
        ? <><span className={naTabela ? "k-sub kx-inline" : undefined}>{segura} ·</span><NaoSai /></>
        : <span className={naTabela ? "k-sub kx-inline" : undefined}>{segura}</span>)}
    </div>
  );
}
