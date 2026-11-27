"""Calibration of the 5 PneumoniaMNIST models, before and after temperature scaling (Guo et al., 2017).

The temperature is fitted on the validation set (128 px). It is then evaluated on
  * the test set at 128 px, the same acquisition as training,
  * the same test patients stored at 64 px and at 28 px, upsampled back to 128 px (a blurrier acquisition).
Note: the share of pneumonia is 74% in train and validation but 62.5% in test, so the test set already
differs from the data the temperature was fitted on.

Writes results/calibration.json.
"""
import json
import numpy as np, torch, torch.nn.functional as F
from train import load, model, logits, RUNS, HERE, DEV
from sklearn_free import auc

SEEDS, BINS, BOOT = [0, 1, 2, 3, 4], 15, 1000


def net(tag):
    m = model(); m.load_state_dict(torch.load(f"{RUNS}/{tag}.pt", map_location="cpu")); return m.to(DEV).eval()


def fit_temperature(z, y):
    logt = torch.zeros(1, requires_grad=True)
    opt = torch.optim.LBFGS([logt], lr=0.1, max_iter=200)
    def step():
        opt.zero_grad(); loss = F.cross_entropy(z / logt.exp(), y); loss.backward(); return loss
    opt.step(step)
    return float(logt.exp())


def ece(conf, correct, bins=BINS):
    e = 0.0; edges = np.linspace(0, 1, bins + 1)
    for lo, hi in zip(edges[:-1], edges[1:]):
        k = (conf > lo) & (conf <= hi)
        if k.any(): e += k.mean() * abs(correct[k].mean() - conf[k].mean())
    return float(e)


def reliability(conf, correct, bins=10):
    edges = np.linspace(0.5, 1, bins + 1); out = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        k = (conf > lo) & (conf <= hi)
        if k.any(): out.append(dict(lo=float(lo), hi=float(hi), n=int(k.sum()), conf=float(conf[k].mean()), acc=float(correct[k].mean())))
    return out


def scores(z, y, T):
    p = (z / T).softmax(1).numpy(); y = y.numpy()
    conf = p.max(1); correct = (p.argmax(1) == y).astype(float)
    nll = float(F.cross_entropy(z / T, torch.tensor(y)))
    rng = np.random.default_rng(0); n = len(y)
    boot = [ece(conf[i], correct[i]) for i in (rng.integers(0, n, n) for _ in range(BOOT))]
    return dict(ece=ece(conf, correct), ece_ci=[float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))],
                acc=float(correct.mean()), mean_conf=float(conf.mean()), nll=nll,
                brier=float(((p[:, 1] - y) ** 2).mean()), auc=auc(y, p[:, 1]),
                overconfident_wrong=int(((conf > 0.95) & (correct == 0)).sum()), n=int(n),
                reliability=reliability(conf, correct))


def main():
    d = load(128); xte, yte = d["test"]
    shifted = {}
    for s in (64, 28):
        x = load(s)["test"][0]
        shifted[f"{s}px"] = F.interpolate(x, size=128, mode="bilinear", align_corners=False)
    out = {"bins": BINS, "boot": BOOT, "prevalence": {k: float(d[k][1].float().mean()) for k in d}, "models": []}
    for s in SEEDS:
        m = net(f"real_s{s}")
        T = fit_temperature(logits(m, d["val"][0]), d["val"][1])
        row = {"seed": s, "T": T, "sets": {}}
        for name, x in [("128px", xte)] + list(shifted.items()):
            z = logits(m, x)
            row["sets"][name] = {"before": scores(z, yte, 1.0), "after": scores(z, yte, T)}
        out["models"].append(row)
        print(s, round(T, 3), {k: (round(v["before"]["ece"], 3), round(v["after"]["ece"], 3), round(v["before"]["acc"], 3)) for k, v in row["sets"].items()}, flush=True)
    json.dump(out, open(f"{HERE}/results/calibration.json", "w"), indent=1)


if __name__ == "__main__":
    main()
