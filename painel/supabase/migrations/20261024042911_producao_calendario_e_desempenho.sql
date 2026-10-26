-- Produção (Roteiros e Prontos), Calendário (vagas), nome curto, Desempenho (toques e perfil por dia) e o original
-- arquivado fora do Mac (24/10). Tudo lido de arquivo do projeto, só lendo; as tabelas são regravadas inteiras a cada
-- passagem (os defaults só servem às linhas de agora e saem logo).

-- ── videos: Roteiros, nome curto e gravação arquivada
alter table videos
  add column tem_roteiro boolean not null default false,    -- videos/<slug>/roteiro.json existe
  add column roteiro_versao int,                            -- roteiro.json → versao
  add column cta_palavra text,                              -- roteiro.json → cta_palavra (NULL: CTA sem palavra)
  add column roteiro_extras int check (roteiro_extras >= 0),-- len(roteiro.json → extras): as cenas extras planejadas
  add column gravacao_prevista date,                        -- a data do slug (AAAA-MM-DD-…), a gravação prevista
  add column nome_curto text not null default '',           -- regra do corte: tema antes de " — "; sem tema, o slug
  add column gravacao_arquivados int not null default 0 check (gravacao_arquivados >= 0),
  add constraint videos_roteiro_so_com_roteiro check (tem_roteiro or (roteiro_versao is null and roteiro_extras is null
                                                                    and cta_palavra is null)),
  add constraint videos_arquivados_dentro check (gravacao_arquivados <= gravacao_arquivos);
alter table videos alter column tem_roteiro drop default, alter column nome_curto drop default,
  alter column gravacao_arquivados drop default;
comment on column videos.nome_curto is
  'título curto para as telas: videos.tema (do tracker) antes do primeiro " — ", sem espaços nas pontas; tema vazio ou '
  'ausente = o slug sem a data, com espaço no lugar do hífen (a regra que o front fazia em formato.ts → tituloVideo)';
comment on column videos.gravacao_arquivados is
  'quantos dos gravacao_arquivos vêm do brutos/principal/ARQUIVADO.json (originais fora do Mac, no HD externo)';

-- ── Prontos: 05-render-pronto/<slug>/pacote.json
create table prontos (
  slug text primary key,                                    -- a pasta em 05-render-pronto/
  video_slug text not null,                                 -- o vídeo de origem (a mesma regra da fila)
  qa text,                                                  -- pacote.json → qa ("PASS" = pronto; videos.pronto)
  duracao numeric check (duracao > 0),                      -- pacote.json → duracao (segundos)
  criado_em timestamptz,                                    -- pacote.json → criado_em
  cta_palavra text                                          -- pacote.json → cta_palavra
);

-- ── Calendário: o bloco vagas_semanais do _controle/calendario.md
create table calendario_vagas (
  dia_semana smallint not null check (dia_semana between 1 and 7),  -- ISO: 1 = segunda … 7 = domingo
  dia text not null,                                        -- segunda · terca · quarta · quinta · sexta · sabado · domingo
  hora time not null,                                       -- hora local
  fuso text not null,                                       -- o fuso do bloco (fuso:), padrão Europe/London como o publicar.py
  primary key (dia_semana, hora)
);

-- ── Desempenho
alter table perfil_snapshots add column toques_links_perfil int check (toques_links_perfil >= 0);
comment on column perfil_snapshots.toques_links_perfil is
  'instagram.metricas_conta.profile_links_taps (janela do snapshot). Pela Meta: toques nos botões de endereço, ligação, '
  'e-mail e mensagem do perfil — não é o link da bio';

create table perfil_diario (
  dia date not null,                                        -- o dia (UTC) a que o valor se refere
  metrica text not null,                                    -- reach, views, …, seguidores
  valor bigint not null check (valor >= 0),
  lido_em timestamptz not null,                             -- quando o perfil.py leu
  primary key (dia, metrica)
);
comment on table perfil_diario is
  'Uma linha por dia × métrica, de _controle/perfil/diario/AAAA-MM-DD.json (proposta: o perfil.py ainda não grava). '
  'Pasta ausente = tabela vazia.';

-- ── Produção · Roteiros numa view só: o que vem do roteiro e o que a Biblioteca já conta (sem contar de novo)
create view videos_producao with (security_invoker = true) as
select v.slug, v.nome_curto, v.estado, v.atualizado, v.tem_roteiro, v.roteiro_versao, v.cta_palavra,
       v.roteiro_extras, coalesce(x.arquivos, 0) as extras_arquivos,
       p.caminho is not null as pdf, p.caminho as pdf_caminho,
       v.gravacao_prevista, v.gravado, v.pronto
from videos v
left join biblioteca_materiais_resumo x on x.video_slug = v.slug and x.grupo = 'extras'
left join lateral (select min(m.caminho) as caminho from biblioteca_materiais m
                   where m.video_slug = v.slug and m.grupo = 'pdf') p on true;

alter table prontos enable row level security;
alter table calendario_vagas enable row level security;
alter table perfil_diario enable row level security;
revoke all on prontos, calendario_vagas, perfil_diario, videos_producao from anon, authenticated, service_role, public;
grant select on prontos, calendario_vagas, perfil_diario, videos_producao to service_role;
