-- 25/10 (coordenação): os dois textos da maquete aprovada que faltavam no banco (painel/design/telas/biblioteca.html).
-- 1. A frase de cada cartão de look: looks.descricao = o desc: do item na seção looks do painel/biblioteca.yaml. O nome
--    do yaml vence o "nome" do .json do look quando existe (o .json inteiro continua em looks.ficha).
-- 2. A nota do HD ("os originais 4K … copiados e conferidos em 24 out"), lida do brutos/principal/ARQUIVADO.json de cada
--    vídeo, sem texto fixo: videos.hd_arquivado_em (arquivado_em → UTC), hd_volume (destino.volume) e hd_conferido (todo
--    arquivo do manifesto tem sha256). Sem ARQUIVADO.json = NULL. A view armazenamento ganha, no fim, a data mais recente
--    e se todos os vídeos no HD foram conferidos.

alter table looks
  add column descricao text check (descricao is null or btrim(descricao) <> '');
comment on column looks.descricao is
  'a frase do cartão: o desc: do item deste cartão na seção looks do painel/biblioteca.yaml; sem item = NULL';
comment on column looks.nome is
  'o nome do cartão: o nome: do item na seção looks do biblioteca.yaml; sem ele, o "nome" do .json do look (que fica '
  'sempre na ficha); vlog sem item = NULL';

alter table videos
  add column hd_arquivado_em timestamptz,
  add column hd_volume text check (hd_volume is null or btrim(hd_volume) <> ''),
  add column hd_conferido boolean,
  add constraint videos_nota_do_hd_so_com_manifesto
    check (hd_conferido is not null or (hd_arquivado_em is null and hd_volume is null));
comment on column videos.hd_arquivado_em is
  'o arquivado_em do brutos/principal/ARQUIVADO.json (ISO com fuso → UTC, até o segundo); NULL = sem manifesto ou sem o campo';
comment on column videos.hd_volume is 'o destino.volume do ARQUIVADO.json (o HD externo); NULL = sem manifesto ou sem o campo';
comment on column videos.hd_conferido is
  'todo arquivo do ARQUIVADO.json tem sha256 de 64 hex (a prova da cópia); NULL = sem manifesto. O sincronizador recusa '
  'o manifesto sem sha256 (✗), então é true sempre que há manifesto legível';

create or replace view armazenamento with (security_invoker = true) as
select coalesce(sum(principal_bytes), 0)::bigint as gravacoes_mac_bytes,
       coalesce(sum(principal_arquivos), 0)::int as gravacoes_mac_arquivos,
       coalesce(sum(bytes), 0)::bigint as material_mac_bytes,
       coalesce(sum(arquivos), 0)::int as material_mac_arquivos,
       (coalesce(sum(principal_bytes), 0) + coalesce(sum(bytes), 0))::bigint as mac_bytes,
       coalesce(sum(principal_hd_bytes), 0)::bigint as hd_bytes,
       coalesce(sum(principal_hd_arquivos), 0)::int as hd_arquivos,
       coalesce(array_agg(video_slug order by video_slug) filter (where principal_hd_arquivos > 0), '{}') as hd_videos,
       (select max(em) from sincronizacoes) as lido_em,
       (select max(hd_arquivado_em) from videos where gravacao_arquivados > 0) as hd_arquivado_em,
       (select bool_and(hd_conferido) from videos where gravacao_arquivados > 0) as hd_todos_conferidos
from biblioteca_por_video;
comment on view armazenamento is
  'uma linha: gravações da câmera no Mac (videos.gravacao_bytes_no_mac), material e cenas extras no Mac (soma de '
  'biblioteca_arquivos), mac_bytes = as duas; no HD externo (videos.gravacao_arquivados_bytes) e os vídeos que têm '
  'original lá (hd_videos); hd_arquivado_em = o arquivado_em mais recente desses vídeos e hd_todos_conferidos = todos '
  'com sha256 (NULL = nada no HD); lido_em = a última passagem do sincronizador';

revoke all on armazenamento from anon, authenticated, service_role, public;
grant select on armazenamento to service_role;
