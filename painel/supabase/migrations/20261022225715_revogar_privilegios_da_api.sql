-- Permissões dos papéis da API, declaradas e fechadas (S0-1 do PORTÃO-DADOS, painel/portoes/dados-2026-10-22-v1.md).
--
-- O que o banco fazia sem isto: os default privileges do schema public para o papel postgres (quem roda as migrações)
-- davam TRUNCATE, REFERENCES, TRIGGER e MAINTAIN a anon e authenticated — e isso + SELECT ao service_role — em toda
-- tabela nova, e UPDATE nas sequências. O RLS não cobre TRUNCATE nem TRIGGER, e nada disso estava em migração.
--
-- O que o painel quer:
--   anon, authenticated -> nada (não há login; o app não usa a chave anon);
--   service_role        -> só SELECT nas tabelas (o app lê do lado do servidor; quem escreve é o sincronizador, como
--                          postgres, dono das tabelas).
-- Vale para o que já existe (1) e, pelos default privileges, para o que as próximas migrações criarem (2).
-- Fora do alcance desta migração: os default privileges do papel supabase_admin (só valem para objetos que ELE cria
-- no public; as migrações rodam como postgres, que não é membro de supabase_admin e não pode alterá-los).

-- 1. O que já existe
revoke all on all tables    in schema public from anon, authenticated, service_role;
revoke all on all sequences in schema public from anon, authenticated, service_role;
revoke all on all routines  in schema public from anon, authenticated, service_role, public;
grant select on all tables in schema public to service_role;

-- 2. O que as próximas migrações criarem
alter default privileges for role postgres in schema public revoke all on tables    from anon, authenticated, service_role;
alter default privileges for role postgres in schema public revoke all on sequences from anon, authenticated, service_role;
alter default privileges for role postgres in schema public revoke all on functions from anon, authenticated, service_role, public;
-- Default privileges POR SCHEMA só somam aos globais, não tiram: o EXECUTE que o Postgres dá a PUBLIC (e portanto a
-- anon) em toda função nova só sai com o default GLOBAL do papel postgres. Sem isto, uma função acrescentada ao public
-- viraria um RPC que a chave anon chama.
alter default privileges for role postgres revoke execute on functions from public;
alter default privileges for role postgres in schema public grant select on tables to service_role;
