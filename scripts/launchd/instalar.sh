#!/bin/bash
# Instala os agendadores (launchd, utilizador atual):
#   uk.korvu.publicar    → scripts/publicar.py --due, a cada 15 min
#   uk.korvu.comentarios → scripts/responder_comentarios.py, a cada 2 min (palavra-chave → material no direct)
#   uk.korvu.metricas    → scripts/metricas.py, 1×/dia às 09:30 (métricas dos Reels com ≥ 5 dias, só leitura)
#   uk.korvu.painel      → painel/sync/sincronizar.py, a cada 15 min + ao entrar (arquivos → banco do painel, só leitura)
#   bash scripts/launchd/instalar.sh                   → instala e carrega os quatro
#   bash scripts/launchd/instalar.sh uk.korvu.comentarios → só um
#   bash scripts/launchd/instalar.sh --so-gerar X [label] → só gera o plist final em X (não instala)
#
# Nota macOS: ~/Documents é protegido (TCC). Se o log mostrar "Operation not permitted",
# dê acesso a "Pastas e ficheiros > Documentos" (ou Acesso Total ao Disco) ao binário do uv/python
# em Ajustes do Sistema > Privacidade e Segurança.
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
PROJETO="$(cd "$DIR/../.." && pwd)"
UV="${UV_BIN:-$(command -v uv || true)}"
[ -z "$UV" ] && [ -x /opt/homebrew/bin/uv ] && UV=/opt/homebrew/bin/uv
if [ -z "$UV" ] || [ ! -x "$UV" ]; then
  echo "uv não encontrado. Defina UV_BIN=/caminho/para/uv" >&2
  exit 1
fi

gerar() {  # gerar <saida> <label>
  sed -e "s|__UV__|$UV|g" -e "s|__PROJETO__|$PROJETO|g" -e "s|__HOME__|$HOME|g" \
      "$DIR/$2.plist" > "$1"
  plutil -lint "$1" >/dev/null
}

if [ "${1:-}" = "--so-gerar" ]; then
  gerar "${2:?indique o arquivo de saída}" "${3:-uk.korvu.publicar}"
  echo "Gerado: $2"
  exit 0
fi

mkdir -p "$PROJETO/_controle/logs" "$HOME/Library/LaunchAgents"
LABELS="${*:-uk.korvu.publicar uk.korvu.comentarios uk.korvu.metricas uk.korvu.painel}"
for LABEL in $LABELS; do
  DESTINO="$HOME/Library/LaunchAgents/$LABEL.plist"
  gerar "$DESTINO" "$LABEL"
  launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
  launchctl bootstrap "gui/$(id -u)" "$DESTINO"
  launchctl enable "gui/$(id -u)/$LABEL"
  echo "✓ Instalado: $DESTINO"
  echo "  Forçar uma execução agora: launchctl kickstart -k gui/$(id -u)/$LABEL"
done
echo "  Logs: _controle/logs/publicar.log, comentarios.log, metricas.log e painel.log"
