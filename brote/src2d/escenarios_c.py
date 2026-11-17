"""Escenarios de la semana 2 (Camila y el robot de chatarra). Se registran en escenarios.BUILD."""
import math, random
import skia
from motor import (C, fill, stroke, lin, rad, rrect, path, typeface, text_center, clamp, lerp)
import escenarios as E
from escenarios import BW, BH, sky, buildings, house_row, tree, concrete


def _speckle(cv, rnd, x0, y0, w, h, n=500, a=0.04):
    for k in range(n):
        cv.drawCircle(x0 + rnd.uniform(0, w), y0 + rnd.uniform(0, h), rnd.uniform(1, 3), fill((0, 0, 0), a))


# ------------------------------------------------------------------ feria de cosas viejas
def _feria(cv, rnd):
    sky(cv, (120, 180, 235), (190, 220, 240), (255, 236, 200), 1200, sun=(1120, 520, 60), sun_col=(255, 240, 200))
    buildings(cv, 1200, rnd, (170, 160, 190), (255, 240, 200), h_min=120, h_max=300, win_p=0.12, alpha=0.6)
    house_row(cv, 1300, rnd, warm=False)
    # banderines
    for row, (y0, sag) in enumerate(((760, 90), (900, 70))):
        pts = [(x, y0 + sag * math.sin(math.pi * x / BW)) for x in range(0, BW + 1, 45)]
        cv.drawPath(path(pts, False), stroke((80, 70, 60), 3))
        for k, (x, y) in enumerate(pts[:-1]):
            col = [(230, 80, 70), (255, 200, 61), (46, 158, 79), (70, 130, 220), (240, 240, 240)][(k + row) % 5]
            cv.drawPath(path([(x + 4, y + 2), (x + 40, y + 2), (x + 22, y + 44)]), fill(col))
    # suelo adoquinado
    cv.drawRect(skia.Rect.MakeXYWH(0, 1540, BW, BH - 1540), lin((0, 1540), (0, BH), [(186, 172, 150), (140, 128, 110)]))
    for row, y in enumerate(range(1540, BH, 54)):
        off = 0 if row % 2 else 70
        for x in range(-off, BW, 140):
            rrect(cv, x + 4, y + 4, 132, 46, 10, fill((255, 255, 255) if rnd.random() < 0.5 else (0, 0, 0), rnd.uniform(0.02, 0.07)))
    # puestos
    stalls = [(40, (220, 70, 60)), (490, (46, 140, 180)), (940, (240, 170, 50))]
    for sx, col in stalls:
        w = 400
        for px in (sx + 14, sx + w - 30): cv.drawRect(skia.Rect.MakeXYWH(px, 1020, 16, 560), fill((120, 88, 60)))
        # toldo a rayas
        cv.drawPath(path([(sx - 20, 1090), (sx + w + 20, 1090), (sx + w - 10, 980), (sx + 10, 980)]), fill(col))
        for k in range(0, 10, 2):
            x0 = sx - 20 + k * (w + 40) / 10; x1 = x0 + (w + 40) / 10
            xa = sx + 10 + k * (w - 20) / 10; xb = xa + (w - 20) / 10
            cv.drawPath(path([(x0, 1090), (x1, 1090), (xb, 980), (xa, 980)]), fill((250, 246, 236)))
        for k in range(10):
            cx_ = sx - 20 + (k + 0.5) * (w + 40) / 10
            cv.drawCircle(cx_, 1092, (w + 40) / 20, fill(col if k % 2 else (250, 246, 236)))
        # mesa con mantel
        rrect(cv, sx, 1400, w, 34, 6, fill((130, 92, 60)))
        cv.drawRect(skia.Rect.MakeXYWH(sx + 10, 1430, w - 20, 150), fill(tuple(int(v * 0.75) for v in col)))
        for k in range(6): cv.drawLine(sx + 30 + k * 66, 1436, sx + 30 + k * 66, 1578, stroke((0, 0, 0), 3, 0.12))
        # cachivaches sobre la mesa
        items = rnd.sample(["radio", "lampara", "reloj", "caja", "tele", "tetera", "libros"], 4)
        for k, it in enumerate(items):
            ix = sx + 50 + k * 95; iy = 1400
            if it == "radio":
                rrect(cv, ix - 36, iy - 56, 72, 56, 8, fill((150, 96, 60))); cv.drawCircle(ix - 12, iy - 28, 16, fill((60, 44, 34)))
                cv.drawRect(skia.Rect.MakeXYWH(ix + 10, iy - 44, 18, 8), fill((230, 220, 190))); cv.drawLine(ix + 24, iy - 56, ix + 44, iy - 100, stroke((120, 120, 120), 3))
            elif it == "lampara":
                cv.drawRect(skia.Rect.MakeXYWH(ix - 4, iy - 70, 8, 70), fill((180, 150, 80)))
                cv.drawPath(path([(ix - 34, iy - 70), (ix + 34, iy - 70), (ix + 20, iy - 120), (ix - 20, iy - 120)]), fill((240, 220, 170)))
            elif it == "reloj":
                cv.drawCircle(ix, iy - 38, 36, fill((200, 60, 60))); cv.drawCircle(ix, iy - 38, 28, fill((250, 246, 236)))
                cv.drawLine(ix, iy - 38, ix, iy - 58, stroke((30, 30, 30), 3)); cv.drawLine(ix, iy - 38, ix + 14, iy - 34, stroke((30, 30, 30), 3))
            elif it == "caja":
                rrect(cv, ix - 40, iy - 46, 80, 46, 4, fill((196, 150, 96)))
                for j in range(5):
                    pth = skia.Path(); pth.moveTo(ix - 30 + j * 14, iy - 44); pth.quadTo(ix - 40 + j * 22, iy - 90 - j * 6, ix - 20 + j * 12, iy - 60)
                    cv.drawPath(pth, stroke([(220, 60, 60), (40, 40, 40), (60, 140, 220), (240, 200, 60), (40, 160, 90)][j], 4))
            elif it == "tele":
                rrect(cv, ix - 42, iy - 70, 84, 70, 10, fill((90, 80, 76))); rrect(cv, ix - 32, iy - 60, 52, 46, 8, fill((140, 170, 170)))
                cv.drawCircle(ix + 32, iy - 48, 5, fill((220, 200, 150))); cv.drawCircle(ix + 32, iy - 30, 5, fill((220, 200, 150)))
            elif it == "tetera":
                cv.drawOval(skia.Rect.MakeXYWH(ix - 34, iy - 56, 68, 56), fill((90, 140, 170))); cv.drawArc(skia.Rect.MakeXYWH(ix + 16, iy - 48, 36, 34), -90, 180, False, stroke((90, 140, 170), 7))
                cv.drawCircle(ix, iy - 60, 8, fill((60, 100, 130)))
            else:
                for j in range(3): rrect(cv, ix - 38 + j * 4, iy - 18 - j * 18, 74, 18, 3, fill([(170, 60, 60), (60, 110, 160), (220, 180, 90)][j]))
        # cajones de madera bajo la mesa
        for k in range(2):
            bx = sx + 40 + k * 170
            rrect(cv, bx, 1590, 130, 90, 4, fill((176, 132, 84)))
            for j in range(3): cv.drawLine(bx, 1612 + j * 26, bx + 130, 1612 + j * 26, stroke((120, 88, 54), 3))
    cv.drawRect(skia.Rect.MakeXYWH(0, 1540, BW, 180), lin((0, 1540), (0, 1720), [(0, 0, 0, 0.18), (0, 0, 0, 0.0)]))


# ------------------------------------------------------------------ cuarto de Camila
def _mini_robot(cv, x, y, s, col):
    st = stroke(col, 3 * s)
    cv.drawRect(skia.Rect.MakeXYWH(x - 22 * s, y - 20 * s, 44 * s, 50 * s), st)
    cv.drawRect(skia.Rect.MakeXYWH(x - 16 * s, y - 52 * s, 32 * s, 26 * s), st)
    cv.drawCircle(x - 7 * s, y - 40 * s, 3 * s, fill(col)); cv.drawCircle(x + 7 * s, y - 40 * s, 3 * s, fill(col))
    cv.drawLine(x, y - 52 * s, x, y - 66 * s, st); cv.drawCircle(x, y - 68 * s, 4 * s, fill(col))
    cv.drawLine(x - 22 * s, y - 8 * s, x - 40 * s, y + 14 * s, st); cv.drawLine(x + 22 * s, y - 8 * s, x + 40 * s, y - 28 * s, st)
    cv.drawLine(x - 10 * s, y + 30 * s, x - 10 * s, y + 52 * s, st); cv.drawLine(x + 10 * s, y + 30 * s, x + 10 * s, y + 52 * s, st)


def _cuarto(cv, rnd):
    cv.drawRect(skia.Rect.MakeWH(BW, 1790), lin((0, 0), (0, 1790), [(120, 176, 170), (92, 146, 142)]))
    _speckle(cv, rnd, 0, 0, BW, 1790)
    # ventana con luz de tarde
    wx, wy = 900, 620
    rrect(cv, wx - 14, wy - 14, 368, 428, 10, fill((240, 236, 226)))
    cv.drawRect(skia.Rect.MakeXYWH(wx, wy, 340, 400), lin((0, wy), (0, wy + 400), [(255, 190, 120), (255, 226, 170)]))
    cv.drawLine(wx + 170, wy, wx + 170, wy + 400, stroke((240, 236, 226), 12)); cv.drawLine(wx, wy + 200, wx + 340, wy + 200, stroke((240, 236, 226), 12))
    # dibujos de robots en la pared
    for (px, py, w, h, rot, pc, ink, sc) in ((150, 620, 250, 320, -4, (250, 248, 240), (40, 70, 140), 2.2), (470, 560, 220, 280, 3, (40, 80, 150), (235, 240, 250), 1.9),
                                           (430, 900, 200, 250, -2, (250, 246, 230), (200, 60, 50), 1.6), (720, 1120, 150, 190, 5, (250, 248, 240), (40, 40, 40), 1.2)):
        cv.save(); cv.translate(px + w / 2, py + h / 2); cv.rotate(rot)
        cv.drawRect(skia.Rect.MakeXYWH(-w / 2 + 6, -h / 2 + 8, w, h), fill((0, 0, 0), 0.2, blur=8))
        cv.drawRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), fill(pc))
        _mini_robot(cv, 0, 10, sc, ink)
        for k in range(3): cv.drawLine(-w / 2 + 16, h / 2 - 20 - k * 12, -w / 2 + 16 + rnd.uniform(40, 90), h / 2 - 20 - k * 12, stroke(ink, 2, 0.6))
        cv.drawRect(skia.Rect.MakeXYWH(-16, -h / 2 - 8, 32, 16), fill((230, 220, 180), 0.9))
        cv.restore()
    # repisa con frascos y herramientas
    cv.drawRect(skia.Rect.MakeXYWH(60, 1090, 330, 18), fill((120, 84, 54)))
    for k in range(5):
        jx = 80 + k * 62; jc = [(200, 220, 230), (230, 200, 150), (190, 230, 200), (230, 190, 200), (210, 210, 230)][k]
        rrect(cv, jx, 1030, 44, 60, 8, fill(jc, 0.85)); cv.drawRect(skia.Rect.MakeXYWH(jx + 4, 1022, 36, 12), fill((150, 150, 156)))
        for j in range(6): cv.drawCircle(jx + 8 + rnd.uniform(0, 28), 1050 + rnd.uniform(0, 34), 4, fill((120, 120, 126)))
    # tablero de herramientas
    rrect(cv, 60, 1180, 330, 250, 8, fill((176, 132, 84)))
    for k in range(4):
        tx = 100 + k * 76
        cv.drawRect(skia.Rect.MakeXYWH(tx - 5, 1220, 10, 110), fill((90, 90, 96))); rrect(cv, tx - 12, 1320, 24, 70, 8, fill([(220, 60, 60), (255, 200, 61), (46, 158, 79), (70, 130, 220)][k]))
    # piso
    cv.drawRect(skia.Rect.MakeXYWH(0, 1790, BW, BH - 1790), lin((0, 1790), (0, BH), [(166, 118, 76), (120, 82, 50)]))
    for y in range(1790, BH, 60): cv.drawLine(0, y, BW, y, stroke((96, 64, 38), 2, 0.6))
    cv.drawPath(path([(wx, 1790), (wx + 340, 1790), (wx + 200, BH), (wx - 300, BH)]), fill((255, 210, 140), 0.14))
    cv.drawRect(skia.Rect.MakeXYWH(0, 1770, BW, 24), fill((240, 236, 226)))


# ------------------------------------------------------------------ patio-taller
def reja_bars(cv, mood="tarde"):
    col = (70, 74, 82) if mood != "noche" else (30, 34, 48)
    for x in range(18, 360, 44): cv.drawRect(skia.Rect.MakeXYWH(x, 1090, 12, 480), fill(col))
    for y in (1110, 1340, 1540): cv.drawRect(skia.Rect.MakeXYWH(0, y, 370, 14), fill(col))
    for x in range(18, 360, 44): cv.drawPath(path([(x - 4, 1092), (x + 16, 1092), (x + 6, 1060)]), fill(col))
    cv.drawRect(skia.Rect.MakeXYWH(360, 1040, 30, 540), fill((150, 110, 90) if mood != "noche" else (50, 50, 80)))


def _patio(cv, rnd, mood="tarde"):
    if mood == "tarde":
        sky(cv, (70, 80, 150), (230, 130, 120), (255, 185, 105), 1150, sun=(520, 1010, 60)); wall = (226, 200, 160); gcol = ((170, 150, 120), (118, 100, 80)); far = (130, 100, 140)
    elif mood == "noche":
        cv.drawRect(skia.Rect.MakeWH(BW, 1200), lin((0, 0), (0, 1200), [(14, 18, 40), (40, 46, 80)])); wall = (70, 74, 110); gcol = ((60, 62, 88), (34, 36, 56)); far = (30, 34, 60)
        for k in range(9):
            cx_, cy_ = rnd.uniform(0, BW), rnd.uniform(200, 800); r = rnd.uniform(140, 260)
            cv.drawOval(skia.Rect.MakeXYWH(cx_ - r, cy_ - r * 0.4, r * 2, r * 0.8), fill((50, 54, 84), 0.8, blur=30))
    else:
        sky(cv, (110, 160, 225), (250, 190, 170), (255, 225, 160), 1150, sun=(240, 1040, 64), sun_col=(255, 230, 170)); wall = (240, 214, 176); gcol = ((190, 170, 136), (136, 118, 92)); far = (160, 150, 190)
    buildings(cv, 1150, rnd, far, (255, 220, 150), h_min=100, h_max=260, win_p=0.2 if mood != "amanecer" else 0.05, alpha=0.8)
    for x in (480, 760): tree(cv, x, 1120, 1.0, rnd, (70, 140, 70) if mood != "noche" else (30, 60, 60))
    # calle visible por la reja
    cv.drawRect(skia.Rect.MakeXYWH(0, 1060, 370, 520), lin((0, 1060), (0, 1580), [tuple(min(255, int(v * 1.05)) for v in far), gcol[0]]))
    # muro del fondo
    cv.drawRect(skia.Rect.MakeXYWH(380, 1050, 620, 520), lin((0, 1050), (0, 1570), [wall, tuple(int(v * 0.82) for v in wall)]))
    for k in range(14):
        x, y = rnd.uniform(390, 980), rnd.uniform(1060, 1560)
        cv.drawOval(skia.Rect.MakeXYWH(x, y, rnd.uniform(30, 90), rnd.uniform(14, 40)), fill((0, 0, 0), 0.05))
    cv.drawRect(skia.Rect.MakeXYWH(380, 1036, 620, 20), fill(tuple(int(v * 0.7) for v in wall)))
    # casa a la derecha con puerta y ventana
    hw = (236, 190, 130) if mood == "tarde" else ((80, 80, 120) if mood == "noche" else (246, 210, 150))
    cv.drawRect(skia.Rect.MakeXYWH(990, 640, 400, 940), lin((990, 0), (1350, 0), [hw, tuple(int(v * 0.85) for v in hw)]))
    cv.drawPath(path([(960, 650), (1380, 650), (1380, 560), (1040, 560)]), fill((150, 70, 50) if mood != "noche" else (60, 40, 60)))
    rrect(cv, 1090, 760, 170, 170, 8, fill((110, 76, 50))); cv.drawRect(skia.Rect.MakeXYWH(1102, 772, 146, 146), fill((255, 214, 140) if mood != "amanecer" else (150, 180, 200)))
    cv.drawLine(1175, 772, 1175, 918, stroke((110, 76, 50), 8)); cv.drawLine(1102, 845, 1248, 845, stroke((110, 76, 50), 8))
    if mood != "amanecer": cv.drawCircle(1175, 845, 190, rad((1175, 845), 190, [(255, 214, 140, 0.3), (255, 214, 140, 0.0)]))
    rrect(cv, 1064, 1070, 212, 510, 8, fill((96, 60, 38)))
    rrect(cv, 1078, 1084, 184, 496, 6, lin((0, 1084), (0, 1580), [(150, 92, 54), (120, 70, 40)]))
    cv.drawCircle(1240, 1340, 10, fill((230, 190, 80)))
    cv.drawRect(skia.Rect.MakeXYWH(1040, 1570, 260, 26), fill((150, 144, 136)))
    # suelo
    cv.drawRect(skia.Rect.MakeXYWH(0, 1570, BW, BH - 1570), lin((0, 1570), (0, BH), list(gcol)))
    for k in range(900):
        x = rnd.uniform(0, BW); y = rnd.uniform(1580, BH); v = rnd.uniform(-1, 1)
        cv.drawCircle(x, y, rnd.uniform(1, 3), fill((255, 255, 255) if v > 0 else (0, 0, 0), 0.07 * abs(v)))
    for k in range(16):
        gx, gy = rnd.uniform(0, BW), rnd.uniform(1600, 2380)
        for j in range(5): cv.drawLine(gx + j * 6, gy, gx + j * 6 + rnd.uniform(-8, 8), gy - rnd.uniform(14, 30), stroke((70, 130, 70) if mood != "noche" else (30, 60, 60), 3))
    # taller: postes y techo de lata
    for px in (400, 930): cv.drawRect(skia.Rect.MakeXYWH(px, 940, 22, 700), lin((px, 0), (px + 22, 0), [(130, 96, 64), (90, 64, 42)]))
    roof = (150, 156, 164) if mood != "noche" else (60, 66, 90)
    cv.drawPath(path([(350, 960), (1000, 900), (1010, 950), (360, 1012)]), fill(roof))
    for k in range(22):
        x0 = 350 + k * 30; y0 = 960 - k * 2.77
        cv.drawLine(x0, y0, x0 + 8, y0 + 50, stroke((0, 0, 0), 4, 0.18)); cv.drawLine(x0 + 12, y0 - 1, x0 + 20, y0 + 49, stroke((255, 255, 255), 3, 0.2))
    for k in range(6): cv.drawOval(skia.Rect.MakeXYWH(rnd.uniform(380, 940), rnd.uniform(920, 970), 50, 22), fill((150, 90, 50), 0.5))
    # banco de trabajo con herramientas
    rrect(cv, 430, 1420, 300, 26, 5, fill((130, 92, 60)))
    for px in (446, 700): cv.drawRect(skia.Rect.MakeXYWH(px, 1444, 16, 150), fill((104, 72, 46)))
    rrect(cv, 450, 1376, 70, 44, 6, fill((200, 60, 50))); cv.drawRect(skia.Rect.MakeXYWH(470, 1366, 30, 12), fill((90, 90, 96)))
    for k in range(3): cv.drawRect(skia.Rect.MakeXYWH(560 + k * 40, 1392, 26, 28), fill([(180, 180, 186), (200, 170, 90), (150, 150, 156)][k]))
    # pila de chatarra a la izquierda del taller
    for k in range(9):
        jx, jy = 410 + rnd.uniform(-10, 120), 1640 - rnd.uniform(0, 70)
        if k % 3 == 0: cv.drawCircle(jx, jy, rnd.uniform(26, 40), stroke((110, 110, 120), 10))
        elif k % 3 == 1: rrect(cv, jx, jy - 30, 44, 60, 6, fill((170, 176, 184)))
        else: rrect(cv, jx - 20, jy - 10, 70, 30, 4, fill((150, 100, 70)))
    reja_bars(cv, mood)
    if mood == "noche":
        for k in range(5): cv.drawOval(skia.Rect.MakeXYWH(rnd.uniform(100, 1100), rnd.uniform(1800, 2300), rnd.uniform(140, 300), rnd.uniform(24, 46)), fill((90, 110, 170), 0.35))
        cv.drawRect(skia.Rect.MakeWH(BW, BH), fill((10, 14, 50), 0.22))
    if mood == "tarde":
        cv.drawRect(skia.Rect.MakeWH(BW, BH), fill((255, 150, 80), 0.06))


def _patio_tarde(cv, rnd): _patio(cv, rnd, "tarde")
def _patio_noche(cv, rnd): _patio(cv, rnd, "noche")
def _patio_amanecer(cv, rnd): _patio(cv, rnd, "amanecer")


# ------------------------------------------------------------------ casa de la abuela (cuarto de costura)
def _casa_abuela(cv, rnd):
    cv.drawRect(skia.Rect.MakeWH(BW, 1790), lin((0, 0), (0, 1790), [(232, 184, 170), (206, 150, 140)]))
    for row, y in enumerate(range(80, 1780, 110)):
        for x in range(40 + (55 if row % 2 else 0), BW, 110):
            cv.drawCircle(x, y, 9, fill((255, 236, 220), 0.35)); cv.drawCircle(x, y, 4, fill((200, 110, 110), 0.4))
    cv.drawRect(skia.Rect.MakeXYWH(0, 1500, BW, 290), fill((176, 120, 100)))
    cv.drawRect(skia.Rect.MakeXYWH(0, 1492, BW, 14), fill((240, 220, 200)))
    # ventana de noche con cortinas
    wx, wy = 560, 640
    rrect(cv, wx - 14, wy - 14, 328, 388, 10, fill((250, 240, 226)))
    cv.drawRect(skia.Rect.MakeXYWH(wx, wy, 300, 360), lin((0, wy), (0, wy + 360), [(60, 60, 120), (150, 110, 150)]))
    cv.drawLine(wx + 150, wy, wx + 150, wy + 360, stroke((250, 240, 226), 10))
    for sx in (wx - 70, wx + 300):
        cv.drawRect(skia.Rect.MakeXYWH(sx, wy - 40, 70, 460), lin((sx, 0), (sx + 70, 0), [(250, 240, 220), (226, 210, 186)]))
    # repisa con carretes de hilo
    cv.drawRect(skia.Rect.MakeXYWH(70, 900, 380, 16), fill((130, 90, 60)))
    for k in range(7):
        hx = 96 + k * 50; hc = [(220, 60, 70), (255, 200, 61), (46, 158, 79), (70, 130, 220), (170, 90, 200), (240, 140, 60), (250, 250, 250)][k]
        rrect(cv, hx - 16, 846, 32, 54, 6, fill(hc)); cv.drawRect(skia.Rect.MakeXYWH(hx - 20, 840, 40, 8), fill((200, 170, 120))); cv.drawRect(skia.Rect.MakeXYWH(hx - 20, 896, 40, 8), fill((200, 170, 120)))
    # maniquí de costura
    cv.drawRect(skia.Rect.MakeXYWH(196, 1380, 10, 400), fill((110, 80, 56)))
    cv.drawPath(path([(150, 1130), (250, 1130), (270, 1250), (240, 1400), (160, 1400), (130, 1250)]), fill((240, 226, 200)))
    cv.drawCircle(200, 1118, 20, fill((110, 80, 56)))
    # lámpara colgante y su luz
    cv.drawLine(430, 0, 430, 560, stroke((60, 50, 44), 5))
    cv.drawPath(path([(350, 640), (510, 640), (470, 560), (390, 560)]), fill((250, 200, 90)))
    cv.drawCircle(430, 660, 26, fill((255, 246, 200)))
    cv.drawPath(path([(350, 640), (510, 640), (900, 1790), (-40, 1790)]), fill((255, 230, 150), 0.16))
    cv.drawCircle(430, 700, 420, rad((430, 700), 420, [(255, 236, 170, 0.35), (255, 236, 170, 0.0)]))
    # telaraña en el rincón de la máquina vieja
    for k in range(6):
        a = math.radians(95 + k * 16)
        cv.drawLine(BW, 520, BW + math.cos(a) * 330, 520 + math.sin(a) * 330, stroke((255, 255, 255), 2, 0.35))
    for r in (110, 190, 270):
        cv.drawArc(skia.Rect.MakeXYWH(BW - r, 520 - r, 2 * r, 2 * r), 95, 82, False, stroke((255, 255, 255), 2, 0.3))
    # piso
    cv.drawRect(skia.Rect.MakeXYWH(0, 1790, BW, BH - 1790), lin((0, 1790), (0, BH), [(150, 100, 66), (104, 66, 40)]))
    for y in range(1790, BH, 60): cv.drawLine(0, y, BW, y, stroke((84, 52, 30), 2, 0.6))
    cv.drawOval(skia.Rect.MakeXYWH(120, 1850, 760, 300), fill((170, 60, 70), 0.55)); cv.drawOval(skia.Rect.MakeXYWH(170, 1880, 660, 240), stroke((250, 220, 190), 8, 0.5))
    cv.drawRect(skia.Rect.MakeXYWH(900, 0, 450, BH), lin((900, 0), (BW, 0), [(40, 20, 40, 0.0), (40, 20, 40, 0.3)]))


# ------------------------------------------------------------------ feria de ciencias
def _feria_ciencias(cv, rnd):
    cv.drawRect(skia.Rect.MakeWH(BW, 1560), lin((0, 0), (0, 1560), [(226, 236, 246), (196, 212, 230)]))
    for x in range(60, BW, 330):
        rrect(cv, x, 300, 240, 300, 10, lin((0, 300), (0, 600), [(255, 255, 255), (190, 220, 250)]))
        cv.drawLine(x + 120, 300, x + 120, 600, stroke((170, 186, 204), 6)); cv.drawLine(x, 450, x + 240, 450, stroke((170, 186, 204), 6))
    # pancarta
    cv.drawRect(skia.Rect.MakeXYWH(150, 720, 1050, 190), fill((0, 0, 0), 0.15, blur=10))
    rrect(cv, 140, 706, 1070, 190, 14, lin((0, 706), (0, 896), [(46, 120, 200), (30, 90, 160)]))
    text_center(cv, "FERIA DE CIENCIAS", BW / 2, 772, 88, (255, 255, 255), None, shadow_=False)
    text_center(cv, "REGIONAL", BW / 2, 852, 54, (255, 200, 61), None, shadow_=False)
    for x in (140, 1210): cv.drawLine(x, 706, x, 560, stroke((90, 90, 96), 5))
    # banderines
    for k in range(18):
        x = 30 + k * 76
        cv.drawPath(path([(x, 960), (x + 60, 960), (x + 30, 1020)]), fill([(230, 80, 70), (255, 200, 61), (46, 158, 79), (70, 130, 220)][k % 4]))
    cv.drawLine(0, 960, BW, 960, stroke((90, 90, 96), 3))
    # mesas del fondo con proyectos relucientes
    for k, tx in enumerate((20, 360, 700, 1040)):
        rrect(cv, tx, 1400, 300, 30, 6, fill((240, 244, 250)))
        cv.drawRect(skia.Rect.MakeXYWH(tx + 8, 1428, 284, 150), lin((0, 1428), (0, 1578), [(60, 110, 190), (40, 80, 150)]))
        cx_ = tx + 150
        if k == 0:   # volcán
            cv.drawPath(path([(cx_ - 100, 1400), (cx_ + 100, 1400), (cx_ + 26, 1280), (cx_ - 26, 1280)]), fill((150, 100, 70)))
            cv.drawPath(path([(cx_ - 26, 1280), (cx_ + 26, 1280), (cx_ + 40, 1330), (cx_ + 4, 1310), (cx_ - 34, 1340)]), fill((240, 90, 40)))
            for j in range(5): cv.drawCircle(cx_ + rnd.uniform(-40, 40), 1250 - j * 16, 8, fill((255, 160, 60), 0.8))
        elif k == 1:  # sistema solar
            cv.drawCircle(cx_, 1300, 36, fill((255, 200, 61)))
            for j, (r, pc) in enumerate(((70, (70, 130, 220)), (104, (220, 90, 70)), (136, (46, 158, 79)))):
                cv.drawOval(skia.Rect.MakeXYWH(cx_ - r, 1300 - r * 0.35, 2 * r, r * 0.7), stroke((120, 130, 150), 3)); cv.drawCircle(cx_ + r * math.cos(j * 2.1), 1300 + r * 0.35 * math.sin(j * 2.1), 14, fill(pc))
        elif k == 2:  # torre con luces
            rrect(cv, cx_ - 60, 1230, 120, 170, 10, fill((200, 206, 216)))
            for j in range(9): cv.drawCircle(cx_ - 36 + (j % 3) * 36, 1262 + (j // 3) * 44, 12, fill([(90, 220, 140), (90, 180, 255), (255, 120, 120)][j % 3]))
        else:         # planta en frasco
            rrect(cv, cx_ - 54, 1280, 108, 120, 16, fill((200, 230, 240), 0.8))
            cv.drawLine(cx_, 1390, cx_, 1250, stroke((46, 140, 70), 7))
            for j in range(4): cv.drawOval(skia.Rect.MakeXYWH(cx_ + (-50 if j % 2 else 6), 1262 + j * 22, 44, 20), fill((70, 170, 90)))
        cv.drawLine(cx_ - 120, 1396, cx_ + 120, 1396, stroke((255, 255, 255), 4, 0.8))
    # piso brillante
    cv.drawRect(skia.Rect.MakeXYWH(0, 1570, BW, BH - 1570), lin((0, 1570), (0, BH), [(214, 220, 230), (160, 170, 186)]))
    for x in range(-200, BW + 200, 150): cv.drawLine(x + 100, 1570, x - 160, BH, stroke((255, 255, 255), 3, 0.35))
    for y in (1700, 1900, 2150): cv.drawLine(0, y, BW, y, stroke((255, 255, 255), 3, 0.3))
    cv.drawRect(skia.Rect.MakeXYWH(0, 1570, BW, 240), lin((0, 1570), (0, 1810), [(255, 255, 255, 0.4), (255, 255, 255, 0.0)]))


# ------------------------------------------------------------------ escenario del premio
def _escenario(cv, rnd):
    cv.drawRect(skia.Rect.MakeWH(BW, 1700), lin((0, 0), (0, 1700), [(24, 30, 70), (50, 60, 120)]))
    for k in range(60): cv.drawCircle(rnd.uniform(200, 1150), rnd.uniform(500, 1500), rnd.uniform(2, 5), fill((255, 240, 200), rnd.uniform(0.2, 0.7)))
    rrect(cv, 150, 420, 1050, 250, 16, lin((0, 420), (0, 670), [(255, 210, 80), (236, 160, 40)]))
    rrect(cv, 166, 436, 1018, 218, 12, stroke((255, 244, 200), 6))
    text_center(cv, "PREMIO A LA", BW / 2, 496, 76, (60, 30, 20), None, shadow_=False)
    text_center(cv, "CREATIVIDAD", BW / 2, 592, 100, (160, 30, 30), None, shadow_=False)
    # focos
    for fx_ in (330, 1020):
        cv.drawPath(path([(fx_ - 30, 0), (fx_ + 30, 0), (BW / 2 + 330, 1750), (BW / 2 - 330, 1750)]), fill((255, 244, 200), 0.1))
    # piso de madera del escenario
    cv.drawRect(skia.Rect.MakeXYWH(0, 1700, BW, 330), lin((0, 1700), (0, 2030), [(190, 130, 76), (150, 96, 54)]))
    for x in range(0, BW, 90): cv.drawLine(x, 1700, x - 60, 2030, stroke((110, 70, 40), 3, 0.5))
    cv.drawOval(skia.Rect.MakeXYWH(BW / 2 - 380, 1800, 760, 170), fill((255, 244, 200), 0.22))
    cv.drawRect(skia.Rect.MakeXYWH(0, 2030, BW, 370), lin((0, 2030), (0, BH), [(60, 20, 30), (20, 8, 14)]))
    # telón
    for side in (0, 1):
        x0 = 0 if side == 0 else BW - 230
        cv.drawRect(skia.Rect.MakeXYWH(x0, 0, 230, 2030), lin((x0, 0), (x0 + 230, 0), [(170, 30, 40), (110, 16, 26), (170, 30, 40), (110, 16, 26)]))
    cv.drawRect(skia.Rect.MakeXYWH(0, 0, BW, 300), fill((150, 24, 34)))
    for k in range(9): cv.drawCircle(75 + k * 150, 300, 80, fill((150, 24, 34)))
    cv.drawRect(skia.Rect.MakeXYWH(0, 290, BW, 14), fill((255, 200, 61), 0.8))


E.BUILD.update({"feria": _feria, "cuarto_camila": _cuarto, "patio_tarde": _patio_tarde, "patio_noche": _patio_noche,
                "patio_amanecer": _patio_amanecer, "casa_abuela": _casa_abuela, "feria_ciencias": _feria_ciencias, "escenario": _escenario})
