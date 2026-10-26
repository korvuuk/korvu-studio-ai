#!/usr/bin/env bash
# Sobe o painel local: banco (Supabase do painel, portas 553xx, só em 127.0.0.1 e sem o Studio — PD9), sincroniza os
# arquivos e abre o app em :3456. Studio: bash painel/studio.sh liga|desliga.
set -euo pipefail
cd "$(dirname "$0")"
source ./so-no-mac.sh
garantir_rede
supabase_painel start
conferir_portas
if studio_ligado; then echo "aviso: o Studio está ligado (sem senha) — ao acabar: bash painel/studio.sh desliga" >&2; fi
(cd .. && uv run python painel/sync/sincronizar.py)
cd web && npm run dev
