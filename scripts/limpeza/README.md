# Limpeza — ferramentas da 1.ª limpeza (23–24/10/2026)

Contexto e decisões: `_controle/limpeza-2026-10-23.md` e `docs/decisoes.md` §5 (limpeza 23/10).
Rodar da raiz do projeto, com `python3 -I` (só biblioteca padrão).

| Script | O que faz |
|---|---|
| `inventario.py <raiz> <saida.json>` | só lê: classifica o projeto nos grupos G1–G5 e soma (não segue symlink) |
| `copiar_verificar.py <raiz> "<pasta no HD>" <resultado.json> <slug>…` | copia `videos/<slug>/brutos/principal/` para o HD com SHA-256 na leitura, relê a cópia do HD **sem cache** e compara; retoma uma cópia interrompida (não recopia o que já tem o mesmo tamanho, mas confere o hash dos dois lados); nunca sobrescreve |
| `finalizar_g3.py <raiz> <resultado.json> [--apagar]` | sem `--apagar` = ensaio. Recusa se a conferência não for 100 %, se o HD não estiver ligado com a cópia, ou se o original mudou desde a cópia; com `--apagar` grava `brutos/principal/ARQUIVADO.json` (formato em `docs/contratos.md` §0) e apaga os `.MOV` do Mac |

Resultado da cópia do Hassabis + Hinton (19 arquivos, 92,4 GiB, todos conferem): `_controle/limpeza-2026-10-23-copia-hd.json`.
O HD **KORVU V01** (exFAT, USB) caiu duas vezes durante o trabalho — a 1.ª com erro de gravação (o volume verificou OK
depois). Na próxima cópia (Fei-Fei, livro), retomar com o mesmo comando se cair.
