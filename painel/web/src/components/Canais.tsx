import Icone from "./Icone";

// Canal (design-system.md §15.2, `.k-canal`): Instagram · Facebook · LinkedIn, SEMPRE os três (decisão de 23/10).
// Vai sair/saiu = contorno cheio; publicado com link = abre o post em nova aba (ícone link-externo); não vai/não saiu =
// tracejado ink-3. O estado também vai por texto para o leitor de tela.

const CANAIS = [
  { id: "instagram", nome: "Instagram" },
  { id: "facebook", nome: "Facebook" },
  { id: "linkedin", nome: "LinkedIn" },
] as const;

export default function Canais({ ativos, links, publicado }: {
  /** canais em que sai/saiu (post.json → plataformas) */
  ativos: string[];
  /** permalink de cada canal, quando publicado */
  links?: Partial<Record<"instagram" | "facebook" | "linkedin", string | null>>;
  /** fala "saiu/não saiu" em vez de "vai sair/não vai sair" */
  publicado?: boolean;
}) {
  const sim = new Set(ativos.map((c) => c.toLowerCase()));
  return (
    <div className="k-canais">
      {CANAIS.map((c) => {
        const link = links?.[c.id];
        if (link) {
          return (
            <a key={c.id} className="k-canal" href={link} target="_blank" rel="noopener noreferrer">
              {c.nome}
              <Icone nome="link-externo" tamanho={12} />
              <span className="k-sr-only"> — abrir o post (abre em outra aba)</span>
            </a>
          );
        }
        const vai = sim.has(c.id);
        return (
          <span key={c.id} className={`k-canal${vai ? "" : " is-off"}`}>
            {c.nome}
            <span className="k-sr-only">{vai ? (publicado ? " — saiu" : " — vai sair") : publicado ? " — não saiu" : " — não vai sair"}</span>
          </span>
        );
      })}
    </div>
  );
}

/** Palavra-chave do CTA (mono em surface-sunken); sem palavra, "—". */
/** Palavra-chave do CTA. `ctaSeguir`: o roteiro não tem palavra de propósito (CTA de seguir) — escrito, não "—". */
export function Palavra({ palavra, ctaSeguir }: { palavra: string | null | undefined; ctaSeguir?: boolean }) {
  if (palavra) return <span className="k-palavra">{palavra}</span>;
  if (ctaSeguir) return <span className="k-sub">sem palavra (CTA seguir)</span>;
  return <span className="k-muted" aria-label="sem palavra-chave">—</span>;
}
