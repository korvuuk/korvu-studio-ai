-- O Supabase novo não dá mais acesso automático às tabelas do schema public para os papéis da API.
-- O app do painel lê com a chave de serviço (só no servidor): leitura para service_role e nada para anon/authenticated.
grant usage on schema public to service_role;
grant select on all tables in schema public to service_role;
alter default privileges in schema public grant select on tables to service_role;
