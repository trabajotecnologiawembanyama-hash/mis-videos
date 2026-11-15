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
