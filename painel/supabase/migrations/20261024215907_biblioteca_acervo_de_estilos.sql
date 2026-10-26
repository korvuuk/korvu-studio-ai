-- Biblioteca nova = o acervo de estilos (decisão do Carlos de 24/10, docs/decisoes.md §5; tela
-- painel/design/telas/biblioteca.md — os nomes seguem os blocos dela). Espelho dos arquivos, regravado inteiro a cada
-- passagem do sincronizador (como as outras tabelas; nada de arquivo histórico aqui):
--   looks                  00-marca/cor/luts/*.json (o topo; _descartadas/ fica fora) + 00-marca/cor/cor.md
--   capa_estilos (+ capa_estilos_exemplos), legenda_estilos, fontes, sistema_ferramentas, modelos_descricao
--                          painel/biblioteca.yaml (crescer = uma linha nova no yaml; um look novo = .cube + .json; uma
--                          animação nova = um brief.md: nada de código nem migração)
--   animacoes              videos/<slug>/animacoes/<Exx>/brief.md (+ o .mp4 que prova a renderização)
--   sistema_contagens      .claude/agents, .claude/skills, .claude/commands
-- e duas views sobre o que o banco já tem: armazenamento (biblioteca_por_video) e sistema_modelos (modelo_por_agente).
-- As tabelas biblioteca_* de 23/10 ficam como estão (a tela nova usa a biblioteca_arquivos só para o armazenamento).
-- As prévias dos looks (painel/previas/looks/) são de outro script, painel/sync/previas_looks.py: o sincronizador só
-- guarda o caminho se o arquivo esperado existe.

create table looks (
  id text primary key check (id in ('vlog', 'rec709') or id ~ '^v[0-9]+$'),
  ordem int not null unique check (ordem >= 0),
  tipo text not null check (tipo in ('referencia', 'base', 'look')),
  nome text,
  papel text check (papel in ('em_uso', 'alternativa', 'arquivado')),
  chaves_cor_md text[] not null,
  linhas_cor_md int[] not null,
  aprovada boolean,
  aprovada_em date,
  criado_em date,
  arquivo_json text,
  ficha jsonb,
  cube text,
  cube_sha256 text check (cube_sha256 ~ '^[0-9a-f]{64}$'),
  rosto_ire numeric check (rosto_ire >= 0 and rosto_ire <= 110),
  rosto_ire_em date,
  rosto_ire_amostra text,
  previa text,
  previa_esperada text,
  constraint looks_tipo_do_id check ((tipo = 'referencia') = (id = 'vlog') and (tipo = 'base') = (id = 'rec709')),
  constraint looks_papel_so_de_look check (papel is null or tipo = 'look'),
  constraint looks_papel_pela_chave check (  -- uma chave = o papel dela; nenhuma ou duas (conflito) = NULL
    (cardinality(chaves_cor_md) = 1) = (papel is not null)
    and (papel is null or chaves_cor_md[1] = case papel when 'em_uso' then 'versao_ativa'
                                                        when 'alternativa' then 'alternativa_medida'
                                                        else 'arquivados' end)),
  constraint looks_uma_linha_por_chave check (cardinality(chaves_cor_md) = cardinality(linhas_cor_md)),
  constraint looks_cube_com_hash check ((cube is null) = (cube_sha256 is null)),
  constraint looks_rosto_com_data check ((rosto_ire is null) = (rosto_ire_em is null)),
  constraint looks_rosto_so_de_look check (rosto_ire is null or tipo = 'look'),
  constraint looks_previa_e_a_esperada check (previa is null or previa = previa_esperada)
);
create unique index looks_um_em_uso on looks (papel) where papel = 'em_uso';
comment on table looks is
  'Os cartões de "looks de cor.": vlog (a amostra 00-marca/cor/amostras/praq0967/praq0967-121.00s.mkv como a câmera '
  'grava), rec709 (luts/entrada-camera.cube) e um por luts/korvu-look-vN.json do topo, pela versão (ordem)';
comment on column looks.papel is
  'do trecho yaml do cor.md: em_uso = versao_ativa; alternativa = alternativa_medida; arquivado = está em arquivados '
  '(24/10: o v4); NULL = nenhuma chave, ou duas ao mesmo tempo (conflito: o sincronizador avisa)';
comment on column looks.chaves_cor_md is
  'as chaves do trecho ```yaml do cor.md que citam a versão, exatamente "vN" (versao_ativa, alternativa_medida, '
  'arquivados); a antiga alternativa não é lida';
comment on column looks.linhas_cor_md is 'o nº da linha do cor.md de cada chave, na mesma ordem';
comment on column looks.aprovada is 'o "aprovada" do .json (o aplicar_cor.py usa a maior versão aprovada)';
comment on column looks.criado_em is 'a data do "criado_em" do .json, como está escrita';
comment on column looks.ficha is 'o .json inteiro (rec709: o entrada-camera.json)';
comment on column looks.rosto_ire is
  'rosto do Carlos em IRE: a ÚNICA medida "rosto <n> IRE" na coluna Decisão das linhas do ## Histórico do cor.md que '
  'citam só esta versão; nenhuma ou várias = NULL';
comment on column looks.rosto_ire_em is 'a coluna Data da linha da medida';
comment on column looks.rosto_ire_amostra is 'a coluna Amostra da linha da medida';
comment on column looks.previa is
  'painel/previas/looks/<id>-<hash>.jpg se o arquivo existe (gerado pelo painel/sync/previas_looks.py), senão NULL';
comment on column looks.previa_esperada is
  'o caminho que a receita pede hoje (hash da receita + amostra + .cube); NULL = sem amostra ou sem .cube';

create table capa_estilos (
  id text primary key check (id ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  ordem int not null unique check (ordem >= 0),
  nome text not null check (btrim(nome) <> ''),
  descricao text not null check (btrim(descricao) <> ''),
  ficha text,
  ficha_existe boolean,
  em_uso boolean not null,
  check ((ficha is null) = (ficha_existe is null))
);
comment on table capa_estilos is 'painel/biblioteca.yaml → capas: um estilo de capa por linha (ordem do yaml)';
comment on column capa_estilos.ficha is 'a ficha do estilo no projeto (ex.: 00-marca/referencias/capas/…), ou NULL';

create table capa_estilos_exemplos (
  estilo_id text not null references capa_estilos (id) deferrable initially deferred,
  ordem int not null check (ordem >= 0),
  slug text not null check (slug ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9]+(-[a-z0-9]+)*$'),
  pasta text check (pasta in ('07-publicados', '06-publicar', '05-render-pronto')),
  caminho text,
  video_slug text,
  primary key (estilo_id, ordem),
  check ((pasta is null) = (caminho is null)),
  check (caminho is null or caminho = pasta || '/' || slug || '/capa/capa.png'),
  check (pasta is not null or video_slug is null)
);
comment on table capa_estilos_exemplos is
  'as capas reais de cada estilo: <pasta>/<slug>/capa/capa.png na 1.ª de 07-publicados, 06-publicar, 05-render-pronto '
  'que a tiver (NULL = não encontrada); video_slug = o vídeo de origem do pacote';

create table legenda_estilos (
  id text primary key check (id ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  ordem int not null unique check (ordem >= 0),
  nome text not null check (btrim(nome) <> ''),
  descricao text not null check (btrim(descricao) <> ''),
  ficha text,
  ficha_existe boolean,
  em_uso boolean not null,
  check ((ficha is null) = (ficha_existe is null))
);
comment on table legenda_estilos is
  'painel/biblioteca.yaml → legendas: um estilo de legenda por linha; a amostra é desenhada pela tela a partir da ficha';

create table fontes (
  familia text primary key check (btrim(familia) <> ''),
  ordem int not null unique check (ordem >= 0),
  remotion text,
  estilo text not null check (estilo in ('normal', 'italico')),
  pesos int[] not null check (cardinality(pesos) > 0 and 100 <= all (pesos) and 1000 >= all (pesos)),
  uso text not null check (btrim(uso) <> ''),
  reserva boolean not null,
  confere_brand_ts boolean,
  check (remotion is not null or confere_brand_ts is null)
);
comment on table fontes is 'painel/biblioteca.yaml → fontes (reserva = só alternativa na pilha; a tela mostra as outras)';
comment on column fontes.remotion is 'o pacote @remotion/google-fonts/<remotion> que o remotion/src/brand.ts importa';
comment on column fontes.confere_brand_ts is
  'o brand.ts importa o pacote e chama o loadFont dele com o mesmo estilo e os mesmos pesos (false = não bate; NULL = '
  'sem brand.ts, sem pacote no yaml ou chamada que não se reconhece)';

create table sistema_ferramentas (
  nome text primary key check (btrim(nome) <> ''),
  ordem int not null unique check (ordem >= 0),
  tipo text not null check (btrim(tipo) <> ''),
  descricao text not null check (btrim(descricao) <> ''),
  versao text,
  versao_de text,
  check (versao is null or versao_de is not null)
);
comment on table sistema_ferramentas is
  'painel/biblioteca.yaml → ferramentas: a stack, lista fixa (24/10: para quem chegar pelo GitHub)';
comment on column sistema_ferramentas.tipo is 'o que a peça é (API, Linguagem, Banco de dados…) — o tipo: do yaml';
comment on column sistema_ferramentas.descricao is 'o que ela faz aqui — o desc: do yaml (desc é palavra reservada no SQL)';
comment on column sistema_ferramentas.versao is
  'lida do arquivo de versao_de (package.json#pacote, config.toml#chave ou a 1.ª linha), nunca escrita à mão; NULL = '
  'sem fonte de versão ou não encontrada';

create table modelos_descricao (
  modelo text primary key check (btrim(modelo) <> ''),
  ordem int not null unique check (ordem >= 0),
  descricao text not null check (btrim(descricao) <> ''),
  com_preco boolean not null
);
comment on table modelos_descricao is
  'painel/biblioteca.yaml → modelos: a frase de cada modelo de IA no Sistema (o desc: do yaml); com_preco = o modelo '
  'está na tabela de preços do sincronizador (sem preço não há consumo: a frase não aparece na sistema_modelos)';

create table animacoes (
  id text primary key,
  video_slug text not null references videos (slug) deferrable initially deferred,
  codigo text not null check (codigo ~ '^E[0-9]+$'),
  titulo text,
  linhas text[] not null,
  modo text check (modo in ('full', 'split', 'card')),
  duracao_s numeric check (duracao_s > 0),
  video_do_brief text,
  renderizada boolean not null,
  mp4 text,
  brief text not null,
  check (id = video_slug || '/' || codigo),
  check (brief = 'videos/' || video_slug || '/animacoes/' || codigo || '/brief.md'),
  check (renderizada = (mp4 is not null))
);
comment on table animacoes is
  'videos/<slug>/animacoes/<Exx>/brief.md: título e linhas do "# Exx — título (L08 + L09)", "- **Vídeo:**", '
  '"- **Modo:**" e a "duração N s" da linha "- **Linha(s):**" (fora do padrão = NULL)';
comment on column animacoes.renderizada is
  'há um .mp4: edicao/extras/<Exx>.mp4, brutos/extras/<Exx>.mp4 ou <Exx>-*.mp4, ou qualquer .mp4 em animacoes/<Exx>/; '
  'false = roteirizada';
comment on column animacoes.mp4 is 'o .mp4 que prova a renderização (o 1.º na ordem acima)';
comment on column animacoes.video_do_brief is 'o slug escrito no brief (difere de video_slug = aviso do sincronizador)';

create table sistema_contagens (
  unico boolean primary key default true check (unico),
  agentes int not null check (agentes >= 0),
  habilidades int not null check (habilidades >= 0),
  comandos int not null check (comandos >= 0)
);
comment on table sistema_contagens is
  'uma linha: agentes = .md no topo de .claude/agents/; habilidades = pastas do topo de .claude/skills/ com SKILL.md; '
  'comandos = .md no topo de .claude/commands/; nome começado por "." ou "_" fica fora';

-- Armazenamento: os totais da Biblioteca por cima do que já existe (biblioteca_por_video = videos.gravacao_*_no_mac,
-- videos.gravacao_arquivados_* e a soma de biblioteca_arquivos por vídeo). Bytes decimais: a tela divide por 10^9.
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
  'original lá; lido_em = a última passagem do sincronizador';

-- Sistema · modelos: a mistura dos 30 dias, por modelo, somando a modelo_por_agente — os mesmos números da Equipe e de
-- Tokens (o consumo da janela inteira: todo membro é um agente de agentes).
create view sistema_modelos with (security_invoker = true) as
select m.modelo, m.modelo_nome, m.tokens, 100.0 * m.tokens / nullif(sum(m.tokens) over (), 0) as pct_tokens,
       m.usd, m.execucoes, m.agentes, d.descricao
from (select modelo, modelo_nome, sum(tokens)::bigint as tokens, sum(usd) as usd, sum(execucoes)::int as execucoes,
             count(*)::int as agentes
      from modelo_por_agente
      where modelo is not null
      group by modelo, modelo_nome) m
left join modelos_descricao d on d.modelo = m.modelo;
comment on view sistema_modelos is
  'por modelo, nos 30 dias UTC até hoje (a janela da modelo_por_agente): tokens, pct_tokens (% do total da janela, '
  'somam 100), usd, execucoes, quantos agentes o usaram e a frase do biblioteca.yaml (descricao; NULL = sem frase)';

alter table looks enable row level security;
alter table capa_estilos enable row level security;
alter table capa_estilos_exemplos enable row level security;
alter table legenda_estilos enable row level security;
alter table fontes enable row level security;
alter table sistema_ferramentas enable row level security;
alter table modelos_descricao enable row level security;
alter table animacoes enable row level security;
alter table sistema_contagens enable row level security;

revoke all on looks, capa_estilos, capa_estilos_exemplos, legenda_estilos, fontes, sistema_ferramentas,
  modelos_descricao, animacoes, sistema_contagens, armazenamento, sistema_modelos
  from anon, authenticated, service_role, public;
grant select on looks, capa_estilos, capa_estilos_exemplos, legenda_estilos, fontes, sistema_ferramentas,
  modelos_descricao, animacoes, sistema_contagens, armazenamento, sistema_modelos to service_role;
