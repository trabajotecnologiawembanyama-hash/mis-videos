"""Las 8 escenas de EL ÚLTIMO MENSAJE DE LA HUMANIDAD. Cada función devuelve (imagen float HxWx3, params de gradación)."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from base import (W, H, FPS, font, clamp01, ease_in_out, ease_out, lerp, to_img, to_arr, blur, blur_hdr, camera,
                  vgrad, radial, silhouette_mask, text_layer, chroma_ab)
from nucleo import ai_core, paste_add
import memorias as M

_plates = {}


def plate(name, fn):
    if name not in _plates:
        _plates[name] = fn()
    return _plates[name]


def hdr_to_pil(a, scale=1.0):
    return to_img(a / scale)


def cam_arr(img_pil, zoom, cx=None, cy=None, rot=0.0, scale=1.0):
    return to_arr(camera(img_pil, zoom, cx, cy, rot)) * scale


# =====================================================================================  ESCENA 1: LA CIUDAD
CW, CH = 2160, 3840
SCREEN = (780, 1080, 1380, 1830)       # x0,y0,x1,y1 de la pantalla gigante en el plate


def build_city():
    rng = np.random.default_rng(101)
    img = vgrad(CW, CH, [(0, (0.004, 0.008, 0.02)), (0.40, (0.02, 0.04, 0.085)), (0.62, (0.06, 0.07, 0.11)),
                         (0.72, (0.16, 0.09, 0.06)), (1, (0.05, 0.03, 0.03))])
    pil = to_img(img)
    d = ImageDraw.Draw(pil)

    def tower(x0, x1, top, base, col, win_p, win_cols, wsz=(6, 9), gap=(14, 18), spire=False, red=False):
        d.rectangle([x0, top, x1, base], fill=col)
        if spire:
            cx = (x0 + x1) / 2
            d.polygon([(cx - 10, top), (cx + 10, top), (cx, top - (x1 - x0) * 0.8)], fill=col)
        if red:
            cx = (x0 + x1) / 2
            d.ellipse([cx - 5, top - 8, cx + 5, top + 2], fill=(255, 40, 30))
        ww, wh = wsz; gx, gy = gap
        cols = int((x1 - x0 - 8) // gx)
        rows = int((base - top - 10) // gy)
        if cols <= 0 or rows <= 0: return
        lit = rng.random((rows, cols)) < win_p
        # bloques de plantas apagadas
        for r in range(rows):
            if rng.random() < 0.25: lit[r] = False
        for r in range(rows):
            for c in range(cols):
                if lit[r, c]:
                    wc = win_cols[rng.integers(len(win_cols))]
                    k = rng.uniform(0.4, 1.0)
                    x = x0 + 6 + c * gx; y = top + 8 + r * gy
                    d.rectangle([x, y, x + ww, y + wh], fill=tuple(int(v * k) for v in wc))

    warm = [(255, 190, 120), (255, 170, 90), (255, 214, 160)]
    cool = [(140, 200, 255), (110, 170, 240), (200, 230, 255)]
    # capa lejana
    x = -20
    while x < CW:
        bw = rng.uniform(50, 130); top = rng.uniform(2150, 2550)
        tower(x, x + bw, top, CH, (14, 20, 36), 0.10, cool + warm, (3, 4), (8, 10), red=rng.random() < 0.1)
        x += bw + rng.uniform(-10, 6)
    hz = to_arr(pil)
    fog = np.exp(-np.abs(np.arange(CH) - 2550)[:, None] / 260.0).astype(np.float32)
    hz = hz + fog[..., None] * np.array([0.10, 0.10, 0.14], np.float32) * 0.9
    pil = to_img(hz); d = ImageDraw.Draw(pil)
    # capa media
    x = -40
    while x < CW:
        bw = rng.uniform(130, 280); top = rng.uniform(1500, 2300)
        if 650 < x < 1450: top = rng.uniform(2100, 2500)
        tower(x, x + bw, top, CH, (8, 12, 22), 0.28, warm + cool, (5, 7), (12, 15), spire=rng.random() < 0.25,
              red=rng.random() < 0.3)
        x += bw + rng.uniform(10, 40)
    mid = to_arr(pil)
    fog2 = np.exp(-np.abs(np.arange(CH) - 2900)[:, None] / 350.0).astype(np.float32)
    mid = mid + fog2[..., None] * np.array([0.06, 0.07, 0.11], np.float32)
    pil = to_img(mid); d = ImageDraw.Draw(pil)
    # megatorre central con la pantalla
    d.polygon([(700, 3840), (700, 980), (760, 900), (1400, 900), (1460, 980), (1460, 3840)], fill=(5, 8, 15))
    d.polygon([(1040, 900), (1120, 900), (1080, 420)], fill=(5, 8, 15))
    d.ellipse([1074, 410, 1086, 422], fill=(255, 50, 40))
    for y in range(1900, 3800, 22):
        for xx in range(720, 1440, 16):
            if rng.random() < 0.18:
                c = warm[rng.integers(3)]
                d.rectangle([xx, y, xx + 6, y + 8], fill=tuple(int(v * 0.7) for v in c))
    # capa cercana (marcos laterales)
    tower(-10, 330, 600, CH, (3, 5, 9), 0.12, warm, (8, 10), (20, 26))
    tower(330, 520, 1300, CH, (4, 6, 11), 0.15, cool, (6, 8), (16, 22), red=True)
    tower(1820, 2170, 450, CH, (3, 5, 9), 0.12, warm, (8, 10), (20, 26), red=True)
    tower(1640, 1820, 1150, CH, (4, 6, 11), 0.15, cool, (6, 8), (16, 22))
    # autopista con estelas de luz
    arr = to_arr(pil)
    for k in range(3):
        y = 3350 + k * 70
        arr[y:y + 6, :, :] += np.array([1.0, 0.25, 0.12], np.float32) * 0.8
        arr[y + 18:y + 22, :, :] += np.array([1.0, 0.92, 0.8], np.float32) * 0.6
    # neblina baja cálida
    fog3 = np.exp(-np.abs(np.arange(CH) - 3400)[:, None] / 300.0).astype(np.float32)
    arr = arr + fog3[..., None] * np.array([0.25, 0.12, 0.06], np.float32) * 0.6
    glow = blur(clamp01(arr - 0.4), 10, 4)
    arr = arr + glow * 0.8
    return to_img(arr)


def screen_content(t):
    x0, y0, x1, y1 = SCREEN
    w, h = x1 - x0, y1 - y0
    img = Image.new("RGB", (w, h), (24, 3, 3))
    d = ImageDraw.Draw(img)
    for y in range(0, h, 6):
        d.line([(0, y), (w, y)], fill=(14, 1, 1))
    secs = 24 * 3600 - int(math.floor(t))
    if t < 1.0: secs = 24 * 3600
    hh, mm, ss = secs // 3600, (secs % 3600) // 60, secs % 60
    txt = f"{hh:02d}:{mm:02d}:{ss:02d}"
    f = font("InterDisplay-Bold", 132)
    tw = d.textlength(txt, font=f)
    d.text(((w - tw) / 2, h * 0.36), txt, font=f, fill=(255, 70, 50))
    # barra de progreso y anillo pulsante
    d.rectangle([60, int(h * 0.66), w - 60, int(h * 0.66) + 8], fill=(80, 10, 8))
    d.rectangle([60, int(h * 0.66), 60 + int((w - 120) * (1 - t / 40)), int(h * 0.66) + 8], fill=(255, 70, 50))
    pulse = 0.5 + 0.5 * math.sin(t * 6)
    r = 34 + 6 * pulse
    d.ellipse([w / 2 - r, h * 0.2 - r, w / 2 + r, h * 0.2 + r], outline=(255, int(60 + 60 * pulse), 40), width=6)
    d.ellipse([w / 2 - 12, h * 0.2 - 12, w / 2 + 12, h * 0.2 + 12], fill=(255, 80, 50))
    return img


def scene1(t, f):
    city = plate("city", build_city)
    p = city.copy()
    x0, y0, x1, y1 = SCREEN
    sc = screen_content(t)
    p.paste(sc, (x0, y0))
    d = ImageDraw.Draw(p)
    # vehículos voladores
    rng = np.random.default_rng(5)
    for k in range(10):
        yy = rng.uniform(1300, 3000); sp = rng.uniform(250, 600) * (1 if k % 2 else -1)
        xx = (rng.uniform(0, CW) + sp * t) % (CW + 400) - 200
        col = (255, 220, 190) if sp > 0 else (255, 60, 50)
        if x0 - 60 < xx < x1 + 60 and y0 - 20 < yy < y1 + 20: continue
        d.line([(xx, yy), (xx - sp * 0.12, yy)], fill=col, width=4)
    u = t / 4.0
    zoom = 1.22 + 1.25 * (u ** 2.3)
    cx = 1080
    cy = lerp(1920, (y0 + y1) / 2, ease_in_out(min(1, u * 1.15)))
    rot = 0.0
    shake = max(0.0, 1 - t / 0.5)
    if shake > 0:
        r2 = np.random.default_rng(f)
        cx += r2.normal() * 14 * shake; cy += r2.normal() * 14 * shake
        rot = r2.normal() * 0.004 * shake
    a = cam_arr(p, zoom, cx, cy, rot)
    # glow de la pantalla (luz roja que contamina la escena)
    red = np.array([1.0, 0.18, 0.1], np.float32)
    sx = (x0 + x1) / 2; sy = (y0 + y1) / 2
    ox = W / 2 + (sx - cx) * zoom / 2; oy = H / 2 + (sy - cy) * zoom / 2
    r = radial(W, H, ox, oy, 300 * zoom, 380 * zoom)
    a = a + red * (np.exp(-r) * 0.35)[..., None]
    if t < 0.5: a = chroma_ab(a, 6 * (1 - t / 0.5))
    return a, dict(tint_shadow=(0.01, 0.04, 0.09), bloom=0.75, contrast=1.15)


# =====================================================================================  ESCENA 2: SALA DE CONTROL
RW, RH = 1350, 2400
VP = (675, 1260)


def build_room():
    rng = np.random.default_rng(202)
    a = vgrad(RW, RH, [(0, (0.006, 0.009, 0.016)), (0.5, (0.016, 0.024, 0.04)), (1, (0.004, 0.006, 0.01))])
    pil = to_img(a); d = ImageDraw.Draw(pil)
    # paredes laterales en perspectiva
    d.polygon([(0, 0), (260, 520), (260, 1640), (0, 2400)], fill=(4, 6, 11))
    d.polygon([(RW, 0), (RW - 260, 520), (RW - 260, 1640), (RW, 2400)], fill=(4, 6, 11))
    # muro del fondo con monitores muertos
    for r in range(7):
        for c in range(6):
            x = 300 + c * 128; y = 560 + r * 150
            if rng.random() < 0.08: continue
            d.rectangle([x, y, x + 112, y + 130], fill=(10, 14, 20), outline=(22, 30, 40), width=3)
            if rng.random() < 0.25:
                g = int(rng.uniform(14, 30))
                d.rectangle([x + 8, y + 8, x + 104, y + 122], fill=(g // 2, g, int(g * 1.4)))
            if rng.random() < 0.15:   # grieta
                d.line([(x + rng.uniform(10, 100), y + 6), (x + rng.uniform(10, 100), y + 124)], fill=(40, 50, 60), width=2)
    # suelo con rejilla en perspectiva
    d.polygon([(260, 1640), (RW - 260, 1640), (RW, 2400), (0, 2400)], fill=(6, 9, 14))
    for k in range(-12, 13):
        xb = RW / 2 + k * 160
        d.line([(RW / 2 + k * 28, 1640), (xb, 2400)], fill=(14, 20, 28), width=2)
    for k in range(10):
        y = 1640 + (2400 - 1640) * (k / 10) ** 1.8
        d.line([(0, y), (RW, y)], fill=(14, 20, 28), width=2)
    # techo con tiras de luz rotas
    for k in range(5):
        y = 120 + k * 80
        x0 = 300 - k * 40; x1 = RW - 300 + k * 40
        segs = np.sort(rng.uniform(x0, x1, 6))
        for i in range(0, 6, 2):
            d.line([(segs[i], y), (segs[i + 1], y)], fill=(60, 80, 100), width=4)
    # consolas en primer plano
    d.polygon([(0, 1900), (430, 1980), (470, 2400), (0, 2400)], fill=(3, 4, 7))
    d.polygon([(RW, 1900), (RW - 430, 1980), (RW - 470, 2400), (RW, 2400)], fill=(3, 4, 7))
    for _ in range(40):
        x = rng.choice([rng.uniform(20, 400), rng.uniform(RW - 400, RW - 20)]); y = rng.uniform(2000, 2300)
        c = [(255, 60, 40), (60, 200, 255), (255, 170, 60)][rng.integers(3)]
        d.rectangle([x, y, x + 5, y + 4], fill=c)
    arr = to_arr(pil)
    # haz de luz volumétrico desde arriba a la izquierda
    shaft = Image.new("L", (RW, RH), 0)
    ImageDraw.Draw(shaft).polygon([(120, 0), (330, 0), (900, 2400), (420, 2400)], fill=255)
    sh = blur(np.asarray(shaft, np.float32) / 255, 40, 4)
    arr = arr + sh[..., None] * np.array([0.10, 0.13, 0.18], np.float32) * 0.55
    arr = arr + blur(clamp01(arr - 0.15), 8, 2) * 0.6
    return to_img(arr)


def thumbs():
    rng = np.random.default_rng(9)
    out = []
    for i in range(28):
        w, h = 60, 44
        bg = vgrad(w, h, [(0, (rng.uniform(0.2, 0.5), rng.uniform(0.12, 0.3), rng.uniform(0.05, 0.2))),
                          (1, (rng.uniform(0.6, 1.0), rng.uniform(0.35, 0.6), rng.uniform(0.15, 0.3)))])
        n = rng.integers(1, 4)
        figs = []
        for k in range(n):
            ch = rng.random() < 0.4
            figs.append((rng.uniform(12, 48), 44, rng.uniform(22, 34) * (0.7 if ch else 1), dict(lean=rng.uniform(-10, 10)), ch))
        m = silhouette_mask((w, h), figs, ss=4)
        img = bg * (1 - m[..., None] * 0.9)
        img[:2] *= 0.3; img[-2:] *= 0.3; img[:, :2] *= 0.3; img[:, -2:] *= 0.3
        out.append(img.astype(np.float32))
    return out


_swarm = None


def swarm():
    global _swarm
    if _swarm is None:
        rng = np.random.default_rng(4)
        n = 260
        i = np.arange(n) + 0.5
        phi = np.arccos(1 - 2 * i / n); th = np.pi * (1 + 5 ** 0.5) * i
        pts = np.stack([np.cos(th) * np.sin(phi), np.cos(phi), np.sin(th) * np.sin(phi)], 1)
        rad = rng.uniform(0.75, 1.25, n)
        dust = rng.normal(0, 1, (5000, 3)); dust /= np.linalg.norm(dust, axis=1, keepdims=True)
        drad = rng.uniform(0.55, 1.6, 5000)
        _swarm = (pts * rad[:, None], rng.integers(0, 28, n), dust * drad[:, None])
    return _swarm


def add_points(a, xs, ys, vals, color):
    m = (xs >= 0) & (xs < W - 1) & (ys >= 0) & (ys < H - 1)
    xs, ys, vals = xs[m].astype(int), ys[m].astype(int), vals[m]
    for c in range(3):
        np.add.at(a[..., c], (ys, xs), vals * color[c])


def draw_swarm(a, t, cx, cy, R, energy=1.0, inward=0.0, warm=0.0):
    pts, tid, dust = swarm()
    th = plate("thumbs", thumbs)
    ang = t * 0.35
    ca, sa = math.cos(ang), math.sin(ang)
    tilt = 0.35
    ct, st = math.cos(tilt), math.sin(tilt)

    def proj(P, scale):
        x = P[:, 0] * ca + P[:, 2] * sa; z = -P[:, 0] * sa + P[:, 2] * ca; y = P[:, 1]
        y, z = y * ct - z * st, y * st + z * ct
        s = 1 / (1.6 - z * 0.6)
        return cx + x * R * scale * s, cy + y * R * scale * s, z, s

    col = np.array([0.35, 0.8, 1.0], np.float32) * (1 - warm) + np.array([1.0, 0.65, 0.3], np.float32) * warm
    xs, ys, z, s = proj(dust, 1.0 - 0.5 * inward)
    add_points(a, xs, ys, (0.25 + 0.5 * (z + 1) / 2) * energy, col)
    xs, ys, z, s = proj(pts, 1.0 - 0.6 * inward)
    order = np.argsort(z)
    for k in order:
        img = th[tid[k]]
        sc = s[k] * 1.25
        if sc < 0.3: continue
        hh, ww = int(img.shape[0] * sc), int(img.shape[1] * sc)
        if hh < 4: continue
        small = np.asarray(Image.fromarray((img * 255).astype(np.uint8)).resize((ww, hh), Image.BILINEAR), np.float32) / 255
        b = (0.25 + 0.75 * (z[k] + 1) / 2) * energy
        tinted = small * 0.75 + col * 0.25 * small.mean()
        x0 = int(xs[k] - ww / 2); y0 = int(ys[k] - hh / 2)
        if x0 < 0 or y0 < 0 or x0 + ww >= W or y0 + hh >= H: continue
        reg = a[y0:y0 + hh, x0:x0 + ww]
        a[y0:y0 + hh, x0:x0 + ww] = reg * (1 - 0.6 * b) + tinted * b * 1.1
        a[y0, x0:x0 + ww] += col * 0.35 * b; a[y0 + hh - 1, x0:x0 + ww] += col * 0.35 * b


def core_at(a, t, cx, cy, size, warm=0.0, energy=1.0, pupil=1.0):
    S = int(round(size / 16)) * 16
    c = ai_core(S, t, warm, energy, pupil)
    paste_add(a, c, cx, cy)
    return a


def room_view(t, zoom, cy_off=0.0, dark=1.0):
    room = plate("room", build_room)
    cx, cy = RW / 2, RH / 2 - 60 * (zoom - 1) * 4 + cy_off
    a = cam_arr(room, zoom, cx, cy) * dark
    # tira de luz parpadeante
    fl = 0.5 + 0.5 * math.sin(t * 37) * math.sin(t * 13.3)
    if fl > 0.6:
        y = int(H / 2 + (200 - cy) * zoom / (RW / W) / 1)
    def to_screen(px, py):
        s = zoom * W / RW
        return W / 2 + (px - cx) * s, H / 2 + (py - cy) * s, s
    return a, to_screen


def dust_motes(a, t, n=220, seed=3, color=(0.7, 0.8, 1.0), gain=0.5):
    rng = np.random.default_rng(seed)
    x = (rng.uniform(0, W, n) + np.sin(t * 0.4 + rng.uniform(0, 6, n)) * 30) % W
    y = (rng.uniform(0, H, n) - t * rng.uniform(5, 25, n)) % H
    v = rng.uniform(0.2, 1.0, n) * (0.5 + 0.5 * np.sin(t * 2 + rng.uniform(0, 6, n))) * gain
    add_points(a, x, y, v, np.array(color, np.float32))
    add_points(a, x + 1, y, v * 0.5, np.array(color, np.float32))


def scene2(t, f):
    lt = t - 4.0
    zoom = 1.0 + 0.10 * ease_in_out(lt / 5)
    a, ts = room_view(t, zoom)
    ccx, ccy, s = ts(RW / 2, 1150)
    energy = 0.6 + 0.4 * ease_out(lt / 1.2)
    # reflejo en el suelo
    refl = np.zeros_like(a)
    core_at(refl, t, ccx, ccy, 840 * s * RW / W)
    fy = int(ts(0, 1640)[1])
    hh = min(H - fy, fy)
    if hh > 0:
        a[fy:fy + hh] += blur_hdr(refl[fy - hh:fy][::-1], 10, 4) * 0.22 * energy
    core_at(a, t, ccx, ccy, 840 * s * RW / W, 0.0, energy)
    draw_swarm(a, t, ccx, ccy, 560 * s * RW / W, energy * ease_out(lt / 0.8))
    dust_motes(a, t)
    # luz azul del núcleo sobre la sala
    r = radial(W, H, ccx, ccy, 700, 900)
    a = a + np.array([0.04, 0.12, 0.2], np.float32) * np.exp(-r)[..., None] * energy
    if lt < 0.12: a = a * (lt / 0.12)
    return a, dict(tint_shadow=(0.0, 0.05, 0.1), tint_high=(0.85, 0.95, 1.05), bloom=0.8, contrast=1.15)


# =====================================================================================  ESCENA 3 / 6: RECUERDOS
def memory_view(name, lt, dur, zoom0=1.0, zoom1=1.08, dx=0.0, dy=0.0):
    a_pl = plate(name, lambda: hdr_to_pil(getattr(M, name)()[0]))
    u = lt / dur
    z = lerp(zoom0, zoom1, ease_in_out(u))
    pw, ph = a_pl.size
    cx = pw / 2 + dx * (u - 0.5) * pw
    cy = ph / 2 + dy * (u - 0.5) * ph
    return cam_arr(a_pl, z, cx, cy)


_rain = None


def rain(a, t, lamp=(540, 690)):
    global _rain
    if _rain is None:
        rng = np.random.default_rng(77)
        _rain = (rng.uniform(0, W, 700), rng.uniform(0, H, 700), rng.uniform(1400, 2200, 700), rng.uniform(20, 55, 700))
    x, y, v, L = _rain
    img = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    yy = (y + v * t) % H
    for i in range(len(x)):
        d.line([(x[i] - 0.08 * L[i], yy[i] - L[i]), (x[i], yy[i])], fill=int(150), width=2)
    m = np.asarray(img, np.float32) / 255
    r = np.exp(-radial(W, H, lamp[0], lamp[1], 520, 760))
    a += (m * (0.12 + 0.9 * r))[..., None] * np.array([0.8, 0.85, 1.0], np.float32)
    return a


def hud(a, t, strength=1.0):
    """Percepción de la IA: línea de escaneo y esquinas sutiles (mismo cian del Núcleo)."""
    col = np.array([0.3, 0.78, 1.0], np.float32) * strength
    y = int((t * 900) % (H + 200)) - 100
    if 0 <= y < H:
        for k in range(-30, 2):
            if 0 <= y + k < H:
                a[y + k] += col * 0.06 * (1 + k / 30)
        a[max(0, y):y + 2] += col * 0.35
    L, m, th = 70, 60, 3
    for (x0, y0, sx, sy) in ((m, m + 120, 1, 1), (W - m, m + 120, -1, 1), (m, H - m - 260, 1, -1), (W - m, H - m - 260, -1, -1)):
        xs = sorted([x0, x0 + sx * L]); ys = sorted([y0, y0 + sy * L])
        a[y0:y0 + th if sy > 0 else y0, xs[0]:xs[1]] += col * 0.5
        a[ys[0]:ys[1], x0:x0 + th if sx > 0 else x0] += col * 0.5
    return a


S3_SHOTS = [("shot_padre_hija", 9.0, 10.25, dict(zoom0=1.0, zoom1=1.07)),
            ("shot_pareja_lluvia", 10.25, 11.5, dict(zoom0=1.08, zoom1=1.0)),
            ("shot_ninos", 11.5, 12.75, dict(zoom0=1.05, zoom1=1.08, dx=0.08)),
            ("shot_ayuda", 12.75, 14.0, dict(zoom0=1.0, zoom1=1.08, dy=-0.02))]


def scene3(t, f):
    for name, t0, t1, kw in S3_SHOTS:
        if t0 <= t < t1:
            lt = t - t0
            a = memory_view(name, lt, t1 - t0, **kw)
            if name == "shot_pareja_lluvia":
                a = rain(a, t)
            a = hud(a, t, 0.6)
            if lt < 0.1: a = chroma_ab(a, 8 * (1 - lt / 0.1)) * (0.6 + 4 * lt)
            dust_motes(a, t, 120, 8, (1.0, 0.8, 0.5), 0.35)
            return a, dict(tint_shadow=(0.03, 0.03, 0.06), tint_high=(1.06, 0.92, 0.78), bloom=0.65, contrast=1.1)


S6_SHOTS = [("shot_ancianos", 25.0, 26.5, dict(zoom0=1.0, zoom1=1.05)),
            ("shot_madre_hijo", 26.5, 28.0, dict(zoom0=1.06, zoom1=1.0, dy=0.02)),
            ("shot_amigos", 28.0, 29.5, dict(zoom0=1.0, zoom1=1.06, dx=-0.03)),
            ("shot_abrazo", 29.5, 31.0, dict(zoom0=1.0, zoom1=1.12))]


def embers(a, t, n=160, seed=12, gain=0.7):
    rng = np.random.default_rng(seed)
    x = (rng.uniform(0, W, n) + np.sin(t * 0.8 + rng.uniform(0, 6, n)) * 40) % W
    y = (rng.uniform(0, H, n) - t * rng.uniform(40, 120, n)) % H
    v = rng.uniform(0.3, 1.0, n) * gain
    col = np.array([1.0, 0.7, 0.35], np.float32)
    for dx in (0, 1):
        for dy in (0, 1):
            add_points(a, x + dx, y + dy, v * (0.6 if dx or dy else 1), col)


def scene6(t, f):
    X = 0.27   # duración del fundido entre planos
    out = None
    for i, (name, t0, t1, kw) in enumerate(S6_SHOTS):
        lo = t0 - (X if i > 0 else 0)
        if lo <= t < t1:
            lt = t - t0 + 0.3
            img = memory_view(name, max(lt, 0), t1 - t0 + 0.6, **kw)
            w = 1.0 if (i == 0 or t >= t0) else ease_in_out((t - lo) / X)
            out = img * w if out is None else out * (1 - w) + img * w
    embers(out, t)
    # leve viñeta cálida + respiración de exposición
    return out, dict(tint_shadow=(0.04, 0.03, 0.05), tint_high=(1.08, 0.92, 0.75), bloom=0.75, contrast=1.08,
                     exposure=1.0 + 0.05 * math.sin(t * 2))


# =====================================================================================  ESCENA 4: LA PREGUNTA
WORDS = ["GUERRAS", "ERRORES", "LOGROS", "SUEÑOS", "AMOR", "MIEDO", "ARTE", "MÚSICA", "FE", "DOLOR", "ESPERANZA",
         "CIENCIA", "FAMILIA", "PERDÓN", "RISA", "MEMORIA", "HOGAR", "INFANCIA", "LÁGRIMAS", "PROMESAS", "CIUDADES",
         "IDIOMAS", "POEMAS", "FRONTERAS", "ESTRELLAS", "VACUNAS", "PUENTES", "CANCIONES", "ABRAZOS", "MADRES",
         "PADRES", "HIJOS", "AMIGOS", "VIAJES", "LIBROS", "MILAGROS", "DUDAS", "VALOR", "ORGULLO", "BONDAD"]
KEY_TIMES = {}


def set_key_times(subs):
    for ln in subs:
        for w in ln["words"]:
            k = w["w"].strip(",.").upper()
            if k in ("GUERRAS", "ERRORES", "LOGROS", "SUEÑOS"):
                KEY_TIMES[k] = w["t0"]


_wsprites = None


def word_sprites():
    global _wsprites
    if _wsprites is None:
        f = font("Inter-Light", 64)
        levels = [0.3, 0.45, 0.65, 0.9, 1.25, 1.7, 2.3]
        _wsprites = {}
        for wd in WORDS:
            tw = int(f.getlength(wd)) + 20
            im = Image.new("L", (tw, 90), 0)
            ImageDraw.Draw(im).text((10, 5), wd, font=f, fill=255)
            _wsprites[wd] = [(lv, np.asarray(im.resize((max(2, int(tw * lv)), max(2, int(90 * lv))), Image.BILINEAR),
                                             np.float32) / 255) for lv in levels]
    return _wsprites


_wpart = None


def word_particles():
    global _wpart
    if _wpart is None:
        rng = np.random.default_rng(14)
        n = 170
        idx = rng.integers(0, len(WORDS), n)
        for k in range(4): idx[k * 3] = k     # asegura las 4 palabras clave
        _wpart = (idx, rng.uniform(-1.3, 1.3, n), rng.uniform(-1.6, 1.6, n), rng.uniform(0.4, 4.0, n), rng.uniform(0.35, 0.8, n))
    return _wpart


def phrase_mask():
    return plate("phrase", lambda: text_layer(["¿QUÉ NOS HACÍA", "HUMANOS?"], font("InterDisplay-SemiBold", 104), tracking=6, cy=860))


def scene4(t, f):
    lt = t - 14.0
    a = np.zeros((H, W, 3), np.float32) + np.array([0.004, 0.008, 0.016], np.float32)
    # el Núcleo en primerísimo primer plano (mismo diseño, ampliado)
    zoom = 1.0 + 0.12 * lt / 5
    rev0 = clamp01((lt - 2.6) / 0.8)
    core_at(a, t, W / 2, 860, int(2000 * zoom), 0.0, 0.9 * (1 - 0.75 * rev0))
    a *= 0.75
    spr = word_sprites()
    idx, X, Y, Z, V = word_particles()
    conv = ease_in_out((lt - 2.3) / 0.9)       # las palabras se reorganizan hacia el centro
    cold = np.array([0.6, 0.85, 1.0], np.float32); amber = np.array([1.0, 0.7, 0.3], np.float32)
    for i in range(len(idx)):
        z = (Z[i] - V[i] * lt * 0.55) % 4.0 + 0.25
        s = 1.0 / z
        px = W / 2 + X[i] * 520 * s
        py = 860 + Y[i] * 520 * s
        px = lerp(px, W / 2 + (X[i] * 40), conv); py = lerp(py, 860 + Y[i] * 30, conv)
        s = s * (1 - conv * 0.85)
        alpha = min(1, (4.2 - z) / 1.2) * min(1, z / 0.45) * (1 - conv)
        if alpha <= 0.02: continue
        lv, m = min(spr[WORDS[idx[i]]], key=lambda q: abs(q[0] - s * 0.9))
        wd = WORDS[idx[i]]
        col = cold
        kt = KEY_TIMES.get(wd)
        boost = 0.55
        if kt is not None and kt - 0.05 <= t < kt + 0.9:
            col = amber; boost = 1.6
        hh, ww = m.shape
        x0, y0 = int(px - ww / 2), int(py - hh / 2)
        if x0 < 0 or y0 < 0 or x0 + ww > W or y0 + hh > H: continue
        a[y0:y0 + hh, x0:x0 + ww] += m[..., None] * col * alpha * boost
    # la frase aparece
    ph = phrase_mask()
    rev = clamp01((lt - 2.9) / 0.9)
    if rev > 0:
        rng = np.random.default_rng(1)
        cols = rng.uniform(0, 1, W)          # revelado por columnas aleatorias (organización)
        reveal = (cols[None, :] < rev).astype(np.float32) * ph
        glow = blur(reveal, 14, 2)
        a = a * (1 - 0.6 * ph[..., None] * rev) + reveal[..., None] * np.array([1.0, 0.98, 0.95], np.float32) * 1.1 \
            + glow[..., None] * cold * 0.9
    # pausa dramática: caída a negro al final
    if lt > 4.6: a = a * clamp01((5.0 - lt) / 0.4)
    return a, dict(tint_shadow=(0.0, 0.04, 0.09), tint_high=(0.9, 0.97, 1.05), bloom=0.8, contrast=1.15)


# =====================================================================================  ESCENA 5: EL GIRO
def build_photo():
    a, _ = M.shot_foto_familia()
    pw, ph = a.shape[1], a.shape[0]
    crop = a[int(ph * 0.38):int(ph * 0.92), int(pw * 0.08):int(pw * 0.92)]
    img = to_img(crop).resize((720, 540), Image.LANCZOS)
    arr = to_arr(img)
    lum = arr.mean(2, keepdims=True)
    sep = lum * np.array([1.07, 0.88, 0.66], np.float32) + 0.04
    rng = np.random.default_rng(8)
    sep = sep * (1 - 0.35 * clamp01(np.sqrt(radial(720, 540, 360, 270, 420, 330)) - 0.6))[..., None]
    pil = to_img(sep); d = ImageDraw.Draw(pil)
    sep_img = pil
    for _ in range(7):
        x = rng.uniform(0, 720); y0_ = rng.uniform(0, 300)
        d.line([(x, y0_), (x + rng.uniform(-20, 20), y0_ + rng.uniform(80, 240))], fill=(170, 150, 120), width=1)
    for _ in range(6):
        x, y, r = rng.uniform(0, 720), rng.uniform(0, 540), rng.uniform(10, 40)
        d.ellipse([x - r, y - r, x + r, y + r], outline=(150, 120, 90))
    pil = pil.filter(ImageFilter.GaussianBlur(1.6))
    framed = Image.new("RGB", (780, 600), (226, 214, 190))
    framed.paste(pil, (30, 30))
    fd = ImageDraw.Draw(framed)
    fd.polygon([(780, 0), (780, 70), (710, 0)], fill=(0, 0, 0))     # esquina rota
    return to_arr(framed)


def scene5(t, f):
    lt = t - 19.0
    warm = ease_in_out((lt - 1.4) / 2.2)
    zoom = 1.0 + 0.16 * ease_in_out(lt / 6)
    a, ts = room_view(t, zoom, cy_off=-120, dark=0.45)
    a = blur(a, 6, 2)                                          # fondo desenfocado (profundidad de campo)
    ccx, ccy, s = ts(RW / 2, 720)
    core_at(a, t, ccx, ccy, 700 * zoom, warm, 0.9)
    # haz de escaneo del Núcleo hacia la fotografía
    px, py, _ = ts(RW / 2, 1420)
    cone = Image.new("L", (W, H), 0)
    ImageDraw.Draw(cone).polygon([(ccx - 20, ccy + 60), (ccx + 20, ccy + 60), (px + 330 * zoom, py - 200 * zoom),
                                  (px - 330 * zoom, py - 200 * zoom)], fill=255)
    cm = blur(np.asarray(cone, np.float32) / 255, 26, 4)
    beamcol = np.array([0.3, 0.78, 1.0], np.float32) * (1 - warm) + np.array([1.0, 0.65, 0.3], np.float32) * warm
    a += cm[..., None] * beamcol * 0.16
    # fotografía antigua
    photo = plate("photo", build_photo)
    ph_img = to_img(photo).rotate(-2.5 + 1.0 * lt / 6, resample=Image.BICUBIC, expand=True)
    sc = zoom * 1.0
    ph_img = ph_img.resize((int(ph_img.width * sc), int(ph_img.height * sc)), Image.BILINEAR)
    parr = to_arr(ph_img)
    pm = (parr.sum(2) > 0.01).astype(np.float32)
    # la foto se ilumina con la luz del Núcleo
    light = 0.55 + 0.65 * warm
    beat = 0.0
    for bt, amp in ((23.25, 1.0), (23.58, 0.6)):
        beat += amp * math.exp(-max(0, t - bt) * 6) * (t >= bt)
    parr = parr * (light + 0.6 * beat) * (beamcol * 0.3 + 0.7)
    hh, ww = parr.shape[:2]
    x0, y0 = int(px - ww / 2), int(py - hh / 2)
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(W, x0 + ww), min(H, y0 + hh)
    sub = a[Y0:Y1, X0:X1]
    pmc = pm[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0][..., None]
    a[Y0:Y1, X0:X1] = sub * (1 - pmc) + parr[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0] * pmc
    # sombra / halo cálido alrededor de la foto
    halo = np.exp(-radial(W, H, px, py, 560 * zoom, 460 * zoom))
    a += halo[..., None] * np.array([1.0, 0.6, 0.3], np.float32) * (0.08 * warm + 0.25 * beat)
    dust_motes(a, t, 160, 5, tuple(beamcol), 0.4)
    ts_ = (np.array([0.0, 0.05, 0.1]) * (1 - warm) + np.array([0.05, 0.03, 0.02]) * warm)
    th_ = (np.array([0.85, 0.95, 1.05]) * (1 - warm) + np.array([1.08, 0.92, 0.76]) * warm)
    if lt < 0.15: a = a * (lt / 0.15)
    return a, dict(tint_shadow=tuple(ts_), tint_high=tuple(th_), bloom=0.7, contrast=1.12)


# =====================================================================================  ESCENA 7: EL MENSAJE
SW, SH = 1080, 2700


def build_space():
    rng = np.random.default_rng(303)
    a = np.zeros((SH, SW, 3), np.float32) + np.array([0.002, 0.003, 0.008], np.float32)
    # vía láctea tenue
    n = rng.normal(0, 1, (SH // 8, SW // 8)).astype(np.float32)
    neb = blur(clamp01(n * 0.5 + 0.5), 6, 1)
    neb = np.asarray(Image.fromarray((neb * 255).astype(np.uint8)).resize((SW, SH), Image.BICUBIC), np.float32) / 255
    y, x = np.mgrid[0:SH, 0:SW].astype(np.float32)
    band = np.exp(-((x * 0.55 + y * 0.25 - 900) / 260) ** 2)
    a += (neb * band)[..., None] * np.array([0.05, 0.06, 0.10], np.float32)
    # estrellas
    ns = 5200
    sx, sy = rng.uniform(0, SW, ns), rng.uniform(0, SH, ns)
    sv = rng.pareto(2.2, ns) * 0.18 + 0.05
    for c, k in zip(range(3), (0.9, 0.95, 1.0)):
        np.add.at(a[..., c], (sy.astype(int), sx.astype(int)), np.minimum(sv, 2.5) * k)
    big = sv > 1.0
    a += blur_hdr(a * 0.6, 2, 1)
    # Tierra: limbo nocturno con luces de ciudades
    R = 2600; ecx, ecy = SW / 2 + 150, SH - 650 + R
    d = np.sqrt((x - ecx) ** 2 + (y - ecy) ** 2)
    inside = d < R
    earth = np.zeros_like(a)
    earth[inside] = np.array([0.004, 0.006, 0.012], np.float32)
    # luces de ciudades
    nl = 26000
    ang = rng.uniform(-0.6, 0.6, nl) - np.pi / 2; rr = R - rng.exponential(220, nl)
    cl = rng.random(nl) < 0.5
    ang = np.where(cl, rng.normal(-np.pi / 2 + rng.uniform(-0.3, 0.3, nl) * 0, 0.12, nl) + rng.choice([-0.3, -0.1, 0.12, 0.28], nl), ang)
    lx = (ecx + np.cos(ang) * rr).astype(int); ly = (ecy + np.sin(ang) * rr).astype(int)
    ok = (lx >= 0) & (lx < SW) & (ly >= 0) & (ly < SH)
    lv = rng.uniform(0.1, 0.8, nl)[ok]
    for c, k in zip(range(3), (1.0, 0.62, 0.28)):
        np.add.at(earth[..., c], (ly[ok], lx[ok]), lv * k)
    earth = earth + blur_hdr(earth, 3, 1) * 1.5
    a = a * (~inside)[..., None] + earth * inside[..., None]
    # atmósfera
    rim = np.exp(-np.abs(d - R) / 14) + 0.5 * np.exp(-np.maximum(d - R, 0) / 60) * (d > R)
    side = clamp01((x - SW * 0.2) / SW) ** 1.5
    a += rim[..., None] * np.array([0.25, 0.55, 1.0], np.float32) * (0.25 + 1.4 * side)[..., None]
    # amanecer en el borde derecho
    sun = np.exp(-np.sqrt((x - SW * 1.02) ** 2 + ((y - (ecy - np.sqrt(max(R ** 2 - (SW * 1.02 - ecx) ** 2, 0)))) * 3) ** 2) / 90)
    a += sun[..., None] * np.array([1.0, 0.85, 0.65], np.float32) * 1.4
    return a


def scene7(t, f):
    lt = t - 31.0
    if lt < 1.3:
        # el Núcleo transmite: haz vertical que atraviesa la sala
        zoom = 1.08 + 0.05 * lt
        a, ts = room_view(t, zoom, cy_off=-180 * ease_in_out(lt / 1.3))
        a *= 0.7
        ccx, ccy, s = ts(RW / 2, 1150)
        en = 1.0 + 1.2 * ease_in_out(lt / 0.5)
        core_at(a, t, ccx, ccy, 840 * s * RW / W, 1.0, en, pupil=1.0 + 0.6 * ease_out(lt / 0.4))
        bw = 30 + 14 * math.sin(t * 40)
        x = np.arange(W, dtype=np.float32)
        beam = np.exp(-((x - ccx) / bw) ** 2) * 2.2 + np.exp(-((x - ccx) / (bw * 6)) ** 2) * 0.5
        ys = np.arange(H, dtype=np.float32)
        top = ccy - (ccy + 200) * ease_out(lt / 0.35)
        vmask = clamp01((ccy - ys) / 40) * (ys > top)
        a += (vmask[:, None] * beam[None, :])[..., None] * np.array([1.0, 0.82, 0.6], np.float32)
        # onda expansiva
        rr = lt * 1500
        ring = np.exp(-((np.sqrt(radial(W, H, ccx, ccy, 1, 1)) - rr) / 30) ** 2) * max(0, 1 - lt / 0.8)
        a += ring[..., None] * np.array([1.0, 0.75, 0.45], np.float32) * 0.8
        if lt < 0.08: a += 0.6 * (1 - lt / 0.08)
        return a, dict(tint_shadow=(0.02, 0.03, 0.06), tint_high=(1.05, 0.95, 0.85), bloom=0.9, contrast=1.12)
    # espacio: la luz del mensaje deja la Tierra
    st = lt - 1.3
    space = plate("space", lambda: hdr_to_pil(build_space(), 2.0))
    cy = SH - H / 2 - 260 * ease_in_out(st / 3.7)
    a = to_arr(camera(space, 1.0 + 0.04 * st / 3.7, SW / 2, cy, out=(W, H))) * 2.0
    off = SH - H / 2 - cy
    p0 = np.array([W / 2 + 40, 1640 + off]); p1 = np.array([W / 2 - 30, 330 + off * 0.4])
    u = ease_out(st / 3.4) ** 1.0
    pos = p0 + (p1 - p0) * u
    # estela
    n = 60
    for k in range(n):
        uu = max(0, u - 0.3 * k / n)
        q = p0 + (p1 - p0) * uu
        g = (1 - k / n) ** 2 * 0.06
        r = radial(64, 64, 32, 32, 6, 6)
        spot = np.exp(-r)[..., None] * np.array([1.0, 0.8, 0.55], np.float32) * g
        paste_add(a, spot, q[0], q[1])
    core = np.exp(-radial(W, H, pos[0], pos[1], 9, 9))
    halo = np.exp(-np.sqrt(radial(W, H, pos[0], pos[1], 1, 1)) / 60)
    streak = np.exp(-np.abs(np.arange(H, dtype=np.float32)[:, None] - pos[1]) / 2.5) * np.exp(-np.abs(np.arange(W, dtype=np.float32)[None, :] - pos[0]) / 380)
    pulse = 1 + 0.15 * math.sin(t * 14)
    a += (core * 3.0 + halo * 0.5 + streak * 0.5)[..., None] * np.array([1.0, 0.86, 0.66], np.float32) * pulse
    if st < 0.1: a = a * (st / 0.1) + (1 - st / 0.1) * 0.8
    return a, dict(tint_shadow=(0.0, 0.02, 0.06), tint_high=(1.0, 0.95, 0.9), bloom=0.9, contrast=1.15, grain=0.03)


def scene8(t, f):
    lt = t - 36.0
    a = np.zeros((H, W, 3), np.float32)
    # última chispa del mensaje que se pierde (continuidad), luego negro total
    if lt < 0.9:
        g = (1 - lt / 0.9) ** 2
        a += np.exp(-radial(W, H, W / 2 - 30, 380, 6, 6))[..., None] * np.array([1.0, 0.85, 0.65], np.float32) * 2.5 * g
    return a, dict(bloom=0.8, vig=False, grain=0.02)


SCENES = [(0.0, 4.0, scene1), (4.0, 9.0, scene2), (9.0, 14.0, scene3), (14.0, 19.0, scene4), (19.0, 25.0, scene5),
          (25.0, 31.0, scene6), (31.0, 36.0, scene7), (36.0, 40.01, scene8)]


def render_scene(t, f):
    for t0, t1, fn in SCENES:
        if t0 <= t < t1:
            return fn(t, f)
