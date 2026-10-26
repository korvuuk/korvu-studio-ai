/**
 * Registry de animações por id.
 *
 * O overlay `{"tipo": "animacao", "id": "L08", "componente"?: "..."}` procura
 * primeiro `componente`, depois `id`. Se nada for encontrado, o Reel mostra
 * uma Cartela provisória com a `descricao`.
 *
 * Para criar uma animação nova: faça um componente `React.FC<AnimacaoProps>`
 * nesta pasta e registre-o abaixo (chave = id da linha ou nome do componente).
 */
import type React from "react";
import type { PalavraAnimacao } from "../lib/tipos";
import { ExemploFluxo } from "./ExemploFluxo";

export type AnimacaoProps = {
  /** Palavras faladas durante o overlay (tempos relativos ao início dele). */
  palavras: PalavraAnimacao[];
  /** Tamanho da área disponível (px). */
  largura: number;
  altura: number;
  modo: "full" | "split" | "card";
  descricao?: string | null;
  /** Duração do overlay em frames. */
  duracaoFrames: number;
} & Record<string, unknown>;

export const ANIMACOES: Record<string, React.FC<AnimacaoProps>> = {
  ExemploFluxo,
  // Teste sintético (tests/make_synthetic.py): cena extra E02 (animacao) do vídeo _teste-sintetico.
  "_teste-sintetico/E02": ExemploFluxo,
};

export const acharAnimacao = (
  ...chaves: Array<string | null | undefined>
): React.FC<AnimacaoProps> | null => {
  for (const k of chaves) {
    if (k && Object.prototype.hasOwnProperty.call(ANIMACOES, k)) {
      return ANIMACOES[k];
    }
  }
  return null;
};
