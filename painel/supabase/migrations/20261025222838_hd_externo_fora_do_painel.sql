-- 25/10 (decisão do Carlos, docs/decisoes.md §5): o HD externo não aparece no painel — foi só a cópia de segurança e já
-- está desligado. Saem os campos da "nota do HD" que a 20261025214021 criou: videos.hd_arquivado_em, hd_volume e
-- hd_conferido, e na view armazenamento hd_arquivado_em e hd_todos_conferidos. A view volta a ser a da 20261024215907
-- (as colunas hd_bytes, hd_arquivos e hd_videos ficam: não são desta decisão).
-- FICA a leitura do brutos/principal/ARQUIVADO.json para contar a gravação (videos.gravado, gravacao_*, *_no_mac,
-- gravacao_arquivados*), com o sha256 de cada arquivo obrigatório como antes. As frases e nomes dos looks
-- (looks.descricao) também ficam.

-- a view lê as colunas que saem: primeiro ela, depois as colunas, e ela de volta sem elas
drop view armazenamento;

alter table videos
  drop constraint videos_nota_do_hd_so_com_manifesto,
  drop column hd_arquivado_em,
  drop column hd_volume,
  drop column hd_conferido;

create view armazenamento with (security_invoker = true) as
select coalesce(sum(principal_bytes), 0)::bigint as gravacoes_mac_bytes,
       coalesce(sum(principal_arquivos), 0)::int as gravacoes_mac_arquivos,
       coalesce(sum(bytes), 0)::bigint as material_mac_bytes,
       coalesce(sum(arquivos), 0)::int as material_mac_arquivos,
       (coalesce(sum(principal_bytes), 0) + coalesce(sum(bytes), 0))::bigint as mac_bytes,
       coalesce(sum(principal_hd_bytes), 0)::bigint as hd_bytes,
       coalesce(sum(principal_hd_arquivos), 0)::int as hd_arquivos,
       coalesce(array_agg(video_slug order by video_slug) filter (where principal_hd_arquivos > 0), '{}') as hd_videos,
       (select max(em) from sincronizacoes) as lido_em
from biblioteca_por_video;
comment on view armazenamento is
  'uma linha: gravações da câmera no Mac (videos.gravacao_bytes_no_mac), material e cenas extras no Mac (soma de '
  'biblioteca_arquivos), mac_bytes = as duas; no HD externo (videos.gravacao_arquivados_bytes) e os vídeos que têm '
  'original lá (o painel não mostra o HD desde 25/10, mas a gravação continua contando o que está nele); lido_em = a '
  'última passagem do sincronizador';

revoke all on armazenamento from anon, authenticated, service_role, public;
grant select on armazenamento to service_role;
