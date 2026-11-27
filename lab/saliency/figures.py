"""Figures for the two notes, in English and Spanish, in the site colours."""
import json, os
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from train import HERE, load

SITE = os.path.abspath(f"{HERE}/../..")
INK, INK2, MAIN, ORANGE, TURQ, GREY, LINE = "#06283a", "#4c6672", "#006f9a", "#d97c00", "#3fb8c0", "#a3b3ba", "#d6e8ec"
CMAP = LinearSegmentedColormap.from_list("ocean", ["#ffffff", "#9fd8e0", MAIN, INK])
plt.rcParams.update({"font.family": ["Helvetica Neue", "Arial", "DejaVu Sans"], "font.size": 10, "text.color": INK,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.edgecolor": LINE,
                     "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 200, "savefig.facecolor": "white"})
METHODS = ["Grad-CAM", "Gradient", "Integrated Gradients", "Guided Backprop"]
COL = {"Grad-CAM": MAIN, "Gradient": TURQ, "Integrated Gradients": GREY, "Guided Backprop": ORANGE}
T = {
 "en": dict(steps=["trained", "output\nlayer", "+ layer4", "+ layer3", "+ layer2", "+ layer1", "+ first\nconv"],
            sim="Similarity to the trained model's map\n(Spearman, 5 models × 200 images)",
            other="another good model", shuf="model trained on shuffled labels",
            rand="Randomized from the output towards the input",
            cols=["Trained", "Output layer\nrandom", "Up to layer3\nrandom", "All layers\nrandom", "Shuffled\nlabels"],
            img="X-ray", ece="Calibration error (ECE)", res=["128 px\n(as trained)", "64 px", "28 px"],
            pneu="Share called pneumonia", truth="real share", fix=["no correction", "temperature\nfrom validation", "prevalence\n+ temperature", "temperature from\nhalf of the test set"],
            conf="Confidence", acc="Share correct", before="before", after="after temperature", perfect="perfect calibration", empty="empty map\n(all zeros)", called="called pneumonia", meanconf="mean confidence"),
 "es": dict(steps=["entrenado", "capa de\nsalida", "+ layer4", "+ layer3", "+ layer2", "+ layer1", "+ primera\nconv"],
            sim="Parecido con el mapa del modelo entrenado\n(Spearman, 5 modelos × 200 imágenes)",
            other="otro modelo bueno", shuf="modelo entrenado con etiquetas revueltas",
            rand="Aleatorizado desde la salida hacia la entrada",
            cols=["Entrenado", "Capa de salida\nal azar", "Hasta layer3\nal azar", "Todas las capas\nal azar", "Etiquetas\nrevueltas"],
            img="Radiografía", ece="Error de calibración (ECE)", res=["128 px\n(como al entrenar)", "64 px", "28 px"],
            pneu="Proporción que llama neumonía", truth="proporción real", fix=["sin corrección", "temperatura\nde validación", "prevalencia\n+ temperatura", "temperatura con\nmitad de la prueba"],
            conf="Seguridad", acc="Proporción de aciertos", before="antes", after="con temperatura", perfect="calibración perfecta", empty="mapa vacío\n(todo en cero)", called="llamadas neumonía", meanconf="seguridad promedio"),
}
OUT = {"en": (f"{SITE}/posts/saliency-checks", f"{SITE}/posts/calibration-shift"),
       "es": (f"{SITE}/es/posts/saliency-checks", f"{SITE}/es/posts/calibration-shift")}


def cascade_fig(t, path):
    S = json.load(open(f"{HERE}/results/sanity_summary.json"))
    get = lambda kind, step, m: next(o for o in S if o["kind"] == kind and o["step"] == step and o["method"] == m)
    fig, axes = plt.subplots(1, 4, figsize=(11, 3.4), sharey=True)
    steps = ["fc", "layer4", "layer3", "layer2", "layer1", "conv1"]
    for ax, m in zip(axes, METHODS):
        ys = [1.0] + [get("cascade", s, m)["spearman"] for s in steps]
        ax.axhline(get("other_seed", "other_seed", m)["spearman"], color=INK, lw=1.2, ls=(0, (4, 3)))
        ax.axhline(get("shuffled", "shuffled", m)["spearman"], color=ORANGE, lw=1.6, ls=(0, (1, 2)))
        ax.axhline(0, color=LINE, lw=1)
        ax.plot(range(7), ys, color=MAIN, lw=2, marker="o", ms=5)
        ax.set_title(m, fontsize=11, fontweight="bold", color=INK, loc="left")
        ax.set_xticks(range(7)); ax.set_xticklabels([x.replace("\n", " ") for x in t["steps"]], fontsize=7.5, rotation=50, ha="right", rotation_mode="anchor")
        ax.set_ylim(-0.2, 1.05); ax.grid(axis="y", color=LINE, lw=0.6)
    axes[0].set_ylabel(t["sim"], fontsize=8.5)
    fig.text(0.5, -0.06, t["rand"], ha="center", color=INK2, fontsize=9)
    h = [plt.Line2D([], [], color=INK, ls=(0, (4, 3))), plt.Line2D([], [], color=ORANGE, ls=(0, (1, 2)))]
    fig.legend(h, [t["other"], t["shuf"]], loc="upper right", ncol=2, frameon=False, fontsize=9, bbox_to_anchor=(0.99, 1.06))
    fig.tight_layout(); fig.savefig(path, bbox_inches="tight"); plt.close(fig)


def maps_fig(t, path):
    E = np.load(os.path.expanduser("~/Desktop/portafolio/_lab_runs/saliency/examples.npz"))
    i = int(np.where(E["y"] == 1)[0][0])
    keys = ["trained", "fc", "layer3", "conv1", "shuffled"]
    fig, axes = plt.subplots(4, 6, figsize=(10, 7.2))
    for r, m in enumerate(METHODS):
        axes[r, 0].imshow(E["x"][i], cmap="gray"); axes[r, 0].set_ylabel(m, fontsize=9, fontweight="bold", color=INK, rotation=0, ha="right", va="center")
        for c, k in enumerate(keys):
            a = E[f"{k}|{m}"][i]; axes[r, c + 1].imshow(a / (a.max() + 1e-12), cmap=CMAP, vmin=0, vmax=1)
            if a.max() == 0: axes[r, c + 1].text(.5, .5, t["empty"], ha="center", va="center", color=INK2, fontsize=8.5, transform=axes[r, c + 1].transAxes)
    for c, lab in enumerate([t["img"]] + t["cols"]): axes[0, c].set_title(lab, fontsize=8.5, color=INK)
    for a in axes.ravel(): a.set_xticks([]); a.set_yticks([]); [s.set_visible(False) for s in a.spines.values()]
    fig.tight_layout(); fig.savefig(path, bbox_inches="tight"); plt.close(fig)


def calib_fig(t, path):
    C = json.load(open(f"{HERE}/results/calibration.json")); K = json.load(open(f"{HERE}/results/calibration_check.json"))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 3.6), gridspec_kw={"width_ratios": [1.25, 1]})
    keys = ["ece_none", "ece_val_T", "ece_prior", "ece_oracle_T"]
    for j, k in enumerate(keys):
        v = [m[k] for m in K["models"]]
        a1.scatter(np.full(5, j) + np.linspace(-.12, .12, 5), v, color=[GREY, ORANGE, TURQ, MAIN][j], s=34, zorder=3, edgecolor="white", lw=.8)
        a1.text(j, max(v) + .008, f"{np.mean(v):.3f}".replace(".", "," if t is T["es"] else "."), ha="center", fontsize=9, color=INK, fontweight="bold")
    a1.set_xticks(range(4)); a1.set_xticklabels(t["fix"], fontsize=8); a1.set_ylabel(t["ece"]); a1.set_ylim(0, .15); a1.grid(axis="y", color=LINE, lw=.6)
    a1.set_title("128 px", loc="left", fontweight="bold", fontsize=11)
    res = ["128px", "64px", "28px"]
    for j, r in enumerate(res):
        b = [m["sets"][r]["before"]["ece"] for m in C["models"]]; a = [m["sets"][r]["after"]["ece"] for m in C["models"]]
        a2.scatter(np.full(5, j) - .14 + np.linspace(-.05, .05, 5), b, color=GREY, s=30, edgecolor="white", lw=.8, zorder=3, label=t["before"] if j == 0 else None)
        a2.scatter(np.full(5, j) + .14 + np.linspace(-.05, .05, 5), a, color=ORANGE, s=30, edgecolor="white", lw=.8, zorder=3, label=t["after"] if j == 0 else None)
    a2.set_xticks(range(3)); a2.set_xticklabels(t["res"], fontsize=8.5); a2.set_ylabel(t["ece"]); a2.set_ylim(0, .4); a2.grid(axis="y", color=LINE, lw=.6)
    a2.legend(frameon=False, fontsize=8.5, loc="upper left")
    fig.tight_layout(); fig.savefig(path, bbox_inches="tight"); plt.close(fig)


def reliab_fig(t, path):
    C = json.load(open(f"{HERE}/results/calibration.json"))
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.5), sharey=True)
    for ax, r, lab in zip(axes, ["128px", "64px", "28px"], t["res"]):
        ax.plot([.5, 1], [.5, 1], color=LINE, lw=1.5); ax.text(.52, .55, t["perfect"], color=INK2, fontsize=7.5, rotation=36)
        for m in C["models"]:
            for k, c in (("before", GREY), ("after", ORANGE)):
                rel = [b for b in m["sets"][r][k]["reliability"] if b["n"] >= 10]
                ax.plot([b["conf"] for b in rel], [b["acc"] for b in rel], color=c, lw=1.2, alpha=.85, marker="o", ms=2.5)
        ax.set_title(lab.replace("\n", " "), loc="left", fontweight="bold", fontsize=10.5)
        ax.set_xlim(.5, 1.01); ax.set_ylim(0, 1.02); ax.set_xlabel(t["conf"]); ax.grid(color=LINE, lw=.5)
    axes[0].set_ylabel(t["acc"])
    h = [plt.Line2D([], [], color=GREY, marker="o", ms=3), plt.Line2D([], [], color=ORANGE, marker="o", ms=3)]
    fig.legend(h, [t["before"], t["after"]], loc="upper right", ncol=2, frameon=False, fontsize=8.5, bbox_to_anchor=(.99, 1.05))
    fig.tight_layout(); fig.savefig(path, bbox_inches="tight"); plt.close(fig)


def called_fig(t, path):
    import torch, torch.nn.functional as F
    from train import logits
    from calibration import net
    y = load(128)["test"][1]; real = float(y.float().mean())
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    for j, s in enumerate((128, 64, 28)):
        x = load(s)["test"][0]
        if s != 128: x = F.interpolate(x, size=128, mode="bilinear", align_corners=False)
        sh, cf = [], []
        for k in range(5):
            z = logits(net(f"real_s{k}"), x); sh.append(float((z.argmax(1) == 1).float().mean())); cf.append(float(z.softmax(1).max(1).values.mean()))
        ax.scatter(np.full(5, j) + np.linspace(-.1, .1, 5), sh, color=MAIN, s=36, edgecolor="white", lw=.8, zorder=3)
        dec = "," if t is T["es"] else "."
        ax.text(j, max(sh) + .035, f"{t['meanconf']} {np.mean(cf):.2f}".replace(".", dec), ha="center", fontsize=8.5, color=INK2)
    ax.axhline(real, color=ORANGE, lw=1.6, ls=(0, (4, 3))); ax.text(2.45, real - .055, t["truth"], color=ORANGE, fontsize=8.5, ha="right")
    ax.set_xticks(range(3)); ax.set_xticklabels(t["res"], fontsize=8.5); ax.set_ylim(.5, 1.08); ax.set_xlim(-.5, 2.5)
    ax.set_ylabel(t["pneu"]); ax.grid(axis="y", color=LINE, lw=.6)
    fig.tight_layout(); fig.savefig(path, bbox_inches="tight"); plt.close(fig)


def res_fig(t, path):
    imgs = [load(s)["test"][0][3, 0].numpy() for s in (128, 64, 28)]
    fig, axes = plt.subplots(1, 3, figsize=(7.5, 2.8))
    for ax, im, lab in zip(axes, imgs, t["res"]):
        ax.imshow(im, cmap="gray"); ax.set_title(lab.replace("\n", " "), fontsize=9, color=INK); ax.axis("off")
    fig.tight_layout(); fig.savefig(path, bbox_inches="tight"); plt.close(fig)


for lang, (p1, p2) in OUT.items():
    os.makedirs(p1, exist_ok=True); os.makedirs(p2, exist_ok=True); t = T[lang]
    cascade_fig(t, f"{p1}/cascade.png"); maps_fig(t, f"{p1}/maps.png")
    calib_fig(t, f"{p2}/ece.png"); called_fig(t, f"{p2}/called.png"); res_fig(t, f"{p2}/resolutions.png")
print("ok")
