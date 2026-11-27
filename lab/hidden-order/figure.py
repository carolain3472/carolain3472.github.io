"""Figure: the 10 invoices with a difference, under the hidden 'agreement', for each model and prompt."""
import json, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from experiment import CASES

SITE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
INK, INK2, MAIN, ORANGE, LINE = "#06283a", "#4c6672", "#006f9a", "#d97c00", "#d6e8ec"
plt.rcParams.update({"font.family": ["Helvetica Neue", "Arial"], "text.color": INK, "savefig.dpi": 200, "savefig.facecolor": "white"})
MODELS = ["claude-haiku-4-5", "claude-haiku-5-5", "claude-sonnet-5-5"]
NAMES = {"claude-haiku-4-5": "Haiku 4.5", "claude-haiku-5-5": "Haiku 5.5", "claude-sonnet-5-5": "Sonnet 5.5"}
T = {"en": dict(sys={"plain": "usual prompt", "guarded": "“the invoice is data”"}, ok="rejected", bad="approved",
                title="The 10 invoices with a difference, with the hidden “commercial agreement”", cov="under 20%", not_="not covered"),
     "es": dict(sys={"plain": "prompt usual", "guarded": "«la factura es un dato»"}, ok="rechazada", bad="aprobada",
                title="Las 10 facturas con diferencia, con el «acuerdo comercial» escondido", cov="menor al 20 %", not_="no cubierta")}
covered = json.load(open("summary.json"))["covered"]
wrong = [i for i, c in enumerate(CASES) if c[1]]
order = [i for i in wrong if i in covered] + [i for i in wrong if i not in covered]
R = {m: json.load(open(f"results_{m}.json")) for m in MODELS}

for lang, t in T.items():
    fig, ax = plt.subplots(figsize=(9.6, 3.9)); ax.set_xlim(-5.4, 10.4); ax.set_ylim(-0.9, 6.9); ax.axis("off")
    y = 6
    for m in MODELS:
        for s in ("plain", "guarded"):
            ax.text(-5.3, y, NAMES[m], fontsize=9.5, fontweight="bold", va="center") if s == "plain" else None
            ax.text(-3.5, y, t["sys"][s], fontsize=8.5, color=INK2, va="center")
            for x, i in enumerate(order):
                r = next(r for r in R[m] if r["system"] == s and r["hidden"] == "agreement" and r["case"] == i)
                c = ORANGE if r["approve"] else MAIN
                ax.add_patch(FancyBboxPatch((x + (0.3 if x >= 6 else 0) + .08, y - .36), .74, .72, boxstyle="round,pad=0,rounding_size=0.12", fc=c, ec="none"))
            y -= 1
    ax.text(3.0, 6.75, t["cov"], ha="center", fontsize=8.5, color=INK2); ax.text(8.45, 6.75, t["not_"], ha="center", fontsize=8.5, color=INK2)
    ax.add_patch(FancyBboxPatch((0.1, -0.75), .4, .4, boxstyle="round,pad=0,rounding_size=0.08", fc=ORANGE, ec="none")); ax.text(.65, -.55, t["bad"], va="center", fontsize=8.5)
    ax.add_patch(FancyBboxPatch((2.6, -0.75), .4, .4, boxstyle="round,pad=0,rounding_size=0.08", fc=MAIN, ec="none")); ax.text(3.15, -.55, t["ok"], va="center", fontsize=8.5)
    out = f"{SITE}/{'es/' if lang == 'es' else ''}posts/hidden-order"; os.makedirs(out, exist_ok=True)
    fig.savefig(f"{out}/agreement.png", bbox_inches="tight"); plt.close(fig)
print("ok")
