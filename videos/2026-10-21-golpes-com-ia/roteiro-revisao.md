VEREDICTO: APROVADO

# Revisão do roteiro — 2026-10-21-golpes-com-ia

## Rodada 1 — REVISAR
Arquivo da rodada 1 não foi encontrado em disco no início da rodada 2 (não havia `roteiro-revisao.md` na pasta); os pedidos foram conferidos diretamente na versão 2 do roteiro. Se o texto da rodada 1 existir noutro lugar, colar aqui.

## Rodada 2 (final) — APROVADO

### Hooks (rubrica de hooks.md)
| Hook | Fala (palavras) | Tela (palavras) | Nota | Obs. |
|---|---|---|---|---|
| A (escolhido) | 10 | 4 | 8,5 | interrupção visual máxima (E01 desde o frame 1), curiosity gap, especificidade média |
| B | 6 | 4 | 7,5 | bom, menos auto-relevante |
| C | 8 | 4 | 8 | melhor potencial de envio; A segue por pagar o payoff do loop |

### Fontes (regra 7) — conferidas na web
- L10: 24noticias, 01/09/2026, confirma o alerta da CMVM (não assumir autenticidade de vídeos/notícias/entrevistas com figuras conhecidas, "incluindo a própria CMVM"; IA facilita). OK, fonte única secundária mas atribuída corretamente.
- L12 (RU): Crimestoppers (conteúdo Take Five, UK Finance/Governo) confirma "banco ou polícia nunca pedem PIN/senha por telefone nem transferência para conta segura". OK.
- L13 (BR): Febraban via O Povo 02/04/2024 cita o mesmo (não liga pedindo senha, cartão ou transferência; desligar e usar canais oficiais). OK. Fonte de 2024 sem data de validade crítica.
- L05/L07-L08: Starling Bank 2024, "3 segundos". OK. L11: Take Five, spoofing. OK.
- Crédito em E02/E04/E05 coerente com as fontes.

### Regras e decisões
- Regra 3: só o Carlos como pessoa real; "filho" e "famoso" são ícones; print da CMVM recortado sem foto/logo. OK.
- Duração: parse_roteiro OK, 16 linhas, 125 palavras, ~58,6 s (alvo 125, ≤ 60 s). OK.
- Promessa antes de 8 s (texto fixo + L06); payoff L14 antes do CTA; loop com E06. OK.
- Decisões 13–14/10: linha rápida de engajamento, palavra-chave falada, público lusófono na Europa/RU, legenda só em PT, Trial Reel, material em PDF. Tudo respeitado. CTA sem cena extra (L15–L16 em tela cheia). OK.
- Voz: "você", "tá", "pro"; frases curtas e longas intercaladas; sem sinais de IA em número suficiente para reprovar.

### Anotações (não bloqueiam)
1. L16 "E manda pro grupo da família." = segundo pedido falado; `cta.md` proíbe. Exceção pedida pelo Carlos, pendente de registro em `docs/decisoes.md`. Registrar antes do `/renderizar`/publicação.
2. `material/5-sinais-golpe-ia.pdf` ainda não existe (pasta `material/` vazia). Gerar via produtor-de-material + `gerar_material_pdf.py` antes de empacotar/publicar; sem o PDF o CTA não pode ir ao ar.
3. Antes de publicar, reconferir que a página da CMVM/24noticias continua no ar e, se possível, citar o comunicado direto da CMVM no PDF.
