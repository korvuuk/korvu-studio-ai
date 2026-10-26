# Briefing do redesign do painel (22/10/2026)

Escrito pelo agente principal para a `designer-de-produto`. As referências do Carlos entram nesta pasta.

## O pedido, nas palavras dele
- "Um sistema visual onde eu vou poder bater o olho e saber o que nós temos, o que nós fizemos."
- "Saber quem é quem… dar um nome, uma foto, um skill… quando a gente quiser contratar um novo funcionário, o que ele
  vai fazer."
- "Dashboard da minha página do Instagram… seguidores de países, os vídeos que estão performando, vídeos que floparam,
  o que funciona mais, qual formato funciona mais."
- "O nosso painel ainda está crua… reestruturar o layout, deixar ele mais organizado… um visual muito mais
  profissional… um sistema com a cara profissional, um sistema com cara premium."
- Ele acompanha também pelo celular.

## As telas de hoje e a pergunta que cada uma responde
| Rota | O Carlos abre para… |
|---|---|
| `/` visão geral | saber como está o estúdio hoje e o que precisa de atenção |
| `/equipe` | ver quem é quem, por departamento, e quem fiscaliza quem |
| `/equipe/<id>` | entender o que uma pessoa da equipe faz, com que modelo/skills, e o que ela aprovou |
| `/equipe/contratar` | descrever uma função nova e pedir ao Claude para contratar |
| `/videos` | ver em que etapa está cada vídeo e se os portões aprovaram; a fila de publicação |
| `/desempenho` | ver seguidores, de onde vem o público, que vídeo foi bem ou mal e o que funciona |

## Os dados que existem (banco do painel, `painel/supabase/migrations/`)
`departamentos`, `agentes` (nome, cargo, papel, modelo, skills, comandos, quem fiscaliza quem), `videos` (+ histórico
de estados), `portoes_estado` e `veredictos` (GAUNTLET), `fila`, `publicacoes`, `metricas` (uma linha por leitura, com
`suspeito`), `perfil_snapshots` (só 16/10 e 22/10 até agora), `perfil_demografia` (país, cidade, idade, gênero de quem
segue e de quem foi alcançado), `sincronizacoes`. **Não existe:** curva de retenção (a API da Meta não dá), evolução
diária de seguidores (só quando o `perfil.py` passar a rodar todo dia), dados do Facebook além de plays e tempo médio.

## O que os portões já acharam de cru (linha de base, 22/10)
Relatórios: `painel/portoes/interface-2026-10-22-v1.md` e `dados-2026-10-22-v1.md`; itens PI1–PI16 e PD1–PD8 em
`_controle/backlog-portoes.md`. Os que são de design: contraste abaixo de AA nos textos apagados e nos rótulos sobre o
laranja; dica do sinal de portão que sai da tela no celular; estados vazio/carregando/erro inexistentes; rótulos de
gráfico cortados; menu sem página atual; precisão misturada nos números; elementos recriados em cada página.

## Restrições
- Marca: `00-marca/design-system/korvu-editorial.md` (ponto de partida; desvio escrito com motivo e aprovado pelo
  Carlos). Nunca o `anthropic-skills:korvu-design-system` (é do CRM Korvu 2.0).
- PT-BR com "você"; autoria "korvu" / "@korvu_oficial"; nada de público por país/"lusófono" nos textos.
- Nenhum número inventado; 375 px sem rolagem lateral; estado nunca só por cor.

## O que ainda falta do Carlos
1. 3 a 5 referências de sistemas/painéis que ele acha premium (prints aqui ou links em `links.md`).
2. Escolher a direção de estilo depois das maquetes (editorial claro × sistema escuro × outra).
3. As 2–3 telas que mais importam no dia a dia.
