"""Agrupa facturas por días de vencidas. Uso: cartera.py archivo.csv AAAA-MM-DD"""
import csv, sys, datetime as d
today = d.date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else d.date.today()
G = [("Sin vencer", -10**6, 0), ("1 a 15 días", 1, 15), ("16 a 45 días", 16, 45), ("Más de 45 días", 46, 10**6)]
rows = list(csv.DictReader(open(sys.argv[1], encoding="utf-8-sig")))
tot = 0
for name, lo, hi in G:
    sel = []
    for r in rows:
        days = (today - d.date.fromisoformat(r["vence"])).days
        if lo <= days <= hi: sel.append((days, r))
    if not sel: continue
    s = sum(int(r["valor"]) for _, r in sel); tot += s
    print(f"\n{name}: {len(sel)} | {s:,}")
    for days, r in sorted(sel, key=lambda x: -x[0]):
        print(f"  {r['cliente']} | {r['factura']} | {int(r['valor']):,} | {days} días | {r.get('nota') or ''}")
print(f"\nTOTAL: {tot:,}")
