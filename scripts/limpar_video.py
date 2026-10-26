#!/usr/bin/env python3
"""Limpa a pasta de um vídeo: deixa só o que é preciso para o arquivo final.

Regra do Carlos (2026-09-16): "remover tudo que não é necessário para o arquivo final" e, nas revisões,
"manter só a atual". Sem isso a pasta acumulava revisao-v1…v8 (≈ 660 MB de rascunho no 1.º vídeo).

MANTÉM
  edicao/  corte.mp4 · corte-audio.wav · final.mp4 (e variantes final-L01B…) · cor/ · fontes/ · audio48k/ ·
           audio16k/ · raw/ · frames/ · extras/ · remotion/ · todos os .json/.md/.srt
           (inclusive edl.auto.json, que o `edl.py --recalcular` usa para saber o que você editou à mão)
           + a revisão MAIS NOVA: revisao-vN.mp4 e revisao-vN-leve.mp4
  capa/    capa.png · grade-3x4.png · titulo.json · capa.props.json
           candidatos/: contato.jpg · scores.json · o frame que virou capa (status.json → capa.frame)

REMOVE  revisões antigas e suas variantes (-sem-cartazes, -legendas, -leve de versões velhas),
        render-remotion.mp4, preview.mp4, edl.v1-auto.json, capas não escolhidas e os candidatos não usados.
        (Capa que está num pacote de 05-render-pronto/ ou 06-publicar/ — a de cada variante — FICA.)

NUNCA TOCA em brutos/ nem em material/. Atenção a material/obra/ (a obra comentada, /obra): pode ter 1 GB+
e PARECE lixo, mas é a fonte dos trechos citados e da conferência de marcas de tempo — quem apaga tem de
baixar tudo de novo. Se um dia fizer sentido limpar, tem de ser pergunta ao Carlos, nunca automático.

Uso:
  uv run python scripts/limpar_video.py videos/<slug>            # só lista (não apaga nada)
  uv run python scripts/limpar_video.py videos/<slug> --apagar   # apaga de verdade
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

REVISAO = re.compile(r"^revisao-v(\d+)(.*)\.mp4$")
SUFIXOS_DA_ATUAL = {"", "-leve"}          # da versão mais nova, só a completa e a leve
DESCARTAVEIS = {"render-remotion.mp4", "preview.mp4", "edl.v1-auto.json"}
CAPA_MANTER = {"capa.png", "grade-3x4.png", "titulo.json", "capa.props.json"}
CAND_MANTER = {"contato.jpg", "scores.json"}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def capas_em_uso(video_dir: Path) -> set[str]:
    raiz = video_dir.resolve().parents[1]
    return {sha(c) for fila in ("05-render-pronto", "06-publicar")
            for c in (raiz / fila).glob(f"{video_dir.name}*/capa/*.png")}


def tamanho(p: Path) -> int:
    return p.stat().st_size if p.is_file() else 0


def humano(n: int) -> str:
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024 or u == "GB":
            return f"{n:.0f} {u}" if u == "B" else f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} GB"


def alvos(video_dir: Path) -> tuple[list[Path], int | None]:
    edicao, capa = video_dir / "edicao", video_dir / "capa"
    fora: list[Path] = []

    # --- revisões: fica só a mais nova (completa + leve) ---
    versoes: dict[int, list[tuple[str, Path]]] = {}
    for f in edicao.glob("revisao-v*.mp4"):
        m = REVISAO.match(f.name)
        if m:
            versoes.setdefault(int(m.group(1)), []).append((m.group(2), f))
    atual = max(versoes) if versoes else None
    for n, itens in versoes.items():
        for sufixo, f in itens:
            if n != atual or sufixo not in SUFIXOS_DA_ATUAL:
                fora.append(f)

    for nome in DESCARTAVEIS:
        if (edicao / nome).exists():
            fora.append(edicao / nome)

    # --- capa: só a escolhida — e as que estão num pacote/na fila (capa própria de cada variante A/B/L01C).
    # Apagá-las tirava-as do portão de imagem na reaprovação seguinte e travava a publicação das variantes (GAUNTLET).
    if capa.is_dir():
        em_uso = capas_em_uso(video_dir)
        for f in capa.iterdir():
            if f.is_file() and f.name not in CAPA_MANTER and not (f.suffix == ".png" and sha(f) in em_uso):
                fora.append(f)
        cands = capa / "candidatos"
        usado = ""
        status = video_dir / "status.json"
        if status.exists():
            usado = (json.loads(status.read_text(encoding="utf-8")).get("capa") or {}).get("frame", "")
        if cands.is_dir():
            for f in cands.iterdir():
                if f.is_file() and f.name not in CAND_MANTER and f.name != usado:
                    fora.append(f)
    return fora, atual


def main() -> None:
    ap = argparse.ArgumentParser(description="Deixa na pasta do vídeo só o que é preciso para o arquivo final")
    ap.add_argument("video_dir", type=Path)
    ap.add_argument("--apagar", action="store_true", help="apaga de verdade (sem isto, só lista)")
    a = ap.parse_args()

    video_dir = a.video_dir.resolve()
    if not (video_dir / "edicao").is_dir():
        raise SystemExit(f"{video_dir}: não parece a pasta de um vídeo (falta edicao/).")

    fora, atual = alvos(video_dir)
    if atual is not None:
        print(f"revisão atual: revisao-v{atual}.mp4 (+ -leve) — as outras saem")
    if not fora:
        print("nada a remover: a pasta já está limpa.")
        return

    total = sum(tamanho(f) for f in fora)
    for f in sorted(fora, key=tamanho, reverse=True):
        print(f"  {'APAGA' if a.apagar else 'apagaria'}  {humano(tamanho(f)):>9}  {f.relative_to(video_dir)}")
        if a.apagar:
            f.unlink()
    print(f"{'removidos' if a.apagar else 'removeria'}: {len(fora)} arquivos · {humano(total)}")
    if not a.apagar:
        print("(nada foi apagado — rode de novo com --apagar)")


if __name__ == "__main__":
    main()
