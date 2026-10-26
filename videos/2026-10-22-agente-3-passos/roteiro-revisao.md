VEREDICTO: APROVADO

Rodada 1. Nenhum bloqueio grave de fato. Os pontos abaixo são ajustes de honestidade, retenção e consistência. `parse_roteiro.py` roda sem erro (14 linhas, 157 palavras, ~71,9 s).

## Notas dos hooks (0-10)

| Hook | Clareza | Curiosity gap | Auto-relevância | Especificidade | Interrupção visual | Envio | Média |
|---|---|---|---|---|---|---|---|
| A (escolhido) "Olha isso: o cliente pergunta, e a resposta já sai pronta." (11 palavras; tela 4) | 8 | 6 | 7 | 7 | 9 | 6 | 7,2 |
| B "Seu primeiro agente de IA. Grátis, em três passos." (9; tela 5) | 9 | 5 | 6 | 7 | 6 | 6 | 6,5 |
| C "Você ainda responde cliente na mão? Olha o que dá pra montar." (11; tela 4) | 7 | 7 | 9 | 6 | 7 | 7 | 7,2 |

A empata com C. Manter A está justificado: mostra o resultado no 1.º quadro (E01) e é o molde da linha 3. C é a melhor alternativa de teste A/B porque tem mais auto-relevância e mais potencial de envio ("manda pra quem ainda responde na mão"). Todos cumprem FALA ≤ 12 palavras, tela de 4 a 7 palavras e visual definido. Nenhum usa abertura banida.

## Os 4 pontos pedidos

**1. Honestidade ("agente" e "grátis")**
- "Agente": o `publico.md` define agente de IA como algo que "executa tarefas (manda e-mail, agenda)". Um Gem não faz isso, e o Google o chama de assistente personalizado, não de agente. O roteiro já se protege: L03 redefine ("agente aqui é um assistente") e L11 diz que ele não manda sozinho. Mas L02 afirma "É um agente de IA" seco, antes da definição. Reescrever L02 como "Eu chamo de agente de IA" é suficiente. Quem entende o termo de forma estrita não se sente enganado.
- A ressalva fica em L11, aos ~55 s. É honesto, mas tarde. O hook diz "a resposta já sai pronta", o que é verdadeiro. Mantenha o vocabulário "resposta pronta" e nunca "atende sozinho".
- "Grátis": a Central de Ajuda não cita plano nenhum; o "grátis" vem de Android Authority (mar/2025) e Chromestory (07/2026). Está bem sustentado para contas Google pessoais. Duas ressalvas: o uso tem limites diários no plano gratuito, e a disponibilidade no Reino Unido/UE (público-alvo) não foi conferida nas fontes. Conferir no dia, com conta aberta num país europeu ou perguntando a alguém lá. Enquadrar como "criar é grátis" e deixar "limites de uso" no PDF.
- Faltou um aviso: o Gem pode errar preço mesmo com "nunca inventa preço". Essa instrução não é garantia. L11 deve incluir "confere antes de mandar".
- Aviso para o PDF: não colar dados pessoais de clientes (LGPD/GDPR).

**2. Pose da capa**
Compatível, com um ajuste.
- Decisão de 18/09: a pose é segurada 3 s e pode ser mão à frente, mas tem de ser segurada para não sair tremida. Decisão de 16/09: capa com boca fechada, sem mão em movimento. Três dedos levantados e segurados cumpre as duas, desde que a mão suba antes e fique firme por 3 s. O `frame_candidates.py` procura a janela mais parada.
- Ajuste: "sorriso confiante" pode abrir a boca ou mostrar os dentes. Trocar por **"sorriso de boca fechada"**, para não bater com a regra da boca fechada.
- Para o Carlos, o texto da capa nunca fica sobre o rosto. A mão levantada precisa ficar fora da faixa de texto. O `render_capa.py` cuida disso, mas o enquadramento deve deixar espaço.
- A pose fica fora da coluna FALA e o ChatGPT Voz a lê. Correto. A mão tem de baixar antes da L01.

**3. L09 "Salvar. / Pronto."**
Funciona. É um beat curto depois de três passos densos e faz parte do ritmo falado. Condições:
- Gravar as duas palavras como uma linha única e o `[pausa]` final depois.
- O `edl.py` não aceita peça de fala < 0,8 s. "Salvar. Pronto." dura ~1 s, então fica no limite. Se o apertador cortar, a linha pode sumir. Não dividir em duas linhas.
- Alternativa se quiser mais corpo: "Salvar. / E pronto, tá feito." Mas a versão seca é melhor.

**4. Duração**
157 palavras, ~71,9 s (parser), alvo 155 palavras (+1,3%) e 68-72 s. Dentro da faixa 50-90 s. O promessa/hook: L01 + L02 somam ~24 palavras (~10 s), então "três passos" só chega perto dos 10 s, acima dos 8 s de `hooks.md`. Encurtar L02 resolve.

## Demais checagens

- **Voz**: PT-BR, sem "tu/teu", sem palavra banida. Contrações presentes ("tá", "pra"), frases de tamanhos variados, "E é grátis" abre frase com "e". Passa no teste "soa a IA?" (nenhum sinal grave). "Passo um/dois/três" é cadência de lista, mas é tutorial numerado por decisão. Passa.
- **Fatos**: botões batem com a Central de Ajuda (conferida hoje): "Abrir barra lateral", "Gems", "Novo Gem", "Conhecimento", "Adicionar arquivos", "Salvar". "Conhecimento" é opcional na fonte; o roteiro o chama de "o pulo do gato", o que não é falso. "Até no celular": confere (Gem criado na web aparece no app; não funciona no Gemini Live). O roteiro pula "Abrir barra lateral" no L05, aceitável porque a tela mostra.
- **CTA**: um CTA principal tipo A com palavra AGENTE (sem acento, maiúscula, 12 palavras em L13). Ok. L14 acrescenta "Salva pra fazer no fim de semana", um segundo pedido falado. `cta.md` lista "Dois CTAs falados" em "Nunca fazer". Como é decisão do Carlos para a linha 3 (MESA.md §4), aceito, mas registrar a exceção em `docs/decisoes.md` se ainda não estiver. O CTA não contém cena extra (correto). Não promete data nem preço da imersão.
- **Material**: `material/agente-3-passos.pdf` ainda NÃO existe (só `_fonte/ferramenta.md`). Obrigatório antes de publicar. O produtor-de-material deve entregar o que L14 promete (instruções prontas para copiar).
- **Retenção**: as telas E04-E07 trocam a cada 1-2 linhas. L11-L14 ficam ~14-16 s só com o Carlos em tela cheia, a maior parte sem interrupção visual. A L13-L14 não pode ter extra, mas L11 e L12 podem.
- **Público**: L12 "É isso que eu ensino pra quem tá começando" é fraca (autopromoção vaga) e não paga nada. Vale encurtar ou trocar.
- **Termos PT-PT**: a tabela de cenas extras usa "ecrã" (E01, E04-E07). Não é fala, mas o projeto manda "tela". Trocar.
- **Demo**: o Café é fictício e o roteiro avisa disso. Colocar um selo "EXEMPLO" na tela de E01 para o espectador não achar que é cliente real.

## Correções por linha

| ID | Problema | Reescrita sugerida |
|---|---|---|
| L02 | "É um agente de IA" afirmado seco; promessa passa de 8 s | "Eu chamo de **agente** de IA. / Você monta o seu em **três passos**. [pausa]" |
| L04 | "grátis" sem enquadramento; limites de uso | "E criar é **grátis**, / só precisa de conta Google." |
| L11 | Ressalva tardia e sem aviso de erro | "Ele não manda sozinho no WhatsApp, tá? / Quem confere e envia é **você**." |
| L12 | Fraca, autopromoção vaga | Remover, ou trocar por algo que pague o hook, ex.: "Dez minutos, e o próximo cliente já tem resposta." Só se o tempo for medido; senão remover. (Se remover, ~145 palavras, ~66 s, ainda na faixa.) |
| Extras | L11-L12 só com o rosto | Adicionar E08 card (L11): "você cola → ele escreve → você confere e envia". Pode cobrir L11-L12. L13-L14 continuam em tela cheia. |
| pose_capa | "sorriso confiante" pode abrir a boca | "três dedos levantados pra câmera, sorriso de boca fechada" |
| E01 | Demo parece cliente real | Selo "EXEMPLO" na tela |
| E01, E04-E07 | "ecrã" (PT-PT) | "tela" |
| PDF | Falta | Produzir `material/agente-3-passos.pdf`, com avisos: erro de preço possível, limites de uso no plano gratuito, não colar dados pessoais |

Pendências de checagem no dia da gravação: nome dos botões na interface (rápida mudança do Google) e disponibilidade/idioma do Gemini com conta europeia (se a interface estiver em pt-PT ou inglês, os nomes dos botões na tela podem diferir do que o Carlos fala).


---

# Rodada 2 (final)

VEREDICTO: APROVADO

parse_roteiro.py sem erros: 13 linhas, 151 palavras, ~69,1 s (alvo 155 palavras, -2,6%; faixa 50-90 s das decisões de 13/10).

## Pedidos da rodada 1
- L02 ("Eu chamo de agente de IA"), L04 ("criar é grátis, só precisa de conta Google"), L11 (não manda sozinho, você confere e envia): aplicados. L12 removida. E08 (card cola, escreve, confere e envia) cobre L11. Selo EXEMPLO em E01. "tela" no lugar de "ecrã". pose_capa agora é parado, boca fechada, sem gesto de mão (cumpre 16/09 e 18/09). Promessa "três passos" chega aos ~7 s.
- Passos vs Central de Ajuda (ferramenta.md): Gemini no computador, Gems, Novo Gem, nome e instruções, Conhecimento, Adicionar arquivos, Salvar, aparece no celular. Tudo confere. L05 pula "Abrir barra lateral" (a tela mostra), aceitável.
- Honestidade: sem "atende sozinho"; L11 diz que não responde sozinho no WhatsApp. OK.
- Hooks (sem mudança de nota): A 7,2 (escolhido), C 7,2, B 6,5. FALA <= 12 palavras e tela de 4 a 7 palavras nos três.

## Sugestão não bloqueante
- L01B diz "Grátis" seco, enquanto a L04 enquadra como "criar é grátis" (há limites de uso). Se B for usado no teste A/B: "Seu primeiro agente de IA. / Criar é grátis, / em três passos."

## Anotações (não bloqueiam)
- "Salva pra fazer no fim de semana" (L13) é exceção ao "dois CTAs falados" de cta.md, pendente de decisão do Carlos. Se ele recusar, cortar a frase (cai para ~145 palavras, ~64 s).
- `material/agente-3-passos.pdf` ainda não existe. Tem de existir (produtor-de-material) antes de empacotar ou publicar, com os avisos listados na seção "Material do CTA".
- No dia da gravação: conferir nomes dos botões na interface e o idioma com conta europeia.
