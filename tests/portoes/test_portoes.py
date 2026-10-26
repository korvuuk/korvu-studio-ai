"""Teste do scripts/portoes.py (GAUNTLET) num ROOT temporário (CONTENT_AI_ROOT). Sem rede, sem tocar no projeto.

Uso (da raiz do projeto):  uv run python tests/portoes/test_portoes.py [--manter]
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

PROJETO = Path(__file__).resolve().parents[2]
ROOT = Path(tempfile.mkdtemp(prefix="korvu-portoes-"))
os.environ["CONTENT_AI_ROOT"] = str(ROOT)
sys.path.insert(0, str(PROJETO / "scripts"))
import portoes  # noqa: E402  (lê o CONTENT_AI_ROOT no import)

RES: list[tuple[str, bool, str]] = []
ROTEIRO_MODELO = PROJETO / "videos" / "2026-10-24-comando-secreto" / "roteiro.md"


def ok(nome: str, cond, detalhe: str = "") -> None:
    RES.append((nome, bool(cond), detalhe))
    print(f"  [{'PASS' if cond else 'FAIL'}] {nome}" + (f" — {detalhe}" if detalhe else ""))


def erro(fn) -> str:
    try:
        fn()
    except portoes.ErroPortao as e:
        return str(e)
    return ""


def relatorio(alvo: Path, nome: str) -> str:
    f = alvo / "qa" / "portoes" / nome
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text("relatório de teste\n")
    return str(f)


def reg(alvo: Path, portao: str, resultado: str = "APROVADO", s0=0, s1=0, s2=0, decisao="") -> dict:
    imp = portoes.impressao(portoes.arquivos_da_area(alvo, portao))
    return portoes.registrar(alvo, portao, resultado, imp, relatorio(alvo, f"{portao}.md"), s0, s1, s2,
                             decisao=decisao)


def st(alvo: Path, portao: str) -> str:
    return portoes.estado(alvo, portao)["status"]


def criar_video(slug: str) -> Path:
    v = ROOT / "videos" / slug
    for d in ("edicao/cor", "capa", "material", "brutos/extras", "qa"):
        (v / d).mkdir(parents=True, exist_ok=True)
    shutil.copy(ROTEIRO_MODELO, v / "roteiro.md")
    (v / "material" / "guia.pdf").write_bytes(b"%PDF-1.4 guia\n")
    (v / "edicao" / "cor" / "corte-cor.mp4").write_bytes(b"cor v5 certa")
    (v / "capa" / "capa-A.png").write_bytes(b"capa A sobre a cor certa")
    (v / "brutos" / "extras" / "E01-foto.png").write_bytes(b"extra 1")
    (v / "brutos" / "extras" / ".DS_Store").write_bytes(b"lixo do Finder")
    (v / "edicao" / "final.mp4").write_bytes(b"final")
    (v / "edicao" / "legendas.srt").write_text("1\n00:00:00,000 --> 00:00:01,000\nOi\n")
    return v


def main() -> int:
    (ROOT / "_controle").mkdir()
    (ROOT / "06-publicar").mkdir()
    v = criar_video("2026-10-30-teste")
    try:
        print("\n== estados básicos ==")
        ok("roteiro pendente antes do portão", st(v, "roteiro") == "pendente")
        ok("pauta não se aplica sem pesquisa", st(v, "pauta") == "nao_se_aplica")
        ok(".DS_Store fora da área", ".DS_Store" not in " ".join(portoes.arquivos_da_area(v, "imagem")))
        ok("exigir aponta os 3 pendentes", len(portoes.exigir(v)) == 3, str(portoes.exigir(v)))

        print("\n== registrar: regras do veredicto ==")
        rel = relatorio(v, "x.md")
        ok("impressão velha é recusada (SHA congelado)",
           "mudou enquanto" in erro(lambda: portoes.registrar(v, "roteiro", "APROVADO", "000000000000", rel, 0, 0, 0)))
        imp = portoes.impressao(portoes.arquivos_da_area(v, "roteiro"))
        ok("APROVADO com S1 aberto é recusado",
           "bloqueiam sempre" in erro(lambda: portoes.registrar(v, "roteiro", "APROVADO", imp, rel, 0, 1, 0)))
        ok("BLOQUEADO só com S2 é recusado",
           "S2 não bloqueia" in erro(lambda: portoes.registrar(v, "roteiro", "BLOQUEADO", imp, rel, 0, 0, 2)))
        ok("'aprovado com ressalvas' não existe",
           "não há aprovado parcial" in erro(lambda: portoes.registrar(v, "roteiro", "PARCIAL", imp, rel, 0, 0, 0)))
        ok("relatório obrigatório",
           "relatório não encontrado" in erro(lambda: portoes.registrar(v, "roteiro", "APROVADO", imp, "nada.md", 0, 0, 0)))
        r = reg(v, "roteiro", s2=1)
        ok("APROVADO com S2 registrado", r["resultado"] == "APROVADO" and st(v, "roteiro") == "aprovado")
        ok("linha do veredicto à letra", portoes.linha_veredicto(r).startswith("PORTÃO-ROTEIRO: APROVADO — sobre "))

        print("\n== roteiro: só a FALA vence o portão ==")
        txt = (v / "roteiro.md").read_text()
        (v / "roteiro.md").write_text(txt + "\n<!-- nota de status: gravado em 30/10 -->\n")
        ok("nota fora da fala não vence", st(v, "roteiro") == "aprovado")
        (v / "roteiro.md").write_text(txt.replace("| Ela vira / cena de filme. |", "| Ela vira / cena de cinema. |"))
        ok("fala mudada vence o roteiro", st(v, "roteiro") == "vencido", portoes.estado(v, "roteiro")["motivos"])
        reg(v, "roteiro")
        (v / "material" / "guia.pdf").write_bytes(b"%PDF-1.4 guia v2\n")
        ok("PDF regerado vence o roteiro", st(v, "roteiro") == "vencido")
        reg(v, "roteiro")

        print("\n== imagem: o caso de 21/10 (cor corrigida, capa velha) ==")
        reg(v, "imagem")
        shutil.copy(v / "capa" / "capa-A.png", v / "capa" / "capa.png")
        ok("capa escolhida = cópia da aprovada continua aprovada", st(v, "imagem") == "aprovado")
        (v / "capa" / "capa-A.png").unlink()
        ok("capa não escolhida apagada (limpar_video) não vence", st(v, "imagem") == "aprovado")
        (v / "edicao" / "cor" / "corte-cor.mp4").write_bytes(b"cor refeita")
        e = portoes.estado(v, "imagem")
        ok("cor refeita → portão imagem VENCIDO (a capa tem de ser revista)",
           e["status"] == "vencido" and "corte-cor.mp4" in e["motivos"][0], e["motivos"])

        print("\n== tecto de 3 voltas ==")
        v1 = reg(v, "imagem", "BLOQUEADO", s0=1)
        v2 = reg(v, "imagem", "BLOQUEADO", s1=2)
        v3 = reg(v, "imagem", "BLOQUEADO", s0=1)
        ok("voltas 1, 2 e a 3.ª vira ESCALADO", (v1["volta"], v2["volta"], v3["resultado"]) == (1, 2, "ESCALADO"),
           f"{v1['volta']},{v2['volta']},{v3['resultado']}")
        ok("estado escalado", st(v, "imagem") == "escalado")
        ok("4.ª volta sem decisão do Carlos é recusada", "ESCALADO" in erro(lambda: reg(v, "imagem")))
        ok("--decisao-carlos fora de um ESCALADO é recusada",
           "só vale depois de um ESCALADO" in erro(lambda: reg(v, "corte", decisao="zerar")))
        ok("capa mais velha que a cor atual não se aprova (o erro de 21/10, no código)",
           "capa mais antiga que a cor atual" in erro(lambda: reg(v, "imagem", decisao="(c) pagar mais voltas")))
        (v / "capa" / "capa.png").write_bytes(b"capa refeita sobre a cor nova")
        v4 = reg(v, "imagem", decisao="(c) pagar mais voltas")
        ok("com a decisão dele volta à volta 1", v4["volta"] == 1 and v4["resultado"] == "APROVADO")
        nova = reg(v, "imagem")
        ok("ESCALADO não se repete à 3.ª volta depois de um APROVADO", nova["volta"] == 1)

        print("\n== pacote: selo e conferência ==")
        reg(v, "corte")
        ok("exigir vazio com os 3 aprovados (pauta n/a)", portoes.exigir(v) == [], str(portoes.exigir(v)))
        pac_dir = ROOT / "06-publicar" / v.name
        for d in ("video", "capa", "material", "legendas"):
            (pac_dir / d).mkdir(parents=True, exist_ok=True)
        shutil.copy(v / "edicao/final.mp4", pac_dir / "video/video-final.mp4")
        shutil.copy(v / "capa/capa.png", pac_dir / "capa/capa.png")
        shutil.copy(v / "material/guia.pdf", pac_dir / "material/guia.pdf")
        shutil.copy(v / "edicao/legendas.srt", pac_dir / "legendas/legendas.srt")
        arq = {"video": "video/video-final.mp4", "variantes": [], "capa": "capa/capa.png",
               "material": "material/guia.pdf", "legendas": "legendas/legendas.srt", "roteiro": "roteiro.md"}
        pac = {"slug": v.name, "qa": "PASS", "arquivos": arq}
        pac["gauntlet"] = portoes.selar(v, pac_dir, arq)
        ok("selo tem origem, veredictos e sha dos arquivos",
           pac["gauntlet"]["origem"] == f"videos/{v.name}" and set(pac["gauntlet"]["veredictos"]) == {"roteiro", "imagem", "corte"}
           and len(pac["gauntlet"]["arquivos"]) == 4, json.dumps(pac["gauntlet"])[:200])
        ok("pacote selado confere (agendar)", portoes.conferir_pacote(pac_dir, pac) == [])
        erros = portoes.conferir_pacote(pac_dir, pac, publicacao=True)
        ok("publicar sem PORTÃO-PUBLICACAO é recusado", any("publicacao" in e for e in erros), str(erros))
        (pac_dir / "legenda-instagram.txt").write_text("Comenta ESTILO\n")
        (pac_dir / "legenda-facebook.txt").write_text("Comenta ESTILO\n")
        post = {"slug": v.name, "plataformas": ["instagram", "facebook"], "estado": "agendado",
                "instagram": {"capa": "capa/capa.png", "trial": None, "share_to_feed": True,
                              "legenda_arquivo": "legenda-instagram.txt", "media_id": None},
                "facebook": {"legenda_arquivo": "legenda-facebook.txt"},
                "material": {"palavra": "ESTILO", "arquivo": "material/guia.pdf", "titulo": "o guia", "url": None}}
        (pac_dir / "post.json").write_text(json.dumps(post))
        reg(pac_dir, "publicacao")
        ok("com o portão da publicação aprovado, publica", portoes.conferir_pacote(pac_dir, pac, post, publicacao=True) == [])
        ig, fb = (pac_dir / "legenda-instagram.txt"), (pac_dir / "legenda-facebook.txt")
        (pac_dir / "legenda-facebook.txt").write_text("Comenta ESTILO no Facebook\n")
        reg(pac_dir, "publicacao")
        a, b = ig.read_text(), fb.read_text()
        ig.write_text(b); fb.write_text(a)
        ok("trocar as duas legendas entre si vence a publicação (aprovação por caminho)",
           st(pac_dir, "publicacao") == "vencido")
        ig.write_text(a); fb.write_text(b)
        (pac_dir / "pacote.json").write_text(json.dumps({**pac, "arquivos": {**arq, "video": "video/outra.mp4"}}))
        ok("apontar o pacote para outro vídeo vence a publicação", st(pac_dir, "publicacao") == "vencido")
        (pac_dir / "pacote.json").unlink()
        ok("de volta ao aprovado", st(pac_dir, "publicacao") == "aprovado")
        post.update(estado="publicado", publicado_em="2026-10-30T19:00:00+00:00")
        post["instagram"]["media_id"] = "IGM1"
        (pac_dir / "post.json").write_text(json.dumps(post))
        ok("estado/ids do post.json não vencem o portão", st(pac_dir, "publicacao") == "aprovado")
        post["instagram"]["trial"] = {"graduation_strategy": "MANUAL"}
        (pac_dir / "post.json").write_text(json.dumps(post))
        ok("trocar Trial × normal vence o portão da publicação", st(pac_dir, "publicacao") == "vencido")
        post["instagram"]["trial"] = None
        (pac_dir / "post.json").write_text(json.dumps(post))
        (pac_dir / "capa" / "capa.png").write_bytes(b"capa com a cor velha")
        erros = portoes.conferir_pacote(pac_dir, pac, post)
        ok("capa trocada na fila depois do selo é recusada", any("trocado depois do selo" in e for e in erros), str(erros))
        shutil.copy(v / "capa/capa.png", pac_dir / "capa/capa.png")
        (v / "edicao" / "cor" / "corte-cor.mp4").write_bytes(b"cor refeita de novo")
        erros = portoes.conferir_pacote(pac_dir, pac, post)
        ok("cor refeita na origem → post na fila bloqueado até o portão rever",
           any("origem" in e and "imagem" in e for e in erros), str(erros))

        print("\n== legado ==")
        sem = {"slug": "velho", "qa": "PASS", "arquivos": {}}
        ok("pacote sem selo e fora do legado é recusado",
           "sem selo GAUNTLET" in " ".join(portoes.conferir_pacote(ROOT / "06-publicar" / "velho", sem)))
        (ROOT / "_controle" / "gauntlet-legado.json").write_text(json.dumps({"slugs": ["velho"]}))
        ok("pacote da lista congelada passa sem selo", portoes.conferir_pacote(ROOT / "06-publicar" / "velho", sem) == [])

        print("\n== pauta ==")
        (v / "material" / "dossie.md").write_text("# dossiê\n")
        ok("pesquisa nova torna a pauta exigida", any("pauta" in p for p in portoes.exigir(v)))

        print("\n== sistema (painel): interface e dados ==")
        pn = ROOT / "painel"
        for d in ("web/src/app", "web/node_modules/x", "web/.next", "supabase/migrations", "sync/__pycache__", "design"):
            (pn / d).mkdir(parents=True, exist_ok=True)
        (pn / "web/src/app/page.tsx").write_text("export default function P() { return null }\n")
        (pn / "web/node_modules/x/index.js").write_text("lixo de dependência")
        (pn / "web/.next/build.js").write_text("lixo de build")
        (pn / "web/.env.local").write_text("SEGREDO=nao-entra")
        (pn / "supabase/migrations/001.sql").write_text("create table t (id int);\n")
        (pn / "sync/sincronizar.py").write_text("print('ok')\n")
        (pn / "sync/__pycache__/sincronizar.cpython-312.pyc").write_bytes(b"\x00cache")
        (pn / "design/tokens.md").write_text("# tokens\n")
        ok("o painel exige os três portões do sistema", portoes.portoes_do_alvo(pn) == ("design", "interface", "dados")
           and len(portoes.exigir(pn)) == 3, str(portoes.exigir(pn)))
        area = portoes.arquivos_da_area(pn, "interface")
        ok("node_modules, .next e .env ficam fora da área", set(area) == {"web/src/app/page.tsx"}, str(sorted(area)))
        ok("o design é uma área própria", set(portoes.arquivos_da_area(pn, "design")) == {"design/tokens.md"})
        ok("portão de vídeo num alvo do painel é recusado",
           "não vale para" in erro(lambda: reg(pn, "roteiro")))
        ok("portão do painel num vídeo é recusado", "não vale para" in erro(lambda: reg(v, "interface")))
        reg(pn, "design")
        ok("__pycache__ fica fora da área de dados", "sync/__pycache__/sincronizar.cpython-312.pyc"
           not in portoes.arquivos_da_area(pn, "dados"))
        reg(pn, "interface")
        reg(pn, "dados")
        ok("com os três aprovados o painel segue", portoes.exigir(pn) == [])
        (pn / "design/tokens.md").unlink()
        ok("no código, apagar arquivo também vence o portão", st(pn, "design") == "vencido"
           and "apagado" in " ".join(portoes.estado(pn, "design")["motivos"]))
        ok("aprovar área vazia é recusado", "área vazia" in erro(lambda: reg(pn, "design")))
        (pn / "design/tokens.md").write_text("# tokens\n")
        (pn / "web/src/app/page.tsx").rename(pn / "web/src/app/inicio.tsx")
        ok("no código, renomear arquivo vence o portão (aprovação por caminho)", st(pn, "interface") == "vencido")
        (pn / "web/src/app/inicio.tsx").rename(pn / "web/src/app/page.tsx")
        (pn / "sync/__pycache__/sincronizar.cpython-312.pyc").write_bytes(b"\x00outro cache")
        ok("recompilar o cache do Python não vence o portão de dados", st(pn, "dados") == "aprovado")
        (pn / "supabase/migrations/002.sql").write_text("alter table t add column x int;\n")
        ok("migração nova vence o portão de dados", st(pn, "dados") == "vencido")
        ok("o portão de vídeo não vale para o painel", portoes.portoes_do_alvo(v) == portoes.EXIGIDOS_PACOTE)
    finally:
        if "--manter" not in sys.argv:
            shutil.rmtree(ROOT, ignore_errors=True)
        else:
            print(f"ROOT mantido: {ROOT}")

    falhas = [r for r in RES if not r[1]]
    print(f"\n{len(RES) - len(falhas)}/{len(RES)} PASS")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
