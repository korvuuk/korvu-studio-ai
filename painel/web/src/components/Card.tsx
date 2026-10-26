import Link from "next/link";
import type { ComponentProps, ElementType, ReactNode } from "react";

// Card (design-system.md §11.4): surface + borda 1px line + raio 12 + sombra quase invisível. Clicável = o card INTEIRO
// é um link (CardLink), hover troca a borda e a sombra (sem escala, sem mudar o fundo). Nunca card dentro de card,
// nunca borda colorida à esquerda.

export function Card({ como: Tag = "div", pad, recorte, className, children, ...resto }: {
  como?: ElementType;
  /** padding padrão do sistema (24px) */
  pad?: boolean;
  /** corta o conteúdo no raio (tabelas que rolam dentro do card) */
  recorte?: boolean;
  className?: string;
  children: ReactNode;
} & Omit<ComponentProps<"div">, "className" | "children">) {
  const classes = ["k-card", pad && "k-pad", recorte && "kx-recorte", className].filter(Boolean).join(" ");
  return <Tag className={classes} {...resto}>{children}</Tag>;
}

export function CardLink({ className, children, ...resto }: Omit<ComponentProps<typeof Link>, "className"> & { className?: string }) {
  return <Link className={["k-card is-interactive", className].filter(Boolean).join(" ")} {...resto}>{children}</Link>;
}

/**
 * Cabeçalho do card: título (15px/600) à esquerda; ação, caption ou contexto à direita.
 * - padrão: a nota embaixo do título, 16px até o conteúdo;
 * - `linha`: título e ação numa linha centrada, sem margem (o conteúdo dá o espaço) — Fila, Portões, Precisam de atenção;
 * - `notaAoLado`: a nota na mesma linha do título ("Roteiros · 7  na ordem de gravação prevista");
 * - `pequeno`: o título de uma lista dentro do card (13px/600, "Quem segue").
 */
export function CardCabecalho({ titulo, como: Tag = "h3", id, nota, notaAoLado, linha, pequeno, acao, className }: {
  titulo: ReactNode; como?: ElementType; id?: string; nota?: ReactNode; notaAoLado?: boolean; linha?: boolean;
  pequeno?: boolean; acao?: ReactNode; className?: string;
}) {
  const tituloEl = <Tag className={pequeno ? "k-body-strong kx-titulo-lista" : "k-card-title"} id={id}>{titulo}</Tag>;
  return (
    <div className={["k-card-head", !linha && "kx-card-head", className].filter(Boolean).join(" ")}>
      {notaAoLado ? (
        <div className="k-row kx-row-10">{tituloEl}{nota && <span className="k-kpi-note">{nota}</span>}</div>
      ) : linha && !nota ? tituloEl : (
        <div className="kx-card-head-texto">
          {tituloEl}
          {nota && <p className="k-kpi-note kx-sem-margem">{nota}</p>}
        </div>
      )}
      {acao}
    </div>
  );
}

/**
 * Cabeçalho de um card de gráfico das telas de 23/10 (Desempenho, Tokens e custos): título de seção em minúsculas com
 * ponto ("crescimento.", h2 em .k-h3), a frase curta ao lado e, à direita, a legenda ou o contexto.
 */
export function CabecalhoGrafico({ titulo, id, nota, junto, acao }: {
  titulo: ReactNode; id: string; nota?: ReactNode;
  /** no lugar da nota, quando ela troca com uma escolha (já vem com a classe .k-kpi-note) */
  junto?: ReactNode;
  acao?: ReactNode;
}) {
  return (
    <div className="k-card-head kx-cab-grafico">
      <div className="k-row kx-cab-grafico-texto">
        <h2 className="k-h3" id={id}>{titulo}</h2>
        {nota && <span className="k-kpi-note">{nota}</span>}
        {junto}
      </div>
      {acao}
    </div>
  );
}
