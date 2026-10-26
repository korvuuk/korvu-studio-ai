VEREDICTO: APROVADO

# Rodada 2 (última) — 2026-10-20-geoffrey-hinton

Parser: 19 linhas, 189 palavras, ~86,8 s, sem erros. 189 contra alvo 185 = +2 %. Está abaixo do teto de 90 s, mas com 3,2 s de folga e a voz do Carlos ainda sem calibrar. Se ele falar mais devagar que 2,3 palavras/s, passa dos 90 s. Não bloqueia. Sugestão: cronometrar uma leitura na gravação e, se estourar, cortar a L19 da fala (ela já está na legenda).

## Correções da rodada 1: conferidas
1. Hook A: TELA "PADRINHO DA IA: SERÁ TROTE?" (5 palavras), FALA com 12 palavras, visual com E01 (celular "02:00 · Suécia") e snap-zoom, nota "L01 sem extra" reescrita. OK.
2. L14 "Um ano e meio depois": 01/05/2023 a 08/10/2024 = 17 meses. OK.
3. L12 atribuída a ele ("dizendo que queria falar dos riscos... sem amarra"): bate com MIT TR e AP. OK.
4. `hook_template: curiosity-gap`. OK.
5. `pose_capa` parada, mãos baixas, sobrancelha erguida. OK.
6. Promessa na L02 ("o recado dele é pra você"), dentro de ~8 s. OK.
7. 189 palavras. OK.
8. L18 com "link oficial". OK; a promessa do PDF é só o link, e o PDF vai entregar isso.
9. E09 dividido em E10 e E11 (corte seco). OK.
10. L19 mantida, "Manda pra quem clica em tudo." (6 palavras). Exceção ao "nunca dois CTAs falados" fica para o Carlos decidir, sem bloqueio. Se ele recusar, a L19 sai (a legenda já tem) e sobram ~3 s.
11. PDF: ainda não existe. Esperado, é gerado pelo `produtor-de-material`. Não bloqueia agora, mas o vídeo não vai para a fila sem ele.

## Hooks (repontuados)
| Hook | Fala / tela | Nota |
|---|---|---|
| A (escolhido) | 12 / 5 | ~7,2 (a tela agora diz IA; tem cena extra E01) |
| B | 9 / 4 | 5,8 |
| C | 12 / 4 | 5,0 |
A é o maior e passa de 6. Sem bloqueio.

## Fatos novos
- L17 "Ele desconfiou até do Nobel.": dossiê M3 (fonte primária, entrevista por telefone do Nobel): "how could I be sure it wasn't a spoof call?", mais Fortune. OK. É um resumo curto, mas fiel. O resto da L17 é conselho prático da Korvu, sem opinião sobre risco, e a fala não atribui o conselho ao Hinton. Correto.
- L13 "E ainda elogiou o Google.": dossiê M5 e §9, o Google "agiu com muita responsabilidade", fala dele no MIT TR e na AP. OK.
- L15–L16: continuam fiéis ao discurso do banquete. A condição "se for dividido igualmente" fica de fora; é aceitável em 90 s. Opcional: inserir "se bem dividido" na L15.
- Nada do §9 foi violado (sem extinção, sem protesto, sem US$ 44 mi, sem "inventou").

## Voz, ritmo e "soa a IA?"
Passa. Tem "Aí", "E ainda", "Tipo", frases de 3 a 14 palavras, o exemplo concreto (trilha no mato) e nada de manual. A cadência do meio (L11–L14) agora se quebra com "Aí" e "E ainda".

## Observações que não bloqueiam
- "Trote" é brasileirismo. Em Portugal, "partida" ou "brincadeira". Contexto resolve; quem decide é o Carlos.
- ENTREVISTA tem 10 letras (ideal de 8 em `cta.md`); sugestão apenas.
- Cena E01 no hook é permitida (a proibição vale só para o CTA). L18–L19 sem extra, correto.

## Correções restantes (nenhuma bloqueante)
1. Carlos decide a L19 (exceção de CTA duplo). Se aceitar, registrar em `docs/decisoes.md` e `cta.md`.
2. Gerar o PDF em `videos/2026-10-20-geoffrey-hinton/material/` antes de publicar.
3. Cronometrar na gravação (ver acima).

---

# Rodada 1 (histórico)


Veredito da rodada 1: REVISAR. O roteiro era bom na base (fatos batendo com o dossiê, voz limpa, parser OK: 194 palavras, ~88,9 s). O que bloqueava: hook A com nota 6,1 (nada dizia que o tema era IA; tela sem relação com IA; rosto parado), promessa só depois de 8 s, e ajustes de fato e formato.

Notas dos hooks (rodada 1): A 6,1 / B 5,8 / C 5,0 (todos abaixo de 7).

Correções pedidas na rodada 1:
1. Hook A: manter a FALA; TELA "PADRINHO DA IA: SERÁ TROTE?"; visual com celular tocando "02:00 · Suécia" e snap-zoom; reescrever a nota "L01 sem extra".
2. L14: "Um ano e meio depois, veio aquela ligação." (17 meses).
3. L12: atribuir a ele, sem motivo único ("saiu, dizendo que queria falar dos riscos da IA sem amarra").
4. `hook_template`: trocar `insider` por `curiosity-gap`.
5. `pose_capa`: parado, mãos baixas, sobrancelha erguida (nada de telefone imaginário no ouvido).
6. Promessa até 8 s: L02 com "Esse é o Geoffrey Hinton. E o recado dele é pra você."; fechar o loop na L17 ("Ele desconfiou até do Nobel").
7. Margem de tempo: mirar ~185 palavras.
8. L18: "o link oficial".
9. E09: dividir em dois cartões em corte seco (L15 e L16).
10. L19: decisão do Carlos sobre a exceção ao "nunca dois CTAs falados" (cta.md); se ficar, encurtar para "Manda pra quem clica em tudo."
11. O PDF do CTA precisa existir em `material/` antes de publicar.

Ressalvas registradas: "trote" é brasileirismo (Portugal: "partida"/"brincadeira"); ENTREVISTA tem 10 letras (ideal até 8); L15 omite "se for dividido igualmente".
