"""Tira um print de uma página web (notícia, anúncio de ferramenta) para usar como cena extra.

Uso: uv run python scripts/print_pagina.py <url> videos/<slug>/brutos/extras/E03-print.png [--desktop] [--altura N]

- Padrão: layout de celular, 390×640 lógicos × 3 = 1170×1920 px (bom para os modos card/split).
- --desktop: janela 1440×900 lógicos × 2 = 2880×1800 px (manchete inteira, bom para full/split).
- --altura N: altura lógica da janela (celular ×3, desktop ×2) para capturar mais da página.
- Não clica em nada (banners de cookies/consentimento podem aparecer: o produtor-de-extras verifica o PNG
  e, se tapar a manchete, pede ao Carlos um print manual). Sempre registrar o crédito no roteiro.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
UA_MOBILE = ("Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 "
             "(KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1")


def main() -> int:
    args = sys.argv[1:]
    if len(args) < 2:
        print(__doc__)
        return 1
    url, saida = args[0], Path(args[1]).resolve()
    if not url.startswith(("http://", "https://")):
        print("ERRO: URL deve começar com http(s)://")
        return 1
    desktop = "--desktop" in args
    largura, altura, escala = (1440, 900, 2) if desktop else (390, 640, 3)
    if "--altura" in args:
        altura = int(args[args.index("--altura") + 1])
    saida.parent.mkdir(parents=True, exist_ok=True)
    # sem --user-data-dir: com perfil próprio o Chrome headless grava o PNG mas não encerra
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--mute-audio",
           f"--window-size={largura},{altura}", f"--force-device-scale-factor={escala}",
           "--virtual-time-budget=8000", f"--screenshot={saida}"]
    if not desktop:
        cmd.append(f"--user-agent={UA_MOBILE}")
    try:
        r = subprocess.run(cmd + [url], capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        r = None
    if not saida.exists():
        print(f"ERRO ao capturar {url}" + (f": {r.stderr[-400:]}" if r else " (tempo esgotado)"))
        return 1
    print(f"Print: {saida} ({largura * escala}×{altura * escala})")
    print("Lembrete: conferir o PNG (banner de cookies?) e preencher a coluna Crédito no roteiro.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
