"""Utilidades comunes de render: lienzo, cámara, glow, gradación de color, texto y siluetas."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
DUR = 40.0
NFRAMES = int(DUR * FPS)
FONT_DIR = "/usr/share/fonts/opentype/inter/"


def font(name, size):
    return ImageFont.truetype(FONT_DIR + name + ".otf", size)


def clamp01(x):
    return np.clip(x, 0.0, 1.0)


def ease_in_out(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def lerp(a, b, t):
    return a + (b - a) * t


def to_img(a):
    return Image.fromarray((clamp01(a) * 255 + 0.5).astype(np.uint8))


def to_arr(img):
    return np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0


def blur(a, radius, down=4):
    """Desenfoque gaussiano rápido (reduce, desenfoca, amplía)."""
    h, w = a.shape[:2]
    img = to_img(a) if a.ndim == 3 else Image.fromarray((clamp01(a) * 255).astype(np.uint8))
    small = img.resize((max(1, w // down), max(1, h // down)), Image.BILINEAR)
    small = small.filter(ImageFilter.GaussianBlur(max(0.5, radius / down)))
    big = small.resize((w, h), Image.BILINEAR)
    return np.asarray(big, dtype=np.float32) / 255.0


def blur_hdr(a, radius, down=4):
    """Desenfoque que conserva valores >1 (escala antes y después)."""
    m = max(1e-6, float(a.max()))
    return blur(a / m, radius, down) * m


def camera(img, zoom=1.0, cx=None, cy=None, rot=0.0, out=(W, H)):
    """Encuadra un 'plate' PIL más grande que la salida: zoom 1 = plate completo escalado a la salida.
    cx, cy = punto del plate que queda en el centro de la imagen."""
    pw, ph = img.size
    ow, oh = out
    if cx is None: cx = pw / 2
    if cy is None: cy = ph / 2
    base = pw / ow                     # px de plate por px de salida a zoom 1
    s = base / zoom
    c, sn = math.cos(rot), math.sin(rot)
    # salida (x,y) -> plate
    a = s * c; b = -s * sn
    d = s * sn; e = s * c
    x0 = cx - (a * ow / 2 + b * oh / 2)
    y0 = cy - (d * ow / 2 + e * oh / 2)
    return img.transform(out, Image.AFFINE, (a, b, x0, d, e, y0), resample=Image.BILINEAR)


_vig = None
_grain = None


def vignette():
    global _vig
    if _vig is None:
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        nx = (x - W / 2) / (W / 2); ny = (y - H / 2) / (H / 2)
        r = np.sqrt(nx ** 2 * 1.0 + ny ** 2 * 0.75)
        _vig = (1 - 0.62 * clamp01((r - 0.45) / 0.9) ** 1.6)[..., None].astype(np.float32)
    return _vig


def grain_bank():
    global _grain
    if _grain is None:
        rng = np.random.default_rng(7)
        g = rng.normal(0, 1, (H // 2, W // 2, 6)).astype(np.float32)
        _grain = g
    return _grain


def grade(a, f, tint_shadow=(0.02, 0.05, 0.09), tint_high=(1.0, 0.93, 0.82), bloom=0.55,
          contrast=1.12, exposure=1.0, grain=0.035, vig=True, sat=1.0):
    """Gradación cinematográfica: bloom, negros profundos, sombras azules, altas luces cálidas, viñeta, grano."""
    a = a * exposure
    if bloom > 0:
        bright = np.maximum(a - 0.55, 0)
        g1 = blur_hdr(bright, 18, 4)
        g2 = blur_hdr(bright, 70, 8)
        a = a + bloom * (0.7 * g1 + 0.6 * g2)
    # tonemapping suave (filmic)
    a = a / (1 + 0.22 * a)
    a = a * 1.22
    lum = (a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722)[..., None]
    if sat != 1.0:
        a = lum + (a - lum) * sat
    # split toning
    ts = np.array(tint_shadow, np.float32); th = np.array(tint_high, np.float32)
    shadow_w = clamp01(1 - lum * 2.2)
    a = a + ts * shadow_w * 0.6
    a = a * (1 - clamp01(lum - 0.4) * 0.5 + clamp01(lum - 0.4) * 0.5 * th)
    # contraste en S alrededor de 0.4, negros aplastados
    a = clamp01(a)
    a = clamp01((a - 0.4) * contrast + 0.4)
    a = clamp01((a - 0.012) / 0.988)
    if vig:
        a = a * vignette()
    if grain > 0:
        gb = grain_bank()
        k = f % gb.shape[2]
        g = gb[..., k]
        g = np.repeat(np.repeat(g, 2, 0), 2, 1)
        if f % 2: g = g[::-1]
        a = a + g[..., None] * grain * (0.35 + 0.65 * (1 - lum))
    return clamp01(a)


def chroma_ab(a, px=3):
    px = int(round(px))
    if px <= 0: return a
    out = a.copy()
    out[:, px:, 0] = a[:, :-px, 0]
    out[:, :-px, 2] = a[:, px:, 2]
    return out


# ----------------------------------------------------------------- figuras humanas (siluetas)
def _pt(p, ang, ln):
    r = math.radians(ang)
    return (p[0] + math.sin(r) * ln, p[1] + math.cos(r) * ln)


def _limb(draw, pts, widths, fill):
    """Miembro cónico suave: segmentos como polígonos + articulaciones redondas."""
    for (p0, p1), (w0, w1) in zip(zip(pts[:-1], pts[1:]), zip(widths[:-1], widths[1:])):
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        draw.polygon([(p0[0] + nx * w0 / 2, p0[1] + ny * w0 / 2), (p1[0] + nx * w1 / 2, p1[1] + ny * w1 / 2),
                      (p1[0] - nx * w1 / 2, p1[1] - ny * w1 / 2), (p0[0] - nx * w0 / 2, p0[1] - ny * w0 / 2)], fill=fill)
    for q, w in zip(pts, widths):
        draw.ellipse([q[0] - w / 2, q[1] - w / 2, q[0] + w / 2, q[1] + w / 2], fill=fill)


def person(draw, x, y, h, pose=None, fill=255, child=False):
    """Silueta humana articulada. (x,y) = pies; h = altura (de pie) en px.
    Ángulos en grados desde la vertical hacia abajo; 90 = derecha, -90 = izquierda, 180 = arriba."""
    p = dict(lean=0, head=0, la=(10, 0), ra=(-10, 0), ll=(6, 0), rl=(-6, 0), hair=0, dress=0, coat=0, hipk=1.0,
             build=1.0, arms=1.0)
    if pose: p.update(pose)
    b = p["build"]
    hr = h * (0.085 if child else 0.062)
    leg = h * (0.235 if child else 0.25)
    hip = (x, y - 2 * leg * p["hipk"])
    lean = p["lean"]
    torso_len = h * (0.25 if child else 0.29)
    neck = _pt(hip, 180 - lean, torso_len)
    waist = _pt(hip, 180 - lean, torso_len * 0.42)
    shw = h * (0.085 if child else 0.098) * b
    hpw = h * (0.06 if child else 0.07) * b
    wsw = h * (0.05 if child else 0.06) * b
    r = math.radians(lean)
    dx, dy = math.cos(r), math.sin(r)
    def side(c, wdt, s): return (c[0] + s * dx * wdt, c[1] + s * dy * wdt)
    shoulder_c = _pt(neck, -lean, h * 0.03)
    lsh, rsh = side(shoulder_c, shw, -1), side(shoulder_c, shw, 1)
    lhp, rhp = side(hip, hpw, -1), side(hip, hpw, 1)
    # piernas
    tw = h * (0.10 if child else 0.105) * b
    for (a1, a2), hp in ((p["ll"], side(hip, hpw * 0.55, -1)), (p["rl"], side(hip, hpw * 0.55, 1))):
        k = _pt(hp, a1, leg)
        f = _pt(k, a1 + a2, leg)
        _limb(draw, [hp, k, f], [tw, tw * 0.66, tw * 0.48], fill)
        fx = 1 if (a1 + a2 * 0.3) >= 0 else -1
        fl = tw * 0.75
        draw.polygon([(f[0] - tw * 0.22, f[1] - tw * 0.2), (f[0] + fx * fl, f[1] + tw * 0.08),
                      (f[0] + fx * fl, f[1] + tw * 0.2), (f[0] - tw * 0.22, f[1] + tw * 0.2)], fill=fill)
    # torso orgánico
    pts = [side(neck, shw * 0.55, -1), lsh, side(_pt(neck, -lean, torso_len * 0.25), shw * 0.95, -1),
           side(waist, wsw, -1), lhp, side(_pt(hip, -lean, h * 0.04), hpw * 0.8, -1),
           side(_pt(hip, -lean, h * 0.04), hpw * 0.8, 1), rhp, side(waist, wsw, 1),
           side(_pt(neck, -lean, torso_len * 0.25), shw * 0.95, 1), rsh, side(neck, shw * 0.55, 1)]
    draw.polygon(pts, fill=fill)
    aw = h * (0.062 if child else 0.058) * b
    for q in (lsh, rsh):
        draw.ellipse([q[0] - aw * 0.75, q[1] - aw * 0.75, q[0] + aw * 0.75, q[1] + aw * 0.75], fill=fill)
    if p["dress"]:
        d = p["dress"] * h
        draw.polygon([side(waist, wsw, -1), side(waist, wsw, 1), (rhp[0] + d * 0.45, rhp[1] + d), (lhp[0] - d * 0.45, lhp[1] + d)], fill=fill)
    if p["coat"]:
        d = p["coat"] * h
        draw.polygon([lsh, rsh, (rhp[0] + d * 0.12, rhp[1] + d), (lhp[0] - d * 0.12, lhp[1] + d)], fill=fill)
    # brazos
    ua = h * (0.15 if child else 0.165) * p["arms"]
    fa = h * (0.14 if child else 0.15) * p["arms"]
    for (a1, a2), sh in ((p["la"], lsh), (p["ra"], rsh)):
        e = _pt(sh, a1, ua)
        wr = _pt(e, a1 + a2, fa)
        hand = _pt(wr, a1 + a2, aw * 0.9)
        _limb(draw, [sh, e, wr, hand], [aw, aw * 0.82, aw * 0.66, aw * 0.72], fill)
    # cuello y cabeza
    hc = _pt(neck, 180 - lean - p["head"], hr * 1.3)
    _limb(draw, [neck, _pt(neck, 180 - lean - p["head"], hr * 0.8)], [hr * 0.85, hr * 0.75], fill)
    hd = math.radians(lean + p["head"])
    # cabeza ligeramente ovalada e inclinada
    for k in range(5):
        o = (k - 2) * hr * 0.06
        cx, cy = hc[0] + math.sin(hd) * o, hc[1] - math.cos(hd) * o
        rr = hr * (0.92 - abs(k - 2) * 0.05)
        draw.ellipse([cx - rr * 0.97, cy - rr, cx + rr * 0.97, cy + rr], fill=fill)
    if p["hair"]:
        L = p["hair"] * h
        draw.polygon([(hc[0] - hr * 0.95, hc[1] - hr * 0.1), (hc[0] + hr * 0.95, hc[1] - hr * 0.1),
                      (hc[0] + hr * 1.05, hc[1] + L), (hc[0] - hr * 1.05, hc[1] + L)], fill=fill)
    return dict(neck=neck, head=hc, hip=hip, lsh=lsh, rsh=rsh)


def silhouette_mask(size, figures, ss=2):
    """figures: lista de (x, y, h, pose, child). Devuelve máscara float con antialias."""
    w, h = size
    m = Image.new("L", (w * ss, h * ss), 0)
    d = ImageDraw.Draw(m)
    for fig in figures:
        x, y, hh, pose, child = fig
        person(d, x * ss, y * ss, hh * ss, pose, 255, child)
    m = m.resize((w, h), Image.LANCZOS)
    return np.asarray(m, dtype=np.float32) / 255.0


def radial(w, h, cx, cy, sx, sy=None):
    sy = sy or sx
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    return ((x - cx) / sx) ** 2 + ((y - cy) / sy) ** 2


def vgrad(w, h, stops):
    """Degradado vertical. stops = [(pos 0..1, (r,g,b)), ...]"""
    ys = np.linspace(0, 1, h, dtype=np.float32)
    out = np.zeros((h, 3), np.float32)
    pos = [s[0] for s in stops]
    for c in range(3):
        out[:, c] = np.interp(ys, pos, [s[1][c] for s in stops])
    return np.repeat(out[:, None, :], w, axis=1)


def bokeh_layer(w, h, n, rng, color_fn, rmin=8, rmax=40, ymin=0.0, ymax=1.0, alpha=0.5, ss=1):
    img = Image.new("RGB", (w, h), (0, 0, 0))
    d = ImageDraw.Draw(img)
    for _ in range(n):
        r = rng.uniform(rmin, rmax)
        x = rng.uniform(0, w); y = rng.uniform(ymin * h, ymax * h)
        c = color_fn(rng)
        a = rng.uniform(0.3, 1.0) * alpha
        col = tuple(int(255 * min(1, ci * a)) for ci in c)
        d.ellipse([x - r, y - r, x + r, y + r], fill=col)
    arr = np.asarray(img, dtype=np.float32) / 255.0
    return blur(arr, 2.5, 1)


def text_layer(lines, fnt, fill=(1, 1, 1), spacing=1.0, tracking=0, size=(W, H), cy=H / 2, align="center", line_gap=1.18):
    """Texto centrado como máscara float (H,W)."""
    img = Image.new("L", size, 0)
    d = ImageDraw.Draw(img)
    asc, desc = fnt.getmetrics()
    lh = (asc + desc) * line_gap
    total = lh * len(lines)
    y = cy - total / 2
    for ln in lines:
        widths = [d.textlength(ch, font=fnt) + tracking for ch in ln]
        tw = sum(widths) - tracking
        x = (size[0] - tw) / 2
        for ch, cw in zip(ln, widths):
            d.text((x, y), ch, font=fnt, fill=255)
            x += cw
        y += lh
    return np.asarray(img, dtype=np.float32) / 255.0
