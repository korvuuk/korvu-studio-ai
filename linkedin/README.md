# LinkedIn do Carlos — portfólio para AI Engineer (2027)

Perfil: https://www.linkedin.com/in/carlos-mendes-pereira-302573a6/
Diagnóstico: `diagnostico-2026-10-23.md` · textos para colar: `perfil-textos.md` · competências pelo mercado:
`pesquisa-skills-mercado-2026-10.md` (449 vagas reais contadas; refazer todo mês com `pesquisa/analisar_vagas.py`). **Fonte da verdade para cargos e datas:** o CV de IA remoto em
`~/Documents/Claude/Projects/Vagas Remotas Tech e AI/` (outro projeto; só leitura) — o LinkedIn tem de bater com ele.

> Frente aberta em 23/10/2026. O LinkedIn dele está parado há mais de 10 anos; volta como **portfólio pessoal**
> para ganhar visibilidade e, em 2027, se candidatar a vagas de **engenheiro de IA**. Entra no CONTENT AI como
> canal próprio (não é a @korvu_oficial). Decisão em `docs/decisoes.md` §5 (23/10).

## O que a API do LinkedIn permite (conferido em 23/10/2026)

| O quê | Pela API? | Como vamos fazer |
|---|---|---|
| **Publicar post no perfil dele** (texto, link, imagem, vídeo) | **Sim**, self-serve: produto "Share on LinkedIn", escopo `w_member_social`, sem revisão do LinkedIn. Limite 150 chamadas/membro/dia. Só cria post já publicado: **não agenda** | script nosso + launchd na hora marcada (como o `publicar.py` faz no IG/FB) |
| **Editar o perfil** (foto, capa, título, sobre, experiência, competências, URL) | **Não para nós.** A Profile Edit API existe, mas é restrita a desenvolvedores aprovados pelo LinkedIn (permissão privada `w_compliance`) | eu escrevo tudo pronto para colar; o Carlos cola no app/site; eu confiro o resultado |
| **Ler o perfil atual inteiro** | **Não** (o login OpenID só dá nome, foto e e-mail) | Carlos manda o PDF do perfil ("Mais → Salvar como PDF") ou a cópia dos dados (Configurações → Privacidade de dados → Obter uma cópia dos seus dados) |
| **Métricas dos posts** (impressões, alcance, reações, comentários, salvamentos, envios, cliques, seguidores e visitas ao perfil vindos do post) | Existe: `memberCreatorPostAnalytics`, escopo `r_member_postAnalytics`, **dentro da Community Management API** — acesso por pedido ao LinkedIn; aprovação para conta pessoal **incerta** | até lá, números do app (Análises do post); pedir o acesso depois de o script de posts funcionar |
| **Token** | Vale **60 dias**. Refresh token só para parceiros aprovados (MDP) | reautorizar no navegador a cada ~60 dias (lembrete, como o da Meta) |
| **App de desenvolvedor** | Criado em linkedin.com/developers; segundo guias de terceiros, precisa ficar ligado a uma Página do LinkedIn (a conferir na criação) | criar quando chegar a fase 4 |

**Não fazer:** robô ou automação no site do LinkedIn (clicar, preencher, curtir, comentar, raspar). O Contrato do
Usuário proíbe bots e automação não autorizada, e a conta pode ser restringida, que é o pior que pode acontecer
com um portfólio. O perfil é editado à mão pelo Carlos; o que for automático passa só pela API oficial.
Exceção combinada (23/10): para o diagnóstico, o Claude **lê** o perfil dele no navegador, com ele logado e vendo,
poucas páginas e sem clicar em nada que mude a conta.

Fontes: [Share on LinkedIn](https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/share-on-linkedin) ·
[Profile Edit API](https://learn.microsoft.com/en-us/linkedin/shared/integrations/people/profile-edit-api) ·
[Member Post Statistics](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/members/post-statistics) ·
[Refresh tokens](https://learn.microsoft.com/en-us/linkedin/shared/authentication/programmatic-refresh-tokens).
O endpoint de post recomendado hoje é o versionado `/rest/posts` (cabeçalho `Linkedin-Version: AAAAMM`; versões
antigas são desligadas — a de 202511 sai em 16/11/2026). Conferir a versão vigente antes de programar.

## Fases

1. **Diagnóstico** — ler o perfil atual (PDF/cópia dos dados), listar o que está velho, o que falta e o que sai.
2. **Posicionamento** — alvo decidido 23/10: **trabalho remoto como especialista em IA**; o perfil fala com
   recrutadores e times que contratam IA remoto. Título, palavras que recrutador procura,
   idioma (**decidido 23/10: perfil principal em inglês + a versão em português do próprio LinkedIn**; o dos
   posts fica para a fase 4), e a história: Sistemas de Informação → Korvu → o sistema de agentes do CONTENT AI.
3. **Perfil novo** — foto (sessão própria com a S5IIX, sem óculos escuros, cor pela cadeia da marca), capa (banner),
   título, Sobre, experiência, **Projetos/Em destaque** (o CONTENT AI como projeto de engenharia de IA: 25 agentes,
   portões de qualidade, pipeline de vídeo em Python/ffmpeg/Remotion, automação da API da Meta, painel
   Next.js + Supabase), competências, formação, URL personalizada, e as configurações (Open to Work só para
   recrutadores, visibilidade, idioma).
4. **Conteúdo e integração** — linha editorial (construir em público), calendário, `scripts/linkedin.py`
   (autorizar · publicar · verificar) + launchd; portão GAUNTLET para os posts antes de qualquer um sair.
5. **Portfólio técnico** — GitHub público com partes do sistema (sem segredos), ligado no perfil.
