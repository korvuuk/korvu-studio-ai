# Automação Meta — instruções desta área

> Esta área é `automacao-meta/`, mas os scripts executáveis ficam em `scripts/` na raiz (não mover — os 4
> jobs do launchd chamam esses caminhos direto; mudar de lugar quebra o agendamento). Regras transversais
> (identidade, legal, segredos) estão no `CLAUDE.md` da raiz — carregado junto quando a sessão abre aqui.
> Detalhe completo da arquitetura: **`ARQUITETURA.md`**. Configurar o app na Meta: **`CONFIGURAR-APP-META.md`**.

## Escopo
Publicar os Reels no Instagram e Facebook na hora agendada, e responder automaticamente quando alguém comenta
a palavra-chave: resposta pública + direct com o PDF do material. **Sem CRM, sem servidor, sem conversa** —
decisão do Carlos de 09/10: só entregar material.

| Peça | Script |
|---|---|
| Publicar IG+FB | `scripts/publicar.py` (launchd `uk.korvu.publicar`, 15 min) |
| Comentário → direct | `scripts/responder_comentarios.py` (launchd `uk.korvu.comentarios`, 2 min) |
| Métricas aos 5 dias | `scripts/metricas.py` (launchd `uk.korvu.metricas`, 09:30) |
| Perfil/bio/público | `scripts/perfil.py` |
| Textos, limites, liga/desliga | `automacao-meta/respostas.yaml` |

## Limite da área
Só mexer em `automacao-meta/` e nos scripts acima. Esta área lê/escreve em `06-publicar/`, `07-publicados/` e
`_controle/` porque é o fim do pipeline de conteúdo — isso não é cruzar pra outra área, é a função dela. Não
tocar em `videos/<slug>/` por conta própria (quem produz o vídeo é a área do estúdio de conteúdo), nem em
`painel/` ou `linkedin/`.

## Regras rígidas (valem também aqui, da raiz)
- **Nunca publicar fora do fluxo**: só publica o que estiver em `06-publicar/` com `pacote.json` QA PASS
  (regra 2 da raiz).
- **Nunca prometer/entregar material que não exista** em `videos/<slug>/material/` (regra 6 da raiz) — o
  direct só manda o PDF que já foi gerado pelo `produtor-de-material`.
- **PORTAO-PUBLICACAO**: `publicar.py` recusa pacote sem o selo do GAUNTLET e post sem o portão de publicação
  aprovado (regra 13 da raiz).
- Tokens só via `.env` / variável de ambiente — nunca ler, imprimir ou logar.
