import Image from "next/image";
import Link from "next/link";
import { iniciais } from "@/lib/formato";
import { Chip, ModeloRodou, type ModeloRodouDados } from "./Chip";

// Cartão de agente com foto (design-system.md §15.2, `.k-agente`): foto 4:3 em cima a 1440 (à esquerda ≥ 1600 e < 640);
// sem foto, as iniciais no mesmo quadro. O nome NUNCA corta: quebra em até 2 linhas. Função, departamento, o chip Portão
// (papel portao) e o modelo que RODOU, com a versão. Presença ("Trabalhando agora") é exemplo nas maquetes e não aparece aqui até
// existir o dado (telas/visao-geral.md).

export default function CartaoAgente({ href, nome, funcao, departamento, foto, portao, rodou }: {
  href: string;
  nome: string;
  funcao: string;
  departamento?: string | null;
  foto: string | null;
  portao?: boolean;
  /** o modelo que rodou nos 30 dias (decisão de 24/10); null = ainda não rodou */
  rodou?: ModeloRodouDados;
}) {
  return (
    <Link className="k-card is-interactive k-agente" href={href}>
      <span className="k-agente-foto" aria-hidden={foto ? undefined : true}>
        {foto ? <Image src={foto} alt={`Retrato de ${nome}`} width={480} height={360} sizes="(max-width: 639px) 96px, 280px" /> : iniciais(nome)}
      </span>
      <div className="k-agente-txt">
        <h3 className="k-agente-nome">{nome}</h3>
        <p className="k-agente-funcao">{funcao}</p>
        {departamento && <p className="k-agente-depto">{departamento}</p>}
        <div className="k-agente-chips">
          {portao && <Chip tom="portao" icone="lock" pequeno>Portão</Chip>}
          {rodou !== undefined && <ModeloRodou rodou={rodou} />}
        </div>
      </div>
    </Link>
  );
}
