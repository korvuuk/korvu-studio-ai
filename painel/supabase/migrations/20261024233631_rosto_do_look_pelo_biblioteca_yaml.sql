-- 25/10 (decisão da coordenação): o rosto do Carlos em IRE de cada look sai da seção `looks` do painel/biblioteca.yaml
-- (id, rosto_ire, medido_em, amostra, fonte = arquivo:linhas de onde veio o número; formato em docs/contratos.md §12).
-- A leitura da tabela ## Histórico do 00-marca/cor/cor.md por regex saiu: todos os looks pelo mesmo lugar. Só os
-- comentários das colunas mudam (o tipo e as constraints ficam como na 20261024215907).

comment on column looks.rosto_ire is
  'rosto do Carlos em IRE: o rosto_ire do item deste look na seção looks do painel/biblioteca.yaml; look sem item = NULL';
comment on column looks.rosto_ire_em is 'o medido_em do item (a data da medição, não a do look)';
comment on column looks.rosto_ire_amostra is 'a amostra do item (o arquivo ou corte medido), ou NULL';
