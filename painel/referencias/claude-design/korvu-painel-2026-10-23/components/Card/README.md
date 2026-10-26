# Card

Contentor base de todo o painel: `k-card`.

- Fundo `surface` (um passo mais claro que `bg`), borda **1px `line`**, raio `radius-card` (12px), sombra `shadow-card` quase invisível.
- Clicável: acrescente `is-interactive`; o hover troca a borda para `line-strong` e a sombra para `shadow-hover`. Sem escala, sem mudança de cor de fundo.
- Padding padrão `space-24` (`k-pad`); cards densos usam 16–20px.
- Cabeçalho: `k-card-head` com `k-card-title` (15px/600) à esquerda e ação ou caption à direita.
- Nunca: bordas coloridas à esquerda, gradientes, sombras fortes, cards dentro de cards.
