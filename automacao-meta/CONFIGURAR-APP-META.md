# Briefing — chat de configuração do app na Meta for Developers

> Para o chat que vai ajudar o Carlos a configurar o app da Meta. Escrito em 2026-10-13.
> Leia também: `automacao-meta/ARQUITETURA.md` (o que a automação faz) e `CLAUDE.md` (regras do projeto).

## 1. Sua missão (e só ela)

Guiar o Carlos, passo a passo e pelos prints que ele mandar, até ele ter **os tokens certos no `.env`**, e depois
confirmar com os comandos de verificação. **Não mexa em scripts, vídeos nem pastas de vídeo**: outras sessões cuidam
disso. Se descobrir que o código precisa mudar (ex.: ele só consegue usar o login do Instagram), **pare e explique**;
não adapte por conta própria.

Fale em **português do Brasil**, simples. Ele não é programador: diga exatamente onde clicar, um passo por vez, e peça
um print quando estiver em dúvida sobre o que ele está vendo. Os nomes dos menus da Meta mudam com frequência:
**guie pelo print dele, não pela memória**.

## 2. A situação

- Ele já tem um app na Meta for Developers, criado para **outra página/Instagram** (projeto antigo Korvu AI / Sarah, que usava n8n).
- Agora quer usar esse app (ou um novo, se for mais simples) na **conta nova do Instagram dele**.
- Objetivo da automação (decisão de 09/10): **publicar os Reels** no Instagram + Página do Facebook e, quando alguém comentar
  a palavra-chave, **responder no comentário e mandar o material (link de PDF) no direct**. Sem conversa, sem n8n, sem CRM.

## 3. O que o código espera (não negociável sem avisar)

Os scripts (`scripts/publicar.py`, `scripts/responder_comentarios.py`) usam o caminho **Facebook Login**:
`https://graph.facebook.com/v23.0`, com a conta do Instagram **ligada a uma Página do Facebook**.

**Requisitos da conta:**
1. O Instagram precisa ser **conta profissional** (Criador de conteúdo ou Empresa). **Conta pessoal não funciona na API.**
   Se a "conta pessoal nova" dele for pessoal, o primeiro passo é trocar para profissional no app do Instagram.
2. Essa conta precisa estar **ligada a uma Página do Facebook** (Central de Contas / configurações da Página). Se não houver
   Página para ela, criar uma.
3. A conta precisa ser **pública** (comentário de conta privada não chega à API).

**Permissões que o token precisa ter** (todas):
`instagram_basic`, `instagram_content_publish`, `instagram_manage_comments`, `instagram_manage_messages`,
`pages_show_list`, `pages_read_engagement`, `pages_manage_posts`. Se a tela pedir, também `pages_manage_metadata` e
`business_management`.

**Variáveis no `.env`** (na raiz do projeto, `/Users/teste/Documents/CONTENT AI/.env`):

| Variável | O que é | Onde achar |
|---|---|---|
| `META_APP_ID` | ID do app | painel do app, Configurações > Básico |
| `META_APP_SECRET` | Chave secreta do app | mesmo lugar ("Mostrar") |
| `META_PAGE_ID` | ID da Página do Facebook ligada ao Instagram novo | `GET /me/accounts` no Graph API Explorer |
| `META_PAGE_ACCESS_TOKEN` | Token da **Página**, de longa duração | `GET /me/accounts` feito com o token de usuário de **longa duração** |
| `INSTAGRAM_USER_ID` | ID da conta profissional do Instagram (número, **não** o @) | `GET /{META_PAGE_ID}?fields=instagram_business_account` |
| `INSTAGRAM_ACCESS_TOKEN` | Pode ser o **mesmo** token da Página | — |

Caminho mais curto para os tokens:
1. **Graph API Explorer** → escolher o app → "Gerar token de acesso" → marcar as permissões acima → na janela da Meta, escolher a **Página nova** e a **conta do Instagram nova** (desmarcar as antigas, se não forem mais usadas).
2. **Ferramenta de depuração de token** (Access Token Debugger) → "Estender token de acesso" → token de usuário de **longa duração** (~60 dias).
3. No Explorer, com esse token longo: `me/accounts` → pegar `id` (= `META_PAGE_ID`) e `access_token` (= token da Página; tirado de um token longo, normalmente **não expira**).
4. `{META_PAGE_ID}?fields=instagram_business_account` → `id` = `INSTAGRAM_USER_ID`.
5. Conferir no Debugger que o token da Página mostra as permissões da lista e "Expira: Nunca".

**Outras coisas a ajustar no app:**
- **Webhooks**: remover a URL de callback do n8n antigo (`korvu.app.n8n.cloud/...`), porque a automação nova não usa webhook. E pedir para ele **desligar o fluxo da Sarah no n8n**, senão dois robôs respondem.
- **Funções do app**: o Carlos tem de ser **administrador** do app, e a Página/Instagram novos devem estar no mesmo **portfólio empresarial** (Business Manager) do app, se o app estiver ligado a um.
- **Modo do app**: começar como está. O teste real decide: se o direct para uma conta de fora falhar por permissão, aí é preciso **Live + App Review** de `instagram_manage_messages`/`instagram_manage_comments` (exige verificação da empresa). Não comece a App Review antes do teste.

**Se o painel só oferecer "API do Instagram com login do Instagram"** (sem Página, tokens `IGAA…`, host `graph.instagram.com`):
isso **não** é o que o código usa. Não siga por esse caminho sem antes dizer ao Carlos que os scripts teriam de ser
adaptados, e registrar isso em `_controle/CONTINUAR.md`. Tente primeiro o caso de uso com login do Facebook
("Gerenciar mensagens e conteúdo no Instagram" / Instagram Graph API com Página).

## 4. Regras de segurança (obrigatórias)

- **Nunca peça ao Carlos que cole token, chave secreta ou senha no chat.** Ele mesmo cola no `.env`. Se ele colar no chat por engano, avise para gerar outro token (o que foi colado deve ser considerado exposto).
- **Não leia nem imprima o `.env`** (regra 9 do `CLAUDE.md`). Para saber se está certo, use os comandos da §5: eles mascaram os tokens.
- Prints com token visível: avise e peça um novo print com o token tapado.
- Não clique por ele em telas de login, nem digite credenciais em lugar nenhum.

## 5. Como confirmar que deu certo

Na raiz do projeto, depois de ele salvar o `.env`:
```bash
uv run python scripts/publicar.py verificar-tokens
uv run python scripts/responder_comentarios.py verificar
```
Sucesso = conta do Instagram com o @ novo, Página certa, tokens válidos, **nenhuma permissão "em falta"**.
Faltam ainda as variáveis `R2_*` (Cloudflare R2, onde ficam vídeo/capa/PDF). Se ele não tiver, isso é uma etapa à parte e não bloqueia a configuração da Meta.

**Primeiro teste de leitura** (sem publicar nada): o `verificar` dos dois scripts. Publicar e mandar direct de verdade
é **outra etapa**, com o OK explícito do Carlos (regra 2 do `CLAUDE.md`). Este chat não publica.

## 6. Ao terminar

Escreva uma entrada no topo do **`HANDOFF.md`** (modelo no arquivo) e atualize `_controle/CONTINUAR.md` (bloco "Automação Instagram"): qual app ficou, a conta @ ligada, quais permissões
o token tem, se precisou de App Review, e o que falta (ex.: R2). **Não escreva nenhum ID secreto nem token lá.**
