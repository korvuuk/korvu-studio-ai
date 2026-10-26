import type { ReactNode } from "react";
import Icone from "./Icone";

// Destaque (design-system.md §15.2, `.k-destaque`): a frase que resume o bloco, em accent-soft com o sparkle; embaixo, a
// meta (de onde vem a conta). Um por bloco, no pé — nunca no lugar dos números.

export default function Destaque({ meta, children, className }: { meta?: ReactNode; children: ReactNode; className?: string }) {
  return (
    <div className={["k-destaque", className].filter(Boolean).join(" ")}>
      <Icone nome="sparkle" tamanho={18} />
      <div>
        <span className="k-destaque-t">{children}</span>
        {meta && <span className="k-destaque-m">{meta}</span>}
      </div>
    </div>
  );
}
