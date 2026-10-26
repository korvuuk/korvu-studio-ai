-- Volta 1 do PORTÃO-DADOS de 24/10 (painel/portoes/dados-2026-10-24-v1.md), S1-2: a Biblioteca mostra o que está NO MAC.
--
-- Desde a 20261024042911, videos.gravacao_arquivos/gravacao_bytes somam os vídeos de brutos/principal/ no disco E os
-- originais que foram para o HD externo (brutos/principal/ARQUIVADO.json) — o certo para "gravado" (Produção). Mas o
-- Armazenamento da Biblioteca ("as gravações da câmera somam …", como o Finder) quer só o que ocupa o Mac. Ficam as duas
-- contas, separadas:
--   gravacao_arquivos_no_mac / gravacao_bytes_no_mac   os vídeos de brutos/principal/ no disco (o stat de cada um);
--   gravacao_arquivados / gravacao_arquivados_bytes     os do ARQUIVADO.json que não estão no disco (no HD externo);
--   a soma das duas = gravacao_arquivos / gravacao_bytes (as de sempre, que continuam a dizer o total).
-- biblioteca_por_video: principal_arquivos/principal_bytes passam a ser SÓ o que está no Mac (antes: o total, que
-- incluiria o HD); principal_hd_arquivos/principal_hd_bytes = o que está no HD. As 5 colunas antigas mantêm nome e tipo.
-- A tabela videos é regravada inteira a cada passagem: os defaults só servem às linhas de agora e saem logo.

alter table videos
  add column gravacao_arquivos_no_mac int not null default 0 check (gravacao_arquivos_no_mac >= 0),
  add column gravacao_bytes_no_mac bigint not null default 0 check (gravacao_bytes_no_mac >= 0),
  add column gravacao_arquivados_bytes bigint not null default 0 check (gravacao_arquivados_bytes >= 0);
update videos set gravacao_arquivos_no_mac = gravacao_arquivos - gravacao_arquivados, gravacao_bytes_no_mac = gravacao_bytes;
alter table videos alter column gravacao_arquivos_no_mac drop default, alter column gravacao_bytes_no_mac drop default,
  alter column gravacao_arquivados_bytes drop default,
  add constraint videos_gravacao_mac_mais_hd check (gravacao_arquivos_no_mac + gravacao_arquivados = gravacao_arquivos
                                                   and gravacao_bytes_no_mac + gravacao_arquivados_bytes = gravacao_bytes);
comment on column videos.gravacao_arquivos is 'vídeos da gravação: no Mac (brutos/principal/) + no HD (ARQUIVADO.json)';
comment on column videos.gravacao_bytes is 'bytes da gravação: no Mac + no HD';
comment on column videos.gravacao_arquivos_no_mac is 'vídeos de brutos/principal/ no disco do Mac';
comment on column videos.gravacao_bytes_no_mac is 'bytes dos vídeos de brutos/principal/ no disco do Mac (o que o Finder soma)';
comment on column videos.gravacao_arquivados_bytes is
  'bytes dos originais do ARQUIVADO.json que não estão no disco (no HD externo; o tamanho é o do manifesto)';
comment on column videos.gravacao_ultima is
  'mtime mais recente da gravação, truncado para o segundo (do disco e do manifesto: o escritor real grava em segundos)';
comment on column videos.gravacao_chegou is
  'ctime mais recente da gravação, truncado para o segundo: quando os arquivos entraram (ou mudaram) no disco do projeto';

create or replace view biblioteca_por_video with (security_invoker = true) as
select v.slug as video_slug, count(a.caminho)::int as arquivos, coalesce(sum(a.bytes), 0)::bigint as bytes,
       v.gravacao_arquivos_no_mac as principal_arquivos, v.gravacao_bytes_no_mac as principal_bytes,
       v.gravacao_arquivados as principal_hd_arquivos, v.gravacao_arquivados_bytes as principal_hd_bytes
from videos v
left join biblioteca_arquivos a on a.video_slug = v.slug
group by v.slug, v.gravacao_arquivos_no_mac, v.gravacao_bytes_no_mac, v.gravacao_arquivados, v.gravacao_arquivados_bytes;
comment on view biblioteca_por_video is
  'por vídeo: material + cenas extras (arquivos, bytes); a gravação da câmera NO MAC (principal_arquivos, principal_bytes) '
  'e NO HD externo (principal_hd_arquivos, principal_hd_bytes)';

revoke all on biblioteca_por_video from anon, authenticated, service_role, public;
grant select on biblioteca_por_video to service_role;
