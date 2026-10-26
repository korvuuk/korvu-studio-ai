// Logotipo "korvu. painel" (design-system.md §9): os SVG de painel/design/marca/, copiados sem mudar para public/marca/.
// ink sobre fundo claro, ivory na barra lateral e na barra de topo. Nunca em laranja, nunca "korvu." sozinho, mínimo 16px.

const PROPORCAO = 6168 / 1030; // viewBox dos dois arquivos

export default function Logo({ tom = "ink", altura = 19, decorativo = false }: {
  tom?: "ink" | "ivory";
  altura?: number;
  /** Dentro de um link que já se chama "korvu. painel — início": o texto alternativo repetiria o nome. */
  decorativo?: boolean;
}) {
  const h = Math.max(16, altura);
  return (
    // eslint-disable-next-line @next/next/no-img-element -- SVG vetorial pequeno: o otimizador de imagens não ganha nada
    <img
      src={`/marca/korvu-painel-${tom}.svg`}
      alt={decorativo ? "" : "korvu. painel"}
      width={Math.round(h * PROPORCAO)}
      height={h}
      style={{ display: "block", height: h, width: "auto" }}
    />
  );
}
