-- Câmbio do custo de IA (decisão do Carlos, 23/10, docs/decisoes.md §5: o custo de IA aparece sempre em libras).
-- O banco continua a guardar o custo em US$ (o preço de tabela da API é a fonte); esta tabela traz a taxa registrada
-- para a tela converter e mostrar qual usou. Fonte: painel/cambio.yaml (do Carlos, como o equipe.yaml), uma linha por
-- data de referência — atualizar = acrescentar uma linha no arquivo, sem mexer em código. O sincronizador regrava a
-- tabela inteira a cada passagem; arquivo ausente ou valor inválido = "✗" e nada gravado.

create table cambio (
  moeda text not null check (moeda ~ '^[A-Z]{3}$' and moeda <> 'USD'),  -- ex.: GBP
  data date not null,                                                   -- data de referência da taxa
  valor numeric(12,6) not null check (valor > 0),                       -- unidades da moeda por 1 US$
  fonte text not null check (btrim(fonte) <> ''),                       -- ex.: XE, média de mercado
  primary key (moeda, data)
);
comment on table cambio is
  'Taxa de câmbio do custo de IA (moeda por 1 US$), espelho de painel/cambio.yaml. A tela usa a mais recente da moeda '
  'e mostra qual usou; o custo guardado continua em US$.';

alter table cambio enable row level security;
revoke all on cambio from anon, authenticated, service_role, public;
grant select on cambio to service_role;
