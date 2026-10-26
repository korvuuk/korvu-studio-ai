#!/usr/bin/env python3
"""GAUNTLET — livro de veredictos dos portões (docs/gauntlet.md).

Quem constrói não é quem aprova. Cada área tem um PORTÃO (agente que audita e não constrói), e o veredicto
dele fica preso aos ARQUIVOS que ele viu: se um arquivo da área muda depois do APROVADO, o veredicto vence
sozinho e o portão roda de novo. Foi o que faltou em 21/10: a cor do livro-chatgpt foi corrigida, mas as capas
feitas com a cor velha seguiram para a fila, porque o único selo do pacote era `"qa": "PASS"`, do vídeo.

Uso (da raiz, sempre com uv):
  uv run python scripts/portoes.py impressao <alvo> <portão>       # o portão congela o que vai auditar
  uv run python scripts/portoes.py registrar <alvo> <portão> APROVADO|BLOQUEADO --impressao <imp> \
        --relatorio <arquivo.md> --s0 N --s1 N --s2 N [--nota "…"] [--decisao-carlos "…"]
  uv run python scripts/portoes.py estado [<alvo>]                 # sinais de um vídeo (ou de todos)
  uv run python scripts/portoes.py exigir <alvo>                   # exit 1 se faltar portão para o pacote
  uv run python scripts/portoes.py conferir-pacote 06-publicar/<slug> [--publicacao]

<alvo> = videos/<slug> (ou só <slug>) para pauta/roteiro/imagem/corte; 06-publicar/<slug> para publicacao;
         painel para design/interface/dados (o GAUNTLET do painel web).

Escala (docs/gauntlet.md §escala): S0 e S1 bloqueiam; S2 vai para _controle/backlog-portoes.md e não bloqueia.
Tecto de 3 voltas: a 3.ª volta BLOQUEADA vira ESCALADO e só volta a rodar com --decisao-carlos.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

PROJETO = Path(__file__).resolve().parent.parent
ROOT = Path(os.environ.get("CONTENT_AI_ROOT") or PROJETO).resolve()
LIVRO = "portoes.json"
CACHE = ROOT / "_controle" / ".cache-portoes.json"
LEGADO = ROOT / "_controle" / "gauntlet-legado.json"
VOLTAS_MAX = 3

# Portão → quem fiscaliza, o que cobre (padrões relativos ao alvo) e onde vive o alvo.
# Os eixos são exclusivos: um arquivo pertence a UM portão (sobreposição faz cada um assumir que o outro viu).
PORTOES: dict[str, dict] = {
    "pauta": {
        "agente": "portao-pauta", "alvo": "video",
        "fiscaliza": ["estrategista", "pesquisador-de-material", "buscador-de-videos", "curador-de-obra"],
        "padroes": ["material/dossie.md", "material/fontes.json", "material/youtube/catalogo*.md",
                    "material/obra*.md", "material/obra*.json", "material/capas/LIVROS.md"],
    },
    "roteiro": {
        "agente": "revisor-de-roteiro", "alvo": "video",
        "fiscaliza": ["roteirista", "produtor-de-material"],
        "padroes": ["roteiro.md", "material/*.pdf"],
    },
    "imagem": {
        "agente": "portao-imagem", "alvo": "video",
        "fiscaliza": ["colorista", "designer-de-capas", "produtor-de-extras", "animador"],
        "padroes": ["brutos/extras/**/*", "edicao/cor/corte-cor*.mp4", "capa/capa*.png"],
    },
    "corte": {
        "agente": "revisor-de-video", "alvo": "video",
        "fiscaliza": ["editor-de-video", "produtor-musical"],
        "padroes": ["edicao/final*.mp4", "edicao/legendas.srt"],
    },
    "publicacao": {
        "agente": "portao-publicacao", "alvo": "fila",
        "fiscaliza": ["publicador"],
        "padroes": ["video/*.mp4", "capa/*.png", "material/*.pdf", "legenda-instagram.txt",
                    "legenda-facebook.txt", "post.json", "pacote.json"],
    },
    # ── SISTEMA (painel web, 22/10): o mesmo GAUNTLET para o código. Alvo = painel/ ──
    # O desenho vem antes do código e é aprovado sozinho (o mesmo agente audita as duas áreas): senão uma entrega só
    # de design nunca passaria, porque o código ainda não a implementou (revisão de 22/10).
    "design": {
        "agente": "portao-interface", "alvo": "sistema",
        "fiscaliza": ["designer-de-produto"],
        "padroes": ["design/**/*"],
    },
    "interface": {
        "agente": "portao-interface", "alvo": "sistema",
        "fiscaliza": ["engenheiro-frontend"],
        "padroes": ["web/src/**/*", "web/public/**/*", "web/package.json", "web/package-lock.json",
                    "web/next.config.ts", "web/postcss.config.mjs", "web/tsconfig.json", "web/eslint.config.mjs",
                    "capturar.sh"],
    },
    "dados": {
        "agente": "portao-dados", "alvo": "sistema",
        "fiscaliza": ["engenheiro-backend"],
        "padroes": ["supabase/config.toml", "supabase/migrations/*.sql", "supabase/seed.sql", "sync/**/*",
                    "tests/**/*", "iniciar.sh", "so-no-mac.sh", "studio.sh", "*.yaml"],
    },
}
# Na fila, o portão aprova cada arquivo NO SEU PAPEL: trocar o vídeo de A por L01C, ou as duas legendas entre si,
# vence o veredicto mesmo que os dois arquivos já tivessem sido aprovados (revisão independente, 22/10).
POR_CAMINHO = {"publicacao", "design", "interface", "dados"}  # no código, mover/renomear arquivo também é mudança
# Pastas que nunca contam (dependências, build, cache do Python) — além de tudo o que começa com ".".
IGNORAR = {"node_modules", "__pycache__", ".next"}
# O pacote só sai de videos/ com estes aprovados (pauta só quando há pesquisa no vídeo).
EXIGIDOS_PACOTE = ("pauta", "roteiro", "imagem", "corte")
# O painel só vai para o Carlos (e, um dia, para o domínio) com os dois portões do sistema aprovados.
EXIGIDOS_SISTEMA = ("design", "interface", "dados")
# Áreas que podem não existir num alvo sem bloquear nada: vídeo sem pesquisa, painel sem design novo.
OPCIONAIS = {"pauta", "design"}
# Arquivo do pacote → portão de origem que tem de o ter aprovado, e de que parte da área ele tem de vir
# (uma capa só vale se o portão a aprovou COMO capa — não porque uma foto de extra tem o mesmo conteúdo).
ORIGEM_DO_ARQUIVO = {"video": "corte", "variantes": "corte", "capa": "imagem", "material": "roteiro",
                     "legendas": "corte"}
PAPEL = {"video": "edicao/final", "variantes": "edicao/final", "capa": "capa/", "material": "material/",
         "legendas": "edicao/legendas"}
SO_LEITURA = False  # o publicar.py liga no --dry-run: nada é escrito, nem o cache
# Campos do post.json que mudam o que vai ao ar. Datas, ids e estado mudam com o uso e não vencem o portão.
POST_ESTAVEL = {"plataformas": None, "instagram": ("capa", "trial", "share_to_feed", "legenda_arquivo"),
                "facebook": ("legenda_arquivo",), "material": ("palavra", "arquivo", "titulo")}


class ErroPortao(Exception):
    pass


def agora() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


# ───────────────────────── impressão dos arquivos ─────────────────────────

_cache: dict | None = None


def _cache_ler() -> dict:
    global _cache
    if _cache is None:
        try:
            _cache = json.loads(CACHE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            _cache = {}
    return _cache


def _cache_gravar() -> None:
    if _cache is None or SO_LEITURA:
        return
    try:
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        tmp = CACHE.with_suffix(".tmp")
        tmp.write_text(json.dumps(_cache), encoding="utf-8")
        tmp.replace(CACHE)
    except OSError:
        pass  # cache é só velocidade; sem ele o hash é recalculado


def sha_arquivo(p: Path) -> str:
    """sha256 do conteúdo. O cache (tamanho + mtime) só evita reler o mesmo arquivo — o valor é o conteúdo."""
    st = p.stat()
    chave = str(p.resolve())
    c = _cache_ler().get(chave)
    if c and c[0] == st.st_size and c[1] == st.st_mtime_ns:
        return c[2]
    h = hashlib.sha256()
    with p.open("rb") as f:
        for bloco in iter(lambda: f.read(4 << 20), b""):
            h.update(bloco)
    _cache_ler()[chave] = [st.st_size, st.st_mtime_ns, h.hexdigest()]
    return h.hexdigest()


def _sha_texto(obj) -> str:
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def _sha_roteiro(p: Path) -> str:
    """Só o que é FALADO e o que o CTA promete. Nota de status, tabela de extras ou checklist no roteiro.md
    não vencem o portão do roteiro (lição do Muntuza: um portão caro demais deixa de ser cumprido)."""
    try:
        spec = importlib.util.spec_from_file_location(
            "_parse_roteiro", PROJETO / ".claude/skills/roteiro-reels/scripts/parse_roteiro.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        rot, erros, _ = mod.parse(p.parent)
        if erros:
            raise ValueError(erros)
        return _sha_texto({
            "linhas": [[ln.get("id"), ln.get("fala")] for ln in rot.get("linhas", [])],
            **{k: rot.get(k) for k in ("cta_tipo", "cta_palavra", "material", "material_titulo")},
        })
    except Exception:  # roteiro que não passa no parser: vale o arquivo inteiro
        return "arquivo:" + sha_arquivo(p)


def _sha_pacote(p: Path) -> str:
    """Do pacote.json, só a escolha dos arquivos: é ela que diz que vídeo e que capa vão ao ar."""
    pac = json.loads(p.read_text(encoding="utf-8"))
    return _sha_texto({"arquivos": pac.get("arquivos"), "cta_palavra": pac.get("cta_palavra")})


def _sha_post(p: Path) -> str:
    post = json.loads(p.read_text(encoding="utf-8"))
    estavel = {}
    for k, campos in POST_ESTAVEL.items():
        v = post.get(k)
        estavel[k] = {c: (v or {}).get(c) for c in campos} if campos else v
    return _sha_texto(estavel)


def arquivos_da_area(alvo: Path, portao: str) -> dict[str, str]:
    """{caminho relativo ao alvo: impressão} de tudo o que o portão cobre hoje."""
    out: dict[str, str] = {}
    padroes = list(PORTOES[portao]["padroes"])
    if portao == "publicacao" and (alvo / "post.json").is_file():
        post = json.loads((alvo / "post.json").read_text(encoding="utf-8"))
        for rede in ("instagram", "facebook"):  # legenda com nome fora do padrão também é coberta
            nome = (post.get(rede) or {}).get("legenda_arquivo")
            if nome and nome not in padroes:
                padroes.append(nome)
    for padrao in padroes:
        for p in sorted(alvo.glob(padrao)):
            rel = p.relative_to(alvo).as_posix()
            partes = p.relative_to(alvo).parts
            if not p.is_file() or any(parte.startswith(".") or parte in IGNORAR for parte in partes):
                continue
            if portao == "roteiro" and rel == "roteiro.md":
                out[rel] = _sha_roteiro(p)
            elif portao == "publicacao" and rel == "post.json":
                out[rel] = _sha_post(p)
            elif portao == "publicacao" and rel == "pacote.json":
                out[rel] = _sha_pacote(p)
            else:
                out[rel] = sha_arquivo(p)
    _cache_gravar()
    return out


def impressao(arquivos: dict[str, str]) -> str:
    if not arquivos:
        return "vazio"
    return hashlib.sha256("\n".join(f"{k}:{v}" for k, v in sorted(arquivos.items())).encode()).hexdigest()[:12]


# ───────────────────────── livro de veredictos ─────────────────────────

def resolver_alvo(txt: str) -> Path:
    p = Path(txt)
    if not p.is_absolute():
        p = ROOT / p
    if not p.is_dir() and (ROOT / "videos" / txt).is_dir():
        p = ROOT / "videos" / txt
    if not p.is_dir():
        raise ErroPortao(f"alvo não existe: {txt}")
    return p.resolve()


def ler_livro(alvo: Path) -> dict:
    f = alvo / LIVRO
    if not f.exists():
        return {"versao": 1, "veredictos": []}
    return json.loads(f.read_text(encoding="utf-8"))


def gravar_livro(alvo: Path, livro: dict) -> None:
    tmp = alvo / (LIVRO + ".tmp")
    tmp.write_text(json.dumps(livro, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(alvo / LIVRO)


def veredictos(alvo: Path, portao: str) -> list[dict]:
    return [v for v in ler_livro(alvo)["veredictos"] if v["portao"] == portao]


def ciclo(vs: list[dict]) -> list[dict]:
    """Veredictos da volta atual: depois do último APROVADO ou da última decisão do Carlos."""
    for i in range(len(vs) - 1, -1, -1):
        if vs[i]["resultado"] == "APROVADO" or vs[i].get("decisao_carlos"):
            return vs[i + 1:] if vs[i]["resultado"] == "APROVADO" else vs[i:]
    return vs


def estado(alvo: Path, portao: str) -> dict:
    """status: aprovado · vencido · bloqueado · escalado · pendente · nao_se_aplica."""
    atuais = arquivos_da_area(alvo, portao)
    vs = veredictos(alvo, portao)
    ultimo = vs[-1] if vs else None
    out = {"portao": portao, "agente": PORTOES[portao]["agente"], "ultimo": ultimo, "arquivos": atuais,
           "impressao": impressao(atuais), "motivos": [], "volta": len(ciclo(vs))}
    if not atuais and not ultimo:
        out["status"] = "nao_se_aplica"
    elif not ultimo:
        out["status"] = "pendente"
        out["motivos"].append("o portão ainda não rodou")
    elif ultimo["resultado"] == "ESCALADO":
        out["status"] = "escalado"
        out["motivos"].append("3 voltas bloqueadas: aguarda decisão do Carlos")
    elif ultimo["resultado"] == "BLOQUEADO":
        out["status"] = "bloqueado"
        out["motivos"].append(f"BLOQUEADO em {ultimo['em']} (S0 {ultimo['achados']['S0']} · S1 {ultimo['achados']['S1']})")
    else:
        # Vale por CONTEÚDO, não por nome: uma cópia de um arquivo aprovado (capa-A.png → capa.png) continua
        # aprovada; arquivo apagado não vence; arquivo novo ou mudado vence.
        if portao in POR_CAMINHO:
            mudados = [k for k, v in atuais.items() if ultimo["arquivos"].get(k) != v]
            # por caminho, apagar também é mudança (uma migração ou um error.tsx que some depois do APROVADO)
            mudados += [f"{k} (apagado)" for k in ultimo["arquivos"] if k not in atuais]
        else:
            aprovados = set(ultimo["arquivos"].values())
            mudados = [k for k, v in atuais.items() if v not in aprovados]
        if mudados:
            out["status"] = "vencido"
            out["motivos"].append("mudou depois do APROVADO: " + ", ".join(mudados))
        else:
            out["status"] = "aprovado"
    return out


def registrar(alvo: Path, portao: str, resultado: str, imp: str, relatorio: str, s0: int, s1: int, s2: int,
              nota: str = "", decisao: str = "") -> dict:
    if portao not in PORTOES:
        raise ErroPortao(f"portão desconhecido: {portao} (há: {', '.join(PORTOES)})")
    resultado = resultado.upper()
    if resultado not in ("APROVADO", "BLOQUEADO"):
        raise ErroPortao("resultado tem de ser APROVADO ou BLOQUEADO (não há aprovado parcial)")
    if resultado == "APROVADO" and (s0 or s1):
        raise ErroPortao(f"APROVADO com S0={s0}/S1={s1} em aberto: S0 e S1 bloqueiam sempre")
    if resultado == "BLOQUEADO" and not (s0 or s1):
        raise ErroPortao("BLOQUEADO sem S0 nem S1: S2 não bloqueia — vai para o backlog e o veredicto é APROVADO")
    if portao not in portoes_do_alvo(alvo):
        raise ErroPortao(f"o portão {portao} não vale para {alvo.name} (aqui valem: {', '.join(portoes_do_alvo(alvo))})")
    atuais = arquivos_da_area(alvo, portao)
    agora_imp = impressao(atuais)
    if resultado == "APROVADO" and not atuais:
        raise ErroPortao(f"APROVADO sobre uma área vazia: não há arquivos de {portao} em {alvo.name} — nada a aprovar")
    if imp != agora_imp:
        raise ErroPortao(f"a área mudou enquanto o portão auditava (impressão {imp} → {agora_imp}): "
                         "o veredicto seria sobre um estado que já não existe. Rode o portão de novo.")
    rel = Path(relatorio)
    if not (rel if rel.is_absolute() else ROOT / rel).is_file() and not (alvo / rel).is_file():
        raise ErroPortao(f"relatório não encontrado: {relatorio} (o veredicto precisa do relatório inteiro)")
    vs = veredictos(alvo, portao)
    if vs and vs[-1]["resultado"] == "ESCALADO" and not decisao:
        raise ErroPortao("o portão está ESCALADO: só volta a rodar com --decisao-carlos (a opção que ele escolheu)")
    if decisao and not (vs and vs[-1]["resultado"] == "ESCALADO"):
        raise ErroPortao("--decisao-carlos só vale depois de um ESCALADO (não é atalho para zerar as voltas)")
    if portao == "imagem" and resultado == "APROVADO":
        cor = alvo / "edicao" / "cor" / "corte-cor.mp4"
        velhas = [c.name for c in sorted((alvo / "capa").glob("capa*.png"))
                  if cor.is_file() and c.stat().st_mtime < cor.stat().st_mtime]
        if velhas:
            raise ErroPortao("capa mais antiga que a cor atual (edicao/cor/corte-cor.mp4): " + ", ".join(velhas)
                             + " — foi tirada da cor anterior (o erro de 21/10). Refazer as capas pela cor atual "
                               "ou apagar as que não vão ser usadas; não se aprova capa velha.")
    volta = 1 if decisao else len(ciclo(vs)) + 1
    if resultado == "BLOQUEADO" and volta >= VOLTAS_MAX:
        resultado = "ESCALADO"
    v = {"portao": portao, "agente": PORTOES[portao]["agente"], "resultado": resultado, "impressao": agora_imp,
         "em": agora(), "volta": volta, "achados": {"S0": s0, "S1": s1, "S2": s2}, "relatorio": relatorio,
         "arquivos": atuais}
    if nota:
        v["nota"] = nota
    if decisao:
        v["decisao_carlos"] = decisao
    livro = ler_livro(alvo)
    livro["veredictos"].append(v)
    gravar_livro(alvo, livro)
    return v


def linha_veredicto(v: dict) -> str:
    sufixo = " — ESCALADO" if v["resultado"] == "ESCALADO" else ""
    res = "BLOQUEADO" if v["resultado"] == "ESCALADO" else v["resultado"]
    return f"PORTÃO-{v['portao'].upper()}: {res}{sufixo} — sobre {v['impressao']} (volta {v['volta']})"


# ───────────────────────── exigências ─────────────────────────

def portoes_do_alvo(alvo: Path) -> tuple[str, ...]:
    """Que portões valem para este alvo: vídeo, pasta da fila ou o sistema (painel/)."""
    if alvo.resolve() == (ROOT / "painel").resolve():
        return EXIGIDOS_SISTEMA
    if alvo.resolve().parent.name == "06-publicar":
        return ("publicacao",)
    return EXIGIDOS_PACOTE


def exigir(vdir: Path) -> list[str]:
    """Problemas que impedem o alvo de seguir: o pacote de sair de videos/<slug>/, ou o painel de ir ao Carlos.
    Lista vazia = pode seguir."""
    problemas = []
    for p in portoes_do_alvo(vdir):
        e = estado(vdir, p)
        if e["status"] == "aprovado" or (p in OPCIONAIS and e["status"] == "nao_se_aplica"):
            continue
        if e["status"] == "nao_se_aplica":
            problemas.append(f"portão {p}: não há arquivos da área ({', '.join(PORTOES[p]['padroes'])})")
        else:
            problemas.append(f"portão {p} ({e['agente']}) {e['status'].upper()}: {'; '.join(e['motivos'])}")
    return problemas


def _aprovados(vdir: Path, portao: str, papel: str = "") -> set[str]:
    e = estado(vdir, portao)
    if e["status"] != "aprovado":
        return set()
    return {v for k, v in e["ultimo"]["arquivos"].items() if k.startswith(papel)}


def selar(vdir: Path, pacote_dir: Path, arquivos: dict) -> dict:
    """Bloco `gauntlet` do pacote.json. `arquivos` = pacote.arquivos (caminhos relativos ao pacote)."""
    vdir, pacote_dir = vdir.resolve(), pacote_dir.resolve()
    problemas = exigir(vdir)
    if problemas:
        raise ErroPortao("o pacote não pode sair sem os portões aprovados:\n  - " + "\n  - ".join(problemas))
    shas, erros = {}, []
    for chave, valor in arquivos.items():
        if chave not in ORIGEM_DO_ARQUIVO or not valor:
            continue
        for rel in (valor if isinstance(valor, list) else [valor]):
            s = sha_arquivo(pacote_dir / rel)
            if s not in _aprovados(vdir, ORIGEM_DO_ARQUIVO[chave], PAPEL[chave]):
                erros.append(f"{rel}: não é nenhum dos arquivos que o portão {ORIGEM_DO_ARQUIVO[chave]} aprovou")
            shas[rel] = s
    _cache_gravar()
    if erros:
        raise ErroPortao("arquivo fora do que os portões viram:\n  - " + "\n  - ".join(erros))
    return {"versao": 1, "origem": vdir.relative_to(ROOT).as_posix(), "selado_em": agora(),
            "veredictos": {p: {"impressao": estado(vdir, p)["impressao"], "em": estado(vdir, p)["ultimo"]["em"]}
                           for p in EXIGIDOS_PACOTE if estado(vdir, p)["status"] == "aprovado"},
            "arquivos": shas}


def legado() -> set[str]:
    try:
        return set(json.loads(LEGADO.read_text(encoding="utf-8")).get("slugs") or [])
    except (OSError, ValueError):
        return set()


def conferir_pacote(pasta: Path, pac: dict, post: dict | None = None, publicacao: bool = False) -> list[str]:
    """Erros do GAUNTLET para um pacote na fila. Chamado pelo publicar.py (agendar e publicar)."""
    g = pac.get("gauntlet")
    if not g:
        if pasta.name in legado():
            return []
        return ["pacote sem selo GAUNTLET (montar de novo com scripts/montar_pacote.py, que só sela com os "
                "portões aprovados) — docs/gauntlet.md"]
    erros = []
    origem = (ROOT / g.get("origem", "")).resolve()
    if not (origem / LIVRO).exists():
        return [f"origem do selo sem livro de veredictos: {g.get('origem')}"]
    erros += [f"origem {g['origem']}: {p}" for p in exigir(origem)]
    arq = dict(pac.get("arquivos") or {})
    capa_post = ((post or {}).get("instagram") or {}).get("capa")
    if capa_post and capa_post != arq.get("capa"):
        arq["capa_post"] = capa_post
    mat_post = ((post or {}).get("material") or {}).get("arquivo")
    if mat_post and mat_post != arq.get("material"):
        arq["material_post"] = mat_post
    selados = set((g.get("arquivos") or {}).values())
    for chave, valor in arq.items():
        papel = {"capa_post": "capa", "material_post": "material"}.get(chave, chave)
        portao = ORIGEM_DO_ARQUIVO.get(papel)
        if not portao or not valor:
            continue
        for rel in (valor if isinstance(valor, list) else [valor]):
            f = pasta / rel
            if not f.is_file():
                continue  # arquivo em falta é erro do validar_pacote, não daqui
            # Vale o que o portão da origem aprova HOJE. Uma variante copiada da origem depois do selo (pasta -a do
            # par A/B) passa se for um arquivo aprovado; a capa velha numa fila cuja cor foi refeita, não.
            s = sha_arquivo(f)
            if s in _aprovados(origem, portao, PAPEL[papel]):
                continue
            if s not in selados:
                erros.append(f"{rel}: trocado depois do selo — não é nenhum arquivo que o portão {portao} aprovou")
            else:
                erros.append(f"{rel}: o portão {portao} da origem já não aprova este arquivo (a origem mudou depois do selo)")
    if publicacao:
        e = estado(pasta, "publicacao")
        if e["status"] != "aprovado":
            erros.append(f"portão publicacao (portao-publicacao) {e['status'].upper()}: {'; '.join(e['motivos'])}")
    _cache_gravar()
    return erros


# ───────────────────────── CLI ─────────────────────────

SINAL = {"aprovado": "✅", "vencido": "⌛", "bloqueado": "⛔", "escalado": "🔺", "pendente": "·", "nao_se_aplica": "—"}


def _sinais(alvo: Path, portoes: list[str]) -> str:
    return " · ".join(f"{p} {SINAL[estado(alvo, p)['status']]}" for p in portoes)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("impressao"); a.add_argument("alvo"); a.add_argument("portao", choices=PORTOES)
    a = sub.add_parser("registrar")
    a.add_argument("alvo"); a.add_argument("portao", choices=PORTOES); a.add_argument("resultado")
    a.add_argument("--impressao", required=True); a.add_argument("--relatorio", required=True)
    for s in ("--s0", "--s1", "--s2"):
        a.add_argument(s, type=int, required=True)
    a.add_argument("--nota", default=""); a.add_argument("--decisao-carlos", default="")
    a = sub.add_parser("estado"); a.add_argument("alvo", nargs="?")
    a = sub.add_parser("exigir"); a.add_argument("alvo")
    a = sub.add_parser("conferir-pacote"); a.add_argument("alvo"); a.add_argument("--publicacao", action="store_true")
    args = ap.parse_args()
    try:
        if args.cmd == "impressao":
            alvo = resolver_alvo(args.alvo)
            if args.portao not in portoes_do_alvo(alvo):
                raise ErroPortao(f"o portão {args.portao} não vale para {alvo.name} "
                                 f"(aqui valem: {', '.join(portoes_do_alvo(alvo))})")
            arqs = arquivos_da_area(alvo, args.portao)
            print(f"impressao {impressao(arqs)}  ({args.portao}, {len(arqs)} arquivos)")
            for k, v in sorted(arqs.items()):
                print(f"  {v[:12]}  {k}")
            return 0
        if args.cmd == "registrar":
            v = registrar(resolver_alvo(args.alvo), args.portao, args.resultado, args.impressao, args.relatorio,
                          args.s0, args.s1, args.s2, args.nota, args.decisao_carlos)
            print(linha_veredicto(v))
            return 0 if v["resultado"] == "APROVADO" else 2
        if args.cmd == "estado":
            if args.alvo:
                alvo = resolver_alvo(args.alvo)
                nomes = list(portoes_do_alvo(alvo))
                for p in nomes:
                    e = estado(alvo, p)
                    linha = f"{SINAL[e['status']]} {p:<11} {e['status']:<13} {e['agente']}"
                    if e["ultimo"]:
                        linha += f"  · último {e['ultimo']['resultado']} {e['ultimo']['em'][:16]} volta {e['ultimo']['volta']}"
                    print(linha)
                    for m in e["motivos"]:
                        print(f"      {m}")
            else:
                for d in sorted((ROOT / "videos").glob("*/")):
                    if not d.name.startswith("_"):
                        print(f"{d.name:<40} {_sinais(d, list(EXIGIDOS_PACOTE))}")
                for d in sorted((ROOT / "06-publicar").glob("*/")):
                    print(f"06-publicar/{d.name:<28} {_sinais(d, ['publicacao'])}"
                          + ("  (legado)" if d.name in legado() else ""))
                if (ROOT / "painel").is_dir():
                    print(f"{'painel (sistema)':<40} {_sinais(ROOT / 'painel', list(EXIGIDOS_SISTEMA))}")
            return 0
        if args.cmd == "exigir":
            problemas = exigir(resolver_alvo(args.alvo))
            for p in problemas:
                print(f"⛔ {p}")
            if not problemas:
                print("✅ todos os portões exigidos estão APROVADOS e válidos")
            return 1 if problemas else 0
        if args.cmd == "conferir-pacote":
            alvo = resolver_alvo(args.alvo)
            pac = json.loads((alvo / "pacote.json").read_text(encoding="utf-8"))
            post = json.loads((alvo / "post.json").read_text(encoding="utf-8")) if (alvo / "post.json").exists() else None
            erros = conferir_pacote(alvo, pac, post, publicacao=args.publicacao)
            for e in erros:
                print(f"⛔ {e}")
            if not erros:
                print("✅ selo GAUNTLET ok" + (" (legado, sem selo)" if not pac.get("gauntlet") else ""))
            return 1 if erros else 0
    except ErroPortao as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
