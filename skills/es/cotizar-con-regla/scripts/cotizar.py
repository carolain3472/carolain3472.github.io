"""Aplica la regla escrita en reglas.json. Los totales salen de aquí, no del modelo."""
import json, sys, pathlib
rules = json.loads((pathlib.Path(__file__).parent.parent / "reglas.json").read_text(encoding="utf-8"))
order = json.load(sys.stdin)                      # {"items": [["product", quantity], ...]}
P = rules["productos"]
sub, rows = 0, []
for name, qty in order["items"]:
    if name not in P:
        sys.exit("No está en la lista: " + name)
    if not isinstance(qty, int) or qty <= 0:
        sys.exit("Cantidad no válida: " + name)
    t = P[name] * qty; sub += t; rows.append((name, qty, P[name], t))
pct = max([p for start, p in rules["descuentos"] if sub >= start], default=0)
disc = round(sub * pct / 100)
ship = 0 if sub >= rules["envio_gratis_desde"] else rules["envio"]
f = lambda n: f"{n:,}".replace(",", ".")
for n, q, p, t in rows: print(f"{n} | {q} x {f(p)} = {f(t)}")
print(f"Subtotal: {f(sub)}"); print(f"Descuento ({pct}%): -{f(disc)}"); print(f"Envío: {f(ship)}"); print(f"TOTAL: {f(sub - disc + ship)}")
