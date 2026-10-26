# Como usar o estúdio de Reels (Korvu)

## O dia a dia em 6 comandos
| Passo | Você faz | Comando |
|---|---|---|
| 1. Ideia | pede sugestões (opcional) | `/ideias` |
| 2. Roteiro | manda o tema | `/novo-video você tá usando o ChatGPT errado` |
| 3. Gravação | cola `videos/<slug>/monitor-chatgpt.txt` no **ChatGPT Voz** e diz "começar": ele lê cada linha, você repete para a câmera, e ele diz "de novo" quando você errar (sem fones — o editor remove a voz da IA; telemóvel a ≥ 1,5 m do microfone, voz do ChatGPT bem diferente da sua, ~1 s de silêncio entre as falas); ou lê pelo `teleprompter.txt`. Você falando → `brutos/principal/`, cenas extras → `brutos/extras/` | — |
| 4. Edição | pede a edição e aprova a EDL ("aprovado" ou "L05 usa T1") | `/editar <slug>` |
| 5. Finalização | corte + revisão + cor + legendas + animações + capa + QA → pacote em `05-render-pronto/<slug>/` | `/renderizar <slug>` |
| 6. Publicação | manda para a fila; o publicador escreve legendas/hooks e agenda IG + FB | `/publicar <slug>` · `/fila` |

`/status` mostra em que etapa está cada vídeo.

## Onde soltar os arquivos (todo vídeo = principal + cenas extras)
- **Vídeo principal** (você falando): `videos/<slug>/brutos/principal/` → `camera-01.mov`, `camera-02.mov`… (+ `camera-00-cor.mov`)
- **Cenas extras**: `videos/<slug>/brutos/extras/` → comece o nome pelo ID da tabela "Cenas extras" do roteiro: `E01-chatgpt.mov`, `E02-print.png`, `E03-noticia.mp4`, `E04-maos.mov`…
- `/extras <slug>` mostra o que falta, tira prints automáticos de notícias e prepara os briefs de animação para o Claude Design.
- **Câmera (Lumix S5IIX):** V-Log · 4K **25p** · 4:2:2 **10-bit** (MOV LongGOP, ou ProRes 422 HQ no SSD) · obturador **1/50** · ISO base (640 ou 4000) · balanço de branco **fixo** (5600K ou personalizado na folha branca — nunca AWB) · expor o V-Log ~+0,5 a +1 stop (pele ~50–55 IRE no waveform; use o "V-Log View Assist" só para monitorar) · ativar "Vertical Position Info".
- **Primeira gravação de cada dia/luz:** 5 s segurando uma folha branca A4 perto do rosto + 5 s parado olhando a câmera → `camera-00-cor.mov` (só para o colorista).
- **Celular:** vertical, 25 ou 30 fps, HDR desligado. **Ecrã:** qualquer fps (é convertido para 25).
- LUT oficial Panasonic (opcional, melhora a conversão V-Log → Rec.709): baixe "V-Log to V-709" no site da Panasonic e coloque em `00-marca/cor/luts/panasonic/`.

## O que você ainda precisa colocar nas pastas
| O quê | Onde |
|---|---|
| Imagem de referência da legenda (a que você mandou no chat) | `00-marca/referencias/legendas/referencia-01.jpg` |
| Guideline / design system | `00-marca/design-system/` |
| Referências de cor (frames/imagens com o look desejado) | `00-marca/cor/referencias/` |
| LUT de entrada da câmera, se gravar em log (ex.: V-Log → V-709 da Panasonic) | `00-marca/cor/luts/entrada-camera.cube` |
| Amostras de voz (3–5 min falando livre + 1 min lendo) | `02-calibracao/amostras/` → depois `/calibrar-voz` |
| Logo e músicas licenciadas | `00-marca/assets/` |

## Chaves (arquivo `.env`, copie de `.env.example`)
- `ELEVENLABS_API_KEY` — transcrição de alta qualidade (sem ela, usa o modelo local `mlx`).
- Tokens Meta/R2 — os mesmos da Korvu + `META_PAGE_ID` / `META_PAGE_ACCESS_TOKEN` da Página do Facebook.

## Ver vídeos ("olhos" do Claude)
`/watch <arquivo ou link> <pergunta>` — o Claude extrai frames + transcrição e assiste. Ex.: `/watch https://www.instagram.com/reel/... como é a legenda desse reel?`

## Instalar a publicação automática (depois de testar)
`bash scripts/launchd/instalar.sh` — roda a fila a cada 15 min (o Mac precisa estar ligado na hora do post).
