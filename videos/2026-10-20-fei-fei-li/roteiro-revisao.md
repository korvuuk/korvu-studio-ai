VEREDICTO: APROVADO COM AJUSTES (ajustes já aplicados no roteiro.md; falta só uma decisão opcional)

Revisão da v3 (narrativa), 15/10/2026. Substitui o parecer da v2.

## Resumo
- Formato: narrativo de verdade. Tem todos os blocos (gancho, história, desafio, virada, clímax, reflexão, CTA), frases inteiras, conectores ("Pois é", "O problema é que", "E o mais curioso é que…", "Mas olha que interessante…") e a frase-lição (L27–L29) antes do CTA. Nada de telegráfico. Está no tom do modelo do Hinton.
- Parser: 32 linhas, 333 palavras, ~156 s, sem erro. Há 1 aviso: L22 com 21 palavras (ideal ≤ 18), efeito do ajuste de honestidade abaixo.
- Tamanho: alvo 310, real 333 (+7%, dentro dos ±10%). Passa de 90 s; permitido pela decisão de 14/10 (no Facebook sai como vídeo da Página).
- Teste "soa a IA?": passa (0–1 sinal). As frases variam de tamanho, têm "pra", começam com "E" e "Mas", e o exemplo é concreto. O único sinal é o par "não aprende por mágica / aprende com exemplo" (L28), leve e aceitável.

## Hooks
| Hook | Fala | Palavras | Tela | Nota | Comentário |
|---|---|---|---|---|---|
| A (escolhido) | "Imagina você chegar adolescente num país novo, sem falar inglês…" | 11 | 4 palavras | 8 | Auto-relevância alta para o lusófono imigrante. Curiosity gap fechado em L02–L03 ("ajudar as máquinas a enxergar", "Fei-Fei Li"). |
| B | "Imagina ouvir dos colegas que era melhor fazer algo mais útil…" | 11 | 4 palavras | 6,5 | Específico, mas sem contexto de quem; depende do próximo. |
| C | "Imagina brincar que ia reabrir a lavanderia pra pagar a sua pesquisa…" | 12 | 4 palavras | 7 | Ótimo curiosity gap e detalhe específico, mas menos universal que o A. |

Escolha A justificada: maior nota e maior ponte com o público (imigrante que traduz para a família), que é o fecho do vídeo (L29/L32). Os três têm visual definido. B e C sem L02/L03 próprios: ao gravar o B/C o Carlos reutiliza L02–L03, o que funciona.

## Conferência de fatos (dossiê + fontes.json)
| Linha | Veredito |
|---|---|
| L01–L04 | OK. "Adolescente" (15 × 16 diverge nas fontes) e China são seguros. |
| L02 "ajudar as máquinas a enxergar" | OK, e a armadilha é resolvida em L20–L25: ela fez o banco de fotos, não a IA vencedora. |
| L05–L07 | AJUSTADO (ver abaixo). |
| L08 | OK. "Foi assim que paguei a faculdade" é fala dela no TED2015 (primária), com "ela conta". |
| L09–L11 | OK (TED2015: criança, milhões de imagens, 2007 "não era óbvio"). |
| L12 | OK. "Some very friendly colleagues advised me to do something more useful for my tenure". |
| L13–L14 | OK. "Chegou a brincar" mantém que foi piada e ela não reabriu. "Faltava tanto dinheiro" é o contexto que o dossiê dá (§2.3); aceitável. |
| L16 | OK. "Segundo ela" está presente (quase 50 mil, só palavras dela no TED). |
| L17, L19 | OK. "Milhões" evita a divergência 14 × 15 mi; "de graça" é fala dela (for free). |
| L20–L22 | OK com ajuste. 15,3% × 26,2% no resultado oficial (image-net.org), Hinton no grupo SuperVision. |
| L21 | OK. O Reel do Hinton está publicado (tracker: publicado 15/10 11:44), então "de quem eu já falei aqui" é verdadeiro. |
| L23 | OK (Wikipedia AlexNet, 1 fonte para a frase, mesma do Hinton). Observação: repete quase literal "Aquilo mudou o rumo da IA" do Reel do Hinton; é do modelo, mas quem vê os dois pode notar. Não bloqueia. |
| L25 | OK e é o melhor trecho: a IA era deles, os exemplos eram dela. Não atribui a ela a IA. |
| L26 | OK. "Chamam ela de" (apelido de imprensa), não título. |
| L28–L29 | Lição do Carlos, sem promessa de resultado. OK. |

Sem AMD/World Labs (acordo não fechado), sem "US$ 20", sem "bolsa integral", sem Maven. Bom.

## CTA
- L30 "Comenta AULA que eu te mando o link da palestra dela." (11 palavras, ≤ 12). AULA = 4 letras, sem acento, fácil de digitar. Única na semana (NOBEL, FOTO, GOLPE, LISTA, AGENTE nos outros).
- Promessa x PDF: o `palestra-fei-fei-li-ted2015.pdf` existe e `_fonte/material.md` entrega: link oficial do TED2015 (ted.com), "cerca de 18 minutos", passo a passo para ligar a legenda em "Português brasileiro" (também "Português de Portugal"). L31 "São 18 minutos, com legenda em português" bate. (TED mostra 17:45, YouTube 18:02; "18" é honesto.)
- L32: 2.º pedido de envio com destinatário concreto ("quem já foi o tradutor da família"), permitido por decisão de 14/10. Sem cena extra no CTA (tabela de extras: E-linhas vão só até L29). OK.
- Nenhuma palavra banida, nenhum "tu/teu", números em algarismo (2007, 2012, 50 mil, 4, 5, 18).

## Ajustes aplicados no roteiro.md (parser rodado depois, sem erro)
| ID | Antes | Depois | Motivo |
|---|---|---|---|
| L05 | Mas lá, / a vida dela começou numa **lavanderia**, / da própria família. | E lá, / ela trabalhava numa **lavanderia**, / da própria família. | "A vida dela começou numa lavanderia" afirma mais que as fontes (quando a loja abriu diverge: Fortune × Wikipedia; Wikipedia diz que ela já trabalhava lá no ensino médio). "Mas" não contrastava com nada. |
| L07 | atendia o telefone, / a cobrança / e até o **fiscal**. | atendia o telefone, / cuidava da cobrança / e até do **fiscal**. | "Atendia a cobrança / o fiscal" não fecha em português falado; agora cada item tem verbo (fonte: atender telefone, cobrança, fiscalização). |
| L22 | O segundo colocado errava / mais de uma em cada 4 fotos. / A IA deles errou **bem menos**. | O segundo colocado errou / mais de uma em cada 4 fotos, / mesmo com 5 palpites. / A IA deles errou **bem menos**. | Os 26,2% são erro top-5 (a resposta certa não estava entre 5 palpites da IA). Sem o "mesmo com 5 palpites", "errar mais de 1 em cada 4 fotos" parece muito pior do que foi e passa uma imagem incorreta da medida. "Errava" virou "errou" (foi um resultado numa competição, não hábito). A conta de 26,2% > 25% continua verdadeira. |

## Pontos de decisão
1. **L22 ficou com 21 palavras** (aviso do parser, ideal ≤ 18). O aviso é só recomendação. Se o Carlos preferir, duas saídas: (a) dividir em duas linhas L22 e L22b ("O segundo colocado errou mais de uma em cada 4 fotos, / mesmo com 5 palpites." + "A IA deles errou **bem menos**."), o que exige renumerar as linhas seguintes e o campo "Linhas" das cenas extras; (b) manter como está. Minha sugestão: manter, é uma linha só, falada com respiro nos "/".
2. **Duração ~156 s** (alvo 150). Dentro da decisão de 14/10 (narrativo pode passar de 90 s; FB recebe como vídeo da Página). Se o Carlos quiser enxugar, o menor corte sem perder arco é L12–L13 fundidos, mas não recomendo mexer.
3. Checklist de gravação já manda reconferir o "CC" em português antes da L31. Manter.

Nenhum problema grave. Pode seguir para teleprompter, monitor e história-completa.
