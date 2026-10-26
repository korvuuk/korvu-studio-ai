"""Converte videos/<slug>/roteiro.md em roteiro.json (contrato: docs/contratos.md §1) e valida.

Uso: uv run python .claude/skills/roteiro-reels/scripts/parse_roteiro.py videos/<slug> [--quiet]
Saída: 0 = ok (pode ter avisos), 1 = erros.
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

import yaml

SECOES = {"hook", "promessa", "corpo", "payoff", "cta", "hook-alt"}
# Roteiro NARRATIVO (decisão do Carlos, 14/10 — 00-marca/modelo-roteiro-narrativo.md): a coluna Seção pode
# usar os nomes dos blocos do arco. Em `roteiro.json`, `secao` continua sendo a seção canônica acima
# (capa, legendas e cartão do CTA leem hook/payoff/cta) e o nome do bloco vai em `bloco`.
BLOCOS = {
    "gancho": "hook", "gancho-alt": "hook-alt",
    "contexto": "corpo", "historia": "corpo", "desafio": "corpo",
    "virada": "corpo", "revolucao": "corpo",
    "climax": "payoff", "reflexao": "payoff",
}


def normalizar_secao(txt: str) -> tuple[str, str]:
    """'Reflexão' → ('payoff', 'reflexao'); 'corpo' → ('corpo', 'corpo'). Seção desconhecida volta como está."""
    s = unicodedata.normalize("NFKD", txt.strip().lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"\s+", "-", s)
    return BLOCOS.get(s, s), s
ID_RE = re.compile(r"^L\d{2}[B-Z]?$")
PAUSA_RE = re.compile(r"\[(pausa(?: longa)?)\]", re.IGNORECASE)
DESTAQUE_RE = re.compile(r"\*\*(.+?)\*\*")
ANIM_RE = re.compile(r"ANIMA[CÇ][AÃ]O\s*\[(full|split|card)\]\s*:\s*(.+)", re.IGNORECASE)
TC = r"\d{1,2}:\d{2}(?:[.,]\d+)?"
EXTRA_RE = re.compile(rf"EXTRA\s*:\s*(E\d{{2}})(?:\s+(split|full|card))?(?:\s+({TC})\s*[–-]\s*({TC}))?", re.IGNORECASE)
EXTRA_ID_RE = re.compile(r"^E\d{2}$")
TIPOS_EXTRA = {"tela", "print", "imagem", "video", "animacao", "camera"}
PAUSA_SEG = {"normal": 0.2, "pausa": 0.6, "pausa_longa": 0.9}


def tc_seg(tc: str | None) -> float | None:
    if not tc:
        return None
    m, s = tc.replace(",", ".").split(":")
    return round(int(m) * 60 + float(s), 3)


def expandir_linhas(txt: str) -> list[str]:
    ids = []
    for a, b in re.findall(r"L(\d{2})\s*[–-]\s*L(\d{2})", txt):
        ids += [f"L{n:02d}" for n in range(int(a), int(b) + 1)]
    ids += re.findall(r"L\d{2}[B-Z]?", re.sub(r"L\d{2}\s*[–-]\s*L\d{2}", "", txt))
    return list(dict.fromkeys(ids))


def ler_extras(corpo: str, erros: list[str], avisos: list[str]) -> list[dict]:
    extras = []
    for cells in ler_tabela(corpo, "Cenas extras", obrigatoria=False):
        cells += [""] * (7 - len(cells))
        eid, tipo, desc, fonte, credito, som, linhas_txt = (c.strip() for c in cells[:7])
        eid = eid.upper()
        tipo = tipo.lower().replace("animação", "animacao").replace("vídeo", "video")
        if not EXTRA_ID_RE.match(eid):
            erros.append(f"Cenas extras: ID '{eid}' inválido (use E01, E02…)")
        if tipo not in TIPOS_EXTRA:
            erros.append(f"{eid}: tipo '{tipo}' inválido ({', '.join(sorted(TIPOS_EXTRA))})")
        credito = None if credito in ("", "—", "-") else credito
        if tipo in ("video", "print") and not credito:
            avisos.append(f"{eid}: extra de terceiros ({tipo}) sem crédito")
        extras.append({"id": eid, "tipo": tipo, "descricao": desc, "fonte": fonte, "credito": credito,
                       "som": som.lower() in ("sim", "s", "yes"), "linhas": expandir_linhas(linhas_txt)})
    if len({e["id"] for e in extras}) != len(extras):
        erros.append("Cenas extras: ID duplicado")
    return extras


def ler_frontmatter(texto: str) -> tuple[dict, str]:
    if not texto.startswith("---"):
        raise ValueError("roteiro.md precisa começar com frontmatter YAML (---)")
    _, fm, corpo = texto.split("---", 2)
    return yaml.safe_load(fm) or {}, corpo


def palavras_de(fala: str) -> list[str]:
    limpo = re.sub(r"[^\wÀ-ÿ\s'-]", " ", fala.lower())
    return [p for p in limpo.split() if p.strip("-'")]


def ler_tabela(corpo: str, titulo: str = "Roteiro", obrigatoria: bool = True) -> list[list[str]]:
    m = re.search(rf"^##\s+{re.escape(titulo)}\s*$(.*?)(?=^##\s|\Z)", corpo, re.MULTILINE | re.DOTALL | re.IGNORECASE)
    if not m:
        if obrigatoria:
            raise ValueError(f"Seção '## {titulo}' não encontrada")
        return []
    linhas = []
    for raw in m.group(1).splitlines():
        raw = raw.strip()
        if not raw.startswith("|") or re.match(r"^\|\s*-", raw):
            continue
        cells = [c.strip() for c in raw.strip("|").split("|")]
        if cells and cells[0].upper() == "ID":
            continue
        linhas.append(cells)
    return linhas


def parse(video_dir: Path) -> tuple[dict, list[str], list[str]]:
    erros: list[str] = []
    avisos: list[str] = []
    fm, corpo = ler_frontmatter((video_dir / "roteiro.md").read_text(encoding="utf-8"))
    wps = float(fm.get("wps_ref") or 2.3)

    linhas = []
    vistos = set()
    t = 0.0
    for cells in ler_tabela(corpo):
        # TELA é OPCIONAL (pedido do Carlos, 2026-09-17: "o roteiro só precisa ter o que eu vou falar").
        # Roteiro enxuto = | ID | Seção | FALA |. As cenas ficam na tabela "## Cenas extras", com o
        # pesquisador-de-material/produtor-de-extras — nunca como instrução de atuação na fala.
        if len(cells) < 3:
            erros.append(f"Linha da tabela com colunas a menos: {cells}")
            continue
        lid, fala_orig = cells[0], cells[2]
        secao, bloco = normalizar_secao(cells[1])
        tela = cells[3] if len(cells) > 3 else ""
        if not ID_RE.match(lid):
            erros.append(f"{lid}: ID inválido (use L01, L02… ou L01B)")
        if lid in vistos:
            erros.append(f"{lid}: ID duplicado")
        vistos.add(lid)
        if secao not in SECOES:
            erros.append(f"{lid}: seção '{cells[1]}' inválida ({', '.join(sorted(SECOES | set(BLOCOS)))})")

        pausas = list(PAUSA_RE.finditer(fala_orig))
        pausa_depois = "normal"
        if pausas:
            ultimo = pausas[-1]
            if fala_orig[ultimo.end():].strip() or len(pausas) > 1:
                erros.append(f"{lid}: [pausa] só pode aparecer uma vez, no fim da linha — divida a frase")
            pausa_depois = "pausa_longa" if "longa" in ultimo.group(1).lower() else "pausa"
        destaques = DESTAQUE_RE.findall(fala_orig)
        fala = PAUSA_RE.sub("", DESTAQUE_RE.sub(r"\1", fala_orig))
        fala = re.sub(r"\s*/\s*", " ", fala)  # "/" = respiro (teleprompter/narrador); não é falado
        fala = re.sub(r"\s+", " ", fala).strip()
        if re.search(r"\[[^\]]+\]", fala):
            erros.append(f"{lid}: indicação entre [colchetes] na FALA — o roteiro só tem o que é falado "
                         "(cena vai na tabela 'Cenas extras'; nada de gesto, olhar ou postura)")
        palavras = palavras_de(fala)
        if not palavras:
            erros.append(f"{lid}: FALA vazia")
        if len(palavras) > 18:
            avisos.append(f"{lid}: {len(palavras)} palavras (ideal ≤ 18) — considere dividir")

        anim = None
        m = ANIM_RE.search(tela)
        if m:
            anim = {"modo": m.group(1).lower(), "descricao": m.group(2).split(" · ")[0].strip()}
        extras_ref = [{"id": x.group(1).upper(), "modo": (x.group(2) or "split").lower(),
                       "in": tc_seg(x.group(3)), "out": tc_seg(x.group(4))} for x in EXTRA_RE.finditer(tela)]

        alternativa = None
        if secao == "hook-alt" or re.match(r"^L\d{2}[B-Z]$", lid):
            alternativa = lid[:3]
            tempo = None
            if len(palavras) > 12:
                avisos.append(f"{lid}: hook alternativo com {len(palavras)} palavras (máx. 12)")
        else:
            dur = len(palavras) / wps + PAUSA_SEG[pausa_depois]
            tempo = [round(t, 2), round(t + dur, 2)]
            t += dur

        linhas.append({
            "id": lid,
            "secao": secao,
            "bloco": bloco,
            "fala": fala,
            "fala_original": fala_orig,
            "palavras": palavras,
            "destaques": destaques,
            "pausa_depois": pausa_depois,
            "tela": tela,
            "animacao": anim,
            "extras_ref": extras_ref,
            "alternativa_de": alternativa,
            "tempo_estimado": tempo,
        })

    principais = [l for l in linhas if not l["alternativa_de"]]
    if not principais:
        erros.append("Nenhuma linha principal encontrada na tabela")
    else:
        if principais[0]["secao"] != "hook":
            erros.append("A primeira linha principal deve ser o hook")
        if len(principais[0]["palavras"]) > 12:
            avisos.append(f"Hook com {len(principais[0]['palavras'])} palavras (máx. 12)")
        if not any(l["secao"] == "cta" for l in principais):
            avisos.append("Nenhuma linha de CTA")
        # Roteiro narrativo (14/10): se usa os blocos do arco, tem de fechar com a lição antes do CTA.
        blocos = {l["bloco"] for l in principais}
        if blocos & (set(BLOCOS) - {"gancho", "gancho-alt"}) and "reflexao" not in blocos:
            avisos.append("Roteiro narrativo sem bloco 'reflexao' — falta a lição no fim "
                          "(00-marca/modelo-roteiro-narrativo.md)")
    for alt in (l for l in linhas if l["alternativa_de"]):
        if alt["alternativa_de"] not in vistos:
            erros.append(f"{alt['id']}: não existe a linha {alt['alternativa_de']}")

    extras = ler_extras(corpo, erros, avisos)
    ids_extras = {e["id"] for e in extras}
    usados = set()
    for l in linhas:
        for r in l["extras_ref"]:
            usados.add(r["id"])
            if r["id"] not in ids_extras:
                erros.append(f"{l['id']}: EXTRA {r['id']} não está na tabela '## Cenas extras'")
            if r["in"] is not None and r["out"] is not None and r["out"] <= r["in"]:
                erros.append(f"{l['id']}: EXTRA {r['id']} com trecho inválido ({r['in']}–{r['out']})")
    # A ligação cena↔linha pode vir de dois lugares: da coluna TELA (`EXTRA: Exx`, formato antigo) ou da
    # coluna "Linhas" da própria tabela de cenas extras — que virou o normal com o roteiro enxuto
    # (2026-09-17: o roteiro só tem a fala). Só avisa quando a cena não aponta para lugar nenhum.
    ids_validos = {l["id"] for l in linhas}
    # 2026-09-19: a coluna "Linhas" era VALIDADA mas nunca virava `extras_ref`, e o edl.py só lê `extras_ref`.
    # Com o roteiro enxuto (sem coluna TELA, decisão de 17/09) deixou de haver qualquer ligação cena↔linha:
    # o Hassabis tinha 9 cenas extras declaradas e a EDL saía com **0 overlays**, em silêncio.
    por_id = {l["id"]: l for l in linhas}
    for e in extras:
        for lid in e["linhas"]:
            l = por_id.get(lid)
            if l is None:
                continue
            # 2026-09-19 (Carlos): "no CTA não precisa passar conteúdo extra nenhum, o meu vídeo tem que
            # assumir a tela toda". O pedido é dele e nada pode competir com ele na tela nesse momento.
            if l.get("secao") == "cta":
                avisos.append(f"{e['id']}: cena extra ignorada na {lid} — o CTA é sempre o Carlos em tela cheia")
                continue
            if any(r["id"] == e["id"] for r in l["extras_ref"]):
                continue                                   # já veio da coluna TELA (formato antigo)
            l["extras_ref"].append({"id": e["id"], "modo": "split", "in": None, "out": None})
            usados.add(e["id"])
    for e in extras:
        if e["id"] not in usados and not e["linhas"]:
            avisos.append(f"{e['id']}: cena extra listada sem linhas — preencha a coluna 'Linhas' da tabela")
        desconhecidas = [x for x in e["linhas"] if x not in ids_validos]
        if desconhecidas:
            erros.append(f"{e['id']}: coluna 'Linhas' cita {', '.join(desconhecidas)}, que não existe no roteiro")

    total = sum(len(l["palavras"]) for l in principais)
    alvo = int(fm.get("palavras_alvo") or round(wps * float(fm.get("duracao_alvo") or 60)))
    if alvo and abs(total - alvo) > 0.10 * alvo:
        avisos.append(f"Total de {total} palavras, alvo {alvo} (±10%)")
    duracao_alvo = float(fm.get("duracao_alvo") or 60)
    if t > duracao_alvo * 1.1:
        avisos.append(f"Duração estimada {t:.1f}s acima do alvo {duracao_alvo:.0f}s")

    if fm.get("cta_tipo") == "palavra-material":
        if not fm.get("cta_palavra"):
            erros.append("cta_tipo palavra-material sem cta_palavra")
        elif not re.fullmatch(r"[A-Z0-9]{2,15}", str(fm["cta_palavra"])):
            avisos.append("cta_palavra deve ser uma palavra só, maiúscula, sem acento")
        elif str(fm["cta_palavra"]).upper() in {"CORVO", "KORVU"}:
            erros.append(f"cta_palavra {fm['cta_palavra']} é proibida (fluxo descontinuado, 00-marca/cta.md)")
        if not fm.get("material"):
            erros.append("cta_tipo palavra-material sem descrição de 'material'")
        # Decisão de 13/10: palavra-chave = SEMPRE um PDF, feito pelo produtor-de-material a partir do roteiro.
        # material_titulo é como o direct chama o PDF: "Aqui está {material_titulo} que você pediu".
        mt = str(fm.get("material_titulo") or "").strip()
        if not mt:
            erros.append("cta_tipo palavra-material sem 'material_titulo' (ex.: \"o guia do prompt\")")
        elif not re.match(r"^(o|a|os|as) ", mt):
            avisos.append(f"material_titulo '{mt}' deve começar com artigo (o/a/os/as) — entra em "
                          "\"Aqui está {material_titulo} que você pediu\"")

    dados = {
        "slug": fm.get("slug") or video_dir.name,
        "versao": fm.get("versao", 1),
        "tema": fm.get("tema"),
        "pilar": fm.get("pilar"),
        "estrutura": fm.get("estrutura"),
        "hook_template": fm.get("hook_template"),
        "duracao_alvo": duracao_alvo,
        "wps_ref": wps,
        "hooks": fm.get("hooks"),
        "hook_escolhido": fm.get("hook_escolhido"),
        "titulo": fm.get("titulo"),
        # pose da capa: o que ele faz nos 3 s parados antes da L01 (muda a cada vídeo, combina com o título).
        # O ChatGPT Voz lê isto em voz alta antes de começar — ele esquece se ninguém lembrar (2026-09-18).
        "pose_capa": fm.get("pose_capa"),
        "cta_tipo": fm.get("cta_tipo"),
        "cta_palavra": fm.get("cta_palavra"),
        "material": fm.get("material"),
        "material_titulo": fm.get("material_titulo"),
        "total_palavras": total,
        "duracao_estimada": round(t, 1),
        "extras": extras,
        "linhas": linhas,
    }
    return dados, erros, avisos


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 1
    video_dir = Path(args[0]).resolve()
    try:
        dados, erros, avisos = parse(video_dir)
    except (ValueError, FileNotFoundError, yaml.YAMLError) as e:
        print(f"ERRO: {e}")
        return 1
    (video_dir / "roteiro.json").write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    if "--quiet" not in sys.argv:
        print(f"{dados['slug']}: {len([l for l in dados['linhas'] if not l['alternativa_de']])} linhas, "
              f"{dados['total_palavras']} palavras, ~{dados['duracao_estimada']}s")
    for a in avisos:
        print(f"AVISO: {a}")
    for e in erros:
        print(f"ERRO: {e}")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
