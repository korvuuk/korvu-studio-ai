"""Calibração de voz com gravação REAL: compara o que o Carlos DISSE (edicao/transcricao.json, só locutor carlos)
com o que o roteiro pedia (roteiro.json), linha a linha, e mede o ritmo nos takes que a EDL escolheu.

Uso: uv run python .claude/skills/roteiro-reels/scripts/comparar_fala.py videos/<slug> > 02-calibracao/analises/<data>-<slug>-fala.md
Precisa de roteiro.json + edicao/transcricao.json + edicao/alinhamento.json (edl.json opcional, para o wps no corte).
Só lê. Não escreve nada na pasta do vídeo. Resultado alimenta 00-marca/voz-carlos.md (ver /calibrar-voz).
"""
from __future__ import annotations

import difflib
import json
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

PAUSA_INTERNA = 0.35  # gap acima disto conta como pausa (mesmo critério do voice_stats.py)
MULETAS = {"é", "eh", "ã", "ah", "hum", "hm", "hã", "tipo", "né", "então", "assim", "bom", "enfim", "sabe", "aí", "hein", "tá", "ou", "seja"}


def norm(t: str) -> str:
    t = t.lower().strip()
    t = re.sub(r"[^\wà-ÿ]+", "", t)
    return t


def main(pasta: str) -> int:
    p = Path(pasta)
    rot = json.loads((p / "roteiro.json").read_text())
    tr = json.loads((p / "edicao" / "transcricao.json").read_text())
    al = json.loads((p / "edicao" / "alinhamento.json").read_text())
    edl_p = p / "edicao" / "edl.json"
    edl = json.loads(edl_p.read_text()) if edl_p.exists() else None

    pal = tr["palavras"]
    carlos = [w for w in pal if w.get("locutor", "carlos") == "carlos"]
    linhas_rot = {l["id"]: l for l in rot["linhas"]}
    escolhido_edl = {}
    if edl:
        for s in edl["segmentos"]:
            escolhido_edl[s["linha"]] = s

    out = []
    out.append(f"# Análise de fala — {rot['slug']} (roteiro v{rot['versao']})\n")
    out.append(f"Palavras do Carlos na transcrição: {len(carlos)} de {len(pal)} (IA: {sum(1 for w in pal if w.get('locutor')=='ia')}, incertas: {sum(1 for w in pal if w.get('locutor') is None)})\n")

    # ---------- 1. linha a linha ----------
    out.append("\n## 1. Linha a linha — roteiro × takes do Carlos\n")
    stats_wps = []  # (linha, take, palavras, dur_edl, dur_take, wps_edl, wps_artic)
    subst = Counter()
    insercoes = Counter()
    delecoes = Counter()
    aberturas = Counter()
    diffs_por_linha = []
    for la in al["linhas"]:
        lid = la["id"]
        lr = linhas_rot.get(lid)
        if not lr:
            continue
        rot_toks = [norm(x) for x in lr["fala"].split()]
        rot_toks = [x for x in rot_toks if x]
        out.append(f"\n### {lid} [{la['status']}] escolhido: {la.get('escolhido')} — {la.get('motivo','')}")
        out.append(f"ROTEIRO: {lr['fala']}")
        seg = escolhido_edl.get(lid)
        for t in la.get("takes", []):
            marca = "★" if t["take_id"] == la.get("escolhido") else " "
            dur = t["fim"] - t["inicio"]
            ws = [w for w in pal[t["i_ini"]:t["i_fim"] + 1] if w.get("locutor", "carlos") == "carlos"]
            n = len(ws)
            # articulação: tempo das palavras + gaps curtos
            gaps = [b["inicio"] - a["fim"] for a, b in zip(ws, ws[1:])]
            fala = sum(w["fim"] - w["inicio"] for w in ws) + sum(g for g in gaps if 0 <= g <= PAUSA_INTERNA)
            pausas = [round(g, 2) for g in gaps if g > PAUSA_INTERNA]
            wps_take = n / dur if dur else 0
            wps_art = n / fala if fala else 0
            linha_txt = f"  {marca} {t['take_id']} sim={t['sim']:.2f} cob={t.get('cobertura',0):.2f} flags={t.get('flags')} dur={dur:.1f}s n={n} wps={wps_take:.2f} artic={wps_art:.2f} pausas>{PAUSA_INTERNA}s={pausas}"
            out.append(linha_txt)
            out.append(f"      DITO: {t['texto']}")
            if marca == "★":
                dito_toks = [norm(w["texto"]) for w in ws]
                dito_toks = [x for x in dito_toks if x]
                sm = difflib.SequenceMatcher(a=rot_toks, b=dito_toks, autojunk=False)
                ops = []
                for tag, i1, i2, j1, j2 in sm.get_opcodes():
                    if tag == "equal":
                        continue
                    a_ = " ".join(rot_toks[i1:i2])
                    b_ = " ".join(dito_toks[j1:j2])
                    ops.append(f"{tag}: «{a_}» → «{b_}»")
                    if tag == "replace":
                        subst[(a_, b_)] += 1
                    elif tag == "insert":
                        insercoes[b_] += 1
                    elif tag == "delete":
                        delecoes[a_] += 1
                if ops:
                    out.append("      DIFF: " + " | ".join(ops))
                    diffs_por_linha.append((lid, lr["fala"], t["texto"], ops))
                if dito_toks:
                    aberturas[dito_toks[0]] += 1
                if seg:
                    dur_edl = (seg["out"] - seg["in"]) - sum(b - a for a, b in seg.get("cortes_internos", []))
                    stats_wps.append((lid, t["take_id"], n, dur_edl, dur, n / dur_edl if dur_edl else 0, wps_art))
                else:
                    stats_wps.append((lid, t["take_id"], n, None, dur, None, wps_art))
        if not la.get("takes"):
            out.append("  (sem take do Carlos)")

    # ---------- 2. ritmo ----------
    out.append("\n## 2. Ritmo nos takes escolhidos\n")
    out.append("| linha | take | palavras | dur. take (s) | dur. na EDL (s) | wps EDL | wps articulação |")
    out.append("|---|---|---|---|---|---|---|")
    for lid, tk, n, de, dt, we, wa in stats_wps:
        out.append(f"| {lid} | {tk} | {n} | {dt:.2f} | {de if de is None else round(de,2)} | {'' if we is None else round(we,2)} | {wa:.2f} |")
    tot_n = sum(s[2] for s in stats_wps)
    tot_dt = sum(s[4] for s in stats_wps)
    tot_de = sum(s[3] for s in stats_wps if s[3])
    wps_edl = [s[5] for s in stats_wps if s[5]]
    wps_art = [s[6] for s in stats_wps if s[6]]
    out.append(f"\nTotal: {tot_n} palavras ditas nos takes escolhidos · {tot_dt:.1f} s de take · {tot_de:.1f} s na EDL")
    if tot_de:
        out.append(f"**wps global na EDL (palavras ditas / tempo no corte): {tot_n/tot_de:.2f}**")
    out.append(f"wps global nos takes (com pausas internas): {tot_n/tot_dt:.2f}")
    if wps_edl:
        out.append(f"wps EDL por linha: mediana {statistics.median(wps_edl):.2f}, mín {min(wps_edl):.2f}, máx {max(wps_edl):.2f}")
    if wps_art:
        out.append(f"wps articulação por linha: mediana {statistics.median(wps_art):.2f}, mín {min(wps_art):.2f}, máx {max(wps_art):.2f}")
    if edl:
        out.append(f"Duração de saída da EDL: {edl.get('duracao_saida')} s · palavras do roteiro nas legendas: {len(edl.get('palavras_saida', []))} → {len(edl.get('palavras_saida', []))/edl['duracao_saida']:.2f} palavras de ROTEIRO por segundo de vídeo")

    # ---------- 3. trocas ----------
    out.append("\n## 3. Trocas sistemáticas (takes escolhidos)\n")
    out.append("### Substituições (roteiro → dito)")
    for (a_, b_), n in subst.most_common():
        out.append(f"- «{a_}» → «{b_}» ×{n}")
    out.append("\n### Inserções (dito a mais)")
    for b_, n in insercoes.most_common():
        out.append(f"- +«{b_}» ×{n}")
    out.append("\n### Omissões (do roteiro, não dito)")
    for a_, n in delecoes.most_common():
        out.append(f"- −«{a_}» ×{n}")
    out.append("\n### Primeira palavra dita nos takes escolhidos")
    out.append(", ".join(f"{w} ×{n}" for w, n in aberturas.most_common()))

    # ---------- 4. não mapeado ----------
    out.append("\n## 4. Fala do Carlos fora das linhas (não mapeado) — improvisos, conversas com a IA, falsos começos\n")
    for nm in al.get("nao_mapeado", []):
        out.append(f"- [{nm['fonte']} {nm['inicio']:.1f}–{nm['fim']:.1f}] {nm['texto']}")
    out.append("\n### Separadores ditos pelo Carlos")
    for s in al.get("separadores", []):
        out.append(f"- [{s['fonte']} {s['inicio']:.1f}] {s['texto']}")

    # ---------- 5. muletas e n-gramas em TODA a fala do Carlos ----------
    out.append("\n## 5. Toda a fala do Carlos (takes + fora) — muletas e repetições\n")
    toks = [norm(w["texto"]) for w in carlos]
    toks = [t for t in toks if t]
    c = Counter(toks)
    mul = {m: c[m] for m in MULETAS if c.get(m)}
    dur_total = 0.0
    for f, info in tr["fontes"].items():
        pass
    segs = sorted(carlos, key=lambda w: (w["fonte"], w["inicio"]))
    span = 0.0
    for a, b in zip(segs, segs[1:]):
        if a["fonte"] == b["fonte"]:
            g = b["inicio"] - a["fim"]
            span += (b["fim"] - a["inicio"]) if g < 2.0 else (b["fim"] - b["inicio"])
    out.append(f"Minutos de fala do Carlos (aprox., pausas < 2 s incluídas): {span/60:.1f}")
    out.append("Muletas (contagem bruta, inclui as que estão no roteiro): " + ", ".join(f"{k} ×{v}" for k, v in sorted(mul.items(), key=lambda x: -x[1])))
    ng = Counter()
    for n in (2, 3):
        for i in range(len(toks) - n + 1):
            ng[" ".join(toks[i:i + n])] += 1
    out.append("\nBigramas/trigramas mais ditos (≥3):")
    for g, n in ng.most_common(60):
        if n >= 3:
            out.append(f"- {g} ×{n}")

    # ---------- 6. fala contínua por fonte (só Carlos), com pausas marcadas ----------
    out.append("\n## 6. Fala contínua do Carlos por arquivo (pausas > 0,7 s marcadas com //; > 2 s com ///)\n")
    for fonte in tr["fontes"]:
        ws = [w for w in carlos if w["fonte"] == fonte]
        if not ws:
            continue
        out.append(f"\n### {fonte}")
        buf = []
        for a, b in zip(ws, ws[1:] + [None]):
            buf.append(a["texto"])
            if b is not None:
                g = b["inicio"] - a["fim"]
                if g > 2.0:
                    buf.append(f"///[{g:.1f}s]")
                elif g > 0.7:
                    buf.append("//")
        out.append(" ".join(buf))

    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
