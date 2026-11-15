"""Episodios 3, 4 y 5 de la semana de Pedrito (usa los ayudantes de episodios.py)."""
import math, random, sys
import skia
from motor import *
import motor as Mo
import escenarios as E
from escenarios import Cam, cam_move, draw_bg, BW, BH, rim_and_net, particles, paper

H_ = sys.modules["__main__"]
RIM = (1010, 1080)


def A(s, n=0): return H_.at(s, n)


def court(cv, cam, name):
    cv.save(); cam.apply(cv); draw_bg(cv, name)


def done(cv): cv.restore()


def ch(*a, **k): return H_.ch(*a, **k)
def shade(*a, **k): return H_.shade(*a, **k)


def lucho_broom(ang=8, L=560):
    return dict(hand_item=lambda c, h: broom(c, h, ang, L))


def bench(cv, x, y, w=420):
    rrect(cv, x - w / 2, y - 120, w, 26, 6, fill((150, 96, 52)))
    for dx in (-w / 2 + 30, w / 2 - 50): cv.drawRect(skia.Rect.MakeXYWH(x + dx, y - 100, 20, 100), fill((90, 60, 36)))


def big_paper_text(cv, lines, x, y, w, h, rot, col=(250, 248, 240), ink=(40, 40, 50), sizes=None, font="Inter-Bold"):
    cv.save(); cv.translate(x, y); cv.rotate(rot)
    cv.drawRect(skia.Rect.MakeXYWH(-w / 2 + 12, -h / 2 + 16, w, h), fill((0, 0, 0), 0.3, blur=16))
    cv.drawRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), fill(col))
    yy = -h / 2 + 70
    for i, ln in enumerate(lines):
        sz = (sizes or [44] * len(lines))[i]
        c = ink if not isinstance(ln, tuple) else ln[1]; s = ln if not isinstance(ln, tuple) else ln[0]
        text_center(cv, s, 0, yy, sz, c, None, font=font, shadow_=False); yy += sz * 1.35
    cv.restore()


# ===================================================================== EPISODIO 3
def ep03():
    S = []
    P_SIT = H_.SIT_GROUND if hasattr(H_, "SIT_GROUND") else SIT_GROUND

    def s1(cv, lt, d, T):  # el hombre de la escoba se acerca
        cam = cam_move(lt, d, (560, 1600, 1.35), (640, 1620, 1.6)); court(cv, cam, "cancha_tarde")
        shade(cv, 820, 1900); ch(cv, PEDRITO, breathe(dict(SIT_GROUND, look=(-0.6, -0.3)), T), 820, 1900, face=-1, T=T)
        x, ph, mv = H_.walker(lt, 0.3, -100, 480, d - 0.6, 1.1)
        p = H_.walk(ph, base=dict(STAND, ab=(10, 80), mood="kind")) if mv else dict(STAND, ab=(10, 80), mood="kind", look=(0.8, 0.3))
        shade(cv, x, 1900); ch(cv, LUCHO, p, x, 1900, face=1, T=T, seed=40, ex=lucho_broom(-150, 420))
        rim_and_net(cv, *RIM); done(cv)
    S.append((0.0, s1))

    def s2(cv, lt, d, T):  # se llamaba Don Lucho; barre la cancha hace treinta años y pregunta
        cam = cam_move(lt, d, (520, 1520, 1.7), (600, 1480, 1.95)); court(cv, cam, "cancha_tarde")
        q = A("¿se ríen") - A("se llamaba")
        sw = math.sin(lt * 5) if lt < q else 0
        p = dict(STAND, lean=10 + 6 * sw, ab=(40 + 20 * sw, 20), af=(30 + 20 * sw, 30), head=6, mood="kind", look=(0.8, 0.5 if lt > q else 0.9))
        shade(cv, 480, 1900); ch(cv, LUCHO, p, 480, 1900, face=1, T=T, seed=40, ex=dict(hand_item=lambda c, h: broom(c, h, 30 + 12 * sw, 560)))
        shade(cv, 860, 1900); ch(cv, PEDRITO, dict(SIT_GROUND, look=(0.8, -0.3)), 860, 1900, face=-1, T=T)
        if lt < q: particles(cv, T, 18, 9, (200, 190, 170), (560, 1820, 300, 120), 15, (2, 5), 0.6)
        done(cv)
    S.append((A("se llamaba"), s2))

    def s3(cv, lt, d, T):  # «no, porque no sé jugar»
        cam = cam_move(lt, d, (840, 1560, 2.5), (860, 1580, 2.8)); court(cv, cam, "cancha_tarde")
        shade(cv, 860, 1900); ch(cv, PEDRITO, breathe(dict(SIT_GROUND, head=24, mood="sad", tears=1, look=(-0.4, 0.8)), T), 860, 1900, face=-1, T=T)
        done(cv)
    S.append((A("no porque"), s3))

    def s4(cv, lt, d, T):  # «mentira... tienes buena muñeca... te falta base»
        cam = cam_move(lt, d, (640, 1540, 1.7), (660, 1520, 1.85)); court(cv, cam, "cancha_tarde")
        k1 = A("tienes") - A("mentira"); k2 = A("lo que") - A("mentira")
        p = keys(lt, [(0, dict(POINT, mood="determined")), (k1, dict(STAND, af=(40, 120), ab=(20, 40), mood="happy")), (k2, dict(STAND, ab=(60, 30), af=(60, 30), lean=6, mood="kind"))])
        shade(cv, 480, 1900); ch(cv, LUCHO, p, 480, 1900, face=1, T=T, seed=40)
        pp = keys(lt, [(0, dict(SIT_GROUND, look=(-0.8, -0.4), mood="surprised")), (k1 + 0.3, dict(STAND, look=(-0.8, -0.6), mood="surprised")), (k2, dict(STAND, mood="happy", look=(-0.8, -0.6)))])
        shade(cv, 860, 1900); ch(cv, PEDRITO, pp, 860, 1900, face=-1, T=T, ex=dict(blush=lt > k1))
        done(cv)
    S.append((A("mentira"), s4))

    def s5(cv, lt, d, T):  # el armario viejo se abre, brillan las zapatillas
        cam = cam_move(lt, d, (700, 1400, 1.3), (760, 1300, 1.6)); cv.save(); cam.apply(cv); draw_bg(cv, "bodega")
        lx, ly, lw, lh = 620, 760, 360, 1000
        rrect(cv, lx, ly, lw, lh, 8, lin((lx, 0), (lx + lw, 0), [(120, 128, 136), (90, 96, 104)]))
        rrect(cv, lx + 20, ly + 20, lw - 40, lh - 40, 6, fill((30, 30, 34)))
        o = ease((lt - 0.6) / 1.2)
        glow = o * (0.7 + 0.3 * math.sin(T * 5))
        cv.drawCircle(lx + lw / 2, ly + 640, 260, rad((lx + lw / 2, ly + 640), 260, [(255, 220, 140, 0.6 * glow), (255, 220, 140, 0)]))
        for k, sx in enumerate((-60, 60)):   # zapatillas retro
            cx_, cy_ = lx + lw / 2 + sx, ly + 650
            rrect(cv, cx_ - 70, cy_ - 34, 140, 60, 26, fill((205, 45, 40))); rrect(cv, cx_ - 72, cy_ + 16, 144, 18, 8, fill((240, 236, 226)))
            cv.drawLine(cx_ - 30, cy_ + 10, cx_ + 40, cy_ - 20, stroke((245, 245, 240), 7))
        cv.drawRect(skia.Rect.MakeXYWH(lx + 20, ly + 720, lw - 40, 12), fill((80, 80, 86)))
        dw = (lw - 20) * (1 - o * 0.85)   # puerta que gira
        rrect(cv, lx + lw - dw if o > 0 else lx, ly, dw, lh, 8, lin((0, 0), (lw, 0), [(140, 148, 156), (100, 106, 114)]))
        for k in range(3): cv.drawRect(skia.Rect.MakeXYWH(lx + lw - dw + dw * 0.2, ly + 80 + k * 26, dw * 0.6, 8), fill((60, 64, 70), 0.6))
        particles(cv, T, 40, 5, (255, 240, 200), (lx - 100, ly, lw + 200, lh), 20, (2, 5), 0.5 + 0.4 * o)
        ch(cv, LUCHO, dict(STAND, af=(80 * o, 40 * o), mood="kind", look=(0.9, 0.2)), 470, 1900, face=1, T=T, seed=40)
        done(cv)
    S.append((A("don lucho abrió"), s5))

    def s6(cv, lt, d, T):  # las zapatillas grandes con calcetines gruesos, sonrisa tímida
        cam = cam_move(lt, d, (680, 1600, 1.8), (680, 1560, 2.1)); court(cv, cam, "cancha_tarde")
        x, ph, mv = H_.walker(lt, 0.5, 560, 720, 1.6, 1.0)
        p = H_.walk(ph, amp=0.6, base=dict(STAND, mood="happy")) if mv else breathe(dict(STAND, head=14, mood="happy", look=(0.2, 0.9)), T)
        shade(cv, x, 1900); ch(cv, PEDRITO_NUEVAS, p, x, 1900, face=1, T=T, ex=dict(blush=True))
        shade(cv, 360, 1900); ch(cv, LUCHO, dict(STAND, mood="happy", look=(0.9, 0.3)), 360, 1900, face=1, T=T, seed=40)
        done(cv)
    S.append((A("son de cuando"), s6))

    def s7(cv, lt, d, T):  # montaje al amanecer: pasos, pases, defensa, mil lanzamientos
        seg = d / 4; k = min(3, int(lt / seg)); u = (lt - k * seg) / seg
        cam = cam_move(u, 1, (600 + k * 30, 1600, 1.5 + 0.08 * k), (640 + k * 30, 1580, 1.6 + 0.08 * k)); court(cv, cam, "cancha_amanecer")
        if k == 0:     # pasos entre conos
            x = 300 + 680 * (0.5 - 0.5 * math.cos(u * math.pi)); ph = u * 4
            shade(cv, x, 1960); ch(cv, PEDRITO_NUEVAS, H_.run(ph, 0.8), x, 1960, face=1, T=T)
        elif k == 1:   # pases con Don Lucho
            shade(cv, 360, 1940); i1 = ch(cv, LUCHO, dict(HOLD, mood="happy"), 360, 1940, face=1, T=T, seed=40)
            shade(cv, 940, 1940); i2 = ch(cv, PEDRITO_NUEVAS, dict(HOLD, mood="determined"), 940, 1940, face=-1, T=T)
            v = (u * 2) % 1; a, b = (i1["hand_f"], i2["hand_f"]) if int(u * 2) % 2 == 0 else (i2["hand_f"], i1["hand_f"])
            bb = H_.arc(a, b, 120, v); ball(cv, bb[0], bb[1], 30, T * 8)
        elif k == 2:   # defensa lateral
            x = 640 + 160 * math.sin(u * 2 * math.pi * 1.5)
            shade(cv, x, 1960); ch(cv, PEDRITO_NUEVAS, dict(CROUCH, ab=(70, -30), af=(80, -40), mood="determined"), x, 1960, face=1, T=T)
        else:          # lanzamientos y sudor
            lt2 = (u * 2.2) % 1.1
            p = keys(lt2, [(0, HOLD), (0.25, CROUCH), (0.45, SHOOT_UP), (1.1, HOLD)])
            shade(cv, 640, 1920); info = ch(cv, PEDRITO_NUEVAS, p, 640, 1920, face=1, T=T)
            if lt2 > 0.45: bb = H_.arc(info["hand_f"], (RIM[0], RIM[1] - 10), 250, min(1, (lt2 - 0.45) / 0.55)); ball(cv, bb[0], bb[1], 28, T * 9)
            for j in range(3): cv.drawOval(skia.Rect.MakeXYWH(info["head"][0] - 60 + j * 50, info["head"][1] - 120 - (T * 80 + j * 30) % 60, 10, 16), fill((140, 200, 255), 0.8))
        rim_and_net(cv, *RIM, t=T); done(cv)
    S.append((A("desde esa"), s7))

    def s8(cv, lt, d, T):  # una semana después: Don Lucho aplaude, tiro limpio
        cam = cam_move(lt, d, (680, 1500, 1.35), (760, 1350, 1.5)); court(cv, cam, "cancha_amanecer")
        cl = (math.sin(T * 14) + 1) / 2
        shade(cv, 260, 1960); ch(cv, LUCHO, mix(CLAP_OPEN, CLAP_SHUT, cl) if lt > 1.2 else dict(STAND, mood="kind"), 260, 1960, face=1, T=T, seed=40)
        p = keys(lt, [(0, HOLD), (0.4, CROUCH), (0.7, dict(SHOOT_UP, air=0.1)), (1.1, SHOOT_UP), (2.0, dict(CHEER, mood="happy"))])
        shade(cv, 680, 1900); info = ch(cv, PEDRITO_NUEVAS, p, 680, 1900, face=1, T=T)
        if lt < 0.7: bb = (info["hand_f"][0], info["hand_f"][1] - 20)
        elif lt < 1.7: bb = H_.arc(info["hand_f"], (RIM[0], RIM[1] - 20), 300, (lt - 0.7))
        else: bb = (RIM[0], lerp(RIM[1], 1900, ease(min(1, (lt - 1.7) / 0.5))))
        ball(cv, bb[0], bb[1], 30, lt * 9)
        rim_and_net(cv, *RIM, swish=clamp(1 - abs(lt - 1.8) / 0.5), t=T); done(cv)
    S.append((A("una semana"), s8))

    def s9(cv, lt, d, T):  # la noticia: último cupo
        cam = cam_move(lt, d, (675, 1500, 1.2), (675, 1220, 1.7)); cv.save(); cam.apply(cv); draw_bg(cv, "colegio_cupo")
        x, ph, mv = H_.walker(lt, 0, -150, 420, 1.6, 2.2)
        p = H_.run(ph, 0.8) if mv else dict(STAND, head=-14, look=(0.7, -0.8), mood="surprised" if lt < 3 else "determined")
        shade(cv, x, 2080); ch(cv, PEDRITO_NUEVAS, p, x, 2080, face=1, T=T)
        done(cv)
    S.append((A("y entonces"), s9))
    texts = [("DON LUCHO", A("se llamaba"), A("¿se ríen") - 0.1), ("ENTRENAMIENTO", A("desde esa"), A("una semana") - 0.1),
             ("ÚLTIMO CUPO", A("último cupo"), 54.6)]
    return S, texts


# ===================================================================== EPISODIO 4
def table(cv, few=True):
    rrect(cv, 140, 1560, 560, 30, 8, fill((120, 72, 40)))
    for x in (170, 640): cv.drawRect(skia.Rect.MakeXYWH(x, 1585, 26, 180), fill((100, 60, 34)))
    for k in range(3 if few else 8): cv.drawOval(skia.Rect.MakeXYWH(300 + k * 30, 1545, 30, 12), fill((225, 175, 70)))


def ep04():
    S = []

    def s1(cv, lt, d, T):  # a un paso de rendirse
        cam = cam_move(lt, d, (675, 1500, 1.4), (675, 1450, 1.75)); cv.save(); cam.apply(cv); draw_bg(cv, "colegio_cupo")
        shade(cv, 680, 2060); info = ch(cv, PEDRITO_NUEVAS, breathe(dict(HOLD, head=26, mood="sad", look=(0.3, 1.0)), T), 680, 2060, T=T)
        paper(cv, info["hand_f"][0] + 10, info["hand_f"][1] - 10, 90, 120, -8)
        done(cv)
    S.append((0.0, s1))

    def s2(cv, lt, d, T):  # la hoja con la cuota enorme, manos temblorosas
        cv.drawRect(skia.Rect.MakeWH(W, H), lin((0, 0), (0, H), [(70, 60, 60), (40, 34, 34)]))
        sh = 3 * math.sin(T * 40) * clamp((lt - 1.2) / 0.5)
        big_paper_text(cv, ["COLEGIO SAN JORGE", "INSCRIPCIÓN EQUIPO", ("CUOTA:", (60, 60, 70)), ("$45.000", (200, 40, 30)), "PAGAR ANTES DEL SÁBADO"],
                       W / 2 + sh, 860 + sh, 760, 1000, -2 + sh * 0.2, sizes=[40, 52, 56, 150, 34])
        for sx in (-1, 1):
            hx, hy = W / 2 + sx * 400 + sh, 1250 + sh
            cv.drawLine(hx, hy, hx + sx * 120, hy + 600, stroke(BLACK, 16)); cv.drawCircle(hx, hy, 24, fill(BLACK))
        done = None
    S.append((A("faltaban"), s2))

    def s3(cv, lt, d, T):  # en su casa no había ese dinero
        cam = cam_move(lt, d, (520, 1500, 1.5), (480, 1520, 1.7)); cv.save(); cam.apply(cv); draw_bg(cv, "casa")
        rrect(cv, 330, 1640, 120, 20, 6, fill((110, 66, 36)))
        ch(cv, MAMA, dict(SIT_BENCH, af=(70, 40), ab=(60, 50), head=16, look=(0.4, 0.9), mood="worried"), 390, 1770, S=520, T=T, seed=3, persp_on=False)
        table(cv, True); cv.restore()
    S.append((A("en su casa"), s3))

    def s4(cv, lt, d, T):  # Tomás se burla
        cam = cam_move(lt, d, (675, 1450, 1.45), (760, 1420, 1.65)); cv.save(); cam.apply(cv); draw_bg(cv, "gimnasio")
        laugh = math.sin(T * 14)
        p = dict(CROSS, lean=-8 + 4 * laugh, head=-12, mood="smug") if lt > 1.0 else dict(CROSS, mood="smug")
        shade(cv, 860, 1900); ch(cv, TOMAS, p, 860, 1900, face=-1, T=T, seed=80)
        shade(cv, 460, 1900); ch(cv, PEDRITO_NUEVAS, dict(SAD_STAND, look=(0.8, -0.3), head=6), 460, 1900, face=1, T=T)
        for k in range(8):
            a = math.sin(T * 6 + k) * 0.5 + 0.5
            cv.drawLine(980 + (k % 4) * 30, 1980, 1000 + (k % 4) * 30, 1960, stroke((255, 255, 255), 4, a))   # brillo zapatillas
        cv.restore()
    S.append((A("tomás"), s4))

    def s5(cv, lt, d, T):  # deja la pelota sobre la banca y se va
        cam = cam_move(lt, d, (640, 1600, 1.35), (560, 1640, 1.4)); court(cv, cam, "cancha_tarde")
        bench(cv, 760, 1880)
        drop = A("dejó su pelota") - A("pedrito caminó") + 0.6; go = A("y se fue") - A("pedrito caminó")
        if lt < drop:
            x, ph, mv = H_.walker(lt, 0, 200, 620, drop - 0.3, 1.2)
            info = ch(cv, PEDRITO_NUEVAS, H_.walk(ph, base=dict(HOLD, mood="sad", head=14)) if mv else dict(CROUCH, mood="sad"), x, 1900, face=1, T=T)
            ball(cv, info["hand_f"][0] + 14, info["hand_f"][1], 34, 0)
        else:
            ball(cv, 760, 1880 - 120 - 34, 34, 0)
            x, ph, mv = H_.walker(lt, max(drop, go), 620, -200, 2.4, 1.2)
            ch(cv, PEDRITO_NUEVAS, H_.walk(ph, base=SAD_STAND) if mv else SAD_STAND, x, 1900, face=-1, T=T)
        rim_and_net(cv, *RIM); done(cv)
    S.append((A("pedrito caminó"), s5))

    def s6(cv, lt, d, T):  # esa noche no durmió; su mamá asoma la cabeza
        cam = cam_move(lt, d, (640, 1450, 1.4), (700, 1420, 1.55)); cv.save(); cam.apply(cv); draw_bg(cv, "pieza_noche")
        cv.save(); cv.translate(440, 1500); cv.rotate(-90)
        ch(cv, PEDRITO_NUEVAS, dict(STAND, mood="worried", look=(-0.2, -1.0), blink=0), 0, 0, S=520, T=T, persp_on=False)
        cv.restore()
        rrect(cv, 300, 1470, 520, 120, 40, fill((80, 100, 170)))      # manta
        u = ease((lt - 0.8) / 1.0)
        cv.save(); cv.clipRect(skia.Rect.MakeXYWH(1080, 800, 300, 1000))
        ch(cv, MAMA, dict(STAND, mood="worried", look=(-0.9, 0.2), lean=-10), lerp(1260, 1150, u), 1760, S=520, face=-1, T=T, seed=3, persp_on=False)
        cv.restore()
        cv.drawRect(skia.Rect.MakeXYWH(0, 0, BW, BH), fill((10, 20, 60), 0.25)); cv.restore()
    S.append((A("esa noche"), s6))

    def s7(cv, lt, d, T):  # en la mañana, la pelota en la puerta con una nota amarilla
        cam = cam_move(lt, d, (640, 1500, 1.25), (640, 1640, 1.6)); cv.save(); cam.apply(cv); draw_bg(cv, "puerta")
        ball(cv, 640, 1760 - 44, 44, 0.3)
        cv.save(); cv.translate(640, 1690); cv.rotate(-12); rrect(cv, -46, -36, 92, 72, 4, fill((255, 220, 60))); cv.restore()
        u = ease((lt - 1.2) / 1.0)
        if u > 0:
            ch(cv, PEDRITO_NUEVAS, dict(STAND, mood="surprised", head=20, look=(0.0, 1.0)), 560, 1760, S=520, face=1, T=T, persp_on=False)
        done(cv)
    S.append((A("en la mañana"), s7))

    def s8(cv, lt, d, T):  # la nota y Pedrito leyendo con una pequeña sonrisa
        hug = A("pedrito la apretó") - A("los sueños")
        if lt < hug:
            cv.drawRect(skia.Rect.MakeWH(W, H), lin((0, 0), (0, H), [(250, 230, 190), (220, 190, 140)]))
            big_paper_text(cv, ["Los sueños no se", "cobran en la entrada.", "", "Ven al partido", "del barrio.", "", "El entrenador va", "a estar mirando."],
                           W / 2, 900, 820, 1050, 3 + math.sin(T) * 0.5, col=(255, 222, 70), ink=(50, 40, 30), font="Inter-SemiBold",
                           sizes=[58, 58, 30, 58, 58, 30, 58, 58])
        else:
            cam = cam_move(lt - hug, d - hug, (640, 1560, 1.9), (640, 1520, 2.3)); cv.save(); cam.apply(cv); draw_bg(cv, "puerta")
            info = ch(cv, PEDRITO_NUEVAS, dict(HUG, mood="happy", head=10, look=(0.3, 0.7)), 640, 1820, S=560, face=1, T=T, persp_on=False, ex=dict(blush=True))
            ball(cv, info["hand_f"][0] - 30, info["hand_f"][1] - 20, 40, 0)
            particles(cv, T, 20, 3, (255, 230, 140), (400, 1200, 500, 500), 30, (2, 5), 0.8)
            cv.restore()
    S.append((A("los sueños"), s8))
    texts = [("LA CUOTA", A("una cuota"), A("en su casa") - 0.1), ("NO PUEDE PAGAR", A("en su casa"), A("tomás") - 0.1),
             ("«LOS SUEÑOS NO SE COBRAN»", A("los sueños"), A("pedrito la apretó") - 0.1)]
    return S, texts


# ===================================================================== EPISODIO 5
def crowd(cv, T, y=1560, cheer=0.0, seed=7):
    rnd = random.Random(seed)
    for k in range(9):
        x = 40 + k * 150 + rnd.uniform(-20, 20)
        hop = abs(math.sin(T * 9 + k)) * 40 * cheer
        p = mix(dict(STAND, mood="worried", look=(0.2, 0.3)), dict(CHEER, mood="happy"), cheer)
        ch(cv, Mo.NEIGHBORS[k % len(Mo.NEIGHBORS)], dict(p, air=0), x, y - hop, S=330, face=1 if k % 2 else -1, T=T, seed=100 + k, persp_on=False)


def scoreboard(cv, x, y, clock="0:05"):
    rrect(cv, x - 170, y - 90, 340, 180, 14, fill((20, 20, 24)))
    f = skia.Font(typeface("Inter-Black"), 70)
    cv.drawString("48", x - 150, y + 10, f, fill((255, 80, 60))); cv.drawString("48", x + 60, y + 10, f, fill((255, 80, 60)))
    cv.drawString(clock, x - 55, y + 75, skia.Font(typeface("Inter-Black"), 50), fill((255, 210, 60)))
    cv.drawRect(skia.Rect.MakeXYWH(x - 8, y + 90, 16, 400), fill((60, 60, 66)))


def ep05():
    S = []
    def s1(cv, lt, d, T):  # cinco segundos, empate, la cancha llena de vecinos
        cam = cam_move(lt, d, (675, 1500, 1.15), (640, 1560, 1.35)); court(cv, cam, "cancha_dorada")
        scoreboard(cv, 430, 1060, "0:05")
        crowd(cv, T)
        shade(cv, 1120, 1960); ch(cv, COACH, dict(CROSS, mood="focused"), 1120, 1960, face=-1, T=T, seed=60)
        shade(cv, 620, 1880); ch(cv, PEDRITO_NUEVAS, breathe(dict(STAND, mood="determined", look=(0.8, -0.6)), T), 620, 1880, face=1, T=T)
        rim_and_net(cv, *RIM); done(cv)
    S.append((0.0, s1))

    def s2(cv, lt, d, T):  # Tomás marcado, pase a Pedrito
        cam = cam_move(lt, d, (640, 1600, 1.4), (720, 1580, 1.55)); court(cv, cam, "cancha_dorada")
        crowd(cv, T, cheer=0.15)
        shade(cv, 380, 1900); iT = ch(cv, TOMAS, dict(HOLD, mood="worried"), 380, 1900, face=1, T=T, seed=80)
        shade(cv, 500, 1910); ch(cv, KIDS[2], dict(STAND, ab=(100, -20), af=(110, -20), mood="determined"), 500, 1910, face=-1, T=T, seed=90)
        catch = A("el balón llegó") - A("tomás se") + 0.6
        shade(cv, 900, 1900); iP = ch(cv, PEDRITO_NUEVAS, dict(HOLD, mood="determined", look=(0.9, -0.7)) if lt > catch else dict(STAND, ab=(60, 20), af=(70, 10), mood="determined"), 900, 1900, face=1, T=T)
        if lt < catch - 0.7: b = iT["hand_f"]
        elif lt < catch: b = H_.arc(iT["hand_f"], iP["hand_f"], 140, (lt - catch + 0.7) / 0.7)
        else: b = iP["hand_f"]
        ball(cv, b[0] + 10, b[1] - 10, 34, T * 6)
        rim_and_net(cv, *RIM); done(cv)
    S.append((A("tomás se"), s2))

    def s3(cv, lt, d, T):  # Don Lucho susurra: base firme, muñeca suave
        cam = cam_move(lt, d, (420, 1450, 2.3), (430, 1430, 2.6)); court(cv, cam, "cancha_dorada")
        crowd(cv, T, cheer=0.1)
        ch(cv, LUCHO, dict(STAND, ab=(70, 70), af=(75, 65), head=6, mood="kind", look=(0.8, 0)), 420, 1880, face=1, T=T, seed=40)
        for k in range(3):
            a = 0.5 + 0.5 * math.sin(T * 4 - k)
            cv.drawArc(skia.Rect.MakeXYWH(520 + k * 26, 1380 - k * 26, 60 + k * 52, 60 + k * 52), -40, 80, False, stroke((255, 255, 255), 5, a))
        done(cv)
    S.append((A("escuchó"), s3))

    def s4(cv, lt, d, T):  # dobla las rodillas, salta, la pelota da una vuelta lenta (cámara lenta)
        cam = cam_move(lt, d, (700, 1550, 1.5), (880, 1250, 1.6)); court(cv, cam, "cancha_dorada")
        crowd(cv, T * 0.4, cheer=0.0)
        rel = A("y soltó") - A("pedrito dobló")
        p = keys(lt, [(0, HOLD), (rel * 0.5, CROUCH), (rel, dict(SHOOT_UP, air=0.14)), (rel + 0.6, SHOOT_UP), (d, SHOOT_UP)])
        shade(cv, 680, 1900); info = ch(cv, PEDRITO_NUEVAS, p, 680, 1900, face=1, T=T)
        if lt < rel: b = (info["hand_f"][0], info["hand_f"][1] - 20)
        else: b = H_.arc((info["hand_f"][0], info["hand_f"][1] - 20), (RIM[0], RIM[1] - 30), 340, clamp((lt - rel) / (d - rel + 0.4)) ** 0.9)
        ball(cv, b[0], b[1], 34, lt * 2)
        cv.drawRect(skia.Rect.MakeXYWH(0, 0, BW, BH), fill((255, 200, 120), 0.08))
        rim_and_net(cv, *RIM); done(cv)
    S.append((A("pedrito dobló"), s4))

    def s5(cv, lt, d, T):  # ¡canasta! la red se mueve, el barrio salta
        cam = Cam(760, 1400, 1.4, shake=max(0, 10 * (1 - lt / 0.4)), t=T); court(cv, cam, "cancha_dorada")
        crowd(cv, T, cheer=ease(lt / 0.5))
        b = (RIM[0], lerp(RIM[1] - 20, 1900, ease(min(1, lt / 0.6)))); ball(cv, b[0], b[1], 34, lt * 6)
        shade(cv, 680, 1900); ch(cv, PEDRITO_NUEVAS, dict(CHEER, air=0.08 * abs(math.sin(T * 8)) if lt > 1 else 0), 680, 1900, face=1, T=T)
        rim_and_net(cv, *RIM, swish=clamp(1 - lt / 1.2), t=T)
        rnd = random.Random(3)
        for k in range(60):   # confeti
            x = rnd.uniform(200, 1200) + math.sin(T * 3 + k) * 30; y = 900 + ((T - A("sonaron")) * rnd.uniform(150, 300) + rnd.uniform(0, 900)) % 1200
            cv.save(); cv.translate(x, y); cv.rotate(T * 200 + k * 30)
            cv.drawRect(skia.Rect.MakeXYWH(-8, -4, 16, 8), fill([(255, 200, 61), (46, 158, 79), (255, 255, 255), (230, 80, 60)][k % 4]))
            cv.restore()
        done(cv)
    S.append((A("sonaron"), s5))

    def s6(cv, lt, d, T):  # apretón de manos y abrazo bajo el sol dorado, lágrimas de alegría
        h = A("pedrito miró") - A("el entrenador sonrió")
        if lt < h:
            cam = cam_move(lt, h, (680, 1500, 1.8), (700, 1480, 2.0)); court(cv, cam, "cancha_dorada")
            shade(cv, 880, 1900); ch(cv, COACH, dict(STAND, af=(70, 10), mood="happy"), 880, 1900, face=-1, T=T, seed=60)
            shade(cv, 560, 1900); ch(cv, PEDRITO_NUEVAS, dict(STAND, af=(70, 10), mood="happy", look=(0.8, -0.4)), 560, 1900, face=1, T=T, ex=dict(blush=True))
            done(cv)
        else:
            cam = cam_move(lt - h, d - h, (680, 1560, 1.6), (680, 1700, 2.1)); court(cv, cam, "cancha_dorada")
            shade(cv, 540, 1920); ch(cv, LUCHO, dict(HUG, tears=1, mood="happy"), 540, 1920, face=1, T=T, seed=40)
            shade(cv, 980, 1920); ch(cv, COACH, dict(HUG, mood="happy"), 980, 1920, face=-1, T=T, seed=60)
            shade(cv, 760, 1940); ch(cv, PEDRITO_NUEVAS, dict(CHEER, tears=1, mood="happy"), 760, 1940, face=1, T=T, ex=dict(blush=True))
            particles(cv, T, 40, 8, (255, 220, 140), (0, 900, BW, 1200), 30, (2, 6), 0.8)
            done(cv)
    S.append((A("el entrenador sonrió"), s6))

    def s7(cv, lt, d, T):  # avance de la próxima semana: una niña con anteojos y un taller de chatarra
        cv.drawRect(skia.Rect.MakeWH(W, H), lin((0, 0), (0, H), [(20, 24, 40), (8, 8, 14)]))
        rnd = random.Random(4)
        for k in range(14):   # chatarra
            x, y, r = rnd.uniform(0, W), rnd.uniform(1250, 1700), rnd.uniform(40, 120)
            cv.drawCircle(x, y, r, stroke((90, 90, 100), 12)); cv.drawCircle(x, y, r * 0.3, fill((60, 60, 70)))
        cv.drawCircle(W / 2, 700, 380, rad((W / 2, 700), 380, [(255, 200, 61, 0.35), (255, 200, 61, 0)]))
        u = ease(lt / 1.5)
        cv.saveLayer(None, None)
        camila = dict(hair="pony", hair_col=(60, 34, 20), shirt=(255, 200, 61), shirt2=(220, 160, 30), pants=(40, 50, 90), shoe=(90, 60, 40), h=1.0)
        info = draw_char(cv, camila, dict(STAND, mood="determined", look=(0.6, 0)), W / 2, 1500, 760, 1, T)
        hc, hr = info["head"], info["hr"]
        for sx in (-1, 1):
            cv.drawCircle(hc[0] + hr * 0.28 + sx * hr * 0.3, hc[1] - hr * 0.02, hr * 0.2, stroke((20, 20, 20), hr * 0.05))
        p = skia.Paint(Color=C((14, 14, 22), 1 - 0.75 * u)); p.setBlendMode(skia.BlendMode.kSrcATop); cv.drawPaint(p)
        cv.restore()
    S.append((A("la próxima"), s7))
    texts = [("CINCO SEGUNDOS", 0.3, A("el partido")), ("¡CANASTA!", A("canasta"), A("el entrenador sonrió") - 0.1),
             ("EL SUEÑO SE CUMPLIÓ", A("pedrito miró"), A("la próxima") - 0.1)]
    return S, texts
