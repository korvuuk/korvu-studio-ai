# Fontes de Notícias de IA + Pontuação

> Pra o pilar **Notícia explicada** (`pilares.md`). Princípio: pesquisar em inglês (onde a novidade sai primeiro) e entregar em PT-BR, traduzido pra **"o que muda pra você"**.

---

## Fontes

### Oficiais (primárias — confirmam lançamento)
| Fonte | Uso |
|---|---|
| Blogs/newsrooms oficiais: OpenAI, Google (Gemini/DeepMind), Anthropic, Meta AI, Microsoft | Confirmar o que foi lançado, quando, pra quem e em que plano |

### Especializadas (alta credibilidade)
| Fonte | Foco |
|---|---|
| MIT Technology Review | Pesquisa, dados e impacto da IA |
| The Verge / Wired | Lançamentos e tendências de consumo |
| TechCrunch | Startups, lançamentos, investimento |
| VentureBeat | IA em empresas, automação |
| Harvard Business Review | IA em gestão e negócios |
| McKinsey Insights / Gartner | Relatórios de adoção e previsões |
| Nature / Science | Pesquisa científica (saúde e ciência) |
| Product Hunt | Ferramentas novas do dia |

### Em português (secundárias — contexto local)
Tecnoblog, Canaltech, Olhar Digital: úteis pra conferir **disponibilidade no Brasil, idioma e preço em R$**. Não substituem a fonte original.

### Tendência (nunca fonte única)
X (Twitter), LinkedIn, Reddit (r/artificial, r/MachineLearning), YouTube — servem pra **descobrir** o assunto. Toda afirmação precisa ser confirmada numa fonte acima.

---

## Pontuação da notícia

Cada critério recebe 1–10:

**Score = Novidade × 0,20 + Impacto × 0,30 + Relevância × 0,30 + Credibilidade × 0,20**

| Critério | Peso | 1–3 | 4–7 | 8–10 |
|---|---|---|---|---|
| **Novidade** | 20% | Mais de 7 dias (só serve como "análise") | 3–7 dias | Últimas 72h |
| **Impacto** | 30% | Nicho técnico, pouca gente afetada | Afeta um setor ou uma ferramenta popular | Afeta ferramenta que milhões usam (ChatGPT, Gemini, WhatsApp, Instagram, Google) |
| **Relevância pro nosso público** | 30% | Só interessa a desenvolvedor/investidor | Interessante, mas sem ação prática | Iniciante ou dono de negócio **consegue fazer algo com isso essa semana** |
| **Credibilidade** | 20% | Rumor, fonte única, post de rede social | 1 fonte especializada | Fonte oficial ou 2+ fontes independentes |

### Decisão
| Score | Decisão |
|---|---|
| ≥ 7,5 | Pode virar Reel |
| 6,0–7,4 | Só se tiver ângulo prático forte e demonstrável |
| < 6,0 | Descartar |

**Desempate:** dá pra mostrar na tela? · funciona no plano grátis? · está disponível em português/no Brasil?

**Confiança:** `alta` (oficial ou 2+ fontes) · `média` (1 fonte boa → falar "segundo [fonte]") · `baixa` (não usar).

---

## Categorias (prioridade pro nosso público)

| # | Categoria | Prioridade | Exemplos de tema |
|---|---|---|---|
| 1 | Ferramentas e lançamentos que dá pra usar hoje | Alta | função nova no ChatGPT/Gemini/Claude, app novo grátis |
| 2 | IA no trabalho e no negócio | Alta | atendimento, propostas, conteúdo, planilhas, agentes |
| 3 | IA no dia a dia (celular, WhatsApp, Instagram, Google) | Alta | IA chegando nos apps que a pessoa já usa |
| 4 | Segurança, golpes e privacidade | Média-alta | golpe com voz clonada, deepfake, o que não compartilhar |
| 5 | Regras e empregos | Média | regulação (ex.: AI Act na Europa), IA e emprego |
| 6 | Saúde e ciência | Baixa | só com gancho de curiosidade forte e fonte científica |

---

## Processo

1. Pesquisar (fontes em inglês + checagem local em português).
2. Montar o top 5 com score, fonte, data e confiança.
3. Escolher 1 (conferir `_controle/temas-ja-feitos.md` — não repetir tema/ângulo).
4. **Validar:** abrir o link · conferir data · achar a fonte oficial · conferir disponibilidade no Brasil/Portugal e no plano grátis · conferir preço (em R$ ou "tem plano grátis/pago").
5. Roteiro na estrutura fixa: **fato em 1 frase → o que muda pra você (1–2 exemplos concretos) → vale testar? como → CTA**.
6. Fonte na legenda ("Fonte: veículo, data").

### Formato do ranking
```yaml
- titulo: ""
  fonte: ""
  url: ""
  url_confirmacao: ""
  publicado_em: "AAAA-MM-DD"
  confianca: alta | media | baixa
  categoria: 1-6
  o_que_muda_pra_voce: ""
  notas: {novidade: 0, impacto: 0, relevancia: 0, credibilidade: 0}
  score: 0.0
```

---

## Armadilhas conhecidas (revalidar sempre)

- **O pipeline antigo gerou notícias com URL e números não verificados.** Ex.: "GPT-5 lançado" aparece como novidade em abril/2026 **e** de novo em julho/2026. Sempre abrir o link e confirmar.
- Fatos registrados em maio/2026 (revalidar antes de usar): Sora (OpenAI) encerrado em 24/03/2026; Claude não gera imagens; Gemini "Advanced" virou "AI Pro".
- Números de usuários variam entre fontes (ex.: Gemini aparece com ~400 milhões e ~750 milhões de usuários mensais em fontes diferentes). Citar sempre fonte + data.
- Preços e planos mudam o tempo todo — conferir no dia da gravação.
- Não usar notícia com mais de 7 dias como novidade; reformular como "o que aprendemos desde…".
