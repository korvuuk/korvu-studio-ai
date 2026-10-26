# ApprovalGate

Portão de aprovação: ponto onde um vídeo **para** até o Carlos decidir.

O consumidor fornece: número do portão / total, nome da etapa, título do vídeo, lista de critérios (feitos/por fazer) e as duas ações.

- Ícone `lock` em `accent-ink` sobre `accent-soft`; chip `k-chip--portao` com o estado (Aguarda · Aprovado · Ajustes).
- Critérios com `k-check`; concluídos ficam riscados em `ink-2`.
- Ação primária "Aprovar e agendar" (`k-btn-primary`), secundária "Pedir ajustes". Aprovar só fica ativo com todos os critérios feitos.
