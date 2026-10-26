"""Verifica se o estúdio está pronto (fase 0). Não imprime valores de segredos.

Uso: uv run python scripts/verificar_setup.py
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from dotenv import dotenv_values

RAIZ = Path(__file__).resolve().parents[1]
ENV = {**dotenv_values(RAIZ / ".env"), **os.environ} if (RAIZ / ".env").exists() else dict(os.environ)
OK, AV, ER = "[OK]   ", "[AVISO]", "[FALTA]"
falhas = 0


def linha(status: str, item: str, detalhe: str = "") -> None:
    global falhas
    falhas += status == ER
    print(f"{status} {item}" + (f" — {detalhe}" if detalhe else ""))


def versao(cmd: list[str]) -> str | None:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=20).stdout.splitlines()[0]
    except Exception:
        return None


print("== Binários ==")
ffmpeg = ENV.get("FFMPEG_BIN") or "/Users/teste/bin/ffmpeg"
v = versao([ffmpeg, "-version"])
if v:
    conf = subprocess.run([ffmpeg, "-hide_banner", "-buildconf"], capture_output=True, text=True).stdout
    faltam = [f for f in ("libass", "libzimg", "libx264") if f"--enable-{f}" not in conf]
    linha(OK if not faltam else AV, f"ffmpeg ({ffmpeg})", v.split(" Copyright")[0] + (f"; sem {faltam}" if faltam else ""))
else:
    linha(ER, "ffmpeg", ffmpeg)
ffprobe = ENV.get("FFPROBE_BIN") or shutil.which("ffprobe") or ""
linha(OK if versao([ffprobe, "-version"]) else ER, "ffprobe", ffprobe)
for b in ("uv", "node", "npx", "yt-dlp"):
    p = shutil.which(b)
    linha(OK if p else ER, b, p or "brew install " + b)
chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
linha(OK if Path(chrome).exists() else AV, "Chrome (PDF do material)", "" if Path(chrome).exists() else "instale o Google Chrome")

print("\n== Projeto ==")
linha(OK if (RAIZ / "remotion/node_modules/remotion").exists() else ER, "Remotion instalado", "cd remotion && npm i")
esperadas = ["roteiro-reels", "corte-por-roteiro", "audio-polish", "color-grading", "legendas-animadas",
             "capa-reels", "animacoes-explicativas", "qa-video", "watch", "remotion-best-practices"]
for s in esperadas:
    linha(OK if (RAIZ / ".claude/skills" / s / "SKILL.md").exists() else ER, f"skill {s}")
agentes = sorted(p.stem for p in (RAIZ / ".claude/agents").glob("*.md"))
linha(OK if len(agentes) >= 9 else AV, f"{len(agentes)} agentes", ", ".join(agentes))
cfg = Path.home() / ".config/watch/.env"
linha(OK if cfg.exists() and "SETUP_COMPLETE=true" in cfg.read_text() else AV, "/watch configurado", str(cfg))

print("\n== Chaves (.env) ==")
if not (RAIZ / ".env").exists():
    linha(AV, ".env", "copie .env.example para .env e preencha")
for k, uso in [("ELEVENLABS_API_KEY", "transcrição Scribe (senão usa mlx local)"),
               ("INSTAGRAM_USER_ID", "publicar IG"), ("INSTAGRAM_ACCESS_TOKEN", "publicar IG"),
               ("META_PAGE_ID", "publicar FB"), ("META_PAGE_ACCESS_TOKEN", "publicar FB"),
               ("R2_ACCOUNT_ID", "URL pública do vídeo"), ("R2_BUCKET_NAME", "URL pública do vídeo"),
               ("R2_PUBLIC_URL", "URL pública do vídeo")]:
    linha(OK if ENV.get(k) else AV, k, "definida" if ENV.get(k) else f"vazia ({uso})")

print("\n== Insumos do Carlos ==")
insumos = [("00-marca/referencias/legendas", "imagem de referência da legenda"),
           ("00-marca/design-system", "guideline / design system"),
           ("00-marca/cor/referencias", "referências de cor"),
           ("02-calibracao/amostras", "amostras de voz")]
for pasta, nome in insumos:
    tem = [p for p in (RAIZ / pasta).glob("*") if p.is_file() and not p.name.startswith(".") and p.suffix != ".md"]
    linha(OK if tem else AV, nome, f"{len(tem)} arquivo(s) em {pasta}")

print(f"\n{'Tudo pronto.' if not falhas else f'{falhas} item(ns) obrigatório(s) faltando.'}")
raise SystemExit(1 if falhas else 0)
