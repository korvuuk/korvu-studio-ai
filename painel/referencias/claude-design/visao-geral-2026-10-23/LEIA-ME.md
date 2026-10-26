# Visão geral — maquete aprovada pelo Carlos (23/10)

- **Origem:** canvas do Claude Design "korvu. painel — Visão geral", https://claude.ai/artifact/9vtqDX3tQ4CCwGWYLaQAQ4
  (versão 1792762806-b0a9), feito sobre o design system "korvu. painel" (cópia em `../korvu-painel-2026-10-23/`).
- **Aprovação:** "Approved. Take the Visão geral mockup into painel/design/ through the designer-de-produto agent and
  run it through the PORTÃO-INTERFACE gate." (23/10)
- `visao-geral.dc.html` = a fonte exata do artboard (formato Design Component: `<x-dc>`, `<sc-for>`, `{{ }}`,
  classe `Component`). Não abre sozinho no navegador; é referência de layout, medidas e dados. Usa as classes
  `k-*` do `components/bundle.css` e define os tokens em `:root`.
- Artboard 1920×1080 (16:9), desktop. Sidebar 208, topbar 64, padding 32, grade de 12 colunas (gutter 24).
- **Imagens** (no canvas são assets `/_blob/…`): retratos = `painel/web/src/app/equipe/img equipe/*.png` reduzidos a
  512×512; capas = `06-publicar/<slug>/capa/capa.png` e `07-publicados/2026-09-17-demis-hassabis/capa/capa.png`.

## De onde vem cada dado
| Bloco | Fonte | Real? |
|---|---|---|
| Seguidores 3.631, alcance 529, 2.448 visualizações, 56 visitas ao perfil | `_controle/perfil/2026-10-22.json` (`instagram.conta`, `metricas_conta`) | sim |
| Fora da bolha 60 % (307 de 513) | `metricas_conta.reach_por_follow_type` (NON_FOLLOWER / soma) | sim |
| Melhor vídeo: Demis Hassabis, 338 alcance, 450 visualizações, 13 out | `instagram.posts[].insights` | sim |
| Deltas +2,4 % · +12,1 % · +8,3 % | pedido do Carlos | **sem fonte no projeto** |
| Próximas publicações (data, hora, Instagram, Trial × Normal) | `06-publicar/*/post.json` (`publicar_em`, `plataformas`, `instagram.trial`) | sim |
| Curva diária de visualizações | o snapshot só tem o total de 28 dias; a forma segue as datas dos posts | **exemplo** |
| Top 10 países (Quem segue · Quem os vídeos alcançam) | `demografia.follower_demographics.country` / `reached_audience_demographics.country` | sim |
| Tokens 248K, GPT-4o 42 %, Claude 28 %, GPT-4.1 18 %, Imagens 8 %, Outros 4 %, £ 12,40 | pedido do Carlos | **sem fonte no projeto** |
| Equipe (nome, função, departamento, portão, modelo) | `painel/equipe.yaml` + `model:` de `.claude/agents/*.md` | sim |
| Status "Trabalhando agora / Em espera", 3 notificações | — | **exemplo** |
