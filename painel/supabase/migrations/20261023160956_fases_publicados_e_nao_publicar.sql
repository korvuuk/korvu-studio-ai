-- Fases da "Produção de conteúdo" (decisão do Carlos, 23/10, docs/decisoes.md §5: Roteiros → Gravados → Prontos →
-- Agendados → Publicados), publicados pelo post.json e a trava "não publicar". Pedido de painel/design/handoff.md §8.
--
-- videos: gravado = há arquivo de vídeo de verdade em videos/<slug>/brutos/principal/ (só a listagem e o tamanho: os
--   brutos não são abertos); pronto = há pacote em 05-render-pronto/ com qa = PASS cujo vídeo de origem é este.
-- fila e publicacoes: video_slug = o vídeo de origem da pasta (gauntlet.origem do pacote.json; senão o slug de videos/
--   mais longo que é prefixo do slug da pasta; senão o próprio slug) — a mesma regra das execuções de tokens.
-- publicacoes: entra pela pasta de 07-publicados/ com post.json (permalinks, plataformas, estado, publicado_em) ou com
--   metricas.json; as métricas chegam depois, quando o metricas.py ler (5 dias). Sem post.json, plataformas/estado NULL.
-- nao_publicar: espelho de _controle/nao-publicar.json (opcional; ausente = nenhuma trava), uma linha por slug travado.
-- As tabelas são regravadas inteiras a cada passagem: os defaults só servem às linhas de agora e saem logo.

alter table videos
  add column gravado boolean not null default false,
  add column gravacao_arquivos int not null default 0 check (gravacao_arquivos >= 0),
  add column gravacao_bytes bigint not null default 0 check (gravacao_bytes >= 0),
  add column gravacao_ultima timestamptz,
  add column pronto boolean not null default false,
  add constraint videos_gravado_tem_arquivo check (gravado = (gravacao_arquivos > 0));
alter table videos alter column gravado drop default, alter column gravacao_arquivos drop default,
  alter column gravacao_bytes drop default, alter column pronto drop default;
comment on column videos.gravado is 'há arquivo de vídeo (.mov, .mp4…, não oculto, > 0 bytes) em brutos/principal/';
comment on column videos.gravacao_arquivos is 'quantos arquivos de vídeo há em brutos/principal/ (subpastas incluídas)';
comment on column videos.gravacao_bytes is 'soma do tamanho desses arquivos';
comment on column videos.gravacao_ultima is 'data de modificação mais recente desses arquivos (NULL sem gravação)';
comment on column videos.pronto is 'há pacote em 05-render-pronto/ com qa = PASS cujo vídeo de origem é este';

alter table fila add column video_slug text;
comment on column fila.video_slug is 'vídeo de origem da pasta (gauntlet.origem → videos/ mais longo que é prefixo → o slug)';

alter table publicacoes
  add column video_slug text,
  add column plataformas text[],
  add column estado text;
comment on column publicacoes.video_slug is 'vídeo de origem da pasta de 07-publicados/ (mesma regra da fila)';
comment on column publicacoes.plataformas is 'post.json → plataformas; NULL se a pasta não tem post.json';
comment on column publicacoes.estado is 'post.json → estado (publicado…); NULL se a pasta não tem post.json';

create table nao_publicar (
  slug text primary key,                          -- o slug travado (vídeo ou pasta de pacote)
  video_slug text not null,                       -- o vídeo de origem desse slug
  motivo text not null check (btrim(motivo) <> ''),
  desde date not null
);
comment on table nao_publicar is
  'Trava manual "não publicar", espelho de _controle/nao-publicar.json ({"travas": [{slug, motivo, desde}]}).';
alter table nao_publicar enable row level security;
revoke all on nao_publicar from anon, authenticated, service_role, public;
grant select on nao_publicar to service_role;
