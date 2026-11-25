"""Compares two CSV files with columns product,quantity,price."""
import csv, sys
def load(path):
    out = {}
    for r in csv.DictReader(open(path, encoding="utf-8-sig")):
        k = r["product"].strip().lower()
        if k in out: sys.exit("Repeated product: " + r["product"])
        out[k] = (float(r["quantity"]), float(r["price"]))
    return out
a, b = load(sys.argv[1]), load(sys.argv[2])       # order.csv invoice.csv
diff, n = 0, 0
for k in sorted(set(a) | set(b)):
    if k not in b: print(f"{k}: is in the order and not in the invoice"); n += 1; diff -= a[k][0] * a[k][1]; continue
    if k not in a: print(f"{k}: is in the invoice and not in the order"); n += 1; diff += b[k][0] * b[k][1]; continue
    (q1, p1), (q2, p2) = a[k], b[k]
    if q1 != q2: print(f"{k}: quantity {q1:g} -> {q2:g}"); n += 1
    if p1 != p2: print(f"{k}: price {p1:g} -> {p2:g}"); n += 1
    diff += q2 * p2 - q1 * p1
print(f"Differences: {n}"); print(f"Invoice minus order: {diff:g}")
