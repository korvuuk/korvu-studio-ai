# Fontes do painel

| Arquivo | Família | Pesos | Uso |
|---|---|---|---|
| `Geist-Variable.woff2` | Geist | 100–900 (variável) | toda a interface (`--font-sans`) |
| `GeistMono-Variable.woff2` | Geist Mono | 100–900 (variável) | modelos, IDs, HEX e contagens de tokens (`--font-mono`) |

- Cópias **byte a byte** de `painel/referencias/claude-design/korvu-painel-2026-10-23/fonts/` (o artefato do Claude Design
  do Carlos, 23/10/2026). Versão 1.200, autoria Basement.studio / Andrés Briganti / Mateo Zaragoza para a Vercel.
- **Licença: SIL Open Font License 1.1** — texto completo em `OFL.txt` (copiado do repositório oficial
  github.com/vercel/geist-font). A OFL permite usar, embutir no app e redistribuir junto com ele; não permite vender as
  fontes sozinhas. Mantenha `OFL.txt` ao lado dos arquivos sempre que copiá-los (ex.: para `painel/web`).
- Carregadas pelo `@font-face` de `../tokens.css` (`font-display: swap`).
- O símbolo `⌘` não existe na Geist: aparece na fonte do sistema.
