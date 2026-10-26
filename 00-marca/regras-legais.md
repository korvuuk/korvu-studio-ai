# Regras Legais e de Plataforma — Korvu Reels

> Regras obrigatórias pra roteiro, edição, legenda e automação. Na dúvida, não publica e pergunta.
> Isto não é parecer jurídico. Em caso concreto (reclamação, notificação, parceria), consultar um advogado.

---

## 1. Imagem de pessoas

- **Pessoa pública, em conteúdo editorial sobre ela: pode** (decisão do Carlos, 2026-09-17, para a série sobre ícones da internet), **desde que o material seja licenciado ou oficial** e com **crédito na legenda do post** (desde 19/10 o crédito NÃO vai na tela — decisão do Carlos, `docs/decisoes.md`; fica completo na descrição):
  - foto de **press kit/newsroom** da empresa, **Wikimedia Commons** (com a licença CC anotada), **domínio público** ou banco licenciado;
  - **trecho curto de vídeo** (≤ 10 s por clipe, com a fala do Carlos por cima), vindo de **newsroom oficial, canal do próprio titular quando a licença permitir, ou arquivo licenciado**.
  - Cada arquivo entra com licença + autor + link em `videos/<slug>/material/fontes.json`. **Sem licença identificada, não usa.**
- **Proibido, mesmo com o material em mãos:** baixar de YouTube/Instagram/TikTok de terceiros (viola os termos dessas plataformas); **deepfake, imagem realista gerada por IA ou clone de voz** da pessoa; montar de forma que sugira que ela endossa a Korvu; usar fora do contexto editorial (ex.: como isca na capa).
- **Pessoa privada** (cliente, conhecido, criança) continua exigindo autorização por escrito — criança, não.
- Frame de keynote/evento público: só em contexto editorial, rápido, com fonte, e nunca na capa.
- Visual realista gerado por IA → usar o rótulo de IA do Instagram e avisar na legenda ("Imagem gerada com IA").
- Cliente ou pessoa que aparece em gravação: só com autorização. Criança: não.

## 2. Marcas e logos de terceiros

- Pode citar e mostrar a ferramenta que está sendo explicada (ChatGPT, Gemini, Claude, Canva…) — uso para **identificar** o produto.
- Não alterar logo, não usar como se fosse da Korvu, não sugerir parceria ou patrocínio que não existe ("parceiro oficial", "certificado por").
- Gravação de tela das ferramentas feita pela gente: pode.
- Parceria paga de verdade → usar o rótulo "Parceria paga" do Instagram.

## 3. Notícias e afirmações

- Toda afirmação de notícia tem **link da fonte** no roteiro (`fontes`) e **fonte na legenda** ("Fonte: veículo, data").
- Confirmar em 2 fontes independentes ou na fonte oficial (blog da empresa). Uma fonte só → "segundo [fonte]".
- Conferir a data: não chamar de "novidade" algo com mais de 7 dias; não dizer "saiu ontem" se não saiu.
- Abrir o link e conferir que o texto diz o que o resumo diz (ver `fontes-noticias.md`).

## 4. Nada inventado

- **Proibido** fabricar história, número, depoimento, cliente, print, resultado ou "teste".
- **"Erro de R$X" só com história real do Carlos** — valor e ano confirmados por ele.
- "Eu fiz", "testei", "me economiza X horas" → só se aconteceu, com prova (gravação de tela, arquivo).
- Caso de cliente: só com autorização por escrito e anonimizado quando necessário.
- Estatística sempre com fonte e data. Sem fonte → não usa.

## 5. Promessas

- **Não prometer resultado nem renda**: nada de "ganhe R$ X com IA", "fique rico", "nunca mais trabalhe", "garantido".
- Economia de tempo/dinheiro vem com contexto: "no meu caso", "nesse exemplo", "pode variar".
- Sem conselho de saúde, jurídico ou financeiro individual — só informação geral e indicação de procurar um profissional.

## 6. Música

- **Padrão (01/10): faixa original gerada pela ElevenLabs Music** para cada vídeo, em `videos/<slug>/musica/` com a procedência em `musica.json` (`scripts/gerar_musica.py`). Uso comercial exige plano pago na conta.
- Faixa de banco (Meta Sound Collection, banco pago) só em `00-marca/assets/musica/`, com o arquivo de licença ao lado. A da Meta vale **só** no Instagram/Facebook.
- Não baixar música comercial de outro lugar pra usar na edição.
- Conta comercial no Instagram tem biblioteca de áudio limitada — na dúvida, usar só as faixas da pasta.

## 7. Direito autoral de vídeo

- Nunca repostar clipe de outra pessoa (nem com crédito). Ver regra de originalidade em `pilares.md`.
- B-roll só próprio ou licenciado (guardar comprovante).
- Citação de texto de notícia: curta, entre aspas, com fonte.

## 8. DMs e automação

- A automação de DM (Claude) **se identifica como assistente de IA na primeira mensagem** (modelo em `cta.md`).
- Nunca se passar pelo Carlos. Sempre oferecer contato com uma pessoa.
- Respeitar "parar"/"sair" na hora.
- Seguir as políticas da Meta pra mensagens automáticas (limites e janelas). Configuração em `automacao-meta/`.

## 9. Dados pessoais (LGPD / GDPR)

A Korvu fala com público no Brasil (LGPD) e na Europa/Reino Unido (GDPR / UK GDPR).
- Coletar só o necessário (normalmente: nome de usuário e, se precisar, e-mail).
- Dizer **pra quê** o dado é usado antes de pedir. Consentimento explícito pra lista de e-mail/marketing.
- Garantir acesso, correção e exclusão quando a pessoa pedir.
- Guardar em lugar seguro — nunca em planilha pública ou link aberto.
- Não colocar dado pessoal de lead em ferramenta de IA sem necessidade.
- Borrar dado pessoal em gravação de tela (contatos, e-mails, telefones, CPF, endereços).
- Segredos (tokens, chaves de API, senhas) só no `.env`, nunca no repositório, roteiro ou vídeo.

## 10. Hashtags

- **Máximo 5 por post** (limite do Instagram). Todas relevantes ao tema; nada de #viral #fyp.

---

## Checklist legal antes de publicar

- [ ] Nenhuma pessoa real além do Carlos em imagem/vídeo realista
- [ ] Logos de terceiros só pra identificar a ferramenta, sem sugerir parceria
- [ ] Notícia/dado com fonte na legenda e data conferida
- [ ] Nenhuma história, número ou resultado inventado
- [ ] Nenhuma promessa de resultado ou renda
- [ ] Música gerada (`videos/<slug>/musica/musica.json`) ou da pasta `00-marca/assets/musica/` com licença
- [ ] Nenhum clipe de terceiros
- [ ] Dados pessoais borrados em tela
- [ ] Se CTA tipo A: aviso de IA configurado na DM
- [ ] Rótulo de IA aplicado, se houver visual realista gerado por IA
- [ ] Máximo 5 hashtags
