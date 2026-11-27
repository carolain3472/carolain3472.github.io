"""Train ResNet-18 on PneumoniaMNIST (128 px).

python train.py --seed 0                 # real labels, keeps the best epoch on validation AUC
python train.py --seed 0 --shuffle       # labels shuffled once, trained until it memorises them

Checkpoints go to RUNS (outside the website). Metrics go to results/.
"""
import argparse, json, os, time
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F
from torchvision.models import resnet18
from sklearn_free import auc

RUNS = os.path.expanduser("~/Desktop/portafolio/_lab_runs/saliency")
HERE = os.path.dirname(os.path.abspath(__file__))
DEV = "mps" if torch.backends.mps.is_available() else "cpu"


def load(size=128):
    name = "pneumoniamnist.npz" if size == 28 else f"pneumoniamnist_{size}.npz"
    z = np.load(os.path.expanduser(f"~/.medmnist/{name}"))
    out = {}
    for sp in ("train", "val", "test"):
        x = torch.tensor(z[f"{sp}_images"], dtype=torch.float32)[:, None] / 255.0
        y = torch.tensor(z[f"{sp}_labels"][:, 0], dtype=torch.long)
        out[sp] = (x, y)
    return out


def model():
    m = resnet18(weights=None, num_classes=2)
    m.conv1 = nn.Conv2d(1, 64, 7, 2, 3, bias=False)
    return m


def norm(x):
    return (x - 0.5) / 0.25


@torch.no_grad()
def logits(m, x, bs=256):
    m.eval()
    return torch.cat([m(norm(x[i:i + bs].to(DEV))).float().cpu() for i in range(0, len(x), bs)])


def evaluate(m, x, y):
    z = logits(m, x)
    p = z.softmax(1)[:, 1].numpy()
    return {"acc": float((z.argmax(1) == y).float().mean()), "auc": auc(y.numpy(), p)}


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--seed", type=int, default=0)
    a.add_argument("--shuffle", action="store_true")
    a.add_argument("--epochs", type=int, default=0)
    args = a.parse_args()
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    d = load(128)
    xtr, ytr = d["train"]
    if args.shuffle:
        ytr = ytr[torch.randperm(len(ytr), generator=torch.Generator().manual_seed(1000 + args.seed))]
    epochs = args.epochs or (60 if args.shuffle else 15)
    m = model().to(DEV)
    opt = torch.optim.Adam(m.parameters(), 1e-3)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, epochs)
    tag = f"{'shuffled' if args.shuffle else 'real'}_s{args.seed}"
    os.makedirs(RUNS, exist_ok=True); os.makedirs(f"{HERE}/results", exist_ok=True)
    best, log = -1, []
    for ep in range(epochs):
        m.train(); t = time.time(); perm = torch.randperm(len(xtr)); tot = 0
        for i in range(0, len(xtr), 64):
            idx = perm[i:i + 64]; xb = xtr[idx]
            if not args.shuffle:  # small random shifts, real labels only
                dx, dy = np.random.randint(-6, 7, 2)
                xb = torch.roll(xb, (int(dy), int(dx)), (2, 3))
            loss = F.cross_entropy(m(norm(xb.to(DEV))), ytr[idx].to(DEV))
            opt.zero_grad(); loss.backward(); opt.step(); tot += loss.item() * len(idx)
        sched.step()
        tr = evaluate(m, xtr, ytr); va = evaluate(m, *d["val"])
        log.append({"epoch": ep + 1, "loss": tot / len(xtr), "train_acc": tr["acc"], "val_auc": va["auc"], "val_acc": va["acc"], "sec": round(time.time() - t, 1)})
        print(tag, log[-1], flush=True)
        score = tr["acc"] if args.shuffle else va["auc"]
        if args.shuffle or score > best:
            best = score; torch.save(m.state_dict(), f"{RUNS}/{tag}.pt")
    m.load_state_dict(torch.load(f"{RUNS}/{tag}.pt"))
    res = {"tag": tag, "epochs": epochs, "log": log, "train": evaluate(m, xtr, ytr), "val": evaluate(m, *d["val"]), "test": evaluate(m, *d["test"])}
    json.dump(res, open(f"{HERE}/results/train_{tag}.json", "w"), indent=1)
    print("FINAL", tag, res["train"], res["test"])


if __name__ == "__main__":
    main()
