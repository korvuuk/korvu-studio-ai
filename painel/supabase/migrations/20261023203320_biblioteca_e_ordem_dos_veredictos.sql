-- Biblioteca (tela aprovada no design, painel/design/telas/biblioteca.md) e a chave dos veredictos (PD20).
--
-- 1. PD20 — veredictos tinha chave (alvo, portao, em), e `em` vem do scripts/portoes.py com resolução de segundo: dois
--    veredictos do mesmo portão no mesmo segundo davam chave repetida e TODA passagem falhava até alguém mexer no livro.
--    A chave passa a ser (alvo, ordem): `ordem` = a posição do veredicto no portoes.json do alvo (0, 1, 2…; o livro só
--    acrescenta no fim), que é única e é a ordem real, mesmo dentro de um segundo. O portoes.py não muda.
--
-- 2. Biblioteca — o índice dos materiais dos vídeos, lido do disco (só a listagem e o stat: nada é aberto):
--    biblioteca_arquivos   uma linha por arquivo de videos/<slug>/material/** e videos/<slug>/brutos/extras/**
--                          (fora: pastas de vídeo que começam com "_" ou ".", como _teste-* e _modelo; nomes ocultos
--                          em qualquer nível — .DS_Store, ._*, .gitkeep; arquivos de 0 byte);
--    biblioteca_materiais  o "material lógico" (regra da designer): cada PDF de material/ com o material/_fonte/ dele,
--                          o dossiê (dossie.md + fontes.json), cada subpasta de material/, os soltos da raiz de
--                          material/ e as cenas extras (brutos/extras/). Quem adicionou é INFERIDO pela pasta.
--    biblioteca_referencias  contagem de arquivos de 00-marca/referencias/ e painel/referencias/ (fora do "Todos");
--    biblioteca_mais_utilizados  o uso pela regra do pipeline (não um registro de uso).
--    Os totais são views sobre biblioteca_arquivos, para nunca divergirem dela. Tudo regravado inteiro a cada passagem.

-- ── 1. PD20
alter table veredictos add column ordem int;
update veredictos v set ordem = x.n
  from (select alvo, portao, em, row_number() over (partition by alvo order by em, portao) - 1 as n
        from veredictos) x
  where v.alvo = x.alvo and v.portao = x.portao and v.em = x.em;
alter table veredictos alter column ordem set not null,
  add constraint veredictos_ordem_positiva check (ordem >= 0);
alter table veredictos drop constraint veredictos_pkey, add primary key (alvo, ordem);
comment on column veredictos.ordem is
  'posição do veredicto no portoes.json do alvo (0 = o mais antigo); com o alvo, é a chave (PD20: em tem resolução de segundo)';

-- ── 2. Biblioteca
create table biblioteca_materiais (
  id text primary key,                            -- <slug>:pdf:<arquivo.pdf> · <slug>:dossie · <slug>:pasta:<nome> ·
                                                  -- <slug>:extras · <slug>:soltos
  video_slug text not null references videos (slug),
  grupo text not null check (grupo in ('pdf', 'dossie', 'pasta', 'extras', 'soltos')),
  nome text not null,                             -- "50 comandos de aprendizado", "trechos do YouTube", "cenas extras"…
  caminho text not null,                          -- onde está, relativo à raiz (o PDF, ou a pasta do material)
  quem_adicionou_inferido text,                   -- INFERIDO pela pasta (o arquivo não guarda autor): id de agente de
                                                  -- painel/equipe.yaml, 'carlos' (gravação de tela) ou NULL
  miniatura text,                                 -- CAMINHO do arquivo candidato (a prévia do PDF, a 1.ª imagem, o 1.º
                                                  -- vídeo); a imagem não é gerada aqui
  obra_estudo boolean not null                    -- material/obra/: cópia de estudo, nunca publicada (CLAUDE.md regra 4)
);
create index biblioteca_materiais_video on biblioteca_materiais (video_slug);

create table biblioteca_arquivos (
  caminho text primary key,                       -- relativo à raiz do projeto
  material_id text not null references biblioteca_materiais (id),
  video_slug text not null references videos (slug),
  area text not null check (area in ('material', 'brutos/extras')),
  extensao text not null,                         -- em minúsculas, com o ponto (".mp4"); "" sem extensão
  tipo text not null check (tipo in ('video', 'imagem', 'documento', 'pesquisa', 'audio', 'outros')),
  bytes bigint not null check (bytes > 0),
  modificado_em timestamptz not null,             -- mtime do arquivo
  data_suspeita boolean not null,                 -- mtime mais de 30 dias antes da data do slug (como na gravação)
  obra_estudo boolean not null                    -- está em material/obra/
);
create index biblioteca_arquivos_material on biblioteca_arquivos (material_id);
create index biblioteca_arquivos_video on biblioteca_arquivos (video_slug);

create table biblioteca_referencias (
  pasta text primary key,                         -- 00-marca/referencias · painel/referencias
  arquivos int not null check (arquivos >= 0),    -- arquivos não ocultos, em qualquer nível
  bytes bigint not null check (bytes >= 0)
);

create table biblioteca_mais_utilizados (
  arquivo text primary key,                       -- o ativo, relativo à raiz
  nome text not null,
  usos int not null check (usos >= 0),
  unidade text not null,                          -- "roteiros", "vídeos gravados", "PDFs da palavra"
  regra text not null,                            -- de onde vem o número (a regra do pipeline, não um registro de uso)
  arquivo_existe boolean not null
);

-- Cada material com os seus totais (o cartão): a soma dos arquivos, e no PDF só o(s) .pdf; a data = a do arquivo mais
-- novo; quantos de cada tipo.
create view biblioteca_materiais_resumo with (security_invoker = true) as
select m.id, m.video_slug, m.grupo, m.nome, m.caminho, m.quem_adicionou_inferido, m.miniatura, m.obra_estudo,
       count(a.caminho)::int as arquivos,
       (case when m.grupo = 'pdf' then coalesce(sum(a.bytes) filter (where a.extensao = '.pdf'), 0)
             else coalesce(sum(a.bytes), 0) end)::bigint as bytes,
       max(a.modificado_em) as modificado_em,
       coalesce(bool_or(a.data_suspeita), false) as data_suspeita,
       (count(*) filter (where a.tipo = 'video'))::int as n_video,
       (count(*) filter (where a.tipo = 'imagem'))::int as n_imagem,
       (count(*) filter (where a.tipo = 'documento'))::int as n_documento,
       (count(*) filter (where a.tipo = 'pesquisa'))::int as n_pesquisa,
       (count(*) filter (where a.tipo = 'audio'))::int as n_audio,
       (count(*) filter (where a.tipo = 'outros'))::int as n_outros
from biblioteca_materiais m
left join biblioteca_arquivos a on a.material_id = m.id
group by m.id;

-- Por tipo: sempre os 6 tipos, também com zero (Áudio 0).
create view biblioteca_por_tipo with (security_invoker = true) as
select t.tipo, t.ordem, count(a.caminho)::int as arquivos, coalesce(sum(a.bytes), 0)::bigint as bytes
from (values ('video', 1), ('imagem', 2), ('documento', 3), ('pesquisa', 4), ('audio', 5), ('outros', 6)) as t (tipo, ordem)
left join biblioteca_arquivos a on a.tipo = t.tipo
group by t.tipo, t.ordem;

-- Por vídeo: material + cenas extras, e ao lado as gravações da câmera (brutos/principal/, de videos.gravacao_*).
create view biblioteca_por_video with (security_invoker = true) as
select v.slug as video_slug, count(a.caminho)::int as arquivos, coalesce(sum(a.bytes), 0)::bigint as bytes,
       v.gravacao_arquivos as principal_arquivos, v.gravacao_bytes as principal_bytes
from videos v
left join biblioteca_arquivos a on a.video_slug = v.slug
group by v.slug, v.gravacao_arquivos, v.gravacao_bytes;

alter table biblioteca_materiais enable row level security;
alter table biblioteca_arquivos enable row level security;
alter table biblioteca_referencias enable row level security;
alter table biblioteca_mais_utilizados enable row level security;
revoke all on biblioteca_materiais, biblioteca_arquivos, biblioteca_referencias, biblioteca_mais_utilizados,
  biblioteca_materiais_resumo, biblioteca_por_tipo, biblioteca_por_video
  from anon, authenticated, service_role, public;
grant select on biblioteca_materiais, biblioteca_arquivos, biblioteca_referencias, biblioteca_mais_utilizados,
  biblioteca_materiais_resumo, biblioteca_por_tipo, biblioteca_por_video to service_role;
