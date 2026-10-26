"""Transcrição com timestamps por palavra -> edicao/transcricao.json (contrato §2)

uso: uv run python transcribe.py <video_dir> [--engine scribe|mlx|whisperx] [--fontes camera-01,...]
                                 [--incluir-tela] [--force]

Engines:
  scribe   ElevenLabs Speech-to-Text (Scribe v2) — padrão se ELEVENLABS_API_KEY estiver definido.
           Resposta bruta em edicao/raw/<fonte>.scribe.json (cache).
  mlx      mlx-whisper local (mlx-community/whisper-large-v3-turbo) — padrão sem API key.
           Precisa do extra: uv run --extra local ...
  whisperx opcional (não instalado por padrão).
"""
from __future__ import annotations

import argparse
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (edicao, escrever_json, fontes_de_edicao, ler_json, log, mean, ordem_fontes,  # noqa: E402
                    refinar_palavras, resolver_video_dir, rel)

SCRIBE_MODEL = os.environ.get("SCRIBE_MODEL", "scribe_v2")
# diarização (método ChatGPT-monitor: IA no celular + Carlos): no máximo 2 vozes; 0 = deixar o Scribe decidir
SCRIBE_NUM_SPEAKERS = int(os.environ.get("SCRIBE_NUM_SPEAKERS", "2") or 0)
MLX_MODEL = os.environ.get("MLX_WHISPER_MODEL", "mlx-community/whisper-large-v3-turbo")
# prompt com hesitações: incentiva o Whisper a transcrever muletas/recomeços (verbatim)
# (sem "de novo" no prompt: uma alucinação desse separador dividiria takes)
PROMPT_VERBATIM = "Então, é... tipo, hum, eu vou, eu vou falar. Né? Ahn."

EVENTOS = [
    ("respiracao", ("breath", "inhal", "exhal", "sigh", "respira", "suspir")),
    ("riso", ("laugh", "chuckle", "giggle", "riso", "risada", "ri)")),
    ("tosse", ("cough", "throat", "tosse", "pigarro", "sneeze", "espirro")),
    ("musica", ("music", "música", "musica", "singing")),
    ("ruido", ("noise", "ruído", "ruido", "click", "clap", "bang", "knock", "footstep", "beep", "static")),
]


def engine_padrao() -> str:
    return "scribe" if os.environ.get("ELEVENLABS_API_KEY") else "mlx"


def tipo_evento(txt: str) -> str:
    t = txt.lower()
    for tipo, chaves in EVENTOS:
        if any(c in t for c in chaves):
            return tipo
    return "outro"


def _cache_valido(cache: Path, wav: Path) -> bool:
    return cache.exists() and cache.stat().st_mtime >= wav.stat().st_mtime


# ---------------------------------------------------------------- engines
def _scribe(wav: Path, cache: Path, force: bool, keyterms: list[str] | None):
    """Scribe com diarização (diarize=True, num_speakers=SCRIBE_NUM_SPEAKERS): o speaker_id de cada palavra vira
    `locutor_bruto` (camada A do locutores.py)."""
    import json
    pedido = {"diarize": True, "num_speakers": SCRIBE_NUM_SPEAKERS or None}
    raw = None
    if not force and _cache_valido(cache, wav):
        raw = json.loads(cache.read_text(encoding="utf-8"))
        if raw.get("_pedido") != pedido:
            if os.environ.get("ELEVENLABS_API_KEY"):
                print("   cache do Scribe sem diarização: chamando de novo (diarize=True)", flush=True)
                raw = None
            else:
                print("   [AVISO] cache do Scribe sem diarização e sem ELEVENLABS_API_KEY: o locutores.py usa só a "
                      "análise local", flush=True)
    if raw is None:
        key = os.environ.get("ELEVENLABS_API_KEY")
        if not key:
            sys.exit("[ERRO] ELEVENLABS_API_KEY não definido (use --engine mlx para transcrever localmente)")
        from elevenlabs.client import ElevenLabs
        client = ElevenLabs(api_key=key)
        kw = dict(model_id=SCRIBE_MODEL, language_code="por", timestamps_granularity="word",
                  tag_audio_events=True, diarize=True)
        if SCRIBE_NUM_SPEAKERS:
            kw["num_speakers"] = SCRIBE_NUM_SPEAKERS
        if keyterms:
            kw["keyterms"] = keyterms[:100]
        with open(wav, "rb") as f:
            resp = client.speech_to_text.convert(file=f, **kw)
        raw = resp.model_dump() if hasattr(resp, "model_dump") else resp.dict()
        raw["_pedido"] = pedido
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(raw, ensure_ascii=False, indent=1), encoding="utf-8")
    if "words" not in raw and raw.get("transcripts"):      # resposta multicanal
        raw = raw["transcripts"][0]
    palavras, eventos = [], []
    for w in raw.get("words", []) or []:
        tp, txt = w.get("type"), (w.get("text") or "").strip()
        if w.get("start") is None or not txt:
            continue
        ini, fim = float(w["start"]), float(w.get("end") or w["start"])
        if tp == "word":
            lp = w.get("logprob")
            conf = math.exp(lp) if lp is not None else 1.0
            p = {"texto": txt, "inicio": ini, "fim": fim, "conf": conf}
            if w.get("speaker_id"):
                p["locutor_bruto"] = str(w["speaker_id"])
            palavras.append(p)
        elif tp == "audio_event":
            eventos.append({"tipo": tipo_evento(txt), "inicio": ini, "fim": fim, "texto": txt})
    return palavras, eventos


# ---------------------------------------------------------------- lacunas (fala sem palavra)
LACUNA_MIN = 0.5            # s — trecho com fala e sem nenhuma palavra do ASR que é re-transcrito sozinho...
LACUNA_VOZ_MIN = 0.25       # ...se tiver pelo menos isso de quadros vozeados (respiração/ruído não conta)
LACUNA_PAD = 0.25           # s de margem no recorte
PALAVRA_COBRE_MAX = 1.2     # s — uma palavra do ASR "cobre" no máximo isso (palavras esticadas sobre a fala seguinte)
VERSAO_CACHE_MLX = 2        # 2 = com preenchimento de lacunas


def lacunas_de_fala(wav: Path, palavras: list[dict]) -> list[tuple[float, float]]:
    """Trechos com fala (energia + quadros vozeados) sem nenhuma palavra do ASR. O Whisper pula a repetição idêntica
    de uma frase dita logo antes — no método ChatGPT-monitor (a IA lê, o Carlos repete) ele "engole" o take."""
    import numpy as np
    from locutores import quadros
    Q = quadros(str(wav))
    t = Q["t"]
    coberto = np.zeros(len(t), bool)
    for w in palavras:
        a, b = float(w["inicio"]), min(float(w["fim"]), float(w["inicio"]) + PALAVRA_COBRE_MAX)
        coberto[np.searchsorted(t, a - 0.05):np.searchsorted(t, b + 0.05)] = True
    idx = np.where(Q["ativo"] & ~coberto)[0]
    if not len(idx):
        return []
    regs = []
    for g in np.split(idx, np.where(np.diff(idx) > 30)[0] + 1):      # buracos < 0,3 s = mesmo trecho
        a, b = float(t[g[0]]), float(t[g[-1]])
        if b - a >= LACUNA_MIN and Q["vozeado"][g].sum() * 0.01 >= LACUNA_VOZ_MIN:
            regs.append((a, b))
    return regs


def preencher_lacunas(wav: Path, palavras: list[dict], transcrever_trecho) -> tuple[list[dict], int]:
    """Re-transcreve sozinho cada trecho de `lacunas_de_fala` e junta as palavras (tempo da fonte). Palavra antiga
    esticada por cima de uma nova é aparada. -> (palavras, nº de lacunas preenchidas)."""
    import tempfile
    import soundfile as sf
    regs = lacunas_de_fala(wav, palavras)
    if not regs:
        return palavras, 0
    x, sr = sf.read(str(wav), dtype="float32")
    novas, n = [], 0
    with tempfile.TemporaryDirectory() as td:
        for a, b in regs:
            a0, b0 = max(0.0, a - LACUNA_PAD), min(len(x) / sr, b + LACUNA_PAD)
            p = Path(td) / f"lacuna-{a0:.2f}.wav"
            sf.write(p, x[int(a0 * sr):int(b0 * sr)], sr)
            ws = [dict(w, inicio=w["inicio"] + a0, fim=w["fim"] + a0) for w in transcrever_trecho(p)]
            ws = [w for w in ws if a - 0.1 <= (w["inicio"] + w["fim"]) / 2 <= b + 0.1]
            print(f"   lacuna {a:.2f}–{b:.2f}s (fala sem palavra no ASR) re-transcrita: +{len(ws)} palavra(s) "
                  f"\"{' '.join(w['texto'] for w in ws)[:70]}\"", flush=True)
            novas += ws
            n += bool(ws)
    todas = sorted(palavras + novas, key=lambda w: w["inicio"])
    for k in range(len(todas) - 1):
        if todas[k + 1]["inicio"] > todas[k]["inicio"] and todas[k]["fim"] > todas[k + 1]["inicio"]:
            todas[k]["fim"] = max(todas[k]["inicio"] + 0.02, todas[k + 1]["inicio"])
    return todas, n


def _palavras_mlx(res: dict) -> list[dict]:
    palavras = []
    for seg in res.get("segments", []):
        for w in seg.get("words", []) or []:
            txt = (w.get("word") or "").strip()
            if not txt:
                continue
            palavras.append({"texto": txt, "inicio": float(w["start"]), "fim": float(w["end"]),
                             "conf": float(w.get("probability", 1.0))})
    return palavras


def _mlx(wav: Path, cache: Path, force: bool, prompt: str | None):
    import json
    if not force and _cache_valido(cache, wav):
        c = json.loads(cache.read_text(encoding="utf-8"))
        if c.get("versao") == VERSAO_CACHE_MLX:
            return c["palavras"], []
    try:
        import mlx_whisper
    except ImportError:
        sys.exit("[ERRO] mlx-whisper não instalado. Rode: uv sync --extra local  (ou uv add --optional local mlx-whisper)")
    kw = dict(path_or_hf_repo=MLX_MODEL, language="pt", word_timestamps=True,
              condition_on_previous_text=False,       # não "pula" takes repetidos entre janelas
              initial_prompt=prompt or PROMPT_VERBATIM, no_speech_threshold=0.6, verbose=None)
    res = mlx_whisper.transcribe(str(wav), hallucination_silence_threshold=2.0, **kw)
    # dentro da mesma janela o Whisper ainda pula a repetição idêntica (IA lê -> Carlos repete): re-transcreve
    # sozinho cada trecho com fala e sem palavra
    palavras, n_lac = preencher_lacunas(wav, _palavras_mlx(res),
                                        lambda p: _palavras_mlx(mlx_whisper.transcribe(str(p), **kw)))
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps({"engine": "mlx", "modelo": MLX_MODEL, "versao": VERSAO_CACHE_MLX, "lacunas": n_lac,
                                 "palavras": palavras, "texto": res.get("text", "")}, ensure_ascii=False, indent=1),
                     encoding="utf-8")
    return palavras, []


def _whisperx(wav: Path, cache: Path, force: bool):
    import json
    if not force and _cache_valido(cache, wav):
        return json.loads(cache.read_text(encoding="utf-8"))["palavras"], []
    try:
        import whisperx
    except ImportError:
        sys.exit("[ERRO] whisperx não está instalado neste projeto. Use --engine mlx ou scribe "
                 "(ou instale: uv add --optional local whisperx).")
    dev = os.environ.get("WHISPERX_DEVICE", "cpu")
    model = whisperx.load_model(os.environ.get("WHISPERX_MODEL", "large-v3"), dev, compute_type="int8", language="pt")
    audio = whisperx.load_audio(str(wav))
    r = model.transcribe(audio, batch_size=8, language="pt")
    am, meta = whisperx.load_align_model(language_code="pt", device=dev)
    r = whisperx.align(r["segments"], am, meta, audio, dev, return_char_alignments=False)
    palavras, ultimo = [], 0.0
    for w in r.get("word_segments", []):
        ini = w.get("start", ultimo)
        fim = w.get("end", ini + 0.2)
        ultimo = fim
        palavras.append({"texto": w["word"].strip(), "inicio": float(ini), "fim": float(fim),
                         "conf": float(w.get("score", 0.8))})
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps({"engine": "whisperx", "palavras": palavras}, ensure_ascii=False), encoding="utf-8")
    return palavras, []


def transcrever_wav(wav: Path, engine: str, cache: Path, force: bool = False,
                    prompt: str | None = None, keyterms: list[str] | None = None, refinar: bool = True):
    """-> (palavras, eventos) com tempos em segundos, já limpos/monótonos e (por padrão)
    com bordas ajustadas à energia do áudio (common.refinar_palavras)."""
    if engine == "scribe":
        palavras, eventos = _scribe(wav, cache, force, keyterms)
    elif engine == "mlx":
        palavras, eventos = _mlx(wav, cache, force, prompt)
    elif engine == "whisperx":
        palavras, eventos = _whisperx(wav, cache, force)
    else:
        sys.exit(f"[ERRO] engine desconhecida: {engine}")
    palavras.sort(key=lambda w: w["inicio"])
    limpas, ultimo_fim = [], 0.0
    for w in palavras:
        ini = max(float(w["inicio"]), 0.0)
        fim = max(float(w["fim"]), ini + 0.02)
        limpas.append({"texto": w["texto"], "inicio": round(ini, 3), "fim": round(fim, 3),
                       "conf": round(float(w.get("conf", 1.0)), 3),
                       **({"locutor_bruto": w["locutor_bruto"]} if w.get("locutor_bruto") else {})})
        ultimo_fim = max(ultimo_fim, fim)
    if refinar and limpas:
        limpas = refinar_palavras(limpas, str(wav))
        n0 = len(limpas)
        limpas = [w for w in limpas if not w.pop("silencio", False)]
        if len(limpas) < n0:
            print(f"   {n0 - len(limpas)} palavra(s) em silêncio total descartada(s) (alucinação do ASR)", flush=True)
    return limpas, [{"tipo": e["tipo"], "inicio": round(e["inicio"], 3), "fim": round(e["fim"], 3)} for e in eventos]


def vocabulario_roteiro(vd: Path) -> list[str]:
    """Termos do roteiro (destaques + palavras com maiúscula no meio da frase)."""
    r = ler_json(vd / "roteiro.json", padrao={})
    termos = []
    for l in r.get("linhas", []):
        termos += l.get("destaques") or []
        ws = (l.get("fala") or "").split()
        termos += [w.strip(".,!?;:\"'") for w in ws[1:] if w[:1].isupper()]
    vistos, out = set(), []
    for t in termos:
        if t and t.lower() not in vistos:
            vistos.add(t.lower())
            out.append(t)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video_dir")
    ap.add_argument("--engine", choices=["scribe", "mlx", "whisperx"], default=None)
    ap.add_argument("--fontes", default=None, help="lista separada por vírgula (padrão: câmera/celular)")
    ap.add_argument("--incluir-tela", action="store_true", help="também transcreve fontes tela-*")
    ap.add_argument("--keyterms", action="store_true", help="(scribe) envia termos do roteiro como keyterms")
    ap.add_argument("--force", action="store_true", help="ignora cache em edicao/raw/")
    ap.add_argument("--sem-refino", action="store_true", help="não ajusta bordas das palavras pela energia")
    args = ap.parse_args()
    vd = resolver_video_dir(args.video_dir)
    ed = edicao(vd)
    todas_fontes = ler_json(ed / "fontes.json").get("fontes", {})
    fontes = fontes_de_edicao(todas_fontes)          # amostras de cor (*-cor.*) nunca são transcritas
    engine = args.engine or engine_padrao()
    if args.fontes:
        sel = [f.strip() for f in args.fontes.split(",") if f.strip()]
        amostras = [f for f in sel if f in todas_fontes and f not in fontes]
        if amostras:
            log(f"   [AVISO] amostra(s) de cor ignorada(s): {amostras}")
            sel = [f for f in sel if f not in amostras]
        faltam = [f for f in sel if f not in fontes]
        if faltam:
            sys.exit(f"[ERRO] fontes inexistentes: {faltam} (disponíveis: {list(fontes)})")
    else:
        tipos = {"camera", "celular"} | ({"tela"} if args.incluir_tela else set())
        sel = [f for f in ordem_fontes(fontes) if fontes[f]["tipo"] in tipos]
    if not sel:
        sys.exit("[ERRO] nenhuma fonte para transcrever")

    tj = ed / "transcricao.json"
    anterior = ler_json(tj, padrao={})
    manter = {}
    if anterior and args.fontes:
        for w in anterior.get("palavras", []):
            if w["fonte"] not in sel:
                manter.setdefault(w["fonte"], {"p": [], "e": []})["p"].append(w)
        for e in anterior.get("eventos", []):
            if e["fonte"] not in sel and e["fonte"] in manter:
                manter[e["fonte"]]["e"].append(e)

    vocab = vocabulario_roteiro(vd)
    prompt = PROMPT_VERBATIM + (" " + ", ".join(vocab[:20]) + "." if vocab else "")
    por_fonte = {f: {"p": [dict(w, fonte=f) for w in v["p"]], "e": v["e"]} for f, v in manter.items()}
    for f in sel:
        wav = vd / fontes[f].get("wav16k", f"edicao/audio16k/{f}.wav")
        if not wav.exists():
            sys.exit(f"[ERRO] {wav} não existe — rode ingest.py")
        log(f"[transcribe] {f} ({fontes[f]['duracao']:.1f}s) com {engine}...")
        cache = ed / "raw" / f"{f}.{engine}.json"
        palavras, eventos = transcrever_wav(wav, engine, cache, args.force, prompt=prompt,
                                            keyterms=vocab if args.keyterms else None,
                                            refinar=not args.sem_refino)
        por_fonte[f] = {"p": [dict(w, fonte=f) for w in palavras], "e": [dict(e, fonte=f) for e in eventos]}
        log(f"   {len(palavras)} palavras, conf média {mean(w['conf'] for w in palavras):.2f}, "
            f"{len(eventos)} eventos")

    todas, evs = [], []
    for f in sorted(por_fonte):
        todas += sorted(por_fonte[f]["p"], key=lambda w: w["inicio"])
        evs += por_fonte[f]["e"]
    saida = {
        "engine": engine, "idioma": "pt",
        "fontes": {f: {"arquivo": fontes[f]["arquivo"], "duracao": fontes[f]["duracao"]} for f in sorted(por_fonte)},
        "palavras": [{"i": i, "fonte": w["fonte"], "texto": w["texto"], "inicio": w["inicio"],
                      "fim": w["fim"], "conf": w["conf"],
                      **({"locutor_bruto": w["locutor_bruto"]} if w.get("locutor_bruto") else {})}
                     for i, w in enumerate(todas)],
        "eventos": [{"fonte": e["fonte"], "tipo": e["tipo"], "inicio": e["inicio"], "fim": e["fim"]} for e in evs],
    }
    escrever_json(tj, saida)
    log(f"[transcribe] {len(todas)} palavras -> {rel(vd, tj)}")


if __name__ == "__main__":
    main()
