"use client";

import { useMemo, useState } from "react";
import { Botao } from "@/components/Botao";
import { CampoEscolha, CampoTexto, CampoTextoLongo } from "@/components/Campo";
import { BlocoCodigo } from "@/components/Texto";
import { MODELOS } from "@/lib/formato";

type Dep = { id: string; nome: string; gerente: string };

// Os modelos que a equipe usa, com a versão (decisão de 23/10). O valor é o apelido que vai para o arquivo do agente
// (`model: opus`); o rótulo mostra a versão. Haiku saiu da lista: nenhum agente usa e não há versão registrada dele.
const OPCOES_MODELO = [
  { valor: "sonnet", rotulo: `${MODELOS.sonnet} — tarefas de execução` },
  { valor: "opus", rotulo: `${MODELOS.opus} — julgamento, texto, edição` },
];

export default function Formulario({ deps }: { deps: Dep[] }) {
  const [f, setF] = useState({
    nome: "", cargo: "", departamento: deps[0]?.id ?? "", faz: "", entrega: "", quando: "", modelo: "sonnet",
  });
  const [copiado, setCopiado] = useState(false);
  const dep = deps.find((d) => d.id === f.departamento);
  const id = f.cargo.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

  const pedido = useMemo(() => [
    `Contratar um agente novo para o CONTENT AI.`,
    ``,
    `- Nome: ${f.nome || "(a definir)"}`,
    `- Cargo: ${f.cargo || "(a definir)"}  → arquivo .claude/agents/${id || "<id>"}.md`,
    `- Departamento: ${dep?.nome ?? "?"} — o trabalho dele passa pelo portão ${dep?.gerente ?? "?"} (GAUNTLET: quem faz não aprova)`,
    `- O que faz: ${f.faz || "(descrever)"}`,
    `- O que entrega (arquivos): ${f.entrega || "(descrever)"}`,
    `- Quando é chamado: ${f.quando || "(comando / etapa do pipeline)"}`,
    `- Modelo: ${f.modelo} (${MODELOS[f.modelo] ?? f.modelo})`,
    ``,
    `Criar o arquivo do agente, a ficha em painel/equipe.yaml, ligar no comando certo e no portão do departamento`,
    `(scripts/portoes.py → PORTOES[...]["fiscaliza"]), registrar a decisão em docs/decisoes.md e rodar o sincronizador.`,
  ].join("\n"), [f, id, dep]);

  const muda = (k: keyof typeof f) => (e: { target: { value: string } }) => setF({ ...f, [k]: e.target.value });

  return (
    <div className="grid gap-12 lg:grid-cols-2">
      <form className="flex flex-col gap-4" onSubmit={(e) => e.preventDefault()}>
        <CampoTexto rotulo="Nome" value={f.nome} onChange={muda("nome")} placeholder="ex.: Rita Souza" />
        <CampoTexto rotulo="Cargo" value={f.cargo} onChange={muda("cargo")} placeholder="ex.: legendador" />
        <CampoEscolha
          rotulo="Departamento"
          value={f.departamento}
          onChange={muda("departamento")}
          opcoes={deps.map((d) => ({ valor: d.id, rotulo: d.nome }))}
        />
        <CampoTextoLongo rotulo="O que faz" value={f.faz} onChange={muda("faz")} placeholder="a função em uma ou duas frases" />
        <CampoTextoLongo rotulo="O que entrega" value={f.entrega} onChange={muda("entrega")} placeholder="que arquivos ficam prontos quando ele termina" />
        <CampoTexto rotulo="Quando é chamado" value={f.quando} onChange={muda("quando")} placeholder="ex.: no /renderizar, depois da cor" />
        <CampoEscolha rotulo="Modelo" value={f.modelo} onChange={muda("modelo")} opcoes={OPCOES_MODELO} />
      </form>
      <div className="flex flex-col gap-3">
        <BlocoCodigo rotulo="Pedido de contratação">{pedido}</BlocoCodigo>
        <div>
          <Botao
            variante="primario"
            icone={copiado ? "check" : undefined}
            onClick={async () => { await navigator.clipboard.writeText(pedido); setCopiado(true); setTimeout(() => setCopiado(false), 2000); }}
          >
            {copiado ? "Pedido copiado" : "Copiar pedido"}
          </Botao>
          <span className="k-sr-only" aria-live="polite">{copiado ? "Pedido copiado" : ""}</span>
        </div>
        <p className="k-kpi-note kx-sem-margem">
          Cole o pedido numa conversa com o Claude no projeto. Ele cria o agente, liga ao portão do departamento e o
          novo funcionário aparece aqui depois do sincronizador. O painel não cria arquivos sozinho.
        </p>
      </div>
    </div>
  );
}
