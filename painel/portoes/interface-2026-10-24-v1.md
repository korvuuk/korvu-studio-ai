PORTÃO-INTERFACE: APROVADO — sobre 5159c93d1a0e (volta 2)

# PORTÃO-INTERFACE · painel · 24/10/2026 · as 6 telas novas · volta 2

- **Alvo:** `painel` · **área:** `interface` · **auditor:** portao-interface (opus) · **fiscalizado:** engenheiro-frontend
- **Impressão:** `5159c93d1a0e` (129 arquivos).
  - Congelada às 22:43 de 23/10.
  - A auditoria parou pelo limite de uso e foi retomada às 05:21 de 24/10.
  - Conferi a impressão de novo nessa hora e antes do registro: continua a mesma.
- **Volta anterior:** `painel/portoes/interface-2026-10-23-v4.md`, BLOQUEADO sobre `591f80519753` (volta 1) por 2 S1:
  - peças montadas à mão;
  - "Jacob coxon".
- **Placar:** S0 0 · S1 0 · S2 2 (1 novo, o PI64, mais o S1-L PI-L1, que continua só na ficha e no Contratar). Nenhum S0-L.
- **Capturas:** `painel/portoes/capturas-5159c93d1a0e/`
  - 9 rotas a 1440 e 375, com fatias;
  - `interacao/`;
  - `estado-fora/`, `estado-vazio/` e `estado-carregando/`.

## O que mudou desde a volta 1 (provado)
Comparei a impressão arquivo por arquivo com a do veredicto da volta 1:
- 3 arquivos novos: `components/Destaque.tsx`, `LinhaPortoes.tsx` e `ListaKv.tsx`;
- 32 mudados;
- nenhum apagado.

Todos estão dentro do que a coordenação descreveu: os 2 S1, o PI59, o PD24, o PI58 e o PI60.

## Os S1 da volta 1, um por um

| S1 | O que conferi | Situação |
|---|---|---|
| **S1-1** peças montadas à mão | Ver detalhe abaixo da tabela | **corrigido** |
| **S1-2** "Jacob coxon" | Ver detalhe abaixo da tabela | **corrigido** |

**S1-1 · peças montadas à mão**
- A Projeção agora é `<Kpi … deltaAoLado>` (`tokens/_componentes/Projecao.tsx:30–55`), com o mesmo desenho: "£ 2.169", "↑ 3,2×" e a nota embaixo.
- O botão de "Precisam de atenção" e o do sino agora usam o `BotaoLink`.
- Fiz um `grep` de classes de componente (`k-btn`, `k-chip`, `k-kpi`, `k-note`, `k-empty`, `k-avatar`, `k-table`, `k-menu`, `k-gate`, `k-event`, `k-destaque`, `k-kv`, `k-direcao`, `k-fase`, `k-filtro`, `k-seg`…) nas páginas fora da vitrine.
- Só sobraram classes de tipografia, que não são componente: `k-kpi-note` e `k-link`.

**S1-2 · "Jacob coxon"**
- `GRAFIA` em `lib/producao.ts:27–30` ganhou `coxon: "Coxon"`, com o comentário do porquê.
- Agora sai "Jacob Coxon" na tabela Roteiros. Os outros 7 nomes curtos batem com a maquete.

## Os S2 que vieram junto

| Item | O que conferi | Situação |
|---|---|---|
| **PI59** linha "Portões:" pelo `erros_gauntlet` | Ver detalhe abaixo da tabela | **fechado** |
| **PD24** paginação dos veredictos | `db.ts:159–161` pagina por (`alvo`, `ordem`), a chave primária (`pg_constraint`), e ordena por tempo depois | **fechado** |
| **PI58** rota de capas | Ver detalhe abaixo da tabela | **fechado** |
| **PI60** concordância | Ver detalhe abaixo da tabela | **fechado** |

**PI59 · linha "Portões:" pelo `erros_gauntlet`**
- `portoesDoPost` (`lib/producao.ts:154–166`) lê a resposta do próprio `conferir_pacote`.
- A coluna é `jsonb NOT NULL` com `check (jsonb_typeof = 'array')`, então "nenhuma mensagem" não pode vir de falta de leitura.
- Copiei o leitor à letra do app e rodei com as frases reais de `scripts/portoes.py:381–481`:
  - sem selo → "Ainda não rodou · selo";
  - publicação pendente;
  - origem vencida + publicação → Vencido · imagem;
  - capa trocada depois do selo e "já não aprova" → Vencido;
  - "não há arquivos da área" → Não se aplica · corte;
  - sem livro na origem;
  - escalado + bloqueado → Escalado · roteiro;
  - falha da conferência → Bloqueado;
  - legado selado → segue a regra normal.
- As 12 formas saem certas.
- Sobra um caso de borda: o PI64, abaixo.

**PI58 · rota de capas**
- Agora usa `Object.hasOwn` (`route.ts:9`, `capas.ts:25`).
- No build: `constructor`, `__proto__`, `toString` e `hasOwnProperty` respondem **404** (antes, 500).
- `..%2F…/.env` responde 404 e as capas reais respondem 200.

**PI60 · concordância**
- A frase virou "Esta parte (os números do perfil) não veio do banco".
- Vi rodando nas 6 telas com o banco fora do ar: 3 a 8 blocos por tela.

## Mudança de dado (não de código): o ChatGPT contexto voltou para Roteiros
- Banco: `videos.gravado = f` e `pronto = f`; `05-render-pronto/` vazio no disco; a trava continua em `nao_publicar`.
- O que a tela mostra:
  - Roteiros **8**, com o ChatGPT contexto primeiro, "16 set · há 38 dias";
  - Prontos **0**, com "Nenhum pacote pronto";
  - o aviso "Pronto, mas não vai ao ar" sumiu;
  - o Calendário diz "Sem horário · nenhum pacote pronto esperando data".
- Portões por área batem com `portoes_estado`: pauta 10·2, roteiro 12, imagem 9·3, corte 4·8 e publicação 5 legado.

## O que verifiquei e como (nesta volta)
- **Código e segurança** (em `painel/web`):
  - `tsc` exit 0, `eslint` exit 0;
  - build em `.next-verificacao` exit 0 (BUILD_ID `vzJ488FhYzVe9ofh3BR1f`, 12 rotas);
  - `grep` de chaves no `static` vazio; o HTML do build não tem chave, nem o endereço do banco, nem caminho `/Users/…`;
  - nenhum `NEXT_PUBLIC_`; `npm audit` 0; nenhuma cor crua.
- **Tela:**
  - 18 capturas, com `scrollWidth` igual à janela em todas;
  - o detector de texto cortado, a 375, 768, 1024, 1440, 1600, 1834 e 1920 px, só acha os dois casos conhecidos do design,
    com `title` (PI41 e PI53 (design));
  - console limpo nas 8 rotas do build;
  - auditoria de acessibilidade pelo DOM igual à volta 1: 1 `h1`, nenhum pulo de nível, nada sem nome ou sem `alt`, nenhum
    id repetido.
- **Interação** (de novo, todas):
  - segmentado do Público ("379 contas", Brasil 52,0 %);
  - filtros e busca da Equipe (7/14/11/25, "Limpar filtros");
  - as 5 fases da Produção pela âncora: Agendados com "hoje / amanhã / em 3 dias" para 24/10, e os links de Publicados;
  - Mês/Semana, ‹ › e Hoje no Calendário;
  - Tokens/Custo ("23 out · £ 330,80") e "Ver os números" com £ e US$;
  - foco `accent-ink` no claro e `accent` na barra lateral;
  - "Novo vídeo" com Esc devolvendo o foco.
- **Números contra o banco** (janela nova, 25 set – 24 out, sincronização das 05:16):
  - 60.500.280 → "60,5M"; US$ 903,19 × 0,7465 = £ 674,23 → "£ 674"; "2,1 bilhões" do cache;
  - 21 que trabalharam; £ 32,11 por agente;
  - pico 23 out 30,3M;
  - 89/8/3 % dos tokens; £ 596,70 / 17,60 / 59,93;
  - Direção 27,8M £ 381,32; Tecnologia 24,9M £ 255,56;
  - Atlas 47 tarefas (£ 8,11 por tarefa), Camila 5,5M £ 57,96 6, Sérgio 5,4M £ 35,08 3;
  - projeção £ 506,18 em 7 dias → £ 2.169 (3,2×);
  - a Equipe mostra os mesmos números (60,5M, £ 674, US$ 903; Atlas 47 · 27,8M · £ 381,32).
- **Estados, vistos rodando nas 6 telas a 1440 e 375:**
  - erro: banco fora do ar, cada bloco com a frase nova;
  - vazio: servidor que imita o banco vazio; as frases do `.md` e "taxa de câmbio não registrada";
  - carregando: banco que segura a resposta 30 s; esqueleto por bloco com `role=status`.
- **Vitrine e redirecionamento:** `/sistema` mostra "Página não encontrada" no build sem `PAINEL_VITRINE`; `/videos` responde
  307 para `/producao`.

## O que NÃO verifiquei (declarado)
- **Leitor de tela de verdade, Safari, 320 px e a janela de preview do app Claude.** O preview do Carlos (:3456) não estava
  no ar e eu não o liguei.
- **Os casos do PI59 em tela:** provados só pela lógica copiada do app com as frases reais. Hoje os 5 posts são legado sem
  selo e o banco não tem nenhum outro caso.
- **O vazio num Postgres vazio de verdade:** usei um servidor que imita o PostgREST vazio. Gravados com conteúdo não foi
  visto, porque a fase está vazia.
- **"Copiar o pedido":** não cliquei.
- **Banco × arquivos:** a área `dados` está ⌛ vencida desde 22:41. Conferi a tela contra o banco, não o banco contra os
  arquivos.
- **As capturas do front-end:** não usei como prova; refiz as minhas.
- **Efeitos colaterais meus:**
  - refiz a `.next-verificacao`;
  - o `next dev` regravou o `next-env.d.ts` (gerado, fora da impressão);
  - derrubei os meus servidores (:3457, :3458) e os servidores de mentira (:59997, :59998).

## Backlog (`_controle/backlog-portoes.md`, só acrescentado)

| Nº | Classe | Onde | Achado | Dono | Gatilho |
|---|---|---|---|---|---|
| PI64 | S2 | `painel/web/src/lib/producao.ts:156` (`portoesDoPost`) | "Legado sem selo vence" é testado **antes** das mensagens. Um post legado sem selo com `erros_gauntlet` não vazio sai "Legado · sem selo", embora não saia. Exemplos: "falta pacote.json" e "GAUNTLET: não consegui conferir…" (para legado sem selo o `conferir_pacote` só devolve `[]`). Basta exigir `motivos.length === 0` para o legado | engenheiro-frontend | próxima mudança na linha "Portões:" |
| PI-L1 | S1-L (continua) | `src/app/equipe/[id]/page.tsx`, `equipe/contratar/*` | Só na ficha e no Contratar, que não têm desenho aprovado. Nas 6 telas, fechado | engenheiro-frontend | quando a ficha e o Contratar tiverem desenho aprovado |
| PI58 · PI59 · PI60 · PD24 (fecho) | — | rota de capas, `producao.ts`, `ErroBloco.tsx`, `db.ts` | Ver acima | — | ✅ fechados em 24/10 |

**Continuam abertos, sem mudança:**
- PI18 (empate no 10.º país; dono: a designer).
- PI29 e PI31.
- PI41 e PI53 (design), com `title` no app.
- PI45 e PI48 (30 paradas de Tab no gráfico de consumo, como a maquete).
- PI55, PI56, PI61, PI62 e PI63.

## S0-L abertos (lista inteira do backlog)
Nenhum. A tabela "BLOQUEIOS DE PUBLICAÇÃO (S0-L)" de `_controle/backlog-portoes.md` está vazia.

## Para o agente principal
- A área `interface` está aprovada sobre `5159c93d1a0e`.
- O `portoes.py estado painel` de agora mostra a área **dados ⌛ vencida** (último APROVADO às 22:41, depois disso o
  backend mexeu de novo). Pela regra 13 do `CLAUDE.md`, a tela só chega ao Carlos com `portoes.py exigir painel` limpo:
  falta o PORTÃO-DADOS.
- Continua valendo a observação de processo da volta 1: o Otávio Reis e a Clara Duarte (portões do roteiro e do corte)
  aparecem nos registros rodando em Sonnet 5.5.
