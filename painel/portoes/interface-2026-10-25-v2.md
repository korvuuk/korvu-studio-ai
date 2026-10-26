PORTÃO-INTERFACE: APROVADO — sobre f466c89d6bff (volta 2)

# PORTÃO-INTERFACE · painel · 25/10/2026 · volta 2 (correção do S1-1, PI76, PI77)

- **Alvo:** `painel` · **área:** `interface` · **auditor:** portao-interface (opus) · **fiscalizado:** engenheiro-frontend
- **Impressão:** `f466c89d6bff` (140 arquivos), congelada antes de ler e conferida de novo antes do registro.
- **Placar:** S0 0 · S1 0 · S2 0 novos. Nenhum S0-L.
- **Capturas:** `painel/portoes/capturas-f466c89d6bff/` (8 rotas + 404 a 1440 e 375 px, e `bib-tela-*`).

## O que mudou desde a volta 1 (52f8b6832fcd)
Comparei o hash de cada arquivo com a lista da volta 1. Mudaram exatamente os 6 declarados:
- `app/biblioteca/_componentes/{Lado,Acervo}.tsx`
- `app/casca.css`
- `app/equipe/page.tsx`
- `components/Acervo.tsx`
- `lib/db.ts`

Nada entrou nem saiu. `acrescimos.css` continua 58bd71d9e817 e `tsconfig.json` continua 8e511b97b9c9, antes e depois do meu servidor.

## O que verifiquei e como
- **Código e segurança:**
  - `tsc`, `eslint` e o build em `.next-verificacao`: exit 0;
  - `grep` de chaves no `static`: vazio;
  - `npm audit`: 0.
  - Servidor de auditoria só com `PAINEL_DIST=.next-trabalho`.
- **S1-1, a líder do Sistema:**
  - `Lado.tsx:60` dá `kx-meta-lider` à 1.ª linha e `k-estilo-meta kx-meta-ink` às outras;
  - a regra está em `casca.css:262` (600 11px mono, `--accent-ink`), sem `.k-estilo-meta` junto.
  - Medido no navegador a 1440 e a 375 px: "93,4 %" em `rgb(179,54,0)` peso 600; "4,7 %" e "1,8 %" em `rgb(17,17,17)` peso 500. Olhei o quadro do card: o líder sai em laranja escuro, como a maquete (`biblioteca.html:68`). **Corrigido.**
- **PI76:**
  - `familiaRodou` e `modelosPrincipais` usam o `principal.nome` que vem do `modelo_nome` de `modelo_por_agente`; o KPI e os filtros não usam mais `MODELOS`.
  - Na tela: "rodaram em Sonnet 5.5: 11 · Opus 5.5: 10 · ainda não: 5".
  - Filtros: Todos 26, Portões 7, Sonnet 5.5 11, Opus 5.5 10 e Ainda não rodou 5. Cada chip deixa visível exatamente o seu número de linhas, com `aria-pressed` certo.
  - A ordem passou a ser por quantidade (Sonnet primeiro). Os números são os mesmos da volta 1.
  - **Fechado.**
- **PI77:**
  - `priority` nas 5 fotos dos looks;
  - o console da Biblioteca está limpo a 1440 e a 375 px (na volta 1 dava 2 avisos de LCP);
  - as 5 fotos carregam;
  - o comentário do câmbio saiu de `db.ts`.
  - **Fechado.**
- **Regressão, porque o `casca.css` vale para todas as telas:**
  - refotografei as 8 rotas + 404 nas duas larguras, com scrollWidth igual à janela;
  - detector de cortes de 375 a 1920 px: só o PI53, já conhecido;
  - varredura de acessibilidade nas 9 rotas: igual à volta 1 (um `h1`, nada sem nome, console limpo; o SVG de Tokens é o mesmo falso positivo de `role="img"` no pai).
  - A Produção ficou 104 px mais alta por causa dos dados: há um aviso novo, "Portão dos dados vencido".

## Divergências e S2 que continuam
- **PI75** (frases dos looks, "WAY", "4K" e data do HD) continua esperando o backend.
- O `estado` mostra a área **dados vencida** desde 21:40 (migração `…_nome_e_frase_dos_looks_e_nota_do_hd.sql`, `sincronizar.py`, `biblioteca.yaml` e testes). É o trabalho do PI75 e precisa do PORTÃO-DADOS antes de `exigir painel` ficar limpo.

## O que NÃO verifiquei
- Os estados vazio, fora e lento nesta volta. As mudanças não tocam os ramos de estado; foram vistos na volta 1.
- Leitor de tela real, navegação inteira por teclado e foco visível nas abas.
- O modo Decisão do Portão na tela (nenhum vídeo em `portao`).
- O banco contra os arquivos, que é do PORTÃO-DADOS.

## S0-L abertos
Nenhum nesta área (lista completa em `_controle/backlog-portoes.md`).
