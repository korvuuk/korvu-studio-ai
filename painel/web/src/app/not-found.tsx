import { BotaoLink } from "@/components/Botao";
import EstadoPagina from "@/components/EstadoPagina";

// Não encontrado (design-system.md §12.3), dentro da casca.
export default function NaoEncontrada() {
  return (
    <EstadoPagina
      icone="search"
      titulo="Página não encontrada"
      texto="Este endereço não existe no painel. Se era a ficha de alguém da equipe, a pessoa pode ter saído ou mudado de nome."
      acoes={
        <>
          <BotaoLink href="/" variante="primario">Ir para a visão geral</BotaoLink>
          <BotaoLink href="/equipe" variante="fantasma">Ver a equipe</BotaoLink>
        </>
      }
    />
  );
}
