---
description: Renderiza o vídeo final — corte, revisão, cor, legendas/títulos/animações, áudio, capa, QA e pacote em 05-render-pronto
argument-hint: <slug>
---

Vídeo: **$ARGUMENTS**. Exige `edicao/edl.json` com `"aprovado": true` — senão parar e pedir aprovação (/editar).

Etapas (parar e reportar se qualquer uma falhar):
1. **Corte** — subagente **editor-de-video**: `render_corte.py` → `verify.py` → filmstrips. Estado `revisao`.
2. **Legendas** — `uv run python .claude/skills/legendas-animadas/scripts/gerar_props.py videos/<slug>` (gera `legendas.json/.srt` e `reel-props.json`).
3. **Revisão 1** — subagente **revisor-de-video**, passagem 1 (corte + legendas). FAIL → devolver ao editor / corrigir legendas e repetir.
4. **Cor** — subagente **colorista**: `/cor` → `edicao/cor/corte-cor.mp4`. Estado `cor`. (Se ainda não existir LUT aprovado, avisar e seguir sem LUT só com a primária, marcando no relatório.)
5. **Animações** — se houver overlays `animacao`: subagente **animador` confere se cada uma está importada e registrada; se faltar export do Claude Design, gerar o brief e parar esta etapa com placeholder (avisar).
6. **Render Remotion** — `gerar_props.py` de novo (agora apontando para `corte-cor.mp4`) → `render_reel.py` → `edicao/render-remotion.mp4`. Estado `legendas`.
7. **Áudio** — `uv run python .claude/skills/audio-polish/scripts/audio.py videos/<slug>/edicao/render-remotion.mp4 videos/<slug>/edicao/final.mp4` (áudio do `edicao/corte-audio.wav` sem perdas: nivelador leve 1,5:1 → −14 LUFS → true peak −1,5 dBTP → AAC 256k; música: se `videos/<slug>/musica/musica.json` tiver `escolhida`, passar `--musica videos/<slug>/musica/opcao-N.mp3` — ver `/musica`).
   Variantes de hook (L01B/L01C), se gravadas: gerar `edicao/final-L01B.mp4` etc. trocando o segmento do hook.
8. **Capa** — subagente **designer-de-capas** (3 variantes; uma capa própria por variante/publicação). Estado `capa`.
8b. **PORTÃO-IMAGEM** — subagente **portao-imagem** sobre cor + capas + extras (GAUNTLET, `docs/gauntlet.md`: roda sozinho, sem perguntar; BLOQUEADO → o construtor corrige os S0/S1 e volta ao mesmo portão, até 3 voltas; nada chega ao Carlos antes do APROVADO). Só depois o Carlos escolhe a capa.
9. **QA final = PORTÃO-CORTE** — subagente **revisor-de-video**, passagem 2, sobre `final.mp4` e cada variante → `qa/relatorio.md` + `portoes.py registrar` (GAUNTLET, `docs/gauntlet.md`: roda sozinho, sem perguntar; BLOQUEADO → o construtor corrige os S0/S1 e volta ao mesmo portão, até 3 voltas; nada chega ao Carlos antes do APROVADO). Estado `qa`.
10. **Pacote** — `uv run python scripts/montar_pacote.py videos/<slug>` → `05-render-pronto/<slug>/`. Estado `pronto`. O script **recusa** sem os portões pauta (se houve pesquisa), roteiro, imagem e corte APROVADOS e válidos, e sela o pacote. Com palavra-chave, leva **só o PDF** de `material/` (sem PDF o script recusa: rodar o **produtor-de-material** e repetir).
11. **Limpeza** — `uv run python scripts/limpar_video.py videos/<slug> --apagar`: deixa só a revisão mais nova e o que o arquivo final precisa (regra do Carlos: "manter só a atual"). Rodar SEMPRE no fim, e também depois de gerar uma revisão nova fora do `/renderizar`.

No fim — só com os portões APROVADOS (`uv run python scripts/portoes.py estado videos/<slug>`) — mostrar o cartão de entrega (`docs/gauntlet.md`): duração, caminho do pacote, capa escolhida, observações do QA, e lembrar: "para publicar, `/publicar <slug>` (ou mover a pasta para `06-publicar/`)".
