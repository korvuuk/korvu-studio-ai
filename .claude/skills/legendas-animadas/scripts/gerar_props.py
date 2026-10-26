#!/usr/bin/env python3
"""Gera as entradas do Remotion a partir da EDL (docs/contratos.md §4, §6, §7).

Saídas (em videos/<slug>/edicao/):
  - legendas.json    Caption[] (@remotion/captions) + linha/destaque
  - legendas.srt     2–4 palavras por cue, máx. 42 caracteres
  - reel-props.json  props da composição Remotion `Reel`, com "fps" = edl.json.fps (FPS_PROJETO, padrão 25)
  - remotion/*.mp4   proxies H.264 8-bit yuv420p (o Chrome do Remotion não lê H.264 4:2:2 10-bit), só quando
                     preciso: o corte sem cor (sem edicao/cor/corte-cor.mp4 ainda: 10-bit V-Log -> 8-bit com a LUT de
                     visualização nos trechos de câmera) e extras de câmera em V-Log sem <ID>-cor.mp4 (+ LUT).
e cria o symlink remotion/public/_render/<slug> → videos/<slug>/edicao.
Cenas extras (overlays `tipo: extra`): ganham `src` (caminho em public/, ex. `_render/<slug>/extras/E01.mp4`) e
`fonteLargura/fonteAltura`; `faltando: true` vira placeholder no Reel (o QA reprova).

Uso:
  uv run python .claude/skills/legendas-animadas/scripts/gerar_props.py videos/<slug>
      [--video edicao/cor/corte-cor.mp4] [--titulo-json caminho.json] [--sem-titulo] [--sem-cta]
      [--overlays edicao/extras-v2/overlays.json]

--overlays: arquivo {"overlays": [...]} (mesmo formato de edl.overlays `tipo: extra`, caminhos relativos à pasta do
vídeo) que SUBSTITUI os overlays `extra` da EDL — para refazer a camada de extras sem mexer no corte/edl.json
(Hinton v2, 15/10). Overlays com `enquadrar` ficam em `full` (preenchem a tela: ver remotion/src/lib/tipos.ts
`Enquadrar`); a regra "o formato manda no modo" não se aplica a eles.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parents[4]
REMOTION = RAIZ / "remotion"
PUBLIC_RENDER = REMOTION / "public" / "_render"
SCRIPTS_CORTE = RAIZ / ".claude" / "skills" / "corte-por-roteiro" / "scripts"


def _carregar_env() -> None:
    env = RAIZ / ".env"
    if not env.exists():
        return
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(env, override=False)


def _bin(env: str, padrao: str, nome: str) -> str:
    v = os.environ.get(env)
    if v:
        return v
    return padrao if Path(padrao).exists() else nome


_carregar_env()
FFMPEG = _bin("FFMPEG_BIN", "/Users/teste/bin/ffmpeg", "ffmpeg")
FFPROBE = _bin("FFPROBE_BIN", "/opt/homebrew/bin/ffprobe", "ffprobe")

MAX_PALAVRAS_SRT = 4
MAX_CHARS_SRT = 42
GAP_QUEBRA_S = 0.7
FIM_FRASE = re.compile(r"[.!?…][\"”')]*$")
PONTUACAO = ".,;:!?…\"“”'()"
RE_TEXTO_TELA = re.compile(r'TEXTO:\s*(?:"([^"]+)"|“([^”]+)”|([^|·]+))', re.IGNORECASE)
EXT_VIDEO = {".mp4", ".mov", ".m4v"}


def _corte():
    """common.py da skill corte-por-roteiro (FPS do projeto, LUT de visualização, perfis)."""
    if str(SCRIPTS_CORTE) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_CORTE))
    import common  # noqa: PLC0415
    return common


# ---------------------------------------------------------------------------
# utilidades
# ---------------------------------------------------------------------------
def normalizar(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^\w]+", "", s.lower())


def ler_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))


def escrever_json(p: Path, dados: Any) -> None:
    p.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ffprobe(arq: Path) -> dict:
    r = subprocess.run(
        [FFPROBE, "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(arq)],
        capture_output=True, text=True, check=True,
    )
    return json.loads(r.stdout)


def duracao_midia(arq: Path) -> float | None:
    try:
        return float(ffprobe(arq)["format"]["duration"])
    except Exception:
        return None


def stream_video(arq: Path) -> dict:
    try:
        return next((s for s in ffprobe(arq)["streams"] if s.get("codec_type") == "video"), {})
    except Exception:
        return {}


def dimensoes(arq: Path) -> tuple[int, int] | None:
    s = stream_video(arq)
    return (int(s["width"]), int(s["height"])) if s.get("width") else None


def compativel_remotion(arq: Path) -> bool:
    """H.264 8-bit 4:2:0 = decodificável pelo Chrome do Remotion (4:2:2 10-bit não é)."""
    s = stream_video(arq)
    return s.get("codec_name") == "h264" and s.get("pix_fmt") in ("yuv420p", "yuvj420p")


def detectar_recorte(arq: Path, inicio: float, fim: float) -> dict | None:
    """cropdetect na janela usada → área útil da gravação de tela (sem o pad). Só para EDLs antigas."""
    dur = max(1.0, min(6.0, fim - inicio))
    r = subprocess.run(
        [FFMPEG, "-hide_banner", "-nostats", "-ss", f"{max(0.0, inicio):.3f}", "-t", f"{dur:.3f}",
         "-i", str(arq), "-vf", "cropdetect=limit=24:round=2:reset=0", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    achados = re.findall(r"crop=(\d+):(\d+):(\d+):(\d+)", r.stderr)
    if not achados:
        return None
    w, h, x, y = map(int, achados[-1])
    return {"x": x, "y": y, "largura": w, "altura": h}


def sem_pontuacao(w: str) -> str:
    return w.strip(PONTUACAO)


# ---------------------------------------------------------------------------
# proxies 8-bit para o Remotion
# ---------------------------------------------------------------------------
def proxy_8bit(src: Path, dst: Path, vista: str, fps: float, motivo: str) -> Path:
    """src -> dst H.264 High 8-bit yuv420p bt709 no fps do projeto (+ `vista` = LUT de visualização).
    Refeito só se a fonte, a LUT ou o fps mudaram (carimbos em edicao/remotion/proxies.json)."""
    C = _corte()
    lut = C.lut_entrada_camera() if vista else None
    carimbo = {"src": str(src.resolve()), "src_mtime": src.stat().st_mtime, "fps": fps, "vista": bool(vista),
               "lut": str(lut) if lut else None, "lut_mtime": lut.stat().st_mtime if lut else None}
    carimbos_p = dst.parent / "proxies.json"
    carimbos = ler_json(carimbos_p) if carimbos_p.exists() else {}
    if dst.exists() and carimbos.get(dst.name) == carimbo:
        print(f"proxy: {dst.name} em dia ({motivo})")
        return dst
    dst.parent.mkdir(parents=True, exist_ok=True)
    vf = (f"{vista},scale=out_color_matrix=bt709:out_range=tv," if vista else "") + \
        "format=yuv420p,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv"
    cmd = [FFMPEG, "-hide_banner", "-nostdin", "-loglevel", "error", "-y", "-i", str(src),
           "-map", "0:v:0", "-map", "0:a?", "-vf", vf,
           "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-profile:v", "high", "-pix_fmt", "yuv420p",
           "-r", f"{fps:g}", "-fps_mode", "cfr", "-colorspace", "bt709", "-color_primaries", "bt709",
           "-color_trc", "bt709", "-color_range", "tv", "-c:a", "copy", "-movflags", "+faststart", str(dst)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"proxy falhou ({dst.name}):\n{r.stderr[-1500:]}")
    carimbos[dst.name] = carimbo
    escrever_json(carimbos_p, carimbos)
    print(f"proxy: {dst.name} ({motivo})")
    return dst


# ---------------------------------------------------------------------------
# §6 legendas
# ---------------------------------------------------------------------------
def limpar_legenda(texto: str) -> str:
    """Texto da legenda SEM pontuação nem caracteres especiais (pedido do Carlos, 2026-09-16: nada de aspas,
    vírgulas, pontos ou parênteses na tela). Mantém letras, números, acentos e o hífen dentro da palavra."""
    t = re.sub(r"[^\w\sÀ-ÿ-]", "", str(texto), flags=re.UNICODE)
    t = re.sub(r"(?<!\w)-|-(?!\w)", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def montar_legendas(palavras: list[dict]) -> list[dict]:
    validas = [p for p in palavras if limpar_legenda(p.get("texto", ""))]
    caps: list[dict] = []
    for i, p in enumerate(validas):
        ini = float(p["inicio"])
        fim = float(p["fim"])
        prox = validas[i + 1] if i + 1 < len(validas) else None
        if prox is not None and fim > float(prox["inicio"]):
            fim = max(ini + 0.01, float(prox["inicio"]))
        s = round(ini * 1000)
        e = max(s + 1, round(fim * 1000))
        conf = p.get("conf")
        caps.append({
            "text": " " + limpar_legenda(p["texto"]),
            "startMs": s,
            "endMs": e,
            "timestampMs": round((s + e) / 2),
            "confidence": float(conf) if conf is not None else 1,
            "linha": p.get("linha"),
            "destaque": bool(p.get("destaque", False)),
        })
    return caps


def _texto(cue: list[dict]) -> str:
    return " ".join(c["text"].strip() for c in cue)


def agrupar_srt(caps: list[dict]) -> list[list[dict]]:
    cues: list[list[dict]] = []
    atual: list[dict] = []
    for c in caps:
        w = c["text"].strip()
        if atual:
            ult = atual[-1]
            if (
                len(atual) >= MAX_PALAVRAS_SRT
                or len(_texto(atual)) + 1 + len(w) > MAX_CHARS_SRT
                or c.get("linha") != ult.get("linha")
                or (c["startMs"] - ult["endMs"]) / 1000 > GAP_QUEBRA_S
                or FIM_FRASE.search(ult["text"].strip())
            ):
                cues.append(atual)
                atual = []
        atual.append(c)
    if atual:
        cues.append(atual)

    # Evita cues de 1 palavra: junta com a anterior ou rouba 1 palavra dela.
    i = 1
    while i < len(cues):
        cue, ant = cues[i], cues[i - 1]
        mesma_linha = cue[0].get("linha") == ant[-1].get("linha")
        continua = not FIM_FRASE.search(ant[-1]["text"].strip())
        perto = (cue[0]["startMs"] - ant[-1]["endMs"]) / 1000 <= GAP_QUEBRA_S
        if len(cue) == 1 and mesma_linha and continua and perto:
            if len(ant) + 1 <= MAX_PALAVRAS_SRT and len(_texto(ant + cue)) <= MAX_CHARS_SRT:
                cues[i - 1] = ant + cue
                del cues[i]
                continue
            if len(ant) >= 3 and len(_texto(ant[-1:] + cue)) <= MAX_CHARS_SRT:
                cues[i] = ant[-1:] + cue
                cues[i - 1] = ant[:-1]
        i += 1
    return cues


def _srt_tempo(ms: int) -> str:
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def gerar_srt(cues: list[list[dict]]) -> str:
    blocos = []
    for i, cue in enumerate(cues):
        ini = cue[0]["startMs"]
        fim = max(cue[-1]["endMs"], ini + 400)
        if i + 1 < len(cues):
            fim = min(fim, cues[i + 1][0]["startMs"] - 1)
        blocos.append(f"{i + 1}\n{_srt_tempo(ini)} --> {_srt_tempo(max(fim, ini + 1))}\n{_texto(cue)}\n")
    return "\n".join(blocos)


# ---------------------------------------------------------------------------
# §7 título (heurística — o agente deve revisar)
# ---------------------------------------------------------------------------
def extrair_texto_tela(tela: str | None) -> str | None:
    if not tela:
        return None
    m = RE_TEXTO_TELA.search(tela)
    if not m:
        return None
    t = next(g for g in m.groups() if g)
    return t.strip().strip('"“”').strip() or None


def grafia_do_roteiro(texto: str, fala: str, destaques: list[str]) -> str:
    """'CHATGPT ERRADO?' → 'ChatGPT errado?' usando a grafia da fala."""
    if texto != texto.upper():
        return texto
    ref = {normalizar(w): sem_pontuacao(w) for w in fala.split() + list(destaques)}
    saida = []
    for w in texto.split():
        m = re.match(r"^(.*?)([.,;:!?…]*)$", w)
        base, pont = (m.group(1), m.group(2)) if m else (w, "")
        saida.append(ref.get(normalizar(base), base.lower()) + pont)
    s = " ".join(saida)
    return s[:1].upper() + s[1:]


def _escolher_corte(palavras: list[str]) -> int:
    n = len(palavras)
    candidatos = [i + 1 for i, w in enumerate(palavras[:-1]) if re.search(r"[,:;—–]$", w) and 2 <= i + 1 <= n - 2]
    alvo = n * 0.45
    if candidatos:
        return min(candidatos, key=lambda k: abs(k - alvo))
    return max(1, min(n - 2, round(alvo))) if n >= 3 else 1


def derivar_titulo(roteiro: dict | None, edl: dict, caps: list[dict]) -> dict | None:
    linhas = [l for l in (roteiro or {}).get("linhas", []) if not l.get("alternativa_de")]
    primeira_seg = (edl.get("segmentos") or [{}])[0].get("linha")
    hook = next((l for l in linhas if l.get("id") == primeira_seg and l.get("secao") == "hook"), None) \
        or next((l for l in linhas if l.get("secao") == "hook"), None)
    if hook:
        hid = hook.get("id")
        fala = hook.get("fala") or ""
        destaques = list(hook.get("destaques") or [])
        tela = hook.get("tela") or ""
    else:
        hid = caps[0].get("linha") if caps else None
        fala = " ".join(c["text"].strip() for c in caps if c.get("linha") == hid)
        destaques = [sem_pontuacao(c["text"].strip()) for c in caps if c.get("linha") == hid and c.get("destaque")]
        tela = ""
    if not fala.strip():
        return None

    texto_tela = extrair_texto_tela(tela)
    palavras = fala.split()
    if texto_tela:
        contexto, impacto = fala.strip(), grafia_do_roteiro(texto_tela, fala, destaques)
    else:
        k = _escolher_corte(palavras)
        contexto, impacto = " ".join(palavras[:k]), " ".join(palavras[k:])

    dnorm = {normalizar(d) for d in destaques}
    imp = impacto.split()
    idx_dest = [i for i, w in enumerate(imp) if normalizar(w) in dnorm]
    cinza = idx_dest[0] if idx_dest else max(0, len(imp) - 1)
    rabisco = sem_pontuacao(imp[idx_dest[-1]] if idx_dest else imp[-1]) if imp else None

    ctx = contexto.split()
    idx_sel = [i for i, w in enumerate(ctx) if normalizar(w) in dnorm]
    if idx_sel:
        ini = idx_sel[0]
        fim = ini
        while fim + 1 < len(ctx) and fim + 1 - ini < 3 and normalizar(ctx[fim + 1]) in dnorm:
            fim += 1
        selecao = " ".join(ctx[ini:fim + 1]) if fim > ini else " ".join(ctx[ini:ini + 2])
    else:
        selecao = " ".join(ctx[-2:]) if len(ctx) >= 2 else None

    fim_hook = max((c["endMs"] for c in caps if c.get("linha") == hid), default=3000) / 1000
    # Sem pontuação também no título (mesma regra das legendas, pedido do Carlos 2026-09-16). A limpeza vem DEPOIS
    # do corte contexto/impacto, que usa a vírgula do roteiro para achar a quebra, e não muda a contagem de palavras
    # (logo `cinza`, `rabisco` e `selecao` continuam válidos).
    return {
        "contexto": limpar_legenda(contexto),
        "impacto": limpar_legenda(impacto),
        "cinza": cinza,
        "rabisco": rabisco,
        "selecao": limpar_legenda(selecao) if selecao else None,
        "fim": round(min(4.5, max(2.5, fim_hook + 0.4)), 2),
        "posicao": "baixo",
        "origem": "heuristica (revise contexto/impacto/cinza/rabisco/selecao)",
    }


def carregar_titulo(caminho: Path) -> dict:
    t = ler_json(caminho)
    faltando = [k for k in ("contexto", "impacto", "cinza") if k not in t]
    if faltando:
        raise SystemExit(f"{caminho}: faltam campos do título: {', '.join(faltando)}")
    t.setdefault("origem", f"manual ({caminho.name})")
    for campo in ("contexto", "impacto", "selecao", "rabisco"):     # sem pontuação na tela, também no título à mão
        if t.get(campo):
            t[campo] = limpar_legenda(t[campo])
    return t


# ---------------------------------------------------------------------------
# §7 cta — cartão "comenta" + PALAVRA gigante (decisão do Carlos, 14/10)
# ---------------------------------------------------------------------------
CTA_SEGURA_S = 0.5            # o cartão fica até o fim da fala do CTA + isto (= brand.ts CTA.seguraSeg)
CTA_RODAPE_PADRAO = "que eu te mando no direct"
CTA_RODAPE_MAX_PALAVRAS = 7


def _rodape_cta(fala: str, palavra: str) -> str:
    """Linha pequena de baixo = o resto da fala depois da PALAVRA, até a 1.ª pontuação ("que eu te mando o link
    oficial"). Curto demais (< 2 palavras) ou longo demais (> 7) → "que eu te mando no direct"."""
    toks = fala.split()
    idx = next((i for i, w in enumerate(toks) if normalizar(w) == normalizar(palavra)), None)
    if idx is None:
        return CTA_RODAPE_PADRAO
    resto = " ".join(toks[idx + 1:])
    resto = re.split(r"[,.;:!?…—–]", resto, maxsplit=1)[0]
    resto = limpar_legenda(resto)
    n = len(resto.split())
    return resto if 2 <= n <= CTA_RODAPE_MAX_PALAVRAS else CTA_RODAPE_PADRAO


def derivar_cta(roteiro: dict | None, caps: list[dict], duracao: float) -> dict | None:
    """Janela do cartão do CTA (docs/contratos.md §7 `cta`).

    - palavra = `roteiro.json.cta_palavra` (sem ela, sem cartão);
    - linha = a 1.ª linha de seção `cta` (fora as alternativas) cuja fala contém a palavra (senão a 1.ª `cta`);
    - inicio = `startMs` da palavra "comenta"/"comente" dita nessa linha (legendas = palavras_saida, tempo da fala);
      sem "comenta" na linha → a própria PALAVRA; sem ela → a 1.ª palavra da linha;
    - fim = fim da última palavra da linha + 0,5 s, sem passar do início da próxima palavra falada (as legendas
      dentro da janela somem no Reel — a linha seguinte nunca pode sumir) nem da duração do vídeo.
    """
    palavra = str((roteiro or {}).get("cta_palavra") or "").strip()
    if not palavra:
        return None
    linhas = [l for l in (roteiro or {}).get("linhas", []) if l.get("secao") == "cta" and not l.get("alternativa_de")]
    if not linhas:
        return None
    alvo = normalizar(palavra)
    linha = next((l for l in linhas if alvo in {normalizar(w) for w in (l.get("fala") or "").split()}), linhas[0])
    lid = linha.get("id")
    idx = [i for i, c in enumerate(caps) if c.get("linha") == lid]
    if not idx:
        print(f"AVISO: linha do CTA {lid} não está no corte — sem cartão do CTA", file=sys.stderr)
        return None
    da_linha = [caps[i] for i in idx]
    ini_cap = next((c for c in da_linha if normalizar(c["text"]).startswith("coment")), None) \
        or next((c for c in da_linha if normalizar(c["text"]) == alvo), None) or da_linha[0]
    inicio = ini_cap["startMs"] / 1000
    fim_fala = da_linha[-1]["endMs"] / 1000
    fim = fim_fala + CTA_SEGURA_S
    prox = caps[idx[-1] + 1] if idx[-1] + 1 < len(caps) else None
    if prox is not None:
        fim = min(fim, max(fim_fala + 0.04, prox["startMs"] / 1000))
    fim = min(fim, duracao)
    if fim <= inicio:
        return None
    return {
        "palavra": limpar_legenda(palavra).upper(),
        "inicio": round(inicio, 3),
        "fim": round(fim, 3),
        "topo": "comenta",
        "rodape": _rodape_cta(linha.get("fala") or "", palavra),
        "linha": lid,
        "origem": "roteiro (cta_palavra + tempo do \"comenta\" falado)",
    }


def carregar_cta(caminho: Path, derivado: dict | None) -> dict | None:
    """`edicao/cta.json` (opcional) sobrescreve campos do derivado — ex.: {"rodape": "..."} ou {"inicio": 41.2}.
    `{"ativo": false}` tira o cartão."""
    manual = ler_json(caminho)
    if manual.get("ativo") is False:
        return None
    base = dict(derivado or {})
    base.update({k: v for k, v in manual.items() if k != "ativo"})
    if not all(k in base for k in ("palavra", "inicio", "fim")):
        raise SystemExit(f"{caminho}: o CTA precisa de palavra/inicio/fim (o roteiro não deu o derivado)")
    base["origem"] = f"manual ({caminho.name}) sobre {derivado.get('origem') if derivado else 'nada'}"
    return base


# ---------------------------------------------------------------------------
# mídia / symlink
# ---------------------------------------------------------------------------
def garantir_link(slug: str, edicao: Path) -> Path:
    """remotion/public/_render/<slug> → videos/<slug>/edicao (absoluto)."""
    PUBLIC_RENDER.mkdir(parents=True, exist_ok=True)
    link = PUBLIC_RENDER / slug
    alvo = edicao.resolve()
    if link.is_symlink():
        if link.resolve() == alvo:
            return link
        link.unlink()
    elif link.exists():
        raise SystemExit(f"{link} existe e não é symlink — remova à mão.")
    link.symlink_to(alvo, target_is_directory=True)
    return link


def escolher_video(video_dir: Path, edicao: Path, arg: str | None) -> Path:
    if arg:
        p = Path(arg)
        p = p if p.is_absolute() else video_dir / p
    else:
        p = next((edicao / c for c in ("cor/corte-cor.mp4", "corte.mp4") if (edicao / c).exists()),
                 edicao / "corte.mp4")
    if not p.exists():
        print(f"AVISO: vídeo não encontrado: {p} (o render vai falhar até ele existir)", file=sys.stderr)
    try:
        p.resolve().relative_to(edicao.resolve())
    except ValueError:
        raise SystemExit(f"O vídeo precisa estar dentro de {edicao} (é o que o symlink expõe): {p}")
    return p


def caminho_public(slug: str, edicao: Path, arq: Path) -> str:
    rel = arq.resolve().relative_to(edicao.resolve()).as_posix()
    return f"_render/{slug}/{rel}"


def video_para_remotion(video_dir: Path, edicao: Path, edl: dict, video: Path, fps: float) -> Path:
    """O corte sem cor (10-bit V-Log) vira proxy 8-bit com a LUT de visualização; outro vídeo incompatível
    vira proxy 8-bit sem LUT."""
    if not video.exists():
        return video
    if video.resolve() == (edicao / "corte.mp4").resolve():
        print("AVISO: sem edicao/cor/corte-cor.mp4 — o Reel usa o corte SEM cor (só a LUT de visualização). "
              "Rode /cor antes do render final.", file=sys.stderr)
        vista = _corte().filtro_vista_log(video_dir, edl)
        if vista or not compativel_remotion(video):
            return proxy_8bit(video, edicao / "remotion" / "corte.mp4", vista, fps,
                              "corte 10-bit/V-Log -> 8-bit" + (" + LUT de visualização" if vista else ""))
        return video
    if not compativel_remotion(video):
        return proxy_8bit(video, edicao / "remotion" / video.name, "", fps, "vídeo não é H.264 8-bit 4:2:0")
    return video


def midia_extra(video_dir: Path, edicao: Path, o: dict, extras_info: dict, fps: float) -> Path | None:
    """Arquivo que o Remotion vai ler para o extra (proxy 8-bit se for vídeo 10-bit / V-Log)."""
    arq_rel = o.get("arquivo")
    if not arq_rel or o.get("faltando"):
        return None
    arq = video_dir / arq_rel
    if not arq.exists():
        print(f"AVISO: extra {o.get('extra')}: {arq_rel} não existe — rode ingest.py + edl.py --recalcular",
              file=sys.stderr)
        return None
    if arq.suffix.lower() not in EXT_VIDEO:
        return arq
    C = _corte()
    perfil = (extras_info.get(o.get("extra")) or {}).get("perfil")
    em_log = C.eh_log(perfil) and not arq.stem.endswith("-cor")
    if em_log or not compativel_remotion(arq):
        vista = C.filtro_lut_camera() if em_log else ""
        return proxy_8bit(arq, edicao / "remotion" / f"{o['extra']}.mp4", vista, fps,
                          f"extra {o['extra']} " + ("V-Log -> 8-bit + LUT de visualização" if em_log else "-> 8-bit"))
    return arq


def segmentos_props(edl: dict) -> list[dict]:
    """Segmentos para o Reel. Com `edl.zoom_no_corte` o plano de zoom (zoom_pecas) JÁ foi aplicado pelo
    render_corte -> zoom null aqui (aplicar de novo = zoom em dobro). EDL antiga: o punch do segmento, com a origem
    do rosto (`zoom_origem`) se houver."""
    no_corte = bool(edl.get("zoom_no_corte"))
    out = []
    for s in edl.get("segmentos", []):
        z = None if no_corte else s.get("zoom")
        if z and s.get("zoom_origem"):
            z = {**z, "origem": s["zoom_origem"]}
        out.append({"saidaInicio": s["saida_inicio"], "saidaFim": s["saida_fim"], "zoom": z,
                    "layout": s.get("layout") or "full"})
    return out


# ---------------------------------------------------------------------------
# principal
# ---------------------------------------------------------------------------
LIMIAR_HORIZONTAL = 1.2      # largura/altura a partir da qual a mídia é "deitada" (formato YouTube)


def modo_pelo_formato(dims: tuple[int, int], modo_atual: str | None) -> str | None:
    """Regra do Carlos (2026-09-17): o FORMATO do arquivo manda no layout.

    Deitado (16:9, "formato YouTube") → `split`: extra em cima, ele embaixo.
    Em pé (vertical) → `full`: ocupa a tela toda até a cena sair.
    `card` é escolha explícita de layout e não é trocada.
    """
    if modo_atual == "card":
        return None
    largura, altura = dims
    if largura <= 0 or altura <= 0:
        return None
    return "split" if largura / altura >= LIMIAR_HORIZONTAL else "full"


def carregar_overlays_extras(video_dir: Path, caminho: Path) -> list[dict]:
    """--overlays: lista de overlays `tipo: extra` que substitui os da EDL (o edl.json não muda)."""
    p = caminho if caminho.is_absolute() else video_dir / caminho
    dados = ler_json(p)
    lista = dados.get("overlays") if isinstance(dados, dict) else dados
    if not isinstance(lista, list) or not lista:
        raise SystemExit(f"{p}: esperado {{\"overlays\": [...]}} com pelo menos um overlay")
    for i, o in enumerate(lista):
        for k in ("extra", "arquivo", "saida_inicio", "saida_fim"):
            if k not in o:
                raise SystemExit(f"{p}: overlay {i} sem '{k}'")
        o.setdefault("tipo", "extra")
        o.setdefault("modo", "full" if o.get("enquadrar") else "split")
        o.setdefault("som", False)
        o.setdefault("faltando", False)
    print(f"overlays: {len(lista)} extras de {p.name} (substituem os extras da EDL)")
    return lista


def gerar(video_dir: Path, video_arg: str | None, titulo_json: Path | None, sem_titulo: bool,
          mostrar_faltando: bool = False, sem_cta: bool = False, overlays_json: Path | None = None,
          sem_legendas: bool = False) -> dict:
    video_dir = video_dir.resolve()
    edicao = video_dir / "edicao"
    edl_p = edicao / "edl.json"
    if not edl_p.exists():
        raise SystemExit(f"EDL não encontrada: {edl_p}")
    edl = ler_json(edl_p)
    rot_p = video_dir / "roteiro.json"
    roteiro = ler_json(rot_p) if rot_p.exists() else None
    fontes_p = edicao / "fontes.json"
    extras_info = (ler_json(fontes_p).get("extras") or {}) if fontes_p.exists() else {}
    slug = edl.get("slug") or video_dir.name
    fps_c = float(edl.get("fps") or _corte().FPS)
    fps: float | int = int(fps_c) if fps_c.is_integer() else fps_c
    if abs(fps_c - float(_corte().FPS)) > 0.01:
        print(f"AVISO: edl.json está a {fps_c:g} fps e FPS_PROJETO a {_corte().FPS} — o Reel sai a {fps_c:g} "
              "(rode ingest/edl de novo se o projeto mudou de fps)", file=sys.stderr)

    caps = montar_legendas(edl.get("palavras_saida", []))
    cues = agrupar_srt(caps)

    video = escolher_video(video_dir, edicao, video_arg)
    dur_edl = edl.get("duracao_saida")
    dur_vid = duracao_midia(video) if video.exists() else None
    if dur_edl and dur_vid and abs(dur_edl - dur_vid) > 0.1:
        print(f"AVISO: duração EDL {dur_edl:.2f}s ≠ vídeo {dur_vid:.2f}s", file=sys.stderr)
    duracao = float(dur_edl or dur_vid or (caps[-1]["endMs"] / 1000 + 0.5 if caps else 1))
    video_remotion = video_para_remotion(video_dir, edicao, edl, video, fps)

    linhas_rot = {l["id"]: l for l in (roteiro or {}).get("linhas", [])}
    overlays, faltando = [], []
    fonte_overlays = edl.get("overlays", [])
    if overlays_json:
        fonte_overlays = [o for o in fonte_overlays if o.get("tipo") != "extra"] + \
            carregar_overlays_extras(video_dir, overlays_json)
    for o in fonte_overlays:
        o = dict(o)
        if o.get("texto"):                     # texto de tela: sem pontuação, como as legendas e o título
            o["texto"] = limpar_legenda(o["texto"])
        if o.get("tipo") == "extra":
            arq = midia_extra(video_dir, edicao, o, extras_info, fps)
            if arq is not None:
                o["src"] = caminho_public(slug, edicao, arq)
                dims = dimensoes(arq)
                if dims:
                    o["fonteLargura"], o["fonteAltura"] = dims
                    novo = None if (o.get("enquadrar") or o.get("modo") in ("pilha", "solo")) \
                        else modo_pelo_formato(dims, o.get("modo"))
                    if novo and novo != o.get("modo"):
                        print(f"extra {o['extra']}: {dims[0]}x{dims[1]} → modo {novo} "
                              f"(roteiro dizia {o.get('modo')}; quem manda é o formato)")
                        o["modo"] = novo
            elif o.get("extra_tipo") != "animacao" or o.get("faltando"):
                o["faltando"] = True
            if o.get("faltando"):
                faltando.append(o.get("extra"))
            for i, item in enumerate(o.get("pilha") or []):   # modo "pilha": cada faixa tem a sua mídia
                item_o = {"arquivo": item.get("arquivo"), "extra": f"{o.get('extra')}-{item.get('id') or i}",
                          "extra_tipo": item.get("extra_tipo", "imagem"), "faltando": False}
                arq_i = midia_extra(video_dir, edicao, item_o, extras_info, fps)
                if arq_i is None:
                    print(f"AVISO: pilha {o.get('extra')}: faixa {i} sem arquivo ({item.get('arquivo')})",
                          file=sys.stderr)
                    continue
                item["src"] = caminho_public(slug, edicao, arq_i)
                d = dimensoes(arq_i)
                if d:
                    item["fonteLargura"], item["fonteAltura"] = d
        elif o.get("tipo") == "tela":          # EDL antiga (tela-NN em edicao/fontes/)
            fonte_rel = (edl.get("fontes") or {}).get(o.get("fonte", ""))
            if fonte_rel:
                arq = video_dir / fonte_rel
                if arq.exists():
                    rec = detectar_recorte(arq, float(o.get("in", 0)), float(o.get("out", 0)))
                    dims = dimensoes(arq)
                    if not compativel_remotion(arq):
                        arq = proxy_8bit(arq, edicao / "remotion" / arq.name, "", fps, "tela 10-bit -> 8-bit")
                    if dims:
                        o["fonteLargura"], o["fonteAltura"] = dims
                    if rec and dims and (rec["largura"] < dims[0] or rec["altura"] < dims[1]):
                        o["recorte"] = rec
                o["src"] = caminho_public(slug, edicao, arq)
        elif o.get("tipo") == "animacao":      # EDL antiga
            anim = (linhas_rot.get(o.get("linha", "")) or {}).get("animacao") or {}
            o.setdefault("descricao", anim.get("descricao"))
        overlays.append(o)

    segmentos = segmentos_props(edl)
    if edl.get("zoom_no_corte"):
        print("zoom: já aplicado no corte (edl.json zoom_no_corte) — o Reel não aplica o zoom dos segmentos")

    titulo = None
    if not sem_titulo:
        explicito = titulo_json or (edicao / "titulo.json")
        titulo = carregar_titulo(explicito) if explicito.exists() else derivar_titulo(roteiro, edl, caps)

    cta = None
    if not sem_cta:
        cta = derivar_cta(roteiro, caps, duracao)
        if (edicao / "cta.json").exists():
            cta = carregar_cta(edicao / "cta.json", cta)

    props = {
        "video": caminho_public(slug, edicao, video_remotion),
        "duracaoSeg": round(duracao, 3),
        "fps": fps,
        "legendas": caps,
        # 21/10 (Carlos): formato rápido de comandos sem legenda karaokê — título e CTA continuam (precisam de `legendas`)
        "mostrarLegendas": not sem_legendas,
        "overlays": overlays,
        "segmentos": segmentos,
        "zoomNoCorte": bool(edl.get("zoom_no_corte")),
        "titulo": titulo,
        "cta": cta,
        # Nenhum vídeo que chega ao Carlos leva etiqueta de extra faltando (regra dele, 2026-09-17):
        # o padrão é NÃO mostrar; `--mostrar-faltando` é só depuração. O QA continua reprovando.
        "mostrarFaltando": mostrar_faltando,
        "estiloLegenda": "selecao",
        "legendaPosicao": "baixo",
    }

    escrever_json(edicao / "legendas.json", caps)
    (edicao / "legendas.srt").write_text(gerar_srt(cues), encoding="utf-8")
    escrever_json(edicao / "reel-props.json", props)
    link = garantir_link(slug, edicao)

    print(f"slug: {slug}")
    print(f"legendas: {len(caps)} palavras → {edicao / 'legendas.json'}")
    print(f"srt: {len(cues)} cues → {edicao / 'legendas.srt'}")
    print(f"props: {edicao / 'reel-props.json'} (vídeo: {props['video']}, {props['duracaoSeg']}s, {fps} fps)")
    ex = [o for o in overlays if o.get("tipo") == "extra"]
    if ex:
        print("extras: " + " · ".join(f"{o['extra']} {o.get('modo')}" + (" FALTANDO" if o.get("faltando") else "")
                                       for o in ex))
    if faltando:
        print(f"AVISO: extras faltando ({', '.join(faltando)}): placeholder no vídeo — o QA reprova até chegarem.",
              file=sys.stderr)
    print(f"symlink: {link} → {edicao}")
    if titulo:
        print(f"título ({titulo.get('origem')}):")
        print(f"  contexto: {titulo['contexto']!r}  seleção: {titulo.get('selecao')!r}")
        print(f"  impacto:  {titulo['impacto']!r}  cinza={titulo['cinza']}  rabisco={titulo.get('rabisco')!r}")
    if cta:
        print(f"CTA: {cta['palavra']!r} {cta['inicio']:.2f}–{cta['fim']:.2f}s (linha {cta.get('linha')}) "
              f"rodapé {cta.get('rodape')!r}")
    return props


def main() -> None:
    ap = argparse.ArgumentParser(description="EDL → legendas.json/.srt + reel-props.json (+ symlink, proxies 8-bit)")
    ap.add_argument("video_dir", type=Path, help="videos/<slug>")
    ap.add_argument("--video", help="vídeo base relativo à pasta do vídeo (padrão: edicao/cor/corte-cor.mp4 → edicao/corte.mp4)")
    ap.add_argument("--titulo-json", type=Path, help="título explícito {contexto, impacto, cinza, rabisco, selecao}")
    ap.add_argument("--sem-titulo", action="store_true", help="não coloca título no hook")
    ap.add_argument("--sem-cta", action="store_true", help="não coloca o cartão do CTA (comenta + PALAVRA)")
    ap.add_argument("--mostrar-faltando", action="store_true",
                    help="só para depuração: desenha a etiqueta 'EXTRA Exx FALTANDO' (padrão: não mostrar)")
    ap.add_argument("--sem-legendas", action="store_true",
                    help="não desenha a legenda karaokê (formato rápido de comandos, 21/10); título e CTA ficam")
    ap.add_argument("--overlays", type=Path,
                    help="JSON {overlays:[...]} que substitui os extras da EDL (relativo à pasta do vídeo)")
    a = ap.parse_args()
    gerar(a.video_dir, a.video, a.titulo_json, a.sem_titulo, a.mostrar_faltando, a.sem_cta, a.overlays, a.sem_legendas)


if __name__ == "__main__":
    main()
