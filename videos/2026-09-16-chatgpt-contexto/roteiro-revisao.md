VEREDICTO: APROVADO

# Revisão do roteiro — 2026-09-16-chatgpt-contexto (versão 2, rodada 2 de 2)

Revisor: revisor-de-roteiro · 2026-09-15 · Base: `roteiro.md` v2 + `roteiro.json`, `00-marca/hooks.md` (rubrica), `tom-de-voz.md`, `voz-carlos.md` (não calibrado → 2,3 palavras/s), `cta.md`, `regras-legais.md`, `publico.md`.

## Histórico
| Rodada | Versão | Veredicto | Motivo |
|---|---|---|---|
| 1 | v1 | REVISAR | L13 (CTA) com 13 palavras, acima do máx. 12 de `cta.md`. Duração estimada 63,7 s (137 palavras). |
| 2 | v2 | **APROVADO** | CTA com 12 palavras; 134 palavras / ~62,4 s; parser sem erros nem avisos. |

### Correções da rodada 1 (aplicadas na v2)
| ID | Problema | Reescrita literal |
|---|---|---|
| L13 | 13 palavras (regra: CTA falado ≤ 12) | "Comenta **PROMPT** que te mando o modelo e dois exemplos no direct." (12) |
| L05 | Linha longa que empurrava a duração | "O problema não é a IA. Ela não conhece o seu café. [pausa longa]" |
| L09 | Idem | "Assim: "tenho um café de bairro, o post é pros vizinhos"." |

## Hooks (rubrica de `hooks.md`)
| Hook | Template | Clareza 20% | Lacuna 20% | Autorrel. 20% | Especif. 15% | Visual 15% | Envio 10% | **Nota** |
|---|---|---|---|---|---|---|---|---|
| **A** (escolhido) — "Pare de pedir post pro ChatGPT sem dizer isso antes." | 1 contrarian | 8 | 8 | 8 | 7 | 8 | 7 | **7,75** |
| B (L01B) — "Você tá usando o ChatGPT do jeito errado." | 2 jeito errado | 9 | 7 | 9 | 5 | 8 | 6 | **7,55** |
| C (L01C) — "O maior erro de quem usa ChatGPT vem antes do pedido." | 5 erro | 7 | 9 | 8 | 5 | 7 | 6 | **7,20** |

Os três ficam na faixa **7,0–7,9: aprovados com ajuste sugerido**. O A é o de maior nota. Todos respeitam FALA ≤ 12, TEXTO 4–7 palavras e visual definido; nenhuma abertura banida.
- **A:** ponto forte: contraste + lacuna ("isso") + tarefa nomeada (post). Sugestão pra passar de 8: no frame 1, o celular já mostra "escreve um post pro meu café" (a fala aponta pra algo visível). Sem mudar a fala.
- **B:** ponto forte: clareza instantânea. Fraco: especificidade. Reescrita sugerida: "Você tá pedindo post pro ChatGPT do jeito errado." (9)
- **C:** ponto forte: curiosidade. Fraco: "vem antes do pedido" pede um segundo pra entender. Reescrita sugerida: "O maior erro no ChatGPT acontece antes de você pedir." (10)

## Checagens
1. **Retenção:** OK. Promessa começa aos ~4,6 s ("no final, te dou o modelo"). Troca visual em toda linha; o maior trecho sem troca é 6,7 s (L08, animação em movimento). Payoff em L11–L12 (~49–57 s), antes do CTA. Loop: "antes" (L12) fecha o "antes" do hook.
2. **Voz:** OK. PT-BR, "você", "pra", frases curtas com médias. Nenhuma palavra banida nem PT-PT (varredura na FALA). 3 pausas (L04, L05 longa, L12), dentro de 2–4. Opcional: "Pare de" → "Para de" soa mais falado; decidir na gravação só se virar nova versão, porque a FALA é literal.
3. **Tamanho:** 134 palavras (alvo 138 ±10% = 124–152): OK. Duração estimada **62,4 s**, acima dos 60 s. A estimativa soma 0,2 s de respiro em cada uma das 13 linhas (2,6 s). Não bloqueia; se o corte real passar de ~62 s, cortar a L07 e manter o TEXTO dela na L06.
4. **Fatos:** OK. Nenhum número ou estatística. O princípio ("dar contexto melhora a resposta") tem fonte oficial (OpenAI e Google, em "Fontes"). "Ela não conhece o seu café" é verdade no **Chat temporário** que o checklist exige (sem memória nem instruções personalizadas). L04/L11 dependem da gravação real; o checklist manda avisar se o resultado não bater, e isso é suficiente.
5. **CTA:** OK. Um só, tipo A (palavra-material), `PROMPT` (sem acento, ≤ 8 letras, primeira da semana). O material existe: `material/guia.md` tem o modelo com lacunas + **dois** exemplos (café, salão), exatamente o que a fala promete. O prompt bom mostrado na L09 é igual ao Exemplo 1. CTA secundário diferente na legenda (Salvar). O pilar tutoriais aceita A.
6. **Formato:** OK. FALA literal, sem indicações; `[pausa]` só no fim; IDs L01–L13 + L01B/L01C; `parse_roteiro.py`: 0 erros, 0 avisos. Conferido também com `edl.overlays_da_linha`: 4 overlays `tela-01` split (00:00–00:08, 00:08–00:15, 00:20–00:28, 00:32–00:40), 1 `animacao` split (L08), TEXTO nas demais, ZOOM em 5 linhas.
7. **Público:** OK. "Prompt" explicado em 1 frase com analogia (L06, recado pra funcionário novo); "contexto" usado no sentido do dia a dia e explicado pela própria animação. O dono de negócio vê aplicação direta (café, salão). Ressalva leve: o hook A fala de "post", menos universal pro iniciante que não posta. O B cobre esse público no Trial Reel.
8. **Legal:** OK. Barra lateral do ChatGPT fechada na gravação (histórico = privacidade); marca só pra identificar a ferramenta; sem pessoas além do Carlos; 5 hashtags.

## Observações não bloqueantes (linha)
| ID | Observação | Sugestão |
|---|---|---|
| L08 | 15 palavras (teleprompter pede ≤ 12) | Manter: as 4 palavras precisam estar na mesma linha pra animação sincronizar. Carlos pode respirar entre os itens. |
| L03 | A tela-01 aparece só ~4,5 s (duração da fala); o prompt fraco tem de ser digitado logo no início | Já está no checklist ("começa a digitar logo"). |
| L01B/L01C | O `titulo` do frontmatter é do hook A | Nas variantes, título próprio ou `titulo: null`. |

## Avisos de pipeline (fora do roteiro, para o coordenador)
- A câmera grava **25p**, mas `ingest.py` força `fps=30` (CFR). Isso duplica 1 a cada 5 quadros e dá judder. Decidir entre pipeline a 25 fps ou conversão com interpolação.
- `ingest.py` converte para **8-bit yuv420p** antes da etapa de cor, então o V-Log 10-bit perde precisão antes do LUT (risco de banding).
- `camera-00-cor.mov` também é ingerido e transcrito pelo `/editar` (é silencioso, então não entra no corte).
