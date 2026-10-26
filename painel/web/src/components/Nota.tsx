import Link from "next/link";
import type { ReactNode } from "react";
import Icone, { type NomeIcone } from "./Icone";

// Notificação (design-system.md §11.13): ícone 32px num quadrado raio 8 — alerta (danger), portão (accent), sucesso
// (positive) ou neutra — + título 13px/600 + corpo 13px ink-2. Não lida = ponto laranja + "não lida" para o leitor de
// tela. Também é o erro de bloco (§12.2): tom "alerta" + ação "Tentar de novo".

export type TomNota = "alerta" | "portao" | "ok" | "neutro";
const CLASSE: Record<TomNota, string> = { alerta: "k-note--alert", portao: "k-note--gate", ok: "k-note--ok", neutro: "" };
const ICONE: Record<TomNota, NomeIcone> = { alerta: "alert", portao: "lock", ok: "check", neutro: "info" };

export default function Nota({ tom = "neutro", icone, titulo, children, acoes, naoLida, papel, href }: {
  tom?: TomNota;
  icone?: NomeIcone;
  titulo: ReactNode;
  children?: ReactNode;
  acoes?: ReactNode;
  naoLida?: boolean;
  /** "alert" quando a nota aparece por causa de um erro */
  papel?: "alert" | "status";
  /** a nota inteira vira link (ex.: na lista de avisos) */
  href?: string;
}) {
  const classe = ["k-note", CLASSE[tom]].filter(Boolean).join(" ");
  const conteudo = (
    <>
      <span className="k-note-icon" aria-hidden="true">
        <Icone nome={icone ?? ICONE[tom]} tamanho={16} />
      </span>
      <div className="kx-note-texto">
        <div className="k-note-title">{titulo}</div>
        {children && <div className="k-note-body">{children}</div>}
        {acoes && <div className="k-note-actions">{acoes}</div>}
      </div>
      {naoLida && (
        <>
          <span className="k-unread" aria-hidden="true" />
          <span className="k-sr-only">não lida</span>
        </>
      )}
    </>
  );
  if (href) return <Link href={href} className={classe}>{conteudo}</Link>;
  return <div className={classe} role={papel}>{conteudo}</div>;
}
