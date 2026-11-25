"""Groups invoices by days overdue. Use: overdue.py file.csv YYYY-MM-DD"""
import csv, sys, datetime as d
today = d.date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else d.date.today()
G = [("Not due", -10**6, 0), ("1 to 15 days", 1, 15), ("16 to 45 days", 16, 45), ("Over 45 days", 46, 10**6)]
rows = list(csv.DictReader(open(sys.argv[1], encoding="utf-8-sig")))
tot = 0
for name, lo, hi in G:
    sel = []
    for r in rows:
        days = (today - d.date.fromisoformat(r["due"])).days
        if lo <= days <= hi: sel.append((days, r))
    if not sel: continue
    s = sum(int(r["amount"]) for _, r in sel); tot += s
    print(f"\n{name}: {len(sel)} | {s:,}")
    for days, r in sorted(sel, key=lambda x: -x[0]):
        print(f"  {r['client']} | {r['invoice']} | {int(r['amount']):,} | {days} days | {r.get('note') or ''}")
print(f"\nTOTAL: {tot:,}")
