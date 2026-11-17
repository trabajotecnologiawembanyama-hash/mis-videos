"""Banda sonora + efectos + voz de cada episodio de Brote. Uso: python3 sonido.py <epXX> <salida.wav>"""
import json, sys, wave, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import sintes as S
from sintes import place, piano, pluck, pad, thump, whistle, squeak, rip, coins, murmur, laughs, wind, reverb, midi, SR, NA

EP, OUT = sys.argv[1], sys.argv[2]
WORDS = json.load(open(f"/tmp/claude-0/brote/k_{EP}/palabras.json"))["words"]
DUR = 55.0


def at(seq, nth=0):
    toks = [x.strip(",.«»¿?¡!:…") for x in seq.lower().split()]; hits = []
    for i in range(len(WORDS) - len(toks) + 1):
        if all(WORDS[i + k]["w"].strip(",.«»¿?¡!:…").lower() == toks[k] for k in range(len(toks))):
            hits.append(WORDS[i]["t0"])
    return hits[nth] - 0.1


mus = np.zeros((NA, 2), np.float32); fx = np.zeros((NA, 2), np.float32)
HOPE = [[60, 64, 67], [57, 60, 64], [53, 57, 60], [55, 59, 62]]      # C Am F G
TENSE = [[57, 60, 64], [53, 57, 60], [55, 59, 62], [52, 55, 59]]     # Am F G Em
TRIUMPH = [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]   # C G Am F


def groove(t0, t1, prog, bar=2.2, vol=0.18, keys=True, padv=0.10, bright=1500):
    t = t0
    while t < t1 - 0.3:
        ch = prog[int((t - t0) / bar) % 4]
        place(mus, pad([midi(m - 12) for m in ch], min(bar + 0.6, t1 - t + 0.4), 0.5, 0.6, padv, bright), t)
        for j, m in enumerate([ch[0], ch[2], ch[1] + 12, ch[2]]):
            if t + j * bar / 4 < t1: place(mus, pluck(midi(m), 1.1, vol), t + j * bar / 4, pan=(-0.3 if j % 2 else 0.3))
        if keys: place(mus, piano(midi(ch[0] + 12), 2.0, 0.14), t + bar / 2)
        t += bar


def sad(t0, t1, notes=(69, 67, 64, 62, 60, 64, 62, 57)):
    for k, m in enumerate(notes):
        if t0 + k * 1.15 < t1: place(mus, piano(midi(m), 2.6, 0.24), t0 + k * 1.15)
    place(mus, pad([midi(m) for m in (45, 52, 57, 60)], t1 - t0 + 1, 1.2, 2, 0.11, 800), t0)


def mystery(t0, t1=DUR):
    place(mus, pad([midi(m) for m in (38, 45, 50, 52)], t1 - t0, 0.5, 2.5, 0.17, 700), t0)
    place(mus, piano(midi(38), 6.0, 0.4), t0 + 0.1)
    place(mus, piano(midi(74), 3.0, 0.2), t0 + 2.6)


def dribbles(t0, t1, every=0.55, f=100, g=0.3):
    for tt in np.arange(t0, t1, every): place(fx, thump(f, 0.25, g), tt)


if EP == "ep01":
    groove(0.0, at("y no sabía"), HOPE)
    mystery(at("y no sabía"))
    dribbles(0.4, at("y un par"), 0.5); dribbles(at("cada") + 0.2, at("quería"), 0.5, 92, 0.22)
    for k in range(5): place(fx, S.coins(0.22), at("unas") + 0.3 + k * 0.6)
    place(fx, rip(0.45, 0.4), at("así que") + 0.5); place(fx, rip(0.35, 0.3), at("una y otra"))
    place(fx, thump(150, 0.15, 0.3), at("lanzó") + 2.1); place(fx, thump(110, 0.25, 0.3), at("lanzó") + 2.6)
    place(fx, wind(DUR - at("y no sabía"), 0.03), at("y no sabía"))
elif EP == "ep02":
    place(fx, murmur(at("en ese instante"), 0.04), 0.0)
    groove(0.0, at("en ese instante"), TENSE, 2.0)
    for tt in (1.2, 2.9, at("los otros") + 1.0, at("pedrito robó") + 0.4, at("pedrito robó") + 1.3): place(fx, squeak(0.08), tt)
    place(fx, whistle(0.9), at("silbato"))
    dribbles(at("pedrito robó") + 0.1, at("saltó"), 0.42, 115, 0.35)
    place(fx, rip(0.5, 0.55), at("la suela") + 0.1)
    place(fx, thump(70, 0.5, 0.9), at("pedrito cayó") + 0.25)
    for k, tt in enumerate((0.5, 1.1, 1.6, 1.95)): place(fx, thump(120, 0.2, 0.4 / (k + 1)), at("pedrito cayó") + tt)
    place(fx, laughs(3.0, 0.13), at("estalló") - 0.1)
    sad(at("pedrito cayó") + 1.0, at("y entonces"))
    place(fx, wind(DUR - at("se sentó"), 0.035), at("se sentó"))
    mystery(at("y entonces"))
elif EP == "ep03":
    mystery(0.0, at("se llamaba") + 1.0)
    groove(at("se llamaba"), at("desde esa"), HOPE, 2.4, 0.15, padv=0.09)
    place(fx, S.rip(0.6, 0.12), at("don lucho abrió") + 0.3)                     # chirrido del armario
    groove(at("desde esa"), at("y entonces"), TRIUMPH, 1.6, 0.22, padv=0.12, bright=2200)
    dribbles(at("desde esa") + 0.3, at("y entonces"), 0.4, 110, 0.28)
    for k in range(3): place(fx, thump(150, 0.15, 0.3), at("una semana") + 0.8 + k * 0.05)
    place(mus, pad([midi(m) for m in (48, 55, 60, 64, 67)], DUR - at("y entonces"), 0.3, 2.5, 0.16, 1600), at("y entonces"))
    place(mus, piano(midi(72), 3, 0.3), at("último cupo")); place(mus, piano(midi(79), 3, 0.25), at("último cupo") + 0.4)
elif EP == "ep04":
    place(mus, pad([midi(m) for m in (45, 52, 57, 60)], at("tomás") + 0.5, 1.0, 1.5, 0.12, 700), 0.0)
    for k, m in enumerate((57, 60, 64, 62, 60)): place(mus, piano(midi(m), 2.2, 0.22), 0.5 + k * 1.6)
    place(fx, S.coins(0.15), at("en su casa") + 0.4)
    place(mus, pad([midi(m) for m in (40, 47, 52, 55)], at("pedrito caminó") - at("tomás") + 0.5, 0.3, 0.8, 0.14, 600), at("tomás"))
    place(fx, laughs(1.4, 0.08), at("se burló"))
    sad(at("pedrito caminó"), at("en la mañana"))
    place(fx, thump(90, 0.3, 0.3), at("dejó su pelota") + 0.8)
    place(fx, wind(4, 0.03), at("esa noche"))
    groove(at("en la mañana"), at("pedrito la apretó"), HOPE, 2.2, 0.16)
    place(mus, pad([midi(m) for m in (48, 55, 60, 64, 67)], DUR - at("pedrito la apretó"), 0.4, 2.5, 0.17, 1500), at("pedrito la apretó"))
    place(mus, piano(midi(72), 3.0, 0.3), at("pedrito la apretó") + 0.3); place(mus, piano(midi(76), 3.0, 0.25), at("pedrito la apretó") + 1.0)
elif EP == "ep05":
    place(fx, murmur(at("la pelota dio"), 0.06), 0.0)
    place(mus, pad([midi(m) for m in (45, 52, 57)], at("la pelota dio"), 0.2, 0.3, 0.16, 900), 0.0)
    for tt in np.arange(0.3, at("la pelota dio"), 0.6): place(fx, thump(60, 0.3, 0.35), tt)       # latido de tensión
    place(fx, thump(115, 0.22, 0.4), at("el balón llegó") + 0.4)
    place(mus, pad([midi(m) for m in (50, 57, 62)], 3.0, 0.1, 1.0, 0.18, 600), at("la pelota dio"))
    place(fx, thump(160, 0.15, 0.5), at("sonaron") + 0.1)
    for k in range(4): place(fx, S.coins(0.12), at("sonaron") + 0.15 + k * 0.08)
    place(fx, laughs(4.0, 0.2), at("canasta")); place(fx, murmur(5.0, 0.16), at("canasta"))
    groove(at("canasta"), at("la próxima"), TRIUMPH, 1.8, 0.24, padv=0.13, bright=2600)
    place(mus, pad([midi(m) for m in (48, 55, 60, 64, 67, 72)], at("la próxima") - at("canasta"), 0.05, 1.5, 0.12, 2400), at("canasta"))
    mystery(at("la próxima"))

elif EP in ("ep06", "ep07", "ep08", "ep09", "ep10"):
    rng = S.rng

    def rainfx(d, g=0.05):
        return (S.bp(rng.normal(0, 1, (int(d * SR), 2)), 1500, 7000) * g).astype(np.float32)

    def thunder(d=3.2, g=0.7):
        n = int(d * SR); t = np.arange(n) / SR
        x = S.lp(rng.normal(0, 1, n), 110) * 6 * np.exp(-t * 1.1) * (0.6 + 0.4 * np.sin(t * 9) ** 2)
        x[:int(0.25 * SR)] += S.bp(rng.normal(0, 1, int(0.25 * SR)), 300, 2500) * np.exp(-np.arange(int(0.25 * SR)) / SR * 14) * 1.5
        return (x * g).astype(np.float32)

    def zap(g=0.5):
        n = int(0.45 * SR); t = np.arange(n) / SR
        x = S.bp(rng.normal(0, 1, n), 1800, 9000) * np.exp(-t * 9) * (rng.random(n) < 0.35) * 3 + np.sign(np.sin(2 * np.pi * 95 * t)) * np.exp(-t * 12) * 0.5
        return (x * g).astype(np.float32)

    def beep(f1=880, f2=1320, g=0.2):
        n = int(0.12 * SR); t = np.arange(n) / SR; e = np.sin(np.pi * t / 0.12)
        return (np.concatenate([np.sin(2 * np.pi * f1 * t) * e, np.sin(2 * np.pi * f2 * t) * e]) * g).astype(np.float32)

    def servo(d=1.0, f0=220, f1=520, g=0.12):
        n = int(d * SR); t = np.arange(n) / SR
        f = f0 + (f1 - f0) * t / d
        x = np.sin(2 * np.pi * np.cumsum(f) / SR + 2.0 * np.sin(2 * np.pi * 38 * t)) * np.minimum(1, t / 0.05) * np.minimum(1, (d - t) / 0.1)
        return (x * g).astype(np.float32)

    def tac(g=0.25, f=900): return thump(f, 0.05, g)

    def clank(g=0.3):
        n = int(0.18 * SR); t = np.arange(n) / SR
        x = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * 28) for f in (410, 987, 1730, 2590)) / 4 + S.bp(rng.normal(0, 1, n), 800, 5000) * np.exp(-t * 60) * 0.4
        return (x * g).astype(np.float32)

    def applause(d, g=0.12):
        n = int(d * SR); x = S.bp(rng.normal(0, 1, (n, 2)), 900, 6500)
        m = np.abs(S.lp(rng.normal(0, 1, (n, 2)), 28)); m = m / (m.max() + 1e-9)
        t = np.arange(n) / SR; e = np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.8)
        return (x * (0.35 + 2.2 * m) * e[:, None] * g).astype(np.float32)

    def sparkle(t0, base=84, n=4, g=0.16):
        for k in range(n): place(mus, piano(midi(base + (0, 4, 7, 12)[k % 4]), 1.6, g), t0 + k * 0.09, pan=(-0.4 + 0.25 * k))

    def tinker(t0, t1, every=0.45, g=0.14):
        for k, tt in enumerate(np.arange(t0, t1, every)): place(fx, tac(g, 700 + 260 * (k % 3)), tt, pan=(-0.3 if k % 2 else 0.3))

    def minor(t0, t1, g=0.12): place(mus, pad([midi(m) for m in (45, 52, 57, 60)], t1 - t0 + 0.6, 0.6, 1.0, g, 800), t0)

    if EP == "ep06":
        place(fx, murmur(at("camila de trece") + 0.4, 0.05), 0.0); place(fx, murmur(at("su sueño") - at("cada domingo") + 0.4, 0.05), at("cada domingo"))
        groove(0.0, at("pero un robot"), HOPE, 2.2, 0.17)
        tinker(at("camila de trece") + 0.3, at("cada domingo"))
        sparkle(at("su sueño") + 0.5); sparkle(at("construir") + 0.2, 79)
        minor(at("pero un robot"), at("con una caja")); place(fx, coins(0.2), at("pero un robot") + 1.6)
        groove(at("con una caja"), at("cuando terminó"), TRIUMPH, 1.8, 0.2, padv=0.11, bright=2000)
        tinker(at("empezó a armar"), at("latas"), 0.4)
        for w_ in ("latas", "tuercas", "un colador"): place(fx, clank(0.35), at(w_) + 0.15); place(fx, thump(300, 0.12, 0.3), at(w_) + 0.15)
        tinker(at("cuando terminó") + 0.1, at("el robot quedó"), 0.28, 0.18)
        mystery(at("el robot quedó"))
        for k in range(4): place(fx, thump(58, 0.3, 0.3), at("necesitas") + 0.2 + k * 0.85); place(fx, thump(52, 0.3, 0.2), at("necesitas") + 0.48 + k * 0.85)
        place(fx, wind(DUR - at("le faltaba"), 0.025), at("le faltaba"))
    elif EP == "ep07":
        place(fx, beep(), 0.25); place(fx, servo(1.1), 0.6)
        groove(0.0, at("un chispazo"), HOPE, 2.0, 0.18)
        tinker(at("camila había") + 0.4, at("las tapas"), 0.5)
        place(fx, beep(), at("las tapas") + 0.1); place(fx, servo(0.9), at("el brazo"))
        place(fx, zap(0.7), at("un chispazo") + 0.1); place(fx, thump(60, 0.6, 0.8), at("un chispazo") + 0.15)
        place(fx, S.bp(rng.normal(0, 1, int(2.5 * SR)), 300, 1500).astype(np.float32) * 0.03, at("el motor echó"))       # humo siseando
        place(fx, laughs(2.6, 0.13), at("se rieron") - 0.2); place(fx, laughs(1.6, 0.09), at("tu robot") + 0.6)
        minor(at("sus compañeros"), at("ella no"), 0.1)
        sad(at("ella no"), at("entonces"))
        place(fx, clank(0.3), at("dejó el destornillador") + 0.4); place(fx, clank(0.15), at("dejó el destornillador") + 0.62)
        place(fx, thump(200, 0.1, 0.3), at("cuatro días")); place(fx, wind(DUR - at("ya no había"), 0.03), at("ya no había"))
        mystery(at("entonces"))
        place(fx, rip(0.7, 0.1), at("se escuchó") - 0.1)
        for k in range(3): place(fx, tac(0.5, 620), at("tac", k) + 0.12); place(fx, tac(0.3, 1200), at("tac", k) + 0.16)
        sparkle(at("mijita") + 0.2, 72, 3, 0.14)
    elif EP == "ep08":
        mystery(0.0, at("abuela rosa") + 0.8)
        groove(at("abuela rosa"), at("en un rincón"), HOPE, 2.4, 0.14, padv=0.09)
        for tt in np.arange(0.3, at("en un rincón"), 0.11): place(fx, tac(0.07, 1100), tt, pan=-0.2)                # máquina de coser
        minor(at("en un rincón"), at("esa ya"), 0.1); place(fx, wind(at("esa ya") - at("en un rincón"), 0.02), at("en un rincón"))
        groove(at("esa ya"), at("camila conectó"), HOPE, 2.2, 0.16)
        sparkle(at("camila abrió") + 0.2); tinker(at("juntas") + 0.2, at("las cosas buenas"), 0.3, 0.16)
        sparkle(at("las cosas buenas") + 0.6, 79, 4, 0.18); place(mus, pad([midi(m) for m in (60, 67, 72, 76)], 3.5, 0.4, 1.5, 0.1, 2400), at("las cosas buenas") + 0.4)
        groove(at("camila conectó"), at("pero la abuela"), TRIUMPH, 1.8, 0.21, padv=0.12, bright=2200)
        tinker(at("camila conectó") + 0.3, at("las tapas"), 0.4)
        place(fx, beep(), at("las tapas") + 0.3); place(fx, servo(1.0), at("y el robot") + 0.1)
        sparkle(at("camila gritó") + 0.3, 84, 4, 0.2); place(fx, applause(1.6, 0.05), at("camila gritó") + 0.4)
        mystery(at("pero la abuela"))
        place(fx, clank(0.2), at("y de dónde") + 0.2)
    elif EP == "ep09":
        tr = at("camila respiró")
        r = rainfx(tr + 3.0, 0.06); n_ = len(r); r[-int(3 * SR):] *= np.linspace(1, 0, int(3 * SR))[:, None]; place(fx, r, 0.0)
        for tt in (0.5, 2.3, at("pero un trueno") + 0.3, at("corrió") + 1.6, at("el robot estaba") + 0.9): place(fx, thunder(), tt)
        minor(0.0, at("corrió"), 0.13)
        groove(at("corrió"), at("el robot estaba"), TENSE, 1.5, 0.2)
        for tt in np.arange(at("corrió") + 0.1, at("corrió") + 2.0, 0.26): place(fx, thump(140, 0.1, 0.22), tt)            # pasos en el agua
        sad(at("el robot estaba"), at("la abuela le puso"))
        for tt in np.arange(at("intentó") + 0.3, at("aún faltaban"), 0.35): place(fx, S.bp(rng.normal(0, 1, int(0.2 * SR)), 500, 3000).astype(np.float32) * 0.05, tt)
        place(mus, pad([midi(m) for m in (53, 60, 65, 69)], tr - at("la abuela le puso") + 0.5, 1.0, 1.5, 0.13, 1500), at("la abuela le puso"))
        for k, m in enumerate((65, 69, 72, 77, 76, 72)): place(mus, piano(midi(m), 2.6, 0.2), at("la abuela le puso") + 0.6 + k * 1.3)
        groove(tr, at("cuando amaneció"), HOPE, 2.0, 0.18); tinker(tr + 0.8, at("cuando amaneció"), 0.4)
        for k in range(6): place(fx, tac(0.12, 2200 + 300 * (k % 3)), at("cuando amaneció") + 0.2 + k * 0.33)        # pájaros
        for k in range(3): place(fx, thump(170, 0.12, 0.6), at("alguien tocó") + 0.5 + k * 0.22)
        groove(at("era todo"), DUR - 0.5, TRIUMPH, 1.8, 0.24, padv=0.13, bright=2600)
        place(fx, applause(DUR - at("era todo") - 0.6, 0.07), at("era todo") + 0.5); sparkle(at("era todo") + 0.3, 84, 4, 0.2)
    else:
        place(fx, murmur(at("respiró"), 0.05), 0.0)
        place(fx, beep(), 0.1); place(fx, servo(0.7), 0.3); place(fx, laughs(0.01, 0.0), 0.0)
        groove(0.0, at("en una esquina"), HOPE, 2.2, 0.17)
        minor(at("en una esquina"), at("las tapas"), 0.14)
        for tt in np.arange(at("en una esquina") + 0.3, at("apretó"), 0.62): place(fx, thump(58, 0.3, 0.32), tt); place(fx, thump(52, 0.3, 0.2), tt + 0.26)
        place(fx, thump(240, 0.08, 0.6), at("apretó") + 0.35); place(fx, tac(0.4, 1500), at("apretó") + 0.37)
        place(fx, beep(), at("las tapas") + 0.15)
        groove(at("las tapas"), at("al final"), HOPE, 2.0, 0.19, padv=0.11, bright=1900)
        for k in range(3): place(fx, clank(0.22), at("el robot dio") + 0.25 + k * 0.42); place(fx, thump(110, 0.12, 0.3), at("el robot dio") + 0.25 + k * 0.42)
        place(fx, servo(0.5, 300, 420), at("tomó") + 0.1); place(fx, servo(0.5, 420, 300), at("y la dejó"))
        for k in range(3): place(fx, thump(260, 0.07, 0.35 / (k + 1)), max(at("y la dejó") + 0.3, at("tomó") + 1.6) + 0.35 + k * 0.3)
        place(fx, servo(0.7, 260, 560), at("luego levantó") + 0.1); sparkle(at("y saludó") + 0.2)
        place(fx, murmur(2.0, 0.07), at("y saludó") + 0.3)
        sparkle(at("de chatarra") + 0.1, 79, 2); sparkle(at("de pilas") + 0.1, 81, 2); sparkle(at("y del motor") + 0.1, 84, 2)
        ta = at("al final"); tc = at("camila subió")
        for k, tt in enumerate(np.arange(ta + 0.3, tc - 0.2, 0.055)): place(fx, thump(180, 0.05, 0.08 + 0.2 * k * 0.055 / max(0.5, tc - ta)), tt)       # redoble
        place(fx, S.bp(rng.normal(0, 1, int(1.6 * SR)), 3000, 11000).astype(np.float32) * np.exp(-np.arange(int(1.6 * SR)) / SR * 2.5).astype(np.float32) * 0.25, tc - 0.2)
        groove(tc, at("la próxima"), TRIUMPH, 1.8, 0.25, padv=0.14, bright=2800)
        place(fx, applause(at("la próxima") - tc + 0.5, 0.12), tc)
        sparkle(at("y levantó") + 0.4, 84, 4, 0.22)
        mystery(at("la próxima"))


mus = reverb(mus, 2.4, 0.3); fx = reverb(fx, 1.2, 0.18)
w = wave.open(f"/tmp/claude-0/brote/k_{EP}/voz.wav"); v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
v = np.pad(v[:NA], (0, max(0, NA - len(v))))
e = np.sqrt(np.convolve(v ** 2, np.ones(4800) / 4800, "same")); e = np.clip(e / 0.04, 0, 1)
e = np.convolve(e, np.ones(9600) / 9600, "same")
mix = mus * (0.55 * (1 - 0.5 * e))[:, None] + fx * 0.8 + np.stack([v, v], 1) * 0.95
fo = int(0.6 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
mix = np.tanh(mix * 1.05); mix = mix / np.abs(mix).max() * 0.95
o = wave.open(OUT, "wb"); o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR); o.writeframes((mix * 32767).astype(np.int16).tobytes()); o.close()
print("ok", OUT)
