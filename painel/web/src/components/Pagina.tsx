import type { ReactNode } from "react";
import Icone, { type NomeIcone } from "./Icone";

// Topo de página e seção (design-system.md §4, §15.2 "Topo de página com subtítulo"; handoff v2 §4).
// v2: o h1 segue as telas do Carlos — minúsculas com ponto final, na cor do texto, NUNCA laranja ("o estúdio hoje.").
// Subtítulo em .k-page-lead; à direita, a meta (.k-page-meta: data, período, fonte) e as ações.

export function CabecalhoPagina({ titulo, descricao, ferramentas, sobretitulo }: {
  titulo: ReactNode;
  /** uma ou duas frases sob o título (15px ink-2) */
  descricao?: ReactNode;
  ferramentas?: ReactNode;
  /** rótulo pequeno acima do título (ex.: o departamento na ficha de uma pessoa) */
  sobretitulo?: ReactNode;
}) {
  return (
    <header className="k-page-head">
      <div className="kx-page-head-texto">
        {sobretitulo && <p className="k-cap kx-sobretitulo">{sobretitulo}</p>}
        <h1 className="k-h1">{titulo}</h1>
        {descricao && <p className="k-page-lead">{descricao}</p>}
      </div>
      {ferramentas && <div className="k-page-tools">{ferramentas}</div>}
    </header>
  );
}

/**
 * Alto da página das 7 telas (handoff v3 §00, decisão de 24/10: sem título visível — o item do menu já diz onde se
 * está): o `h1` só para o leitor de tela e, se houver busca, data ou período, a `.k-page-barra`. Sem barra, o conteúdo
 * começa nos 24px da área.
 */
export function BarraPagina({ titulo, children }: { titulo: string; children?: ReactNode }) {
  return (
    <>
      <h1 className="k-sr-only">{titulo}</h1>
      {children && <div className="k-page-barra">{children}</div>}
    </>
  );
}

/** Meta do topo da página: ícone + texto em ink-3 (data de hoje, período, fonte). */
export function MetaPagina({ icone, children }: { icone?: NomeIcone; children: ReactNode }) {
  return (
    <span className="k-page-meta">
      {icone && <Icone nome={icone} tamanho={16} />}
      {children}
    </span>
  );
}

/**
 * Seção da página. `estilo` "h3" é o das telas de painel (título de 22px com a frase curta ao lado, `sub`); "h2" (30px)
 * é o das páginas de ficha. `descricao` é um parágrafo inteiro embaixo do título.
 */
export function Secao({ titulo, sub, descricao, acao, id, estilo = "h2", rotulo, className, children }: {
  titulo?: ReactNode;
  /** frase curta ao lado do título (.k-section-sub): "5 agendadas · horário de Londres" */
  sub?: ReactNode;
  descricao?: ReactNode;
  acao?: ReactNode;
  id?: string;
  estilo?: "h2" | "h3";
  /** seção sem título visível (ex.: os KPIs): nome para o leitor de tela */
  rotulo?: string;
  /** só layout (ex.: a 1.ª seção dentro de uma coluna, sem a margem de cima) */
  className?: string;
  children: ReactNode;
}) {
  return (
    <section className={["k-section", className].filter(Boolean).join(" ")} id={id} aria-label={!titulo ? rotulo : undefined}>
      {titulo && (
        <div className="k-section-head">
          {sub ? (
            <div className="k-row">
              <h2 className={estilo === "h3" ? "k-h3" : "k-h2"}>{titulo}</h2>
              <span className="k-section-sub">{sub}</span>
            </div>
          ) : (
            <div className="kx-section-texto">
              <h2 className={estilo === "h3" ? "k-h3" : "k-h2"}>{titulo}</h2>
              {descricao && <p className="kx-section-sub">{descricao}</p>}
            </div>
          )}
          {acao}
        </div>
      )}
      {children}
    </section>
  );
}
