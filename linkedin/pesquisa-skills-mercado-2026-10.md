# Que competências o mercado de IA pede — pesquisa de 23/10/2026

> Pedido do Carlos (23/10): "pesquisa e sabe qual skill o mercado de AI procura para não ficar adivinhando o que
> colocar". As competências do LinkedIn saem daqui, cruzadas com o que ele consegue provar.

## Método

- **Vagas reais, contadas** (não opinião): 963 anúncios baixados em 23/10 de 4 fontes públicas: Himalayas (10 buscas
  × 3 páginas: AI engineer, LLM engineer, AI automation, applied AI, AI agent, generative AI, ML engineer,
  AI solutions engineer, automation engineer, forward deployed engineer), RemoteOK (tags ai, llm,
  machine-learning), We Work Remotely (programação, full-stack, back-end) e o "Who is hiring" de outubro/2026
  do Hacker News.
- **Filtro pelo título:** fica só vaga de IA; saem os bicos de "treinar IA" (expert, tutor, rater, annotator…) e as
  repetidas. Sobram **449 vagas**, publicadas entre maio e 23/10/2026, em 3 famílias:
  - **A. AI / LLM engineer** (213): AI engineer, agentic AI engineer, AI agent developer, applied AI…
  - **B. Automação / implementação / solutions** (158): AI automation engineer/specialist, AI implementation,
    solutions engineer/architect, forward deployed… = **o Nível A da análise de 26/09** (aplicar já).
  - **C. ML engineer / data science** (78): para comparar; não é o alvo dele.
- **Contagem:** % das vagas da família cujo texto cita a competência (dicionário de ~80 termos).
  Script e números: `linkedin/pesquisa/analisar_vagas.py` e `linkedin/pesquisa/resultado-2026-10-23.json`
  (rodar de novo todo mês com dados novos para ver a tendência).
- **Limites:** contagem por palavra (uma vaga que cita "Python" como diferencial conta igual a uma que exige);
  o Himalayas é 77% da amostra; termos genéricos ("production", "communication") inflam um pouco.

## O que as vagas pedem (% das vagas que citam)

| Competência | A. AI engineer | B. Automação | Carlos prova? |
|---|---:|---:|---|
| LLMs (integração de modelos de linguagem) | 66% | 50% | ✅ OpenAI, Claude e Gemini por API (MUNTUZA, CONTENT AI, n8n) |
| AI agents / agentic | 63% | 43% | ✅ 25 agentes no CONTENT AI; agentes no n8n |
| Python | 51% | 49% | 🟡 o pipeline do CONTENT AI é em Python (escrito com o Claude Code) + certificado introdutório; **produção ainda não** |
| REST APIs | 44% | 55% | ✅ Meta Graph API, webhooks, edge functions |
| Integrações com sistemas de terceiros | 33% | 59% | ✅ Instagram, Facebook, WhatsApp, R2, ElevenLabs |
| Comunicação | 38% | 68% | ✅ carreira em comunicação digital (o diferencial dele) |
| Trabalho com cliente / stakeholders | 32% | 55% | ✅ ONGs, PNUD, clientes do freelance |
| System design / arquitetura | 52% | 47% | 🟡 desenhou o MUNTUZA e o CONTENT AI; precisa saber explicar sem ajuda |
| RAG (busca + LLM) | 42% | 26% | ❌ **falta** |
| Prompt engineering | 31% | 23% | ✅ |
| AWS | 31% | 19% | ❌ falta (plano Bedrock da análise) |
| Observabilidade de LLM (LangSmith, Langfuse) | 30% | 20% | ❌ falta |
| Testes | 30% | 37% | ✅ 900+ testes no MUNTUZA |
| Anthropic / Claude | 29% | 23% | ✅ |
| Custo / latência | 29% | 13% | ✅ auditoria de custo em tokens, limites |
| Evals (avaliação de LLM) | 28% | 18% | ❌ **falta** |
| Guardrails / segurança de IA | 25% | 16% | ✅ moderação com GPT-4o, limites, chave só no servidor |
| OpenAI / GPT | 23% | 13% | ✅ |
| Vector DB (pgvector, Pinecone…) | 23% | 9% | ❌ falta |
| TypeScript | 22% | 22% | ✅ MUNTUZA (~54 mil linhas) |
| CI/CD | 20% | 20% | ✅ GitHub Actions |
| Workflow automation | 10% | 20% | ✅ n8n |
| LangChain / LangGraph | 18% / 14% | 7% / — | ❌ falta |
| MCP | 17% | 14% | 🟡 usa no dia a dia; ainda não construiu um servidor MCP |
| n8n | 2% | 13% | ✅ |
| Docker / Kubernetes | 10% / 18% | 6% / — | ❌ falta |
| PostgreSQL | 10% | — | ✅ |
| **Supabase** | **1%** | **1%** | ✅ prova, mas **quase nenhuma vaga pede** → sai do título e do top 5 |

Na família C (ML engineer) mandam Python (71%), PyTorch (42%), MLOps (35%) e TensorFlow (35%): é outro mercado,
de quem treina modelos. **Não é o alvo** — o perfil dele é de quem constrói produto em cima de LLM (famílias A e B).

## O que os relatórios dizem (contexto)

- **AI Engineer** está no topo da lista de cargos que mais crescem do LinkedIn em 2026 (Jobs on the Rise); no Reino
  Unido já era o que mais crescia na edição de 2025. Competências citadas: LLMs, RAG, LangChain, MLOps.
- **Upwork (fev/2026):** a demanda por competências de IA aplicada ao trabalho dobrou (+109% no ano); "AI
  integration" +178% e "AI chatbot development" +71% — é o freelance da Korvu.
- **Stanford AI Index 2026 (dados da Lightcast):** programação continua no topo, com Python à frente.

## Achados que mudam o perfil

1. **Supabase sai do título e do top 5** (1% das vagas). Entra **"API integrations"** (55–59% nas vagas de automação).
2. **Top 5 de competências = o que o mercado mais pede E ele prova:** AI Agents · Large Language Models (LLM) ·
   API Integration · Prompt Engineering · Workflow Automation.
3. **Python** está em metade das vagas: entra na lista agora (ele tem o pipeline e o certificado) e sobe para o top 5
   quando houver um projeto Python dele no GitHub.
4. **Comunicação e trabalho com cliente** aparecem em 55–68% das vagas de automação: é o diferencial dele (anos de
   comunicação digital) — o Sobre já conta essa história; "Communication" e "Stakeholder Management" entram na lista.
5. **As lacunas confirmam o plano de estudo de 26/09:** RAG (42%), evals (28%), observabilidade (30%), AWS (31%),
   vector DB (23%), LangChain/LangGraph (18%). Ordem sugerida pelo peso no mercado: **Python de verdade → RAG com
   pgvector → evals + observabilidade (Langfuse) → AWS (Bedrock) → um agente com MCP/LangGraph**, cada um virando
   um repositório público e uma competência nova no LinkedIn.
6. **Localização:** no Himalayas, só ~15% das vagas "remotas" de IA aceitam Reino Unido, Europa ou o mundo todo; a
   maioria é só EUA, América Latina ou Filipinas. Filtrar por "Worldwide / EMEA / UK" antes de ler a vaga.

Fontes dos relatórios: [Jobs on the Rise 2026 — UK](https://maxwell-bond.sites.sourceflow.co.uk/insights/blog/ai-and-data-talent-tops-the-list-what-jobs-on-the-rise-2026-tells-us-about-the-uk-market) ·
[Upwork In-Demand Skills 2026](https://www.upwork.com/press/releases/upworks-in-demand-skills-2026-demand-for-top-ai-skills-more-than-doubles-as-ai-is-embedded-into-everyday-work) ·
[Stanford AI Index 2026 / Lightcast (Voronoi)](https://www.voronoiapp.com/work/Which-AI-Skills-Are-Most-in-Demand-8212).
Fontes das vagas: [Himalayas](https://himalayas.app/jobs) · [Remote OK](https://remoteok.com) ·
[We Work Remotely](https://weworkremotely.com) · [HN Who is hiring, out/2026](https://news.ycombinator.com/item?id=49922569).
