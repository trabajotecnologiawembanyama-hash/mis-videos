"""Planos de recuerdos humanos: siluetas a contraluz, luz cálida, bokeh. Usados en escenas 3, 5 y 6."""
import math
import numpy as np
from PIL import Image, ImageDraw
from base import (W, H, vgrad, radial, silhouette_mask, bokeh_layer, blur, to_img, clamp01)

PW, PH = int(W * 1.2), int(H * 1.2)


def warm_bokeh_color(rng):
    return (1.0, rng.uniform(0.55, 0.8), rng.uniform(0.25, 0.45))


def cool_bokeh_color(rng):
    return rng.choice([(0.45, 0.7, 1.0), (1.0, 0.7, 0.4), (0.6, 0.85, 1.0)])


def backlit(spec, seed=1):
    rng = np.random.default_rng(seed)
    pw, ph = PW, PH
    sky = vgrad(pw, ph, spec["sky"])
    sx, sy = spec["sun"][0] * pw, spec["sun"][1] * ph
    sc = np.array(spec.get("sun_color", (1.0, 0.72, 0.38)), np.float32)
    d2 = radial(pw, ph, sx, sy, 1.0)
    d = np.sqrt(d2)
    sr = spec.get("sun_r", 70)
    img = sky
    img = img + sc * (np.exp(-d / (sr * 6)) * 0.85)[..., None]
    img = img + sc * (np.exp(-d / (sr * 1.6)) * 0.9)[..., None]
    img = img + np.array([1.0, 0.95, 0.85], np.float32) * clamp01((sr - d) / 3)[..., None] * 1.6
    # bandas de neblina horizontales
    hy = spec["horizon"] * ph
    ys = np.arange(ph, dtype=np.float32)[:, None]
    img = img + sc * (np.exp(-np.abs(ys - hy) / 60) * 0.35)[..., None]
    # bokeh
    if spec.get("bokeh"):
        n, cf, rmin, rmax, y0, y1, a = spec["bokeh"]
        img = img + bokeh_layer(pw, ph, n, rng, cf, rmin, rmax, y0, y1, a)
    # ciudad/colinas lejanas con perspectiva atmosférica
    far = spec.get("far_fn")
    if far is not None:
        fimg = Image.new("L", (pw * 2, ph * 2), 0)
        far(ImageDraw.Draw(fimg), pw * 2, ph * 2, rng)
        fmask = np.asarray(fimg.resize((pw, ph), Image.LANCZOS), np.float32) / 255
        hazec = img * 0.45 + np.array([0.02, 0.02, 0.03], np.float32)
        img = img * (1 - fmask[..., None]) + hazec * fmask[..., None]
        # ventanas encendidas diminutas
        win = np.zeros((ph, pw), np.float32)
        ys_, xs_ = np.nonzero(fmask > 0.9)
        if len(ys_):
            sel = rng.choice(len(ys_), min(len(ys_), 900), replace=False)
            win[ys_[sel], xs_[sel]] = rng.uniform(0.3, 1.0, sel.size)
            win = np.maximum(win, np.roll(win, 1, 1))
        img = img + win[..., None] * np.array([1.0, 0.75, 0.45], np.float32) * 0.8
    # suelo / horizonte
    ground = spec.get("ground_fn")
    gm = np.zeros((ph, pw), np.float32)
    if ground is not None:
        gimg = Image.new("L", (pw * 2, ph * 2), 0)
        ground(ImageDraw.Draw(gimg), pw * 2, ph * 2, rng)
        gm = np.asarray(gimg.resize((pw, ph), Image.LANCZOS), np.float32) / 255
    # personas
    figs = [(x * pw, y * ph, h * ph, pose, child) for (x, y, h, pose, child) in spec["figures"]]
    fm = silhouette_mask((pw, ph), figs)
    extra = spec.get("extra_fn")
    if extra is not None:
        em = Image.new("L", (pw * 2, ph * 2), 0)
        extra(ImageDraw.Draw(em), pw * 2, ph * 2)
        fm = np.maximum(fm, np.asarray(em.resize((pw, ph), Image.LANCZOS), np.float32) / 255)
    mask = np.maximum(gm, fm)
    # luz que envuelve la silueta (rim light) — más fuerte cerca del sol
    soft = blur(mask, 6, 2)
    rim = clamp01(mask - soft) * 2.2
    near = np.exp(-d / (pw * 0.55))
    dark = np.array(spec.get("sil_color", (0.012, 0.010, 0.014)), np.float32)
    lit = img * (1 - mask[..., None]) + dark * mask[..., None]
    lit = lit + (rim * near)[..., None] * sc * 1.8
    # rayos de luz volumétricos desde el sol (por delante)
    if spec.get("rays", 0.0) > 0:
        th = np.arctan2(np.arange(ph)[:, None] - sy, np.arange(pw)[None, :] - sx)
        k = np.arange(1, 40)
        ph_ = rng.uniform(0, 6.28, k.size)
        thl = np.linspace(-np.pi, np.pi, 4096)
        pat = (np.sin(k[:, None] * thl[None, :] * 2 + ph_[:, None]) / k[:, None] ** 0.6).sum(0)
        pat = clamp01((pat - pat.mean()) / pat.std() * 0.5 + 0.3)
        rays = pat[((th + np.pi) / (2 * np.pi) * 4095).astype(int)]
        occl = blur(1 - mask, 30, 4)
        lit = lit + (rays * np.exp(-d / (pw * 0.5)) * spec["rays"] * (0.08 + 0.92 * occl ** 2))[..., None] * sc
    # reflejo en suelo mojado (opcional)
    if spec.get("wet"):
        y0 = int(spec["wet"] * ph)
        refl = lit[max(0, 2 * y0 - ph):y0][::-1]
        hh = min(refl.shape[0], ph - y0)
        lit[y0:y0 + hh] = lit[y0:y0 + hh] * 0.55 + blur(refl[:hh], 6, 2) * 0.4
    return lit.astype(np.float32), mask


# ---------------------------------------------------------------- suelos
def field(draw, w, h, rng, y=0.80):
    pts = [(0, h * y)]
    for i in range(0, 61):
        x = w * i / 60
        pts.append((x, h * y + math.sin(i * 0.7) * 6 + rng.uniform(-4, 4)))
    pts += [(w, h), (0, h)]
    draw.polygon(pts, fill=255)
    for _ in range(1600):           # hierba
        x = rng.uniform(0, w); yy = h * y + rng.uniform(-2, 30)
        draw.line([(x, yy + 18), (x + rng.uniform(-10, 10), yy - rng.uniform(10, 46))], fill=255, width=3)


def hill(draw, w, h, rng, y=0.78):
    pts = [(0, h)]
    for i in range(0, 101):
        x = w * i / 100
        pts.append((x, h * y + (1 - math.cos((i / 100 - 0.5) * 3.0)) * h * 0.06))
    pts += [(w, h)]
    draw.polygon(pts, fill=255)


def city_far(draw, w, h, rng, y=0.70):
    x = -20
    while x < w:
        bw = rng.uniform(90, 300); bh = rng.uniform(20, 200) * (1.8 if rng.random() < 0.15 else 1.0)
        draw.rectangle([x, h * y - bh, x + bw, h], fill=255)
        if rng.random() < 0.2:
            draw.rectangle([x + bw * 0.45, h * y - bh - 60, x + bw * 0.5, h * y - bh], fill=255)
        x += bw + rng.uniform(-30, 6)


def street(draw, w, h, rng, y=0.82):
    draw.rectangle([0, h * y, w, h], fill=255)


# ---------------------------------------------------------------- planos
def shot_padre_hija():
    return backlit(dict(
        sky=[(0, (0.03, 0.04, 0.08)), (0.45, (0.20, 0.12, 0.10)), (0.66, (0.75, 0.42, 0.18)), (1, (0.08, 0.05, 0.04))],
        sun=(0.52, 0.64), sun_r=60, horizon=0.66,
        bokeh=(70, warm_bokeh_color, 6, 30, 0.45, 0.75, 0.35),
        ground_fn=lambda d, w, h, r: field(d, w, h, r, 0.80),
        figures=[
            (0.39, 0.83, 0.50, dict(lean=18, head=16, hipk=0.5, ll=(90, -90), rl=(0, -90), la=(25, 20), ra=(45, 30), arms=0.45), False),
            (0.60, 0.83, 0.33, dict(lean=-14, head=-18, la=(-150, -20), ra=(-30, -20), arms=0.55, ll=(4, 0), rl=(-4, 0), dress=0.09, hair=0.06), True),
        ], rays=0.25), seed=11)


def shot_pareja_lluvia():
    return backlit(dict(
        sky=[(0, (0.01, 0.02, 0.05)), (0.5, (0.05, 0.08, 0.15)), (0.78, (0.12, 0.12, 0.16)), (1, (0.02, 0.02, 0.03))],
        sun=(0.50, 0.36), sun_r=24, sun_color=(1.0, 0.70, 0.40), horizon=0.75,
        bokeh=(120, cool_bokeh_color, 8, 46, 0.30, 0.80, 0.45),
        ground_fn=lambda d, w, h, r: street(d, w, h, r, 0.84),
        figures=[
            (0.42, 0.85, 0.46, dict(lean=5, head=-24, la=(8, 0), ra=(35, 20), arms=0.85, coat=0.10), False),
            (0.58, 0.85, 0.43, dict(lean=-7, head=10, la=(-35, -20), ra=(-8, 0), arms=0.85, hair=0.07, dress=0.14), False),
        ], rays=0.12, wet=0.84), seed=12)


def shot_ninos():
    return backlit(dict(
        sky=[(0, (0.04, 0.05, 0.10)), (0.4, (0.25, 0.15, 0.12)), (0.68, (0.95, 0.55, 0.22)), (1, (0.10, 0.06, 0.04))],
        sun=(0.70, 0.68), sun_r=70, horizon=0.70,
        bokeh=(90, warm_bokeh_color, 4, 18, 0.5, 0.85, 0.5),
        ground_fn=lambda d, w, h, r: field(d, w, h, r, 0.82),
        figures=[
            (0.25, 0.86, 0.30, dict(lean=12, la=(60, 40), ra=(-50, -30), ll=(40, 30), rl=(-35, 50)), True),
            (0.50, 0.85, 0.33, dict(lean=8, la=(170, 10), ra=(-160, -10), ll=(-30, 40), rl=(45, 10), hair=0.06), True),
            (0.76, 0.86, 0.27, dict(lean=-6, la=(-120, -20), ra=(130, 20), ll=(20, 0), rl=(-30, 30)), True),
        ], extra_fn=lambda d, w, h: d.ellipse([w * 0.60, h * 0.47, w * 0.64, h * 0.47 + w * 0.04], fill=255),
        rays=0.3), seed=13)


def shot_ayuda():
    return backlit(dict(
        sky=[(0, (0.02, 0.03, 0.07)), (0.45, (0.12, 0.10, 0.14)), (0.68, (0.80, 0.45, 0.22)), (1, (0.06, 0.04, 0.04))],
        sun=(0.42, 0.66), sun_r=50, horizon=0.70,
        bokeh=(80, warm_bokeh_color, 5, 26, 0.4, 0.72, 0.35),
        far_fn=lambda d, w, h, r: city_far(d, w, h, r, 0.72),
        ground_fn=lambda d, w, h, r: street(d, w, h, r, 0.82),
        figures=[
            (0.30, 0.85, 0.40, dict(lean=-14, head=8, hipk=0.13, ll=(-80, 4), rl=(-70, -20), la=(-30, 0), ra=(135, 0)), False),
            (0.60, 0.85, 0.48, dict(lean=-30, head=-15, la=(-18, 6), ra=(-4, 10), ll=(-6, 0), rl=(14, 0), coat=0.13), False),
        ], rays=0.25, wet=0.82), seed=14)


def shot_ancianos():
    def bench(d, w, h):
        d.rectangle([w * 0.18, h * 0.72, w * 0.82, h * 0.74], fill=255)
        d.rectangle([w * 0.18, h * 0.64, w * 0.82, h * 0.655], fill=255)
        d.rectangle([w * 0.18, h * 0.68, w * 0.82, h * 0.69], fill=255)
        for x in (0.22, 0.78):
            d.rectangle([w * (x - 0.008), h * 0.64, w * (x + 0.008), h * 0.86], fill=255)
    return backlit(dict(
        sky=[(0, (0.03, 0.04, 0.09)), (0.42, (0.30, 0.17, 0.14)), (0.62, (0.98, 0.55, 0.25)), (0.66, (0.55, 0.30, 0.16)), (1, (0.12, 0.07, 0.05))],
        sun=(0.50, 0.615), sun_r=85, horizon=0.64,
        bokeh=(60, warm_bokeh_color, 6, 30, 0.62, 0.95, 0.45),
        ground_fn=lambda d, w, h, r: hill(d, w, h, r, 0.84),
        extra_fn=bench,
        figures=[
            (0.40, 0.86, 0.43, dict(lean=9, head=20, hipk=0.65, ll=(0, 0), rl=(0, 0), la=(20, 10), ra=(35, 25)), False),
            (0.59, 0.86, 0.41, dict(lean=-7, head=-24, hipk=0.65, ll=(0, 0), rl=(0, 0), la=(-25, -10), ra=(-35, -20), hair=0.05), False),
        ], rays=0.35), seed=21)


def shot_madre_hijo():
    return backlit(dict(
        sky=[(0, (0.05, 0.06, 0.12)), (0.45, (0.35, 0.20, 0.15)), (0.70, (1.0, 0.62, 0.30)), (1, (0.12, 0.07, 0.04))],
        sun=(0.50, 0.38), sun_r=80, horizon=0.74,
        bokeh=(80, warm_bokeh_color, 6, 34, 0.15, 0.7, 0.4),
        ground_fn=lambda d, w, h, r: field(d, w, h, r, 0.84),
        figures=[
            (0.50, 0.88, 0.50, dict(lean=-4, head=-25, la=(-172, 8), ra=(172, -8), hair=0.08, dress=0.12), False),
            (0.50, 0.44, 0.26, dict(lean=0, head=10, la=(-115, -25), ra=(115, 25), ll=(25, 40), rl=(-10, 45), build=1.25, dress=0.05), True),
        ], rays=0.45), seed=22)


def shot_amigos():
    poses = []
    xs = [0.20, 0.40, 0.60, 0.80]
    for i, x in enumerate(xs):
        poses.append((x, 0.84, 0.40 + (i % 2) * 0.03,
                      dict(lean=(3 if i < 2 else -3), head=(10 if i < 2 else -10), la=(-40, -35) if i > 0 else (10, 0), ra=(40, 35) if i < 3 else (-10, 0), arms=0.7,
                           hair=0.05 if i in (1, 3) else 0), False))
    return backlit(dict(
        sky=[(0, (0.02, 0.03, 0.08)), (0.45, (0.18, 0.12, 0.16)), (0.63, (0.95, 0.50, 0.22)), (1, (0.09, 0.05, 0.04))],
        sun=(0.50, 0.63), sun_r=60, horizon=0.66,
        bokeh=(60, warm_bokeh_color, 4, 20, 0.62, 0.75, 0.6),
        far_fn=lambda d, w, h, r: city_far(d, w, h, r, 0.68),
        ground_fn=lambda d, w, h, r: hill(d, w, h, r, 0.80),
        figures=poses, rays=0.35), seed=23)


def shot_abrazo():
    return backlit(dict(
        sky=[(0, (0.04, 0.03, 0.06)), (0.5, (0.45, 0.25, 0.16)), (0.8, (0.95, 0.60, 0.32)), (1, (0.30, 0.16, 0.08))],
        sun=(0.51, 0.60), sun_r=80, horizon=0.86,
        ground_fn=lambda d, w, h, r: field(d, w, h, r, 0.86),
        bokeh=(110, warm_bokeh_color, 10, 60, 0.0, 1.0, 0.35),
        figures=[
            (0.425, 0.88, 0.58, dict(lean=6, head=10, la=(10, 0), ra=(40, 25), arms=0.5, coat=0.1), False),
            (0.59, 0.88, 0.54, dict(lean=-6, head=-12, la=(-40, -25), ra=(-10, 0), arms=0.5, hair=0.10, dress=0.12), False),
        ], rays=0.45), seed=24)


def shot_foto_familia():
    return backlit(dict(
        sky=[(0, (0.22, 0.22, 0.22)), (0.6, (0.48, 0.45, 0.40)), (1, (0.25, 0.23, 0.21))],
        sun=(0.5, 0.58), sun_r=60, sun_color=(0.55, 0.50, 0.42), horizon=0.72,
        sil_color=(0.10, 0.08, 0.07),
        ground_fn=lambda d, w, h, r: field(d, w, h, r, 0.82),
        figures=[
            (0.33, 0.86, 0.50, dict(lean=5, head=14, la=(6, 0), ra=(14, 4), arms=0.95, coat=0.08), False),
            (0.67, 0.86, 0.47, dict(lean=-5, head=-14, la=(-14, -4), ra=(-6, 0), arms=0.95, hair=0.08, dress=0.12), False),
            (0.45, 0.86, 0.30, dict(lean=3, head=10, la=(-8, 0), ra=(10, 0)), True),
            (0.56, 0.86, 0.25, dict(lean=-3, head=-10, la=(-10, 0), ra=(8, 0), dress=0.08, hair=0.05), True),
        ], rays=0.0), seed=31)
