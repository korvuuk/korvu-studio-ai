PORTÃO-INTERFACE: APROVADO — sobre e5b9b4bcef0c (volta 1)

# PORTÃO-INTERFACE · painel · 25/10/2026 · Biblioteca sem HD externo + frases dos looks (PI75)

- **Alvo:** `painel` · **área:** `interface` · **auditor:** portao-interface (opus) · **fiscalizado:** engenheiro-frontend
- **Impressão:** `e5b9b4bcef0c` (140 arquivos), congelada antes de ler e conferida de novo antes do registro.
- **Placar:** S0 0 · S1 0 · S2 0. Nenhum S0-L.
- **Base:** design APROVADO edfdd38cbaf5 (sem HD) · decisão `docs/decisoes.md:167` (25/10).
- **Capturas:** `painel/portoes/capturas-e5b9b4bcef0c/` (Biblioteca a 1440 e a 375 px).

## O que mudou desde o APROVADO f466c89d6bff
Comparei o hash de cada arquivo. Mudaram exatamente os 3 declarados:
- `lib/db.ts`
- `app/biblioteca/_componentes/Lado.tsx`
- `app/biblioteca/_componentes/Acervo.tsx`

Nada entrou nem saiu. `tsconfig.json` continua 8e511b97b9c9, antes e depois do meu servidor (`.next-trabalho`).

## O que verifiquei e como
- **Código e segurança:**
  - `tsc`, `eslint` e o build em `.next-verificacao`: exit 0;
  - `grep` de chaves no `static`: vazio;
  - `npm audit`: 0.
- **"HD" no app inteiro** (`grep -rn` em `painel/web/src` por `\bHD\b`, `hd_`, `no_hd`, "externo"): só 2 comentários que citam a decisão (`Lado.tsx:10`, `db.ts:180`) e o ícone `link-externo`, que não tem nada a ver.
  - `armazenamento()` faz `select` só de `gravacoes_mac_bytes, material_mac_bytes, material_mac_arquivos, mac_bytes`; o tipo não tem mais `hd_*`.
  - No HTML servido não há "HD"; o único "99,2" é parte de uma coordenada no payload do React ("99,294,36"), não texto da tela.
- **Armazenamento contra o banco** (consulta só de leitura à `armazenamento`, lida às 22:25:09):
  - 117.045.314.891 + 6.725.597.758 = 123.770.912.649 bytes;
  - a tela, nas duas larguras: "123,8 GB no Mac", "Gravações da câmera 117,0 GB", "Material e cenas extras 6,7 GB";
  - a barra tem 2 segmentos, com `aria-label` "Gravações da câmera 117,0 GB, Material e cenas extras 6,7 GB";
  - "Ver os números" tem 2 linhas, com a porcentagem sobre a soma das duas, que é igual a `mac_bytes`.
  - O vazio agora diz "o espaço no Mac aparece aqui", sem HD (só li o código).
- **Looks (PI75):**
  - `looks.nome` e `looks.descricao` no banco = `painel/biblioteca.yaml:135–` = o texto da tela, à letra, nos 5 cartões: "Original da câmera", "Só a conversão", "Look v4", "Look v5 · WAY", "Look v11" e as 5 frases.
  - É igual à maquete aprovada. Se `nome` ou `descricao` vierem nulos, o código cai no nome fixo ou em nada, nunca num texto inventado.
- **Tela:**
  - abri a captura de 1440 px e ela bate com a maquete edfdd38cbaf5;
  - scrollWidth igual à janela nas duas larguras;
  - o detector de cortes (375 a 1920 px) não acha nada na Biblioteca;
  - a varredura de acessibilidade da Biblioteca está limpa (um `h1`, nada sem nome, sem imagem sem `alt`);
  - o console está limpo.

## Atenção: a área dados
O `portoes.py estado painel` mostra a área **dados vencida**. A migração `…_nome_e_frase_dos_looks_e_nota_do_hd.sql`, o `sincronizar.py` e o `biblioteca.yaml`, que trazem as colunas `nome` e `descricao`, ainda não têm o APROVADO do PORTÃO-DADOS. Registrei só a minha área: a interface mostra certo o que o banco tem; se o banco tem certo é com ele. Enquanto dados não aprovar, `exigir painel` não fica limpo.

## O que NÃO verifiquei
- Os estados fora, vazio e lento nesta rodada. Li o código do vazio do Armazenamento; os ramos de erro não mudaram.
- As outras telas: os 3 arquivos só servem à Biblioteca (`armazenamento` e `looks` não são lidos em outras páginas; conferi com `grep`).
- Leitor de tela real.
- A migração e o sincronizador, que são do PORTÃO-DADOS.

## S0-L abertos
Nenhum nesta área (lista completa em `_controle/backlog-portoes.md`).
