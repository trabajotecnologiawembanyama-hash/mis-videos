"""Banda sonora sintetizada + diseño sonoro + mezcla con la narración (ducking). Salida: WAV estéreo 48 kHz, 40 s."""
import sys, wave
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

BUILD = sys.argv[1]
SR = 48000
DUR = 40.0
N = int(SR * DUR)
rng = np.random.default_rng(42)
t_all = np.arange(N) / SR


def buf(): return np.zeros((N, 2), np.float32)


def env(n, a, r, sustain=None):
    e = np.ones(n, np.float32)
    na = max(1, int(a * SR)); nr = max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na)
    e[-nr:] *= np.linspace(1, 0, nr)
    return e


def place(b, x, t0, gain=1.0, pan=0.0):
    i0 = int(t0 * SR)
    if x.ndim == 1: x = np.stack([x * (1 - max(0, pan)), x * (1 + min(0, pan))], 1)
    n = min(len(x), N - i0)
    if n > 0: b[i0:i0 + n] += x[:n] * gain


def lp(x, f, order=2): return sosfilt(butter(order, f, "low", fs=SR, output="sos"), x, axis=0)
def hp(x, f, order=2): return sosfilt(butter(order, f, "high", fs=SR, output="sos"), x, axis=0)
def bp(x, f1, f2): return sosfilt(butter(2, [f1, f2], "band", fs=SR, output="sos"), x, axis=0)


def midi(m): return 440 * 2 ** ((m - 69) / 12)


def reverb(x, secs=2.8, wet=0.3, damp=3500):
    n = int(secs * SR)
    ir = rng.normal(0, 1, (n, 2)).astype(np.float32) * np.exp(-np.arange(n) / (SR * secs / 6.5))[:, None]
    ir = lp(ir, damp)
    ir[:int(0.012 * SR)] = 0
    ir /= np.sqrt((ir ** 2).sum(0))
    y = np.stack([fftconvolve(x[:, c], ir[:, c])[:len(x)] for c in range(2)], 1)
    return x * (1 - wet) + y * wet * 1.6


# ----------------------------------------------------------------- instrumentos
def piano(freq, dur=3.5, vel=0.6):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.zeros(n, np.float32)
    B = 0.0004
    for k in range(1, 9):
        fk = freq * k * np.sqrt(1 + B * k * k)
        if fk > 12000: break
        dec = 1.2 + 2.2 / k
        x += (0.7 ** (k - 1)) * np.sin(2 * np.pi * fk * t + rng.uniform(0, 6)) * np.exp(-t * (1.0 / dec) * (1 + k * 0.35))
    att = np.minimum(1, t / 0.004)
    ham = rng.normal(0, 1, n) * np.exp(-t * 90) * 0.15
    x = (x * att + lp(ham, freq * 4)) * vel
    x *= env(n, 0.002, 0.25)
    return x.astype(np.float32)


def strings(freqs, dur, attack=1.5, release=1.5, bright=2200, voices=6):
    n = int(dur * SR); t = np.arange(n) / SR
    out = np.zeros((n, 2), np.float32)
    for f in freqs:
        for v in range(voices):
            det = f * (1 + rng.uniform(-0.006, 0.006))
            vib = 1 + 0.003 * np.sin(2 * np.pi * rng.uniform(4.5, 5.5) * t + rng.uniform(0, 6))
            ph = np.cumsum(2 * np.pi * det * vib / SR)
            saw = 2 * ((ph / (2 * np.pi)) % 1) - 1
            pan = rng.uniform(-0.7, 0.7)
            out[:, 0] += saw * (1 - pan) * 0.5; out[:, 1] += saw * (1 + pan) * 0.5
    out = lp(out, bright, 3)
    out *= env(n, attack, release)[:, None]
    return out / (len(freqs) * voices) * 2.2


def sub_boom(dur=3.0, f0=70, f1=28, noise=0.6):
    n = int(dur * SR); t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t * 3)
    ph = np.cumsum(2 * np.pi * f / SR)
    x = np.sin(ph) * np.exp(-t * 1.1)
    nz = lp(rng.normal(0, 1, n), 900) * np.exp(-t * 7) * noise
    crack = hp(rng.normal(0, 1, n), 2000) * np.exp(-t * 40) * 0.3
    return (x + nz + crack).astype(np.float32)


def braam(freq, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.zeros((n, 2), np.float32)
    for mult, g in ((1, 1.0), (2, 0.5), (1.5, 0.35), (0.5, 0.7)):
        for v in range(4):
            ph = np.cumsum(2 * np.pi * freq * mult * (1 + rng.uniform(-0.004, 0.004)) / SR * np.ones(n))
            saw = 2 * ((ph / (2 * np.pi)) % 1) - 1
            x[:, v % 2] += saw * g
    cutoff_env = np.exp(-t * 1.2)
    x = lp(x, 900, 2) * (0.4 + 0.6 * cutoff_env[:, None])
    x = np.tanh(x * 0.8)
    return x * env(n, 0.01, 1.2)[:, None] * 0.35


def heartbeat():
    def thump(f, d, g):
        n = int(d * SR); t = np.arange(n) / SR
        return (np.sin(2 * np.pi * (f + 30 * np.exp(-t * 30)) * t) * np.exp(-t * 14) * g).astype(np.float32)
    x = np.zeros(int(0.9 * SR), np.float32)
    a = thump(52, 0.35, 1.0); b = thump(46, 0.35, 0.7)
    x[:len(a)] += a; x[int(0.33 * SR):int(0.33 * SR) + len(b)] += b
    return lp(x, 180)


def blip(f, d=0.06, g=0.3):
    n = int(d * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) * np.exp(-t * 60) * g).astype(np.float32)


def noise_bed(dur, lo, hi, g):
    n = int(dur * SR)
    return bp(rng.normal(0, 1, (n, 2)).astype(np.float32), lo, hi) * g


# ----------------------------------------------------------------- composición
mus = buf()     # música (se reduce bajo la voz)
sfx = buf()     # efectos

# ESCENA 1 — gancho: impacto + braam + ambiente futurista
place(sfx, sub_boom(4.0, 80, 30, 0.8), 0.0, 1.0)
place(mus, braam(midi(26), 3.4), 0.0, 0.9)
amb = noise_bed(3.6, 200, 2500, 0.05) * env(int(3.6 * SR), 0.05, 0.6)[:, None]
place(sfx, amb, 0.0)
hum = np.sin(2 * np.pi * 55 * t_all[:int(3.6 * SR)]) * 0.05 * env(int(3.6 * SR), 0.05, 0.5)
place(sfx, hum.astype(np.float32), 0.0)
for k in range(4):  # tics de cuenta regresiva
    place(sfx, blip(1760, 0.05, 0.12), k * 1.0 + 0.02, pan=0.2)
# (3.25–4.0: silencio breve tras la frase)

# ESCENA 2 — pulsos electrónicos, zumbidos, música que empieza a crecer
place(sfx, sub_boom(2.5, 60, 30, 0.3), 4.0, 0.55)
for k in range(20):
    tt = 4.0 + k * 0.25
    place(sfx, blip(880 if k % 4 else 1320, 0.05, 0.08 + 0.004 * k), tt, pan=(-0.4 if k % 2 else 0.4))
place(sfx, (np.sin(2 * np.pi * 110 * t_all[:5 * SR]) * 0.025 * np.sin(2 * np.pi * 0.5 * t_all[:5 * SR]) ** 2).astype(np.float32), 4.0)
place(mus, strings([midi(38), midi(45), midi(50)], 5.4, attack=3.5, release=0.6, bright=900), 4.0, 0.8)

# ESCENA 3 — recuerdos: piano emocional
chords = [[50, 53, 57], [46, 50, 53], [53, 57, 60], [48, 52, 55]]  # Dm Bb F C
for i, ch in enumerate(chords):
    t0 = 9.0 + i * 1.25
    place(mus, piano(midi(ch[0] - 12), 3.0, 0.45), t0, pan=-0.2)
    for j, m in enumerate([ch[0], ch[1], ch[2], ch[1] + 12]):
        place(mus, piano(midi(m + 12), 2.5, 0.28), t0 + j * 0.31, pan=0.25 - j * 0.12)
place(mus, strings([midi(50), midi(57)], 5.4, attack=1.5, release=1.2, bright=1400), 9.0, 0.55)
place(sfx, noise_bed(1.25, 1500, 9000, 0.06) * env(int(1.25 * SR), 0.05, 0.1)[:, None], 10.25)   # lluvia

# ESCENA 4 — la pregunta: tensión creciente y pausa dramática
place(mus, strings([midi(38), midi(50), midi(53), midi(57)], 4.7, attack=2.0, release=0.25, bright=1800), 14.0, 0.9)
for k in range(18):
    place(sfx, blip(660, 0.05, 0.05 + 0.004 * k), 14.0 + k * 0.25, pan=(-0.3 if k % 2 else 0.3))
for i, m in enumerate([62, 65, 69, 74]):
    place(mus, piano(midi(m), 2.5, 0.25), 14.6 + i * 0.95)
# 18.7–19.0: silencio

# ESCENA 5 — el giro: frío a cálido, la música se detiene, latido aislado
place(mus, strings([midi(41), midi(48), midi(53), midi(57)], 3.9, attack=1.2, release=0.8, bright=1300), 19.0, 0.7)
place(mus, piano(midi(65), 3.0, 0.3), 19.9)
place(mus, piano(midi(69), 3.0, 0.25), 21.1)
place(sfx, heartbeat(), 23.25, 1.3)
# 22.9–24.95: silencio musical (solo latido + voz)

# ESCENA 6 — la revelación: orquesta emocional en ascenso
prog = [([46, 53, 58, 62], 25.0), ([41, 53, 57, 60], 26.5), ([48, 55, 60, 64], 28.0), ([38, 50, 57, 62, 65], 29.5)]
for i, (ch, t0) in enumerate(prog):
    g = 0.55 + 0.18 * i
    place(mus, strings([midi(m) for m in ch], 1.9, attack=0.5 if i else 1.0, release=0.5, bright=1600 + 500 * i), t0 - 0.2, g)
    place(mus, strings([midi(ch[0] - 12)], 1.9, attack=0.4, release=0.5, bright=500), t0 - 0.2, g * 0.8)
melody = [(74, 25.2), (72, 25.9), (70, 26.6), (69, 27.3), (72, 28.1), (74, 28.8), (77, 29.6), (76, 30.3)]
for m, t0 in melody:
    place(mus, piano(midi(m), 2.0, 0.33), t0, pan=0.15)
roll = np.zeros(int(1.0 * SR), np.float32)
for k in range(24):
    b = sub_boom(0.4, 90, 60, 0.4) * (0.2 + 0.8 * k / 24) * 0.25
    i0 = int(k * SR / 24); roll[i0:i0 + len(b)] += b[:len(roll) - i0]
place(sfx, roll, 30.0)

# ESCENA 7 — el mensaje final: gran crescendo + transmisión profunda
place(sfx, sub_boom(5.0, 90, 26, 1.0), 31.0, 1.1)
place(mus, braam(midi(26), 4.5), 31.0, 0.7)
place(mus, strings([midi(m) for m in [38, 50, 57, 62, 65, 69, 74]], 5.0, attack=0.05, release=2.5, bright=4200), 31.0, 1.0)
n = int(4.8 * SR); tt = np.arange(n) / SR
whine = np.sin(2 * np.pi * np.cumsum(300 + 900 * (1 - np.exp(-tt * 0.8))) / SR) * 0.04 * np.exp(-tt * 0.4)
trans = (np.sin(2 * np.pi * 36 * tt) * 0.35 + whine) * env(n, 0.02, 2.0)
place(sfx, trans.astype(np.float32), 31.05)
for k in range(30):  # ráfagas de datos de la transmisión
    place(sfx, blip(rng.choice([2200, 2640, 3300]), 0.03, 0.05 * np.exp(-k / 18)), 31.1 + k * 0.07, pan=rng.uniform(-0.6, 0.6))
place(mus, piano(midi(62), 4.0, 0.35), 32.3)
place(mus, piano(midi(69), 4.0, 0.3), 33.5)

# ESCENA 8 — cierre: última nota de piano y silencio
place(mus, piano(midi(50), 3.0, 0.22), 36.25)
place(mus, piano(midi(74), 3.0, 0.5), 39.25)
place(mus, piano(midi(62), 3.0, 0.3), 39.25)

# ----------------------------------------------------------------- mezcla
mus = reverb(mus, 3.2, 0.35)
sfx = reverb(sfx, 2.0, 0.18, 2500)

w = wave.open(f"{BUILD}/voz.wav"); v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
v = v[:N]; v = np.pad(v, (0, N - len(v)))
voice = np.stack([v, v], 1)
voice = voice * 0.92 + reverb(voice, 1.4, 0.12, 4000) * 0.15
# ducking: envolvente de voz suavizada
e = np.sqrt(np.convolve(v ** 2, np.ones(4800) / 4800, "same"))
e = np.clip(e / 0.05, 0, 1)
k = np.exp(-np.arange(int(0.25 * SR)) / (0.08 * SR)); k /= k.sum()
e = np.convolve(e, k, "same")
duck = 1 - 0.55 * e
mix = mus * 0.55 * duck[:, None] + sfx * 0.75 * (1 - 0.3 * e[:, None]) + voice * 1.0
# silencios marcados por el guion
def gate(a, b, fade=0.08):
    i0, i1 = int(a * SR), int(b * SR); f = int(fade * SR)
    g = np.ones(N, np.float32); g[i0:i1] = 0
    g[i0 - f:i0] = np.linspace(1, 0, f); g[i1:i1 + f] = np.linspace(0, 1, f)
    return g
mus_sfx_gate = gate(3.35, 3.98) * gate(18.75, 18.98)
mix = mus * 0.55 * duck[:, None] * mus_sfx_gate[:, None] * gate(22.9, 24.95, 0.5)[:, None] \
    + sfx * 0.75 * (1 - 0.3 * e[:, None]) * mus_sfx_gate[:, None] + voice
# fundido final a silencio
fo = int(0.5 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 2
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
mix = mix / np.abs(mix).max() * 0.95
out = wave.open(f"{BUILD}/mezcla.wav", "wb"); out.setnchannels(2); out.setsampwidth(2); out.setframerate(SR)
out.writeframes((mix * 32767).astype(np.int16).tobytes()); out.close()
print("ok")
