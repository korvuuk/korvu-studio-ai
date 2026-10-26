-- Data da gravação: a câmera do Carlos grava os .MOV com o relógio em 2024 (mtime e data de criação dos PRAQ*.MOV =
-- jul/ago 2024; ctime = o dia em que entraram no projeto, set/out 2026). videos.gravacao_ultima (a data do próprio
-- arquivo) fica como está e ganha: gravacao_chegou = o ctime mais recente (quando o arquivo entrou ou mudou no disco do
-- projeto) e gravacao_data_suspeita = a data do arquivo é mais de 30 dias anterior à data do slug (a gravação prevista).
-- Dado suspeito se marca, não se esconde. Tabela regravada inteira: os defaults saem logo.

alter table videos
  add column gravacao_chegou timestamptz,
  add column gravacao_data_suspeita boolean not null default false,
  add constraint videos_chegou_so_com_gravacao check (gravado or gravacao_chegou is null);
alter table videos alter column gravacao_data_suspeita drop default;
comment on column videos.gravacao_ultima is
  'data de modificação mais recente dos vídeos de brutos/principal/ (a do arquivo: vem do relógio da câmera)';
comment on column videos.gravacao_chegou is
  'ctime mais recente desses arquivos: quando entraram (ou mudaram) no disco do projeto; NULL sem gravação';
comment on column videos.gravacao_data_suspeita is
  'gravacao_ultima é mais de 30 dias anterior à data do slug (relógio da câmera errado): não mostrar como data da gravação';
