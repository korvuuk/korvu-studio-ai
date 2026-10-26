"""Quem fala cada palavra: o Carlos (perto da câmera) ou a IA (ChatGPT Voice pelo alto-falante do celular)
-> `locutor`/`locutor_conf` em cada palavra do edicao/transcricao.json + edicao/locutores.json (contrato §2b)

uso: uv run python locutores.py <video_dir> [--ia-primeiro] [--forcar-metodo scribe|local]

Método de gravação do Carlos: o ChatGPT Voice (celular na sala, sem fone) lê cada linha do roteiro e o Carlos
repete para a câmera; o ChatGPT também "monitora" ("de novo", "repete: …", "faltou a palavra X", "próxima").
O áudio da câmera tem DUAS vozes dizendo (quase) o mesmo texto — o corte só pode usar a do Carlos.

Camada A (preferida, se houver): diarização do ElevenLabs Scribe (`transcribe.py` com Scribe grava
  `locutor_bruto` = speaker_id em cada palavra; diarize=True, num_speakers=2). Os ids viram 2 classes; o modelo
  acústico local confirma cada palavra (discordância forte -> `locutor: null`).
Camada B (local, sempre disponível): quadros de 32 ms / passo 10 ms do wav 16 kHz -> razão de graves
  (energia < 250 Hz / 250–4000 Hz; alto-falante de celular quase não tem graves), nível (dBFS), centróide e
  rolloff espectrais, pitch (autocorrelação normalizada, Boersma). Enunciados (palavras com intervalo ≤ 0,35 s)
  -> k-means com 2 classes em escalas fixas "dentro do mesmo locutor" -> teste de 2 locutores (distância entre
  centros ≥ 3) -> HMM de 2 estados por palavra (troca de locutor barata só em silêncios) -> posterior por palavra.
Qual classe é a IA — combinação de evidências (impressas e gravadas no locutores.json):
  (a) assinatura do celular: menos graves e menos nível;
  (b) ordem: numa linha do roteiro, a 1.ª leitura fluente é seguida pela repetição do outro locutor (a IA lê
      primeiro; `--ia-primeiro` dobra o peso desta evidência);
  (c) frases de monitor ("de novo", "repete", "próxima", "faltou", "ótimo", "perfeito"…) fora do texto da linha;
  (d) inscrição opcional: `00-marca/voz-carlos.json` (`perfil_locutor`) ou áudio em `02-calibracao/amostras/`.
Confiança baixa (evidências em conflito, palavra ambígua, sobreposição) -> `locutor: null` — o align marca a
linha como [REVISAR]; nunca chuta em silêncio.
Saídas extras no locutores.json: `zonas_ia` (fala da IA + cauda da reverb, zonas proibidas para pontos de corte),
`sobreposicoes` (IA e Carlos sem silêncio entre si), estatísticas e o `modelo` por quadro usado pelo verify.py
para medir voz de IA residual no corte (`residuo_ia`).
"""
from __future__ import annotations

import argparse
import datetime as dt
import math
import subprocess
import sys
import tempfile
from functools import lru_cache
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (FFMPEG, ROOT, edicao, escrever_json, fmt_t, ler_json, log, norm_palavra, rel,  # noqa: E402
                    resolver_video_dir)

# ---------------------------------------------------------------- parâmetros
SR16 = 16000
WIN, HOP, NFFT = 512, 160, 1024          # 32 ms / 10 ms
BANDA_GRAVE = (60.0, 250.0)
BANDA_MEIO = (250.0, 4000.0)
BANDA_TOTAL = (60.0, 7600.0)
F0_MIN, F0_MAX = 75.0, 400.0
VOZ_MIN = 0.45                           # pico da autocorrelação normalizada p/ quadro vozeado
DIMS = ("graves_db", "nivel_db", "centroide_oct", "rolloff_oct", "pitch_st")
# escala "dentro do mesmo locutor" de cada dimensão (distância 1 = variação normal de uma mesma voz)
ESCALAS = np.array([3.0, 3.0, 0.25, 0.30, 2.0])
DIST_2_LOCUTORES = 3.0                   # distância entre os centros das 2 classes p/ aceitar 2 vozes
DIST_CINZA = 2.0                         # 2,0–3,0: zona cinzenta (1 voz, com aviso)
MIN_FRAC_MINORIA = 0.05                  # a classe menor precisa de ≥ 5 % da fala...
MIN_ENUNC_MINORIA = 2                    # ...e ≥ 2 enunciados
GAP_ENUNCIADO = 0.35                     # s — palavras mais próximas que isso = mesmo enunciado (clusterização)
GAP_SEGMENTO = 0.60                      # s — segmentos de saída (mesmo locutor)
TEMPERATURA = 0.7                        # suaviza as verossimilhanças por palavra
DESVIO_MIN = 0.35                        # desvio mínimo por dimensão (unidades de ESCALAS)
CONF_MIN = 0.75                          # abaixo disso a palavra fica `locutor: null`
PESOS = {"assinatura": 2.0, "ordem": 1.5, "monitor": 1.0, "inscricao": 1.5}
NIVEL_DECISIVO = 12.0   # dB de diferença de nível entre as classes a partir do qual o nível decide sozinho
                        # quem é a IA (alto-falante do telemóvel na sala x voz perto do microfone)
FRASES_MONITOR = ["de novo", "repete", "repita", "repetir", "proxima", "faltou", "otimo", "perfeito",
                  "mais uma vez", "vamos pular", "vamos la", "boa", "muito bem", "terminamos", "de volta",
                  "tente de novo", "outra vez", "errou", "trocou"]
SOBREP_GAP = 0.10                        # IA e Carlos a menos disso (ou sem silêncio entre si) = sobreposição
CAUDA_MAX = 0.50                         # s — cauda máxima da reverb anexada a uma zona da IA
CAUDA_DB = 6.0                           # cauda = nível > piso de ruído + 6 dB
ZONA_ACUSTICA_MIN = 0.15                 # s — voz de IA sem palavra transcrita que vira zona
LIMIAR_LLR = 3.0                         # quadro "de IA" p/ zonas sem palavra e parada da cauda (LLR IA − Carlos)
# verify (voz de IA residual no corte): o mais sensível com 0 s de falso positivo na voz do Carlos no teste
# sintético (mediana 9 quadros, LLR > 1,5, ≥ 2 quadros). Mede ~50 % de um vazamento ≥ 0,5 s; vazamento curto
# (fim sibilante de uma leitura, cauda da reverb) quem pega é a conta determinística EDL × zonas_ia no verify.
RESIDUO_LIMIAR = 1.5
BORDA_SIL = 0.15                         # s de silêncio dentro de uma palavra = borda esticada pelo ASR
RESIDUO_MIN_RUN = 2                      # quadros seguidos (depois da mediana de 9) para contar como voz de IA
MODELO_DIMS = ("graves_db", "centroide_oct", "pitch_st")   # invariantes ao ganho (verify roda no corte)
MODELO_DESVIO_MIN = np.array([1.5, 0.08, 0.7])
EXT_AMOSTRA = {".wav", ".m4a", ".mp3", ".aac", ".flac", ".mov", ".mp4", ".m4v", ".aiff"}


# ---------------------------------------------------------------- quadros
@lru_cache(maxsize=8)
def quadros(wav: str) -> dict:
    """Características por quadro (32 ms, passo 10 ms) de um wav mono 16 kHz."""
    import soundfile as sf
    x, sr = sf.read(wav, dtype="float32", always_2d=True)
    x = x.mean(axis=1)
    if sr != SR16:
        raise RuntimeError(f"{wav}: esperado wav 16 kHz (é {sr})")
    if len(x) < WIN:
        x = np.pad(x, (0, WIN - len(x)))
    n = 1 + (len(x) - WIN) // HOP
    f = np.fft.rfftfreq(NFFT, 1 / SR16)
    m_low = (f >= BANDA_GRAVE[0]) & (f < BANDA_GRAVE[1])
    m_mid = (f >= BANDA_MEIO[0]) & (f < BANDA_MEIO[1])
    m_tot = (f >= BANDA_TOTAL[0]) & (f < BANDA_TOTAL[1])
    ft = f[m_tot]
    w = np.hanning(WIN).astype(np.float32)
    rw = np.fft.irfft(np.abs(np.fft.rfft(w, NFFT)) ** 2, NFFT)[:WIN]
    rw = rw / rw[0]
    lo, hi = int(SR16 / F0_MAX), int(SR16 / F0_MIN)
    nivel = np.empty(n, np.float32)
    graves = np.empty(n, np.float32)
    cent = np.empty(n, np.float32)
    roll = np.empty(n, np.float32)
    pitch = np.full(n, np.nan, np.float32)
    rmax_all = np.zeros(n, np.float32)
    for c0 in range(0, n, 4000):                         # em blocos (vídeos longos)
        c1 = min(n, c0 + 4000)
        idx = np.arange(WIN)[None, :] + HOP * np.arange(c0, c1)[:, None]
        fr = x[idx]
        nivel[c0:c1] = 10 * np.log10((fr ** 2).mean(axis=1) + 1e-12)
        P = np.abs(np.fft.rfft((fr - fr.mean(axis=1, keepdims=True)) * w, NFFT)) ** 2
        e_low, e_mid, e_tot = P[:, m_low].sum(1), P[:, m_mid].sum(1), P[:, m_tot].sum(1)
        graves[c0:c1] = 10 * np.log10((e_low + 1e-10) / (e_mid + 1e-10))
        pt = P[:, m_tot]
        cent[c0:c1] = (pt * ft).sum(1) / (e_tot + 1e-12)
        cum = np.cumsum(pt, axis=1)
        roll[c0:c1] = ft[np.argmax(cum >= 0.85 * cum[:, -1:], axis=1)]
        r = np.fft.irfft(P, NFFT)[:, :WIN]
        r = r / (r[:, :1] + 1e-12) / np.maximum(rw, 1e-3)[None, :]
        seg = np.clip(r[:, lo:hi + 1], -1, 1.0)
        rmax = seg.max(axis=1)
        # menor lag com pico local ≥ 0,9·máximo (evita erro de oitava para baixo)
        pico = np.zeros_like(seg, bool)
        pico[:, 1:-1] = (seg[:, 1:-1] >= seg[:, :-2]) & (seg[:, 1:-1] >= seg[:, 2:])
        cand = pico & (seg >= 0.9 * rmax[:, None])
        k = np.where(cand.any(axis=1), np.argmax(cand, axis=1), np.argmax(seg, axis=1))
        rmax_all[c0:c1] = rmax
        pitch[c0:c1] = SR16 / (lo + k)
    p10, p99 = np.percentile(nivel, [10, 99])
    limiar = float(max(p10 + 12.0, p99 - 40.0))
    ativo = nivel > limiar
    vozeado = ativo & (rmax_all > VOZ_MIN)
    pitch_st = np.where(vozeado, 12 * np.log2(pitch / 100.0), np.nan)
    t = (np.arange(n) * HOP + WIN / 2) / SR16
    return {"t": t, "nivel": nivel, "graves": graves, "cent_oct": np.log2(np.maximum(cent, 50) / 1000),
            "roll_oct": np.log2(np.maximum(roll, 50) / 1000), "pitch_st": pitch_st, "ativo": ativo,
            "vozeado": vozeado, "limiar": limiar, "piso": float(p10)}


def agregar(Q: dict, a: float, b: float) -> tuple[np.ndarray, int]:
    """Vetor (DIMS) de um intervalo + nº de quadros ativos. NaN onde não há dado."""
    i0, i1 = np.searchsorted(Q["t"], a), np.searchsorted(Q["t"], b)
    at, vz = Q["ativo"][i0:i1], Q["vozeado"][i0:i1]
    v = np.full(len(DIMS), np.nan)
    na = int(at.sum())
    if na < 2:
        return v, na
    g = Q["graves"][i0:i1]
    v[0] = np.median(g[vz]) if vz.sum() >= 3 else np.median(g[at])
    v[1] = np.percentile(Q["nivel"][i0:i1][at], 75)
    v[2] = np.median(Q["cent_oct"][i0:i1][at])
    v[3] = np.median(Q["roll_oct"][i0:i1][at])
    if vz.sum() >= 3:
        v[4] = np.median(Q["pitch_st"][i0:i1][vz])
    return v, na


def descrever(v) -> str:
    g, n, c, _, p = [float(x) if x is not None else float("nan") for x in v]
    ptxt = "—" if math.isnan(p) else f"{100 * 2 ** (p / 12):.0f} Hz"
    return f"graves {g:+.1f} dB · nível {n:.1f} dBFS · centróide {2 ** c:.2f} kHz · pitch {ptxt}"


# ---------------------------------------------------------------- clusterização
def _imputar(X: np.ndarray, w: np.ndarray) -> np.ndarray:
    X = X.copy()
    for d in range(X.shape[1]):
        m = np.isnan(X[:, d])
        if m.all():
            X[:, d] = 0.0
        elif m.any():
            ok = ~m
            ordem = np.argsort(X[ok, d])
            cw = np.cumsum(w[ok][ordem])
            X[m, d] = X[ok, d][ordem][np.searchsorted(cw, cw[-1] / 2)]
    return X


def kmeans2(X: np.ndarray, w: np.ndarray, reinicios: int = 16, seed: int = 7):
    """k-means ponderado (k=2) -> (rótulos, centros, inércia)."""
    rng = np.random.default_rng(seed)
    n = len(X)
    inits = [(int(np.argmin(X[:, 0])), int(np.argmax(X[:, 0])))]
    inits += [tuple(int(i) for i in rng.choice(n, 2, replace=False)) for _ in range(reinicios)]
    melhor = None
    for i, j in inits:
        if np.allclose(X[i], X[j]):
            continue
        C = X[[i, j]].astype(float).copy()
        lab = np.zeros(n, int)
        for _ in range(60):
            d = ((X[:, None, :] - C[None]) ** 2).sum(-1)
            lab = d.argmin(1)
            if lab.min() == lab.max():
                break
            novo = np.array([np.average(X[lab == k], axis=0, weights=w[lab == k]) for k in (0, 1)])
            if np.allclose(novo, C):
                break
            C = novo
        d = ((X[:, None, :] - C[None]) ** 2).sum(-1)
        inercia = float((w * d[np.arange(n), lab]).sum())
        if lab.min() != lab.max() and (melhor is None or inercia < melhor[2]):
            melhor = (lab, C, inercia)
    return melhor


def silhueta(X: np.ndarray, lab: np.ndarray) -> float:
    if len(X) > 600:
        sel = np.linspace(0, len(X) - 1, 600).astype(int)
        X, lab = X[sel], lab[sel]
    D = np.sqrt(((X[:, None, :] - X[None]) ** 2).sum(-1))
    s = []
    for i in range(len(X)):
        mesma, outra = lab == lab[i], lab != lab[i]
        mesma[i] = False
        if not mesma.any() or not outra.any():
            continue
        a, b = D[i, mesma].mean(), D[i, outra].mean()
        s.append((b - a) / max(a, b, 1e-9))
    return float(np.mean(s)) if s else 0.0


# ---------------------------------------------------------------- HMM por palavra
def p_troca(gap: float) -> float:
    if gap < 0.15:
        return 0.02
    if gap < 0.40:
        return 0.10
    if gap < 1.00:
        return 0.35
    return 0.50


def modelos_classes(Z: np.ndarray, peso: np.ndarray, resp: np.ndarray) -> list[tuple[np.ndarray, np.ndarray]]:
    """Média/desvio por dimensão (espaço escalado) de cada classe, ponderados por responsabilidade × peso."""
    out = []
    for k in (0, 1):
        m, s = np.zeros(Z.shape[1]), np.ones(Z.shape[1])
        for d in range(Z.shape[1]):
            ok = ~np.isnan(Z[:, d])
            ww = (resp[:, k] * peso)[ok]
            if ww.sum() < 1e-6:
                continue
            m[d] = np.average(Z[ok, d], weights=ww)
            s[d] = max(DESVIO_MIN, math.sqrt(np.average((Z[ok, d] - m[d]) ** 2, weights=ww)))
        out.append((m, s))
    return out


def emissoes(Z: np.ndarray, n_ativos: np.ndarray, mods) -> np.ndarray:
    ll = np.zeros((len(Z), 2))
    tau = np.clip(n_ativos / 15.0, 0.25, 1.0) * TEMPERATURA
    for k, (m, s) in enumerate(mods):
        termo = -0.5 * ((Z - m) / s) ** 2 - np.log(s)
        ll[:, k] = np.nansum(termo, axis=1) * tau
    return ll


def forward_backward(ll: np.ndarray, gaps: np.ndarray) -> np.ndarray:
    n = len(ll)
    if n == 0:
        return np.zeros((0, 2))
    la = np.zeros((n, 2))
    la[0] = ll[0] + np.log(0.5)
    for k in range(1, n):
        p = p_troca(gaps[k])
        lt = np.log(np.array([[1 - p, p], [p, 1 - p]]))
        la[k] = ll[k] + np.logaddexp(la[k - 1][0] + lt[0], la[k - 1][1] + lt[1])
    lb = np.zeros((n, 2))
    for k in range(n - 2, -1, -1):
        p = p_troca(gaps[k + 1])
        lt = np.log(np.array([[1 - p, p], [p, 1 - p]]))
        nx = ll[k + 1] + lb[k + 1]
        lb[k] = np.logaddexp(lt[:, 0] + nx[0], lt[:, 1] + nx[1])
    lp = la + lb
    lp -= lp.max(axis=1, keepdims=True)
    p = np.exp(lp)
    return p / p.sum(axis=1, keepdims=True)


# ---------------------------------------------------------------- roteiro (evidências de ordem/monitor)
def _linhas_tokens(roteiro: dict) -> list[tuple[str, list[str]]]:
    out = []
    for l in roteiro.get("linhas", []):
        toks = [t for w in (l.get("fala") or "").split() for t in norm_palavra(w)]
        if toks:
            out.append((l["id"], toks))
    return out


def _melhor_linha(toks: list[str], linhas) -> tuple[str | None, float, float]:
    """-> (linha, cobertura = LCS/n_linha, precisão = LCS/n_trecho)."""
    from rapidfuzz.distance import LCSseq
    if not toks:
        return None, 0.0, 0.0
    melhor = (None, 0.0, 0.0)
    for lid, lt in linhas:
        lcs = LCSseq.similarity(toks, lt)
        cob, prec = lcs / len(lt), lcs / len(toks)
        if (cob, prec) > (melhor[1], melhor[2]):
            melhor = (lid, cob, prec)
    return melhor


def _frases_monitor(toks: list[str], toks_linha: set[str]) -> list[str]:
    s = " " + " ".join(toks) + " "
    achadas = []
    for fr in FRASES_MONITOR:
        if " " + fr + " " in s and not set(fr.split()) <= toks_linha:
            achadas.append(fr)
    return achadas


# ---------------------------------------------------------------- inscrição (voz do Carlos)
def perfil_inscricao() -> tuple[np.ndarray | None, str]:
    """Perfil acústico do Carlos: 00-marca/voz-carlos.json['perfil_locutor'] ou 1.º áudio de 02-calibracao/amostras/."""
    vj = ROOT / "00-marca" / "voz-carlos.json"
    if vj.exists():
        try:
            p = (ler_json(vj) or {}).get("perfil_locutor") or {}
        except Exception:
            p = {}
        if p:
            v = np.full(len(DIMS), np.nan)
            if p.get("graves_db") is not None:
                v[0] = float(p["graves_db"])
            if p.get("centroide_hz"):
                v[2] = math.log2(float(p["centroide_hz"]) / 1000)
            if p.get("pitch_hz"):
                v[4] = 12 * math.log2(float(p["pitch_hz"]) / 100)
            return v, rel(ROOT, vj)
    am = ROOT / "02-calibracao" / "amostras"
    arqs = sorted(p for p in am.glob("*") if p.suffix.lower() in EXT_AMOSTRA) if am.is_dir() else []
    if not arqs:
        return None, "ausente"
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "amostra.wav"
        r = subprocess.run([FFMPEG, "-hide_banner", "-nostdin", "-loglevel", "error", "-y", "-i", str(arqs[0]),
                            "-t", "120", "-vn", "-ac", "1", "-ar", str(SR16), "-c:a", "pcm_s16le", str(wav)],
                           capture_output=True)
        if r.returncode != 0:
            return None, f"amostra ilegível ({arqs[0].name})"
        Q = quadros(str(wav))
        v, na = agregar(Q, 0.0, float(Q["t"][-1]) + 1)
        quadros.cache_clear()
    return (v if na >= 50 else None), rel(ROOT, arqs[0])


# ---------------------------------------------------------------- bordas esticadas pelo ASR
def _runs_ativos(Q: dict, a: float, b: float) -> list[tuple[float, float]]:
    """Trechos com energia de fala dentro de [a, b], separados por silêncio ≥ BORDA_SIL."""
    i0, i1 = np.searchsorted(Q["t"], a), np.searchsorted(Q["t"], b)
    runs, cur, sil = [], None, 0
    for j, v in enumerate(Q["ativo"][i0:i1]):
        if v:
            if cur is not None and sil * HOP / SR16 >= BORDA_SIL:
                runs.append(cur)
                cur = None
            cur = [j, j] if cur is None else [cur[0], j]
            sil = 0
        else:
            sil += 1
    if cur is not None:
        runs.append(cur)
    t = Q["t"]
    return [(float(t[i0 + r0]) - 0.015, float(t[i0 + r1]) + 0.015) for r0, r1 in runs]


def ajustar_bordas(palavras: list[dict], Qs: dict) -> int:
    """Numa troca de locutor, o Whisper costuma esticar a 1.ª palavra do novo locutor para trás, por cima da cauda
    da voz anterior ("O" = cauda da IA + silêncio + "O" do Carlos). Palavra entre vizinhos de locutores diferentes
    com 2+ trechos de energia separados por silêncio ≥ BORDA_SIL fica só com o último trecho (ou o primeiro, se ela
    encosta na anterior e a próxima está longe). A borda original fica em `borda_asr`. Só age com 2 locutores."""
    n = 0
    fontes = sorted({w["fonte"] for w in palavras})
    for f in fontes:
        ks = sorted((k for k, w in enumerate(palavras) if w["fonte"] == f), key=lambda k: palavras[k]["inicio"])
        for j in range(1, len(ks) - 1):
            kp, k, kn = ks[j - 1], ks[j], ks[j + 1]
            lp, ln = palavras[kp].get("locutor"), palavras[kn].get("locutor")
            if lp is None or ln is None or lp == ln:
                continue
            w = palavras[k]
            runs = _runs_ativos(Qs[f], w["inicio"], w["fim"])
            if len(runs) < 2:
                continue
            gp, gn = w["inicio"] - palavras[kp]["fim"], palavras[kn]["inicio"] - w["fim"]
            a, b = runs[0] if (gn >= 0.3 and gp < 0.05) else runs[-1]
            a, b = max(a, w["inicio"]), min(b, w["fim"])
            if b - a < 0.05:
                continue
            w.setdefault("borda_asr", [w["inicio"], w["fim"]])
            w["inicio"], w["fim"] = round(a, 3), round(b, 3)
            n += 1
    return n


# ---------------------------------------------------------------- núcleo
def rotular(transcricao: dict, wavs: dict[str, str], roteiro: dict, ia_primeiro: bool = False,
            forcar_metodo: str | None = None, verbose: bool = True) -> tuple[list[dict], dict]:
    """-> (palavras com locutor/locutor_conf, locutores.json). `wavs` = {fonte: wav 16 kHz}.
    Duas passadas: a 1.ª só para achar as trocas de locutor e ajustar bordas esticadas pelo ASR (`ajustar_bordas`);
    a 2.ª é a definitiva."""
    p1, d1 = _rotular(transcricao, wavs, roteiro, ia_primeiro, forcar_metodo, verbose=False)
    n = ajustar_bordas(p1, {f: quadros(str(wavs[f])) for f in wavs}) if d1["n_locutores"] == 2 else 0
    if n:
        transcricao = {**transcricao, "palavras": [{k: v for k, v in w.items() if k not in ("locutor", "locutor_conf")}
                                                   for w in p1]}
    palavras, dados = _rotular(transcricao, wavs, roteiro, ia_primeiro, forcar_metodo, verbose=verbose)
    if n and verbose:
        log(f"   {n} palavra(s) com a borda do ASR esticada por cima da outra voz: bordas ajustadas "
            "(original em `borda_asr`)")
    dados["bordas_ajustadas"] = n
    return palavras, dados


def _rotular(transcricao: dict, wavs: dict[str, str], roteiro: dict, ia_primeiro: bool = False,
             forcar_metodo: str | None = None, verbose: bool = True) -> tuple[list[dict], dict]:
    say = log if verbose else (lambda *_: None)
    palavras = [dict(w) for w in transcricao.get("palavras", [])]
    fontes = sorted({w["fonte"] for w in palavras})
    Qs = {f: quadros(str(wavs[f])) for f in fontes}
    # --- características por palavra (espaço escalado) + ordem por fonte
    Z = np.full((len(palavras), len(DIMS)), np.nan)
    na = np.zeros(len(palavras))
    for k, w in enumerate(palavras):
        v, n = agregar(Qs[w["fonte"]], w["inicio"], w["fim"])
        Z[k], na[k] = v / ESCALAS, n
    por_fonte = {f: sorted((k for k, w in enumerate(palavras) if w["fonte"] == f),
                           key=lambda k: palavras[k]["inicio"]) for f in fontes}
    # --- método
    tem_bruto = sum(1 for w in palavras if w.get("locutor_bruto")) >= 0.8 * max(1, len(palavras))
    if forcar_metodo == "scribe" and not tem_bruto:
        raise SystemExit("[ERRO] --forcar-metodo scribe: a transcrição não tem `locutor_bruto` (transcreva com "
                         "Scribe, diarize=True — transcribe.py --engine scribe --force)")
    metodo = "scribe" if (tem_bruto and forcar_metodo != "local") else "local"
    # --- enunciados (clusterização local)
    enunc = []
    for f in fontes:
        cur = []
        for k in por_fonte[f]:
            if cur and palavras[k]["inicio"] - palavras[cur[-1]]["fim"] > GAP_ENUNCIADO:
                enunc.append(cur)
                cur = []
            cur.append(k)
        if cur:
            enunc.append(cur)
    EX, EW = [], []
    for e in enunc:
        f = palavras[e[0]]["fonte"]
        v, n = agregar(Qs[f], palavras[e[0]]["inicio"], palavras[e[-1]]["fim"])
        EX.append(v / ESCALAS)
        EW.append(max(1, n))
    EX, EW = np.array(EX) if EX else np.zeros((0, len(DIMS))), np.array(EW, float)
    dist, sil, frac_min, lab_e, C, n_min = 0.0, 0.0, 0.0, None, None, 0
    if len(EX) >= 3:
        Xi = _imputar(EX, EW)
        km = kmeans2(Xi, EW)
        if km:
            lab_e, C, _ = km
            dist = float(np.linalg.norm(C[0] - C[1]))
            sil = silhueta(Xi, lab_e)
            tempo = np.array([EW[lab_e == k].sum() for k in (0, 1)])
            frac_min = float(tempo.min() / tempo.sum())
            n_min = int(min((lab_e == 0).sum(), (lab_e == 1).sum()))
    dois_local = (lab_e is not None and dist >= DIST_2_LOCUTORES and frac_min >= MIN_FRAC_MINORIA
                  and n_min >= MIN_ENUNC_MINORIA)
    # --- rótulos iniciais por palavra
    resp = np.full((len(palavras), 2), 0.5)
    bruto_ids = []
    if metodo == "scribe":
        tempo_id: dict[str, float] = {}
        for w in palavras:
            if w.get("locutor_bruto"):
                tempo_id[w["locutor_bruto"]] = tempo_id.get(w["locutor_bruto"], 0) + (w["fim"] - w["inicio"])
        bruto_ids = sorted(tempo_id, key=lambda i: -tempo_id[i])
        tot = sum(tempo_id.values()) or 1
        if len(bruto_ids) < 2 or tempo_id[bruto_ids[1]] / tot < MIN_FRAC_MINORIA:
            if dois_local:
                say(f"   [AVISO] Scribe viu 1 voz, mas a análise local separa 2 (distância {dist:.1f}) — usando a local")
                metodo = "local"
            bruto_ids = bruto_ids[:1]
        else:
            if len(bruto_ids) > 2:
                say(f"   [AVISO] Scribe viu {len(bruto_ids)} vozes ({', '.join(bruto_ids)}): as 2 com mais tempo "
                    "viram as classes; o resto é decidido pela acústica")
            for k, w in enumerate(palavras):
                if w.get("locutor_bruto") == bruto_ids[0]:
                    resp[k] = (1.0, 0.0)
                elif w.get("locutor_bruto") == bruto_ids[1]:
                    resp[k] = (0.0, 1.0)
    dois = dois_local if metodo == "local" else len(bruto_ids) >= 2
    info_sep = {"distancia": round(dist, 2), "limiar": DIST_2_LOCUTORES, "silhueta": round(sil, 3),
                "fracao_minoria": round(frac_min, 3), "enunciados": len(enunc)}
    say(f"[locutores] {len(palavras)} palavras · {len(enunc)} enunciados · método {metodo} · separação acústica "
        f"{dist:.2f} (limiar {DIST_2_LOCUTORES:g}; silhueta {sil:.2f}; minoria {frac_min:.0%})")
    linhas_rot = _linhas_tokens(roteiro)

    if not dois:
        return _um_locutor(palavras, por_fonte, Qs, dist, info_sep, metodo, ia_primeiro, linhas_rot, say)

    if metodo == "local":
        for ei, e in enumerate(enunc):
            for k in e:
                resp[k] = (1.0, 0.0) if lab_e[ei] == 0 else (0.0, 1.0)
    # --- HMM por palavra (2 iterações de reestimação)
    peso = np.maximum(na, 1)
    gaps = {f: np.array([9.0] + [palavras[b]["inicio"] - palavras[a]["fim"]
                                 for a, b in zip(por_fonte[f][:-1], por_fonte[f][1:])]) for f in fontes}
    post = resp.copy()
    base = resp.copy()
    for it in range(3):
        mods = modelos_classes(Z, peso, post if it else base)
        ll = emissoes(Z, na, mods)
        if metodo == "scribe":          # diarização como "observação" extra (confiança 0,92)
            lg = math.log(0.92 / 0.08)
            ll += np.where(base == 1.0, lg / 2, np.where(base == 0.0, -lg / 2, 0.0))
        novo = np.zeros_like(post)
        for f in fontes:
            ix = por_fonte[f]
            novo[ix] = forward_backward(ll[ix], gaps[f])
        post = novo
    classe = post.argmax(axis=1)
    pmax = post.max(axis=1)

    # --- segmentos (runs do mesmo locutor)
    segs = []
    for f in fontes:
        cur = []
        for k in por_fonte[f]:
            if cur and (classe[k] != classe[cur[-1]] or palavras[k]["inicio"] - palavras[cur[-1]]["fim"] > GAP_SEGMENTO):
                segs.append(cur)
                cur = []
            cur.append(k)
        if cur:
            segs.append(cur)
    seg_info = []
    for s in segs:
        toks = [t for k in s for t in norm_palavra(palavras[k]["texto"])]
        lid, cob, prec = _melhor_linha(toks, linhas_rot)
        tl = set(next((lt for i, lt in linhas_rot if i == lid), []))
        seg_info.append({"ks": s, "classe": int(classe[s[0]]), "fonte": palavras[s[0]]["fonte"],
                         "inicio": palavras[s[0]]["inicio"], "fim": palavras[s[-1]]["fim"], "toks": toks,
                         "linha": lid if cob >= 0.6 else None, "cobertura": round(cob, 3),
                         "monitor": _frases_monitor(toks, tl if cob >= 0.6 else set())})

    # --- evidências: qual classe é a IA (valor > 0 => classe 1 é a IA)
    evid = []
    cls_vec = []
    for k in (0, 1):
        sel = classe == k
        v = np.array([np.nanmedian(Z[sel, d] * ESCALAS[d]) if np.any(sel & ~np.isnan(Z[:, d])) else np.nan
                      for d in range(len(DIMS))])
        cls_vec.append(v)
    g0, g1, n0, n1 = cls_vec[0][0], cls_vec[1][0], cls_vec[0][1], cls_vec[1][1]
    # 2026-09-18: o NÍVEL é o cue físico mais confiável deste método — a IA sai do alto-falante do telemóvel,
    # do outro lado da sala, e o Carlos fala perto do microfone. A assinatura de graves supõe que o telemóvel
    # corta os graves; numa sala que devolve grave isso não vale (no Hassabis a diferença de graves foi de só
    # -1,1 dB, e AO CONTRÁRIO, contra 20,2 dB de nível). Com 0,7/0,3 fixos, um sinal decisivo perdia para um
    # ruído e TODAS as palavras ficavam sem locutor. Agora: diferença de nível grande decide; graves desempatam.
    t_g, t_n = math.tanh((g0 - g1) / 6.0), math.tanh((n0 - n1) / 6.0)
    dec_n = min(1.0, abs(n0 - n1) / NIVEL_DECISIVO)
    e_a = dec_n * t_n + (1 - dec_n) * (0.7 * t_g + 0.3 * t_n)
    evid.append({"nome": "assinatura", "valor": e_a, "peso": PESOS["assinatura"],
                 "detalhe": f"classe B tem {g0 - g1:+.1f} dB de graves e {n0 - n1:+.1f} dB de nível a menos que A"})
    votos = [0, 0]
    for a, b in zip(seg_info[:-1], seg_info[1:]):
        if (a["fonte"] == b["fonte"] and a["classe"] != b["classe"] and b["inicio"] - a["fim"] <= 4.0
                and a["linha"] and a["linha"] == b["linha"]):
            votos[a["classe"]] += 1
    tv = sum(votos)
    if tv:
        e_b = (votos[1] - votos[0]) / tv * min(1.0, tv / 3)
        evid.append({"nome": "ordem", "valor": e_b, "peso": PESOS["ordem"] * (2 if ia_primeiro else 1),
                     "detalhe": f"{tv} par(es) leitura→repetição: A leu primeiro {votos[0]}×, B {votos[1]}×"})
    mon = [0, 0]
    exemplos: list[list[str]] = [[], []]
    for s in seg_info:
        if s["monitor"]:
            mon[s["classe"]] += 1
            exemplos[s["classe"]] += s["monitor"][:1]
    if sum(mon):
        e_c = (mon[1] - mon[0]) / sum(mon) * min(1.0, sum(mon) / 2)
        evid.append({"nome": "monitor", "valor": e_c, "peso": PESOS["monitor"],
                     "detalhe": f"frases de monitor: A {mon[0]} ({', '.join(sorted(set(exemplos[0]))) or '—'}), "
                                f"B {mon[1]} ({', '.join(sorted(set(exemplos[1]))) or '—'})"})
    perfil, origem = perfil_inscricao()
    if perfil is not None:
        dd = [2, 4] + ([0] if not math.isnan(perfil[0]) else [])
        dist_p = []
        for v in cls_vec:
            z = [(v[d] - perfil[d]) / ESCALAS[d] for d in dd if not (math.isnan(v[d]) or math.isnan(perfil[d]))]
            dist_p.append(math.sqrt(sum(x * x for x in z) / max(1, len(z))))
        e_d = math.tanh((dist_p[1] - dist_p[0]) / 1.5)
        evid.append({"nome": "inscricao", "valor": e_d, "peso": PESOS["inscricao"],
                     "detalhe": f"{origem}: distância ao perfil do Carlos A {dist_p[0]:.2f}, B {dist_p[1]:.2f}"})
    # 2026-09-18: a média pura DILUÍA. No Hassabis a assinatura era decisiva (+1,00: 20 dB de diferença de
    # nível) e as outras concordavam, mas uma delas valia pouco (3 pares de leitura→repetição) com peso alto —
    # média 0,39, abaixo do limiar, e as 1133 palavras ficaram SEM LOCUTOR. Evidências independentes que
    # apontam para o mesmo lado têm de se reforçar. Soma comprimida: o sinal cresce, o sinal contrário continua
    # a descontar, e caso genuinamente ambíguo (média < 0,25) continua a ficar `null`.
    media = sum(e["valor"] * e["peso"] for e in evid) / max(1e-9, sum(e["peso"] for e in evid))
    S = math.tanh(2.0 * media)
    ia_cls = 1 if S > 0 else 0
    conf_papel = abs(S)
    nome_cls = {0: "A", 1: "B"}
    papel = {ia_cls: "ia", 1 - ia_cls: "carlos"}
    for k in (0, 1):
        tempo = sum(palavras[j]["fim"] - palavras[j]["inicio"] for j in range(len(palavras)) if classe[j] == k)
        say(f"   classe {nome_cls[k]}: {descrever(cls_vec[k])} · {tempo:.1f}s de palavras")
    for e in evid:
        lado = "B" if e["valor"] > 0 else "A"
        say(f"   evidência {e['nome']:<10} (peso {e['peso']:.1f}): {lado} = IA ({e['valor']:+.2f}) — {e['detalhe']}")
    if perfil is None:
        say("   evidência inscricao  : sem perfil (00-marca/voz-carlos.json `perfil_locutor` ou 02-calibracao/amostras/)")
    discord = [e["nome"] for e in evid if e["valor"] * S < 0 and abs(e["valor"]) > 0.2]
    say(f"   => IA = classe {nome_cls[ia_cls]} · confiança do papel {conf_papel:.2f}"
        + (f" · [AVISO] evidências em conflito: {', '.join(discord)}" if discord else ""))
    teto = 0.5 + conf_papel / 2
    if teto < CONF_MIN:
        say(f"   [AVISO] confiança do papel baixa ({conf_papel:.2f}): palavras ficam `locutor: null` — as linhas "
            "vão para [REVISAR]; confira no preview")

    # --- palavras
    for k, w in enumerate(palavras):
        c = float(min(pmax[k], teto))
        w["locutor"] = papel[int(classe[k])] if c >= CONF_MIN else None
        w["locutor_conf"] = round(c, 3)
    modelo = _modelo_quadros(palavras, Qs)
    zonas, sobre = _zonas_e_sobreposicoes(palavras, por_fonte, Qs, modelo)
    segmentos = []
    for s in seg_info:
        ks = s["ks"]
        locs = {palavras[k]["locutor"] for k in ks}
        loc = papel[s["classe"]] if locs == {papel[s["classe"]]} else (None if locs == {None} else "misto")
        v, _ = agregar(Qs[s["fonte"]], s["inicio"], s["fim"])
        tipo = ("leitura" if s["linha"] else "monitor") if papel[s["classe"]] == "ia" else ("take" if s["linha"] else "fala")
        segmentos.append({"fonte": s["fonte"], "inicio": s["inicio"], "fim": s["fim"], "locutor": loc,
                          "classe": nome_cls[s["classe"]], "conf": round(float(np.mean([palavras[k]["locutor_conf"] for k in ks])), 3),
                          "tipo": tipo, "linha": s["linha"], "cobertura": s["cobertura"],
                          "monitor": s["monitor"], "i_ini": palavras[ks[0]]["i"], "i_fim": palavras[ks[-1]]["i"],
                          "texto": " ".join(palavras[k]["texto"] for k in ks),
                          "graves_db": _r(v[0]), "nivel_db": _r(v[1]),
                          "pitch_hz": None if math.isnan(v[4]) else round(100 * 2 ** (v[4] / 12), 1)})
    dados = {
        "metodo": metodo, "n_locutores": 2, "protocolo_ia_primeiro": bool(ia_primeiro), "separacao": info_sep,
        "classes": {nome_cls[k]: {"papel": papel[k], **{d: _r(cls_vec[k][i]) for i, d in enumerate(DIMS)},
                                  **({"id_scribe": bruto_ids[k]} if metodo == "scribe" and k < len(bruto_ids) else {})}
                    for k in (0, 1)},
        "papel": {"ia": nome_cls[ia_cls], "carlos": nome_cls[1 - ia_cls], "confianca": round(conf_papel, 3),
                  "evidencias": [{**e, "valor": round(e["valor"], 3),
                                  "aponta_ia": nome_cls[1 if e["valor"] > 0 else 0]} for e in evid],
                  "conflito": discord},
        "segmentos": segmentos, "zonas_ia": zonas, "sobreposicoes": sobre,
        "incertos": [{"fonte": w["fonte"], "i": w["i"], "texto": w["texto"], "inicio": w["inicio"],
                      "conf": w["locutor_conf"]} for w in palavras if w["locutor"] is None],
        "estatisticas": _estatisticas(palavras, segmentos, zonas, sobre),
        "modelo": modelo,
    }
    return palavras, dados


def _r(x, n=2):
    return None if x is None or (isinstance(x, float) and math.isnan(x)) else round(float(x), n)


def _um_locutor(palavras, por_fonte, Qs, dist, info_sep, metodo, ia_primeiro, linhas_rot, say):
    """Uma voz só (gravação clássica): tudo do Carlos. Com --ia-primeiro, as 1.ªs leituras de pares
    leitura→repetição ficam `null` (provável IA parecida demais com o Carlos — nunca chutar)."""
    cinza = dist >= DIST_CINZA
    conf = 0.80 if cinza else 0.95
    for w in palavras:
        w["locutor"], w["locutor_conf"] = "carlos", conf
    incertos_pares = 0
    if ia_primeiro:
        for f, ks in por_fonte.items():
            runs, cur = [], []
            for k in ks:
                if cur and palavras[k]["inicio"] - palavras[cur[-1]]["fim"] > GAP_SEGMENTO:
                    runs.append(cur)
                    cur = []
                cur.append(k)
            if cur:
                runs.append(cur)
            info = []
            for r in runs:
                toks = [t for k in r for t in norm_palavra(palavras[k]["texto"])]
                lid, cob, _ = _melhor_linha(toks, linhas_rot)
                info.append((r, lid if cob >= 0.6 else None))
            for (ra, la), (rb, lb) in zip(info[:-1], info[1:]):
                if la and la == lb and palavras[rb[0]]["inicio"] - palavras[ra[-1]]["fim"] <= 4.0:
                    for k in ra:
                        palavras[k]["locutor"], palavras[k]["locutor_conf"] = None, 0.5
                    incertos_pares += 1
        say(f"   [AVISO] --ia-primeiro, mas só 1 voz foi separada acusticamente: {incertos_pares} 1.ª(s) leitura(s) "
            "de pares leitura→repetição ficaram `locutor: null` (IA com voz parecida com a do Carlos? celular "
            "baixo demais?) — confira no preview")
    elif cinza:
        say(f"   [AVISO] separação {dist:.2f} na zona cinzenta ({DIST_CINZA:g}–{DIST_2_LOCUTORES:g}): tratado como "
            "1 voz (Carlos). Se a gravação tinha o ChatGPT falando, rode com --ia-primeiro")
    say(f"   => 1 locutor (Carlos) · {len(palavras)} palavras" + (" (zona cinzenta)" if cinza else ""))
    segs = []
    for f, ks in por_fonte.items():
        cur = []
        for k in ks:
            if cur and (palavras[k]["inicio"] - palavras[cur[-1]]["fim"] > GAP_SEGMENTO
                        or palavras[k]["locutor"] != palavras[cur[-1]]["locutor"]):
                segs.append(cur)
                cur = []
            cur.append(k)
        if cur:
            segs.append(cur)
    segmentos = [{"fonte": palavras[s[0]]["fonte"], "inicio": palavras[s[0]]["inicio"], "fim": palavras[s[-1]]["fim"],
                  "locutor": palavras[s[0]]["locutor"], "classe": "A", "conf": palavras[s[0]]["locutor_conf"],
                  "tipo": "fala", "i_ini": palavras[s[0]]["i"], "i_fim": palavras[s[-1]]["i"],
                  "texto": " ".join(palavras[k]["texto"] for k in s)} for s in segs]
    dados = {"metodo": metodo, "n_locutores": 1, "protocolo_ia_primeiro": bool(ia_primeiro), "separacao": info_sep,
             "classes": {"A": {"papel": "carlos"}}, "papel": {"ia": None, "carlos": "A",
                                                             "confianca": round(conf, 3), "evidencias": [], "conflito": []},
             "segmentos": segmentos, "zonas_ia": {f: [] for f in por_fonte}, "sobreposicoes": [],
             "incertos": [{"fonte": w["fonte"], "i": w["i"], "texto": w["texto"], "inicio": w["inicio"],
                           "conf": w["locutor_conf"]} for w in palavras if w["locutor"] is None],
             "estatisticas": _estatisticas(palavras, segmentos, {}, []), "modelo": None}
    return palavras, dados


def _estatisticas(palavras, segmentos, zonas, sobre) -> dict:
    def seg_tempo(loc):
        return round(sum(s["fim"] - s["inicio"] for s in segmentos if s["locutor"] == loc), 2)
    return {"segundos_ia": seg_tempo("ia"), "segundos_carlos": seg_tempo("carlos"),
            "segundos_incerto": round(sum(s["fim"] - s["inicio"] for s in segmentos if s["locutor"] in (None, "misto")), 2),
            "segundos_zonas_ia": round(sum(b - a for z in zonas.values() for a, b in z), 2),
            "palavras_ia": sum(1 for w in palavras if w["locutor"] == "ia"),
            "palavras_carlos": sum(1 for w in palavras if w["locutor"] == "carlos"),
            "palavras_incertas": sum(1 for w in palavras if w["locutor"] is None),
            "sobreposicoes": len(sobre)}


# ---------------------------------------------------------------- modelo por quadro, zonas, sobreposições
def _matriz_modelo(Q: dict, sel: np.ndarray) -> np.ndarray:
    return np.stack([Q["graves"][sel], Q["cent_oct"][sel], Q["pitch_st"][sel]], axis=1)


def _modelo_quadros(palavras, Qs) -> dict | None:
    """Gaussianas diagonais por locutor sobre quadros vozeados (graves, centróide, pitch — sem nível)."""
    X = {"ia": [], "carlos": []}
    for w in palavras:
        if w["locutor"] not in X or w["locutor_conf"] < 0.9:
            continue
        Q = Qs[w["fonte"]]
        i0, i1 = np.searchsorted(Q["t"], w["inicio"]), np.searchsorted(Q["t"], w["fim"])
        sel = np.zeros(len(Q["t"]), bool)
        sel[i0:i1] = Q["vozeado"][i0:i1]
        if sel.any():
            X[w["locutor"]].append(_matriz_modelo(Q, sel))
    if not X["ia"] or not X["carlos"]:
        return None
    out = {"dims": list(MODELO_DIMS), "limiar_llr": RESIDUO_LIMIAR, "min_quadros": RESIDUO_MIN_RUN}
    for k, v in X.items():
        M = np.concatenate(v)
        out[k] = {"media": [round(float(x), 4) for x in M.mean(0)],
                  "desvio": [round(float(x), 4) for x in np.maximum(M.std(0), MODELO_DESVIO_MIN)],
                  "quadros": int(len(M))}
    return out


def llr_quadros(Q: dict, modelo: dict) -> np.ndarray:
    """log p(IA) − log p(Carlos) por quadro vozeado (NaN nos outros)."""
    out = np.full(len(Q["t"]), np.nan)
    sel = Q["vozeado"]
    if not sel.any() or not modelo:
        return out
    X = _matriz_modelo(Q, sel)
    lp = []
    for k in ("ia", "carlos"):
        m, s = np.array(modelo[k]["media"]), np.array(modelo[k]["desvio"])
        lp.append((-0.5 * ((X - m) / s) ** 2 - np.log(s)).sum(1))
    out[sel] = lp[0] - lp[1]
    return out


def _suavizar(llr: np.ndarray, janela: int = 9) -> np.ndarray:
    from scipy.ndimage import median_filter
    x = np.where(np.isnan(llr), -10.0, llr)
    return median_filter(x, size=janela, mode="nearest")


def _runs(mask: np.ndarray, t: np.ndarray, min_len: int) -> list[list[float]]:
    out, k, n = [], 0, len(mask)
    while k < n:
        if not mask[k]:
            k += 1
            continue
        k2 = k
        while k2 + 1 < n and mask[k2 + 1]:
            k2 += 1
        if k2 - k + 1 >= min_len:
            out.append([float(t[k] - HOP / SR16 / 2), float(t[k2] + HOP / SR16 / 2)])
        k = k2 + 1
    return out


def _fundir(iv: list[list[float]], tol: float = 0.02) -> list[list[float]]:
    iv = sorted(iv)
    out: list[list[float]] = []
    for a, b in iv:
        if out and a <= out[-1][1] + tol:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return [[round(a, 3), round(b, 3)] for a, b in out]


def _tem_silencio(Q: dict, a: float, b: float, n_min: int = 3) -> bool:
    i0, i1 = np.searchsorted(Q["t"], a), np.searchsorted(Q["t"], b)
    run = 0
    for v in Q["nivel"][i0:i1] <= Q["limiar"]:
        run = run + 1 if v else 0
        if run >= n_min:
            return True
    return False


def _zonas_e_sobreposicoes(palavras, por_fonte, Qs, modelo):
    """Zonas da IA por fonte (palavras da IA + cauda da reverb + voz de IA sem palavra) e sobreposições
    (IA e Carlos colados: menos de SOBREP_GAP entre si ou nenhum silêncio no meio)."""
    zonas, sobre = {}, []
    for f, ks in por_fonte.items():
        Q = Qs[f]
        llr = _suavizar(llr_quadros(Q, modelo)) if modelo else None
        iv = []
        nao_ia = [palavras[k] for k in ks if palavras[k]["locutor"] != "ia"]
        ini_nao = np.array([w["inicio"] for w in nao_ia]) if nao_ia else np.zeros(0)
        fim_nao = np.array([w["fim"] for w in nao_ia]) if nao_ia else np.zeros(0)
        run = []
        for k in ks + [None]:
            if k is not None and palavras[k]["locutor"] == "ia" and (
                    not run or palavras[k]["inicio"] - palavras[run[-1]]["fim"] <= GAP_SEGMENTO):
                run.append(k)
                continue
            if run:
                a, b = palavras[run[0]]["inicio"], palavras[run[-1]]["fim"]
                # cauda (reverb) depois: nível acima do piso + 6 dB, sem entrar num quadro vozeado "do Carlos"
                prox = ini_nao[ini_nao >= b - 0.05]
                lim = min(b + CAUDA_MAX, (prox.min() - 0.02) if len(prox) else b + CAUDA_MAX)
                j = np.searchsorted(Q["t"], b)
                while j < len(Q["t"]) and Q["t"][j] <= lim and Q["nivel"][j] > Q["piso"] + CAUDA_DB and not (
                        llr is not None and Q["vozeado"][j] and llr[j] < -LIMIAR_LLR):
                    j += 1
                b2 = max(b, min(float(Q["t"][min(j, len(Q["t"]) - 1)]), lim))
                ant = fim_nao[fim_nao <= a + 0.05]
                lim0 = max(a - 0.20, (ant.max() + 0.02) if len(ant) else a - 0.20)
                j = np.searchsorted(Q["t"], a) - 1
                while j >= 0 and Q["t"][j] >= lim0 and Q["nivel"][j] > Q["piso"] + CAUDA_DB:
                    j -= 1
                a2 = min(a, max(float(Q["t"][max(j, 0)]), lim0))
                iv.append([a2, b2])
                run = [k] if k is not None and palavras[k]["locutor"] == "ia" else []
        # voz de IA que o ASR não transcreveu (fora de qualquer palavra)
        if llr is not None:
            fora = np.ones(len(Q["t"]), bool)
            for k in ks:
                i0 = np.searchsorted(Q["t"], palavras[k]["inicio"] - 0.05)
                i1 = np.searchsorted(Q["t"], palavras[k]["fim"] + 0.05)
                fora[i0:i1] = False
            for a, b in _runs(fora & (llr > LIMIAR_LLR), Q["t"], int(ZONA_ACUSTICA_MIN * 100)):
                iv.append([a, b])
        zonas[f] = _fundir(iv)
        # sobreposições: vizinhos (no tempo) de locutores diferentes sem silêncio entre si
        for a, b in zip(ks[:-1], ks[1:]):
            la, lb = palavras[a]["locutor"], palavras[b]["locutor"]
            if {la, lb} != {"ia", "carlos"}:
                continue
            gap = palavras[b]["inicio"] - palavras[a]["fim"]
            if gap < SOBREP_GAP or not _tem_silencio(Q, palavras[a]["fim"] - 0.02, palavras[b]["inicio"] + 0.02):
                wc, wi = (palavras[a], palavras[b]) if la == "carlos" else (palavras[b], palavras[a])
                sobre.append({"fonte": f, "tipo": "ia_depois_do_carlos" if la == "carlos" else "carlos_depois_da_ia",
                              "inicio": round(min(palavras[a]["fim"], palavras[b]["inicio"]), 3),
                              "fim": round(max(palavras[a]["fim"], palavras[b]["inicio"]), 3),
                              "gap": round(gap, 3), "carlos_i": wc["i"], "ia_i": wi["i"],
                              "texto": f"{palavras[a]['texto']} | {palavras[b]['texto']}"})
    return zonas, sobre


# ---------------------------------------------------------------- verify: voz de IA residual
def residuo_ia(wav: str, loc: dict | None, palavras: list[dict] | None = None) -> dict:
    """Mede voz de IA num áudio (ex.: corte.mp4) com o modelo por quadro do locutores.json da gravação original.
    -> {"aplicavel", "segundos", "trechos": [[a,b]], "palavras_ia": [...]}."""
    modelo = (loc or {}).get("modelo")
    if not loc or loc.get("n_locutores", 1) < 2 or not modelo:
        return {"aplicavel": False, "segundos": 0.0, "trechos": [], "palavras_ia": [],
                "motivo": "gravação com 1 locutor (sem modelo de IA)" if loc else "sem locutores.json"}
    Q = quadros(str(wav))
    llr = llr_quadros(Q, modelo)
    sm = _suavizar(llr)
    iv = _runs(sm > RESIDUO_LIMIAR, Q["t"], RESIDUO_MIN_RUN)
    pal_ia = []
    for w in palavras or []:
        i0, i1 = np.searchsorted(Q["t"], w["inicio"]), np.searchsorted(Q["t"], w["fim"])
        v = llr[i0:i1]
        v = v[~np.isnan(v)]
        if len(v) >= 3 and float(np.median(v)) > RESIDUO_LIMIAR:
            pal_ia.append({"texto": w["texto"], "inicio": w["inicio"], "fim": w["fim"],
                           "llr": round(float(np.median(v)), 2)})
            iv.append([w["inicio"], w["fim"]])
    iv = _fundir(iv)
    return {"aplicavel": True, "segundos": round(sum(b - a for a, b in iv), 3), "trechos": iv,
            "palavras_ia": pal_ia, "limiar_llr": RESIDUO_LIMIAR}


# ---------------------------------------------------------------- arquivos
def caminho(vd: Path) -> Path:
    return Path(vd) / "edicao" / "locutores.json"


def carregar(vd: Path) -> dict | None:
    p = caminho(vd)
    return ler_json(p) if p.exists() else None


def desatualizado(vd: Path) -> bool:
    """locutores.json ausente, mais velho que a transcrição, ou transcrição sem `locutor` nas palavras."""
    ed = Path(vd) / "edicao"
    tj, lj = ed / "transcricao.json", caminho(vd)
    if not tj.exists():
        return False
    if not lj.exists() or lj.stat().st_mtime < tj.stat().st_mtime - 1e-6:
        return True
    ws = (ler_json(tj) or {}).get("palavras") or []
    return bool(ws) and any("locutor" not in w for w in ws)


def executar(vd: Path, ia_primeiro: bool | None = None, forcar_metodo: str | None = None) -> dict:
    ed = edicao(vd)
    tj = ed / "transcricao.json"
    tr = ler_json(tj)
    roteiro = ler_json(vd / "roteiro.json", padrao={})
    anterior = carregar(vd) or {}
    if ia_primeiro is None:
        ia_primeiro = bool(anterior.get("protocolo_ia_primeiro"))
    fontes = tr.get("fontes") or {}
    wavs = {}
    for f in sorted({w["fonte"] for w in tr.get("palavras", [])}):
        w = ed / "audio16k" / f"{f}.wav"
        if not w.exists():
            sys.exit(f"[ERRO] {w} não existe — rode ingest.py")
        wavs[f] = str(w)
    palavras, dados = rotular(tr, wavs, roteiro, ia_primeiro=ia_primeiro, forcar_metodo=forcar_metodo)
    tr["palavras"] = palavras
    escrever_json(tj, tr)
    dados = {"versao": 1, "gerado_em": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
             "fontes": sorted(fontes) or sorted(wavs), **dados}
    escrever_json(caminho(vd), dados)
    st = dados["estatisticas"]
    log(f"[locutores] IA {st['segundos_ia']:.1f}s · Carlos {st['segundos_carlos']:.1f}s · incerto "
        f"{st['segundos_incerto']:.1f}s · palavras IA {st['palavras_ia']} / Carlos {st['palavras_carlos']} / "
        f"null {st['palavras_incertas']} · sobreposições {st['sobreposicoes']} · zonas IA {st['segundos_zonas_ia']:.1f}s")
    for s in dados["sobreposicoes"]:
        log(f"   sobreposição {s['fonte']} {fmt_t(s['inicio'])}: {s['texto']} (gap {s['gap']:+.2f}s)")
    log(f"[locutores] -> {rel(vd, caminho(vd))} (+ locutor/locutor_conf em {rel(vd, tj)})")
    return dados


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video_dir")
    ap.add_argument("--ia-primeiro", action="store_true",
                    help="gravação no método ChatGPT-monitor (a IA lê cada linha antes): dobra o peso da evidência "
                         "de ordem e, se só 1 voz for separada, marca as 1.as leituras como incertas")
    ap.add_argument("--forcar-metodo", choices=["scribe", "local"], default=None,
                    help="scribe = usar a diarização do Scribe (locutor_bruto); local = só a acústica local")
    args = ap.parse_args()
    vd = resolver_video_dir(args.video_dir)
    executar(vd, ia_primeiro=args.ia_primeiro or None, forcar_metodo=args.forcar_metodo)


if __name__ == "__main__":
    main()
