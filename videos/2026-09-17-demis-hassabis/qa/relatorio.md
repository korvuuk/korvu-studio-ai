RESULTADO: PASS

# QA final — Hassabis, versão E (`edicao/final.mp4`) — 2026-10-02

## Checagens
| Check | Resultado |
|---|---|
| qa_check.py (19 checagens: 1080x1920, 25 fps, H.264 High yuv420p bt709, AAC 48k, faststart, 57,90 s vs EDL 57,84) | PASS |
| Loudness / true peak | -13,9 LUFS / -1,7 dBTP: PASS |
| Preto / congelado | 0 / 0: PASS |
| Cenas extras | 9 de 9 presentes, nenhum "faltando": PASS |
| Legendas vs roteiro | 0 divergências; grafia DeepMind, AlphaFold, IA, Nobel ok: PASS |
| Crédito "Fonte:" em cada extra (conferido por frame) | presente nos 9: PASS |
| Split sem faixa preta (extra em y 0–608, Carlos de 608 ao fim, legenda ~y 715) | PASS |
| Legendas sobre o rosto | ficam acima do queixo, sem cobrir olhos/boca: PASS |
| CTA (L13) | Carlos em tela cheia, sem extra: PASS |
| Cor entre takes (balanço de branco por arquivo) | sem degrau visível nos 14 frames amostrados: PASS |
| Capa 3:4 | pose de mão no queixo coerente com o hook "Nobel": PASS |

## Avisos (decisão do Carlos)
1. **Material de terceiros na tela: 47,56 s de 57,90 s** (todos os extras, de 0 a 47,56 s), acima do teto de 30 s da regra 4. Ele tratou este vídeo como teste e autorizou o máximo; a decisão de publicar assim é dele.
2. **L11 (Nobel de Química com John Jumper) não foi gravada.** Não está no vídeo nem nas legendas. O hook e a capa prometem o Nobel e a fala só o retoma no fim ("o menino do xadrez virou um dos nomes mais importantes"). Já sabido.

## Observações (não bloqueiam)
- E44 (L05–L06, ~15,8–27,4 s): o clipe tem moldura preta com vinheta, de cerca de 65 px no topo e 100 px nas laterais, e o conteúdo fica pequeno. Parece uma faixa preta dentro do extra. Se ele reclamar de novo, recortar/ampliar esse clipe.
- A legenda no split entra em y~715, logo abaixo do extra. A animação de entrada deixa algumas palavras semitransparentes em alguns frames (ex.: "AlphaFold"). É só a transição.
- O crédito "Fonte:" é pequeno (~20 px de texto em 1080) mas legível. Fica na base do extra, dentro das zonas seguras.
- Nos 14 frames amostrados não apareceu voz nem texto da IA. A checagem de áudio foi só pelo qa_check e pelo alinhamento das legendas, sem escuta integral.
- Capa: a linha de contexto ("Aprendeu xadrez aos quatro anos") não aparece na grade 3:4. Só a linha de impacto está visível. Confirmar se isso é intencional.

## Correção depois do QA (02/10)
- E44: moldura preta/vinheta do documentário removida (recorte 1488×837 → 1920×1080; original em `material/obra/trechos-originais/`). `cropdetect` no clipe: 1920:1080:0:0. Re-render com música 1 → `qa_check` PASS (−14,0 LUFS, TP −1,7). A observação do E44 está resolvida.
