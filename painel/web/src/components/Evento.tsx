import type { StatusPortao } from "@/lib/db";
import { ChipPortao } from "./Chip";

// Evento do calendário (design-system.md §11.12): raio 6, surface, borda line; canal pela barra de 3px (Instagram =
// accent, Facebook = chart-5, mais de um = ink) E pelo nome escrito na 2.ª linha. Título e hora · canal em uma linha
// cada, com reticências. Linha "Portões:" em TODOS os posts da fila, respondendo se o post sai (o pior estado do que o
// publicar.py confere; legado vence); se algo segura, "<portão> · não sai" em danger.

const CANAL: Record<string, string> = { instagram: "Instagram", facebook: "Facebook", linkedin: "LinkedIn" };
export const nomeDosCanais = (canais: string[]) => canais.map((c) => CANAL[c.toLowerCase()] ?? c).join(" + ");

function classeDoCanal(canais: string[]) {
  const c = canais.map((x) => x.toLowerCase());
  if (c.length === 1 && c[0] === "instagram") return " k-event--ig";
  if (c.length === 1 && c[0] === "facebook") return " k-event--fb";
  return "";
}

export default function Evento({ titulo, hora, canais, extra, portoes }: {
  titulo: string;
  hora: string;
  canais: string[];
  /** variante, trial… (ex.: "r2", "l01c") */
  extra?: string;
  /** o que o publicar.py confere; `segura` = o portão que segura o post ("imagem", "imagem e mais 1") */
  portoes?: { status: StatusPortao; legado?: boolean; segura?: string };
}) {
  return (
    <div className={`k-event${classeDoCanal(canais)}`}>
      <b title={titulo}>{titulo}</b>
      <span>{[hora, nomeDosCanais(canais), extra].filter(Boolean).join(" · ")}</span>
      {portoes && (
        <div className="k-event-portao">
          <span>Portões:</span>
          <ChipPortao status={portoes.status} legado={portoes.legado} como="small" />
          {portoes.segura && !portoes.legado && (
            <>
              <span>{portoes.segura} ·</span>
              <span className="k-segura">não sai</span>
            </>
          )}
        </div>
      )}
    </div>
  );
}

/** Portão marcado num dia do calendário (fundo accent-soft, sem barra de canal). */
export function EventoPortao({ titulo, texto }: { titulo: string; texto: string }) {
  return (
    <div className="k-event k-event--gate">
      <b>{titulo}</b>
      <span>{texto}</span>
    </div>
  );
}
