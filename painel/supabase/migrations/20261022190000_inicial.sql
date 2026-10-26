-- Painel do CONTENT AI — espelho dos arquivos do projeto (os arquivos são a fonte da verdade).
-- Quem escreve: só o sincronizador (painel/sync/sincronizar.py), que apaga e regrava cada tabela inteira.
-- Quem lê: o app Next.js, do lado do servidor, com a chave de serviço. Nenhuma política para anon: RLS fechado.

create table departamentos (
  id text primary key,
  nome text not null,
  ordem int not null,
  descricao text not null,
  gerente_id text
);

create table agentes (
  id text primary key,                 -- nome do arquivo em .claude/agents/ ("diretor" = o Claude principal)
  nome text not null,
  cargo text not null,
  departamento_id text not null references departamentos(id),
  papel text not null check (papel in ('diretor', 'portao', 'construtor', 'analista')),
  resumo text not null,
  personalidade text,
  descricao text,                      -- description do frontmatter
  modelo text,
  ferramentas text[] not null default '{}',
  skills text[] not null default '{}',
  comandos text[] not null default '{}',
  fiscalizado_por text,                -- id do portão que aprova o trabalho dele
  fiscaliza text[] not null default '{}',
  retrato text,                        -- caminho do retrato em painel/public/equipe/
  arquivo text
);

create table videos (
  slug text primary key,
  tema text,
  pilar text,
  estrutura text,
  cta text,
  estado text,
  atualizado text,
  historico jsonb not null default '[]'
);

create table portoes_estado (
  alvo text not null,                  -- videos/<slug> ou 06-publicar/<slug>
  slug text not null,
  portao text not null,
  agente text not null,
  status text not null,                -- aprovado · vencido · bloqueado · escalado · pendente · nao_se_aplica
  motivos jsonb not null default '[]',
  volta int not null default 0,
  primary key (alvo, portao)
);

create table veredictos (
  alvo text not null,
  slug text not null,
  portao text not null,
  agente text not null,
  resultado text not null,
  impressao text not null,
  em timestamptz not null,
  volta int not null,
  s0 int not null, s1 int not null, s2 int not null,
  relatorio text,
  nota text,
  decisao_carlos text,
  primary key (alvo, portao, em)
);

create table fila (
  slug text primary key,
  publicar_em timestamptz,
  plataformas text[] not null default '{}',
  estado text,
  trial text,
  palavra text,
  legado boolean not null default false,
  confirmar boolean
);

create table publicacoes (
  slug text primary key,
  publicado_em timestamptz,
  tema text,
  pilar text,
  palavra text,
  duracao_s numeric,
  trial text,
  permalink_instagram text,
  permalink_facebook text
);

create table metricas (
  slug text not null references publicacoes(slug) on delete cascade,
  lido_em timestamptz not null,
  dias numeric,
  views int, alcance int,
  tempo_medio_s numeric, pct_assistido numeric,
  curtidas int, comentarios int, salvamentos int, compartilhamentos int,
  plays_fb int, tempo_medio_fb_s numeric,
  palavra_comentarios int, palavra_directs int,
  suspeito boolean not null default false,  -- número que a API devolveu impossível (ex.: tempo médio > duração)
  primary key (slug, lido_em)
);

create table perfil_snapshots (
  lido_em timestamptz primary key,
  seguidores int, seguindo int, posts int,
  janela_dias int,
  alcance int, views int, contas_engajadas int, interacoes int, visitas_perfil int,
  alcance_seguidores int, alcance_nao_seguidores int,
  fb_seguidores int
);

create table perfil_demografia (
  lido_em timestamptz not null references perfil_snapshots(lido_em) on delete cascade,
  publico text not null,               -- seguidores · alcancados
  dimensao text not null,              -- country · city · age · gender
  chave text not null,
  valor int not null,
  primary key (lido_em, publico, dimensao, chave)
);

create table sincronizacoes (
  em timestamptz primary key default now(),
  resumo jsonb not null
);

alter table departamentos enable row level security;
alter table agentes enable row level security;
alter table videos enable row level security;
alter table portoes_estado enable row level security;
alter table veredictos enable row level security;
alter table fila enable row level security;
alter table publicacoes enable row level security;
alter table metricas enable row level security;
alter table perfil_snapshots enable row level security;
alter table perfil_demografia enable row level security;
alter table sincronizacoes enable row level security;
