"""Compara dos CSV con columnas producto,cantidad,precio."""
import csv, sys
def load(path):
    out = {}
    for r in csv.DictReader(open(path, encoding="utf-8-sig")):
        k = r["producto"].strip().lower()
        if k in out: sys.exit("Producto repetido: " + r["producto"])
        out[k] = (float(r["cantidad"]), float(r["precio"]))
    return out
a, b = load(sys.argv[1]), load(sys.argv[2])       # order.csv invoice.csv
diff, n = 0, 0
for k in sorted(set(a) | set(b)):
    if k not in b: print(f"{k}: está en el pedido y no en la factura"); n += 1; diff -= a[k][0] * a[k][1]; continue
    if k not in a: print(f"{k}: está en la factura y no en el pedido"); n += 1; diff += b[k][0] * b[k][1]; continue
    (q1, p1), (q2, p2) = a[k], b[k]
    if q1 != q2: print(f"{k}: cantidad {q1:g} -> {q2:g}"); n += 1
    if p1 != p2: print(f"{k}: precio {p1:g} -> {p2:g}"); n += 1
    diff += q2 * p2 - q1 * p1
print(f"Diferencias: {n}"); print(f"La factura menos el pedido: {diff:g}")
