import Esqueleto from "@/components/Esqueleto";

// Enquanto o servidor lê o banco: o esqueleto da página DENTRO da casca (a barra lateral não pisca), nunca um spinner
// de página inteira (design-system.md §12.1).
export default function Carregando() {
  return <Esqueleto />;
}
