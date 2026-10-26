---
description: Pesquisa um tema ou pessoa e entrega o dossiê com fatos verificados + a lista de material (com licença) para o Carlos baixar
argument-hint: "<tema ou nome>" [slug]
---

Assunto: **$ARGUMENTS**. Usar o subagente **pesquisador-de-material**.

1. Se o nome/tema for ambíguo ou vier de áudio, **confirmar com o Carlos** quem é antes de pesquisar fundo (mostrar os candidatos com link).
2. Sem slug, propor um (`AAAA-MM-DD-palavra-chave`) e criar `videos/<slug>/material/`.
3. Entregar:
   - `material/dossie.md` — quem é, linha do tempo, fatos com fonte, citações, ganchos, o que não afirmar;
   - `material/fontes.json` — cada item de material com licença, autor, crédito, link e `permitido`;
   - proposta da tabela `## Cenas extras` no formato do roteiro (tipo · modo pelo formato · crédito).
3b. **PORTÃO-PAUTA** — subagente **portao-pauta** sobre o dossiê e o `fontes.json` (GAUNTLET, `docs/gauntlet.md`: roda sozinho, sem perguntar; BLOQUEADO → o construtor corrige os S0/S1 e volta ao mesmo portão, até 3 voltas; nada chega ao Carlos antes do APROVADO).
4. Com o PORTÃO-PAUTA APROVADO, responder com: o resumo em 5 linhas, **o que o Carlos precisa baixar** (lista com link direto) e o que ficou de fora por falta de licença.
5. Depois disso: `/novo-video <tema>` (o roteirista usa o dossiê) e `/extras <slug>`.

Regras: `00-marca/regras-legais.md` §1 (pessoa pública só com material licenciado/oficial + crédito) e §4 (nada inventado). Não baixar de YouTube/Instagram/TikTok de terceiros.
