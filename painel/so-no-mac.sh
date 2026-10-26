#!/usr/bin/env bash
# Supabase do painel só no próprio Mac (PD9, 23/10).
#
# O Docker daqui é o Colima com encaminhador `ssh`: porta que o contêiner publica em 0.0.0.0 dentro da VM vira
# `*:porta` no Mac (a rede local inteira vê); porta publicada em 127.0.0.1 vira `127.0.0.1:porta` (só o Mac).
# O config.toml do Supabase CLI não tem opção de endereço de escuta, então o caminho é o da documentação do Supabase
# ("Local development", aviso sobre rede não confiável): uma rede Docker com
# `com.docker.network.bridge.host_binding_ipv4=127.0.0.1`. Ela leva o nome que o CLI usa por padrão
# (`supabase_network_<project_id>`), então TODO comando do CLI no painel (start, db reset, db diff…) já cai nela sem
# flag. É criada SEM o rótulo do CLI, para o `supabase stop` não a apagar. Nada aqui toca no Colima, no firewall do
# macOS nem nos contêineres `*_MUNTUZA_CMS`.
#
#   bash painel/so-no-mac.sh            confere: rede certa, contêineres do painel só em 127.0.0.1, 553xx só em 127.0.0.1
#   source painel/so-no-mac.sh          (iniciar.sh, studio.sh) garantir_rede · conferir_portas · studio_ligado ·
#                                       supabase_painel <comando do CLI>

PAINEL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJETO_PAINEL="content-ai-painel"
REDE_PAINEL="supabase_network_${PROJETO_PAINEL}"
OPCAO_IP="com.docker.network.bridge.host_binding_ipv4"

# CLI do Supabase no painel, sem o falatório (inclusive o aviso fixo do CLI "All services bind to 0.0.0.0", que é
# texto genérico e aqui não vale — quem diz onde as portas escutam é o conferir_portas). Se falhar, mostra tudo.
supabase_painel() {
  local log rc=0
  log=$(mktemp "${TMPDIR:-/tmp}/supabase-painel.XXXXXX")
  (cd "$PAINEL_DIR" && supabase "$@") >"$log" 2>&1 || rc=$?
  if [ "$rc" -ne 0 ]; then cat "$log" >&2; echo "✗ supabase $* falhou (código $rc)" >&2; fi
  rm -f "$log"
  return "$rc"
}

_conferir_projeto() {
  grep -q "^project_id = \"${PROJETO_PAINEL}\"" "$PAINEL_DIR/supabase/config.toml" || {
    echo "✗ painel/supabase/config.toml não é do projeto ${PROJETO_PAINEL} — nada foi parado" >&2; return 1; }
}

# Garante a rede do painel publicando só em 127.0.0.1. Se ela existir publicando em outro endereço (ex.: criada pelo
# CLI antes do PD9), para SÓ o Supabase do painel (sem --no-backup: os dados ficam no volume) e recria a rede.
garantir_rede() {
  _conferir_projeto || return 1
  local ip
  if ip=$(docker network inspect "$REDE_PAINEL" --format "{{index .Options \"$OPCAO_IP\"}}" 2>/dev/null); then
    [ "$ip" = "127.0.0.1" ] && return 0
    echo "rede ${REDE_PAINEL} publica em ${ip:-0.0.0.0 e [::]}: parando o Supabase do painel para recriá-la só em 127.0.0.1" >&2
    supabase_painel stop || return 1
    docker network rm "$REDE_PAINEL" >/dev/null 2>&1 || true   # o stop já apaga a rede que o CLI criou com rótulo
  fi
  docker network create -o "${OPCAO_IP}=127.0.0.1" "$REDE_PAINEL" >/dev/null || return 1
  echo "rede ${REDE_PAINEL} criada (só 127.0.0.1)" >&2
}

# Recusa (exit 1) se algum contêiner do painel publicar fora de 127.0.0.1 ou se o Mac escutar alguma 553xx fora de
# 127.0.0.1. O encaminhador do Colima leva uns segundos para acompanhar: tenta por até ~15 s antes de recusar.
conferir_portas() {
  local docker_aberto lsof_aberto i
  for i in $(seq 1 15); do
    docker_aberto=$(docker ps --filter "label=com.supabase.cli.project=${PROJETO_PAINEL}" \
      --format '{{.Names}} {{.Ports}}' | grep -E '0\.0\.0\.0:|\[::\]:' || true)
    lsof_aberto=$(lsof -nP -iTCP -sTCP:LISTEN 2>/dev/null | awk '$9 ~ /:553[0-9][0-9]$/ && $9 !~ /^127\.0\.0\.1:/' || true)
    [ -z "$docker_aberto" ] && [ -z "$lsof_aberto" ] && return 0
    sleep 1
  done
  echo "✗ Supabase do painel aberto para a rede local (deveria ser só 127.0.0.1):" >&2
  [ -n "$docker_aberto" ] && echo "$docker_aberto" >&2
  [ -n "$lsof_aberto" ] && echo "$lsof_aberto" >&2
  echo "  conserto: bash painel/so-no-mac.sh (diz o que está errado); a rede ${REDE_PAINEL} precisa de ${OPCAO_IP}=127.0.0.1" >&2
  return 1
}

studio_ligado() {
  [ -n "$(docker ps -q --filter "name=^supabase_studio_${PROJETO_PAINEL}$" --filter status=running)" ]
}

# Rodado direto: só confere e mostra o estado; não muda nada.
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  set -euo pipefail
  ip=$(docker network inspect "$REDE_PAINEL" --format "{{index .Options \"$OPCAO_IP\"}}" 2>/dev/null || echo "sem rede")
  echo "rede ${REDE_PAINEL}: ${ip:-0.0.0.0 e [::] (padrão do Docker)}"
  docker ps --filter "label=com.supabase.cli.project=${PROJETO_PAINEL}" --format '  {{.Names}}  {{.Ports}}' | sort
  echo "escutando no Mac (553xx):"
  lsof -nP -iTCP -sTCP:LISTEN 2>/dev/null | awk '$9 ~ /:553[0-9][0-9]$/ {print "  " $9}' | sort -u
  if [ -z "$(docker ps -q --filter "name=^supabase_db_${PROJETO_PAINEL}$")" ]; then
    echo "Supabase do painel PARADO — subir: bash painel/iniciar.sh"; fi
  if studio_ligado; then echo "Studio: LIGADO em http://127.0.0.1:55323 (sem senha) — desligar: bash painel/studio.sh desliga"
  else echo "Studio: desligado — ligar: bash painel/studio.sh liga"; fi
  if [ "$ip" = "127.0.0.1" ] && conferir_portas; then echo "✓ só no Mac (127.0.0.1)"; else echo "✗ não está só no Mac"; exit 1; fi
fi
