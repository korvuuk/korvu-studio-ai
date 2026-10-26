"""Conferência do painel/biblioteca.yaml REAL contra as fontes dele (só leitura; nada é escrito).

O test_sincronizar.py prova as regras numa raiz temporária; este confere o arquivo de verdade:
  - os textos são os da maquete APROVADA da designer (painel/design/telas/biblioteca.html), à letra: o nome e a frase de
    cada look (na ordem dos cartões), os estilos de capa e de legenda (nome, descrição, qual está em uso), as fontes
    (nome e uso), a stack (nome, tipo, desc) e a frase de cada modelo;
  - o rosto de cada look (seção looks) aparece, com vírgula decimal, em cada linha que a `fonte` cita;
  - cada fonte bate com o remotion/src/brand.ts (pacote importado, estilo e pesos do loadFont);
  - o sincronizador lê o yaml, o cor.md, as LUTs e os briefs reais sem erro e sem nenhum aviso ⚠, cada capa de
    exemplo existe e cada ficha existe.
Lê o projeto real; não abre o banco nem os registros do Claude Code.

Uso (da raiz do projeto):  uv run python painel/tests/test_biblioteca_yaml.py
"""
from __future__ import annotations

import html as html_
import importlib.util
import os
import re
import sys
from pathlib import Path

import yaml

sys.dont_write_bytecode = True

CODIGO = Path(__file__).resolve().parents[2]
SYNC = Path(os.environ.get("PAINEL_TESTE_SYNC") or CODIGO / "painel" / "sync" / "sincronizar.py").resolve()
MAQUETE = CODIGO / "painel" / "design" / "telas" / "biblioteca.html"
YAML = CODIGO / "painel" / "biblioteca.yaml"
for k in ("PAINEL_PROJETO", "CONTENT_AI_ROOT"):
    os.environ.pop(k, None)  # o projeto real
sys.argv = [str(SYNC)]
_spec = importlib.util.spec_from_file_location("sincronizar_conferencia", SYNC)
SN = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(SN)

RES: list[tuple[str, bool]] = []


def ok(nome: str, cond, detalhe="") -> None:
    RES.append((nome, bool(cond)))
    print(f"  [{'PASS' if cond else 'FAIL'}] {nome}" + (f" — {detalhe}" if detalhe and not cond else ""))


def igual(nome: str, obtido, esperado) -> None:
    ok(nome, obtido == esperado, f"obtido {obtido!r} · esperado {esperado!r}")


def secao(html: str, titulo: str) -> str:
    """O trecho da maquete entre o <h2> "titulo" (a 1.ª vez que aparece) e o <h2> seguinte."""
    m = re.search(rf"<h2[^>]*>{re.escape(titulo)}</h2>", html)
    if not m:
        return ""
    prox = re.search(r"<h2[^>]*>", html[m.end():])
    return html[m.end():m.end() + prox.start()] if prox else html[m.end():]


def nome_e_desc(trecho: str) -> list[tuple[str, str]]:
    return [(html_.unescape(n), html_.unescape(d)) for n, d in re.findall(
        r'class="k-estilo-nome">([^<]*)</span>.*?class="k-estilo-desc">([^<]*)</span>', trecho, re.S)]


def main() -> int:
    print(f"sincronizador: {SYNC}\nprojeto:       {SN.PROJETO}\nmaquete:       {MAQUETE.relative_to(CODIGO)}")
    cfg = yaml.safe_load(YAML.read_text(encoding="utf-8"))
    html = MAQUETE.read_text(encoding="utf-8")
    avisos: list[str] = []
    try:
        lido = SN.ler_acervo_yaml(avisos)
        lks = SN.looks(avisos, SN.looks_do_yaml(lido))
        acv = SN.acervo(SN.destinos_de_video(), avisos, lido)
        vids = [d.name for d in sorted((SN.PROJETO / "videos").iterdir()) if d.is_dir() and not d.name.startswith("_")]
        anims = SN.animacoes(vids, avisos)
        erro = None
    except SN.ErroArquivo as e:
        lks, acv, anims, erro = [], {}, [], str(e)

    print("\n== os textos = a maquete aprovada (biblioteca.html), à letra ==")
    looks_m = nome_e_desc(secao(html, "looks de cor."))
    ok("a maquete tem os cartões de look (o teste não passa no vazio)", len(looks_m) >= 1, looks_m)
    igual("looks: o nome e a frase de cada cartão, na ordem (o nome do yaml vence o do .json)",
          [(r["nome"], r["descricao"]) for r in sorted(lks, key=lambda r: r["ordem"])], looks_m)
    capas_t = secao(html, "capas.")
    capas_m = nome_e_desc(capas_t)
    ok("a maquete tem os estilos de capa", len(capas_m) >= 1, capas_m)
    igual("capas (nome, descrição) = a maquete, na mesma ordem", [(c["nome"], c["descricao"]) for c in cfg["capas"]],
          capas_m)
    metas = [html_.unescape(m) for m in re.findall(r'class="k-estilo-meta">([^<]*)</span>', capas_t)]
    igual("em uso = o cartão da maquete que diz \"em uso\" (o outro diz \"usado em\")",
          [c["em_uso"] for c in cfg["capas"]], [m.startswith("em uso") for m in metas])
    igual("legendas (nome, descrição) = a maquete", [(c["nome"], c["descricao"]) for c in cfg["legendas"]],
          nome_e_desc(secao(html, "legendas.")))
    igual("fontes (nome, uso) = a maquete; a reserva (Inter Tight) não aparece na tela",
          [(f["familia"], f["uso"]) for f in cfg["fontes"] if not f.get("reserva")], nome_e_desc(secao(html, "fontes.")))
    sis = secao(html, "sistema.")
    stack = []
    for t in re.findall(r'<div class="k-sis"><span class="k-estilo-nome">([^<]*)</span><span><span class="k-etiqueta '
                        r'k-etiqueta--tipo">([^<]*)</span></span><span class="k-estilo-desc">([^<]*)</span>', sis):
        if tuple(html_.unescape(x) for x in t) not in stack:
            stack.append(tuple(html_.unescape(x) for x in t))
    ok("a maquete tem a stack", len(stack) >= 1, len(stack))
    igual("ferramentas (nome, tipo, desc) = a maquete, na mesma ordem",
          [(f["nome"], f["tipo"], f["desc"]) for f in cfg["ferramentas"]], stack)
    modelos = [tuple(html_.unescape(x) for x in t) for t in re.findall(
        r'<span class="k-estilo-nome">([^<]*)</span><span class="k-etiqueta k-etiqueta--tipo">Modelo de IA</span></div>'
        r'\s*<span class="k-sis-modelo-pct">[^<]*</span><span class="k-estilo-desc">([^<]*)</span>', sis)]
    ok("a maquete tem os modelos", len(modelos) >= 1, modelos)
    igual("modelos (o nome da tabela de preços, desc) = a maquete, na mesma ordem",
          [(SN.PRECOS.get(m["modelo"], ("?",))[0], m["desc"]) for m in cfg["modelos"]], modelos)

    print("\n== o rosto de cada look está nas linhas que a fonte cita ==")
    for x in [x for x in cfg.get("looks", []) if "rosto_ire" in x]:
        m = re.fullmatch(r"([^:]+):(\d+(?:,\d+)*)", x["fonte"])
        texto = (SN.PROJETO / m.group(1)).read_text(encoding="utf-8").splitlines() if m else []
        numero = f"{x['rosto_ire']:.1f}".replace(".", ",")
        linhas = [int(n) for n in m.group(2).split(",")] if m else []
        ok(f"{x['id']}: rosto {numero} IRE em {x['fonte']}", m and linhas and all(
            0 < n <= len(texto) and numero in texto[n - 1] and "rosto" in texto[n - 1].lower() for n in linhas),
           x["fonte"])

    print("\n== o sincronizador lê os arquivos reais sem erro nem aviso ==")
    ok("nenhum ✗ (arquivo ilegível ou fora do formato)", erro is None, erro)
    igual("nenhum aviso ⚠ (yaml, cor.md, LUTs, briefs)", avisos, [])
    ok("cada capa de exemplo foi achada", acv and all(r["caminho"] for r in acv["capa_estilos_exemplos"]),
       [r["slug"] for r in acv.get("capa_estilos_exemplos", []) if not r["caminho"]])
    ok("cada ficha citada existe", acv and all(r["ficha_existe"] is not False
                                               for r in acv["capa_estilos"] + acv["legenda_estilos"]))
    ok("cada fonte com pacote bate com o remotion/src/brand.ts (confere_brand_ts = true)",
       acv and all(r["confere_brand_ts"] is True for r in acv["fontes"] if r["remotion"]),
       [(r["familia"], r["confere_brand_ts"]) for r in acv.get("fontes", [])])
    ok("cada modelo com frase está na tabela de preços", acv and all(r["com_preco"] for r in acv["modelos_descricao"]))
    ok("há um look em uso e os papéis vêm do cor.md", sum(1 for r in lks if r["papel"] == "em_uso") == 1,
       [(r["id"], r["papel"]) for r in lks])
    igual("o rosto de cada look = o do yaml (os sem item ficam NULL)",
          {r["id"]: r["rosto_ire"] for r in lks if r["tipo"] == "look"},
          {r["id"]: next((SN.Decimal(str(x["rosto_ire"])) for x in cfg.get("looks", [])
                          if x["id"] == r["id"] and "rosto_ire" in x), None)
           for r in lks if r["tipo"] == "look"})
    ok("toda animação com título, modo e duração", all(r["titulo"] and r["modo"] and r["duracao_s"] for r in anims),
       [r["id"] for r in anims if not (r["titulo"] and r["modo"] and r["duracao_s"])])
    falhas = [r for r in RES if not r[1]]
    print(f"\n{len(RES) - len(falhas)}/{len(RES)} PASS" + (f" · {len(falhas)} FAIL" if falhas else ""))
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
