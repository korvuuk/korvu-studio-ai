PORTÃO-INTERFACE: APROVADO — sobre f8729aa1ee1a (volta 1)

# PORTÃO-INTERFACE · painel · 24/10/2026 · Biblioteca + PI64 · ciclo novo, volta 1

- **Alvo:** `painel` · **área:** `interface` · **auditor:** portao-interface (opus) · **fiscalizado:** engenheiro-frontend
- **Impressão:** `f8729aa1ee1a` (150 arquivos), congelada antes de ler e conferida de novo antes do registro.
- **Ciclo novo:** o APROVADO de 05:33 (`5159c93d1a0e`) venceu. Desde ele, 21 arquivos são novos, 12 mudaram e nenhum foi
  apagado. Entre os novos estão as 15 miniaturas de `public/biblioteca/`.
- **Placar:** S0 0 · S1 0 · S2 3 (2 novos + o S1-L PI-L1, só na ficha e no Contratar). Nenhum S0-L.
- **Capturas:** `painel/portoes/capturas-f8729aa1ee1a/`
  - as 7 telas a 1440 e 375, com fatias;
  - `estado-fora/`, `estado-vazio/` e `estado-carregando-biblioteca-*`;
  - `bib-busca-vazia.png`.

## O que verifiquei e como

### Código e segurança
- `tsc` exit 0 · `eslint` exit 0.
- Build em `.next-verificacao` exit 0 (BUILD_ID `HvTT3B54WzeauNYyuqyHs`).
- `grep` de chaves no `static` vazio; nenhum `NEXT_PUBLIC_`; `npm audit` 0; nenhuma cor crua fora de `src/app/design/`.

### Rota nova `/miniatura/[id]`
Testada no build com 7 endereços.

**Como ela se protege:**
- o endereço não escolhe o arquivo: o caminho vem do banco, só para aquele material (`miniaturaDoMaterial(id)`);
- só aceita extensão de imagem;
- `resolve` + `startsWith(<raiz>/videos/)`;
- `stat` e só arquivo.

**O que respondeu:**
- `..%2F..%2F.env`, `<slug>:..%2F..%2F.env`, `constructor`, `%00` e um id inexistente dão **404**;
- os materiais reais (`2026-09-17-demis-hassabis:extras` e o PDF do Jensen) dão **200 `image/png`**.

**Limite:** serve qualquer imagem de `videos/` que o banco aponte, inclusive de `material/obra/` (cópia de estudo). O painel só
abre em `127.0.0.1`, então não há exposição.

### A tela Biblioteca contra o banco
Consultas só de leitura, sincronização das 05:48.

**Tipos e totais**
- Todos 639 · Vídeos 333 · Imagens 240 · Documentos 41 · Pesquisas 22 · Referências 118 · Áudio 0: igual a
  `biblioteca_por_tipo` e `biblioteca_referencias`.
- Armazenamento: **6,73 GB** = 6.725.597.758 bytes, "639 arquivos em 12 vídeos".
- Por tipo: vídeos 6,29 GB · 93,5 %, imagens 434 MB · 6,5 %, documentos e pesquisas 3,3 MB, outros 3 arquivos · 860 KB.
- Gravações fora da conta: "216,2 GB", que é a soma de `principal_bytes`.
- **A divergência declarada (639 / 6,73 GB contra 659 / 13,95 GB da maquete) confere com o banco.** A limpeza de 23/10
  apagou material.

**Recentes**
- "Ver todos os 44 materiais" = 44 materiais com arquivo.
- Os 8 recentes são os 8 mais novos de `biblioteca_materiais_resumo`, na ordem, com tamanho e data:
  - Comandos de estilo 21/10 21:21;
  - Livro · cenas extras 19:12;
  - 50 comandos 18:37;
  - Livro · imagens 17:10;
  - gravação de tela 17:03;
  - capas 16:26;
  - Jensen · YouTube 17/10 15:53 (148 trechos, 4,65 GB);
  - Fei-Fei · fotos 15:38.
- "Quem adicionou" sai com "· inferido" (fecha a parte da tela do PI44).

**Mais utilizados**
- 12 · 9 · 4 · 4, igual a `biblioteca_mais_utilizados`, ordenado por número de usos (desvio declarado, aceito).
- A nota diz que o número vem da regra do pipeline, não de um registro de uso.

**Por vídeo**
- Jensen 4,78 GB · Golpes 571 MB · Fei-Fei 320 MB · Agente 3 passos 228 MB · Hinton 219 MB.
- Cada valor com a sua unidade (desvio declarado, aceito: são grandezas diferentes).

### Interação
- Chip "Imagens" dá 19 cartões; busca "jensen" dá 4.
- O dropdown Vídeo lista os vídeos, e Vídeo = Fei-Fei dá 5.
- Sem resultado: "Nada recente com esse filtro" + "Limpar filtros".
- "Adicionar material" abre o pedido (`/material <tema ou pessoa>`).
- `aria-pressed` nos chips; `aria-expanded` nos dropdowns.

### Estados (vistos rodando no meu servidor)
- **Erro:** banco fora do ar, 6 blocos com "Tentar de novo".
- **Vazio:** "Nenhum material ainda", "Nada usado em mais de um vídeo", "Pasta vazia".
- **Carregando:** 53 blocos de esqueleto com `role=status` nos 4 blocos.
- 1440 e 375 sem rolagem lateral.

### Telas
- 14 capturas (7 telas × 1440/375) com `scrollWidth` igual à janela.
- **Detector de texto cortado**, 7 larguras de 375 a 1920:
  - na Biblioteca, só a 1024: os 4 nomes do PI52 (design), já previstos na maquete, todos com `title`;
  - nas outras telas, só os dois casos conhecidos (PI41 e PI53 (design)).
- Auditoria de acessibilidade pelo DOM nas 8 rotas: igual à volta anterior, mais a Biblioteca com o `h1` "biblioteca." e
  sem nada sem nome, sem `alt` ou com id repetido. Console limpo.

### As 6 telas aprovadas (o código compartilhado mudou)
Mudaram `ListaKv`, `Numeros`, `Graficos`, `Pagina`, `Selecao`, `FiltroLista`, `db.ts`, `formato.ts` e `producao.ts`.
- Tokens contra o banco na sincronização das 05:48: 65.548.140 → "65,5M"; US$ 956,92 → "£ 714"; £ 546,29 em 7 dias → £ 2.341.
- Custo por vídeo: igual à volta anterior.
- Detector, acessibilidade e console: sem regressão.

### PI64
- `lib/producao.ts:186`: o legado sem selo só vence com `motivos.length === 0`. **Fechado.**

### Desvios declarados
| Desvio | Veredicto |
|---|---|
| 639 / 6,73 GB contra 659 / 13,95 GB da maquete | **aceito**: é o banco depois da limpeza de 23/10 |
| "mais utilizados" pelo número de usos | **aceito** |
| "Por vídeo" com a unidade de cada valor | **aceito** |
| Miniatura recortada pelo topo (`objectPosition 50% 0` em `components/Biblioteca.tsx:37`) contra o `acrescimos.css:530` (`50% 20%`) | **aceito**. A maquete aprovada mostra o topo (a `<img>` fica na altura natural e a caixa corta embaixo), então o app segue o que o Carlos viu. A contradição entre o CSS e a maquete é da designer (PI66) |

## O que NÃO verifiquei (declarado)
- **Leitor de tela de verdade, Safari, 320 px e a janela de preview do app Claude.** A :3456 do Carlos não estava no ar.
- **Miniatura de material novo sem recorte da designer:** só vi duas pela rota (`extras` do Demis e o PDF do Jensen).
- **O vazio num Postgres vazio de verdade:** usei o servidor de mentira.
- **"Copiar o pedido":** não cliquei.
- **Banco × disco:** a área `dados` está ⌛ vencida e cabe ao PORTÃO-DADOS. Conferi a tela contra o banco.
- **As capturas do front-end:** não usei como prova.
- **Efeitos colaterais meus:**
  - refiz a `.next-verificacao`;
  - o `next dev` regravou o `next-env.d.ts`;
  - derrubei todos os meus servidores.

## Backlog (só acrescentado)
| Nº | Classe | Onde | Achado | Dono | Gatilho |
|---|---|---|---|---|---|
| PI65 | S2 | `src/app/biblioteca/_componentes/Materiais.tsx:48–51`, vazio de "Por vídeo", busca a 375 | Três problemas de texto na Biblioteca. (a) Busca sem resultado (ex.: "zzzz") mostra "As músicas geradas ficam na pasta de edição… e as referências em 00-marca/", frase que o `biblioteca.md` pensou só para Áudio e Referências. (b) O vazio de "Por vídeo" fala em "o espaço por tipo", copiado do Armazenamento. (c) A 375 o texto de exemplo da busca corta ("…vídeos, in") | engenheiro-frontend | próxima mudança na Biblioteca |
| PI66 | S2 | `painel/design/acrescimos.css:530` × `telas/biblioteca.html` | A regra do CSS (`object-position: 50% 20%`) e a maquete (topo da imagem) dizem coisas diferentes; o app seguiu a maquete | designer-de-produto | próxima volta de design |
| PI64 (fecho) | — | `lib/producao.ts:186` | Legado sem selo só vence sem mensagens | — | ✅ 24/10 |
| PI-L1 | S1-L (continua) | ficha e Contratar | Sem desenho aprovado | engenheiro-frontend | quando houver desenho |

## S0-L abertos
Nenhum.

## Para o agente principal
- A área `interface` está aprovada com as 7 telas.
- O painel só chega ao Carlos com `exigir painel` limpo, e a área **dados está ⌛ vencida**: falta o PORTÃO-DADOS.
