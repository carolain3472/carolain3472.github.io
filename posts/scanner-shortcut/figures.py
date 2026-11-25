"""Builds images.png and auc.svg from experiment.py and results.json (NumPy only)."""
import json, struct, zlib
import numpy as np
from experiment import make_images, SIZE

# --- example images
tiles = []
for d, s in [(0, 0), (1, 0), (0, 1), (1, 1)]:
    im = make_images(np.array([d]), np.array([s]), np.random.default_rng(3))
    tiles.append(im.reshape(SIZE, SIZE))
lo, hi = min(t.min() for t in tiles), max(t.max() for t in tiles)
k, gap = 6, 14
h = SIZE * k
canvas = np.full((h, 4 * h + 3 * gap), 255, np.uint8)
for i, t in enumerate(tiles):
    g = ((t - lo) / (hi - lo) * 255).astype(np.uint8)
    canvas[:, i * (h + gap):i * (h + gap) + h] = np.kron(g, np.ones((k, k), np.uint8))
raw = b"".join(b"\0" + r.tobytes() for r in canvas)
chunk = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d))
open("images.png", "wb").write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(
    ">IIBBBBB", canvas.shape[1], h, 8, 0, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))

# --- line chart
R = json.load(open("results.json"))
P = [0.5, 0.6, 0.7, 0.8, 0.9]
X = lambda p: 60 + (p - 0.5) / 0.4 * 420
Y = lambda v: 40 + (1 - v) / 0.5 * 260
o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 370" role="img" '
     'aria-label="AUC against share of patients from scanner 1" style="width:100%;height:auto;font-family:system-ui,sans-serif">',
     '<rect width="700" height="370" fill="#fcfcfb"/>',
     '<text x="20" y="22" font-size="13" fill="#52514e">AUC (mean of 10 runs)</text>']
for v in (0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
    o.append(f'<line x1="60" x2="480" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="#e4e3df"/>'
             f'<text x="50" y="{Y(v)+4:.1f}" font-size="12" text-anchor="end" fill="#52514e">{v:.1f}</text>')
for p in P:
    o.append(f'<text x="{X(p):.0f}" y="322" font-size="12" text-anchor="middle" fill="#52514e">{p:.0%}</text>')
o.append('<text x="270" y="350" font-size="13" text-anchor="middle" fill="#52514e">Patients that come from scanner 1</text>')
for key, color, l1, l2 in [("same_mix", "#2a78d6", "Same scanner mix", "as in training"),
                           ("balanced", "#eb6834", "Scanner unrelated", "to disease")]:
    v = [R[f"real lesion|{p}"]["mean"][key] for p in P]
    o.append(f'<polyline fill="none" stroke="{color}" stroke-width="2" points="' +
             " ".join(f"{X(p):.1f},{Y(a):.1f}" for p, a in zip(P, v)) + '"/>')
    for p, a in zip(P, v):
        o.append(f'<circle cx="{X(p):.1f}" cy="{Y(a):.1f}" r="5" fill="{color}" stroke="#fcfcfb" stroke-width="2">'
                 f'<title>{l1} {l2}, {p:.0%}: AUC {a:.2f}</title></circle>')
    o.append(f'<circle cx="502" cy="{Y(v[-1])-4:.1f}" r="4" fill="{color}"/>'
             f'<text x="514" y="{Y(v[-1]):.1f}" font-size="13" fill="#0b0b0b">{l1}'
             f'<tspan x="514" dy="17">{l2}</tspan><tspan x="514" dy="17" font-weight="600">AUC {v[-1]:.2f}</tspan></text>')
o.append('</svg>')
open("auc.svg", "w").write("\n".join(o))
