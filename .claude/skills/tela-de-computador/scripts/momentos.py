"""Mapeia os MOMENTOS de uma gravação de tela de computador (ChatGPT no Mac, ou outro app)
-> <saida>/momentos.json + folhas de contato para o editor olhar.

uso: uv run python .claude/skills/tela-de-computador/scripts/momentos.py <gravacao.mov> [--saida DIR]
         [--fps 2] [--caixa 0.78]  [--limiar-caixa 1.5] [--limiar-tela 6]

O que faz (sem OCR, só diferença entre quadros):
- extrai 1 quadro a cada 1/fps s, reduzido (largura 320);
- mede a mudança em duas regiões: a CAIXA (faixa de baixo, onde se anexa e digita: fração `--caixa` da altura
  para baixo) e a TELA (o resto, onde o resultado aparece);
- marca eventos: `caixa` (mexeu na caixa: anexou/digitou/enviou), `tela` (mudança grande em cima: resultado
  apareceu / rolou), `parado` (trechos ≥ 8 s sem nada mudar = geração ou espera — é o que o editor corta);
- escreve `momentos.json` {"video", "duracao", "fps", "eventos": [{"t", "tipo", "score"}], "parados": [{"inicio",
  "fim"}]} e `momentos-contato.jpg` (um quadro por evento, com o tempo escrito) + `momentos-caixa.jpg` (só a caixa,
  ampliada, nos eventos `caixa` — para ler o que foi digitado).

O editor (ou o agente) olha as folhas, confirma que comando foi digitado em cada evento `caixa` e escreve o
`tela.json` do recortar.py. Nada aqui decide sozinho o que vai para o vídeo.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

FFMPEG = os.environ.get("FFMPEG_BIN", "ffmpeg")
FFPROBE = os.environ.get("FFPROBE_BIN", "ffprobe")


def duracao(video: Path) -> float:
    out = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
                         capture_output=True, text=True, check=True).stdout.strip()
    return float(out)


def extrair(video: Path, fps: float, largura: int, destino: Path) -> list[Path]:
    destino.mkdir(parents=True, exist_ok=True)
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", str(video),
                    "-vf", f"fps={fps},scale={largura}:-1", str(destino / "q_%05d.png")], check=True)
    return sorted(destino.glob("q_*.png"))


def carregar(p: Path):
    from PIL import Image
    import numpy as np
    return np.asarray(Image.open(p).convert("L"), dtype="float32")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--saida", default=None, help="pasta de saída (padrão: ao lado do vídeo, pasta 'momentos')")
    ap.add_argument("--fps", type=float, default=2.0)
    ap.add_argument("--caixa", type=float, default=0.78, help="a caixa de digitação começa nesta fração da altura")
    ap.add_argument("--limiar-caixa", type=float, default=1.5, help="diferença média (0–255) para contar como mexida na caixa")
    ap.add_argument("--limiar-tela", type=float, default=6.0, help="diferença média para contar como mudança na tela")
    ap.add_argument("--parado-min", type=float, default=8.0, help="segundos sem mudança para virar trecho 'parado'")
    args = ap.parse_args()

    video = Path(args.video).resolve()
    saida = Path(args.saida).resolve() if args.saida else video.parent / "momentos"
    saida.mkdir(parents=True, exist_ok=True)
    dur = duracao(video)

    import numpy as np
    from PIL import Image, ImageDraw

    with tempfile.TemporaryDirectory() as td:
        quadros = extrair(video, args.fps, 320, Path(td))
        if len(quadros) < 2:
            sys.exit("[momentos] vídeo curto demais")
        prev = carregar(quadros[0])
        h = prev.shape[0]
        yc = int(h * args.caixa)
        eventos, quieto_desde, parados = [], 0.0, []
        for i, q in enumerate(quadros[1:], start=1):
            cur = carregar(q)
            t = i / args.fps
            d = np.abs(cur - prev)
            d_caixa = float(d[yc:, :].mean())
            d_tela = float(d[:yc, :].mean())
            tipo = None
            if d_tela >= args.limiar_tela:
                tipo = "tela"
            elif d_caixa >= args.limiar_caixa:
                tipo = "caixa"
            if tipo:
                if t - quieto_desde >= args.parado_min:
                    parados.append({"inicio": round(quieto_desde, 2), "fim": round(t, 2)})
                quieto_desde = t
                # junta eventos do mesmo tipo a menos de 1 s
                if eventos and eventos[-1]["tipo"] == tipo and t - eventos[-1]["t"] <= 1.0:
                    eventos[-1]["fim"] = round(t, 2)
                    eventos[-1]["score"] = max(eventos[-1]["score"], round(max(d_caixa, d_tela), 2))
                else:
                    eventos.append({"t": round(t, 2), "fim": round(t, 2), "tipo": tipo,
                                    "score": round(max(d_caixa, d_tela), 2), "quadro": q.name})
            prev = cur
        if dur - quieto_desde >= args.parado_min:
            parados.append({"inicio": round(quieto_desde, 2), "fim": round(dur, 2)})

        # folhas de contato (quadro inteiro nos eventos; caixa ampliada nos eventos 'caixa')
        def folha(items, nome, recorte_caixa: bool):
            if not items:
                return
            tiles = []
            for e in items:
                im = Image.open(Path(td) / e["quadro"]).convert("RGB")
                if recorte_caixa:
                    im = im.crop((0, yc, im.width, im.height)).resize((im.width * 2, (im.height - yc) * 2))
                dr = ImageDraw.Draw(im)
                dr.rectangle((0, 0, 150, 18), fill="white")
                dr.text((3, 3), f"{e['t']:.1f}s {e['tipo']}", fill="red")
                tiles.append(im)
            w, h2 = tiles[0].size
            cols = 6
            rows = (len(tiles) + cols - 1) // cols
            sheet = Image.new("RGB", (cols * (w + 4), rows * (h2 + 4)), "black")
            for k, im in enumerate(tiles):
                sheet.paste(im.resize((w, h2)), ((k % cols) * (w + 4), (k // cols) * (h2 + 4)))
            sheet.save(saida / nome, quality=85)

        folha(eventos, "momentos-contato.jpg", False)
        folha([e for e in eventos if e["tipo"] == "caixa"], "momentos-caixa.jpg", True)

    res = {"video": str(video), "duracao": round(dur, 2), "fps": args.fps, "caixa_fracao": args.caixa,
           "eventos": [{k: v for k, v in e.items() if k != "quadro"} for e in eventos], "parados": parados}
    (saida / "momentos.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[momentos] {len(eventos)} eventos, {len(parados)} trechos parados (≥ {args.parado_min:.0f} s) em {dur:.0f} s")
    for e in eventos:
        print(f"  {e['t']:7.1f}s  {e['tipo']:5s}  score {e['score']}")
    print(f"[momentos] -> {saida / 'momentos.json'}, momentos-contato.jpg, momentos-caixa.jpg")


if __name__ == "__main__":
    main()
