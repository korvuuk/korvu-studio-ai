"""Monta o pacote final de um vídeo em 05-render-pronto/<slug>/ (contrato: docs/contratos.md §9).

Uso: uv run python scripts/montar_pacote.py videos/<slug> [--capa capa-A.png] [--material nome.pdf] [--sem-material]

Requisitos:
- videos/<slug>/edicao/final.mp4            (render Remotion + loudnorm)
- videos/<slug>/capa/<capa escolhida>.png   (padrão: capa/capa.png, senão a única capa-*.png)
- videos/<slug>/edicao/legendas.srt
- videos/<slug>/qa/relatorio.md com a linha "RESULTADO: PASS"
- videos/<slug>/material/<arquivo>.pdf se o CTA for de palavra-chave (gerado pelo produtor-de-material)
- GAUNTLET (22/10, docs/gauntlet.md): portões pauta (se houver pesquisa), roteiro, imagem e corte APROVADOS e
  válidos em videos/<slug>/portoes.json. O pacote sai SELADO (`pacote.json.gauntlet`): o publicar.py recusa
  arquivo trocado depois do selo ou que os portões não viram.

MATERIAL: o pacote leva SÓ o PDF (decisão de 13/10: palavra-chave = sempre um PDF). dossie.md, fontes.json,
obra*.json/md, _fonte/ e afins ficam em videos/ — o publicar.py sobe o material para o R2 PÚBLICO, e estudo
ou cópia de obra nunca pode sair de casa (docs/contratos.md §1a).
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

import portoes

RAIZ = Path(__file__).resolve().parents[1]


def falhar(msg: str) -> int:
    print(f"ERRO: {msg}")
    return 1


def main() -> int:
    args = [a for a in sys.argv[1:]]
    if not args:
        print(__doc__)
        return 1
    vdir = (RAIZ / args[0]).resolve() if not Path(args[0]).is_absolute() else Path(args[0])
    slug = vdir.name
    roteiro = json.loads((vdir / "roteiro.json").read_text(encoding="utf-8"))
    edl = json.loads((vdir / "edicao" / "edl.json").read_text(encoding="utf-8"))

    final = vdir / "edicao" / "final.mp4"
    if not final.exists():
        return falhar(f"{final.relative_to(RAIZ)} não existe — rode /renderizar")

    problemas = portoes.exigir(vdir)
    if problemas:
        return falhar("portões GAUNTLET sem APROVADO válido — o pacote não sai assim:\n  - " + "\n  - ".join(problemas)
                      + f"\n  (sinais: uv run python scripts/portoes.py estado videos/{slug})")

    relatorio = vdir / "qa" / "relatorio.md"
    if not relatorio.exists() or not re.search(r"^RESULTADO:\s*PASS\b", relatorio.read_text(encoding="utf-8"), re.M):
        return falhar("qa/relatorio.md sem 'RESULTADO: PASS' — o revisor-de-video precisa aprovar")

    capas = sorted((vdir / "capa").glob("capa*.png"))
    escolhida = None
    if "--capa" in args:
        escolhida = vdir / "capa" / args[args.index("--capa") + 1]
    elif (vdir / "capa" / "capa.png").exists():
        escolhida = vdir / "capa" / "capa.png"
    elif len([c for c in capas if c.name.startswith("capa-")]) == 1:
        escolhida = [c for c in capas if c.name.startswith("capa-")][0]
    if not escolhida or not escolhida.exists():
        return falhar("capa não definida — passe --capa capa-X.png ou crie capa/capa.png")

    srt = vdir / "edicao" / "legendas.srt"
    if not srt.exists():
        return falhar("edicao/legendas.srt não existe")

    # Só PDFs da raiz de material/ contam como material; o resto da pasta é estudo e não sai de videos/.
    pdfs = sorted(p for p in (vdir / "material").glob("*.pdf") if p.is_file() and not p.name.startswith("."))
    com_palavra = roteiro.get("cta_tipo") == "palavra-material" or bool(roteiro.get("cta_palavra"))
    material = None
    if "--material" in args:
        material = vdir / "material" / args[args.index("--material") + 1]
        if material.suffix.lower() != ".pdf" or not material.is_file():
            return falhar(f"--material tem de ser um .pdf existente em videos/{slug}/material/ ({material.name})")
    elif com_palavra and "--sem-material" not in args:
        if not pdfs:
            return falhar(f"o CTA é de palavra-chave ({roteiro.get('cta_palavra')}) mas não há PDF em "
                          f"videos/{slug}/material/ — rode o produtor-de-material (scripts/gerar_material_pdf.py)")
        if len(pdfs) > 1:
            return falhar("há mais de um PDF em material/: " + ", ".join(p.name for p in pdfs)
                          + " — escolha com --material nome.pdf")
        material = pdfs[0]

    dest = RAIZ / "05-render-pronto" / slug
    for sub in ("video", "capa", "legendas", "material"):
        (dest / sub).mkdir(parents=True, exist_ok=True)

    shutil.copy2(final, dest / "video" / "video-final.mp4")
    variantes = []
    for v in sorted((vdir / "edicao").glob("final-L01*.mp4")):
        nome = v.name.replace("final-", "video-final-")
        shutil.copy2(v, dest / "video" / nome)
        variantes.append(f"video/{nome}")
    shutil.copy2(escolhida, dest / "capa" / "capa.png")
    for extra in capas:
        if extra != escolhida:
            shutil.copy2(extra, dest / "capa" / extra.name)
    grade = vdir / "capa" / "grade-3x4.png"
    if grade.exists():
        shutil.copy2(grade, dest / "capa" / grade.name)
    shutil.copy2(srt, dest / "legendas" / "legendas.srt")
    for velho in (dest / "material").iterdir():      # pacote refeito: tira material de uma versão anterior
        if velho.is_file() and (material is None or velho.name != material.name):
            velho.unlink()
            print(f"  (removido do pacote: material/{velho.name})")
    if material:
        shutil.copy2(material, dest / "material" / material.name)
    shutil.copy2(vdir / "roteiro.md", dest / "roteiro.md")
    shutil.copy2(relatorio, dest / "qa-relatorio.md")

    pacote = {
        "slug": slug,
        "criado_em": datetime.now().astimezone().isoformat(timespec="seconds"),
        "duracao": edl.get("duracao_saida"),
        "qa": "PASS",
        "arquivos": {
            "video": "video/video-final.mp4",
            "variantes": variantes,
            "capa": "capa/capa.png",
            "legendas": "legendas/legendas.srt",
            "material": f"material/{material.name}" if material else None,
            "roteiro": "roteiro.md",
            "qa": "qa-relatorio.md",
        },
        "cta_palavra": roteiro.get("cta_palavra"),
        "material_titulo": roteiro.get("material_titulo"),
        "tema": roteiro.get("tema"),
        "pilar": roteiro.get("pilar"),
    }
    try:
        pacote["gauntlet"] = portoes.selar(vdir, dest, pacote["arquivos"])
    except portoes.ErroPortao as e:
        return falhar(str(e))
    (dest / "pacote.json").write_text(json.dumps(pacote, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Pacote pronto: 05-render-pronto/{slug}/")
    for k, v in pacote["arquivos"].items():
        print(f"  {k:10} {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
