-- Cache gravado por TTL (correção do coordenador, 23/10). A gravação de cache tem DOIS preços: 5 min = 1,25 × a entrada,
-- 1 h = 2 × a entrada (documentação de prompt caching da Anthropic). Cada usage traz cache_creation
-- {ephemeral_5m_input_tokens, ephemeral_1h_input_tokens}; o tokens-custos.py de referência cobrava tudo a 1,25 × e por
-- isso dava US$ 482,14 no corte de 23/10 15:02:49Z, quando o certo é US$ 536,09. Os tokens não mudam.
--
-- uso_execucao: cache_gravado vira cache_gravado_5m + cache_gravado_1h (+ cache_gravado_sem_ttl, a parte dos 5 min que
-- veio sem o detalhe e foi tratada como 5 min). precos_modelo: um preço para cada gravação. As views passam a cobrar
-- pelo TTL. Aplicada antes de qualquer passagem gravar o arquivo (uso_execucao vazia): a divisão por TTL não se
-- reconstrói de linhas antigas, então a migração recusa se já houver consumo guardado.

do $$
begin
  if exists (select 1 from uso_execucao) then
    raise exception 'uso_execucao já tem linhas: a divisão do cache por TTL não se reconstrói delas';
  end if;
end
$$;

drop view consumo_diario;
drop view execucoes_custo;
drop view consumo;

alter table uso_execucao drop column tokens;
alter table uso_execucao rename column cache_gravado to cache_gravado_5m;  -- o check (>= 0) acompanha o nome
alter table uso_execucao
  add column cache_gravado_1h bigint not null default 0 check (cache_gravado_1h >= 0),
  add column cache_gravado_sem_ttl bigint not null default 0 check (cache_gravado_sem_ttl >= 0),
  add constraint uso_execucao_sem_ttl_dentro_dos_5m check (cache_gravado_sem_ttl <= cache_gravado_5m);
alter table uso_execucao alter column cache_gravado_1h drop default, alter column cache_gravado_sem_ttl drop default;
alter table uso_execucao
  add column tokens bigint generated always as (entrada + cache_gravado_5m + cache_gravado_1h + saida) stored;
comment on column uso_execucao.cache_gravado_5m is
  'cache_creation.ephemeral_5m_input_tokens (= cache_creation_input_tokens − a parte de 1 h; sem o detalhe, tudo aqui)';
comment on column uso_execucao.cache_gravado_1h is 'cache_creation.ephemeral_1h_input_tokens';
comment on column uso_execucao.cache_gravado_sem_ttl is
  'tokens de cache gravado que vieram sem cache_creation e foram tratados como 5 min (já somados em cache_gravado_5m)';
comment on column uso_execucao.tokens is 'entrada + cache gravado (5 min + 1 h) + saída; o cache lido fica fora';

alter table precos_modelo rename column cache_gravado to cache_gravado_5m;
alter table precos_modelo add column cache_gravado_1h numeric(10,4) not null default 0 check (cache_gravado_1h >= 0);
alter table precos_modelo alter column cache_gravado_1h drop default;
comment on column precos_modelo.cache_gravado_5m is 'US$/M de cache gravado com TTL de 5 min (1,25 × a entrada)';
comment on column precos_modelo.cache_gravado_1h is 'US$/M de cache gravado com TTL de 1 h (2 × a entrada)';

-- As mesmas três views, agora cobrando o cache gravado pelo TTL.
create view consumo with (security_invoker = true) as
select u.arquivo, u.dia, u.modelo, p.nome as modelo_nome,
       e.tipo, e.agente_tipo, e.membro_id, e.departamento_id, e.video_slug, e.registro_presente,
       u.respostas, u.entrada, u.cache_gravado_5m, u.cache_gravado_1h, u.cache_gravado_sem_ttl, u.cache_lido, u.saida,
       u.tokens,
       (u.entrada * p.entrada + u.cache_gravado_5m * p.cache_gravado_5m + u.cache_gravado_1h * p.cache_gravado_1h
        + u.cache_lido * p.cache_lido + u.saida * p.saida) / 1000000 as usd
from uso_execucao u
join precos_modelo p on p.modelo = u.modelo  -- modelo sem preço não conta (não se inventa preço)
join execucoes e on e.arquivo = u.arquivo;

create view consumo_diario with (security_invoker = true) as
select dia, modelo, modelo_nome, tipo, agente_tipo, membro_id, departamento_id,
       count(distinct arquivo)::int as execucoes, sum(respostas)::int as respostas,
       sum(entrada)::bigint as entrada, sum(cache_gravado_5m)::bigint as cache_gravado_5m,
       sum(cache_gravado_1h)::bigint as cache_gravado_1h, sum(cache_gravado_sem_ttl)::bigint as cache_gravado_sem_ttl,
       sum(cache_lido)::bigint as cache_lido, sum(saida)::bigint as saida, sum(tokens)::bigint as tokens,
       sum(usd) as usd
from consumo
group by dia, modelo, modelo_nome, tipo, agente_tipo, membro_id, departamento_id;

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

revoke all on consumo, consumo_diario, execucoes_custo from anon, authenticated, service_role, public;
grant select on consumo, consumo_diario, execucoes_custo to service_role;
