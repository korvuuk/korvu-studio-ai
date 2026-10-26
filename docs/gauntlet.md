# GAUNTLET — a cadeia de portões do CONTENT AI

> **Modelo aprovado pelo Carlos em 22/10/2026**, trazido do projeto Muntuza Tickets
> (`MUNTUZA TICKET/muntuza-tickets/documentação/15-gauntlet.md`): *"cada funcionário responsável por uma função tem
> um agente que fiscaliza o trabalho… enquanto essa verificação não foi aprovada, ele não chega para mim."*
> Livro de veredictos: `scripts/portoes.py` · testes: `tests/portoes/test_portoes.py`.

## O problema que isto resolve

Quem faz não consegue se revisar. Não é falta de competência, é **posição**: quem acabou de fazer já se convenceu de que
está certo. O CONTENT AI tem a prova escrita:

- **21/10 — capas com a cor errada na fila.** O colorista usou a cadeia de cor descartada; o Carlos viu, a cor foi refeita
  — mas as capas tinham sido tiradas da cor velha e **ninguém as refez**. Foram para `06-publicar/`. O único selo do pacote
  era `"qa": "PASS"`, que é do vídeo; a capa não passava por portão nenhum, e o selo não sabia que a cor tinha mudado.
- **19/09 — "corrigido" sem estar.** Dois vídeos mandados ao Carlos como corrigidos; o render tinha falhado e os arquivos
  eram de 4 h antes (`CLAUDE.md` regra 10).
- **16/10 — pessoa errada na foto.** A F20 do Hinton era o Tom Kalil, catalogada como Hinton; foi publicada.

**Nada fecha por auto-relato.**

## A cadeia

```
  DECIDE O QUÊ               CONSTRUTORES                   PORTÃO (gerente)                DESTINO
 ┌───────────────┐   estrategista · pesquisador ·    ┌──────────────────────────┐
 │ docs/         │   buscador · curador          ──▶ │ PORTÃO-PAUTA             │─┐
 │ decisoes.md   │   roteirista · produtor-de-     │ │                          │ │   AGENTE PRINCIPAL
 │ (as regras do │   material                    ──▶ │ PORTÃO-ROTEIRO           │─┤   (Atlas)  ──▶  CARLOS
 │  Carlos)      │   colorista · designer-de-capas·  │                          │ │   só reporta com
 │               │   produtor-de-extras · animador──▶ │ PORTÃO-IMAGEM            │─┤   TODOS os portões
 │ dúvida já     │   editor-de-video · produtor-     │                          │ │   da etapa APROVADOS
 │ decidida NÃO  │   musical                     ──▶ │ PORTÃO-CORTE             │─┤
 │ sobe a ele    │   publicador                  ──▶ │ PORTÃO-PUBLICACAO        │─┘
 └───────────────┘                                   └──────────────────────────┘
```

O "product-owner" do Muntuza aqui é o **`docs/decisoes.md`**: toda dúvida que ele já decidiu se resolve lá, não com
pergunta ao Carlos (regra dele: "essas dúvidas não podem existir no processo").

## Os portões

Cada portão é o **gerente** do seu departamento: audita e **não constrói**. Os eixos são exclusivos — um arquivo
pertence a um portão só (sobreposição faz cada um assumir que o outro viu).

| Portão | Agente | Fiscaliza | Cobre (arquivos que vencem o veredicto) | Roda quando |
|---|---|---|---|---|
| **PAUTA** | `portao-pauta` | estrategista, pesquisador-de-material, buscador-de-videos, curador-de-obra | `material/dossie.md`, `fontes.json`, `youtube/catalogo*.md`, `obra*`, `capas/LIVROS.md` | depois de /material, /obra, /buscar-videos (e do passo 4b do /novo-video) |
| **ROTEIRO** | `revisor-de-roteiro` | roteirista, produtor-de-material | a **fala** do `roteiro.md` + CTA/material do frontmatter, `material/*.pdf` | depois do roteiro **e** do PDF (/novo-video, /roteiro, PDF regerado) |
| **IMAGEM** | `portao-imagem` | colorista, designer-de-capas, produtor-de-extras, animador | `brutos/extras/**`, `edicao/cor/corte-cor*.mp4`, `capa/capa*.png` | depois de /extras, /animar, /cor, /capa — e no /renderizar depois da capa |
| **CORTE** | `revisor-de-video` (passagem 2) | editor-de-video, produtor-musical | `edicao/final*.mp4`, `edicao/legendas.srt` | no /renderizar, depois do áudio |
| **PUBLICACAO** | `portao-publicacao` | publicador | na pasta da fila: `video/`, `capa/`, `material/*.pdf`, legendas do post, campos do `post.json` que vão ao ar, a escolha de arquivos do `pacote.json` | no /publicar, depois do `agendar`; de novo se a legenda ou o post mudar |

### O sistema (painel web) — departamento de tecnologia (22/10)

O mesmo método vale para o painel (`painel/`). Construtores: `designer-de-produto` (UI/UX → `painel/design/`),
`engenheiro-frontend` (`painel/web/`) e `engenheiro-backend` (`painel/supabase/`, `painel/sync/`, `painel/tests/`).
Dois agentes-portão auditam **três áreas**, cada uma com o seu veredicto (`portoes.py … painel <área>`):

| Área | Agente | Fiscaliza | Cobre (relativo a `painel/`) | Roda quando |
|---|---|---|---|---|
| **DESIGN** | `portao-interface` (gerente de tecnologia) | designer-de-produto | `design/**` | direção nova (antes de o Carlos escolher) e design system/telas novos ou mudados |
| **INTERFACE** | `portao-interface` | engenheiro-frontend | `web/src/**`, `web/public/**`, `package.json`/`package-lock.json` e configs do `web/`, `capturar.sh` | tela, componente ou dependência mudados — antes de o Carlos ver |
| **DADOS** | `portao-dados` | engenheiro-backend | `supabase/config.toml`, `supabase/migrations/*.sql`, `supabase/seed.sql`, `sync/**`, `tests/**`, `iniciar.sh`, `so-no-mac.sh`, `studio.sh` | migração, sincronizador ou testes mudados |

O design é aprovado **sozinho, antes do código** (senão uma entrega só de design nunca passaria); o código é comparado
com o design aprovado. No sistema a aprovação é **por caminho**: arquivo novo, mudado, renomeado ou **apagado** vence.
Nunca contam `node_modules/`, `.next*/`, `__pycache__/` nem nada que comece com `.` (inclusive `.env.local`). Ficam fora
de propósito: `painel/referencias/` (referências e o `BRIEF.md`), `painel/trabalho/` (capturas e rascunhos de quem
constrói), `painel/portoes/` (relatórios) e `painel/equipe.yaml` (fonte do Carlos, como os arquivos do projeto).
Os portões olham a tela de verdade com `bash painel/capturar.sh` (Chrome sem janela com emulação de 1440 e 375 px,
página inteira, `scrollWidth` medido). Banco de teste: `painel_teste` criado e apagado no mesmo Postgres — nunca o
banco do Carlos. Sinais: `portoes.py estado painel`.

**Onde a regra morde hoje:** "nada do painel chega ao Carlos sem `portoes.py exigir painel` limpo" ainda é regra do
agente principal — o preview do Carlos roda `next dev` na mesma pasta onde se trabalha. O ponto executável (o Carlos vê
só um build feito depois de `exigir painel` passar; quem constrói trabalha noutra porta) está no backlog (D4).

### Linha de base (1.ª auditoria de uma área que já existia)
Quando um portão nasce depois do código (o painel de 22/10), tudo o que ele acha é anterior a ele. **S0 corrige-se já**
(é o Carlos vendo algo errado). **S1 que um trabalho já decidido vai substituir** (o redesign do painel) vai ao backlog
como **S1-L** com dono e gatilho = esse trabalho, conta como `--s2` e não segura o veredicto — o portão lista quais no
relatório e o agente principal avisa o Carlos no cartão. S1 que nenhum trabalho decidido cobre corrige-se já.

**Só roda o portão da área que foi mexida.** Uma correção de legenda do post não passa pelo portão de imagem. Isto não é
para poupar trabalho: um processo caro demais deixa de ser cumprido, e passa a dar a ilusão de rigor sem o rigor.

## O veredicto preso aos arquivos (o "SHA congelado")

O projeto não tem commits, então o veredicto nomeia uma **impressão** — o sha256 de cada arquivo da área:

1. **Passo zero do portão:** `uv run python scripts/portoes.py impressao <alvo> <portão>` — anota a impressão antes de ler
   uma linha. Enquanto o portão audita, ninguém mexe na área.
2. No fim, `portoes.py registrar … --impressao <a mesma>`: se a área mudou no meio, o registro é **recusado** — um
   veredicto sobre um estado que já não existe não prova nada.
3. **Arquivo novo ou mudado depois do APROVADO → o veredicto VENCE sozinho** (`⌛`), e o portão roda de novo.
   Foi exatamente o que faltou em 21/10: a cor refeita teria vencido o portão de imagem, e as capas velhas não passavam.
4. Vale por **conteúdo**, não por nome: `capa-A.png` copiada para `capa.png` continua aprovada; arquivo apagado pelo
   `limpar_video.py` não vence nada.
5. No roteiro vale só **o que é falado** (e o CTA/material): nota de status, tabela de extras ou checklist no
   `roteiro.md` não vencem o portão.
6. No `post.json` valem só os campos que vão ao ar (plataformas, capa, Trial × normal, legenda, material). Data,
   ids e estado mudam com o uso e não vencem.

## Portão executável — não é um pedido, é um controle

| Momento | Quem barra | O que exige |
|---|---|---|
| `montar_pacote.py` | o próprio script | pauta (se houver pesquisa), roteiro, imagem e corte **APROVADOS e válidos**; cada arquivo copiado tem de ser um dos que os portões viram. O pacote sai **selado** (`pacote.json.gauntlet`, `docs/contratos.md` §9) |
| `publicar.py agendar` | `validar_pacote` | selo presente; nenhum arquivo do pacote trocado depois do selo; origem ainda válida |
| `publicar.py publicar` / `--due` (launchd) | `validar_pacote(publicacao=True)` | tudo acima **+ PORTÃO-PUBLICACAO aprovado e válido** sobre a pasta da fila |

Se a cor da origem for refeita depois de o post estar na fila, o portão de imagem vence e **o post não sai**. O launchd
marca o post como `erro`, regista e avisa; **ele não tenta de novo sozinho**: depois de os portões reaprovarem (e a capa
ser refeita, se for o caso), reagendar com `publicar.py agendar <slug> --reagendar` (ou publicar com o OK do Carlos).

Travas que o próprio código faz (não dependem de o portão lembrar):
- **Capa mais velha que a cor atual** (`capa/capa*.png` anterior a `edicao/cor/corte-cor.mp4`) **não se aprova** — o
  `registrar` do portão de imagem recusa. Refazer as capas pela cor nova, ou apagar as que não vão ser usadas.
- Na fila, o portão da publicação aprova cada arquivo **no seu papel** (por caminho): trocar o vídeo de variante, as
  duas legendas entre si ou o `pacote.json` vence o veredicto. Na origem vale o conteúdo (cópia de capa aprovada passa).
- Uma capa do pacote só vale se o portão de imagem a aprovou **como capa** (`capa/`), não por coincidir com um extra.
- O `limpar_video.py` não apaga capa que esteja num pacote ou na fila (a capa própria de cada variante).
- Um container do Instagram criado antes da última aprovação não é reaproveitado numa nova tentativa.
- Falha ao ler os portões (livro corrompido, arquivo sumindo) bloqueia **só aquele post**, nunca o `--due` inteiro.

**Legado:** os 6 pacotes que já estavam na fila em 22/10 (montados antes do GAUNTLET) estão em
`_controle/gauntlet-legado.json` e publicam sem selo, com aviso no log. **A lista é congelada** — nunca se acrescenta
slug novo ali.

## A escala de gravidade

Todo achado sai classificado, com a classe escrita ao lado:

| Classe | Definição no CONTENT AI | Efeito |
|---|---|---|
| **S0** | **Vai ao ar errado** se publicar: cor/capa errada, texto sobre o rosto, fato falso ou sem fonte, pessoa errada na foto, palavra-chave que não entrega o PDF certo, nome pessoal do Carlos no material, voz da IA no corte, público definido por país/"lusófono", Trial × normal contra a regra do par, segredo/token exposto | **BLOQUEIA** |
| **S1** | Ainda não vai ao ar, mas **está no trabalho desta tarefa** e a próxima etapa vai propagar: roteiro picado/sem arco, > 90 s, palavra-chave dita uma vez só, número por extenso, PDF > 2 páginas, identidade de foto não conferida, extra sem movimento, LUFS fora | **BLOQUEIA** |
| **S2** | O trabalho está certo; falta polimento ou a prova de que um controle pegaria a regressão | **NÃO bloqueia** → `_controle/backlog-portoes.md` com **dono** e **gatilho** |
| **S0-L** | Gravidade de S0, mas **anterior a esta tarefa e independente dela** (ex.: PDF antigo no layout velho, que esta tarefa não tocou). Tem de ser **provado** (o arquivo não é desta tarefa) | Não bloqueia esta tarefa · **bloqueia a publicação do que o usa** · lista própria no backlog, repetida em cada veredicto |

Achado sem classe não conta como bloqueio. **Não há "aprovado com ressalvas"**: as ressalvas perdem-se.

## Tecto de três voltas

Cada portão dá **no máximo 3 voltas** por ciclo (o ciclo recomeça depois de um APROVADO).

| Ao fim da 3.ª volta | Veredicto |
|---|---|
| só restam S2 | `APROVADO` |
| ainda há S0/S1 | `BLOQUEADO — ESCALADO` (o `portoes.py` converte sozinho) |

O ESCALADO vai ao Carlos **como decisão**, não como pedido de autorização, com a recomendação do portão:
**(a)** refazer a peça pela raiz · **(b)** entregar sem essa parte · **(c)** pagar mais voltas. A volta seguinte só se
registra com `--decisao-carlos "<a opção dele>"`.

> Três voltas bloqueadas no mesmo eixo já não é detalhe: a peça está errada na raiz.

## O veredicto — a parte que não é negociável

O portão termina com **uma linha à letra**:

```
PORTÃO-IMAGEM: APROVADO — sobre 3f1a9c2b77e0 (volta 2)
PORTÃO-IMAGEM: BLOQUEADO — sobre 3f1a9c2b77e0 (volta 1)
PORTÃO-IMAGEM: BLOQUEADO — ESCALADO — sobre 3f1a9c2b77e0 (volta 3)
```

1. **O portão não corrige.** Aponta, com arquivo e o ponto exato (linha do roteiro, segundo do vídeo, quadro, pixel) e o
   **cenário concreto** ("se publicar, a capa sai esverdeada ao lado do vídeo quente"), e devolve a quem construiu.
   Achado sem cenário é opinião.
2. **O que não foi verificado, declara-se.** Um portão que aprova o que não viu é pior do que nenhum portão.
3. **Confere no ponto do defeito e pelo meio certo** (`CLAUDE.md` regra 10): abre o PNG, extrai o quadro, mede o
   número. "Compilou" não é "funciona".
4. **Nunca roda num modelo mais fraco do que quem construiu.** Os portões (cinco do conteúdo, dois do sistema) rodam em **opus**.

Relatórios: `videos/<slug>/qa/portoes/<portão>-AAAA-MM-DD-vN.md` (o do roteiro continua em `roteiro-revisao.md` e o do
corte em `qa/relatorio.md`, que o `montar_pacote.py` lê); o da publicação em `06-publicar/<slug>/portoes/publicacao-vN.md`;
os do painel em `painel/portoes/<design|interface|dados>-AAAA-MM-DD-vN.md` (livro em `painel/portoes.json`).

## Como se invoca: automaticamente, e em ciclo

> Do Muntuza: *"Não é quando você implementa e depois volta para me perguntar se vai aplicar o GAUNTLET ou não."*

1. O construtor termina e diz que acabou.
2. O agente principal vê que área foi mexida e chama **o portão dessa área**, na hora. Portões de áreas diferentes
   podem rodar em paralelo.
3. `BLOQUEADO` → devolver os **S0/S1** ao construtor, corrigir, **voltar ao mesmo portão**. Não se argumenta com o
   veredicto: corrige-se, ou demonstra-se que o achado está errado. Os S2 vão para o backlog.
4. Até 3 voltas; na 3.ª com S0/S1 → ESCALADO → decisão do Carlos.
5. Com tudo APROVADO, **só então** fala-se com o Carlos.

| ⛔ Nunca | ✅ Em vez disso |
|---|---|
| "Está feito. Quer que eu rode o portão?" | Rodar o portão e trazer o resultado |
| Mostrar ao Carlos capa, corte, roteiro ou PDF ainda BLOQUEADO | Corrigir, voltar ao portão, e só depois mostrar |
| Deixar os portões para o fim do vídeo | Um portão por etapa, quando a etapa acaba |
| "Aprovado com ressalvas" | APROVADO (S2 no backlog) ou BLOQUEADO |

As aprovações que são **do Carlos** continuam dele (roteiro, EDL, escolha da capa, música, autorização de publicar):
o portão roda **antes** de a peça chegar a ele, para que ele só escolha entre coisas certas.

## O que chega ao Carlos: o cartão de entrega

Uma mensagem por ciclo terminado, **decisão primeiro**, no máximo ~15 linhas:

```
🎬 <vídeo · etapa>   ✅ ENTREGUE   (ou ⛔ ESCALADO — preciso de uma decisão)

O QUE ESTÁ PRONTO
<1 a 3 linhas: o que ele já pode ver/aprovar>

⚠️ DECIDIR   (só o que é dele)
1. <pergunta numa linha> → recomendo <X>, porque <meia linha>
   — se não houver nada: «Nada. Sigo para <próximo passo>.»

⛔ NÃO ASSUMIR QUE ESTÁ CERTO
<o que nenhum portão verificou — ou a linha some>

PORTÕES  pauta ✅ · roteiro ✅ · imagem ✅ · corte ✅ · publicação ✅
DETALHE  qa/portoes/… · HANDOFF.md
```

"O portão devolveu BLOQUEADO, vou corrigir" não é notícia: é o ciclo funcionando.

## Sinais

`uv run python scripts/portoes.py estado` mostra todos os vídeos e a fila; `estado videos/<slug>` mostra um vídeo com os
motivos. `✅` aprovado · `⌛` vencido (mudou depois do APROVADO) · `⛔` bloqueado · `🔺` escalado · `·` ainda não rodou ·
`—` não se aplica. O painel web (próxima etapa) lê o mesmo `portoes.json`.
