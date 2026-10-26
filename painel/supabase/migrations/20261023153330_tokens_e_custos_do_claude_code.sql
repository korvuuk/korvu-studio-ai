-- Tokens e custos do Claude Code (23/10) — telas "Tokens e custos", "Equipe" e "Visão geral".
--
-- Fonte: os registros das sessões do Claude Code deste projeto (~/.claude/projects/<raiz com / e espaço → ->/**/*.jsonl;
-- pasta configurável por PAINEL_REGISTROS). Sessão principal = .jsonl de primeiro nível; subagente =
-- <sessão>/subagents/[workflows/<wf>/]agent-<id>.jsonl, com o tipo no agent-<id>.meta.json (agentType). Cada resposta
-- traz message.usage + message.model + timestamp. As regras de leitura são as do tokens-custos.py de referência
-- (painel/referencias/claude-design/telas-2026-10-23/): deduplicação por (message.id ou uuid) + arquivo, ficando com a
-- primeira ocorrência; dia = 10 primeiros caracteres do timestamp (data UTC); tokens = entrada + cache gravado + saída
-- (o cache lido entra só no custo); modelo sem preço não conta.
--
-- ARQUIVO, não espelho. O Claude Code apaga os registros com mais de 30 dias (cleanupPeriodDays). Se estas tabelas
-- fossem regravadas inteiras como as outras, o painel perderia o histórico a cada limpeza. O sincronizador, numa
-- transação só: apaga e regrava as execuções cujo .jsonl ainda existe (o arquivo continua a ser a verdade enquanto
-- existe) e MANTÉM as que já sumiram, com registro_presente = false. Nunca trunca estas três tabelas.
--
-- Custo = equivalente no preço de tabela da API (US$ por milhão de tokens), NÃO a fatura da assinatura. Não é guardado
-- nas linhas: as views calculam-no a partir de precos_modelo, então o número e a sua origem são sempre os mesmos — e
-- uma resposta de modelo sem preço fica guardada (uso_execucao) mas fora de todo custo e de toda contagem de tarefas.
-- Nada de texto de conversa no banco: nem o pedido nem a resposta — só números, ids, tipo, modelo, horários, slug e a
-- description curta do .meta.json.

create table precos_modelo (
  modelo text primary key,                       -- message.model do registro (ex.: claude-opus-5-5)
  nome text not null,                            -- como o painel mostra (ex.: Opus 5.5)
  entrada numeric(10,4) not null check (entrada >= 0),             -- US$ por milhão de tokens de entrada
  cache_gravado numeric(10,4) not null check (cache_gravado >= 0), -- US$/M de cache gravado (1,25 × a entrada)
  cache_lido numeric(10,4) not null check (cache_lido >= 0),       -- US$/M de cache lido
  saida numeric(10,4) not null check (saida >= 0)                  -- US$/M de saída
);
comment on table precos_modelo is
  'Preço de tabela da API por milhão de tokens (US$). Regravada a cada passagem a partir de PRECOS no sincronizador. '
  'Custo = equivalente na API, não a fatura da assinatura.';

create table execucoes (
  arquivo text primary key,                      -- caminho do .jsonl relativo à pasta dos registros
  tipo text not null check (tipo in ('principal', 'subagente')),
  sessao text not null,                          -- id da sessão do Claude Code (no subagente: a sessão-mãe)
  agente_id text,                                -- o <id> de agent-<id>.jsonl; NULL na sessão principal
  workflow text,                                 -- wf_… quando o subagente rodou dentro de um workflow
  agente_tipo text,                              -- agentType cru do .meta.json (NULL: sessão principal ou meta ausente)
  membro_id text not null,                       -- quem é na equipe (painel/equipe.yaml): sessão principal, ajudantes
                                                 -- (general-purpose, workflow-subagent, claude, Explore, Plan) e
                                                 -- agentType fora do yaml = 'diretor' (Atlas)
  departamento_id text not null,                 -- departamento do membro no equipe.yaml (diretor = direcao)
  descricao text check (char_length(descricao) <= 200), -- description curta do .meta.json (não é o pedido)
  profundidade int,                              -- spawnDepth do .meta.json
  terminou boolean,                              -- finished do .meta.json
  video_slug text,                               -- só subagente: o primeiro videos/<slug> do 1.º pedido cujo slug
                                                 -- existe como pasta em videos/, 05-render-pronto/, 06-publicar/ ou
                                                 -- 07-publicados/; senão NULL
  inicio timestamptz,                            -- 1.ª e última resposta com usage (qualquer modelo)
  fim timestamptz,
  registro_presente boolean not null default true, -- false = o .jsonl já sumiu dos registros; a linha é o arquivo
  visto_em timestamptz not null,                 -- última passagem que leu o .jsonl
  check ((tipo = 'principal') = (agente_id is null)),
  check (fim >= inicio)
);
comment on table execucoes is
  'Uma linha por .jsonl dos registros do Claude Code com ao menos uma resposta. ARQUIVO: a linha fica quando o .jsonl '
  'some (registro_presente = false). Tarefa (como no tokens-custos.py) = execução com resposta de modelo COM preço: '
  'conte em consumo/execucoes_custo, não aqui.';

create table uso_execucao (
  arquivo text not null references execucoes (arquivo) on delete cascade,
  dia date not null,                             -- 10 primeiros caracteres do timestamp da resposta (data UTC)
  modelo text not null,                          -- message.model (também os sem preço: ficam guardados, não contam)
  respostas int not null check (respostas > 0),  -- respostas distintas (message.id ou uuid) neste arquivo
  entrada bigint not null check (entrada >= 0),             -- input_tokens
  cache_gravado bigint not null check (cache_gravado >= 0), -- cache_creation_input_tokens
  cache_lido bigint not null check (cache_lido >= 0),       -- cache_read_input_tokens
  saida bigint not null check (saida >= 0),                 -- output_tokens
  tokens bigint generated always as (entrada + cache_gravado + saida) stored, -- o cache lido fica fora
  primary key (arquivo, dia, modelo)
);
create index uso_execucao_dia on uso_execucao (dia);  -- as telas filtram sempre por janela de dias
comment on table uso_execucao is
  'Consumo de cada execução por dia (UTC) × modelo, contado do .jsonl. ARQUIVO como execucoes.';

-- Consumo que conta: execução × dia × modelo COM preço, com o custo e quem é. A base de todas as somas das telas
-- (total, por dia, por modelo, por departamento, por agente, por vídeo, tarefas = count(distinct arquivo)).
create view consumo with (security_invoker = true) as
select u.arquivo, u.dia, u.modelo, p.nome as modelo_nome,
       e.tipo, e.agente_tipo, e.membro_id, e.departamento_id, e.video_slug, e.registro_presente,
       u.respostas, u.entrada, u.cache_gravado, u.cache_lido, u.saida, u.tokens,
       (u.entrada * p.entrada + u.cache_gravado * p.cache_gravado + u.cache_lido * p.cache_lido
        + u.saida * p.saida) / 1000000 as usd
from uso_execucao u
join precos_modelo p on p.modelo = u.modelo  -- modelo sem preço não conta (não se inventa preço)
join execucoes e on e.arquivo = u.arquivo;

-- O grão das telas: dia × modelo × agente (e departamento). "execucoes" é por dia — não se soma entre dias (uma
-- execução que atravessa a meia-noite UTC aparece nos dois): para tarefas numa janela, count(distinct arquivo) em consumo.
create view consumo_diario with (security_invoker = true) as
select dia, modelo, modelo_nome, tipo, agente_tipo, membro_id, departamento_id,
       count(distinct arquivo)::int as execucoes, sum(respostas)::int as respostas,
       sum(entrada)::bigint as entrada, sum(cache_gravado)::bigint as cache_gravado,
       sum(cache_lido)::bigint as cache_lido, sum(saida)::bigint as saida, sum(tokens)::bigint as tokens,
       sum(usd) as usd
from consumo
group by dia, modelo, modelo_nome, tipo, agente_tipo, membro_id, departamento_id;

-- Cada execução com os seus totais (de sempre). tarefa = tem resposta de modelo com preço (a regra do tokens-custos.py).
create view execucoes_custo with (security_invoker = true) as
select e.arquivo, e.tipo, e.sessao, e.agente_id, e.workflow, e.agente_tipo, e.membro_id, e.departamento_id,
       e.descricao, e.profundidade, e.terminou, e.video_slug, e.inicio, e.fim, e.registro_presente, e.visto_em,
       coalesce(c.respostas, 0) > 0 as tarefa,
       coalesce(c.respostas, 0)::int as respostas, coalesce(c.tokens, 0)::bigint as tokens,
       coalesce(c.usd, 0) as usd, coalesce(f.respostas, 0)::int as respostas_sem_preco
from execucoes e
left join (select arquivo, sum(respostas) as respostas, sum(tokens) as tokens, sum(usd) as usd
           from consumo group by arquivo) c on c.arquivo = e.arquivo
left join (select u.arquivo, sum(u.respostas) as respostas
           from uso_execucao u
           where not exists (select 1 from precos_modelo p where p.modelo = u.modelo)
           group by u.arquivo) f on f.arquivo = e.arquivo;

-- RLS em toda tabela (sem política: só quem ignora RLS — postgres, que escreve, e service_role, que lê — passa). As
-- views são security_invoker: valem as permissões e o RLS de quem consulta.
alter table precos_modelo enable row level security;
alter table execucoes enable row level security;
alter table uso_execucao enable row level security;

-- Permissões declaradas aqui, sem depender só dos default privileges da 20261022225715: anon e authenticated sem nada
-- (não há login); service_role só SELECT (o app lê do lado do servidor).
revoke all on precos_modelo, execucoes, uso_execucao, consumo, consumo_diario, execucoes_custo
  from anon, authenticated, service_role, public;
grant select on precos_modelo, execucoes, uso_execucao, consumo, consumo_diario, execucoes_custo to service_role;
