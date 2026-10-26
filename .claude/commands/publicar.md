---
description: Coloca um pacote pronto na fila de publicação (IG + FB) — o publicador escreve legendas, hooks e agenda
argument-hint: <slug> [data/hora opcional] [só instagram|facebook]
---

Pedido: **$ARGUMENTS**

1. Confirmar com o Carlos que quer publicar **<slug>** (mover para `06-publicar/` = autorização). Se ele já disse isso nesta mensagem, seguir.
2. Mover `05-render-pronto/<slug>/` → `06-publicar/<slug>/`.
3. Usar o subagente **publicador** (legendas IG/FB, hooks, agendamento, `post.json → material = {palavra, arquivo, titulo, url: null}` com o PDF). Se foi pedida data/hora ou só uma plataforma, passar isso ao `post.json`.
4. **PORTÃO-PUBLICACAO** — subagente **portao-publicacao** sobre `06-publicar/<slug>/` depois do `agendar` (GAUNTLET, `docs/gauntlet.md`: roda sozinho, sem perguntar; BLOQUEADO → o construtor corrige os S0/S1 e volta ao mesmo portão, até 3 voltas; nada chega ao Carlos antes do APROVADO). **Sem ele APROVADO o `publicar.py` não publica.** Cada pasta da fila (par A/B, variantes) tem o seu portão.
5. Com o APROVADO, mostrar: data/hora, plataformas, legendas e se o post vai pedir confirmação (primeiros posts). Se o Carlos editar legenda, capa ou post depois, o portão roda de novo antes da hora (o veredicto vence sozinho).
