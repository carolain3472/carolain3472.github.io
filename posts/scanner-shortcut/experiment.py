"""Can a classifier learn the scanner instead of the disease?

Toy experiment with simulated images. Needs only NumPy:
    python experiment.py
"""
import json
import numpy as np

SIZE = 32
N_TRAIN, N_TEST, N_SEEDS = 600, 1000, 10
yy, xx = np.mgrid[-1:1:SIZE * 1j, -1:1:SIZE * 1j]


def make_images(disease, scanner, rng, lesion=0.25, bias=0.12):
    """One simulated slice per subject."""
    n = len(disease)
    images = np.zeros((n, SIZE, SIZE))
    for i in range(n):
        # Anatomy: an ellipse whose size changes from person to person.
        a, b = rng.normal(0.80, 0.03), rng.normal(0.70, 0.03)
        brain = ((xx / a) ** 2 + (yy / b) ** 2 < 1).astype(float)
        # Disease: a faint dark spot whose position moves a little.
        cx, cy = rng.normal(0.30, 0.08), rng.normal(-0.20, 0.08)
        spot = np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * 0.12 ** 2))
        # Scanner: a smooth left-right change in brightness.
        shading = 1 + bias * (2 * scanner[i] - 1) * xx
        img = brain * (1 - lesion * disease[i] * spot) * shading
        img += rng.normal(0, 0.15, img.shape)
        # Intensity normalization, image by image.
        images[i] = (img - img.mean()) / img.std()
    return images.reshape(n, -1)


def sample(n, p, rng, **kw):
    """p = share of patients from scanner 1 (controls: 1 - p)."""
    disease = np.repeat([0, 1], n // 2)
    prob = np.where(disease == 1, p, 1 - p)
    scanner = (rng.random(n) < prob).astype(int)
    return make_images(disease, scanner, rng, **kw), disease, scanner


def fit_logistic(X, y, l2=300.0, steps=25):
    """L2-regularized logistic regression, Newton's method (dual form)."""
    mu, sd = X.mean(0), X.std(0) + 1e-9
    Z = (X - mu) / sd
    K = Z @ Z.T / l2 + 1.0            # + 1.0 is the intercept
    alpha = np.zeros(len(y))
    for _ in range(steps):
        f = K @ alpha
        q = 1 / (1 + np.exp(-f))
        w = np.maximum(q * (1 - q), 1e-6)
        z = f + (y - q) / w
        alpha = np.linalg.solve(K + np.diag(1 / w), z)
    return lambda Xn: ((Xn - mu) / sd) @ Z.T @ alpha / l2 + alpha.sum()


def auc(score, y):
    ranks = np.empty(len(score))
    ranks[np.argsort(score)] = np.arange(1, len(score) + 1)
    n1 = y.sum()
    n0 = len(y) - n1
    return (ranks[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def run(p, seed, **kw):
    rng = np.random.default_rng(seed)
    X, d, _ = sample(N_TRAIN, p, rng, **kw)
    model = fit_logistic(X, d)
    # New people, same mix of scanners as in training.
    Xi, di, si = sample(N_TEST, p, rng, **kw)
    # New people, scanner unrelated to disease.
    Xe, de, _ = sample(N_TEST, 0.5, rng, **kw)
    score = model(Xi)
    # Same people as above, but each scanner is scored on its own.
    within = np.mean([auc(score[si == k], di[si == k]) for k in (0, 1)])
    return dict(same_mix=auc(score, di), within=within,
                balanced=auc(model(Xe), de),
                scanner_only=auc(si + 1e-6 * rng.random(len(si)), di))


if __name__ == "__main__":
    out = {}
    for name, kw in [("real lesion", {}), ("no lesion", dict(lesion=0.0))]:
        print(f"\n{name}\n   p   same mix  within scanner  balanced  scanner label only")
        for p in (0.5, 0.6, 0.7, 0.8, 0.9):
            rows = [run(p, seed, **kw) for seed in range(N_SEEDS)]
            m = {k: float(np.mean([r[k] for r in rows])) for k in rows[0]}
            s = {k: float(np.std([r[k] for r in rows])) for k in rows[0]}
            out[f"{name}|{p}"] = dict(mean=m, sd=s)
            print(f"{p:5.1f}  {m['same_mix']:.3f}      {m['within']:.3f}"
                  f"          {m['balanced']:.3f}     {m['scanner_only']:.3f}")
    json.dump(out, open("results.json", "w"), indent=1)
