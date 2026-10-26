> Diário das sessões (o que cada chat fez): **`HANDOFF.md`** na raiz. Este arquivo é o **estado atual**.

# ▶ AGORA — comece por aqui (atualizado 26/10)

**0q. PROJETO DIVIDIDO EM 4 ÁREAS, cada uma com o seu CLAUDE.md (26/10):** estúdio de conteúdo (raiz) · painel web (`painel/CLAUDE.md`) · LinkedIn (`linkedin/CLAUDE.md`) · automação Meta (`automacao-meta/CLAUDE.md`). Pedido dele: parar de ter que dizer "fala só do painel" em toda sessão nova. Índice em `CLAUDE.md` (seção "Áreas do projeto"); nenhum arquivo/script mudou de pasta, zero risco pro `painel/sync` e pros 4 jobs do launchd (publicar, comentários, métricas, painel) — eles não leem CLAUDE.md. O limite de cada área é convenção (documentada em cada arquivo), não uma trava técnica. Decisão em `docs/decisoes.md` §5 (26/10).

**0p. PAINEL WEB — 7 TELAS NO AR, PORTÕES VERDES (25/10, 23:13):** respostas do Carlos aplicadas (sem título, sem botões, US$, projeção 30 dias, Equipe = modelo que rodou, Biblioteca = acervo de estilos com aba Sistema, sem HD). Antes (24/10): Visão geral · Equipe · Produção de conteúdo (5 fases) · Calendário · Desempenho · Tokens e custos (£) · Biblioteca, no design "korvu. painel", com dados do banco. Portões: design ✅ (v5 23/10) · interface ✅ (`painel/portoes/interface-2026-10-24-v3.md`, 1f444d78dc16) · dados ✅ (`dados-2026-10-24-v2.md`); `portoes.py exigir painel` exit 0. Abrir: `bash painel/iniciar.sh` → http://localhost:3456. **Falta o Carlos:** olhar o painel + as dúvidas da designer (`painel/design/telas/*.md` § "Dúvidas para o Carlos"); decidir `perfil.py` diário (curva diária) e o rótulo dos toques (são botões de contato, não o link da bio). S2 no backlog: PI66 (recorte das miniaturas, designer), PI67, PI68, PD21 (maquete com tokens antigos).

**0g. TRIAL SUSPENSO — tudo sai NORMAL por agora (Carlos, 22/10; decisões §5b):** prioridade = a automação da palavra-chave ser testada por gente de verdade. **Regra do par (22/10): A (ele desde o 1.º segundo) = NORMAL na página, IG + FB; B (conteúdo primeiro) = Trial MANUAL, só IG.** **Livro-chatgpt A PUBLICADO 22/10** (normal; IG 21:10 https://www.instagram.com/reel/Dezzw0iimTe/ · FB 21:19 https://www.facebook.com/reel/1829716168045842/ — upload lento; automação LIVRO vigiando desde 21:19) · livro B ter 27/10 21:00 (Trial) · L01C qua 28/10 (Trial) · L01C-A dom 01/11 (Trial — confirmado pelo Carlos 22/10: não repetir o vídeo do livro na grade) · **repost da Fei-Fei A sáb 24/10 19:00** (`06-publicar/2026-10-20-fei-fei-li-r2`, só IG, normal; o FB já tem a Fei-Fei B). `calendario.md` `trial_padrao` vazio = todo post novo nasce normal. ⚠ **O 1.º direct para quem NÃO tem papel no app da Meta nunca foi testado** (`automacao-meta/ARQUITETURA.md`): se falhar por permissão, o `responder_comentarios.py` para e avisa → App Review de `instagram_manage_messages`/`instagram_manage_comments`. Conferir `_controle/logs/comentarios.log` depois das 21:00. Comentário LIVRO no **Facebook** não é automatizado (o script só lê o IG). **Repost do Hinton dom 25/10 19:00** (`06-publicar/2026-10-20-geoffrey-hinton-r2`, só IG, normal, palavra NOBEL). Base: `_controle/analise-trial-vs-normal-2026-10-22.md`.

**0n. LIMPEZA DO PROJETO (23/10):** 283 → 229 GB (54,1 GB apagados, aprovados pelo Carlos). Saíram G1 (renders intermediários, prévias, cópias idênticas de `07-publicados/`), G2 (vídeo-teste `chatgpt-contexto` — ficaram só os textos do roteiro, trava "não publicar" no painel —, `_teste-monitor`/`_teste-sintetico` — recriar com `tests/make_synthetic.py [--modo monitor]` antes de rodar as suítes —, versões A–E do Hassabis) e G4 (obra e vídeos do YouTube inteiros dos 3 publicados; os cortes ficaram). Quadros de calibração do LUT salvos sem perdas em `00-marca/cor/amostras/praq0967/`. Análise: `_controle/limpeza-2026-10-23.md`; lista do que saiu: `limpeza-2026-10-23-apagados.tsv`. **G3 Hassabis + Hinton FEITO (24/10 07:43):** 19 originais (92,4 GiB) copiados para o HD KORVU V01 (só backup, guardado), conferidos 19/19 por SHA-256 e apagados do Mac; no lugar, `brutos/principal/ARQUIVADO.json`. PORTÃO-DADOS APROVADO antes (sessão "Tokens e custos"); o painel ficou com os 6 campos de gravação idênticos. **Fei-Fei (81,4 GiB) espera outro HD/espaço** (`scripts/limpeza/README.md`). **G5 (27,6 GB, original do livro-chatgpt): rever depois de 06/11** (último post da fila em 01/11 + 5 dias de métricas).

**0m-FEITO (24/10) — LinkedIn ATUALIZADO pelo briefing** (detalhe e pendências em `linkedin/perfil-final-2026-10-23.md`): inglês principal + PT, headline/Sobre/top 5, MUNTUZA + Korvu + ProDoctor, formação, Python, idiomas, 4 projetos, ~20 competências, Open to Work só recrutadores, URL `linkedin.com/in/carlosmendespereira`, capa antiga apagada. **Falta dele:** ligar a visibilidade pública (está desligada), mês real da Korvu (ficou out/2025), telefone +55 e site korvu.com.br nos contatos, foto e capa novas, Em destaque.

**0m-ANTES (23/10, noite) — histórico: parou no meio pelo limite de uso:** fonte = `linkedin/briefing-2026-10-23.md` → `linkedin/perfil-final-2026-10-23.md` (antes: `perfil-antes-2026-10-23.md`). **FEITO no perfil:** inglês como idioma principal; nome sem "(korvu)"; headline EN e PT novos; local London; setor Software Development; **About EN salvo**; as 5 "principais competências" antigas removidas (**top 5 ficou VAZIO** — falta pôr AI Agents · RAG · Prompt Engineering · Claude API · n8n). **FALTA:** top 5; About PT; experiências (MUNTUZA nova, Korvu "AI Automation Builder" 2025, ProDoctor 2014–2019); formação (apagar a vazia); certificados (tirar Sass/Gulp, pôr Python); projetos (4); competências; idiomas (sem crioulo); Open to Work só recrutadores; URL; capa sem o telefone +55. Dica técnica: no LinkedIn, `form_input` funciona em textarea; nos campos editáveis (Sobre, título PT) digitar em pedaços curtos e conferir — a digitação longa perde letras.

**0m. LinkedIn do Carlos (23/10, sessão própria):** portfólio pessoal para vaga de engenheiro de IA em 2027 — `linkedin/README.md` (o que a API permite + 5 fases). Publicar pela API dá; editar o perfil, não (ele cola os textos); nada de robô no site. Perfil principal em **inglês** + versão em português do próprio LinkedIn; alvo = trabalho remoto como especialista em IA (23/10). **Diagnóstico pronto:** `linkedin/diagnostico-2026-10-23.md` (fonte da verdade = CV de IA remoto em `~/Documents/Claude/Projects/Vagas Remotas Tech e AI/`). Korvu = freelance de IA (jan/2023 – hoje) com o CONTENT AI dentro (23/10). **Textos prontos (v4: v3 aprovada pela revisão + título e competências pela pesquisa de 449 vagas reais, sem crioulo):** `linkedin/perfil-textos.md` (passo 0 = inglês como principal); pesquisa em `linkedin/pesquisa-skills-mercado-2026-10.md`. **Próximo:** ele cola → corrigir o CV de IA remoto igual (com o ok dele) → foto e capa novas.

**0l. Painel só no Mac (23/10):** banco, API **e site** em 127.0.0.1 — abre em qualquer rede pelo `http://localhost:3456` no próprio Mac; celular/outros aparelhos não. Studio desligado (`bash painel/studio.sh liga|desliga`), `bash painel/so-no-mac.sh` mostra o estado. Portões dados e interface APROVADOS. Falta: firewall (Carlos); acesso de fora só com o domínio + login.

**0k. Departamento de TECNOLOGIA do painel (22–23/10):** designer-de-produto · engenheiro-frontend · engenheiro-backend, portões `portao-interface` (design + interface, gerente) e `portao-dados`. 1.º ciclo GAUNTLET feito: dados APROVADO (v2), interface APROVADO (v3), `exigir painel` limpo. **Design system IMPORTADO (23/10):** artefato "korvu. painel" do Carlos (https://claude.ai/artifact/NXsnDGtogDFtQvSeLJVGrv) → `painel/design/` em PT-BR (livro `design-system.md`, tokens, componentes, prévias, `handoff.md`); **PORTÃO-DESIGN APROVADO (volta 3)**. Cópia exata em `painel/referencias/claude-design/korvu-painel-2026-10-23/`. Telas: o Carlos desenha no Claude Design (opção que entrega código); a Visão geral (outra sessão) é a próxima a entrar em `painel/design/telas/`. **Próximo:** Visão geral → portão → `engenheiro-frontend` (tokens + Geist + casca). Decidido por ele (23/10, decisões §5): retrato = foto realista; menu "Vídeos e portões" → "Produção de conteúdo" (5 fases). **`painel/design/` agora é da sessão "Korvu Painel overview interface"** (5 telas + ajustes no livro) até o próximo veredicto do portão. Contraste: ele aceitou `line-strong` #928874 e foco em `accent-ink` nos fundos claros (23/10) — a sessão do painel aplica; as outras 8 combinações ficam. S2: PI38 (fechar no próximo ciclo), PI39, PI40. Avisar: PD9 (painel aberto na rede local, firewall desligado). Detalhe no HANDOFF.

**0j. Painel web NO AR localmente (22/10):** `bash painel/iniciar.sh` → http://localhost:3456 (visão geral · equipe · vídeos e portões · desempenho). Supabase próprio em `painel/supabase` (portas 553xx). Sincroniza sozinho a cada 15 min (launchd `uk.korvu.painel`, log `_controle/logs/painel.log`); à mão: `uv run python painel/sync/sincronizar.py`. Nomes da equipe em `painel/equipe.yaml` (propostos, aguardam o Carlos). **Próximo:** `perfil.py` diário, retratos desenhados, domínio.

**0i. GAUNTLET LIGADO (22/10) — quem faz não aprova (`docs/gauntlet.md`, `CLAUDE.md` regra 13):** 5 portões-gerentes (opus): PAUTA `portao-pauta` · ROTEIRO `revisor-de-roteiro` · IMAGEM `portao-imagem` · CORTE `revisor-de-video` passagem 2 · PUBLICACAO `portao-publicacao`. O portão da área roda sozinho no fim de cada etapa, antes de qualquer coisa chegar ao Carlos; veredicto em `portoes.json`, vence se o arquivo mudar. **`montar_pacote.py` recusa sem os portões; `publicar.py` recusa sem selo e sem o PORTÃO-PUBLICACAO** — então todo pacote NOVO tem de passar pelos portões. Os 6 da fila de hoje são legado (`_controle/gauntlet-legado.json`, congelado). Sinais: `uv run python scripts/portoes.py estado`. **Próximo:** 1.º uso real no próximo vídeo; depois o painel web.

**0h. Painel web do projeto (22/10, etapa 0 — só arquitetura):** equipe (agentes com nome, cargo, retrato em ilustração editorial) + produção + desempenho IG/FB + memória. Next.js/TS em `painel/` + sincronizador Python + Supabase próprio (local → nuvem). Os arquivos são a fonte da verdade; o painel só lê. **Próximo:** Carlos aprova os nomes dos 17 agentes → `painel/ARQUITETURA.md` + base do Next.js → módulo Equipe. Decisão em `docs/decisoes.md` §5 (22/10).

**0e. Design system NOVO, editorial (21/10):** `00-marca/design-system/korvu-editorial.md` (fonte única dos tokens) — papel `#E7E4D9` + tinta `#111` + laranja `#E85002`, títulos em minúsculas com ponto em **Bricolage Grotesque 800** (escolha do Carlos), números "1.", carimbo de bolinha, fios de 0,5 pt; nada de degradê/sombra/canto/mono. **Aplicado:** (1) `scripts/gerar_material_pdf.py` (todo PDF de palavra-chave; teto agora **2 páginas**, blocos `:::colunas` e `---`); (2) cartão do CTA no Remotion (`CtaPalavra.tsx`, tokens `CTA`/`EDITORIAL` em `brand.ts`: "comenta" + "nobel." num cartão de papel). **Regras novas (decisões §4):** PDF curto — a entrega logo de cara + "como usar" em 3 passos; **sem o nome pessoal do Carlos** no material (só korvu / @korvu_oficial). PDF do LIVRO já refeito assim (2 págs). **Ainda no estilo antigo:** legendas ("Texto Selecionado"), título do hook (`Titulo.tsx`), cartelas e capas (Geist/Playfair) — próximo passo. **Modelo APROVADO pelo Carlos (21/10), com a palavra do CTA SEM ponto** ("comenta aula", nunca "aula."). **Sem carimbo** no CTA e no PDF (21/10). PDFs antigos (AULA, NOBEL, PRATO, FOTO, GOLPE, LISTA, AGENTE) continuam no layout velho até serem regerados.

**0f. 2.º rápido de comandos — `videos/2026-10-24-comando-secreto/` (21/10):** "Coloca sua foto no ChatGPT e escreve barra cinematic" → /goldenhour → /droneview → virada "Chamam isso de comando secreto. Mas a barra não muda nada" → neblina sem barra → **ESTILO** (FOTO continua do foto-da-loja; decisão em `docs/decisoes.md` §1, 21/10). **Roteiro v2 e PDF APROVADOS pelo Carlos (22/10)** (81 palavras, ~35 s; revisor APROVADO COM AJUSTES, aplicados), leitura + `historia-completa.txt`, PDF `material/comandos-de-estilo-para-fotos.pdf` (2 págs, 76 comandos + neblina, conferido nas prévias). **Próximo:** tirar a foto original e TESTAR os 4 pedidos num chat temporário (neblina sem barra gera? Enter com o menu do "/" aberto envia? rosto sobrevive ao /droneview — senão /polaroid?) → gravar a tela do Mac + baixar os 4 PNG → skill `tela-de-computador` → `fala-carlos.json` ("cinematic", "golden hour", "drone view") → gravar → `/editar`. Os outros comandos do PDF (/telephoto, /dollyzoom, /levitation, /particles…) ainda não foram testados.

**0d. Biblioteca de comandos do ChatGPT (21/10):** `01-ideias/pesquisas/2026-10-21-biblioteca-comandos.md` — fotos (~250 atalhos em 21 famílias, ⚡ = bom pro rápido), 22 combinações, 45 de produto, 30 de e-book, 20 de PDF, 14 ganchos de Reel e ordem dos módulos da futura página do curso. Base de todo "rápido de comandos" e de PDFs de palavra-chave. **Avisos que valem para roteiro/PDF:** barra não é função (a palavra é que funciona; "/" abre o menu de apps); Canvas saiu dos modelos atuais (28/05/2026) — PDF pelo caminho .docx → PDF; plano grátis = 3 envios de arquivo por dia. **Próximo:** Carlos escolhe os ganchos (§6) → testar no ChatGPT os comandos escolhidos (os marcados PRINT não têm fonte indexada) → conferir no app os estilos oficiais da aba Imagens. A página do curso ainda não existe.

**0d. Design system editorial + CTA novo (21/10, outra sessão):** o Carlos achou o PDF "com a cara do Claude Code" e o CTA com fonte desagradável → `00-marca/design-system/korvu-editorial.md` (fonte única: papel/tinta/laranja, Bricolage Grotesque + Inter), `gerar_material_pdf.py` com o CSS novo (PDF curto: máx. 2 págs, entrega primeiro, como usar em 3 passos), `CtaPalavra.tsx` sem ponto depois da palavra. **Aprovado por ele.** O PDF dos 50 comandos do livro-chatgpt já foi regerado nesse modelo (2 págs) e o render do livro-chatgpt sai com o CTA novo. Pendente dessa frente: levar o sistema para legendas/título/cartelas/capa e regerar os PDFs antigos. Detalhe: HANDOFF (7) de 21/10 e `docs/decisoes.md` §4.

**0c. LIVRO-CHATGPT (1.º rápido de comandos) — AGENDADO (21–22/10):** `06-publicar/2026-10-23-livro-chatgpt` (B, dom 25/10 19:00 IG+FB) · `-a` (ter 27/10 21:00 IG) · `-l01c` (qua 28/10 21:00 IG, hook "Você nunca mais vai ler um livro sem fazer isso no ChatGPT") · `-l01c-a` (dom 01/11 19:00 IG, o Carlos fala esse hook em tela); Trial MANUAL, confirmados por ele (`confirmar: false`), publicação automática pelo launchd; cada um com a SUA capa (cor certa, headline e pose próprias). Palavra LIVRO → PDF de 2 págs (design editorial). **Regras do formato (21/10, decisões §3/§4):** réplica do molde viral mudando só a imagem · cartão do comando NO PEITO (1000×330) · resultado inteiro em `full` · SEM legenda karaokê, SEM título do hook, SEM véu escuro · música cinematográfica · cor = `aplicar_cor.py` sempre (cadeia WB-fixo apagada; folha branca opcional) · skill `tela-de-computador` para gravação de tela do Mac. **Próximo:** conferir no app em 25/10; métricas aos 5 dias (30/10) → analista compara abertura (B×A) e hook (L01×L01C) em `testes-abertura.md`; 1.º comentário LIVRO real → direct. Dívidas: `capa-reels` no design system novo; `render_capa.py` N variantes; `pose_capa` do roteiro ≠ gravado.

**0b. Teste A/B da abertura em TODO vídeo (17/10):** A = Carlos desde 0, B = conteúdo primeiro; os dois Trial MANUAL, B primeiro (IG+FB), A ≥ 24 h depois (só IG); vagas novas dom 19:00 / ter 21:00 / qua 21:00. `_controle/testes-abertura.md`. Na B o Carlos entra aos **~10 s** (depois do gancho inteiro). Fei-Fei **agendada e conferida**: B dom 18/10 19:00 (IG+FB, entra em 8,88 s) · A ter 20/10 21:00 (só IG); os dois Trial MANUAL. Falta automatizar o par no pipeline. B do Hassabis/Hinton **cancelada** (Carlos, 17/10: "não precisa mais") — A/B só em vídeos novos. Fei-Fei = C5 **feita e conferida** (17/10 08:19: quadros 0–4,8 s = Fei-Fei/Bloomberg, Carlos entra em 5,0 s; 1080×1920 25 fps, 168,5 s); publica 18/10 19:00. Prints do app aos 5 dias (23/10) → `testes-abertura.md`.

**0a. Prints do app (17/10):** metade sai nos primeiros ~5 s; quem passa dos 20 s fica até o fim; Hassabis 62 % não seguidores (RU 21 % + PT 14 %), 0,3 % salvamentos, 0 seguidores. Decisão: Reels só IA (vida pessoal nos Stories), não alimentar a bolha, alternar PERFIL × PRÁTICO — tudo em `_controle/estrategia-de-alcance.md` §2. **Próximo vídeo depois da Fei-Fei: PRÁTICO** (prompt/passo a passo → PDF).

**0. Perfil / sair da bolha (16/10):** `_controle/auditoria-perfil.md` (agente `auditor-de-perfil`, dados `scripts/perfil.py`). 55,8 % dos seguidores na Guiné-Bissau, mas o RU já é 38,9 % de quem foi alcançado; Página FB com 0 seguidores (por isso não entrega). **Nome e bio já trocados (16/10 noite, conferidos pela API).** **Próximo:** Carlos fixa 3 Reels e arquiva as fotos de 2018/2023 NO APP (a web não tem essas opções), decide P1–P5 (geotag Londres, hashtags locais, corte ≤ 90 s p/ FB, "Londres" na legenda, Trial + compartilhamento automático) e manda os prints pedidos. **Regras de alcance DECIDIDAS (16/10 tarde): `_controle/estrategia-de-alcance.md`** — todo roteiro segue (virada até ~20 s, palavra 2×, salvar, **todo vídeo ≤ 90 s, um só para IG e FB** — sem versão curta separada); Fei-Fei (hoje ~156 s) vai ser reescrita com elas e cair para ≤ 90 s. Reauditar ~16/11 com a mesma base.

**0b. Voz do Carlos CALIBRADA (17/10):** `00-marca/voz-carlos.md` (status calibrado, 4 gravações: Fei-Fei + Hinton + Hassabis + ChatGPT) — **`wps_roteiro` = 2,1** (90 s ≈ 185 palavras, máx. 190; a conta "190–210" estoura), 13 padrões de como ele reescreve o texto (sujeito explícito, infinitivo, "dele", corta "é que", "E aí"/"Só que", CTA "Comenta a palavra X que eu vou te enviar…") e §10 "Para o roteirista" (8 regras). `00-marca/fala-carlos.json` corrigido (a chave `"a i"` fazia todo "a" virar "ia" no alinhador em roteiro com IA) e ampliado. Ferramenta: `comparar_fala.py` (skill roteiro-reels). Fei-Fei já somada (2,11 wps nos takes; alinhada às 02:02/02:04 com o dicionário corrigido). **Próximo:** quando a EDL da Fei-Fei existir, `comparar_fala.py` de novo para o wps no corte; na edição, conferir que L04/L06/L08/L09/L10/L15/L17/L29 estão no corte (a 1.ª rodada do align as perdia por causa da L07 "Ela.").

**1. Hinton (`videos/2026-10-20-geoffrey-hinton/`) — REPUBLICADO 15/10 11:44 com a cor da marca** (cadeia do Hassabis; a 1.ª publicação saiu com WB neutro).
IG Trial Reel https://www.instagram.com/reel/Degw3KFDvcO/ · FB https://www.facebook.com/reel/1033107573077272/ · pacote em `07-publicados/`.
Reel antigo apagado pelo Carlos no app (15/10, conferido pela API). **Próximo:** comentários NOBEL (direct automático) e métricas aos 5 dias (20/10).

**1b. Fei-Fei Li — PAR A/B agendado: B (conteúdo primeiro) dom 18/10 19:00 IG + FB em `06-publicar/2026-10-20-fei-fei-li/`; A (Carlos desde 0) ter 20/10 21:00 só IG em `06-publicar/2026-10-20-fei-fei-li-a/`; as duas Trial MANUAL (`_controle/testes-abertura.md`). 17/10 ~12h: o Carlos achou que apareceu cedo demais na B (5 s) → B v2 em render: a Fei-Fei cobre L01–L02 (Y55 + Y67) e ele entra na L03 (8,88 s); A v2 idêntica dali em diante (CAPA-01 passou para a L04, Y01 para a L05, E02 saiu). v3.2 (crédito no rodapé; L22 em pilha com movimento) já está nos DOIS pacotes de `06-publicar/` (qa_check PASS). Versões B do Hinton e do Hassabis: card de sessão proposto (regra em decisões §5b 17/10).** Não mover nem re-renderizar sem avisar; a publicação é automática (launchd).
Vídeo v3.1 (168,5 s; EDL v13 aprovada; legendas da fala real; cor = cadeia do Hassabis; música opção 1); capa nº 1; PDF AULA. Extras em **4 layouts** (full / pilha / solo / split —
**padrão dos próximos perfis**, `docs/decisoes.md` 17/10), camada `edicao/extras-v2/overlays-v3.json` (`montar_v3.py`; tabela em `edicao/sequencia-extras.md`). Remotion: `modo: "pilha"` e `modo: "solo"` (`docs/contratos.md` §4).
**Próximo:** publicação automática 18/10 19:00 → comentários AULA (direct) → métricas aos 5 dias (23/10), comparando a abertura C5 com os controles. Avisos de acabamento no `qa/relatorio.md` (legenda grande passa 7–21 px de y 1250 em 3 palavras; resto do chip CBS em 2 pilhas) — se quiser polir: `A_CBS.altura` 765 e quebrar "da inteligência artificial" em 2 linhas.
Armadilhas: `edl.py` sempre com `--recalcular` (12 linhas manuais); `edl.json.palavras_saida` = fala real (original em `edl.antes-legendas.json`); um `solo` precisa de `fonteLargura/Altura` (vem do gerar_props).

**1c. Jensen Huang (`videos/2026-10-18-jensen-huang/`) — roteiro v1 narrativo APROVADO (17/10), PDF PRATO pronto, 51 fotos; grava 18/10.**
182 palavras (~88 s), PRATO dito na L05 (~24 s) e na L18, pedido de salvar na L17, par A/B na abertura (B: conteúdo até o fim do gancho, Carlos na L03; A: desde 0). Leitura em `roteiro-limpo.txt`/`teleprompter.txt`/`monitor-chatgpt.txt`.
PRONTOS: `historia-completa.txt`, `material/youtube/` (126 cortes, `catalogo-insert.md`), `edicao/sequencia-extras.md` + `qa/sequencia-extras-contato.jpg` + `edicao/extras-v2/montar_v1.py` (A e B; tempos estimados até a EDL). Decisões do Carlos pendentes (ver HANDOFF 17/10 meio-dia): L04 placa × ele inteiro; 1.º quadro da B; "5 tri" full × solo; capas na L14; Musk fora. **Depois da gravação:** `/editar` → EDL → `/renderizar` com os 4 layouts (`montar_v3.py` da Fei-Fei como modelo) e as DUAS versões (A e B) → QA → pacote → publicar depois da Fei-Fei (20/10+).

**2. Os outros 4 roteiros** (foto-da-loja FOTO, golpes GOLPE, 15-coisas LISTA, agente AGENTE) estão aprovados, com PDF,
material em vídeo cortado e `historia-completa.txt` — **MAS ainda no formato antigo (picado)**. **Próximo:** reescrever cada um no padrão
NARRATIVO (`00-marca/modelo-roteiro-narrativo.md`) com o roteirista, mantendo palavra-chave, PDF e extras (religar às linhas novas),
revisar, regenerar leitura e a parte "momentos" da história completa. Agente em 3 passos: Gems viram "skills" em 17/11/2026 (decidir com o Carlos: mencionar, esperar ou trocar ferramenta).

**3. Regras novas desta sessão (todas em `docs/decisoes.md`):** roteiro narrativo · vídeo é o carro-chefe (buscador automático no `/novo-video` 4b,
sem teto de trecho, áudio baixo/mudo + crédito, sem licença quando narra por cima) · `historia-completa.txt` em todo roteiro (6b) · palavra-chave
curta (≤ ~6 letras) · cartão grande do CTA (laranja #E85002, aprovado) · 2.º pedido falado (enviar/salvar) permitido · legenda só PT · público =
lusófonos na Europa/RU que não aprendem sozinhos (imersão presencial), NÃO britânicos · publicar SEMPRE IG + FB · Trial Reels por padrão ·
métricas aos 5 dias (`analista-de-metricas`) · material = sempre PDF (`produtor-de-material`).
Números em ALGARISMO no roteiro (2024, não "dois mil e vinte e quatro") — Hinton já corrigido. **Não perguntar ao Carlos** o que já está decidido (ele pediu: "essas dúvidas não podem existir no processo").

**4. Pesquisa de referências:** `01-ideias/pesquisas/referencias-instagram/MESA.md` (7 regras dos campeões, ideias por linha). Série de perfis: `01-ideias/pesquisas/2026-10-13-mesa-perfis.md` + dossiês em `perfis/`.

**5. Automação ligada no Mac (launchd):** publicar (15 min), comentários (2 min), métricas (09:30), painel (15 min, `uk.korvu.painel`). Token da Página: expira nunca; renovar acesso aos dados até ~11/01/2027.

> Os blocos abaixo são histórico do dia; onde divergirem do bloco acima, **vale o de cima** (ex.: foto-da-loja agora é FOTO, launchd já está instalado).

# Vídeo 2026-10-21-foto-da-loja — roteiro aprovado (14/10)
Linha 2 (rápido). Roteiro + PDF PROMPT (`material/6-pedidos-fotos-do-negocio.pdf`) prontos. **Próximo:** o Carlos testa os 6 pedidos
no ChatGPT do celular com a foto real (conta paga ou 2 dias: limite de imagens), baixa os PNG (E02–E14), grava principal + tela → `/editar`.
Se trocar um pedido: ajustar a linha da fala e regerar o PDF. Palavra PROMPT = mesma do `2026-09-16-chatgpt-contexto` (semanas diferentes).

# Material do CTA = sempre PDF — 13/10

Roteiro com `cta_tipo: palavra-material` marca `cta_palavra` + `material` + `material_titulo` (o parser recusa sem eles) →
**`produtor-de-material`** (logo depois do roteiro aprovado, em `/novo-video`) escreve `material/_fonte/material.md` e roda
`scripts/gerar_material_pdf.py` → `material/<arquivo>.pdf` + prévia PNG → `montar_pacote.py` leva **só o PDF** (+ `material_titulo`)
→ `publicador`/`agendar` põe `post.json.material = {palavra, arquivo, titulo, url}` → `publicar.py` sobe **só esse PDF** para o R2.
Nenhum vídeo em andamento usa palavra-chave ainda; o 1.º a usar estreia o fluxo. `scripts/md_para_pdf.py` (antigo) ficou, mas não é mais citado.

# Automação Instagram — 09/10

**Decisão do Carlos:** só entregar material (comentário com palavra → resposta pública → direct com link + convite para curtir/seguir). Sem CRM, sem conversa. Tudo em **`automacao-meta/ARQUITETURA.md`**.

| Peça | Estado |
|---|---|
| `scripts/publicar.py` (postar IG+FB) | 62/62 offline · **nunca publicou de verdade** |
| `scripts/responder_comentarios.py` (palavra → direct + resposta) | **novo**, 25/25 offline (`tests/comentarios/test_responder.py`) · nunca rodou de verdade |
| `automacao-meta/respostas.yaml` | textos e limites — o Carlos pode editar |
| launchd (`uk.korvu.publicar` 15 min + `uk.korvu.comentarios` 2 min) | `instalar.sh` instala os dois · **não instalado** |

**Meta configurada em 13/10 ✅** (chat dedicado):
- App **KORVU 20 AI** (modo Ativo, portfólio KORVU_UK), caminho **login do Facebook** (`graph.facebook.com`). O "korvu 20 v2" não é usado.
- Instagram **@korvu_oficial** (profissional, Criador digital, pública) ligado à Página nova **"Korvu"** (criada em 13/10). A Página Korvu.uk foi desligada do @korvu.uk antigo.
- Token no `.env` = **token da Página Korvu, tipo PAGE, expira nunca**, com `instagram_basic`, `instagram_content_publish`, `instagram_manage_comments`, `instagram_manage_messages`, `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`, `business_management`. Nada enviado para App Review.
- Webhook do n8n (`korvu.app.n8n.cloud`): todos os campos com a assinatura cancelada (lado "login do Instagram"); no lado "login do Facebook" não havia nenhum. A Sarah/n8n já estava desligada (Carlos).
- Verificado: `publicar.py verificar-tokens` → conta @korvu_oficial, Página Korvu, tokens PAGE válidos sem expiração, nenhum escopo em falta; `responder_comentarios.py verificar` → exit 0.
- ⏰ **Até ~11/01/2027:** a Meta pede renovação do "acesso aos dados" a cada 90 dias. Repetir no Graph API Explorer: Generate Access Token → estender → `me/accounts` → token da Página novo no `.env`.

**13/10 — 1.º TESTE REAL ✅ (Hassabis):**
- R2 copiado do `Korvu 2.0-Project-app/.env` (bucket `instagramimages`, público em `media.korvuai.com`).
- Publicado: IG https://www.instagram.com/reel/DecK5CDk34q/ · FB https://www.facebook.com/reel/1350369576981188/ → `07-publicados/2026-09-17-demis-hassabis/`.
- Palavra **KORVU20** → `material/documentario-the-thinking-game.pdf` (link oficial do documentário no YouTube). Comentário da @korvu.uk → **direct ✓ + resposta pública ✓**.
- Duas correções no código: (1) `publicar.py` envia o vídeo do Facebook do disco (rupload binário), porque o `file_url` levava 403 da Cloudflare; (2) `responder_comentarios.py` manda o direct por `/{META_PAGE_ID}/messages`, porque `/{ig-user-id}/messages` dá erro #3 no login do Facebook. Testes 62/62 e 25/25.
- Os arquivos de estudo (`dossie.md`, `fontes.json`, `obra*.json/md`) saíram do pacote para não irem ao R2 público; as cópias ficam em `videos/2026-09-17-demis-hassabis/material/`.

**launchd instalado em 13/10** (`uk.korvu.publicar` 15 min, `uk.korvu.comentarios` 2 min; 1.ª passagem automática ok, sem reenviar).
**Métricas (13/10):** `scripts/metricas.py` pronto (32/32 offline) → `metricas.json` + `_controle/metricas.md` → agente `analista-de-metricas` → `_controle/aprendizados.md` (roteirista/estrategista leem). **Bloqueado por permissão:** o token não tem `instagram_manage_insights` (IG) nem `read_insights` (Página) — a leitura real de 13/10 só trouxe curtidas/comentários. Depois de trocar o token: `uv run python scripts/metricas.py verificar` → `bash scripts/launchd/instalar.sh uk.korvu.metricas` (launchd 09:30, **não instalado**). A API só dá tempo médio assistido, não a curva.
**Próximo passo:** testar um comentário de uma conta **que não seja do Carlos** (a @korvu.uk é dele: o direct pode ter passado por ele ter papel no app).
⚠ Ainda incerto: direct para quem não tem papel no app. Se falhar, o script para com erro de permissão (sem descartar ninguém) e é preciso App Review.

**`historia-completa.txt` pronto nos 6 roteiros (14/10)** — texto para ouvir antes de gravar. Palavras: NOBEL, AULA, FOTO, GOLPE, LISTA, AGENTE. Publicação: sempre IG + FB.
**Material em vídeo pronto nos 6 roteiros (14/10)** — `brutos/extras/` + `material/youtube/catalogo.md` (Hinton 69 s de vídeo dele). `baixar_obra.py` sem teto.
**Hinton = gravação de hoje (14/10)**, palavra **NOBEL**; cartão do CTA pronto no Remotion (`CtaPalavra`).
**6 roteiros prontos para gravar (14/10)** — todos com revisão APROVADA e PDF do CTA em `material/`: `2026-10-20-geoffrey-hinton` (ENTREVISTA), `2026-10-20-fei-fei-li` (PALESTRA), `2026-10-21-foto-da-loja` (PROMPT), `2026-10-21-golpes-com-ia` (GOLPE), `2026-10-22-15-coisas-ia-negocio` (LISTA), `2026-10-22-agente-3-passos` (AGENTE). Datas do slug provisórias. Pendentes do Carlos: exceção do 2.º pedido falado (enviar/salvar) em 5 deles; lista na tela já no hook (15 coisas); Gems do Gemini acabam nas contas pessoais em nov/2026 (agente 3 passos); testar os pedidos (foto da loja, itens 6 e 15 das 15 coisas) e a legenda do TED/60 Minutes antes de gravar.
**Referências (14/10):** 45 Reels campeões dos 9 perfis indicados pelo Carlos + ~35 canais de fora analisados (frames + transcrição, download anônimo). Síntese para decidir: `01-ideias/pesquisas/referencias-instagram/MESA.md`. **Aguarda o Carlos escolher os primeiros vídeos** e decidir sobre cancelar o A/B de legenda (público fala português).
**Série de perfis (13/10, noite):** 8 candidatos em `01-ideias/pesquisas/2026-10-13-serie-perfis-ia.md`; dossiês prontos de Fei-Fei Li, Jensen Huang, Geoffrey Hinton, Andrew Ng e João Moura em `01-ideias/pesquisas/perfis/`. Resumo para decidir: `01-ideias/pesquisas/2026-10-13-mesa-perfis.md`. **Aguarda o Carlos escolher** → `/novo-video` (roteirista até 90 s, CTA falado + produtor-de-material).
**Próximo conteúdo (pedido do Carlos, 13/10):** engenharia reversa de apps com o Claude Code (recriar/clonar aplicativos). Briefing em `01-ideias/proximo-tema-engenharia-reversa.md`; pesquisa ainda não iniciada (ele dispara quando voltar).
**Token (13/10, 18:41):** token da PÁGINA Korvu, expira nunca, com as 10 permissões (+ `instagram_manage_insights`, `read_insights`). Dica para renovar: basta o Carlos colar no `.env` o token de USUÁRIO longo; o Claude deriva o da Página com `me/accounts` por script, sem imprimir.
**Métricas ligadas (13/10):** `uk.korvu.metricas` instalado (09:30/dia); 1.ª leitura real ok (Hassabis: 136 views, alcance 70, 14,6 s = 25% assistido).
**Trial Reels ligados (13/10):** `trial_padrao: SS_PERFORMANCE` em `_controle/calendario.md` → todo `post.json` novo nasce com `instagram.trial` (testes 63/63).
**Legenda = teste A/B EN × PT (decidido 13/10):** alternar por vídeo; falta implementar a versão EN no `legendas-animadas` e marcar a língua no pacote/métricas. Dublagem Meta AI: testar manualmente no app num Reel.
**A estruturar com ele:** Facebook via compartilhamento automático do Instagram vs. post separado pelo `publicar.py` (não ligar os dois → Reel duplicado na Página).

---

# Continuar daqui — estado em 2026-10-01

## 0. Novo em 01/10 — material do YouTube e música de fundo

| Peça | Estado |
|---|---|
| `scripts/buscar_youtube.py` + agente `buscador-de-videos` + `/buscar-videos` | **testado** (busca, baixa H.264, momento, trecho 25 fps, `catalogo.md`). Qualquer vídeo pode ser baixado para análise (decisão 01/10); na tela valem as condições do §5 de `decisoes.md` |
| `baixar_obra.py` | o teto de citação agora soma os trechos do catálogo do YouTube (teto do Reel, não da fonte) |
| `scripts/gerar_musica.py` + agente `produtor-musical` + `/musica` | mixagem **testada** com trilha sintética sob o final-A do Hassabis (−14,1 LUFS, TP −1,7, música ~27 dB sob a voz, fade-out ok; ducking não medido — o A não tem pausas). **Geração funcionando** (chave no `.env`, permissões Music Generation + Speech to Text; sem `user_read`, então `/v1/user/subscription` dá 401 — é esperado). Hassabis: `musica/opcao-1.mp3` (piano/cordas) e `opcao-2.mp3` (eletrônica leve), mixadas em `edicao/final-A-musica-1/2.mp4` (−14,1 LUFS; música ~15 dB sob a voz) |

**Próximo passo:** o Carlos escolher a opção 1 ou 2 (ou pedir outro clima/volume) → `gerar_musica.py escolher`.

### Hassabis versão D (02/10) — a mais nova
`edicao/final-D-musica-1.mp4` (piano/cordas) e `final-D-musica-2.mp4` (eletrônica), + `-leve`, QA PASS. Mesmo corte/cor da C; extras trocados por cenas CALMAS (saíram E31/E33/E34/E35/E36 — gesticulação) e L07 = a partida contra o Lee Sedol (E45). Tabela no `roteiro.md`. Ele escolhe a música; depois `gerar_musica.py escolher` e limpar as versões que sobrarem (A/B/C/D) com `limpar_video.py`, perguntando antes.

**02/10:** split sem faixa preta (extra em y 0–608, Carlos 608–1920, legenda 715) — `final-D-musica-1/2` re-renderizados com isso, QA PASS. Ele aprovou o nível da música; falta dizer QUAL das duas.

**08/10 — as 3 capas finais geradas** (`--subir-frame 290`: a foto sobe e o título sai do queixo; opção nova no `render_capa.py`/`Capa.tsx`, junto com `--tamanho`). No pacote: `capa/capa-1-quem-e-o-genio.png`, `capa-2-menino-do-xadrez.png`, `capa-3-conheca-o-homem.png` + `grade-comparacao.jpg`; `capa.png` = opção 1 PROVISÓRIA (a capa B antiga continua como `capa-B.png`). **07/10 — CAPA DO HASSABIS: falta ele escolher entre 3 headlines** (`capa/grade-comparacao.jpg`; títulos em `capa/titulo-A/C/D.json`): A "Quem é o gênio que ganhou o Nobel com IA" · C "O menino do xadrez que ganhou o Nobel com IA" · D "Conheça o homem que ganhou o Nobel com IA". Ele aprovou as três ("ficaram ótimas"). Depois da escolha: resolver o texto encostado na mão/queixo (letra menor ou outro quadro da pose), copiar para `capa/capa.png` e remontar o pacote. A capa B antiga continua no pacote até lá. **NÃO limpar nenhuma versão deste vídeo** (pedido dele).
Regra registrada: 3 capas = 3 HEADLINES DIFERENTES (agente `designer-de-capas` passo 4, skill `capa-reels`, `/capa`); `render_capa.py` agora gera `grade-<V>.png` + `grade-comparacao.jpg`.

**02/10 — HASSABIS PRONTO (versão E).** Pacote em `05-render-pronto/2026-09-17-demis-hassabis/` (vídeo = `edicao/final.mp4`, capa B como `capa.png`, QA do revisor PASS + correção do E44 anotada). status `pronto`. **Não publicado** — decisão dele, com 2 avisos: 47,6 s de terceiros em 57,9 s (teto 30 s) e a L11 do Nobel não gravada (o hook promete o Nobel).
E44: a moldura preta/vinheta do documentário foi recortada (original em `material/obra/trechos-originais/`). Rodar `cropdetect` em todo extra antes do render — clipe com moldura vira faixa preta.
`limpar_video.py` só preserva a capa se ela se chamar `capa.png` (apagaria `capa-B.png` sozinha) e NÃO vê as versões final-A/B/C/D/E: a limpeza delas está pendente da autorização dele.

**02/10 — música 1 escolhida** (`musica.json` escolhida=1). Final aprovado: `edicao/final-D-musica-1.mp4` (cor D = `cor/corte-cor-D.mp4`, igual ao `corte-cor.mp4` atual).
**Teste de cor E** (`final-E-cor.mp4` + `-leve`, QA PASS): a D + balanço de branco POR ARQUIVO medido na CAMISA BRANCA (referência neutra), só para quem destoa (0970/0971 esverdeados, 0974/0975 levemente), luma preservada. Variação de R/G da camisa entre linhas 0,106 → 0,046. Grafo: `cor/filtro-E.txt`; cor: `cor/corte-cor-E.mp4`. ⚠ `render-remotion.mp4` atual é o da E.
⚠ **Máscara de pele YCrCb mede as LENTES VERMELHAS dele** nos planos fechados (R/G sobe com o zoom): a tentativa de casar a pele linha a linha deixou a L04 MAIS verde. Para balanço de branco use a camisa branca, não a pele.
Se ele escolher a E: adotar camisa como referência no `cor_pele_casada.py` (e generalizar o caminho fixo do Hassabis).

### Hassabis versão C (01/10, noite) — o que ele vai avaliar
`edicao/final-C-hassabis.mp4` (+ `-leve`), 57,9 s, QA técnico PASS, **sem música** ainda.
- **Ritmo:** EDL da A apertada com `scripts/apertar_ritmo.py` (pausas 10,4 → 5,8 s; 61,2 → 57,8 s). O que saiu era silêncio (3/333 janelas de 10 ms acima de −40 dBFS).
- **Extras:** E30–E39, o Hassabis em cena em cada linha L01–L10 (tabela no `roteiro.md`; a tabela da A ficou em `edicao/roteiro-versao-A.md`). Clipes estendidos para cobrir a linha inteira (sem "sobe e desce"); E30 estendido pelo COMEÇO por causa do limite das 23:07. Total citado ~51 s: acima do teto de 30 s — teste autorizado por ele, mas o número tem de ir à frente dele.
- ⚠ **O homem careca de óculos em E32/E33/E39 É o Hassabis** (fase recente; legenda do documentário: "I applied to Cambridge…", "HASSABIS: I just felt disappointed"). Eu quase troquei achando que era outra pessoa — conferir pela legenda/transcrição, não pela cara.
- `edicao/edl.json` = versão C. A e B intactas (`edl-A-71pct.json`, `edl-continuo.json`, `final-A-71pct.mp4`, `final-B-100pct.mp4`).
- **render_corte.py mudou:** o áudio do corte agora é montado em numpy (`montar_audio`) e entra no ffmpeg como UM arquivo. A cadeia de 40+ entradas `-ss/-t` + `acrossfade` falhava de forma intermitente no ffmpeg 7.1 ("Could not open encoder before EOF"; mesmo trecho passava e falhava). Arquivo intermediário: `edicao/.audio-montado.wav`.
- **edl.py:** margens padrão apertadas para os próximos vídeos (PRE 0,06 / POS 0,08 / PAUSA_ALVO normal 0,08 / PAUSA_INTERNA 0,25 / PAUSA_RESTA 0,12); teste sintético ajustado.
- **Suítes (01/10, depois das mudanças):** clássica 45/47, monitor 26/28. Margens, voz da IA fora do corte e áudio montado: tudo PASS. As 4 falhas NÃO vêm das mudanças de hoje: 2 testes desatualizados (esperam "segurar o último quadro", contra a decisão de 19/09, e leem o roteiro do ChatGPT no formato antigo com TELA) + 2 no `align.py` (L03 do monitor escolhe T1 em vez do retake T2; "de novo" da IA fora dos separadores) — o `align.py` não foi tocado e não usa nada do `edl.py`. Investigar à parte.
- Cor: mesma cadeia da A (`aplicar_cor` + `cor_pele_casada`). Os arquivos da regravação (praq0974/75/76) têm preto 14–15 IRE contra 5,5–6 dos primeiros; a curva fecha só esses três. **A reclamação de cor dele ainda não foi tratada a fundo** — próximo assunto.
**Também pendente:** a cor do take que ele regravou no Hassabis destoa do primeiro — corrigir **por fonte** e no mínimo (`cor_pele_casada.py`, que ainda tem os caminhos do Hassabis fixos; regra 11).
Obs.: sem a chave, a transcrição também tem rodado no modo local (mlx), não no Scribe.

---

# Estado em 2026-09-19

> **Leia antes de tocar em qualquer coisa:** `docs/decisoes.md` (o que o Carlos decidiu e por quê — 63 linhas,
> vale sobre o seu instinto) e `CLAUDE.md` (regras do projeto). Este arquivo é o **estado**, não a regra.

---

## 1. A ÚNICA COISA QUE ESPERA POR ELE

**Hassabis: escolher entre a versão A e a versão B.** As duas estão renderizadas, com áudio, ritmo, cor,
legendas e transições **idênticos** — a única diferença é quanto documentário fica na tela:

| | arquivo | documentário | como fecha |
|---|---|---|---|
| **A** | `edicao/final-A-71pct.mp4` | 43 s de 61,2 s (**71%**) | ele em tela cheia no payoff e no CTA (11 s) |
| **B** | `edicao/final-B-100pct.mp4` | 61 s de 61,2 s (**100%**) | documentário até a última palavra |

As EDLs correspondentes: `edicao/edl-A-71pct.json` e `edicao/edl-continuo.json`. **`edicao/edl.json` está com a A.**
Para trocar: copiar a EDL escolhida por cima de `edl.json` → `gerar_props.py --sem-titulo` → `render_reel.py`
→ `audio.py` → `qa_check.py`.

**O que dizer a ele se perguntar:** 62–100% de material de terceiros passa muito do teto de 30 s que ele mesmo
autorizou (`docs/decisoes.md`). Ele chamou isto de teste e disse que pode regravar. A decisão de publicar é
dele, com o número à frente — não nossa por omissão. Se quiser baixar para ~30 s, a ordem recomendada é tirar
**E08** (Go, redundante com o E07), **E10** (gráfico ilegível em 4 s num telemóvel) e **E11** (apontamento da
UCL) — **tirando do roteiro, não apagando de `brutos/`**.

## 2. Estado dos vídeos

| Vídeo | Estado | O que falta |
|---|---|---|
| **2026-09-16-chatgpt-contexto** | `edicao/final.mp4` 53,7 s, cor v5, capa pronta | era teste de cor; **não publicar**. A L02 não foi gravada e o CTA é o improvisado dele |
| **2026-09-17-demis-hassabis** | duas versões prontas, QA PASS | **a escolha dele** (§1). A **L11 (Nobel) não foi gravada** e o hook promete Nobel — o print E03 está reservado para ela |
| **2026-09-17-jacob-coxon** | roteiro pronto (151 palavras) | ele gravar; falta o print da thread do X (`E01`) — o print automático leva 403 |

## 3. A outra sessão (`content-ai-72`)

Trabalha na **obra** (`material/obra/`, `brutos/extras/`, `scripts/baixar_obra.py`, agente `curador-de-obra`).
`edicao/`, `roteiro.md` e `edl.json` são desta sessão. A divisão funcionou bem; fale com ela por `SendMessage`.
**Nem toda mensagem chega** — a primeira dela nunca chegou. Se algo parecer em falta, confirme em vez de assumir.

Ela tem os 15 trechos cortados (4 longos + 11 curtos), todos mudos e a 25 fps nativos. O mapa verificado está
em `material/obra-mapa-trechos.md`. Três limites do material, descobertos errando:
- o xadrez **não pode passar de 23:07** (corta para uma entrevista do pai, com tarja de nome);
- o Go tem **legendas embutidas em inglês** antes de 18:09, que competiriam com as nossas;
- a proteína só lê como proteína até ~46:43; depois vira partículas abstratas. **Aparar pelo fim.**

## 4. Ferramentas novas desta sessão (em `scripts/`)

| Script | O que faz | Quando usar |
|---|---|---|
| `cor_pele_casada.py` | Casa a **pele** entre arquivos e fecha o **preto** de quem destoa, numa passagem só a partir do corte de 10 bits | Sempre que a gravação vier em **várias partes**. Rodar **depois** do `aplicar_cor.py`, **uma vez só** |
| `apertar_ritmo.py` | Corta o ar morto: margens no mínimo e pausas internas encurtadas | Quando ele disser que "a pausa deixou o vídeo morto" |
| `extras_continuos.py` | Monta a variante com a metade de cima sempre ocupada | Só a pedido — dispara o tempo de citação |

⚠ **`cor_pele_casada.py` tem os caminhos do Hassabis fixos no código.** Generalizar antes de usar noutro vídeo.

## 5. Armadilhas já conhecidas (não repetir)
- **Hinton publicado: a foto `F20-hinton-fei-fei-li-conversa-chm.jpg` NÃO tem o Hinton** — é a Fei-Fei com Tom Kalil (CHM, 17/09/2024). Entrou no overlays-v3 (L16, ~91–95 s, "10 anos no Google"). Conferir a legenda da fonte antes de pôr uma foto como "pessoa X".

- **Verificar a coisa CERTA.** Compilar o TypeScript não prova que a correção funciona — só que os tipos batem.
  O render morria em execução (`inputRange must be strictly monotonically increasing`) e eu dei por concluído.
- **Erro em pipe some.** `comando | tail -1` devolve o código do `tail`: o `set -e` não dispara, o script segue
  e sai arquivo NOVO com conteúdo VELHO. Mandei dois vídeos ao Carlos dizendo que estavam corrigidos e não
  estavam. Use `test ${PIPESTATUS[0]} -eq 0 || exit 1`.
- **Conferir no ponto do defeito, não perto dele.** Ele reclamou das TROCAS entre cenas extras; eu conferi os
  segundos dos prints dele. Só apareceu quando extraí quadro a quadro (0,04 s) nas 12 emendas.
- **Máscara de pele YCrCb dá falso positivo** em madeira clara (tabuleiro de Go) e em tons quentes. Boa para
  medir a pele DELE num close; ruim para decidir "há pessoa neste plano".
- **Não matar um `ingest.py --force` a meio**: deixa o intermediário truncado e o render falha com "Invalid
  data found". Conferir com `ffmpeg -xerror -t 3 -i <fonte> -f null -` e refazer só o arquivo partido.
- **Nunca medir em cima do próprio resultado**: rodei a correção de cor duas vezes e a segunda, medindo o
  arquivo já corrigido, concluiu que não era preciso nada e desfez o conserto da primeira.
- **zsh não divide palavras**: `set -- $var` não funciona; `--include=*.md` precisa de aspas; `timeout` não existe.
- **`file://` precisa de caminho absoluto** (`capturar_animacao.mjs`).
- **archive.org recusa conexão desta máquina** (TLS): "não achei" ≠ "não existe".
- **Wikimedia Commons exige `gsrnamespace=6`**; sempre rodar um termo de controle antes de acreditar num resultado vazio.
- **`criar_look.py --base`**: os padrões agora são neutros — antes ele reaplicava a curva em S e engolia o ajuste.
- **Ao medir movimento entre quadros**, os vizinhos têm de vir do **mesmo arquivo** da amostra.
- **`status: parafrase` não quer dizer "improvisou"** — cobre tudo abaixo de 0,80. Usar `sim < 0,55`.
- **A âncora do `align.py` só dispara nas 2–3 PRIMEIRAS palavras da linha.** Se ele improvisar o começo, a
  linha vem com `takes: []` — e aí **baixar `SIM_PARAFRASE` não adianta**, não há candidato para pontuar.
  Foi o que derrubou 6 linhas em 18/09. A saída é a busca sem âncora (`candidatos_livres`).
- **`sim` (Levenshtein) mede mal o improviso**: ele diz MAIS palavras que o roteiro e cada palavra a mais
  derruba a nota, então o editor prefere um pedacinho curto à frase inteira. Usar cobertura (F1/`cobertura`).
- **Não aceitar take que termina no meio da frase** — sem `FIM_FRASE` o hook saía cortado.
- **A medição de voz de fundo tem de cobrir 150–500 Hz**: procurando só 70–350 Hz eu concluí "não há vozes"
  e havia (criança/adulto no outro quarto, a −67 dBFS).
- Antes de mudar qualquer coisa de legenda/cor, **reprocessar um vídeo já entregue e comparar** — foi assim que se pegou uma regressão.

---

### Baixar do YouTube: B-roll ≠ comentário (2026-09-18)
Não tratar todo download do YouTube como violação. São dois casos:
- **B-roll** (o trecho ilustra outra coisa) → precisa de licença: `/material`, `buscar_video.py`.
- **Comentário/reação** (o Reel fala SOBRE a obra) → `/obra`, `baixar_obra.py`, com crédito e os tetos de citação.
Eu confundi os dois e dei sermão no Carlos por um uso legítimo; ele corrigiu. Condições em `docs/decisoes.md` §5.

### Vídeo do YouTube em 1080p não abre no QuickTime (2026-09-18)
Vem em **VP9/Opus**, que o macOS não decodifica — parece arquivo corrompido e **não é**. O `baixar_obra.py`
já pede H.264/AAC e gera uma cópia `-VER.mp4` quando não consegue. Diagnóstico: `ffprobe` mostra o codec;
se o `ffmpeg -f null -` decodifica sem erro, o arquivo está bom.

### archive.org: bloqueio do operador por SNI (2026-09-18, causa confirmada)
`TLSV1_ALERT_ACCESS_DENIED` em curl, openssl e yt-dlp. **Prova de que o destino está vivo:** ligando ao mesmo
IP com o SNI trocado para `github.com`, o servidor responde e devolve o certificado `CN=*.archive.org`;
a porta 80 devolve 200. Falha em IPv4 e IPv6, TLS 1.2 e 1.3, e só com esse nome. Não é o yt-dlp, não é o Mac,
não é falta de material. Contorno: outra rede (hotspot 4G) ou VPN.


## 6. Decisões pendentes do Carlos

1. **A ou B no Hassabis** (§1) — a única que trava a entrega.
2. Gravar a **L11 do Nobel**? Sem ela o hook promete um Nobel que o vídeo não entrega.
3. ~~Apagar `videos/2026-09-16-chatgpt-contexto/brutos/_nao-usar/` (`PRAQ0967.MOV`, 17 GB) e
   `videos/2026-09-17-demis-hassabis/brutos/_nao-usar/` (documentário completo, 151 MB)?~~ **Apagados na limpeza de 23/10** (bloco 0n).
4. ~~`videos/_teste-monitor` e `_teste-sintetico` (3,8 GB) — recriáveis pelas suítes; apagar?~~ **Apagados em 23/10**; recriar com `tests/make_synthetic.py` antes das suítes.
5. Ele quer **testar o modelo Fable 5.1** para edição. É ele quem troca, no seletor do app.
