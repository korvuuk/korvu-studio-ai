#!/bin/bash
# Remove os agendadores (launchd). Sem argumentos remove os quatro; ou indique o label.
#   bash scripts/launchd/desinstalar.sh uk.korvu.comentarios
set -uo pipefail
for LABEL in ${*:-uk.korvu.publicar uk.korvu.comentarios uk.korvu.metricas uk.korvu.painel}; do
  DESTINO="$HOME/Library/LaunchAgents/$LABEL.plist"
  if launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null; then
    echo "✓ $LABEL descarregado do launchd"
  else
    echo "($LABEL não estava carregado)"
  fi
  rm -f "$DESTINO" && echo "✓ Removido $DESTINO"
done
