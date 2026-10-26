-- O modelo que RODOU, por agente (decisão do Carlos, 24/10, docs/decisoes.md §5: "Equipe mostra o modelo que RODOU",
-- não o configurado — quem escolhe o modelo são os orquestradores, pela tarefa). Uma view sobre o consumo que já está no
-- banco (os registros do Claude Code): nada novo é lido de arquivo.
--
-- Uma linha por agente × modelo que rodou nos últimos 30 dias, e uma linha com modelo NULL para o agente que não rodou
-- na janela — todo agente de `agentes` aparece. Membro = a regra do sincronizador: a sessão principal, os ajudantes do
-- Claude Code (general-purpose, workflow-subagent, claude, Explore, Plan) e qualquer agentType fora do equipe.yaml contam
-- como `diretor` (Atlas) — a mistura de modelos do Atlas inclui os ajudantes. Conta o que está em `consumo` (modelo com
-- preço), inclusive as execuções arquivadas (o .jsonl já sumiu, registro_presente = false).
--
-- JANELA: os 30 dias UTC até hoje, inclusive — de (hoje − 29) a hoje, com hoje = (now() at time zone 'UTC')::date (o
-- `dia` do consumo é a data UTC; o banco do painel roda em UTC, então é o mesmo que current_date). Para teste e
-- reconciliação, um `set painel.hoje = 'AAAA-MM-DD'` na sessão fixa o "hoje"; o app não o usa.

create view modelo_por_agente with (security_invoker = true) as
with janela as (
  select hoje - 29 as inicio, hoje as fim
  from (select coalesce(nullif(current_setting('painel.hoje', true), '')::date,
                        (now() at time zone 'UTC')::date) as hoje) h
),
uso as (  -- o consumo na janela, por agente × modelo
  select c.membro_id as agente_id, c.modelo, c.modelo_nome, sum(c.tokens)::bigint as tokens, sum(c.usd) as usd,
         count(distinct c.arquivo)::int as execucoes, max(e.fim) as ultima_execucao
  from consumo c
  join execucoes e on e.arquivo = c.arquivo
  cross join janela j
  where c.dia between j.inicio and j.fim
  group by c.membro_id, c.modelo, c.modelo_nome
),
sempre as (  -- toda execução do agente, de sempre (também as arquivadas e as só de modelo sem preço)
  select membro_id as agente_id, max(fim) as ultima_execucao_geral
  from execucoes
  group by membro_id
)
select a.id as agente_id, a.modelo as modelo_declarado, u.modelo, u.modelo_nome,
       coalesce(u.tokens, 0)::bigint as tokens,
       100.0 * u.tokens / nullif(sum(u.tokens) over (partition by a.id), 0) as pct_tokens,
       coalesce(u.usd, 0) as usd, coalesce(u.execucoes, 0)::int as execucoes, u.ultima_execucao,
       s.ultima_execucao_geral, s.agente_id is null as nunca_rodou
from agentes a
left join uso u on u.agente_id = a.id
left join sempre s on s.agente_id = a.id;

comment on view modelo_por_agente is
  'O modelo que rodou, por agente (decisão de 24/10): uma linha por agente × modelo nos 30 dias UTC até hoje (inclusive), '
  'ou uma linha com modelo NULL se o agente não rodou na janela. pct_tokens = % dos tokens do agente na janela (somam '
  '100 por agente). Membro: a sessão principal e os ajudantes do Claude Code contam como diretor. modelo_declarado = '
  'agentes.modelo (o model: de .claude/agents/*.md). ultima_execucao_geral = o fim mais recente de sempre, também '
  'arquivada; nunca_rodou = nenhuma execução em execucoes.';

revoke all on modelo_por_agente from anon, authenticated, service_role, public;
grant select on modelo_por_agente to service_role;
