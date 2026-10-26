-- Prova do S1-1 da volta 2 (max_rows = 1000): banco DESCARTÁVEL (contêiner painel_fe_teste_db), nunca o do Carlos.
-- Parte dos dados reais do painel (pg_dump só de leitura) e passa de 1.000 linhas em perfil_demografia, metricas e
-- veredictos, gravando na ordem do sincronizador (por data; a foto mais nova por último).
begin;
-- 5 fotos novas do perfil (23 a 27/10), cópias da de 22/10. A de 27/10 é MARCADA para se reconhecer na tela:
-- alcançados +1000, seguidores +7.
create temp table base_dem as select * from perfil_demografia where lido_em = '2026-10-22 13:00:32+00';
create temp table base_snap as select * from perfil_snapshots where lido_em = '2026-10-22 13:00:32+00';
create temp table velha_dem as select * from perfil_demografia order by lido_em;
truncate perfil_demografia;
insert into perfil_demografia select * from velha_dem order by lido_em;  -- 16/10 e 22/10, nessa ordem
do $$
declare d int;
begin
  for d in 1..5 loop
    insert into perfil_snapshots
      select lido_em + make_interval(days => d), seguidores + d, seguindo, posts, janela_dias, alcance, views,
             contas_engajadas, interacoes, visitas_perfil, alcance_seguidores, alcance_nao_seguidores, fb_seguidores
      from base_snap;
    insert into perfil_demografia
      select lido_em + make_interval(days => d), publico, dimensao, chave,
             valor + case when d = 5 then (case when publico = 'alcancados' then 1000 else 7 end) else 0 end
      from base_dem order by publico desc, dimensao, chave;  -- "seguidores" antes de "alcancados", como no sync
  end loop;
end $$;

-- 1.100 leituras de métricas ANTIGAS (2025) do Demis, alcance 1: se a leitura cortar, a tela mostra 1 em vez de 338
create temp table velha_met as select * from metricas;
delete from metricas;
insert into metricas (slug, lido_em, dias, views, alcance, suspeito)
  select '2026-09-17-demis-hassabis', timestamptz '2025-01-01 00:00+00' + make_interval(hours => n), 0, 1, 1, false
  from generate_series(1, 1100) n;
insert into metricas select * from velha_met;

-- 1.100 veredictos ANTIGOS (2025) do portão de interface: se cortar, "veredictos recentes" mostra SINTETICO
insert into veredictos (alvo, slug, portao, agente, resultado, impressao, em, volta, s0, s1, s2)
  select 'painel', 'painel', 'interface', 'portao-interface', 'SINTETICO', 'x',
         timestamptz '2025-01-01 00:00+00' + make_interval(hours => n), 99, 0, 0, 0
  from generate_series(1, 1100) n;
commit;
select 'perfil_demografia', count(*) from perfil_demografia
union all select 'metricas', count(*) from metricas
union all select 'veredictos', count(*) from veredictos
union all select 'perfil_snapshots', count(*) from perfil_snapshots;
