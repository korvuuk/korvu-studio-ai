import dados from "@/app/design/icones.json";
import telas from "@/app/design/icones-telas.json";

// Os 31 ícones do sistema (painel/design/icones/icones.json) + os 4 das telas de 23/10 (icones/telas/icones-telas.json:
// documento, seta-direita, link-externo, camera), copiados sem mudar: outline, grade 24, traço 1,5, currentColor.
// Tamanhos: 18 na barra lateral, 16 em botões e campos, 14 em chips e tabelas, 22–24 em estados vazios.
// O <span data-icon> é o que o componentes.css espera (ex.: o ícone do item ativo da barra lateral fica laranja).

const TODOS = { ...dados.icones, ...telas.icones };
export type NomeIcone = keyof typeof TODOS;

export default function Icone({
  nome, tamanho = 16, rotulo, traco = 1.5,
}: {
  nome: NomeIcone;
  tamanho?: number;
  /** Só quando o ícone está sozinho e diz algo; decorativo (o padrão) fica fora do leitor de tela. */
  rotulo?: string;
  traco?: number;
}) {
  return (
    <span data-icon={nome} aria-hidden={rotulo ? undefined : true} role={rotulo ? "img" : undefined} aria-label={rotulo}>
      <svg
        viewBox={dados.viewBox}
        width={tamanho}
        height={tamanho}
        fill="none"
        stroke="currentColor"
        strokeWidth={traco}
        strokeLinecap="round"
        strokeLinejoin="round"
        focusable="false"
        // conteúdo estático do próprio sistema (icones*.json), nunca vindo do banco nem de quem usa o painel
        dangerouslySetInnerHTML={{ __html: TODOS[nome] }}
      />
    </span>
  );
}
