# Button

Botões de 36px de altura, raio `radius-btn` (8px), label em `small` semibold.

| Variante | Classe | Quando |
|---|---|---|
| Primary | `k-btn k-btn-primary` | Uma ação principal por vista (Novo vídeo, Aprovar e agendar). Fundo `accent`, texto `on-accent` (#111). |
| Secondary | `k-btn k-btn-secondary` | Ações de apoio (Exportar, Pedir ajustes). `surface` + borda `line-strong`. |
| Ghost | `k-btn k-btn-ghost` | Ações terciárias e cancelar. Texto `ink-2`. |
| Dark | `k-btn k-btn-dark` | Confirmação de portão — decisão do Carlos. |
| Icon | `+ k-btn-icon` | Ícone 16px sem texto; dê sempre `aria-label`. |

- O consumidor fornece: o texto, um ícone opcional (`<span data-icon="…" data-size="16">`).
- Texto branco sobre o laranja **não é permitido** (3.3:1); use sempre `on-accent`.
- `k-btn-sm` (28px) só em tabelas e toolbars densas.
