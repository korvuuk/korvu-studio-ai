import Link from "next/link";
import Capa from "./Capa";
import { ChipModo } from "./Chip";
import { nomeDosCanais } from "./Evento";

// Cartão de publicação (design-system.md §15.2, `.k-post`): capa, dia em caption + hora (Londres, o mesmo do
// publicar.py), "amanhã/em N dias" (accent-ink quando é hoje ou amanhã), nome curto, os canais que vão sair e o modo.
// O cartão inteiro é link.

export default function CartaoPublicacao({ href, capa, nome, dia, hora, relativo, perto, canais, trial }: {
  href: string;
  capa: string | null;
  nome: string;
  /** "Sáb 24 out" */
  dia: string;
  /** "19:00" */
  hora: string;
  /** "amanhã", "em 4 dias" */
  relativo: string;
  perto?: boolean;
  canais: string[];
  trial: string | null;
}) {
  return (
    <Link className="k-card is-interactive k-post" href={href}>
      <Capa src={capa} nome={nome} tamanho="md" />
      <div className="k-post-corpo">
        <div className="k-post-quando">
          <span>
            <span className="k-cap">{dia}</span>
            <span className="k-mono k-ink2">{hora}</span>
          </span>
          <span className={`k-post-rel${perto ? " is-perto" : ""}`}>{relativo}</span>
        </div>
        <span className="k-post-titulo" title={nome}>{nome}</span>
        <span className="k-post-onde">
          {nomeDosCanais(canais)}
          <ChipModo trial={trial} />
        </span>
      </div>
    </Link>
  );
}
