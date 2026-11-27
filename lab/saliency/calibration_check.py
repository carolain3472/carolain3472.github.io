"""Why does temperature scaling help so little on the 128 px test set?

Hypothesis: the temperature is fitted on validation data (74% pneumonia) and the test set has 62.5%.
Three checks, test set at 128 px, 5 models:
  1. where the errors are (false positives vs false negatives) and how confident they are;
  2. an oracle: temperature fitted on one half of the test set, ECE measured on the other half
     (100 random splits). If this fixes it, the method works and the validation data was the problem;
  3. a prior correction that only uses the two prevalences (Saerens et al., 2002): add
     log(0.625/0.375) - log(0.742/0.258) to the pneumonia logit, then apply the validation temperature.

Writes results/calibration_check.json.
"""
import json
import numpy as np, torch
from train import load, logits, HERE
from calibration import net, fit_temperature, ece, SEEDS


def conf_correct(z, y, T=1.0):
    p = (z / T).softmax(1)
    return p.max(1).values.numpy(), (p.argmax(1) == y).float().numpy()


def main():
    d = load(128); (xv, yv), (xt, yt) = d["val"], d["test"]
    pv, pt = float(yv.float().mean()), float(yt.float().mean())
    shift = np.log(pt / (1 - pt)) - np.log(pv / (1 - pv))
    out = {"val_prevalence": pv, "test_prevalence": pt, "logit_shift": shift, "models": []}
    for s in SEEDS:
        m = net(f"real_s{s}"); zv, zt = logits(m, xv), logits(m, xt)
        T = fit_temperature(zv, yv)
        pred = zt.argmax(1); conf = zt.softmax(1).max(1).values
        fp = ((pred == 1) & (yt == 0)); fn = ((pred == 0) & (yt == 1))
        row = dict(seed=s, T_val=T, false_pos=int(fp.sum()), false_neg=int(fn.sum()),
                   normals=int((yt == 0).sum()), pneumonia=int((yt == 1).sum()),
                   fp_over_95=int((fp & (conf > 0.95)).sum()), fn_over_95=int((fn & (conf > 0.95)).sum()),
                   ece_none=ece(*conf_correct(zt, yt)), ece_val_T=ece(*conf_correct(zt, yt, T)))
        rng = np.random.default_rng(s); oracle, oracle_T = [], []
        for _ in range(100):
            i = torch.tensor(rng.permutation(len(yt))); a, b = i[: len(i) // 2], i[len(i) // 2:]
            To = fit_temperature(zt[a], yt[a]); oracle_T.append(To)
            oracle.append(ece(*conf_correct(zt[b], yt[b], To)))
        row["ece_oracle_T"] = float(np.mean(oracle)); row["oracle_T"] = float(np.mean(oracle_T))
        zs = zt.clone(); zs[:, 1] += shift
        row["ece_prior"] = ece(*conf_correct(zs, yt, T))
        row["acc_none"] = float((pred == yt).float().mean()); row["acc_prior"] = float((zs.argmax(1) == yt).float().mean())
        out["models"].append(row)
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in row.items()}, flush=True)
    json.dump(out, open(f"{HERE}/results/calibration_check.json", "w"), indent=1)


if __name__ == "__main__":
    main()
