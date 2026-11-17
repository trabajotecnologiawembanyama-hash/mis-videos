"""Narrador de Brote con Fish Audio (voz 1: masculina joven, enérgica). Emoción por frase con puntuación, velocidad y volumen.
Uso: voz_fish.py <epXX> <salida_dir>   (la clave de API la inyecta el proxy del entorno)"""
import io, json, os, re, subprocess, sys, time, urllib.request
import numpy as np
import soundfile as sf

VOICE = "a335d470fff248e8890dce6550a2874b"
MODEL = os.environ.get("FISH_MODEL", "s2.1-pro-free")
EP, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
src = open(os.path.join(os.path.dirname(__file__), "voz_kokoro.py")).read()
ns = {}
exec(src[src.index("EMO = {"):src.index("k = Kokoro")], ns)
EMO, GUION = ns["EMO"], ns["GUION"]
GAP_K = float(os.environ.get("GAP_K", "1.6"))


def tts(text, speed, vol):
    body = json.dumps({"text": text, "reference_id": VOICE, "format": "wav", "sample_rate": 44100,
                       "prosody": {"speed": round(speed, 2), "volume": round(vol, 1)}, "normalize": True}).encode()
    for attempt in range(5):
        try:
            req = urllib.request.Request("https://api.fish.audio/v1/tts", data=body, method="POST",
                                         headers={"Authorization": "Bearer proxy-injected", "Content-Type": "application/json", "model": MODEL})
            data = urllib.request.urlopen(req, timeout=180).read()
            x, sr = sf.read(io.BytesIO(data))
            if x.ndim > 1: x = x.mean(1)
            return x.astype(np.float32), sr
        except Exception as e:
            print("reintento", attempt, e, flush=True); time.sleep(5 + attempt * 5)
    raise SystemExit("Fish Audio no respondió")


def syllables(w):
    w = re.sub(r"[^a-záéíóúüñ]", "", w.lower())
    return max(1, len(re.findall(r"[aeiouáéíóúü]+", w)))


SR = 48000
TARGET = float(os.environ.get("TARGET", "50.5"))
import hashlib
os.makedirs(f"{OUT}/cache", exist_ok=True)
segs_all = []
for si, (disp, spoken, emo) in enumerate(GUION[EP]):
    spd, semis, gain, gap = EMO[emo]
    speed = 1.0 + (spd - 1.0) * 0.8
    key = hashlib.md5(f"{VOICE}|{MODEL}|{spoken or disp}|{speed:.2f}|{gain * 0.6:.1f}".encode()).hexdigest()[:16]
    cf = f"{OUT}/cache/{key}.wav"
    if not os.path.exists(cf):
        x, sr = tts(spoken or disp, speed, gain * 0.6)
        tmp = f"{OUT}/tmp.wav"; sf.write(tmp, x, sr)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-ar", str(SR), "-ac", "1", cf], check=True)
        os.remove(tmp)
    y, _ = sf.read(cf); y = y.astype(np.float32)
    env = np.sqrt(np.convolve(y ** 2, np.ones(960) / 960, "same"))
    thr = 0.08 * env.max()
    on = np.where(env > thr)[0]
    y = y[max(0, on[0] - 480): on[-1] + 2400]; env = env[max(0, on[0] - 480): on[-1] + 2400]
    active = env > thr
    gaps, i = [], 0
    while i < len(active):
        if not active[i]:
            j = i
            while j < len(active) and not active[j]: j += 1
            if (j - i) / SR > 0.09 and i > 0 and j < len(active): gaps.append((i, j))
            i = j
        else: i += 1
    a0 = int(np.argmax(active)); a1 = len(active) - int(np.argmax(active[::-1]))
    phrases = re.split(r"(?<=[,;:])\s+", disp)
    if len(gaps) >= len(phrases) - 1 and len(phrases) > 1:
        gs = sorted(sorted(gaps, key=lambda g: g[1] - g[0], reverse=True)[:len(phrases) - 1])
        segs, s0 = [], a0
        for g in gs: segs.append((s0, g[0])); s0 = g[1]
        segs.append((s0, a1))
    else:
        phrases, segs = [disp], [(a0, a1)]
    rel = []
    for ph, (s0, s1) in zip(phrases, segs):
        ws = ph.split(); wt = np.array([syllables(w) + 0.35 for w in ws]); c = np.concatenate([[0], np.cumsum(wt)]) / wt.sum()
        for n, w in enumerate(ws):
            rel.append((w, (s0 + c[n] * (s1 - s0)) / SR, (s0 + c[n + 1] * (s1 - s0)) / SR))
    segs_all.append((y, rel, gap, emo, disp))
    print(f"{si:2d} {emo:9s} {len(y) / SR:5.2f}s {disp}", flush=True)
speech = sum(len(y) for y, *_ in segs_all) / SR
base = sum(g for _, _, g, _, _ in segs_all[:-1])
K = min(3.4, max(1.0, (TARGET - 0.3 - 0.5 - speech - 0.4) / base)) if "GAP_K" not in os.environ else GAP_K
print(f"voz {speech:.1f}s, pausas x{K:.2f}")
audio = [np.zeros(int(0.3 * SR), np.float32)]; t = 0.3; words = []
for si, (y, rel, gap, emo, disp) in enumerate(segs_all):
    for w, r0, r1 in rel:
        words.append({"w": w, "t0": round(t + r0, 3), "t1": round(t + r1, 3), "s": si, "emo": emo})
    g = gap * K + (0.5 if si == len(segs_all) - 2 else 0)
    audio += [y, np.zeros(int(g * SR), np.float32)]
    t += len(y) / SR + g
x = np.concatenate(audio); sf.write(f"{OUT}/voz_raw.wav", x, SR)
af = ("highpass=f=60,equalizer=f=160:t=q:w=1:g=0.8,acompressor=threshold=-24dB:ratio=1.8:attack=15:release=250,"
      "aecho=0.85:0.4:18|31:0.06|0.04,loudnorm=I=-16:TP=-1.5")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{OUT}/voz_raw.wav", "-af", af, "-ar", str(SR), "-ac", "1", f"{OUT}/voz.wav"], check=True)
json.dump({"duration": round(t, 3), "voice": f"fish {VOICE} {MODEL}", "words": words, "sentences": [g_[0] for g_ in GUION[EP]]},
          open(f"{OUT}/palabras.json", "w"), ensure_ascii=False, indent=1)
print(f"duración {t:.2f}s")
