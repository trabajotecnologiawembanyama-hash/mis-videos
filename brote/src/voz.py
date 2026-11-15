"""Narrador único de Brote: Piper (voz neuronal masculina, fonética es-419) con alineación por fonema.
Uso: voz.py <guion.txt> <salida_dir> [length_scale]"""
import json, re, subprocess, sys, wave, os
import numpy as np
from piper import PiperVoice, SynthesisConfig

VOICE = "/tmp/claude-0/tts/voice-es-carlfm-x-low"
src, out = sys.argv[1], sys.argv[2]
ls = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
tempo = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
gap_base = float(sys.argv[5]) if len(sys.argv) > 5 else 0.45
os.makedirs(out, exist_ok=True)
text = open(src).read().strip()
v = PiperVoice.load(f"{VOICE}/carlfm_align.onnx", config_path=f"{VOICE}/latam.json")
cfg = SynthesisConfig(length_scale=ls, noise_scale=0.55, noise_w_scale=0.6)
SR0 = 16000

# frases (se respetan las comillas en pantalla; se quitan para hablar)
sents = re.findall(r"[^.!?]+[.!?»]+(?:»)?", text)
sents = [s.strip() for s in sents if s.strip()]
audio, words, t = [], [], 0.25
audio.append(np.zeros(int(0.25 * SR0), np.float32))
for si, s in enumerate(sents):
    spoken = s.replace("«", "").replace("»", "")
    chunks = list(v.synthesize(spoken, syn_config=cfg, include_alignments=True))
    x = np.concatenate([c.audio_float_array for c in chunks])
    al = [a for c in chunks for a in (c.phoneme_alignments or [])]
    # grupos de fonemas por palabra (separados por espacio)
    groups, cur, pos = [], None, 0
    for a in al:
        if a.phoneme in ("^", "$", "_"):
            pos += a.num_samples; continue
        if a.phoneme == " " or a.phoneme in ",.;:?!":
            if cur is not None: groups.append(cur); cur = None
            pos += a.num_samples; continue
        if cur is None: cur = [pos, pos]
        pos += a.num_samples; cur[1] = pos
    if cur is not None: groups.append(cur)
    disp = s.split()
    if len(groups) != len(disp):
        print(f"aviso: frase {si} {len(groups)} grupos vs {len(disp)} palabras -> proporcional")
        a0, a1 = (groups[0][0], groups[-1][1]) if groups else (0, len(x))
        L = np.array([len(w) + 1 for w in disp], float); c = np.concatenate([[0], np.cumsum(L)]) / L.sum()
        groups = [[a0 + c[k] * (a1 - a0), a0 + c[k + 1] * (a1 - a0)] for k in range(len(disp))]
    for w, (g0, g1) in zip(disp, groups):
        words.append({"w": w, "t0": round(t + g0 / SR0, 3), "t1": round(t + g1 / SR0, 3), "s": si})
    audio.append(x)
    t += len(x) / SR0
    gap = gap_base
    if si == len(sents) - 2: gap = gap_base + 0.4          # pausa antes del gancho final
    audio.append(np.zeros(int(gap * SR0), np.float32)); t += gap
x = np.concatenate(audio)
for wd in words: wd["t0"] = round(wd["t0"] / tempo, 3); wd["t1"] = round(wd["t1"] / tempo, 3)
t = t / tempo
raw = f"{out}/voz_raw.wav"
w = wave.open(raw, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR0)
w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
# voz cálida y cercana: sin cambio de tono, graves suaves, presencia, compresión ligera
af = (f"atempo={tempo},aresample=48000:resampler=soxr,highpass=f=75,equalizer=f=180:t=q:w=1:g=3,equalizer=f=2800:t=q:w=1.2:g=2,"
      "equalizer=f=6500:t=q:w=1:g=-2.5,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=150,"
      "aecho=0.8:0.5:28:0.10,loudnorm=I=-16:TP=-1.5")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", af, "-ac", "1", "-ar", "48000", f"{out}/voz.wav"], check=True)
json.dump({"duration": round(t, 3), "sentences": sents, "words": words}, open(f"{out}/palabras.json", "w"), ensure_ascii=False, indent=1)
print(f"duración {t:.2f}s, {len(words)} palabras")
for si, s in enumerate(sents):
    ws = [x for x in words if x["s"] == si]
    print(f"{ws[0]['t0']:6.2f}-{ws[-1]['t1']:6.2f}  {s}")
