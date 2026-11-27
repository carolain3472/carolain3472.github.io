"""Summary table of results/sanity.json: mean over seeds and images, with a 95% bootstrap interval over images."""
import json, numpy as np
from train import HERE

R = json.load(open(f"{HERE}/results/sanity.json"))
rng = np.random.default_rng(0)


def summary(rows, key):
    a = np.array([r[key] for r in rows])  # seeds x images
    m = a.mean()
    boot = [a[:, rng.integers(0, a.shape[1], a.shape[1])].mean() for _ in range(1000)]
    return round(float(m), 3), [round(float(np.percentile(boot, 2.5)), 3), round(float(np.percentile(boot, 97.5)), 3)]


out = []
groups = {}
for r in R["rows"]:
    step = r["step"] if r["kind"] in ("cascade", "edges") else r["kind"]
    groups.setdefault((r["kind"], step, r["method"]), []).append(r)
for (kind, step, method), rows in groups.items():
    sp, spci = summary(rows, "spearman"); ss, ssci = summary(rows, "ssim")
    out.append(dict(kind=kind, step=step, method=method, seeds=len(rows), spearman=sp, spearman_ci=spci,
                    ssim=ss, ssim_ci=ssci, flat=sum(r["flat"] for r in rows)))
json.dump(out, open(f"{HERE}/results/sanity_summary.json", "w"), indent=1)
for o in out:
    print(f"{o['kind']:10} {o['step']:9} {o['method']:21} rho {o['spearman']:.3f} {o['spearman_ci']}  ssim {o['ssim']:.3f} {o['ssim_ci']}  flat {o['flat']}")
