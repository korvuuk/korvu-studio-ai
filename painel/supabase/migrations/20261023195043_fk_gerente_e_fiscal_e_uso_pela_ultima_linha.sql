-- Volta 1 do PORTÃO-DADOS (painel/portoes/dados-2026-10-23-v2.md).
--
-- S1-6 (PD5): o gerente de cada departamento e o portão que fiscaliza cada agente têm de ser agentes do painel
-- (painel/equipe.yaml). Um "gerente:" com erro de digitação passava a "?" na tela; agora a passagem falha com uma linha
-- ✗ e o banco fica com a anterior. A relação é circular (agentes.departamento_id → departamentos; departamentos.gerente_id
-- → agentes) e a passagem faz truncate + insert numa transação só, então as duas FKs são conferidas no commit
-- (deferrable initially deferred). Conferido antes: no banco do painel e nos dados de teste, todo gerente_id e todo
-- fiscalizado_por é um agente.
--
-- S1-1: a regra do consumo mudou (sincronizador): de cada resposta vale o usage da ÚLTIMA linha (as versões
-- 2.1.270–2.1.304 do Claude Code gravam na 1.ª o usage provisório, com output_tokens 1–3). Os comentários de SQL da
-- 20261023153330 ("ficando com a primeira ocorrência") ficam como registro do que foi aplicado; vale o comentário abaixo.

alter table departamentos
  add constraint departamentos_gerente_id_fkey foreign key (gerente_id) references agentes (id)
  deferrable initially deferred;
alter table agentes
  add constraint agentes_fiscalizado_por_fkey foreign key (fiscalizado_por) references agentes (id)
  deferrable initially deferred;
create index agentes_fiscalizado_por on agentes (fiscalizado_por);  -- FK sem índice = varredura a cada conferência
create index departamentos_gerente_id on departamentos (gerente_id);

comment on table uso_execucao is
  'Consumo de cada execução por dia (UTC) × modelo, contado do .jsonl: uma resposta = as linhas com a mesma chave '
  '(message.id, ou uuid) no mesmo arquivo; vale o usage da ÚLTIMA linha lida (a 1.ª pode trazer o usage provisório), '
  'com o dia da 1.ª. ARQUIVO como execucoes.';
