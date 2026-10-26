-- Fila: origem, selo e a conferência do GAUNTLET de cada post (PI39 do _controle/backlog-portoes.md; regra em
-- painel/design/handoff.md §5, "Fila no calendário"). A linha "Portões:" da tela responde se o post SAI, e quem decide
-- isso é o publicar.py, pelo scripts/portoes.py:
--   - pacote SEM selo e na lista congelada (_controle/gauntlet-legado.json) → legado: nada é exigido;
--   - pacote COM selo (legado ou não) → regra normal: os portões da origem (exigir) + os arquivos que eles aprovaram +
--     o portão da publicação sobre a pasta;
--   - pacote SEM selo e FORA da lista → recusado.
-- `fila.legado` continua a dizer só "o slug está na lista congelada"; a dispensa é legado AND NOT selado.
-- `erros_gauntlet` é o que portoes.conferir_pacote(pasta, pacote, post, publicacao=True) dá NESTA passagem (a mesma
-- chamada do publicar.py na hora de publicar): [] = o post pode sair. Pega também arquivo trocado depois do selo.
-- A fila é regravada inteira a cada passagem (a tabela fica vazia entre o truncate e o insert): as colunas entram com
-- default só para as linhas de agora e o default sai logo — o sincronizador grava sempre os três valores.

alter table fila
  add column origem text,                                  -- pacote.json → gauntlet.origem (ex.: videos/<slug>); NULL sem selo
  add column selado boolean not null default false,        -- o pacote.json tem o bloco gauntlet
  add column erros_gauntlet jsonb not null default '[]',   -- conferir_pacote(…, publicacao=True); [] = pode sair
  add constraint fila_origem_so_com_selo check (selado or origem is null),
  add constraint fila_erros_gauntlet_lista check (jsonb_typeof(erros_gauntlet) = 'array');
alter table fila alter column selado drop default, alter column erros_gauntlet drop default;

comment on column fila.legado is 'o slug está na lista congelada _controle/gauntlet-legado.json (dispensa = legado e não selado)';
comment on column fila.origem is 'pacote.json → gauntlet.origem (videos/<slug>); NULL quando o pacote não tem selo';
comment on column fila.selado is 'o pacote.json tem o bloco gauntlet (selado pelo montar_pacote.py)';
comment on column fila.erros_gauntlet is
  'erros de portoes.conferir_pacote(pasta, pacote, post, publicacao=True) nesta passagem; [] = o post pode sair';
