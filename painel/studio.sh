#!/usr/bin/env bash
# Liga e desliga o Supabase Studio do painel (PD9, 23/10). No dia a dia ele fica DESLIGADO (`[studio] enabled = false`
# no config.toml): o Studio e o postgres-meta (que o CLI só sobe junto com ele e que a API serve em /pg/*) não têm
# senha. Mesmo ligado, só responde no próprio Mac (http://127.0.0.1:55323) — ver painel/so-no-mac.sh. Ligar = subir com
# SUPABASE_STUDIO_ENABLED=true (o CLI aceita sobrepor qualquer chave do config.toml por SUPABASE_<SEÇÃO>_<CHAVE>).
#
#   bash painel/studio.sh liga       sobe o Studio (reinicia o Supabase do painel, ~30 s)
#   bash painel/studio.sh desliga    tira o Studio (reinicia o Supabase do painel, ~30 s)
#   bash painel/studio.sh            estado (rede, portas, Studio ligado ou não)
#
# Por que reinicia: o `supabase start` com o banco no ar não sobe serviço novo (só mostra o estado), e o CLI não tem
# como ligar um serviço sozinho. O reinício é só do painel (`supabase stop` SEM --no-backup: tabelas ficam no volume);
# o MUNTUZA_CMS não é tocado. Durante o reinício o app e a passagem do launchd (15 min) dão erro e voltam sozinhos.
set -euo pipefail
cd "$(dirname "$0")"
source ./so-no-mac.sh

case "${1:-estado}" in
  liga)
    garantir_rede
    if studio_ligado; then echo "Studio já está ligado: http://127.0.0.1:55323"; exit 0; fi
    echo "ligando o Studio (reinicia o Supabase do painel; os dados ficam)…"
    supabase_painel stop
    (export SUPABASE_STUDIO_ENABLED=true; supabase_painel start)
    conferir_portas
    studio_ligado || { echo "✗ o Studio não subiu — veja: cd painel && supabase status" >&2; exit 1; }
    echo "✓ Studio ligado: http://127.0.0.1:55323 (sem senha, só neste Mac). Ao acabar: bash painel/studio.sh desliga"
    ;;
  desliga)
    garantir_rede
    if ! studio_ligado && [ -z "$(docker ps -q --filter "name=^supabase_pg_meta_${PROJETO_PAINEL}$")" ]; then
      echo "Studio já está desligado"; exit 0
    fi
    echo "desligando o Studio (reinicia o Supabase do painel; os dados ficam)…"
    supabase_painel stop
    (unset SUPABASE_STUDIO_ENABLED; supabase_painel start)
    conferir_portas
    if studio_ligado; then echo "✗ o Studio continua ligado — confira [studio] enabled no config.toml" >&2; exit 1; fi
    echo "✓ Studio desligado (porta 55323 fechada)"
    ;;
  estado)
    exec bash ./so-no-mac.sh
    ;;
  *)
    echo "uso: bash painel/studio.sh [liga|desliga]" >&2; exit 2
    ;;
esac
