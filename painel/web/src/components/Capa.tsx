import Image from "next/image";
import Icone from "./Icone";

// Capa 9:16 (design-system.md §15.2): a capa real (`capa/capa.png`, servida por app/capa/… e reduzida pelo otimizador de
// imagens); sem capa, o quadro surface-sunken com `play`; roteiro (ainda sem vídeo) = ícone `documento`.
// Tamanhos: xs 18×32 · sm 24×42 · padrão 27×48 · md 36×64 · lg 58×103 · doc 32×40.

export type TamanhoCapa = "xs" | "sm" | "padrao" | "md" | "lg" | "doc";
const LARGURA: Record<TamanhoCapa, number> = { xs: 18, sm: 24, padrao: 27, md: 36, lg: 58, doc: 32 };

export default function Capa({ src, nome, tamanho = "padrao" }: {
  /** endereço de lib/capas.ts → capa(); null = sem capa */
  src?: string | null;
  /** para o texto alternativo: "Capa de Fei-Fei Li r2" */
  nome: string;
  tamanho?: TamanhoCapa;
}) {
  const classe = `k-capa${tamanho === "padrao" ? "" : ` k-capa--${tamanho}`}`;
  if (tamanho === "doc") {
    return <span className={classe} aria-hidden="true"><Icone nome="documento" tamanho={18} /></span>;
  }
  return (
    <span className={classe}>
      {src ? (
        // largura × 2 para tela de alta densidade; a imagem cobre o quadro (object-fit: cover no acrescimos.css)
        <Image src={src} alt={`Capa de ${nome}`} width={LARGURA[tamanho] * 2} height={Math.round(LARGURA[tamanho] * 2 * 16 / 9)} />
      ) : (
        <Icone nome="play" tamanho={tamanho === "xs" || tamanho === "sm" ? 12 : 14} rotulo={`${nome}: sem capa`} />
      )}
    </span>
  );
}
