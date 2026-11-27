"""Randomization tests for saliency maps on PneumoniaMNIST (after Adebayo et al., 2018).

For each of the 5 trained models and 200 test images, four maps are computed:
vanilla gradient, Integrated Gradients, Guided Backprop and Grad-CAM (layer4).
Then the maps are recomputed
  * after re-initialising the network layer by layer, from the output to the input (cascading randomization),
  * on a model of the same seed trained on shuffled labels,
  * on a second model trained with a different seed (how much two equally good models agree),
and compared with the originals (Spearman rank correlation and SSIM of the absolute maps).
Every map is also compared with the edges of the image (Sobel), the thing a map can show without any model.

Writes results/sanity.json (and the example maps to RUNS, outside the website).
"""
import json, os, copy
import numpy as np, torch, torch.nn as nn
from scipy.stats import spearmanr
from scipy.ndimage import sobel
from skimage.metrics import structural_similarity as ssim
from train import load, model, norm, RUNS, HERE, DEV

N_IMG, SEEDS, SHUFFLED = 200, [0, 1, 2, 3, 4], [0, 1, 2]
CASCADE = ["fc", "layer4", "layer3", "layer2", "layer1", "conv1"]  # conv1 includes bn1
METHODS = ["Gradient", "Integrated Gradients", "Guided Backprop", "Grad-CAM"]


def net(tag):
    m = model()
    m.load_state_dict(torch.load(f"{RUNS}/{tag}.pt", map_location="cpu"))
    for mod in m.modules():
        if isinstance(mod, nn.ReLU): mod.inplace = False
    return m.to(DEV).eval()


def reinit(m, upto, seed):
    """Re-initialise the blocks in CASCADE[:upto] with PyTorch's default initialisation."""
    m = copy.deepcopy(m); torch.manual_seed(seed)
    for name in CASCADE[:upto]:
        mods = [getattr(m, name)] + ([m.bn1] if name == "conv1" else [])
        for block in mods:
            for mod in block.modules():
                if hasattr(mod, "reset_parameters"): mod.reset_parameters()
                if hasattr(mod, "reset_running_stats"): mod.reset_running_stats()
    return m.eval()


def gradient(m, x, t):
    x = x.clone().requires_grad_(True)
    m(norm(x)).gather(1, t[:, None]).sum().backward()
    return x.grad.detach()


def integrated(m, x, t, steps=32):
    total = torch.zeros_like(x)
    for a in (torch.arange(steps, device=x.device) + 0.5) / steps:  # baseline: black image
        total += gradient(m, a * x, t)
    return (x * total / steps).detach()


def guided(m, x, t):
    hooks = [mod.register_full_backward_hook(lambda mod, gi, go: (gi[0].clamp(min=0),))
             for mod in m.modules() if isinstance(mod, nn.ReLU)]
    try:
        return gradient(m, x, t)
    finally:
        for h in hooks: h.remove()


def gradcam(m, x, t):
    store = {}
    h = m.layer4.register_forward_hook(lambda mod, i, o: store.__setitem__("a", o))
    try:
        out = m(norm(x)).gather(1, t[:, None]).sum()
        a = store["a"]; g, = torch.autograd.grad(out, a)
        cam = torch.relu((g.mean((2, 3), keepdim=True) * a).sum(1, keepdim=True))
        return nn.functional.interpolate(cam, size=x.shape[-2:], mode="bilinear", align_corners=False).detach()
    finally:
        h.remove()


FUN = dict(zip(METHODS, [gradient, integrated, guided, gradcam]))


def maps(m, x, t, bs=50):
    out = {}
    for k, f in FUN.items():
        out[k] = torch.cat([f(m, x[i:i + bs], t[i:i + bs]).abs().sum(1).cpu() for i in range(0, len(x), bs)]).numpy()
    return out


def sim(a, b):
    """Spearman and SSIM per image, on maps scaled to [0, 1]."""
    rs, ss = [], []
    for u, v in zip(a, b):
        flat = np.ptp(u) == 0 or np.ptp(v) == 0  # an all-zero map has no ranking; counted as 0 and reported
        rs.append(np.nan if flat else spearmanr(u.ravel(), v.ravel())[0])
        u = (u - u.min()) / (np.ptp(u) + 1e-12); v = (v - v.min()) / (np.ptp(v) + 1e-12)
        ss.append(ssim(u, v, data_range=1.0))
    rs = np.array(rs)
    return rs, np.array(ss)


def main():
    xte, yte = load(128)["test"]
    rng = np.random.default_rng(0)
    idx = np.sort(np.concatenate([rng.choice(np.where(yte == c)[0], N_IMG // 2, replace=False) for c in (0, 1)]))
    x = xte[idx].to(DEV); y = yte[idx]
    edges = np.stack([np.hypot(sobel(i[0], 0), sobel(i[0], 1)) for i in xte[idx].numpy()])
    R = {"images": idx.tolist(), "labels": y.tolist(), "cascade": CASCADE, "rows": []}
    ex = {"x": x[:8].cpu().numpy()[:, 0], "y": y[:8].numpy()}

    def add(kind, seed, step, mk, a, b):
        r, s = sim(a, b)
        R["rows"].append(dict(kind=kind, seed=seed, step=step, method=mk, flat=int(np.isnan(r).sum()),
                              spearman=np.nan_to_num(r).tolist(), ssim=s.tolist()))

    base = {}
    for s in SEEDS:
        m = net(f"real_s{s}")
        with torch.no_grad(): t = m(norm(x)).argmax(1)  # explain the class the trained model predicts
        orig = maps(m, x, t); base[s] = (orig, t)
        for k in METHODS: add("edges", s, "trained", k, orig[k], edges)
        if s == 0:
            for k in METHODS: ex[f"trained|{k}"] = orig[k][:8]
        for j in range(1, len(CASCADE) + 1):
            mj = reinit(m, j, 100 * s + j); rand = maps(mj, x, t)
            for k in METHODS:
                add("cascade", s, CASCADE[j - 1], k, orig[k], rand[k])
                if j == len(CASCADE): add("edges", s, "random", k, rand[k], edges)
                if s == 0: ex[f"{CASCADE[j-1]}|{k}"] = rand[k][:8]
        print("cascade done", s, flush=True)
    for s in SEEDS:  # a different, equally trained model
        o = SEEDS[(SEEDS.index(s) + 1) % len(SEEDS)]
        other = maps(net(f"real_s{o}"), x, base[s][1])
        for k in METHODS: add("other_seed", s, f"s{o}", k, base[s][0][k], other[k])
    for s in SHUFFLED:
        sh = maps(net(f"shuffled_s{s}"), x, base[s][1])
        for k in METHODS: add("shuffled", s, "shuffled", k, base[s][0][k], sh[k])
        if s == 0:
            for k in METHODS: ex[f"shuffled|{k}"] = sh[k][:8]
    ex["edges"] = edges[:8]
    json.dump(R, open(f"{HERE}/results/sanity.json", "w"))
    np.savez_compressed(f"{RUNS}/examples.npz", **ex)  # 13 MB, kept out of the website
    print("saved")


if __name__ == "__main__":
    main()
