#!/usr/bin/env python3
"""Procura VÍDEO que a gente pode mesmo usar — o que tem licença legível — e baixa só esse.

Regra do Carlos (2026-09-17): cena extra em vídeo dá mais credibilidade que foto. Mas "público" não é
"liberado": baixar de YouTube/Instagram/TikTok de terceiros viola os termos dessas plataformas, o vídeo tem
dono e o Rights Manager da Meta silencia ou derruba o Reel. Então este script **só** aceita fonte que declara
a licença de forma legível por máquina:

  archive.org        API de metadados devolve `licenseurl` / `rights`
  Wikimedia Commons  API devolve licença e autor (CC BY, CC BY-SA, CC0, domínio público)
  URL direta         .mp4/.webm de newsroom/press kit oficial — você confirma os termos e passa --licenca

Uso:
  uv run python scripts/buscar_video.py buscar "jacob coxon"                    # procura nas duas fontes
  uv run python scripts/buscar_video.py baixar <url> videos/<slug>/brutos/extras/E01-nome.mp4 [--licenca "..."]

Saída: o arquivo + uma linha em videos/<slug>/material/fontes.json com licença, autor, link e data.
"""
from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

UA = {"User-Agent": "KorvuContentAI/1.0 (pesquisa de material com licenca)"}
# Casar com o texto REAL que as APIs devolvem. O Commons manda "Public domain", "CC BY-SA 4.0", "CC0";
# o archive.org manda URL ("creativecommons.org/licenses/by/4.0"). Em 2026-09-17 a lista só tinha
# "publicdomain" (sem espaço) e o script rotulou vídeo de domínio público como "sem licença livre" —
# ou seja, descartava justamente o material que serve. Comparar sempre em minúsculas, com espaço e hífen.
LIVRES = ("creativecommons.org", "public domain", "publicdomain", "domínio público", "cc0", "cc-by",
          "cc by", "by-sa", "by sa", "pd-", "no known copyright")


def _licenca_livre(txt: str) -> bool:
    t = (txt or "").lower()
    return any(s in t for s in LIVRES)


def _json(url: str) -> dict:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def buscar_archive(termo: str, n: int = 8) -> list[dict]:
    q = urllib.parse.quote(f'"{termo}" AND mediatype:(movies)')
    url = (f"https://archive.org/advancedsearch.php?q={q}"
           "&fl%5B%5D=identifier&fl%5B%5D=title&fl%5B%5D=licenseurl&fl%5B%5D=year"
           f"&rows={n}&page=1&output=json")
    try:
        docs = _json(url).get("response", {}).get("docs", [])
    except Exception as e:                      # noqa: BLE001
        # Nesta máquina o archive.org recusa a conexão por TLS (conferido em 2026-09-17: curl também falha,
        # enquanto o Commons responde 200). Isso é bloqueio de rede, NÃO ausência de material:
        # "não achei" aqui nunca pode ser lido como "não existe".
        print(f"  archive.org NÃO RESPONDEU a partir desta máquina ({e.__class__.__name__}): a busca ficou "
              "incompleta — não conclua que não há vídeo livre; tente pelo navegador.")
        return []
    out = []
    for d in docs:
        lic = d.get("licenseurl") or ""
        out.append({"fonte": "archive.org", "titulo": d.get("title"),
                    "url": f"https://archive.org/details/{d['identifier']}",
                    "licenca": lic or "NÃO DECLARADA",
                    "permitido": bool(lic) and _licenca_livre(lic)})
    return out


def buscar_commons(termo: str, n: int = 8) -> list[dict]:
    # gsrnamespace=6 (Arquivo) é obrigatório: sem ele a busca cai no namespace de artigos e devolve
    # ZERO até para "Barack Obama" — foi o que me enganou em 2026-09-17.
    q = urllib.parse.quote(f"{termo} filetype:video")
    url = ("https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search"
           f"&gsrsearch={q}&gsrlimit={n}&gsrnamespace=6&prop=imageinfo&iiprop=url|extmetadata")
    try:
        paginas = _json(url).get("query", {}).get("pages", {})
    except Exception as e:                      # noqa: BLE001
        print(f"  Commons indisponível: {e}")
        return []
    out = []
    for p in paginas.values():
        info = (p.get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata", {})
        lic = (meta.get("LicenseShortName", {}) or {}).get("value", "") or "NÃO DECLARADA"
        autor = (meta.get("Artist", {}) or {}).get("value", "")
        out.append({"fonte": "Wikimedia Commons", "titulo": p.get("title"),
                    "url": info.get("descriptionurl") or info.get("url"),
                    "arquivo": info.get("url"), "licenca": lic, "autor": autor,
                    "permitido": _licenca_livre(lic)})
    return out


def baixar(url: str, destino: Path, licenca: str | None) -> int:
    dominio = urllib.parse.urlparse(url).netloc.lower()
    proibidos = ("youtube.com", "youtu.be", "instagram.com", "tiktok.com", "facebook.com", "x.com", "twitter.com")
    if any(d in dominio for d in proibidos):
        print(f"RECUSADO: {dominio} não permite download por fora dos meios da própria plataforma, e o vídeo tem\n"
              "dono. Caminhos válidos: licença CC BY confirmada na página + cópia liberada pelo autor, press kit\n"
              "oficial, agência licenciada, ou autorização por escrito do titular.")
        return 1
    if not licenca and "archive.org" not in dominio and "wikimedia" not in dominio:
        print("RECUSADO: sem licença declarada. Se for press kit/newsroom oficial, confirme os termos na página\n"
              "e repita com --licenca \"...\" (o texto vai para o fontes.json e para o crédito).")
        return 1
    destino.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as r, open(destino, "wb") as f:
        f.write(r.read())
    mb = destino.stat().st_size / 1e6
    print(f"Baixado: {destino} ({mb:.1f} MB)\nLicença: {licenca or 'ver página da fonte'}")
    print("Anote no material/fontes.json: licença, autor, link e crédito — sem crédito o extra não entra.")
    return 0


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1
    if args[0] == "buscar" and len(args) > 1:
        termo = args[1]
        achados = buscar_archive(termo) + buscar_commons(termo)
        if not achados:
            print("Nada com licença legível. Alternativas: press kit oficial, agência licenciada,\n"
                  "ou pedir autorização por escrito ao titular. Enquanto isso, print de página pública.")
            return 0
        for a in sorted(achados, key=lambda x: not x["permitido"]):
            marca = "USÁVEL " if a["permitido"] else "sem licença livre"
            print(f"[{marca}] {a['fonte']}: {a.get('titulo')}\n   {a['url']}\n   licença: {a['licenca']}")
        return 0
    if args[0] == "baixar" and len(args) > 2:
        lic = args[args.index("--licenca") + 1] if "--licenca" in args else None
        return baixar(args[1], Path(args[2]).resolve(), lic)
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
