"""Escenarios ilustrados 2D de Brote (se dibujan una vez y se reutilizan como imagen) + cámara + utilería."""
import math, random
import skia
from motor import (W, H, C, fill, stroke, lin, rad, rrect, path, typeface, text_center, ball, clamp, ease, lerp)

BW, BH = 1350, 2400          # mundo = 1.25 x pantalla; la cámara se mueve dentro
GROUND = 1760                # línea de suelo por defecto


def surface():
    s = skia.Surface(BW, BH); return s, s.getCanvas()


def sky(cv, top, mid, hor, y_h=1300, sun=None, sun_col=(255, 210, 140)):
    cv.drawRect(skia.Rect.MakeWH(BW, y_h + 50), lin((0, 0), (0, y_h), [top, mid, hor], [0, 0.55, 1]))
    if sun:
        x, y, r = sun
        cv.drawCircle(x, y, r * 7, rad((x, y), r * 7, [sun_col + (0.45,), sun_col + (0.0,)]))
        cv.drawCircle(x, y, r * 2.2, rad((x, y), r * 2.2, [(255, 245, 220, 0.9), sun_col + (0.0,)]))
        cv.drawCircle(x, y, r, fill((255, 248, 225)))


def buildings(cv, base_y, rnd, col, win_col, n_min=60, n_max=200, h_min=150, h_max=420, win_p=0.25, alpha=1.0):
    x = -40
    while x < BW + 40:
        w = rnd.uniform(n_min, n_max); h = rnd.uniform(h_min, h_max)
        cv.drawRect(skia.Rect.MakeXYWH(x, base_y - h, w, h + 400), fill(col, alpha))
        if rnd.random() < 0.3:
            cv.drawPath(path([(x - 8, base_y - h), (x + w / 2, base_y - h - w * 0.35), (x + w + 8, base_y - h)]), fill(tuple(int(v * 0.85) for v in col), alpha))
        for wy in range(int(base_y - h + 20), int(base_y - 30), 46):
            for wx in range(int(x + 14), int(x + w - 24), 38):
                if rnd.random() < win_p:
                    cv.drawRect(skia.Rect.MakeXYWH(wx, wy, 18, 24), fill(win_col, 0.9 * alpha))
        x += w + rnd.uniform(4, 30)


def house_row(cv, base_y, rnd, warm=True):
    cols = [(232, 170, 110), (150, 190, 205), (236, 214, 160), (205, 120, 100), (170, 190, 130), (240, 230, 215)]
    x = -60
    while x < BW + 60:
        w = rnd.uniform(220, 340); h = rnd.uniform(230, 360); c = cols[rnd.randrange(len(cols))]
        shade = tuple(int(v * 0.78) for v in c)
        cv.drawRect(skia.Rect.MakeXYWH(x, base_y - h, w, h + 300), lin((x, 0), (x + w, 0), [c, shade]))
        cv.drawPath(path([(x - 14, base_y - h + 4), (x + w / 2, base_y - h - 70), (x + w + 14, base_y - h + 4)]), fill((140, 70, 50)))
        for k in range(int(w // 110)):
            wx = x + 30 + k * 110; wy = base_y - h + 70
            lit = rnd.random() < 0.45
            rrect(cv, wx, wy, 62, 78, 6, fill((255, 205, 130) if lit and warm else (70, 90, 110)))
            cv.drawLine(wx + 31, wy, wx + 31, wy + 78, stroke((255, 255, 255), 3, 0.6))
        x += w + rnd.uniform(-10, 20)


def tree(cv, x, y, s, rnd, col=(70, 140, 70)):
    cv.drawRect(skia.Rect.MakeXYWH(x - 10 * s, y - 140 * s, 20 * s, 140 * s), fill((90, 60, 40)))
    for k in range(7):
        cx = x + rnd.uniform(-60, 60) * s; cy = y - 170 * s + rnd.uniform(-60, 40) * s; r = rnd.uniform(45, 70) * s
        cv.drawCircle(cx, cy, r, rad((cx - r * 0.3, cy - r * 0.4), r * 1.3, [tuple(min(255, int(v * 1.25)) for v in col), col, tuple(int(v * 0.7) for v in col)]))


def wires(cv, y, rnd):
    for px in (120, 680, 1240):
        cv.drawRect(skia.Rect.MakeXYWH(px - 9, y - 40, 18, 470), fill((90, 64, 44)))
        cv.drawRect(skia.Rect.MakeXYWH(px - 50, y, 100, 10), fill((90, 64, 44)))
    for dy in (0, 26):
        for a, b in ((120, 680), (680, 1240)):
            pth = skia.Path(); pth.moveTo(a, y + dy); pth.quadTo((a + b) / 2, y + dy + 60, b, y + dy)
            cv.drawPath(pth, stroke((30, 30, 30), 2.5, cap=False))


def fence(cv, y0, y1, col=(150, 155, 160), a=0.75):
    st = stroke(col, 2.2, a)
    step = 34
    for x in range(-int(y1 - y0), BW + 40, step):
        cv.drawLine(x, y1, x + (y1 - y0), y0, st); cv.drawLine(x, y0, x + (y1 - y0), y1, st)
    for x in range(0, BW + 1, 270):
        cv.drawRect(skia.Rect.MakeXYWH(x - 6, y0 - 10, 12, y1 - y0 + 10), fill((120, 122, 126)))
    cv.drawRect(skia.Rect.MakeXYWH(0, y0 - 8, BW, 10), fill((120, 122, 126)))


def concrete(cv, y0, y1, c1=(150, 148, 146), c2=(110, 108, 106), rnd=None):
    cv.drawRect(skia.Rect.MakeXYWH(0, y0, BW, y1 - y0), lin((0, y0), (0, y1), [c1, c2]))
    rnd = rnd or random.Random(5)
    for k in range(1600):
        x = rnd.uniform(0, BW); y = rnd.uniform(y0, y1); v = rnd.uniform(-1, 1)
        cv.drawCircle(x, y, rnd.uniform(0.8, 2.2), fill((255, 255, 255) if v > 0 else (0, 0, 0), 0.08 * abs(v)))
    for k in range(10):   # grietas
        x = rnd.uniform(0, BW); y = rnd.uniform(y0 + 30, y1)
        pts = [(x, y)]
        for j in range(5): x += rnd.uniform(-30, 40); y += rnd.uniform(-8, 22); pts.append((x, y))
        cv.drawPath(path(pts, False), stroke((70, 68, 66), 2, 0.55))


def court_lines(cv, y0, y1, col=(235, 232, 220), a=0.75):
    st = stroke(col, 6, a)
    cv.drawPath(path([(170, y0), (BW - 170, y0), (BW + 120, y1), (-120, y1)]), st)
    cv.drawLine(BW / 2 - 30, y0, BW / 2 - 90, y1, st)
    cv.drawOval(skia.Rect.MakeXYWH(BW / 2 - 330, y0 + 60, 520, 170), st)


def hoop(cv, x, y_rim, rusty=True, glass=False, s=1.0):
    pole = (110, 80, 60) if rusty else (60, 64, 72)
    cv.drawRect(skia.Rect.MakeXYWH(x + 150 * s, y_rim - 120 * s, 22 * s, 1200 * s), lin((x + 150 * s, 0), (x + 172 * s, 0), [pole, tuple(int(v * 0.6) for v in pole)]))
    cv.drawRect(skia.Rect.MakeXYWH(x + 60 * s, y_rim - 100 * s, 100 * s, 14 * s), fill(pole))
    bb = skia.Rect.MakeXYWH(x - 90 * s, y_rim - 210 * s, 180 * s, 140 * s)
    if glass:
        cv.drawRect(bb, fill((210, 230, 245), 0.55)); cv.drawRect(bb, stroke((40, 40, 40), 5 * s))
    else:
        cv.drawRect(bb, lin((0, bb.top()), (0, bb.bottom()), [(238, 234, 222), (205, 198, 182)]))
        cv.drawRect(bb, stroke((150, 80, 50) if rusty else (40, 40, 40), 5 * s))
        for k in range(6):
            cv.drawCircle(x + random.Random(k).uniform(-80, 80) * s, y_rim - random.Random(k + 9).uniform(80, 200) * s, 6 * s, fill((160, 100, 60), 0.35))
    cv.drawRect(skia.Rect.MakeXYWH(x - 36 * s, y_rim - 135 * s, 72 * s, 55 * s), stroke((200, 60, 40), 5 * s))


def rim_and_net(cv, x, y_rim, s=1.0, rusty=True, swish=0.0, t=0.0):
    """Aro y red (se dibujan delante del balón). swish 0..1 = la red se mueve tras una canasta."""
    col = (170, 80, 40) if rusty else (240, 90, 20)
    for k in range(9):
        a0 = x - 52 * s + k * 13 * s
        wob = math.sin(t * 25 + k) * 8 * s * swish
        cv.drawLine(a0, y_rim, x - 30 * s + k * 7.5 * s + wob, y_rim + 75 * s + 10 * s * swish, stroke((240, 240, 235), 2.5 * s, 0.9))
    for j in range(1, 4):
        yy = y_rim + j * 22 * s + 4 * s * swish
        cv.drawLine(x - (52 - j * 6) * s, yy, x + (52 - j * 6) * s, yy, stroke((240, 240, 235), 2 * s, 0.7))
    cv.drawOval(skia.Rect.MakeXYWH(x - 56 * s, y_rim - 9 * s, 112 * s, 18 * s), stroke(col, 7 * s))


# ------------------------------------------------------------------ escenarios
_cache = {}


def bg(name):
    if name not in _cache:
        s, cv = surface(); rnd = random.Random(hash(name) % 1000)
        BUILD[name](cv, rnd)
        _cache[name] = s.makeImageSnapshot()
    return _cache[name]


def _cancha(cv, rnd, mood="tarde"):
    if mood == "tarde":
        sky(cv, (60, 70, 140), (220, 120, 120), (255, 175, 95), 1330, sun=(980, 1180, 70))
        far = (120, 90, 140); win = (255, 210, 140)
    elif mood == "amanecer":
        sky(cv, (90, 140, 210), (250, 170, 170), (255, 215, 150), 1330, sun=(260, 1240, 60), sun_col=(255, 225, 170))
        far = (150, 140, 190); win = (255, 230, 180)
    else:  # dorado (final)
        sky(cv, (70, 90, 170), (245, 150, 100), (255, 200, 110), 1330, sun=(700, 1150, 80))
        far = (130, 100, 150); win = (255, 220, 150)
    buildings(cv, 1330, rnd, far, win, h_min=120, h_max=330, win_p=0.18, alpha=0.75)
    house_row(cv, 1440, rnd)
    for x in (90, 420, 960, 1260): tree(cv, x + rnd.uniform(-30, 30), 1450, 1.1, rnd)
    wires(cv, 980, rnd)
    fence(cv, 1310, 1560)
    concrete(cv, 1540, BH, (160, 156, 150), (112, 110, 106), rnd)
    court_lines(cv, 1600, 2300)
    for k in range(30):   # hojas secas
        x, y = rnd.uniform(0, BW), rnd.uniform(1560, 2350)
        cv.drawOval(skia.Rect.MakeXYWH(x, y, 14, 7), fill((150, 90, 40), 0.8))
    hoop(cv, 1010, 1080, rusty=True)


def _cancha_tarde(cv, rnd): _cancha(cv, rnd, "tarde")
def _cancha_amanecer(cv, rnd):
    _cancha(cv, rnd, "amanecer")
    for x, y in ((300, 1900), (520, 2000), (740, 1880), (960, 1990)):   # conos
        cv.drawPath(path([(x - 26, y), (x + 26, y), (x + 8, y - 70), (x - 8, y - 70)]), fill((255, 120, 30)))
        cv.drawRect(skia.Rect.MakeXYWH(x - 18, y - 40, 36, 10), fill((255, 255, 255)))
        cv.drawRect(skia.Rect.MakeXYWH(x - 34, y - 6, 68, 8), fill((230, 100, 20)))
def _cancha_dorada(cv, rnd): _cancha(cv, rnd, "dorado")


def _gimnasio(cv, rnd):
    cv.drawRect(skia.Rect.MakeWH(BW, 1500), lin((0, 0), (0, 1500), [(232, 236, 242), (214, 220, 230)]))
    for x in range(40, BW, 300):
        rrect(cv, x, 420, 240, 150, 8, lin((0, 420), (0, 570), [(255, 255, 255), (200, 225, 250)]))
        cv.drawRect(skia.Rect.MakeXYWH(x + 118, 420, 4, 150), fill((180, 190, 200)))
    cv.drawRect(skia.Rect.MakeXYWH(0, 1120, BW, 400), fill((52, 100, 170)))
    cv.drawRect(skia.Rect.MakeXYWH(0, 1110, BW, 14), fill((240, 200, 60)))
    for k in range(4):   # gradería
        cv.drawRect(skia.Rect.MakeXYWH(0, 1290 + k * 60, 300 - k * 40, 62), fill((170, 120, 70) if k % 2 else (190, 140, 85)))
    cv.drawRect(skia.Rect.MakeXYWH(0, 1500, BW, BH - 1500), lin((0, 1500), (0, BH), [(214, 160, 100), (190, 128, 70)]))
    for y in range(1500, BH, 46):
        cv.drawLine(0, y, BW, y, stroke((160, 105, 55), 2, 0.6))
        off = rnd.uniform(0, 300)
        for x in range(int(off) - 300, BW, 300): cv.drawLine(x, y, x, y + 46, stroke((160, 105, 55), 2, 0.5))
    cv.drawRect(skia.Rect.MakeXYWH(0, 1500, BW, 300), lin((0, 1500), (0, 1800), [(255, 255, 255, 0.35), (255, 255, 255, 0.0)]))
    cv.drawPath(path([(420, 1500), (930, 1500), (1050, 1900), (300, 1900)]), fill((52, 100, 170), 0.85))
    court_lines(cv, 1560, 2300, (255, 255, 255), 0.9)
    for x in (300, 700, 1100):
        rrect(cv, x - 90, 60, 180, 22, 8, fill((255, 255, 240)))
        cv.drawCircle(x, 80, 160, rad((x, 80), 160, [(255, 255, 230, 0.35), (255, 255, 230, 0.0)]))
    hoop(cv, 1000, 1080, rusty=False, glass=True)


def _casa_tarde(cv, rnd, night=False):
    wall = (232, 196, 150) if not night else (60, 70, 110)
    cv.drawRect(skia.Rect.MakeWH(BW, 1760), lin((0, 0), (0, 1760), [wall, tuple(int(v * 0.85) for v in wall)]))
    for k in range(400):
        cv.drawCircle(rnd.uniform(0, BW), rnd.uniform(0, 1760), rnd.uniform(1, 3), fill((0, 0, 0), 0.03))
    wx, wy = 760, 760
    rrect(cv, wx - 14, wy - 14, 448, 448, 10, fill((120, 80, 50)))
    if night:
        cv.drawRect(skia.Rect.MakeXYWH(wx, wy, 420, 420), lin((0, wy), (0, wy + 420), [(20, 30, 70), (50, 60, 110)]))
        cv.drawCircle(wx + 300, wy + 110, 46, fill((250, 245, 220))); cv.drawCircle(wx + 300, wy + 110, 120, fill((250, 245, 220), 0.12, blur=30))
        for k in range(14): cv.drawCircle(wx + rnd.uniform(10, 410), wy + rnd.uniform(10, 300), 2, fill((255, 255, 255), 0.8))
    else:
        cv.drawRect(skia.Rect.MakeXYWH(wx, wy, 420, 420), lin((0, wy), (0, wy + 420), [(255, 170, 110), (255, 220, 150)]))
        cv.drawCircle(wx + 260, wy + 300, 50, fill((255, 245, 210)))
        cv.save(); cv.clipRect(skia.Rect.MakeXYWH(wx, wy, 420, 420))
        buildings(cv, wy + 420, random.Random(3), (200, 120, 110), (255, 220, 150), 40, 90, 60, 180, 0.2)
        cv.restore()
    cv.drawLine(wx + 210, wy, wx + 210, wy + 420, stroke((120, 80, 50), 12)); cv.drawLine(wx, wy + 210, wx + 420, wy + 210, stroke((120, 80, 50), 12))
    for sx in (wx - 90, wx + 420):
        cv.drawRect(skia.Rect.MakeXYWH(sx, wy - 40, 90, 520), lin((sx, 0), (sx + 90, 0), [(190, 60, 50), (150, 40, 34)]))
    rrect(cv, 160, 600, 170, 130, 6, fill((90, 60, 40))); rrect(cv, 172, 612, 146, 106, 4, fill((230, 210, 170)))   # cuadro
    cv.drawRect(skia.Rect.MakeXYWH(0, 1760, BW, BH - 1760), lin((0, 1760), (0, BH), [(150, 96, 56), (110, 68, 38)]))
    for y in range(1760, BH, 60): cv.drawLine(0, y, BW, y, stroke((90, 56, 30), 2, 0.6))
    if not night:
        # luz cálida de la ventana sobre el piso
        cv.drawPath(path([(wx, 1760), (wx + 420, 1760), (wx + 300, BH), (wx - 260, BH)]), fill((255, 200, 120), 0.18))


def _casa(cv, rnd): _casa_tarde(cv, rnd, False)


def _pieza_noche(cv, rnd):
    _casa_tarde(cv, rnd, True)
    # cama
    rrect(cv, 80, 1560, 700, 220, 20, fill((90, 60, 40)))
    rrect(cv, 100, 1500, 660, 130, 30, fill((90, 110, 180)))
    rrect(cv, 110, 1470, 200, 80, 30, fill((235, 235, 245)))
    # puerta entreabierta con luz
    cv.drawRect(skia.Rect.MakeXYWH(1080, 900, 260, 860), fill((40, 30, 30)))
    cv.drawPath(path([(1080, 900), (1130, 900), (1130, 1760), (1080, 1760)]), fill((255, 200, 120), 0.9))
    cv.drawPath(path([(1080, 1760), (1130, 1760), (1000, BH), (700, BH)]), fill((255, 200, 120), 0.18))


def _puerta(cv, rnd):
    sky(cv, (120, 170, 230), (210, 225, 240), (255, 230, 190), 1000, sun=(1150, 400, 60), sun_col=(255, 235, 190))
    cv.drawRect(skia.Rect.MakeXYWH(0, 300, BW, 1500), lin((0, 0), (BW, 0), [(236, 214, 160), (210, 186, 130)]))
    rrect(cv, 380, 760, 520, 1000, 10, fill((120, 70, 40)))
    rrect(cv, 410, 790, 460, 940, 8, lin((0, 790), (0, 1730), [(160, 96, 56), (130, 76, 42)]))
    cv.drawCircle(820, 1280, 16, fill((230, 190, 80)))
    cv.drawRect(skia.Rect.MakeXYWH(300, 1760, 680, 60), fill((170, 160, 150)))
    cv.drawRect(skia.Rect.MakeXYWH(0, 1820, BW, BH - 1820), lin((0, 1820), (0, BH), [(150, 148, 140), (110, 108, 100)]))
    rrect(cv, 1020, 1560, 140, 200, 14, fill((190, 90, 60)))
    for k in range(8): tree_leaf = cv.drawCircle(1090 + rnd.uniform(-70, 70), 1520 + rnd.uniform(-70, 40), 40, fill((70, 150, 80)))
    cv.drawPath(path([(1350, 300), (1350, 1820), (900, 1820)]), fill((255, 240, 200), 0.12))


def _colegio(cv, rnd, poster="pruebas"):
    sky(cv, (110, 150, 220), (240, 180, 150), (255, 210, 150), 700, sun=(1100, 520, 60))
    cv.drawRect(skia.Rect.MakeXYWH(0, 640, BW, 1200), fill((150, 64, 44)))
    for row, y in enumerate(range(640, 1840, 44)):
        off = 0 if row % 2 else 60
        for x in range(-off, BW, 120):
            c = rnd.uniform(0.85, 1.1)
            rrect(cv, x + 3, y + 3, 114, 38, 3, fill(tuple(min(255, int(v * c)) for v in (178, 82, 56))))
    for x in (60, 1050):
        rrect(cv, x, 760, 240, 260, 6, fill((90, 110, 130))); cv.drawRect(skia.Rect.MakeXYWH(x + 10, 770, 220, 240), lin((0, 770), (0, 1010), [(170, 200, 230), (120, 150, 180)]))
    concrete(cv, 1840, BH, (175, 172, 166), (130, 128, 124), rnd)
    # cartel
    px, py, pw, ph = 420, 850, 510, 720
    cv.drawRect(skia.Rect.MakeXYWH(px + 8, py + 12, pw, ph), fill((0, 0, 0), 0.25, blur=10))
    cv.drawRect(skia.Rect.MakeXYWH(px, py, pw, ph), fill((248, 242, 226)))
    for (tx, ty) in ((px - 10, py - 6), (px + pw - 50, py - 6)):
        cv.save(); cv.translate(tx + 30, ty + 10); cv.rotate(-20 if tx < px + 10 else 20); rrect(cv, -30, -10, 60, 20, 2, fill((230, 220, 180), 0.9)); cv.restore()
    if poster == "pruebas":
        cv.drawRect(skia.Rect.MakeXYWH(px, py, pw, 120), fill((200, 40, 30)))
        text_center(cv, "PRUEBAS", px + pw / 2, py + 60, 82, (255, 255, 255), None, shadow_=False)
        text_center(cv, "DEL EQUIPO", px + pw / 2, py + 190, 66, (30, 30, 30), None, shadow_=False)
        text_center(cv, "—", px + pw / 2, py + 270, 50, (30, 30, 30), None, shadow_=False)
        text_center(cv, "VIERNES", px + pw / 2, py + 350, 96, (200, 40, 30), None, shadow_=False)
        ball(cv, px + pw / 2, py + 560, 100, 0.3)
    else:
        cv.drawRect(skia.Rect.MakeXYWH(px, py, pw, 120), fill((40, 120, 60)))
        text_center(cv, "ÚLTIMO CUPO", px + pw / 2, py + 60, 72, (255, 255, 255), None, shadow_=False)
        text_center(cv, "PARTIDO", px + pw / 2, py + 210, 74, (30, 30, 30), None, shadow_=False)
        text_center(cv, "DEL BARRIO", px + pw / 2, py + 290, 64, (30, 30, 30), None, shadow_=False)
        text_center(cv, "SÁBADO", px + pw / 2, py + 400, 96, (40, 120, 60), None, shadow_=False)
        ball(cv, px + pw / 2, py + 590, 80, 0.8)


def _colegio_pruebas(cv, rnd): _colegio(cv, rnd, "pruebas")
def _colegio_cupo(cv, rnd): _colegio(cv, rnd, "cupo")


def _bodega(cv, rnd):
    cv.drawRect(skia.Rect.MakeWH(BW, 1780), lin((0, 0), (0, 1780), [(70, 70, 76), (46, 46, 52)]))
    for k in range(600): cv.drawCircle(rnd.uniform(0, BW), rnd.uniform(0, 1780), rnd.uniform(1, 4), fill((0, 0, 0), 0.06))
    cv.drawPath(path([(980, 0), (1250, 0), (900, 1780), (480, 1780)]), fill((255, 230, 170), 0.12))   # haz de luz
    for y in (700, 1000):
        cv.drawRect(skia.Rect.MakeXYWH(40, y, 300, 18), fill((110, 90, 70)))
        for k in range(3): rrect(cv, 60 + k * 90, y - 90, 70, 90, 6, fill((150 - k * 20, 110, 70)))
    cv.drawRect(skia.Rect.MakeXYWH(0, 1780, BW, BH - 1780), lin((0, 1780), (0, BH), [(110, 104, 96), (80, 76, 70)]))
    tree_ = None


BUILD = {"cancha_tarde": _cancha_tarde, "cancha_amanecer": _cancha_amanecer, "cancha_dorada": _cancha_dorada,
         "gimnasio": _gimnasio, "casa": _casa, "pieza_noche": _pieza_noche, "puerta": _puerta,
         "colegio_pruebas": _colegio_pruebas, "colegio_cupo": _colegio_cupo, "bodega": _bodega}


# ------------------------------------------------------------------ cámara
class Cam:
    """Encuadre del mundo (BW x BH) en la pantalla. z=1 muestra el ancho completo del mundo."""
    def __init__(self, cx=BW / 2, cy=BH / 2, z=1.0, shake=0.0, t=0.0):
        self.cx, self.cy, self.z = cx, cy, z
        if shake:
            self.cx += math.sin(t * 61) * shake; self.cy += math.cos(t * 53) * shake

    def apply(self, cv):
        k = self.z * W / BW
        hw, hh = (W / 2) / k, (H / 2) / k
        self.cx = min(max(self.cx, hw), BW - hw); self.cy = min(max(self.cy, hh), BH - hh)
        cv.translate(W / 2, H / 2); cv.scale(k, k); cv.translate(-self.cx, -self.cy)


def cam_move(t, dur, a, b):
    u = ease(t / dur)
    return Cam(lerp(a[0], b[0], u), lerp(a[1], b[1], u), lerp(a[2], b[2], u))


def draw_bg(cv, name):
    cv.drawImage(bg(name), 0, 0)


def particles(cv, t, n, seed, col, area=(0, 0, BW, BH), up=30, size=(2, 5), a=0.6):
    rnd = random.Random(seed)
    for k in range(n):
        x = area[0] + (rnd.uniform(0, area[2]) + math.sin(t * 0.7 + k) * 20) % area[2]
        y = area[1] + (rnd.uniform(0, area[3]) - t * up * rnd.uniform(0.5, 1.5)) % area[3]
        cv.drawCircle(x, y, rnd.uniform(*size), fill(col, a * (0.5 + 0.5 * math.sin(t * 2 + k))))


def vignette(cv, strength=0.45):
    p = rad((W / 2, H / 2), H * 0.75, [(0, 0, 0, 0.0), (0, 0, 0, 0.0), (0, 0, 0, strength)], [0, 0.6, 1])
    cv.drawRect(skia.Rect.MakeWH(W, H), p)


def paper(cv, x, y, w, h, rot=0, col=(250, 248, 240)):
    cv.save(); cv.translate(x, y); cv.rotate(rot)
    cv.drawRect(skia.Rect.MakeXYWH(-w / 2 + 10, -h / 2 + 14, w, h), fill((0, 0, 0), 0.3, blur=14))
    cv.drawRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), fill(col))
    cv.restore()
