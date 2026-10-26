# LinkedIn do Carlos — instruções desta área

> Esta área é `linkedin/`. Regras transversais (legal, segredos, GAUNTLET em geral) estão no `CLAUDE.md` da
> raiz — o Claude Code carrega os dois quando a sessão abre aqui, então não duplicar.
> Detalhe completo (diagnóstico, textos, fases): **`linkedin/README.md`**.

## Escopo
Portfólio pessoal do Carlos para vaga de **engenheiro de IA em 2027**. Canal próprio — **não é** o
`@korvu_oficial` nem o estúdio de conteúdo. Fonte da verdade para cargos e datas: o CV de IA remoto em
`~/Documents/Claude/Projects/Vagas Remotas Tech e AI/` (outro projeto, só leitura) — o LinkedIn tem de bater
com ele, nunca o contrário.

## Limite da área
Só mexer dentro de `linkedin/`. Nunca editar `videos/`, `00-marca/`, `painel/` ou `automacao-meta/` a partir de
uma sessão desta área sem avisar o Carlos.

## Regras rígidas
1. **Nunca automatizar o site do LinkedIn** (clicar, preencher, curtir, comentar, raspar) — o Contrato do
   Usuário proíbe bot/automação não autorizada e pode restringir a conta. Única exceção combinada: ler o
   perfil no navegador com o Carlos logado e vendo, sem clicar em nada que mude a conta.
2. **Editar o perfil é sempre manual** — eu escrevo o texto pronto para colar, o Carlos cola, eu confiro o
   resultado. A Profile Edit API é restrita e não está disponível pra nós.
3. **Publicar post** pode ser automático, mas só pela API oficial (`Share on LinkedIn`, escopo
   `w_member_social`) — nunca "não agenda", então o disparo é por launchd na hora marcada, como o
   `publicar.py` faz no IG/FB.
4. Token da API vale **60 dias** — reautorizar no navegador quando expirar (lembrete, como o da Meta).
5. **GAUNTLET**: quando os posts entrarem (fase 4), nenhum sai sem passar por um portão antes do Carlos —
   mesmo princípio das outras áreas (`docs/gauntlet.md`).

## Fases
Diagnóstico → Posicionamento → Perfil novo → Conteúdo e integração (posts + GAUNTLET) → Portfólio técnico
(GitHub público, sem segredos). Detalhe de cada fase: `linkedin/README.md`.
