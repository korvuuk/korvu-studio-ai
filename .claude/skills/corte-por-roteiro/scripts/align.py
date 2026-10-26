"""Alinha a transcrição (palavras) às linhas do roteiro -> edicao/alinhamento.json (contrato §3)

uso: uv run python align.py <video_dir>

Algoritmo completo, limiares e pesos: ../references/algoritmo.md
Resumo: âncoras (2–3 primeiras palavras, rapidfuzz ratio >= 80) -> janelas de 0,6n–1,4n tokens
-> melhor janela por similaridade Levenshtein em listas de palavras -> flags -> disputa entre
linhas parecidas (programação dinâmica monotônica) -> escolha do take (último limpo) -> status.

Locutores (método ChatGPT-monitor, edicao/locutores.json — roda o locutores.py antes se estiver ausente ou
desatualizado): takes só com palavras `locutor: carlos` (e `null`, com a flag `locutor_incerto` -> [REVISAR]);
palavras da IA dividem blocos como um separador e nunca viram take. As leituras da IA de cada linha vão para
`linhas[].leituras_ia`; o resto da fala da IA (monitor: "de novo", "próxima"…) vai para `fala_ia` (não para
`nao_mapeado`). Take com voz da IA colada/por cima = `sobreposicao_ia` (impede take limpo); fala da IA dentro de
um silêncio do take = `fala_ia_interna` (vira corte interno na EDL).
"""
from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path

from rapidfuzz import fuzz
from rapidfuzz.distance import LCSseq, Levenshtein

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (SEPARADORES, edicao, eh_muleta, escrever_json, fmt_t, ler_json, log, mean,  # noqa: E402
                    norm_palavra, palavras_da_fala, rel, resolver_video_dir, carregar_roteiro)

# ---------------------------------------------------------------- parâmetros
GAP_TAKE = 1.5          # s — silêncio que separa takes
PAUSA_INTERNA = 0.7     # s — pausa dentro da linha que vira flag + corte interno
ANCORA_MIN = 80         # rapidfuzz ratio (0-100) das primeiras palavras
ANCORA2_MIN = 85        # âncora secundária (1ª palavra perdida pela transcrição)
JANELA = (0.6, 1.4)     # tamanho da janela em múltiplos de n (tokens do roteiro)
SIM_OK = 0.80
# 2026-09-17 (Carlos): "eu posso improvisar… o editor tem que levar em consideração a forma que eu falo".
# Improviso é uma versão VÁLIDA da linha, não take ruim. Antes 0,60 — abaixo disso a linha virava `faltando`
# e a frase sumia do vídeo. Agora 0,45: entra como `parafrase` e a legenda passa a seguir a FALA (edl.py).
SIM_PARAFRASE = 0.45
SIM_CANDIDATO = 0.40    # abaixo disso o candidato só fica se for falso começo
# 2026-09-18 (Carlos): "eu improvisei algumas partes… tudo que vem último é o que vale".
# Busca SEM âncora, para as linhas cujo COMEÇO foi improvisado: a âncora só dispara quando as 2–3 primeiras
# palavras do roteiro aparecem faladas, então improvisar o começo deixava a linha com `takes: []` (nem take
# fraco) e ela sumia do vídeo. Baixar SIM_PARAFRASE não resolve isso — não há candidato para pontuar.
F1_LIVRE = 0.45         # busca sem âncora: mede-se COBERTURA DE CONTEÚDO (F1 entre as palavras do take e as
                        # da linha), não distância palavra a palavra. Improvisando ele diz MAIS palavras que o
                        # roteiro, e a similaridade de Levenshtein pune cada palavra a mais — com ela o editor
                        # escolhia o pedacinho curto que "bate" em vez da frase inteira que ele disse.
COB_IMPROVISO = 0.55    # take sem âncora entra mesmo com `sim` baixo se cobrir este tanto do conteúdo da linha
JANELA_LIVRE = (0.5, 2.2)   # janela em múltiplos de n: ele alonga muito a frase ao improvisar
FIM_FRASE = 0.45        # s — silêncio que fecha uma frase. O take sem âncora TEM de terminar aqui (ou na fala
                        # da IA / no fim do trecho): nunca no meio de uma frase dele. Começar depois do início
                        # é permitido (é assim que se apara um falso começo) — acabar antes do fim, não.
GAP_SUPER = 15.0        # s — junta pedaços da MESMA linha separados pela fala da IA (ele pede à IA para
                        # partir a linha em blocos: "vamos dividir em quatro blocos") ; a EDL corta o miolo
FALSO_PREFIXO = 0.85
FALSO_COBERTURA = 0.60
CONF_MIN = 0.60
LAMBDA_ORDEM = 0.10     # penalidade da PD por "voltar" no roteiro
SUBST_OK = 60           # ratio p/ considerar substituição como a mesma palavra (grafia)
PESOS = {"sim": 0.55, "cobertura": 0.15, "fluencia": 0.10, "recencia": 0.10, "confianca": 0.10}
TROPECOS = {"false_start", "recomeco", "final_cortado", "sobreposicao_ia"}   # impedem "take limpo"
MARGEM_IA_INTERNA = 0.04   # s — fala da IA dentro de um silêncio do take, com esta folga das palavras do Carlos


# ---------------------------------------------------------------- estruturas
@dataclass
class Tok:
    t: str
    wi: int          # 1ª palavra (índice global i)
    wf: int          # última palavra
    ini: float
    fim: float
    conf: float
    sep: bool = False
    ia: bool = False         # palavra da IA (locutor "ia"): divide blocos, nunca entra num take
    incerto: bool = False    # locutor null: pode entrar num take, mas marca `locutor_incerto`


@dataclass
class LinhaRot:
    id: str
    alt: str | None
    fala: str
    palavras: list[str]          # grafia do roteiro
    toks: list[str]              # tokens normalizados
    tok_palavra: list[int]       # token -> índice da palavra do roteiro
    pausa_depois: str = "normal"

    @property
    def n(self) -> int:
        return len(self.toks)


@dataclass
class Cand:
    linha: str
    fonte: str
    p: int           # índice do token inicial (na lista da fonte)
    e: int           # fim exclusivo
    sim: float = 0.0
    prefixo: float = 0.0
    cobertura: float = 0.0
    flags: list = field(default_factory=list)
    muletas: list = field(default_factory=list)     # índices globais de palavras
    pausas: list = field(default_factory=list)      # [[t0, t1]]
    conf: float = 1.0
    score: float = 0.0
    ordem: tuple = ()


class Vocab:
    def __init__(self):
        self.m: dict[str, int] = {}

    def ids(self, toks):
        return [self.m.setdefault(t, len(self.m)) for t in toks]


# ---------------------------------------------------------------- preparação
def preparar_roteiro(roteiro: dict) -> list[LinhaRot]:
    linhas = []
    for l in roteiro.get("linhas", []):
        pal = palavras_da_fala(l.get("fala", ""))
        toks, tp = [], []
        for j, w in enumerate(pal):
            for t in norm_palavra(w):
                toks.append(t)
                tp.append(j)
        linhas.append(LinhaRot(l["id"], l.get("alternativa_de"), l.get("fala", ""), pal, toks, tp,
                               l.get("pausa_depois") or "normal"))
    return linhas


def _parecida(t: str, vocab_longo: list[str], corte: int) -> str | None:
    from rapidfuzz import process
    r = process.extractOne(t, vocab_longo, scorer=fuzz.ratio, score_cutoff=corte)
    return r[0] if r else None


def _dicionario_fala() -> dict[str, str]:
    """`00-marca/fala-carlos.json` → {o que o ASR ouve: palavra do roteiro}.

    O jeito de falar dele não é erro: "pronto" por "prompt" tem ratio 60 e nunca passaria pelo corte de 88
    da aproximação por grafia. Aqui a troca é explícita, e a lista cresce a cada vídeo (2026-09-17).
    """
    from common import ROOT  # noqa: PLC0415
    d = ler_json(ROOT / "00-marca" / "fala-carlos.json") or {}
    saida: dict[str, str] = {}
    for ouvido, alvo in (d.get("pronuncia") or {}).items():
        if ouvido.startswith("_"):
            continue
        for tk in norm_palavra(ouvido):
            saida[tk] = " ".join(norm_palavra(alvo))
    return saida


def tokens_por_fonte(palavras: list[dict], linhas: list[LinhaRot], aproximar: bool = True) -> dict[str, list[Tok]]:
    """Tokens normalizados por fonte, com:
    - compostos quebrados pela transcrição juntados ("chat IGPT" -> "chatgpt"),
    - (aproximar=True) grafias quase iguais a uma palavra do roteiro trocadas por ela (ratio >= 88),
    - separadores falados marcados (sep=True)."""
    vocab = {t for l in linhas for t in l.toks}
    vocab_longo = sorted(t for t in vocab if len(t) >= 4)
    frases_roteiro = [" " + " ".join(l.toks) + " " for l in linhas]
    out: dict[str, list[Tok]] = {}
    for w in palavras:
        loc = w.get("locutor", "carlos")          # sem o campo (gravação antiga / verify) = Carlos
        for t in norm_palavra(w["texto"]):
            out.setdefault(w["fonte"], []).append(
                Tok(t, w["i"], w["i"], w["inicio"], w["fim"], w.get("conf", 1.0), ia=loc == "ia", incerto=loc is None))
    for f, toks in out.items():
        merged: list[Tok] = []
        for tk in toks:
            if merged and merged[-1].ia == tk.ia:
                a = merged[-1]
                cat = a.t + tk.t
                if (a.t not in vocab or tk.t not in vocab) and tk.ini - a.fim < 0.3 and a.wf != tk.wi:
                    alvo = cat if cat in vocab else _parecida(cat, vocab_longo, 85)
                    if alvo and fuzz.ratio(a.t, alvo) < 85 and fuzz.ratio(tk.t, alvo) < 85:
                        merged[-1] = Tok(alvo, a.wi, tk.wf, a.ini, tk.fim, min(a.conf, tk.conf), ia=a.ia,
                                         incerto=a.incerto or tk.incerto)
                        continue
            merged.append(tk)
        if aproximar:
            fala = _dicionario_fala()
            for tk in merged:
                # 1º o jeito dele falar (lista explícita): "pronto"->"prompt", "antropica"->"anthropic".
                # Só troca se a palavra-alvo existir no roteiro — assim o dicionário nunca inventa texto.
                alvo_fala = fala.get(tk.t)
                if alvo_fala and alvo_fala in vocab:
                    tk.t = alvo_fala
                    continue
                if tk.t not in vocab and len(tk.t) >= 5:
                    alvo = _parecida(tk.t, vocab_longo, 88)
                    if alvo:
                        tk.t = alvo
        # separadores falados ("de novo", "corta"...)
        k = 0
        while k < len(merged):
            for pat in SEPARADORES:
                seg = [x.t for x in merged[k:k + len(pat)]]
                if seg != pat or any(x.ia for x in merged[k:k + len(pat)]):   # "de novo" da IA -> fala_ia
                    continue
                roteirizado = any(" " + " ".join(pat) + " " in fr for fr in frases_roteiro)
                if roteirizado:
                    antes = merged[k].ini - merged[k - 1].fim if k > 0 else 9
                    fim = k + len(pat)
                    depois = merged[fim].ini - merged[fim - 1].fim if fim < len(merged) else 9
                    if antes < 0.3 or depois < 0.3:
                        continue
                for x in merged[k:k + len(pat)]:
                    x.sep = True
                k += len(pat) - 1
                break
            k += 1
        out[f] = merged
    return out


def blocos(toks: list[Tok]) -> list[tuple[int, int]]:
    """Faixas [b0, b1) sem separadores, sem fala da IA e sem silêncio > GAP_TAKE."""
    res, b0 = [], None
    for k, tk in enumerate(toks):
        if tk.sep or tk.ia:
            if b0 is not None:
                res.append((b0, k))
            b0 = None
            continue
        if b0 is None:
            b0 = k
        elif tk.ini - toks[k - 1].fim > GAP_TAKE:
            res.append((b0, k))
            b0 = k
    if b0 is not None:
        res.append((b0, len(toks)))
    return res


# ---------------------------------------------------------------- alinhamento fino
def alinhar_ids(a: list[int], b: list[int]):
    """Pares (i_a, j_b) casados (equal/replace) + inserções em a (sem par) + faltas em b."""
    pares, sobra_a, falta_b = [], [], []
    for op in Levenshtein.opcodes(a, b):
        if op.tag == "equal" or op.tag == "replace":
            la, lb = op.src_end - op.src_start, op.dest_end - op.dest_start
            m = min(la, lb)
            for k in range(m):
                pares.append((op.src_start + k, op.dest_start + k, op.tag == "equal"))
            sobra_a += range(op.src_start + m, op.src_end)
            falta_b += range(op.dest_start + m, op.dest_end)
        elif op.tag == "delete":
            sobra_a += range(op.src_start, op.src_end)
        elif op.tag == "insert":
            falta_b += range(op.dest_start, op.dest_end)
    return pares, sobra_a, falta_b


def mapear(take_toks: list[str], linha: LinhaRot):
    """-> (tok_take -> palavra do roteiro | None, índices de tokens de muleta, tokens do roteiro casados)."""
    voc = Vocab()
    a, b = voc.ids(take_toks), voc.ids(linha.toks)
    pares, sobra, _ = alinhar_ids(a, b)
    mapa: dict[int, int | None] = {i: None for i in range(len(a))}
    casados = set()
    for i, j, igual in pares:
        if igual or fuzz.ratio(take_toks[i], linha.toks[j]) >= SUBST_OK:
            mapa[i] = linha.tok_palavra[j]
            casados.add(j)
    muletas = [i for i in sobra if eh_muleta(take_toks[i])]
    for i, j, igual in pares:        # muleta "substituindo" palavra muito diferente também é muleta
        if not igual and mapa[i] is None and eh_muleta(take_toks[i]) and not eh_muleta(linha.toks[j]):
            muletas.append(i)
    return mapa, sorted(set(muletas)), casados


def metricas(c: Cand, toks: list[Tok], linha: LinhaRot, voc: Vocab) -> None:
    # só as palavras DELE contam como texto do take: um candidato pode atravessar a fala da IA (linha dita
    # em pedaços), e essas palavras não são dele — o intervalo vira pausa interna e a EDL corta (2026-09-18).
    tt = [x for x in toks[c.p:c.e] if not (x.ia or x.sep)]
    if not tt:
        c.sim = c.cobertura = c.prefixo = c.conf = 0.0
        c.flags = ["vazio"]
        return
    ts = [x.t for x in tt]
    a, b = voc.ids(ts), voc.ids(linha.toks)
    n = max(1, linha.n)
    c.sim = round(Levenshtein.normalized_similarity(a, b), 3)
    c.prefixo = round(Levenshtein.normalized_similarity(a, b[:len(a)]), 3) if a else 0.0
    mapa, mul, casados = mapear(ts, linha)
    c.cobertura = round(min(1.0, LCSseq.similarity(a, b) / n), 3)
    c.conf = round(mean(x.conf for x in tt), 3) if tt else 0.0
    flags = []
    if c.prefixo >= FALSO_PREFIXO and c.cobertura < FALSO_COBERTURA:
        flags.append("false_start")
    if len(b) >= 2:
        big = (b[0], b[1])
        n_take = sum(1 for k in range(1, len(a) - 1) if (a[k], a[k + 1]) == big)
        n_rot = sum(1 for k in range(1, len(b) - 1) if (b[k], b[k + 1]) == big)
        if n_take > n_rot:
            flags.append("recomeco")
    c.muletas = sorted({tt[i].wi for i in mul if 0 < i < len(tt) - 1})
    if mul:
        flags.append("muleta")
    c.pausas = [[round(tt[k - 1].fim, 3), round(tt[k].ini, 3)] for k in range(1, len(tt))
                if tt[k].ini - tt[k - 1].fim > PAUSA_INTERNA and tt[k].wi != tt[k - 1].wi]
    if c.pausas:
        flags.append("pausa_interna")
    ult = list(range(max(0, n - 2), n)) if n >= 3 else [n - 1]
    if "false_start" not in flags and not any(j in casados for j in ult):
        flags.append("final_cortado")
    if c.conf < CONF_MIN:
        flags.append("baixa_confianca")
    if any(x.incerto for x in tt):
        flags.append("locutor_incerto")
    c.flags = flags


# ---------------------------------------------------------------- candidatos
def candidatos_linha(linha: LinhaRot, fonte: str, toks: list[Tok], voc: Vocab) -> list[Cand]:
    n = linha.n
    if n == 0 or not toks:
        return []
    k = 3 if n >= 5 else min(2, n)
    anc = " ".join(linha.toks[:k])
    anc2 = " ".join(linha.toks[1:1 + k]) if n >= 5 else None
    # repetições do início dentro do próprio roteiro (não são recomeço)
    rep = [d for d in range(1, n - k + 1) if linha.toks[d:d + k] == linha.toks[:k]]
    b = voc.ids(linha.toks)
    out: list[Cand] = []
    for b0, b1 in blocos(toks):
        prim, sec = [], []
        for p in range(b0, b1):
            kk = min(k, b1 - p)
            if kk < min(2, n):
                continue
            s = " ".join(x.t for x in toks[p:p + kk])
            if fuzz.ratio(s, " ".join(linha.toks[:kk])) >= ANCORA_MIN:
                prim.append(p)
            elif anc2 and b1 - p >= k and fuzz.ratio(s, anc2) >= ANCORA2_MIN:
                sec.append(p)
        _ = anc
        for p in prim + sec:
            lim = b1
            for q2 in prim:
                if q2 >= p + 2 and not any(abs((q2 - p) - d) <= 2 for d in rep):
                    lim = min(lim, q2)
                    break
            e_lo = min(p + max(1, math.ceil(JANELA[0] * n)), lim)
            e_hi = min(p + max(1, math.floor(JANELA[1] * n)), lim)
            e_lo = max(e_lo, p + 1)
            melhor, mk = None, None
            for e in range(e_lo, max(e_lo, e_hi) + 1):
                a = voc.ids([x.t for x in toks[p:e]])
                s = Levenshtein.normalized_similarity(a, b)
                chave = (round(s, 4), LCSseq.similarity(a, b), -e)
                if mk is None or chave > mk:
                    mk, melhor = chave, e
            # 2026-10-17 (Fei-Fei, L07 "Ela."): linha de 1–2 palavras só casa como FALA ISOLADA (silêncio
            # >= FIM_FRASE ou borda do bloco dos dois lados). Sem isto, o "Ela" de toda frase dele virava take da
            # L07 (27 takes), e na PD o candidato de 1 palavra (sim 1,0, sobreposição 100 % com a frase inteira)
            # roubava a região das linhas longas — L04, L06, L08, L09, L10, L15, L17, L29 sumiam do vídeo.
            if n <= 2 and not ((p == b0 or toks[p].ini - toks[p - 1].fim >= FIM_FRASE)
                               and (melhor >= b1 or toks[melhor].ini - toks[melhor - 1].fim >= FIM_FRASE)):
                continue
            c = Cand(linha.id, fonte, p, melhor)
            metricas(c, toks, linha, voc)
            if c.sim >= SIM_CANDIDATO or (c.prefixo >= FALSO_PREFIXO and (c.e - c.p >= 2 or n <= 2)):
                out.append(c)
    # remove duplicatas da mesma linha (sobreposição > 50%)
    out.sort(key=lambda c: (-c.sim, -(c.e - c.p)))
    aceitos: list[Cand] = []
    for c in out:
        if all(sobrepos(c, d) <= 0.5 for d in aceitos):
            aceitos.append(c)
    return aceitos


def regioes_carlos(toks: list[Tok]) -> list[list[int]]:
    """Grupos de índices de palavras DELE que podem pertencer à mesma linha. O grupo continua por cima da
    fala da IA (ele repete a linha em pedaços, com a IA lendo o pedaço seguinte no meio) e quebra num
    separador falado ("de novo", "corta") ou num silêncio dele maior que GAP_SUPER."""
    grupos: list[list[int]] = []
    atual: list[int] = []
    for k, x in enumerate(toks):
        if x.sep:
            if atual:
                grupos.append(atual)
            atual = []
            continue
        if x.ia:
            continue
        if atual and x.ini - toks[atual[-1]].fim > GAP_SUPER:
            grupos.append(atual)
            atual = []
        atual.append(k)
    if atual:
        grupos.append(atual)
    return grupos


def candidatos_livres(linha: LinhaRot, fonte: str, toks: list[Tok], voc: Vocab) -> list[Cand]:
    """Candidatos SEM âncora, para a linha que o improviso deixou sem nenhum candidato (`takes: []`).
    Varre toda a fala dele por janelas de 0,5n–2,2n palavras, inclusive janelas que atravessam a fala da IA."""
    n = linha.n
    if n == 0 or not toks:
        return []
    b = voc.ids(linha.toks)
    lo = max(2, math.ceil(JANELA_LIVRE[0] * n))
    hi = max(lo, math.ceil(JANELA_LIVRE[1] * n))
    brutos: list[tuple[float, int, int]] = []
    for g in regioes_carlos(toks):
        # posições onde uma frase dele COMEÇA (início do trecho ou depois de uma pausa) e onde ela TERMINA
        # (fim do trecho ou antes de uma pausa/da fala da IA)
        pode_ini = {0} | {x for x in range(1, len(g))
                          if toks[g[x]].ini - toks[g[x - 1]].fim >= PAUSA_INTERNA}
        pode_fim = {len(g) - 1} | {x for x in range(len(g) - 1)
                                   if toks[g[x + 1]].ini - toks[g[x]].fim >= FIM_FRASE}
        for i in range(len(g)):
            if i not in pode_ini:
                continue
            for j in range(i + lo, min(len(g), i + hi) + 1):
                if j - 1 not in pode_fim:
                    continue
                sel = g[i:j]
                p, e = sel[0], sel[-1] + 1
                n_ia = sum(1 for x in toks[p:e] if x.ia)
                if n_ia > 1.5 * len(sel):          # miolo de IA maior que a fala dele: não é uma linha só
                    continue
                a = voc.ids([toks[k].t for k in sel])
                lcs = LCSseq.similarity(a, b)
                if not lcs:
                    continue
                prec, rec = lcs / len(a), lcs / n
                f1 = 2 * prec * rec / (prec + rec)
                if f1 >= F1_LIVRE:
                    brutos.append((round(f1, 4), p, e))
    brutos.sort(key=lambda x: (-x[0], -(x[2] - x[1])))   # empate: fica a janela MAIOR (a frase inteira)
    out: list[Cand] = []
    for f1, p, e in brutos:
        c = Cand(linha.id, fonte, p, e)
        if any(sobrepos(c, d) > 0.5 for d in out):
            continue
        metricas(c, toks, linha, voc)
        c.flags.append("sem_ancora")
        out.append(c)
        if len(out) >= 6:
            break
    return out


def sobrepos(a: Cand, b: Cand) -> float:
    if a.fonte != b.fonte:
        return 0.0
    inter = min(a.e, b.e) - max(a.p, b.p)
    if inter <= 0:
        return 0.0
    return inter / max(1, min(a.e - a.p, b.e - b.p))


# ---------------------------------------------------------------- disputa entre linhas (PD)
def resolver_donos(cands: list[Cand], idx_principal: dict[str, int]) -> list[Cand]:
    """Agrupa candidatos sobrepostos de linhas diferentes e decide o dono de cada região com
    uma PD (Viterbi) que prefere seguir a ordem do roteiro (penalidade LAMBDA_ORDEM ao voltar)."""
    cands = sorted(cands, key=lambda c: c.ordem)
    pai = list(range(len(cands)))

    def raiz(x):
        while pai[x] != x:
            pai[x] = pai[pai[x]]
            x = pai[x]
        return x

    for i in range(len(cands)):
        for j in range(i + 1, len(cands)):
            if cands[j].fonte != cands[i].fonte or cands[j].p >= cands[i].e + 50:
                continue
            if cands[i].linha != cands[j].linha and sobrepos(cands[i], cands[j]) > 0.5:
                pai[raiz(j)] = raiz(i)
    grupos: dict[int, list[Cand]] = {}
    for i, c in enumerate(cands):
        grupos.setdefault(raiz(i), []).append(c)
    clusters = sorted(grupos.values(), key=lambda g: min(c.ordem for c in g))
    dp = {0: (0.0, [])}
    for g in clusters:
        rotulos = {}
        for c in g:
            rotulos[c.linha] = max(rotulos.get(c.linha, 0.0), c.sim)
        nd = {}
        for s, (sc, cam) in dp.items():
            for rot, e in rotulos.items():
                m = idx_principal.get(rot)
                ns, pen = (s, 0.0) if m is None else (m, LAMBDA_ORDEM if m < s else 0.0)
                v = sc + e - pen
                if ns not in nd or v > nd[ns][0]:
                    nd[ns] = (v, cam + [rot])
        dp = nd
    caminho = max(dp.values(), key=lambda x: x[0])[1] if dp else []
    donos = []
    for g, rot in zip(clusters, caminho):
        donos += [c for c in g if c.linha == rot]
    return donos


def aparar_sobreposicoes(donos: list[Cand], toks: dict[str, list[Tok]], linhas: dict[str, LinhaRot],
                         voc: Vocab) -> list[Cand]:
    """Sobreposição residual (< 50%) entre linhas diferentes: apara o fim do take anterior."""
    donos = sorted(donos, key=lambda c: c.ordem)
    res: list[Cand] = []
    for c in donos:
        if res and res[-1].fonte == c.fonte and res[-1].e > c.p:
            a = res[-1]
            if a.linha == c.linha:
                if c.sim > a.sim:
                    res[-1] = c
                continue
            a.e = c.p
            if a.e - a.p < 1:
                res.pop()
            else:
                metricas(a, toks[a.fonte], linhas[a.linha], voc)
        res.append(c)
    return res


# ---------------------------------------------------------------- escolha
def escolher(takes: list[dict]) -> tuple[str | None, str, str]:
    """-> (take_id escolhido, status, motivo)"""
    limpos = [t for t in takes if t["sim"] >= SIM_OK and not (set(t["flags"]) & TROPECOS)]
    if limpos:
        t = limpos[-1]
        extra = []
        if "muleta" in t["flags"]:
            extra.append("muleta cortada internamente")
        if "pausa_interna" in t["flags"]:
            extra.append("pausa interna encurtada")
        if "fala_ia_interna" in t["flags"]:
            extra.append("fala da IA no meio cortada internamente")
        pulados = [x["take_id"].split("-")[-1] for x in takes[takes.index(t) + 1:]
                   if "sobreposicao_ia" in x["flags"] and x["sim"] >= SIM_OK]
        if pulados:
            extra.append(f"{', '.join(pulados)} descartado(s): voz da IA por cima")
        motivo = (f"último take limpo{' sem voz da IA' if pulados else ''} (sim {t['sim']:.2f})"
                  + (f"; {', '.join(extra)}" if extra else ""))
        if "baixa_confianca" in t["flags"]:
            return t["take_id"], "revisar", motivo + "; transcrição com confiança baixa — conferir"
        if "locutor_incerto" in t["flags"]:
            return t["take_id"], "revisar", motivo + "; locutor incerto em alguma palavra (voz da IA?) — conferir"
        return t["take_id"], "ok", motivo
    def serve(t: dict) -> bool:
        # improviso: a frase dele pode ficar longe do roteiro palavra a palavra e ainda dizer a mesma coisa —
        # aí o que vale é quanto do conteúdo da linha ele cobriu, não a distância de edição (2026-09-18)
        return t["sim"] >= SIM_PARAFRASE or ("sem_ancora" in t["flags"] and t["cobertura"] >= COB_IMPROVISO)

    validos = [t for t in takes if serve(t) and "false_start" not in t["flags"]]
    if not validos:
        # improvisou tanto que todo take ficou marcado como falso começo: melhor a frase dita do que a linha fora
        validos = [t for t in takes if serve(t)]
    if validos:
        # 2026-09-18 (Carlos): "tudo que vem último é o que vale" — ele refaz a linha até ficar do jeito dele,
        # então a última versão é a boa, mesmo que uma anterior pontue mais.
        t = validos[-1]
        melhor = max(validos, key=lambda x: x["score"])
        ia = "; voz da IA por cima — conferir no preview" if "sobreposicao_ia" in t["flags"] else ""
        if melhor["take_id"] != t["take_id"] and melhor["score"] - t["score"] > 0.10:
            ia += (f"; {melhor['take_id']} pontua mais ({melhor['score']:.2f} vs {t['score']:.2f}) — "
                   f"peça a troca se preferir")
        if t["sim"] >= SIM_OK:
            return t["take_id"], "revisar", (f"nenhum take limpo; melhor score {t['score']:.2f} "
                                             f"(sim {t['sim']:.2f}, flags: {', '.join(t['flags'])}){ia}")
        return t["take_id"], "parafrase", f"paráfrase: melhor sim {t['sim']:.2f} (score {t['score']:.2f}){ia}"
    if takes:
        return None, "faltando", f"só tentativas incompletas/fracas ({len(takes)} take(s), melhor sim " \
                                 f"{max(t['sim'] for t in takes):.2f})"
    return None, "faltando", "linha não encontrada na gravação"


def flags_ia(palavras: list[dict], fonte: str, wi: int, wf: int, locutores: dict | None) -> list[str]:
    """`sobreposicao_ia`: a IA fala colada/por cima do take (sem silêncio para cortar) · `fala_ia_interna`: a IA
    fala dentro de um silêncio entre duas palavras do take (a EDL corta)."""
    if not locutores:
        return []
    fl = []
    if any(wi <= s["carlos_i"] <= wf for s in locutores.get("sobreposicoes") or [] if s.get("fonte") == fonte):
        fl.append("sobreposicao_ia")
    ws = [palavras[i] for i in range(wi, wf + 1) if palavras[i]["fonte"] == fonte and palavras[i].get("locutor") != "ia"]
    if not ws:
        return fl
    t0, t1 = ws[0]["inicio"], ws[-1]["fim"]
    for za, zb in (locutores.get("zonas_ia") or {}).get(fonte, []):
        if zb <= t0 or za >= t1:
            continue
        dentro = any(a["fim"] + MARGEM_IA_INTERNA <= za and zb <= b["inicio"] - MARGEM_IA_INTERNA
                     for a, b in zip(ws[:-1], ws[1:]))
        fl.append("fala_ia_interna" if dentro else "sobreposicao_ia")
    return list(dict.fromkeys(fl))


def leituras_da_ia(palavras: list[dict], linhas: list[LinhaRot], fontes_ordem: list[str], ordem_f: dict,
                   idx_principal: dict, voc: Vocab) -> tuple[dict[str, list[dict]], set[int]]:
    """Alinha só as palavras da IA às linhas (para registro/depuração: `leituras_ia`). Nunca viram take."""
    pal_ia = [{k: v for k, v in w.items() if k != "locutor"} for w in palavras if w.get("locutor") == "ia"]
    if not pal_ia:
        return {}, set()
    toks_ia = tokens_por_fonte(pal_ia, linhas)
    lmap = {l.id: l for l in linhas}
    cands = []
    for l in linhas:
        for f in fontes_ordem:
            for c in candidatos_linha(l, f, toks_ia.get(f, []), voc):
                c.ordem = (ordem_f[f], toks_ia[f][c.p].ini)
                cands.append(c)
    donos = aparar_sobreposicoes(resolver_donos(cands, idx_principal), toks_ia, lmap, voc)
    leituras: dict[str, list[dict]] = {}
    usados: set[int] = set()
    for c in sorted(donos, key=lambda c: c.ordem):
        if c.sim < SIM_PARAFRASE:
            continue
        tt = toks_ia[c.fonte][c.p:c.e]
        wi, wf = tt[0].wi, tt[-1].wf
        leituras.setdefault(c.linha, []).append({
            "fonte": c.fonte, "inicio": palavras[wi]["inicio"], "fim": palavras[wf]["fim"], "sim": c.sim,
            "i_ini": wi, "i_fim": wf,
            "texto": " ".join(palavras[i]["texto"] for i in range(wi, wf + 1) if palavras[i].get("locutor") == "ia")})
        usados.update(i for i in range(wi, wf + 1) if palavras[i].get("locutor") == "ia")
    return leituras, usados


def alinhar(transcricao: dict, roteiro: dict, locutores: dict | None = None) -> dict:
    palavras = transcricao.get("palavras", [])
    fontes_ordem = sorted({w["fonte"] for w in palavras})
    ordem_f = {f: k for k, f in enumerate(fontes_ordem)}
    linhas = preparar_roteiro(roteiro)
    lmap = {l.id: l for l in linhas}
    principais = [l for l in linhas if not l.alt]
    idx_principal = {l.id: k + 1 for k, l in enumerate(principais)}
    toks = tokens_por_fonte(palavras, linhas)
    voc = Vocab()
    cands: list[Cand] = []
    for l in linhas:
        achados: list[Cand] = []
        for f in fontes_ordem:
            achados += [(c, f) for c in candidatos_linha(l, f, toks.get(f, []), voc)]
        # nenhum take limpo -> ou a âncora não disparou (começo improvisado), ou disparou e a janela pegou só
        # um pedaço da frase. Nos dois casos vale procurar a linha inteira sem âncora (2026-09-18)
        if not any(c.sim >= SIM_OK for c, _ in achados):
            for f in fontes_ordem:
                achados += [(c, f) for c in candidatos_livres(l, f, toks.get(f, []), voc)]
        for c, f in achados:
            c.ordem = (ordem_f[f], toks[f][c.p].ini)
            cands.append(c)
    donos = resolver_donos(cands, idx_principal)
    donos = aparar_sobreposicoes(donos, toks, lmap, voc)

    por_linha: dict[str, list[Cand]] = {}
    for c in donos:
        por_linha.setdefault(c.linha, []).append(c)
    leituras, usados_ia = leituras_da_ia(palavras, linhas, fontes_ordem, ordem_f, idx_principal, voc)
    usados = {w["i"] for w in palavras if w.get("locutor") == "ia"}     # fala da IA nunca é "não mapeado"
    saida_linhas, resumo = [], {"ok": 0, "revisar": 0, "parafrase": 0, "faltando": 0}
    for l in linhas:
        cs = sorted(por_linha.get(l.id, []), key=lambda c: c.ordem)
        takes = []
        for k, c in enumerate(cs):
            tt = toks[c.fonte][c.p:c.e]
            wi, wf = tt[0].wi, tt[-1].wf
            for fl in flags_ia(palavras, c.fonte, wi, wf, locutores):
                if fl not in c.flags:
                    c.flags.append(fl)
            n_trop = len(set(c.flags) & TROPECOS)
            # Punição leve (antes 0,34 por tropeço e 0,1 por muleta): o Carlos é gago e come o fim das
            # palavras — punir isso fazia o sistema escolher sempre o take mais mecânico, que é justamente
            # o que soa lido. O que importa é ele ter dito a frase, não ter dito sem tropeçar (2026-09-17).
            flu = max(0.0, 1 - 0.12 * n_trop - 0.04 * len(c.muletas) - 0.06 * len(c.pausas))
            rec = k / (len(cs) - 1) if len(cs) > 1 else 1.0
            c.score = round(PESOS["sim"] * c.sim + PESOS["cobertura"] * c.cobertura + PESOS["fluencia"] * flu
                            + PESOS["recencia"] * rec + PESOS["confianca"] * c.conf, 3)
            usados.update(range(wi, wf + 1))
            takes.append({
                "take_id": f"{l.id}-T{k + 1}", "fonte": c.fonte, "i_ini": wi, "i_fim": wf,
                "inicio": palavras[wi]["inicio"], "fim": palavras[wf]["fim"],
                "sim": c.sim, "cobertura": c.cobertura, "flags": c.flags, "score": c.score,
                "texto": " ".join(palavras[i]["texto"] for i in range(wi, wf + 1)),
                "prefixo": c.prefixo, "conf": c.conf, "muletas": c.muletas, "pausas": c.pausas,
            })
        esc, status, motivo = escolher(takes)
        li = [{k: v for k, v in x.items() if k in ("fonte", "inicio", "fim", "sim", "texto")}
              for x in leituras.get(l.id, [])]
        if status == "faltando" and li:
            motivo = f"a IA leu a linha ({len(li)}×), mas não há take do Carlos" + (f"; {motivo}" if takes else "")
        item = {"id": l.id, "status": status, "escolhido": esc, "motivo": motivo, "takes": takes, "leituras_ia": li}
        if l.alt:
            item["alternativa_de"] = l.alt
        else:
            resumo[status] += 1
        saida_linhas.append(item)

    separadores, nao_mapeado = [], []
    for f in fontes_ordem:
        for tk in toks.get(f, []):
            if tk.sep:
                usados.update(range(tk.wi, tk.wf + 1))
                if separadores and separadores[-1]["fonte"] == f and tk.ini - separadores[-1]["fim"] < 0.8:
                    separadores[-1]["fim"] = tk.fim
                    separadores[-1]["texto"] += " " + palavras[tk.wi]["texto"]
                else:
                    separadores.append({"fonte": f, "inicio": tk.ini, "fim": tk.fim,
                                        "texto": palavras[tk.wi]["texto"]})
    grupo = None
    for w in palavras:
        if w["i"] in usados:
            grupo = None
            continue
        if grupo and grupo["fonte"] == w["fonte"] and w["i"] == grupo["i_fim"] + 1 and w["inicio"] - grupo["fim"] <= 1.0:
            grupo["fim"] = w["fim"]
            grupo["i_fim"] = w["i"]
            grupo["texto"] += " " + w["texto"]
        else:
            grupo = {"fonte": w["fonte"], "inicio": w["inicio"], "fim": w["fim"], "texto": w["texto"],
                     "i_ini": w["i"], "i_fim": w["i"]}
            nao_mapeado.append(grupo)
    for g in nao_mapeado:
        g["so_muletas"] = all(all(eh_muleta(t) for t in norm_palavra(palavras[i]["texto"]) or ["x"])
                              for i in range(g["i_ini"], g["i_fim"] + 1))
    resumo["nao_mapeado"] = len([g for g in nao_mapeado if not g["so_muletas"]])
    # fala da IA que não é leitura de linha (monitor: "de novo", "repete", "próxima", "faltou a palavra X"…)
    fala_ia, grupo = [], None
    for w in palavras:
        if w.get("locutor") != "ia" or w["i"] in usados_ia:
            grupo = None
            continue
        if grupo and grupo["fonte"] == w["fonte"] and w["i"] == grupo["i_fim"] + 1 and w["inicio"] - grupo["fim"] <= 1.0:
            grupo["fim"], grupo["i_fim"] = w["fim"], w["i"]
            grupo["texto"] += " " + w["texto"]
        else:
            grupo = {"fonte": w["fonte"], "inicio": w["inicio"], "fim": w["fim"], "texto": w["texto"],
                     "i_ini": w["i"], "i_fim": w["i"]}
            fala_ia.append(grupo)
    resumo["leituras_ia"] = sum(len(v) for v in leituras.values())
    resumo["fala_ia"] = len(fala_ia)
    resumo["palavras_locutor_incerto"] = sum(1 for w in palavras if "locutor" in w and w["locutor"] is None)
    loc_res = None
    if locutores:
        loc_res = {"metodo": locutores.get("metodo"), "n_locutores": locutores.get("n_locutores"),
                   "confianca_papel": (locutores.get("papel") or {}).get("confianca"),
                   "sobreposicoes": len(locutores.get("sobreposicoes") or []),
                   "segundos_ia": (locutores.get("estatisticas") or {}).get("segundos_ia")}
    return {"linhas": saida_linhas, "nao_mapeado": nao_mapeado, "separadores": separadores, "fala_ia": fala_ia,
            "locutores": loc_res, "resumo": resumo,
            "parametros": {"gap_take": GAP_TAKE, "pausa_interna": PAUSA_INTERNA, "sim_ok": SIM_OK,
                           "sim_parafrase": SIM_PARAFRASE, "pesos": PESOS}}


def imprimir_resumo(al: dict) -> None:
    marca = {"ok": "[OK]", "revisar": "[REVISAR]", "parafrase": "[PARAFRASE]", "faltando": "[FALTANDO]"}
    if al.get("locutores") and al["locutores"].get("n_locutores") == 2:
        lr = al["locutores"]
        log(f"locutores: {lr['metodo']} · IA identificada (confiança {lr['confianca_papel']}) · "
            f"{lr['segundos_ia']}s de fala da IA fora dos takes · sobreposições {lr['sobreposicoes']}")
    log(f"{'LINHA':<6} {'STATUS':<12} {'ESCOLHIDO':<10} {'SIM':>5} {'TAKES':>5} {'IA':>3}  DETALHES")
    for l in al["linhas"]:
        esc = next((t for t in l["takes"] if t["take_id"] == l["escolhido"]), None)
        det = []
        for t in l["takes"]:
            if t["take_id"] != l["escolhido"]:
                det.append(f"{t['take_id'].split('-')[-1]}:{t['sim']:.2f}"
                           + (f"({','.join(t['flags'])})" if t["flags"] else ""))
        if esc and esc["flags"]:
            det.insert(0, "escolhido:" + ",".join(esc["flags"]))
        alt = f" (alt de {l['alternativa_de']})" if l.get("alternativa_de") else ""
        log(f"{l['id']:<6} {marca[l['status']]:<12} {(l['escolhido'] or '—'):<10} "
            f"{(esc['sim'] if esc else 0):>5.2f} {len(l['takes']):>5} {len(l.get('leituras_ia') or []):>3}  "
            f"{' | '.join(det)}{alt}")
    r = al["resumo"]
    log(f"resumo: ok {r['ok']} · revisar {r['revisar']} · parafrase {r['parafrase']} · faltando {r['faltando']}"
        f" · trechos não mapeados {r['nao_mapeado']} · separadores {len(al['separadores'])}"
        + (f" · leituras da IA {r['leituras_ia']} · fala da IA (monitor) {r['fala_ia']}" if r.get("leituras_ia")
           or r.get("fala_ia") else ""))
    for g in al["nao_mapeado"]:
        if not g["so_muletas"]:
            log(f"   não mapeado [{g['fonte']} {g['inicio']:.2f}-{g['fim']:.2f}]: {g['texto']}")
    for g in al.get("fala_ia") or []:
        log(f"   fala da IA  [{g['fonte']} {fmt_t(g['inicio'])}]: {g['texto']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video_dir")
    args = ap.parse_args()
    vd = resolver_video_dir(args.video_dir)
    ed = edicao(vd)
    roteiro = carregar_roteiro(vd)
    import locutores as LOC
    if LOC.desatualizado(vd):
        log("[align] edicao/locutores.json ausente ou mais velho que a transcrição — rodando locutores.py antes")
        LOC.executar(vd)
    loc = LOC.carregar(vd)
    tr = ler_json(ed / "transcricao.json")
    al = alinhar(tr, roteiro, loc)
    escrever_json(ed / "alinhamento.json", al)
    imprimir_resumo(al)
    log(f"[align] -> {rel(vd, ed / 'alinhamento.json')}")


if __name__ == "__main__":
    main()
