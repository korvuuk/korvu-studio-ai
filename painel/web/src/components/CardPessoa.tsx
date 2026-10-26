import { CardLink } from "./Card";
import Avatar from "./Avatar";
import { primeiraMaiuscula } from "@/lib/formato";
import { Chip, ChipModelo } from "./Chip";

// Card de pessoa (TeamMemberCard, design-system.md §11.8): o card inteiro abre a ficha. Avatar 56 (foto ou iniciais),
// nome + chip do modelo (com a versão) + "Portão" para o gerente, cargo · departamento, e as métricas à direita.
// Métricas só com fonte de dados: sem `metricas`, o bloco não aparece (nunca número inventado). Tokens em accent-ink.

export type MetricaPessoa = { rotulo: string; valor: string; tokens?: boolean };

export default function CardPessoa({ href, nome, cargo, departamento, modelo, foto, portao, metricas }: {
  href: string;
  nome: string;
  cargo?: string | null;
  departamento?: string | null;
  modelo?: string | null;
  foto?: string | null;
  portao?: boolean;
  metricas?: MetricaPessoa[];
}) {
  return (
    <CardLink href={href} className="k-member">
      <Avatar nome={nome} foto={foto} tamanho={56} />
      <div className="k-member-id">
        <div className="k-member-name-row">
          <span className="k-member-name">{nome}</span>
          {modelo && <ChipModelo modelo={modelo} />}
          {portao && <Chip tom="portao" icone="lock">Portão</Chip>}
        </div>
        <div className="k-member-role">{[cargo, departamento].filter(Boolean).map(primeiraMaiuscula).join(" · ")}</div>
      </div>
      {metricas && metricas.length > 0 && (
        <div className="k-member-stats">
          {metricas.map((m) => (
            <div key={m.rotulo}>
              <div className={`k-member-stat-value${m.tokens ? " k-tokens" : ""}`}>{m.valor}</div>
              <span className="k-member-stat-label">{m.rotulo}</span>
            </div>
          ))}
        </div>
      )}
    </CardLink>
  );
}
