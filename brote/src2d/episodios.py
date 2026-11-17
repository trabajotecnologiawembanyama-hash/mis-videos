"""Los 5 episodios de la semana de Pedrito (Brote) en animación 2D. Uso: python3 episodios.py <ep01..ep05> <salida.mp4> [preview_seg...]"""
import json, math, os, random, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import skia
from motor import *
import motor as Mo
import escenarios as E
from escenarios import Cam, cam_move, draw_bg, BW, BH, rim_and_net, particles, vignette, paper

EP = sys.argv[1]
DUR = 55.0
VOZ = f"/tmp/claude-0/brote/k_{EP}"
WORDS = json.load(open(f"{VOZ}/palabras.json"))["words"]
AMARILLO = (255, 200, 61)
RIM = (1010, 1080)


def at(seq, nth=0):
    toks = [x.strip(",.«»¿?¡!:…") for x in seq.lower().split()]; hits = []
    for i in range(len(WORDS) - len(toks) + 1):
        if all(WORDS[i + k]["w"].strip(",.«»¿?¡!:…").lower() == toks[k] for k in range(len(toks))):
            hits.append(WORDS[i]["t0"])
    return hits[nth] - 0.1


def end_of(seq, nth=0):
    toks = [x.strip(",.«»¿?¡!:…") for x in seq.lower().split()]; hits = []
    for i in range(len(WORDS) - len(toks) + 1):
        if all(WORDS[i + k]["w"].strip(",.«»¿?¡!:…").lower() == toks[k] for k in range(len(toks))):
            hits.append(WORDS[i + len(toks) - 1]["t1"])
    return hits[nth]


def persp(y):
    return 0.62 + 0.5 * clamp((y - 1550) / 700, -0.3, 1.2)


def ch(cv, spec, p, x, y, S=520, face=1, T=0.0, ex=None, seed=1, persp_on=True):
    p = dict(p)
    p["blink"] = max(p.get("blink", 0), blink_at(T, seed))
    k = persp(y) * 1.4 if persp_on else 1.0
    return draw_char(cv, spec, p, x, y, S * k, face, T, ex)


def shade(cv, x, y, S=520, persp_on=True):
    k = persp(y) * 1.4 if persp_on else 1.0
    Mo.shadow(cv, x, y, 0.32 * S * k)


def silhouette_begin(cv):
    cv.saveLayer(None, None)


def silhouette_end(cv, col=(26, 22, 36), a=0.92):
    p = skia.Paint(Color=C(col, a)); p.setBlendMode(skia.BlendMode.kSrcATop); cv.drawPaint(p); cv.restore()


def dribble(hand, ground, phase, r):
    u = abs(math.cos(math.pi * phase))
    return (hand[0], lerp(ground - r, hand[1] + r * 0.6, u))


def arc(p0, p1, h, u):
    return (lerp(p0[0], p1[0], u), lerp(p0[1], p1[1], u) - 4 * h * u * (1 - u))


def walker(T, t0, x0, x1, dur, speed=1.6):
    u = clamp((T - t0) / dur); x = lerp(x0, x1, u)
    moving = 0 < (T - t0) < dur
    return x, (T - t0) * speed, moving


def court(cv, cam, name="cancha_tarde", T=0.0, swish=0.0):
    cv.save(); cam.apply(cv); draw_bg(cv, name)
    return cv


def done(cv): cv.restore()


# ===================================================================== EPISODIO 1
def ep01():
    S = []
    # 1. gancho: plano cenital-alto de la cancha, Pedrito cruza botando una pelota
    def s1(cv, lt, d, T):
        cam = cam_move(lt, d, (600, 1750, 1.35), (640, 1800, 1.6)); court(cv, cam)
        x, ph, mv = walker(lt, 0, 250, 700, d + 0.5, 1.5)
        y = 1950; shade(cv, x, y)
        info = ch(cv, PEDRITO, dict(walk(ph), af=(30 + 25 * math.cos(2 * math.pi * ph * 2), 40), mood="neutral"), x, y, T=T)
        b = dribble(info["hand_f"], y, ph * 2, 36 * persp(y)); ball(cv, b[0] + 18, b[1], 36 * persp(y), ph * 3)
        rim_and_net(cv, *RIM); done(cv)
    S.append((0.0, s1))

    # 2. primer plano de las zapatillas rotas con cinta; la suela aletea al caminar
    def s2(cv, lt, d, T):
        cam = cam_move(lt, d, (640, 2030, 3.4), (660, 2040, 3.6)); court(cv, cam)
        ph = lt * 0.7
        info = ch(cv, PEDRITO, walk(ph, amp=0.7), 640 - lt * 25, 2160, S=2300, T=T, ex=dict(sole_flap=-12 - 14 * abs(math.sin(ph * 6.28))), persp_on=False)
        done(cv)
    S.append((at("y un par"), s2))

    # 3. cada tarde cruzaba la cancha gris con una pelota casi sin aire
    def s3(cv, lt, d, T):
        cam = cam_move(lt, d, (520, 1650, 1.25), (700, 1680, 1.35)); court(cv, cam)
        x, ph, mv = walker(lt, 0, 220, 820, d, 1.3)
        y = 1880; shade(cv, x, y)
        info = ch(cv, PEDRITO, dict(walk(ph, amp=0.85), af=(28 + 20 * math.cos(2 * math.pi * ph * 2), 45), mood="neutral"), x, y, T=T)
        r = 36 * persp(y); ph2 = (ph * 2) % 1
        b = dribble(info["hand_f"], y, ph2, r)
        squash = 0.75 if abs(b[1] - (y - r)) < 4 else 1.0          # pelota desinflada
        cv.save(); cv.translate(b[0] + 16, b[1] + r * (1 - squash)); cv.scale(1 + (1 - squash) * 0.6, squash); ball(cv, 0, 0, r, ph); cv.restore()
        rim_and_net(cv, *RIM); done(cv)
    S.append((at("cada"), s3))

    # 4. quería ser la estrella: mira el aro, chispas de sueño
    def s4(cv, lt, d, T):
        cam = cam_move(lt, d, (760, 1500, 1.7), (800, 1380, 2.0)); court(cv, cam)
        y = 1820; shade(cv, 760, y)
        p = breathe(dict(HOLD, head=-14, look=(0.6, -0.8), mood="happy"), T)
        info = ch(cv, PEDRITO, p, 760, y, T=T, ex=dict(blush=True))
        ball(cv, info["hand_f"][0] + 22, info["hand_f"][1] - 8, 36 * persp(y))
        particles(cv, T, 26, 4, (255, 230, 140), (700, 900, 450, 600), 40, (2, 6), 0.9)
        rim_and_net(cv, *RIM); done(cv)
    S.append((at("quería"), s4))

    # 5. en su casa el dinero alcanzaba justo: mamá cuenta monedas, Pedrito mira por la ventana
    def table(cv, coins_moved):
        rrect(cv, 140, 1560, 560, 30, 8, fill((120, 72, 40)))
        for x in (170, 640): cv.drawRect(skia.Rect.MakeXYWH(x, 1585, 26, 180), fill((100, 60, 34)))
        cv.drawOval(skia.Rect.MakeXYWH(560, 1520, 110, 50), fill((210, 150, 80)))       # pan
        rnd = random.Random(2)
        for k in range(8):
            mx = 300 + k * 26 if k < coins_moved else 240 + rnd.uniform(-30, 30)
            cv.drawOval(skia.Rect.MakeXYWH(mx, 1545 - (k % 3) * 3, 30, 12), fill((225, 175, 70) if k % 3 else (205, 205, 210)))

    def s5(cv, lt, d, T):
        cam = cam_move(lt, d, (680, 1500, 1.15), (620, 1520, 1.3)); cv.save(); cam.apply(cv); draw_bg(cv, "casa")
        n = int(lt * 3) % 9
        ph = (lt * 3) % 1
        rrect(cv, 330, 1640, 120, 20, 6, fill((110, 66, 36)))      # silla
        ch(cv, MAMA, dict(SIT_BENCH, af=(70 + 15 * math.sin(ph * 6.28), 40), ab=(60, 50), head=14, look=(0.5, 0.8), mood="worried"),
           390, 1770, S=520, face=1, T=T, seed=3, persp_on=False)
        table(cv, n)
        ch(cv, PEDRITO, dict(STAND, head=-6, look=(0.9, -0.3), mood="sad"), 1000, 1790, S=520, face=-1 if lt < d * 0.5 else 1, T=T, seed=5, persp_on=False)
        done(cv)
    S.append((at("pero"), s5))

    # 6. unas zapatillas nuevas costaban un mes de alquiler: primer plano de las monedas contadas
    def s6(cv, lt, d, T):
        cam = cam_move(lt, d, (420, 1540, 3.0), (440, 1545, 3.3)); cv.save(); cam.apply(cv); draw_bg(cv, "casa")
        table(cv, min(8, int(lt * 2.5)))
        # mano de mamá empujando monedas
        hx = 300 + (lt * 2.5 % 1) * 70
        cv.drawLine(hx - 60, 1440, hx, 1535, stroke(BLACK, 9)); cv.drawCircle(hx, 1535, 12, fill(BLACK))
        # volante de zapatillas con precio alto
        paper(cv, 560, 1490, 130, 90, -8, (255, 255, 255))
        text_center(cv, "$$$", 560, 1470, 34, (200, 40, 30), None, shadow_=False)
        done(cv)
    S.append((at("unas"), s6))

    # 7. pegaba las suyas con cinta, una y otra vez
    def s7(cv, lt, d, T):
        cam = cam_move(lt, d, (640, 1900, 2.3), (660, 1960, 2.7)); court(cv, cam)
        ph = (lt * 1.6) % 1
        p = dict(SIT_GROUND, mood="focused", head=24, look=(0.6, 0.9), af=(70 + 25 * math.sin(ph * 6.28), 30 + 30 * math.cos(ph * 6.28)), ab=(60, 40))
        info = ch(cv, PEDRITO, p, 600, 2080, S=700, T=T, persp_on=False)
        f = info["foot_f"]
        cv.drawCircle(f[0] + 90, f[1] - 6, 34, stroke((176, 178, 182), 16))         # rollo de cinta
        cv.drawLine(f[0] + 60, f[1] - 18, info["hand_f"][0], info["hand_f"][1], stroke((200, 202, 206), 8, 0.9))
        done(cv)
    S.append((at("así que"), s7))

    # 8. el colegio anunció las pruebas: niños llegan al cartel
    def s8(cv, lt, d, T):
        cam = cam_move(lt, d, (675, 1420, 1.15), (675, 1300, 1.45)); cv.save(); cam.apply(cv); draw_bg(cv, "colegio_pruebas")
        for k, (x0, x1, y) in enumerate(((-100, 330, 2060), (1450, 980, 2040), (-200, 520, 2140), (1500, 800, 2120))):
            x, ph, mv = walker(lt, k * 0.35, x0, x1, 2.2, 1.6)
            p = walk(ph) if mv else breathe(dict(STAND, head=-10, look=(0.3, -0.6), mood="happy"), T + k)
            shade(cv, x, y); ch(cv, KIDS[k], p, x, y, S=560, face=1 if x1 > x0 else -1, T=T, seed=10 + k)
        done(cv)
    S.append((at("esa tarde"), s8))

    # 9. todos llegarían con zapatillas brillantes: pies de los niños, brillos
    def s9(cv, lt, d, T):
        cam = cam_move(lt, d, (675, 2000, 2.6), (700, 2010, 2.8)); cv.save(); cam.apply(cv); draw_bg(cv, "colegio_pruebas")
        for k in range(3):
            x, ph, mv = walker(lt, k * 0.25, -200 + k * 120, 360 + k * 300, 2.0, 1.6)
            ch(cv, KIDS[k], walk(ph) if mv else STAND, x, 2170, S=1500, T=T, seed=20 + k, persp_on=False)
        for k in range(10):   # destellos
            sx = 300 + (k * 97) % 800; sy = 2120 + (k * 53) % 60; a = max(0, math.sin(T * 6 + k))
            cv.drawLine(sx - 16 * a, sy, sx + 16 * a, sy, stroke((255, 255, 255), 4, a)); cv.drawLine(sx, sy - 16 * a, sx, sy + 16 * a, stroke((255, 255, 255), 4, a))
        done(cv)
    S.append((at("todos"), s9))

    # 10. miró sus pies, respiró hondo, apretó la pelota; «tendré que tener algo más»
    def s10(cv, lt, d, T):
        q = at("si no") - at("pedrito miró")
        if lt < q: cam = cam_move(lt, q, (680, 1600, 1.5), (680, 1560, 1.7))
        else: cam = cam_move(lt - q, d - q, (700, 1420, 2.6), (700, 1400, 2.8))
        court(cv, cam)
        y = 1850; shade(cv, 680, y)
        if lt < 1.4: p = dict(HOLD, head=26, look=(0.4, 1.0), mood="worried")
        elif lt < q: p = breathe(dict(HOLD, head=-4, look=(0.6, 0), mood="focused", lean=-3 + 4 * math.sin(lt * 3)), T)
        else: p = dict(HOLD, head=-2, look=(0.8, -0.1), mood="determined", ab=(25, 95), af=(18, 100))
        info = ch(cv, PEDRITO, p, 680, y, T=T)
        ball(cv, info["hand_f"][0] + 16, info["hand_f"][1] - 6, 36 * persp(y) * (0.93 if lt > q else 1.0))
        rim_and_net(cv, *RIM); done(cv)
    S.append((at("pedrito miró"), s10))

    # 11. lanzó una vez más al aro oxidado (animación de tiro completa)
    def s11(cv, lt, d, T):
        cam = cam_move(lt, d, (760, 1450, 1.3), (860, 1250, 1.45)); court(cv, cam)
        x, y = 640, 1880; shade(cv, x, y)
        p = keys(lt, [(0.0, HOLD), (0.45, CROUCH), (0.75, dict(SHOOT_UP, air=0.12)), (1.1, dict(SHOOT_UP, air=0.0)), (2.0, dict(STAND, mood="happy", head=-12, look=(0.7, -0.7)))])
        info = ch(cv, PEDRITO, p, x, y, T=T)
        r = 36 * persp(y); rel = 0.75; fl = 1.25
        if lt < rel: b = (info["hand_f"][0] + 12, info["hand_f"][1] - 10)
        elif lt < rel + fl: b = arc((info["hand_f"][0], info["hand_f"][1] - 20), (RIM[0], RIM[1] - 20), 300, (lt - rel) / fl)
        else:
            u = min(1, (lt - rel - fl) / 0.5); b = (RIM[0] + 8 * math.sin(lt * 30) * (1 - u), lerp(RIM[1] - 20, y - r, ease(u)))
        ball(cv, b[0], b[1], r * (0.85 if rel < lt < rel + fl + 0.4 else 1), lt * 9)
        sw = clamp(1 - abs(lt - rel - fl - 0.15) / 0.5)
        rim_and_net(cv, *RIM, swish=sw, t=T); done(cv)
    S.append((at("lanzó"), s11))

    # 12. y no sabía que, desde la reja, alguien llevaba semanas mirándolo (Don Lucho de espaldas, en silueta)
    def s12(cv, lt, d, T):
        cam = cam_move(lt, d, (700, 1600, 1.15), (560, 1650, 1.45)); court(cv, cam)
        # al fondo, Pedrito sigue lanzando
        ph = (lt % 2.4) / 2.4
        p = keys(ph * 2.4, [(0, HOLD), (0.5, CROUCH), (0.8, SHOOT_UP), (1.6, HOLD)])
        info = ch(cv, PEDRITO, p, 820, 1700, S=420, T=T)
        if 0.8 < ph * 2.4 < 1.9:
            b = arc(info["hand_f"], (RIM[0], RIM[1] - 10), 160, (ph * 2.4 - 0.8) / 1.1); ball(cv, b[0], b[1], 18, T * 8)
        rim_and_net(cv, *RIM)
        # reja en primer plano
        E.fence(cv, 1180, 2400, (120, 125, 130), 0.85)
        silhouette_begin(cv)
        ch(cv, LUCHO, dict(STAND, ab=(10, 80), af=(20, 70), head=-4), 330, 2330, S=1050, face=1, T=T, seed=40, persp_on=False,
           ex=dict(hand_item=lambda c, h: broom(c, h, 6, 640)))
        silhouette_end(cv)
        done(cv)
    S.append((at("y no sabía"), s12))
    texts = [("SUEÑO ENORME", 0.35, at("y un par")), ("ZAPATILLAS ROTAS", at("y un par"), at("cada") - 0.1),
             ("PRUEBAS EL VIERNES", at("las pruebas"), at("todos") - 0.1)]
    return S, texts


# ===================================================================== EPISODIO 2
def gym_kids(cv, T, lt, xs=(200, 380, 560, 740, 920), y=1900, S=520, laugh=False, seed0=50):
    for k, x in enumerate(xs):
        if laugh:
            p = dict(STAND, lean=-6 + 6 * math.sin(T * 14 + k), ab=(60, 70), af=(55, 75), head=-10, mood="happy")
        else:
            ph = (T * 1.2 + k * 0.3) % 1
            p = dict(STAND, ab=(90 + 60 * math.sin(ph * 6.28), 0), af=(90 - 60 * math.sin(ph * 6.28), 0), mood="happy") if k % 2 else run(ph * 0.5, 0.35)
        shade(cv, x, y); ch(cv, KIDS[k % 5], p, x, y, S=S, face=1 if k % 2 else -1, T=T, seed=seed0 + k)


def ep02():
    S = []
    def s1(cv, lt, d, T):
        cam = cam_move(lt, d, (675, 1500, 1.0), (760, 1560, 1.25)); cv.save(); cam.apply(cv); draw_bg(cv, "gimnasio")
        gym_kids(cv, T, lt, xs=(180, 340, 500, 660, 820), y=1880)
        shade(cv, 1060, 1880)
        ch(cv, PEDRITO, breathe(dict(STAND, mood="worried", look=(-0.6, 0), head=4), T), 1060, 1880, S=520, face=-1, T=T)
        rim_and_net(cv, *RIM, rusty=False); done(cv)
    S.append((0.0, s1))

    def s2(cv, lt, d, T):   # los otros niños reían y calentaban con zapatillas nuevas
        cam = cam_move(lt, d, (600, 1650, 1.7), (680, 1660, 1.85)); cv.save(); cam.apply(cv); draw_bg(cv, "gimnasio")
        gym_kids(cv, T, lt, xs=(380, 620, 860), y=1940, S=560, laugh=(int(T) % 2 == 0))
        done(cv)
    S.append((at("los otros"), s2))

    def s3(cv, lt, d, T):   # en la fila, la cinta bien apretada (pies + manos tirando la cinta)
        cam = cam_move(lt, d, (640, 2030, 3.0), (650, 2040, 3.3)); cv.save(); cam.apply(cv); draw_bg(cv, "gimnasio")
        p = dict(STAND, lb=(4, 0), lf=(-4, 0))
        info = ch(cv, PEDRITO, p, 640, 2160, S=2200, T=T, persp_on=False)
        pull = 6 * math.sin(lt * 8)
        for f in (info["foot_f"],):
            cv.drawLine(f[0] - 40, f[1] - 50, f[0] - 90, f[1] - 260 + pull, stroke((190, 192, 196), 10))
        done(cv)
    S.append((at("pedrito se paró"), s3))

    def s4(cv, lt, d, T):   # el entrenador tocó el silbato
        cam = cam_move(lt, d, (760, 1400, 1.9), (780, 1350, 2.2)); cv.save(); cam.apply(cv); draw_bg(cv, "gimnasio")
        blow = at("silbato") - at("el entrenador")
        p = keys(lt, [(0, dict(STAND, mood="focused")), (max(0.2, blow - 0.3), WHISTLE), (d, WHISTLE)])
        ch(cv, COACH, dict(p, mood="focused"), 760, 1880, S=560, face=-1, T=T, seed=60)
        if lt > blow:
            for k in range(3):
                a = clamp(1 - (lt - blow) / 0.8)
                cv.drawArc(skia.Rect.MakeXYWH(560 - k * 30, 1390 - k * 30, 80 + k * 60, 80 + k * 60), 140, 80, False, stroke((255, 255, 255), 6, a))
        done(cv)
    S.append((at("el entrenador"), s4))

    def s5(cv, lt, d, T):   # robó un balón, esquivó a dos y corrió
        cam = cam_move(lt, d, (450, 1650, 1.25), (800, 1600, 1.3)); cv.save(); cam.apply(cv); draw_bg(cv, "gimnasio")
        x, ph, mv = walker(lt, 0, 150, 900, d, 2.4)
        for k, dx in enumerate((420, 700)):
            dodge = clamp((x - dx + 120) / 160)
            shade(cv, dx, 1880)
            ch(cv, KIDS[k], dict(STAND, ab=(110, -20), af=(100, -10), lean=-8 * dodge, mood="surprised"), dx, 1880 - 40 * math.sin(dodge * math.pi), S=520, face=-1, T=T, seed=70 + k)
        shade(cv, x, 1900)
        info = ch(cv, PEDRITO, dict(run(ph), af=(35, 40)), x, 1900 - 30 * math.sin(clamp((x - 330) / 160) * math.pi) - 30 * math.sin(clamp((x - 610) / 160) * math.pi), T=T)
        b = dribble(info["hand_f"], 1900, ph * 2, 36 * persp(1900)); ball(cv, b[0] + 20, b[1], 36 * persp(1900), ph * 4)
        rim_and_net(cv, *RIM, rusty=False); done(cv)
    S.append((at("pedrito robó"), s5))

    def s6(cv, lt, d, T):   # saltó hacia el aro
        cam = cam_move(lt, d, (850, 1450, 1.4), (900, 1300, 1.6)); cv.save(); cam.apply(cv); draw_bg(cv, "gimnasio")
        u = clamp(lt / d)
        x = lerp(760, 900, u); air = 0.5 * math.sin(math.pi * clamp(lt / (d * 0.95)))
        p = dict(SHOOT_UP, air=air, lb=(30, -60), lf=(-10, -20))
        shade(cv, x, 1880)
        info = ch(cv, PEDRITO, p, x, 1880, T=T)
        ball(cv, info["hand_f"][0], info["hand_f"][1] - 20, 36 * persp(1880), T * 5)
        rim_and_net(cv, *RIM, rusty=False); done(cv)
    S.append((at("saltó"), s6))

    def s7(cv, lt, d, T):   # la suela se soltó y rodó por el piso (cámara lenta)
        cam = cam_move(lt, d, (640, 1950, 2.6), (700, 1980, 2.9)); cv.save(); cam.apply(cv); draw_bg(cv, "gimnasio")
        info = ch(cv, PEDRITO, dict(SHOOT_UP, air=0.25 - lt * 0.02, lb=(30, -60), lf=(-10, -20), mood="surprised"), 560, 2160, S=1500, T=T, persp_on=False)
        f = info["foot_f"]; u = clamp(lt / d)
        sx = f[0] + 80 + u * 520; sy = f[1] + 40 + 300 * (u ** 0.6) - 180 * math.sin(math.pi * u)
        cv.save(); cv.translate(sx, sy); cv.rotate(u * 540)
        rrect(cv, -90, -14, 180, 28, 10, fill((190, 185, 175))); cv.restore()
        done(cv)
    S.append((at("en ese instante"), s7))

    def s8(cv, lt, d, T):   # cayó, el balón rebotó lejos
        cam = Cam(700, 1650, 1.4, shake=max(0, 14 * (1 - lt / 0.5)), t=T); cv.save(); cam.apply(cv); draw_bg(cv, "gimnasio")
        p = keys(lt, [(0, dict(SHOOT_UP, air=0.25)), (0.35, FALL_POSE), (d, dict(FALL_POSE, head=26, mood="sad"))])
        shade(cv, 640, 1900); ch(cv, PEDRITO, p, 640, 1900, T=T)
        bx = 700 + lt * 260; by = 1900 - 26 - abs(math.sin(lt * 4.2)) * 260 * math.exp(-lt * 0.9)
        ball(cv, bx, by, 36 * persp(1900), lt * 8)
        done(cv)
    S.append((at("pedrito cayó"), s8))

    def s9(cv, lt, d, T):   # el gimnasio estalló en risas
        cam = cam_move(lt, d, (675, 1600, 1.3), (675, 1600, 1.4)); cv.save(); cam.apply(cv); draw_bg(cv, "gimnasio")
        gym_kids(cv, T, lt, xs=(200, 420, 920, 1140), y=1840, laugh=True)
        shade(cv, 660, 1980)
        info = ch(cv, PEDRITO, dict(SIT_GROUND, mood="sad", tears=1, head=20), 660, 1980, T=T)
        done(cv)
    S.append((at("y el gimnasio"), s9))

    def s10(cv, lt, d, T):  # «puedes ir a sentarte»
        cam = cam_move(lt, d, (720, 1420, 1.9), (700, 1400, 2.05)); cv.save(); cam.apply(cv); draw_bg(cv, "gimnasio")
        p = keys(lt, [(0, STAND), (0.5, dict(POINT, mood="neutral")), (d, dict(POINT, mood="neutral"))])
        ch(cv, COACH, p, 640, 1880, S=560, face=1, T=T, seed=60)
        done(cv)
    S.append((at("puedes"), s10))

    def s11(cv, lt, d, T):  # recogió su suela, la guardó en el bolsillo y salió sin mirar a nadie
        cam = cam_move(lt, d, (640, 1500, 1.9), (520, 1560, 1.6)); cv.save(); cam.apply(cv); draw_bg(cv, "gimnasio")
        g1 = at("la guardó") - at("pedrito recogió"); g2 = at("y salió") - at("pedrito recogió")
        if lt < g2:
            p = keys(lt, [(0, dict(CROUCH, mood="sad", tears=1, head=24)), (g1, dict(HOLD, mood="sad", tears=1, head=20)), (g2, dict(SAD_STAND, tears=1))])
            info = ch(cv, PEDRITO, p, 700, 1880, T=T)
            if lt < g1 + 0.4: cv.save(); cv.translate(info["hand_f"][0], info["hand_f"][1]); rrect(cv, -40, -10, 80, 20, 8, fill((190, 185, 175))); cv.restore()
        else:
            x, ph, mv = walker(lt, g2, 700, 120, d - g2 + 0.3, 1.2)
            ch(cv, PEDRITO, walk(ph, base=dict(SAD_STAND, tears=1)), x, 1880, face=-1, T=T)
        done(cv)
    S.append((at("pedrito recogió"), s11))

    def s12(cv, lt, d, T):  # se sentó solo en la cancha gris
        cam = cam_move(lt, d, (640, 1650, 1.2), (640, 1700, 1.45)); court(cv, cam)
        shade(cv, 640, 1900); ch(cv, PEDRITO, breathe(SIT_GROUND, T), 640, 1900, T=T)
        rim_and_net(cv, *RIM); done(cv)
    S.append((at("se sentó"), s12))

    def s13(cv, lt, d, T):  # una sombra le tapó el sol
        cam = cam_move(lt, d, (640, 1700, 1.45), (640, 1760, 1.9)); court(cv, cam)
        shade(cv, 640, 1900)
        look = lt > at("una sombra") - at("y entonces")
        ch(cv, PEDRITO, dict(SIT_GROUND, head=-10 if look else 12, look=(-0.8, -0.6) if look else (0.3, 0.6), mood="surprised" if look else "sad"), 640, 1900, T=T)
        u = ease(clamp((lt - 0.4) / 2.0))
        sh = skia.Path(); x0 = lerp(-900, 260, u)
        sh.addOval(skia.Rect.MakeXYWH(x0, 1830, 900, 150))
        sh.addRect(skia.Rect.MakeXYWH(x0 + 820, 1500, 60, 380))   # escoba
        cv.save(); cv.clipRect(skia.Rect.MakeXYWH(-400, 1550, 2400, 1000)); cv.drawPath(sh, fill((10, 10, 30), 0.55, blur=12)); cv.restore()
        cv.drawRect(skia.Rect.MakeXYWH(0, 0, BW, BH), fill((20, 20, 60), 0.25 * u))
        done(cv)
    S.append((at("y entonces"), s13))
    texts = [("SE ROMPIÓ", at("la suela"), at("pedrito cayó") - 0.1), ("TODOS RÍEN", at("estalló"), at("puedes") - 0.1),
             ("¿FIN DEL SUEÑO?", at("se sentó"), at("y entonces") - 0.1)]
    return S, texts


EPISODES = {"ep01": ep01, "ep02": ep02}
if os.path.exists(os.path.join(os.path.dirname(__file__), "episodios_b.py")):
    from episodios_b import ep03, ep04, ep05
    EPISODES.update(ep03=ep03, ep04=ep04, ep05=ep05)
if os.path.exists(os.path.join(os.path.dirname(__file__), "episodios_c.py")):
    from episodios_c import ep06, ep07, ep08, ep09, ep10
    EPISODES.update(ep06=ep06, ep07=ep07, ep08=ep08, ep09=ep09, ep10=ep10)


# ===================================================================== render
def subtitle(cv, T):
    for k, w in enumerate(WORDS):
        nxt = WORDS[k + 1]["t0"] if k + 1 < len(WORDS) else 99
        end = nxt if nxt - w["t1"] < 0.35 else w["t1"] + 0.18
        if w["t0"] <= T < end:
            s = 0.86 + 0.14 * ease((T - w["t0"]) / 0.08)
            text_center(cv, w["w"].replace("«", "").replace("»", "").upper(), W / 2, 1450, 104, (255, 255, 255), (0, 0, 0), 0.085, scale=s)
            return


def key_texts(cv, T, texts):
    for s, t0, t1 in texts:
        if t0 <= T < t1:
            a = min(1, (T - t0) / 0.15) * min(1, (t1 - T) / 0.15)
            f = skia.Font(typeface("Inter-Black"), 80); fit = min(1.0, 980 / max(1, f.measureText(s)))
            text_center(cv, s, W / 2, 250, 80 * fit, AMARILLO, (17, 17, 17), 0.09, a=a, scale=0.92 + 0.08 * ease((T - t0) / 0.2))


def render(out, only=None):
    shots, texts = EPISODES[EP]()
    starts = [s for s, _ in shots] + [DUR]
    wr = Mo.Writer(out)
    frames = range(int(DUR * FPS)) if not only else [int(t * FPS) for t in only]
    for f in frames:
        T = f / FPS
        cv = wr.canvas(); cv.clear(C((0, 0, 0)))
        for i, (t0, fn) in enumerate(shots):
            if t0 <= T < starts[i + 1]:
                cv.save(); fn(cv, T - t0, starts[i + 1] - t0, T); cv.restore(); break
        vignette(cv, 0.35)
        key_texts(cv, T, texts)
        subtitle(cv, T)
        if T < 0.2: cv.drawRect(skia.Rect.MakeWH(W, H), fill((0, 0, 0), 1 - T / 0.2))
        if T > DUR - 0.5: cv.drawRect(skia.Rect.MakeWH(W, H), fill((0, 0, 0), (T - (DUR - 0.5)) / 0.5))
        if only:
            wr.surf.makeImageSnapshot().save(f"{out}_{T:05.2f}.png")
        else:
            wr.push()
        if f % 300 == 0: print(EP, "frame", f, flush=True)
    wr.close()


if __name__ == "__main__":
    out = sys.argv[2]
    only = [float(x) for x in sys.argv[3:]] or None
    render(out, only)
