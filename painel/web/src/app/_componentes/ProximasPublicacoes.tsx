import CartaoPublicacao from "@/components/CartaoPublicacao";
import ErroBloco from "@/components/ErroBloco";
import { BotaoLink } from "@/components/Botao";
import Vazio from "@/components/Vazio";
import { capa } from "@/lib/capas";
import { diaCurto, diasEntre, hora, relativo } from "@/lib/formato";
import { lerProducao } from "@/lib/producao";

// Visão geral · Próximas publicações (telas/visao-geral.md): a fila por data, um cartão por post, com a capa do pacote em
// 06-publicar/<slug>/capa/. Dia e hora no horário de Londres (o fuso em que os posts são agendados — não é definição de
// público). O cartão leva ao Calendário.

export async function ProximasPublicacoes() {
  let posts: Awaited<ReturnType<typeof lerProducao>>["agendados"];
  try {
    ({ agendados: posts } = await lerProducao());
  } catch {
    return <ErroBloco oque="A fila de publicação" />;
  }
  const hoje = new Date();
  const fila = posts.filter((p) => p.publicar_em).sort((a, b) => a.publicar_em!.localeCompare(b.publicar_em!));
  if (fila.length === 0) {
    return (
      <Vazio icone="clock" titulo="Nada agendado" acao={<BotaoLink href="/producao" variante="secundario" pequeno>Ver produção</BotaoLink>}>
        Quando um pacote entrar na fila, aparece aqui com dia, hora e canal.
      </Vazio>
    );
  }
  return (
    <div className="k-posts">
      {fila.map((p) => {
        const d = diasEntre(hoje, p.publicar_em!);
        return (
          <CartaoPublicacao
            key={p.slug}
            href="/calendario"
            capa={capa(p.slug, "fila")}
            nome={p.nome}
            dia={diaCurto(p.publicar_em!)}
            hora={hora(p.publicar_em)}
            relativo={relativo(d)}
            perto={d === 0 || d === 1}
            canais={p.plataformas}
            trial={p.trial}
          />
        );
      })}
    </div>
  );
}

/** "5 agendadas · horário de Londres" (o subtítulo da seção). */
export async function ContagemDaFila() {
  try {
    const { agendados } = await lerProducao();
    const n = agendados.filter((p) => p.publicar_em).length;
    return <>{n} {n === 1 ? "agendada" : "agendadas"} · horário de Londres</>;
  } catch {
    return <>horário de Londres</>;
  }
}
