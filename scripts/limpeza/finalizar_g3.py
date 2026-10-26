"""Depois da cópia conferida: escreve brutos/principal/ARQUIVADO.json (docs/contratos.md §0) e apaga os originais do Mac.
Recusa se a conferência não for 100 %, se a cópia no HD mudou/sumiu ou se o original mudou desde a cópia."""
import datetime as dt, json, sys
from pathlib import Path

R = Path(sys.argv[1]).resolve(); COPIA = json.loads(Path(sys.argv[2]).read_text()); APAGAR = "--apagar" in sys.argv
VOL = {"volume": "KORVU V01", "volume_uuid": "D4CCA486-F81F-339B-8C2C-A6F8D6DC8FDB", "formato": "exFAT"}
iso = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).isoformat(timespec="seconds")
assert COPIA.get("tudo_confere") is True, "a conferência não fechou — não apago nada"
por_slug = {}
for a in COPIA["arquivos"]:
    assert a["confere"] and a["sha256_origem"] == a["sha256_destino"] and a["bytes"] == a["bytes_destino"], a["nome"]
    por_slug.setdefault(a["slug"], []).append(a)
for slug, itens in por_slug.items():
    pr = R / "videos" / slug / "brutos" / "principal"
    no_disco = sorted(f for f in pr.iterdir() if f.is_file() and not f.name.startswith(".") and f.name != "ARQUIVADO.json")
    assert {f.name for f in no_disco} == {a["nome"] for a in itens}, f"{slug}: lista no disco ≠ lista copiada"
    arquivos = []
    for a in sorted(itens, key=lambda x: x["nome"]):
        src, dst = pr / a["nome"], Path(a["destino"])
        st = src.stat()
        assert st.st_size == a["bytes"] and abs(st.st_mtime - a["mtime"]) < 1, f"{a['nome']} mudou desde a cópia"
        assert dst.is_file() and dst.stat().st_size == a["bytes"], f"cópia sumiu/mudou no HD: {dst}"
        arquivos.append({"nome": a["nome"], "bytes": a["bytes"], "sha256": a["sha256_origem"],
                         "mtime": iso(st.st_mtime), "ctime": iso(st.st_ctime)})
    man = {"arquivado_em": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
           "motivo": "vídeo publicado; original 4K fora do Mac (limpeza 23/10, aprovada pelo Carlos: copiar para HD externo antes)",
           "destino": {**VOL, "pasta": f"CONTENT AI - originais 4K/{slug}/brutos/principal"},
           "conferencia": "sha256 da origem (lido na cópia) = sha256 relido do HD sem cache, arquivo por arquivo",
           "intermediarios": "edicao/fontes/ (1440×2560 10-bit 4:2:2 V-Log, duração igual à do original) + edicao/audio48k/",
           "arquivos": arquivos}
    total = sum(a["bytes"] for a in arquivos)
    print(f"{slug}: {len(arquivos)} arquivos · {total/2**30:.2f} GiB {'→ apagando' if APAGAR else '(ensaio)'}")
    if APAGAR:
        (pr / "ARQUIVADO.json").write_text(json.dumps(man, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        for a in arquivos:
            (pr / a["nome"]).unlink()
        ds = pr / ".DS_Store"
        if ds.is_file(): ds.unlink()
