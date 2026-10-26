import Image from "next/image";
import type { CSSProperties } from "react";
import { iniciais } from "@/lib/formato";

// Avatar (design-system.md §11.7): quadrado 1:1. Com foto (retrato realista, decisão do Carlos de 23/10 — arquivos em
// public/equipe/<id>.jpg, lidos por lib/retratos.ts), a foto cobre o quadrado (object-fit: cover); sem foto, as
// iniciais em ink-2 sobre surface-sunken. Tamanhos do sistema: 56 raio 10 (card de equipe), 40 raio 8 (listas),
// 28–32 redondo (pilhas). Acima de 72, raio do card (12).

export default function Avatar({ nome, foto, tamanho = 40, redondo, rotulado, semRaio, className }: {
  nome: string;
  foto?: string | null;
  tamanho?: number;
  redondo?: boolean;
  /** true quando o nome não está escrito ao lado (o avatar sozinho diz quem é) */
  rotulado?: boolean;
  /** o raio vem do CSS de quem contém o avatar (ex.: .k-direcao-quem > .k-avatar, 10px) */
  semRaio?: boolean;
  className?: string;
}) {
  const estilo = { "--s": `${tamanho}px` } as CSSProperties;
  if (!redondo && !semRaio && tamanho >= 72) estilo.borderRadius = "var(--radius-card)";
  else if (!redondo && !semRaio && tamanho >= 56) estilo.borderRadius = "10px";
  return (
    <span
      className={["k-avatar", redondo && "is-round", className].filter(Boolean).join(" ")}
      style={estilo}
      role={rotulado ? "img" : undefined}
      aria-label={rotulado ? nome : undefined}
      aria-hidden={rotulado ? undefined : true}
    >
      {foto ? (
        <Image src={foto} alt="" fill sizes={`${tamanho}px`} />
      ) : (
        iniciais(nome)
      )}
    </span>
  );
}
