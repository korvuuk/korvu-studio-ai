"""Capas Fei-Fei Li com FOTO real preenchendo 1080x1920 (sem margem preta, sem blur, sem esticar). Roda sozinho.
Adaptado de videos/2026-10-20-geoffrey-hinton/capa/modelo-foto/compor_foto.py (padrao aprovado em 15/10).
uv run python compor_foto.py   -> capa-<id>-previa.png, grade-<id>-previa.png, contato.jpg, medidas.json"""
import os, sys, json, math, itertools
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
Image.MAX_IMAGE_PIXELS = None
AQUI = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(AQUI + "/../..")
FOTOS = PROJ + "/material/fotos/"
FRAMES = AQUI + "/frames/"
W, H = 1080, 1920
BG = (13, 13, 13); BRANCO = (242, 242, 242); CINZA = (170, 170, 170); LARANJA = (232, 80, 2)   # = brand.ts (cinza do Hinton aprovado)

def geist(sz, peso=800):
    f = ImageFont.truetype(AQUI + "/geist.ttf", sz); f.set_variation_by_axes([peso]); return f
def playfair(sz):
    f = ImageFont.truetype(AQUI + "/pf.ttf", sz); f.set_variation_by_axes([700]); return f

def abrir(path):
    return ImageOps.exif_transpose(Image.open(path)).convert("RGB")

def painel(img, box, size, nitidez=False):
    """Recorte REAL (sem preenchimento): box dentro da imagem, mesma proporcao do destino -> resize."""
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    assert 0 <= x0 < x1 <= img.width and 0 <= y0 < y1 <= img.height, ("recorte fora da foto", box, img.size)
    assert abs((x1 - x0) / (y1 - y0) - size[0] / size[1]) < 0.01, ("proporcao", box, size)
    out = img.crop((x0, y0, x1, y1)).resize(size, Image.LANCZOS)
    if nitidez:   # foto ampliada: um pouco de nitidez para nao ficar mole
        out = out.filter(ImageFilter.UnsharpMask(radius=1.6, percent=70, threshold=2))
    return out

def full916(img, cx, y0=0, nitidez=False):
    """Janela 9:16 de altura total (ou a partir de y0 ate o fim) centrada em cx."""
    ch = img.height - y0; cw = int(ch * W / H); x0 = int(round(cx - cw / 2)); x0 = max(0, min(img.width - cw, x0))
    return painel(img, (x0, y0, x0 + cw, y0 + ch), (W, H), nitidez)

def scrim(cv, y0, y1, forca=0.62, y_sai=1450, y_fim=1820):
    """Degrade escuro suave sobre a foto (nao e faixa): sobe em y0->y1, segura, e volta a 0 em y_sai->y_fim."""
    ov = Image.new("L", (W, H), 0)
    for y in range(y0, H):
        if y <= y1: a = forca * (y - y0) / (y1 - y0)
        elif y <= y_sai: a = forca
        else: a = forca * max(0.0, (y_fim - y) / (y_fim - y_sai))
        ov.paste(int(255 * a), (0, y, W, y + 1))
    cv.paste(Image.new("RGB", (W, H), (8, 8, 8)), (0, 0), ov)

def titulo(canvas, palavras, cinza, chave, cor_risco, box, tam_max=130, tam_min=56, sub=None):
    """Titulo Geist ExtraBold (cinza + branco) com UMA palavra em Playfair italico + rabisco. `sub` = linha menor opcional."""
    x0, y0, x1, y1 = box; bw, bh = x1 - x0, y1 - y0
    d = ImageDraw.Draw(canvas); n = len(palavras); melhor = None
    sub_h = 0
    if sub: fs = geist(48, 700); sub_h = 48 * 1.45 + 34
    bh_main = bh - sub_h
    for tam in range(tam_max, tam_min - 1, -2):
        fg, fp = geist(tam), playfair(int(tam * 1.18)); sp = tam * 0.28
        ws = [d.textlength(p, font=(fp if i == chave else fg)) for i, p in enumerate(palavras)]
        lh = tam * 1.0
        for nl in range(1, 4):
            if lh * nl > bh_main: break
            for cuts in itertools.combinations(range(1, n), nl - 1):
                idx = (0,) + cuts + (n,)
                larg = [sum(ws[idx[k]:idx[k + 1]]) + sp * (idx[k + 1] - idx[k] - 1) for k in range(nl)]
                if max(larg) <= bw and (melhor is None or (nl, max(larg)) < melhor[0]): melhor = ((nl, max(larg)), idx)
            if melhor: break
        if melhor: break
    idx = melhor[1]
    linhas = [[(i, palavras[i], (fp if i == chave else fg), ws[i]) for i in range(idx[k], idx[k + 1])] for k in range(len(idx) - 1)]
    y = y0 + (bh - lh * len(linhas) - sub_h) / 2
    for ln in linhas:
        wl = sum(w for *_, w in ln) + sp * (len(ln) - 1); x = x0 + (bw - wl) / 2
        for i, p, f, w in ln:
            cor = CINZA if i < cinza else BRANCO
            dy = tam * 0.04 if i != chave else -tam * 0.10
            d.text((x + 2, y + 3 + dy), p, font=f, fill=(0, 0, 0))  # sombra leve
            d.text((x, y + dy), p, font=f, fill=cor)
            if i == chave:
                by = y + lh * 0.98; pts = []
                for k in range(15): pts.append((x + w * k / 14, by + (5 if k % 2 else -5) + math.sin(k) * 2))
                d.line(pts, fill=cor_risco, width=9, joint="curve")
            x += w + sp
        y += lh
    if sub:
        wl = d.textlength(sub, font=fs); xs = x0 + (bw - wl) / 2; ys = y + 38
        d.text((xs + 2, ys + 3), sub, font=fs, fill=(0, 0, 0)); d.text((xs, ys), sub, font=fs, fill=BRANCO)
    return tam

def credito(cv, txt, y=1655):
    d = ImageDraw.Draw(cv); f = geist(22, 500)
    d.text((W - 38, y + 2), txt, font=f, fill=(0, 0, 0), anchor="rs"); d.text((W - 40, y), txt, font=f, fill=(215, 215, 215), anchor="rs")

# ---- titulos: (palavras, n_cinza, indice_da_chave, cor_do_rabisco, sub) --------------------------------------------
TITS = {
  "A": (["Quem", "é", "a", "madrinha", "da", "IA"], 3, 3, LARANJA, None),
  "B": (["Ela", "chegou", "sem", "falar", "inglês"], 4, 4, LARANJA, "e ensinou a IA a enxergar"),
  "C": (["A", "adolescente", "que", "ensinou", "a", "IA", "a", "ver"], 5, 7, LARANJA, None),
}

# ---- fotos: arquivo, centro-x do rosto (px da foto), y inicial da janela, credito, nitidez -------------------------
FOTO = {
  # CAPA-01 = recorte vertical do retrato N11 (8192x5464, Stanford HAI). O arquivo CAPA-01 cortava o cabelo na direita;
  # aqui a janela 9:16 de altura total (3073x5464, mesma resolucao) e centrada no rosto. Sem ampliar.
  "CAPA01": ("N11-feifei-2025-qeprize-estudio-original.jpg", 4748, 0, "Foto: Stanford HAI", False),
  "CAPA02": ("CAPA-02-feifei-2025-retrato-st-james-getty.jpg", 554, 0, "Foto: Monica Schipper / Getty Images", False),
  "CAPA03": ("CAPA-03-feifei-c2017-retrato-mao-no-rosto.jpg", 420, 0, "Foto: Paul & Daisy Soros Fellowships", True),
}
# caixa do titulo e inicio do degrade por foto (queixo medido na foto)
LAYOUT = {"CAPA01": dict(box=(60, 1010, 1020, 1262), s0=870, s1=1170),
          "CAPA02": dict(box=(60, 1330, 1020, 1600), s0=1240, s1=1400),
          "CAPA03": dict(box=(60, 1130, 1020, 1380), s0=1040, s1=1190)}

LAYOUT_T = {("CAPA01", "B"): dict(box=(60, 975, 1020, 1268))}
CAPA03_L = dict(box=(60, 1040, 1020, 1300), s0=980, s1=1120)

def solo(chave_foto, t):
    arq, cx, y0, cred, nit = FOTO[chave_foto]; L = dict(LAYOUT[chave_foto]); L.update(LAYOUT_T.get((chave_foto, t), {}))
    cv = full916(abrir(FOTOS + arq), cx, y0, nit)
    scrim(cv, L["s0"], L["s1"], y_sai=L.get("y_sai", 1450))
    p, ch, kw, cr, sub = TITS[t]; titulo(cv, p, ch, kw, cr, L["box"], sub=sub); credito(cv, cred)
    return cv

CARLOS = "carlos-pose-55.107.png"     # frame da pose da capa (telefone no ouvido), cadeia de cor do video
def dividida(chave_foto, y_seam=1000, ww=3700, cx=4748):
    arq, _, _, cred, _ = FOTO[chave_foto]
    h = abrir(FOTOS + arq)
    wh = ww * y_seam / W
    x0 = cx - ww / 2
    hp = painel(h, (x0, 0, x0 + ww, wh), (W, y_seam))
    c = abrir(FRAMES + CARLOS)      # 1440x2560
    ph = H - y_seam                 # altura do painel do Carlos
    cs = W / c.width                # 0.75
    sy0 = 371 - 40 / cs             # topo da cabeca na fonte ~ y 371 -> ~40 px abaixo da emenda
    cp = painel(c, (0, sy0, c.width, sy0 + ph / cs), (W, ph))
    cv = Image.new("RGB", (W, H)); cv.paste(hp, (0, 0)); cv.paste(cp, (0, y_seam))
    return cv, cred

def split_completo(chave_foto, t, y_seam=1000, **kw):
    cv, cred = dividida(chave_foto, y_seam, **kw)
    ov = Image.new("L", (W, H), 0)
    for y in range(y_seam - 230, y_seam):
        ov.paste(int(255 * 0.78 * (y - (y_seam - 230)) / 230), (0, y, W, y + 1))
    cv.paste(Image.new("RGB", (W, H), (8, 8, 8)), (0, 0), ov)
    ImageDraw.Draw(cv).rectangle((0, y_seam - 2, W, y_seam + 1), fill=LARANJA)
    p, ch, k, cr, _ = TITS[t]; titulo(cv, p, ch, k, cr, (60, y_seam - 140, 1020, y_seam - 8))
    credito(cv, cred, y=1655)
    return cv

def grade(im): return im.crop((0, 240, W, 1680))

def medir(im):
    g = ImageOps.grayscale(im); w, h = g.size
    def media(box):
        c = g.crop(box); return round(sum(c.tobytes()) / (c.width * c.height), 1)
    return {"topo": media((0, 0, w, 20)), "base": media((0, h - 20, w, h)), "esq": media((0, 0, 20, h)), "dir": media((w - 20, 0, w, h))}

PLANO = [   # (numero, id, descricao, funcao)
    ("A-CAPA01", "Quem é a madrinha da IA · retrato de estúdio", lambda: solo("CAPA01", "A")),
    ("B-CAPA01", "Ela chegou sem falar inglês · retrato de estúdio", lambda: solo("CAPA01", "B")),
    ("C-CAPA01", "A adolescente que ensinou a IA a ver · retrato de estúdio", lambda: solo("CAPA01", "C")),
    ("A-CAPA02", "Quem é a madrinha da IA · close sorrindo (título abaixo da zona segura de 1250)", lambda: solo("CAPA02", "A")),
    ("A-CAPA03", "Quem é a madrinha da IA · mão no queixo (reserva: foto de 760 px ampliada 1,7x, título abaixo da zona segura)", lambda: solo("CAPA03", "A")),
    ("DIV-A-CAPA01", "DIVIDIDA · Quem é a madrinha da IA · Fei-Fei + Carlos", lambda: split_completo("CAPA01", "A")),
]
if __name__ == "__main__":
    sel = sys.argv[1:]
    plano = {}
    for nome, desc, fn in PLANO:
        if sel and nome not in sel: continue
        plano[nome] = fn()
    json_med = {}
    for n, im in plano.items():
        im.save(f"{AQUI}/capa-{n}-previa.png"); grade(im).save(f"{AQUI}/grade-{n}-previa.png"); json_med[n] = medir(im)
    print(json.dumps(json_med))
    if not sel:
        json.dump(json_med, open(AQUI + "/medidas.json", "w"), indent=1)
        # folha de contato numerada (grade 3:4 = como aparece no perfil)
        tw, th, gap, rod = 360, 480, 14, 100; nomes = [n for n, *_ in PLANO if n in plano]
        cols = 4; linhas = math.ceil(len(nomes) / cols)
        sheet = Image.new("RGB", (gap + cols * (tw + gap), gap + linhas * (th + rod + gap)), (30, 30, 30))
        d = ImageDraw.Draw(sheet); fn_ = geist(26, 800); fs_ = geist(17, 500)
        for i, (n, desc, _) in enumerate(PLANO):
            r, c = divmod(i, cols); x = gap + c * (tw + gap); y = gap + r * (th + rod + gap)
            sheet.paste(Image.open(f"{AQUI}/grade-{n}-previa.png").resize((tw, th), Image.LANCZOS), (x, y))
            d.ellipse((x + 8, y + 8, x + 52, y + 52), fill=LARANJA); d.text((x + 30, y + 31), str(i + 1), font=fn_, fill=(255, 255, 255), anchor="mm")
            d.text((x, y + th + 8), f"{i + 1}  {n}", font=geist(20, 800), fill=(235, 235, 235))
            ln, yy = "", y + th + 34
            for w_ in desc.split():
                if d.textlength((ln + " " + w_).strip(), font=fs_) > tw: d.text((x, yy), ln, font=fs_, fill=(170, 170, 170)); ln, yy = w_, yy + 21
                else: ln = (ln + " " + w_).strip()
            d.text((x, yy), ln, font=fs_, fill=(170, 170, 170))
        sheet.save(AQUI + "/contato.jpg", quality=92)
