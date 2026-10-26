/**
 * Medição de texto (só chamar com as fontes carregadas — ver `useFontesProntas`,
 * porque o `measureText` guarda cache).
 */
import { fillTextBox, measureText } from "@remotion/layout-utils";
import { FONTE } from "../brand";

type Estilo = { peso: number; tracking: string; familia?: string };

export const larguraTexto = (texto: string, tamanho: number, estilo: Estilo): number =>
  measureText({
    text: texto,
    fontFamily: estilo.familia ?? FONTE.familia,
    fontSize: tamanho,
    fontWeight: estilo.peso,
    letterSpacing: estilo.tracking,
  }).width;

/** Maior tamanho (passo 2 px) em que as palavras cabem em `maxLinhas`. */
export const tamanhoQueCabe = ({
  palavras,
  larguraMax,
  maxLinhas,
  tamanhoMax,
  tamanhoMin,
  peso,
  tracking,
}: {
  palavras: string[];
  larguraMax: number;
  maxLinhas: number;
  tamanhoMax: number;
  tamanhoMin: number;
  peso: number;
  tracking: string;
}): number => {
  if (palavras.length === 0) return tamanhoMax;
  for (let t = tamanhoMax; t > tamanhoMin; t -= 2) {
    const caixa = fillTextBox({ maxBoxWidth: larguraMax, maxLines: maxLinhas });
    let excede = false;
    palavras.forEach((p, i) => {
      const r = caixa.add({
        text: i === 0 ? p : ` ${p}`,
        fontFamily: FONTE.familia,
        fontSize: t,
        fontWeight: peso,
        letterSpacing: tracking,
      });
      if (r.exceedsBox) excede = true;
    });
    const palavraGrande = palavras.some(
      (p) => larguraTexto(p, t, { peso, tracking }) > larguraMax,
    );
    if (!excede && !palavraGrande) return t;
  }
  return tamanhoMin;
};
