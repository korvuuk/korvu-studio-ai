RESULTADO: PASS

# QA final — Geoffrey Hinton — v3 (`edicao/final.mp4`)

Data: 2026-10-15. Passagem 2. Mídia não alterada.

## Checagens

| Checagem | Valor | Status |
|---|---|---|
| Resolução / FPS | 1080x1920 / 25,0 | PASS |
| Codec / perfil / pix_fmt | H.264 High, yuv420p, tags bt709 | PASS |
| Áudio | AAC 48 kHz | PASS |
| Duração | 158,74 s (EDL 158,68; limite 180 s) | PASS |
| Loudness integrada | -14,1 LUFS | PASS |
| True peak | -1,9 dBTP | PASS |
| Faststart | ftyp > moov > mdat | PASS |
| Tamanho / bitrate | 163,5 MB / 8,64 Mbps | PASS |
| Pretos (>=0,5 s) / congelados (>=2 s) | 0 / 0 | PASS |
| Cenas extras "faltando" | qa_check acusa E01/E04/E06 | PASS (falso positivo, ver abaixo) |
| Legendas vs roteiro | 56 divergências | OK (esperado, legenda = fala real) |
| Borda preta / caixa / layout split | nenhum quadro com barra preta ou split | PASS |
| Texto em inglês queimado por nós | nenhum | PASS |
| Créditos "Fonte:" | presentes nos 26 extras | PASS (aviso de contraste) |
| Legendas dentro das safe zones | sim (faixa ~60% da altura) | PASS |
| Carlos de volta (L11/L17/L24) e tela cheia no início/fim | 59,04-63,60 / 94,84-97,96 / 128,72-133,28 / 0-12,48 / 139,12-fim | PASS |
| CTA "NOBEL" | visível 148,5 / 151,0 / 151,5 s, fora do rosto | PASS |
| Capa `capa/capa.png` | 1080x1920, título no peito/gravata, fora do rosto | PASS |
| Capa 3:4 (`grade-3x4.png`) | título e crédito inteiros dentro do corte | PASS |

## Sobre o FAIL do qa_check ("E01, E04, E06 faltando")
O `qa_check.py` lê o `edl.json`, que ainda tem as animações E01/E04/E06 marcadas como `faltando`. A camada real vem do `reel-props.json` / `overlays-v3.json` (26 imagens e vídeos, nenhum `faltando: true`). Nos quadros, esses trechos mostram imagens ou vídeos de verdade, sem placeholder. Quem rodar o `montar_pacote.py` não deve usar o `qa-tecnico.md` como fonte de PASS. Sugestão: atualizar o `edl.json` ou o `qa_check` para ler o `--overlays`.

## Frames conferidos
Cerca de 50 quadros: 1 a cada 10 s, início e fim de cada extra (início +1,0 s e fim -0,3 s), os retornos do Carlos e o CTA. Todos em tela cheia, sem barra preta e sem caixa. Nenhum degrau de cor visível entre os takes do Carlos.

## Avisos (não bloqueiam)
1. Crédito "Fonte:" pequeno e quase ilegível sobre fundo claro: 13,48-16,18 s (John Sears, fundo branco), 19,52-20,14 s (gravura), 86,84-87,38 s (Eviatar Bach, fundo branco). Sugestão: sombra ou fundo suave no crédito.
2. Legenda sobre o rosto do Hinton em planos fechados: 49,92-56,18 s (rosto jovem, texto sobre nariz e boca) e 102,3-106,9 s (BBC, legenda sobre boca e nariz). Poderia subir ou descer a legenda nesses trechos.
3. 75,0-80,6 s (V17): o vídeo mostra uma tela branca brilhante, quase vazia, sobre preto. Parece painel vazio. Confirmar se é intencional. A legenda "Foi aí" cai dentro do retângulo branco, com contraste baixo.
4. Texto em inglês vindo das próprias fontes, não queimado por nós: cartões "WRONG/NIGHT/WOMAN" em 39-42 s e a interface do ImageNet em 70,5-74,3 s. Aceitável (material de terceiros).
5. Capa: "Quem é o" em cinza médio, contraste um pouco menor que o resto do título. Legível.
6. Hook (0-3 s): Carlos em tela cheia, legenda "Imagina você passar 50 anos...". Ok. Os zooms alternam por corte sem saltos.

Arquivos: `/Users/teste/Documents/CONTENT AI/videos/2026-10-20-geoffrey-hinton/qa/qa-tecnico.md` e `/Users/teste/Documents/CONTENT AI/videos/2026-10-20-geoffrey-hinton/qa/relatorio.md`.
