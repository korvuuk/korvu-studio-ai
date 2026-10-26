#!/usr/bin/env python3
"""Renderiza a composição Remotion `Reel` → videos/<slug>/edicao/render-remotion.mp4.

Saída 8-bit yuv420p bt709 (Instagram) no fps de reel-props.json ("fps" = edl.json.fps = FPS_PROJETO, padrão 25),
H.264 CRF 18, AAC. Bloqueado enquanto edl.json.aprovado != true (use --auto só se o Carlos pedir).
Extras faltando não bloqueiam: saem como placeholder "EXTRA Exx FALTANDO" e o QA reprova.

Uso:
  uv run python .claude/skills/legendas-animadas/scripts/render_reel.py videos/<slug> [--auto] [--concurrency 4]
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gerar_props import FFPROBE, REMOTION, garantir_link, ler_json  # noqa: E402


def fracao(s: str | None) -> float:
    if not s or s == "0/0":
        return 0.0
    n, _, d = s.partition("/")
    return float(n) / float(d or 1)


def main() -> None:
    ap = argparse.ArgumentParser(description="Render do Reel no Remotion (H.264 CRF 18, fps do projeto)")
    ap.add_argument("video_dir", type=Path)
    ap.add_argument("--auto", action="store_true", help="ignora edl.aprovado (só com pedido explícito)")
    ap.add_argument("--saida", type=Path, help="padrão: edicao/render-remotion.mp4")
    ap.add_argument("--concurrency", type=int, default=None)
    a = ap.parse_args()

    video_dir = a.video_dir.resolve()
    edicao = video_dir / "edicao"
    edl = ler_json(edicao / "edl.json")
    if edl.get("aprovado") is not True and not a.auto:
        raise SystemExit("BLOQUEADO: edl.json.aprovado != true (regra 1 do CLAUDE.md). Use --auto só se o Carlos pedir.")

    props_p = edicao / "reel-props.json"
    if not props_p.exists():
        raise SystemExit(f"{props_p} não existe — rode gerar_props.py antes.")
    props = ler_json(props_p)
    slug = edl.get("slug") or video_dir.name
    garantir_link(slug, edicao)

    video_public = REMOTION / "public" / props["video"]
    if not video_public.exists():
        raise SystemExit(f"Vídeo não encontrado via public/: {video_public}")
    fps_esp = float(props.get("fps") or edl.get("fps") or 25)
    if abs(fps_esp - float(edl.get("fps") or fps_esp)) > 0.01:
        raise SystemExit(f"reel-props.json ({fps_esp:g} fps) ≠ edl.json ({edl.get('fps')} fps) — rode gerar_props.py")
    faltam = [o.get("extra") for o in props.get("overlays", []) if o.get("tipo") == "extra" and o.get("faltando")]
    if faltam:
        print(f"AVISO: extras faltando ({', '.join(faltam)}) — saem como placeholder; o QA vai reprovar.", flush=True)

    # --saida relativo é relativo à PASTA DO VÍDEO (não ao cwd), senão "edicao/x.mp4" cai fora do vídeo
    saida = (edicao / "render-remotion.mp4" if a.saida is None
             else a.saida if a.saida.is_absolute() else video_dir / a.saida).resolve()
    npx = shutil.which("npx") or "npx"
    cmd = [
        npx, "remotion", "render", "Reel", str(saida),
        f"--props={props_p}",
        "--codec=h264", "--crf=18", "--pixel-format=yuv420p", "--color-space=bt709",
        "--audio-codec=aac", "--enforce-audio-track", "--overwrite",
    ]
    if a.concurrency:
        cmd.append(f"--concurrency={a.concurrency}")
    print("→", " ".join(cmd[1:4]), f"… ({fps_esp:g} fps)", flush=True)
    r = subprocess.run(cmd, cwd=REMOTION)
    if r.returncode != 0:
        raise SystemExit(f"Remotion falhou (código {r.returncode})")

    info = json.loads(subprocess.run(
        [FFPROBE, "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(saida)],
        capture_output=True, text=True, check=True).stdout)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    fps_out = fracao(v.get("r_frame_rate"))
    ok_fps = abs(fps_out - fps_esp) <= 0.01
    print(f"OK: {saida}  {v['width']}x{v['height']} {v['r_frame_rate']} fps {v.get('pix_fmt')}  "
          f"{float(info['format']['duration']):.2f}s  → próximo passo: audio.py (loudnorm) + qa_check.py")
    if not ok_fps:
        raise SystemExit(f"ERRO: render saiu a {fps_out:g} fps, esperado {fps_esp:g} (props.fps)")


if __name__ == "__main__":
    main()
