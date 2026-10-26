#!/usr/bin/env python3
"""Música de fundo dos Reels — gerada sob medida pela ElevenLabs Music e misturada sob a voz do Carlos.

Decisão do Carlos (2026-10-01): a automação não pode depender dele buscar, baixar e pôr música na pasta.
A Meta Sound Collection não tem API (só abre logado no Facebook), por isso a fonte automática é a
ElevenLabs Music: uma faixa ORIGINAL por vídeo, sem gravação pré-existente para o Rights Manager casar,
com uso comercial liberado nos planos pagos. Requer ELEVENLABS_API_KEY no ambiente/.env (nunca imprimir).

Como fica no disco:
  videos/<slug>/musica/opcao-N.mp3   as opções geradas
  videos/<slug>/musica/musica.json   prompt, modelo, duração, data e qual foi a escolhida

Uso:
  uv run python scripts/gerar_musica.py gerar <slug> --clima "inspirador, curioso, tecnológico" [--n 2]
                                                    [--dur 65] [--modelo music_v2_5]
  uv run python scripts/gerar_musica.py mixar <slug> --opcao 1 [--entrada edicao/final-A.mp4]
                                                    [--saida edicao/final-musica.mp4] [--db -22]
  uv run python scripts/gerar_musica.py escolher <slug> <N>
  uv run python scripts/gerar_musica.py estado <slug>

A mixagem é o audio.py (audio-polish): música com volume fixo (padrão −22 dB), ducking automático pela voz
(sidechain), fade-out de 1,5 s e o master inteiro a −14 LUFS / −1,5 dBTP. O vídeo é copiado sem reencode.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
AUDIO_PY = RAIZ / ".claude/skills/audio-polish/scripts/audio.py"
API = "https://api.elevenlabs.io/v1/music"

# Regras fixas de toda trilha da Korvu: é CAMA para a voz, não música para ouvir. Sem voz cantada (briga
# com a fala e com a legenda), sem solo agudo na região da voz, sem queda/drop que puxe a atenção.
BASE = ("Instrumental background music bed for a spoken-word social media video (Instagram Reel) about "
        "artificial intelligence. No vocals, no choir, no spoken words. Leave room for a male voice in the "
        "200 Hz-4 kHz range: soft, sparse mid-range, no prominent lead melody, no sudden drops, builds or "
        "loud hits. Steady energy from start to end, clean ending. Mood: ")


def env() -> None:
    try:
        from dotenv import load_dotenv
        if (RAIZ / ".env").exists():          # nunca imprimir o .env
            load_dotenv(RAIZ / ".env", override=False)
    except ImportError:
        pass


def pasta(slug: str) -> Path:
    vd = RAIZ / "videos" / slug
    if not vd.is_dir():
        raise SystemExit(f"[erro] vídeo não existe: videos/{slug}")
    p = vd / "musica"
    p.mkdir(exist_ok=True)
    return p


def ler(slug: str) -> dict:
    p = pasta(slug) / "musica.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {"opcoes": [], "escolhida": None}


def escrever(slug: str, d: dict) -> None:
    (pasta(slug) / "musica.json").write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def duracao(arq: Path) -> float:
    ffprobe = os.environ.get("FFPROBE_BIN") or "ffprobe"
    r = subprocess.run([ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(arq)],
                       capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def video_base(slug: str) -> Path | None:
    e = RAIZ / "videos" / slug / "edicao"
    for nome in ("render-remotion.mp4", "final.mp4", "corte.mp4"):
        if (e / nome).is_file():
            return e / nome
    return None


def cmd_gerar(a: argparse.Namespace) -> int:
    env()
    chave = os.environ.get("ELEVENLABS_API_KEY")
    if not chave:
        raise SystemExit("[erro] ELEVENLABS_API_KEY não está definida. O Carlos põe a chave no .env "
                         "(ELEVENLABS_API_KEY=...) — não leia nem edite o .env por ele.")
    dur = a.dur
    if not dur:
        base = video_base(a.slug)
        if not base:
            raise SystemExit("[erro] sem vídeo em edicao/ para medir a duração — passe --dur <segundos>.")
        dur = duracao(base) + 2.0      # sobra: o audio.py corta no fim do vídeo e faz o fade-out
    d = ler(a.slug)
    prompt = BASE + a.clima
    for _ in range(a.n):
        n = len(d["opcoes"]) + 1
        destino = pasta(a.slug) / f"opcao-{n}.mp3"
        corpo = json.dumps({"prompt": prompt, "music_length_ms": int(round(dur * 1000)),
                            "model_id": a.modelo, "force_instrumental": True}).encode()
        req = urllib.request.Request(f"{API}?output_format=mp3_44100_192", data=corpo, method="POST",
                                     headers={"xi-api-key": chave, "Content-Type": "application/json"})
        print(f"[musica] gerando opção {n} ({dur:.0f} s, {a.modelo}) — {a.clima}")
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                destino.write_bytes(r.read())
        except urllib.error.HTTPError as e:
            detalhe = e.read()[:400].decode(errors="replace")
            dica = (" — a chave não tem acesso à música (plano gratuito?). O uso comercial exige plano pago."
                    if e.code in (401, 402, 403) else "")
            raise SystemExit(f"[erro] ElevenLabs respondeu {e.code}{dica}\n       {detalhe}")
        real = duracao(destino)
        if real < 3:
            destino.unlink(missing_ok=True)
            raise SystemExit("[erro] o arquivo devolvido não é áudio válido.")
        d["opcoes"].append({"n": n, "arquivo": str(destino.relative_to(RAIZ)), "clima": a.clima, "prompt": prompt,
                            "modelo": a.modelo, "duracao_s": round(real, 2),
                            "gerada_em": datetime.now().isoformat(timespec="seconds"),
                            "licenca": "ElevenLabs Music — faixa original, uso comercial pelo plano pago da conta"})
        escrever(a.slug, d)
        print(f"[musica] pronto: {destino.relative_to(RAIZ)} ({real:.1f} s)")
    return 0


def cmd_mixar(a: argparse.Namespace) -> int:
    d = ler(a.slug)
    op = next((o for o in d["opcoes"] if o["n"] == a.opcao), None)
    if not op:
        raise SystemExit(f"[erro] opção {a.opcao} não existe — veja 'estado'.")
    vd = RAIZ / "videos" / a.slug
    ent = vd / a.entrada if a.entrada else video_base(a.slug)
    if not ent or not ent.is_file():
        raise SystemExit("[erro] vídeo de entrada não encontrado (use --entrada edicao/<arquivo>.mp4).")
    sai = vd / a.saida if a.saida else vd / "edicao" / f"final-musica-{a.opcao}.mp4"
    cmd = ["uv", "run", "python", str(AUDIO_PY), str(ent), str(sai), "--musica", str(RAIZ / op["arquivo"]),
           "--musica-db", str(a.db)]
    print("[musica] " + " ".join(Path(c).name if "/" in c else c for c in cmd[3:]))
    r = subprocess.run(cmd, cwd=RAIZ)
    if r.returncode != 0:
        raise SystemExit("[erro] o audio.py falhou — nada foi gerado.")
    print(f"[musica] pronto: {sai.relative_to(RAIZ)}")
    return 0


def cmd_escolher(a: argparse.Namespace) -> int:
    d = ler(a.slug)
    if not any(o["n"] == a.n for o in d["opcoes"]):
        raise SystemExit(f"[erro] opção {a.n} não existe.")
    d["escolhida"] = a.n
    escrever(a.slug, d)
    op = next(o for o in d["opcoes"] if o["n"] == a.n)
    print(f"[musica] escolhida: opção {a.n} — no /renderizar use --musica {op['arquivo']}")
    return 0


def cmd_estado(a: argparse.Namespace) -> int:
    d = ler(a.slug)
    if not d["opcoes"]:
        print("Nenhuma música gerada ainda.")
    for o in d["opcoes"]:
        marca = "  <- escolhida" if d.get("escolhida") == o["n"] else ""
        print(f"opção {o['n']}: {o['arquivo']} · {o['duracao_s']} s · {o['clima']}{marca}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gerar"); g.add_argument("slug"); g.add_argument("--clima", required=True)
    g.add_argument("--n", type=int, default=2); g.add_argument("--dur", type=float)
    g.add_argument("--modelo", default="music_v2_5", choices=["music_v1", "music_v2", "music_v2_5"])
    g.set_defaults(func=cmd_gerar)
    m = sub.add_parser("mixar"); m.add_argument("slug"); m.add_argument("--opcao", type=int, required=True)
    m.add_argument("--entrada"); m.add_argument("--saida"); m.add_argument("--db", type=float, default=-22)
    m.set_defaults(func=cmd_mixar)
    e = sub.add_parser("escolher"); e.add_argument("slug"); e.add_argument("n", type=int)
    e.set_defaults(func=cmd_escolher)
    s = sub.add_parser("estado"); s.add_argument("slug"); s.set_defaults(func=cmd_estado)
    a = ap.parse_args()
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
