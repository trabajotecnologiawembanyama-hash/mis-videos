"""Exporta los subtítulos sincronizados (SRT por frases cortas y SRT palabra a palabra)."""
import json, sys
sys.argv += []
import render  # reutiliza la segmentación exacta usada en pantalla
def ts(x):
    ms = int(round(x * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
out = sys.argv[1]
with open(f"{out}/subtitulos.srt", "w") as fh:
    for i, c in enumerate(render.CHUNKS, 1):
        fh.write(f"{i}\n{ts(c['t0'])} --> {ts(c['t1'])}\n{' '.join(w['w'] for w in c['words']).upper()}\n\n")
with open(f"{out}/subtitulos_palabra_a_palabra.srt", "w") as fh:
    k = 1
    for ln in render.SUBS:
        for w in ln["words"]:
            fh.write(f"{k}\n{ts(w['t0'])} --> {ts(w['t1'])}\n{w['w']}\n\n"); k += 1
json.dump(render.SUBS, open(f"{out}/tiempos_voz.json", "w"), ensure_ascii=False, indent=1)
