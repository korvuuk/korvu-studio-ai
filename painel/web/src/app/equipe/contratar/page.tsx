import { BotaoLink } from "@/components/Botao";
import { CabecalhoPagina } from "@/components/Pagina";
import * as db from "@/lib/db";
import { primeiraMaiuscula } from "@/lib/formato";
import Formulario from "./Formulario";

export default async function Contratar() {
  const [deps, ags] = await Promise.all([db.departamentos(), db.agentes()]);
  const nome = new Map(ags.map((a) => [a.id, a.nome]));
  const lista = deps
    .filter((d) => d.id !== "direcao")
    .map((d) => ({
      id: d.id, nome: primeiraMaiuscula(d.nome), gerente: d.gerente_id ? `${nome.get(d.gerente_id)} (${d.gerente_id})` : "?",
    }));
  return (
    <>
      <div className="mb-6">
        <BotaoLink href="/equipe" variante="fantasma" pequeno className="-ml-2.5">Voltar para a equipe</BotaoLink>
      </div>
      <CabecalhoPagina
        titulo="Contratar"
        descricao="Descreva a função. Todo funcionário novo entra num departamento e o trabalho dele passa pelo gerente (o portão) desse departamento antes de chegar ao Carlos."
      />
      <Formulario deps={lista} />
    </>
  );
}
