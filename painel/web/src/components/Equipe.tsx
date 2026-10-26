import Link from "next/link";
import type { ReactNode } from "react";
import Avatar from "./Avatar";
import { Chip, ChipModelo, ModeloRodou, type ModeloRodouDados } from "./Chip";
import Icone from "./Icone";

// Peças da Equipe (design-system.md §15.2): Direção (`.k-direcao`), Departamento (`.k-depto`) e a linha de pessoa
// (`.k-pessoa-linha`). A linha inteira é o link para a ficha. Gerente com fundo surface-hover e contorno line (o laranja
// do artboard saiu: laranja é ação e foco). Portão: cadeado + "Portão da pauta" em accent-ink na 3.ª linha. Consumo em
// tokens (accent-ink) + US$; quem não rodou: "—" e "não rodou". Status (presença) é EXEMPLO na maquete e fica fora até
// existir o dado (telas/equipe.md) — por isso a linha tem uma coluna a menos (.kx-sem-status).

export type ConsumoPessoa = { tokens: string; custo: string } | null;

export function LinhaPessoa({ href, nome, funcao, portao, foto, rodou, consumo, tarefas, gerente, tags, busca }: {
  href: string;
  nome: string;
  funcao: string;
  /** "Portão da pauta" (só para quem é portão) */
  portao?: string | null;
  foto: string | null;
  /** o modelo que rodou nos 30 dias (null = ainda não rodou; undefined = sem a leitura) */
  rodou?: ModeloRodouDados;
  consumo: ConsumoPessoa;
  tarefas: number | null;
  gerente?: boolean;
  /** para o filtro da página: "todos portoes opus" */
  tags: string;
  /** texto em que a busca procura */
  busca: string;
}) {
  return (
    <li data-tags={tags} data-busca={busca}>
      <Link className={`k-pessoa-linha kx-sem-status${gerente ? " is-gerente" : ""}`} href={href}>
        <Avatar nome={nome} foto={foto} tamanho={32} />
        <span className="k-pessoa-id">
          <span className="k-pessoa-nome"><b title={nome}>{nome}</b></span>
          <span className="k-pessoa-funcao">{funcao}</span>
          {portao && <span className="k-pessoa-portao"><Icone nome="lock" tamanho={12} /> {portao}</span>}
        </span>
        <span>{rodou !== undefined && <ModeloRodou rodou={rodou} />}</span>
        <span className="k-pessoa-num k-dir">
          {consumo ? (
            <><span className="k-tokens">{consumo.tokens}<span className="k-sr-only"> tokens</span></span><small>{consumo.custo}</small></>
          ) : (
            <><span className="k-muted" aria-hidden="true">—</span><small>não rodou</small></>
          )}
        </span>
        <span className="k-pessoa-num k-dir">{tarefas ? <>{tarefas}<span className="k-sr-only"> tarefas</span></> : <span aria-label="nenhuma tarefa">—</span>}</span>
        <span className="k-pessoa-seta" aria-hidden="true"><Icone nome="chevron-right" tamanho={14} /></span>
      </Link>
    </li>
  );
}

export function Departamento({ nome, quantos, soma, children }: {
  nome: string;
  quantos: number;
  /** "1,7M tokens · US$ 10,80" — tokens em accent-ink */
  soma?: { tokens: string; custo: string } | null;
  children: ReactNode;
}) {
  return (
    <section className="k-card k-depto" aria-label={nome} data-grupo-filtro="">
      <div className="k-depto-head">
        <div>
          <h3 className="k-card-title">{nome}</h3>
          <span className="k-kpi-note">{quantos} {quantos === 1 ? "agente" : "agentes"}</span>
        </div>
        {soma && <span className="k-depto-soma"><span className="k-tokens">{soma.tokens} tokens</span> · {soma.custo}</span>}
      </div>
      <ul className="k-pessoas">
        <li aria-hidden="true">
          <div className="k-pessoa-linha k-pessoa-cab kx-sem-status">
            <span />
            <span>Agente</span>
            <span>Modelo</span>
            <span className="k-dir">Consumo</span>
            <span className="k-dir">Tarefas</span>
            <span />
          </div>
        </li>
        {children}
      </ul>
    </section>
  );
}

export function Direcao({ href, nome, cargo, resumo, foto, rodou, numeros, tags, busca }: {
  href: string;
  nome: string;
  cargo: string;
  resumo: string | null;
  foto: string | null;
  rodou?: ModeloRodouDados;
  /** Tarefas, Tokens, Custo (o número; tokens em accent, "US$" em <small>) e Rodou em (os modelos dos registros) */
  numeros: { rotulo: string; valor?: string; prefixo?: string; tokens?: boolean; modelos?: string[] }[];
  tags: string;
  busca: string;
}) {
  return (
    <div data-tags={tags} data-busca={busca}>
      <Link className="k-card is-interactive k-direcao" href={href}>
        <div className="k-direcao-quem">
          <Avatar nome={nome} foto={foto} tamanho={72} semRaio />
          <div className="kx-pilha-mini">
            <span className="k-cap">Direção</span>
            <div className="k-row kx-row-8">
              <h2 className="k-h3">{nome}</h2>
              {rodou !== undefined && <ModeloRodou rodou={rodou} />}
              <Chip tom="agendado" semPonto pequeno>Claude principal</Chip>
            </div>
            <span className="k-small k-ink2">{cargo}</span>
          </div>
        </div>
        {resumo && <p className="k-direcao-texto">{resumo}</p>}
        <div className="k-stats">
          {numeros.map((n) => (
            <div key={n.rotulo} className="k-stat">
              <span className="k-cap">{n.rotulo}</span>
              {n.modelos
                ? <span className="k-row kx-row-4">{n.modelos.map((m) => <ChipModelo key={m} modelo={m} rotulo={m} pequeno />)}</span>
                : (
                  <span className={`k-stat-v${n.tokens ? " k-tokens" : ""}`}>
                    {n.prefixo && n.valor !== "—" && <small>{n.prefixo}</small>}
                    {n.valor ?? "—"}
                  </span>
                )}
            </div>
          ))}
        </div>
      </Link>
    </div>
  );
}
