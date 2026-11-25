"""Applies the rule written in rules.json. Totals come from here, not from the model."""
import json, sys, pathlib
rules = json.loads((pathlib.Path(__file__).parent.parent / "rules.json").read_text(encoding="utf-8"))
order = json.load(sys.stdin)                      # {"items": [["product", quantity], ...]}
P = rules["products"]
sub, rows = 0, []
for name, qty in order["items"]:
    if name not in P:
        sys.exit("Not in the list: " + name)
    if not isinstance(qty, int) or qty <= 0:
        sys.exit("Invalid quantity: " + name)
    t = P[name] * qty; sub += t; rows.append((name, qty, P[name], t))
pct = max([p for start, p in rules["discounts"] if sub >= start], default=0)
disc = round(sub * pct / 100)
ship = 0 if sub >= rules["free_shipping_from"] else rules["shipping"]
f = lambda n: f"{n:,}".replace(",", ",")
for n, q, p, t in rows: print(f"{n} | {q} x {f(p)} = {f(t)}")
print(f"Subtotal: {f(sub)}"); print(f"Discount ({pct}%): -{f(disc)}"); print(f"Shipping: {f(ship)}"); print(f"TOTAL: {f(sub - disc + ship)}")
