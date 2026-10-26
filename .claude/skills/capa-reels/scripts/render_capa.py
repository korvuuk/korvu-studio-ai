#!/usr/bin/env python3
"""Renderiza a capa do Reel (Remotion `Capa` 1080×1920) e a prévia da grade (`CapaGrade` 1080×1440).

Uso:
  uv run python .claude/skills/capa-reels/scripts/render_capa.py videos/<slug> --frame cand-03.jpg --variante A
      [--titulo-json caminho.json] [--posicao topo|base] [--cor-rabisco acento|#RRGGBB] [--com-contexto]

Variantes: A = texto embaixo, rabisco cinza · B = texto em cima, rabisco cinza
           C = texto embaixo, rabisco laranja · D = texto em cima, rabisco laranja
Saídas: videos/<slug>/capa/capa-<V>.png, capa/grade-3x4.png (+ capa-<V>.props.json)
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]
REMOTION = RAIZ / "remotion"
PUBLIC_CAPAS = REMOTION / "public" / "_render" / "_capas"

VARIANTES = {
    "A": {"posicao": "base", "corRabisco": None},
    "B": {"posicao": "topo", "corRabisco": None},
    "C": {"posicao": "base", "corRabisco": "acento"},
    "D": {"posicao": "topo", "corRabisco": "acento"},
}

# 2026-09-18 (Carlos): "o texto nunca pode ficar no meu rosto, nunca. Sempre tem que levar isso em
# consideração quem vai editar." Deixou de ser cuidado de quem edita: o rosto é detectado e a faixa
# do texto é escolhida sozinha na metade livre.
FAIXA_TEXTO = {"topo": (0.06, 0.42), "base": (0.58, 0.94)}   # fração da altura ocupada pelo título


def faixa_livre(frame: Path, pedida: str | None) -> tuple[str, str]:
    """-> (posicao, explicação). Escolhe a faixa do título que NÃO cai sobre o rosto."""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        import cv2                                              # noqa: PLC0415
        from frame_candidates import DetectorPele, criar_detector   # noqa: PLC0415
        img = cv2.imread(str(frame))
        if img is None:
            raise RuntimeError("não abriu o frame")
        cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        caixas = criar_detector().rostos(img, cinza)
        if not caixas:
            # ele grava de óculos escuros e o Haar procura olhos: cai para a heurística de pele
            caixas = DetectorPele().rostos(img, cinza)
    except Exception as e:                                       # detector indisponível: não adivinha
        return (pedida or "base"), f"sem detecção de rosto ({e}) — usando {pedida or 'base'}"
    if not caixas:
        return (pedida or "base"), "rosto não detectado — texto embaixo por precaução"
    h = img.shape[0]
    x, y, bw, bh = max(caixas, key=lambda c: c[2] * c[3])
    r0, r1 = y / h, (y + bh) / h
    folga = 0.03
    livres = [p for p, (a, b) in FAIXA_TEXTO.items() if b + folga <= r0 or a >= r1 + folga]
    if pedida and pedida in livres:
        return pedida, f"rosto em {r0:.0%}–{r1:.0%} da altura; {pedida} está livre"
    if livres:
        escolha = livres[0] if pedida is None else livres[0]
        aviso = "" if pedida is None else f" (a variante pedia '{pedida}', que cairia no rosto)"
        return escolha, f"rosto em {r0:.0%}–{r1:.0%} da altura -> texto em '{escolha}'{aviso}"
    # rosto ocupa as duas faixas: fica a que sobrepõe menos
    def sobrep(p):
        a, b = FAIXA_TEXTO[p]
        return max(0.0, min(b, r1) - max(a, r0))
    escolha = min(FAIXA_TEXTO, key=sobrep)
    return escolha, (f"[AVISO] o rosto ({r0:.0%}–{r1:.0%}) cobre as duas faixas — "
                     f"'{escolha}' é a que menos invade; escolha outro frame se der")


def ler_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def achar_titulo(video_dir: Path, arg: Path | None) -> dict:
    for p in [arg, video_dir / "capa" / "titulo.json", video_dir / "edicao" / "titulo.json"]:
        if p and p.exists():
            return ler_json(p)
    props = video_dir / "edicao" / "reel-props.json"
    if props.exists() and ler_json(props).get("titulo"):
        return ler_json(props)["titulo"]
    raise SystemExit("Sem título: passe --titulo-json, crie capa/titulo.json ou rode gerar_props.py antes.")


def still(comp: str, saida: Path, props_p: Path) -> None:
    npx = shutil.which("npx") or "npx"
    r = subprocess.run([npx, "remotion", "still", comp, str(saida), f"--props={props_p}",
                        "--image-format=png", "--overwrite", "--log=error"], cwd=REMOTION)
    if r.returncode != 0:
        raise SystemExit(f"Remotion falhou ao renderizar {comp}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Capa do Reel via Remotion")
    ap.add_argument("video_dir", type=Path)
    ap.add_argument("--frame", required=True, help="nome em capa/candidatos/ ou caminho de imagem")
    ap.add_argument("--variante", default="A", choices=sorted(VARIANTES))
    ap.add_argument("--titulo-json", type=Path)
    ap.add_argument("--posicao", choices=["topo", "base"])
    ap.add_argument("--cor-rabisco", help='"acento" (laranja da marca) ou cor CSS')
    ap.add_argument("--serifa", help="palavra do impacto em serifa itálica (estilo editorial da referência)")
    ap.add_argument("--escurecer", type=float, default=0.12)
    ap.add_argument("--com-contexto", action="store_true", help="inclui a linha de contexto (nível 1)")
    ap.add_argument("--tamanho", type=int, help="tamanho do título em px (padrão 150); menor = sobe menos no rosto")
    ap.add_argument("--subir-frame", type=int, default=0,
                    help="sobe a foto N px (close com a mão no queixo: o título deixa de cobrir o queixo)")
    a = ap.parse_args()

    video_dir = a.video_dir.resolve()
    slug = video_dir.name
    frame = Path(a.frame)
    if not frame.exists():
        frame = video_dir / "capa" / "candidatos" / a.frame
    if not frame.exists():
        raise SystemExit(f"Frame não encontrado: {a.frame}")

    destino = PUBLIC_CAPAS / slug
    destino.mkdir(parents=True, exist_ok=True)
    shutil.copy2(frame, destino / frame.name)

    titulo = achar_titulo(video_dir, a.titulo_json)
    var = dict(VARIANTES[a.variante])
    # o texto nunca entra no rosto: a faixa é escolhida pela detecção, não pela variante (2026-09-18)
    pos, porque = faixa_livre(frame, a.posicao or var["posicao"])
    if pos != var["posicao"]:
        print(f"[capa] posição trocada: {var['posicao']} -> {pos}")
    print(f"[capa] {porque}")
    var["posicao"] = pos
    if a.cor_rabisco:
        var["corRabisco"] = a.cor_rabisco
    props = {
        "frame": f"_render/_capas/{slug}/{frame.name}",
        "contexto": titulo.get("contexto") if a.com_contexto else None,
        "impacto": titulo["impacto"],
        "cinza": int(titulo.get("cinza", 0)),
        "rabisco": titulo.get("rabisco"),
        "serifa": a.serifa or titulo.get("serifa"),
        "selecao": titulo.get("selecao"),
        "escurecer": a.escurecer,
        "tamanhoTitulo": a.tamanho,
        "deslocarFrameY": -abs(a.subir_frame),
        **var,
    }

    capa_dir = video_dir / "capa"
    capa_dir.mkdir(exist_ok=True)
    props_p = capa_dir / f"capa-{a.variante}.props.json"
    props_p.write_text(json.dumps(props, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    capa = capa_dir / f"capa-{a.variante}.png"
    grade = capa_dir / "grade-3x4.png"
    still("Capa", capa, props_p)
    still("CapaGrade", grade, props_p)
    # 2026-10-02: cada variante tem a SUA grade (antes todas escreviam grade-3x4.png e só a última sobrava) e
    # um mosaico lado a lado — é por ele que o Carlos escolhe a headline. grade-3x4.png = a última renderizada.
    grade_v = capa_dir / f"grade-{a.variante}.png"
    shutil.copy2(grade, grade_v)
    mosaico = capa_dir / "grade-comparacao.jpg"
    grades = sorted(capa_dir.glob("grade-[A-Z].png"))
    if len(grades) > 1:
        import os
        ff = os.environ.get("FFMPEG_BIN") or shutil.which("ffmpeg") or "ffmpeg"
        ins = sum((["-i", str(g)] for g in grades), [])
        fc = "".join(f"[{k}]scale=480:-1[g{k}];" for k in range(len(grades))) + \
             "".join(f"[g{k}]" for k in range(len(grades))) + f"hstack={len(grades)}"
        subprocess.run([ff, "-v", "error", "-y", *ins, "-filter_complex", fc, str(mosaico)], check=False)
    print(f"capa: {capa}\ngrade: {grade_v}\nprops: {props_p}" + (f"\ncomparação: {mosaico}" if len(grades) > 1 else ""))


if __name__ == "__main__":
    main()
