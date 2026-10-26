# Automação Meta

**Leia `ARQUITETURA.md`** — como o projeto posta no Instagram/Facebook e entrega o material quando alguém
comenta a palavra-chave, o que já está pronto e o checklist para ligar.

- Textos das respostas (comentário e direct), limites, liga/desliga: `respostas.yaml`
- Postar: `scripts/publicar.py` · Comentários → direct: `scripts/responder_comentarios.py`
- Configurar o app na Meta (tokens, permissões, conta nova): `CONFIGURAR-APP-META.md`
- Agendadores: `scripts/launchd/instalar.sh` (os dois) / `desinstalar.sh`

**Mudança de 2026-10-09:** o plano anterior (bot com Claude conversando no direct, dentro do korvu20-crm, com
webhooks e Supabase) foi **abandonado**. O Carlos não quer vender nem conversar agora: só entregar o material.
Sem CRM, sem servidor, sem conversa.

Referências: [private replies](https://developers.facebook.com/docs/instagram-platform/private-replies) ·
[webhooks](https://developers.facebook.com/docs/instagram-platform/webhooks) ·
[política de mensagens](https://developers.facebook.com/documentation/business-messaging/messenger-platform/policy)
