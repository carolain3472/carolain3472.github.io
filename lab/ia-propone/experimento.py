"""¿Quién hace la cuenta? Un municipio inventado, 40 documentos y tres formas de llegar al total.
A) el modelo lee y calcula    B) el modelo lee y un programa calcula    C) el programa con los datos correctos (la verdad)
Todo es ficticio: ni las tarifas ni las reglas son de un municipio real."""
import sys, json, random, re
from decimal import Decimal as D, ROUND_HALF_UP
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, ".."); from llm import ask
RATES = {"101": D("4.14"), "203": D("6.9"), "305": D("7.7"), "412": D("9.66"), "508": D("11.04")}
NAMES = {"101":"producción de alimentos","203":"comercio al por menor","305":"comercio de ferretería","412":"consultoría","508":"restaurante"}
def miles(x): return (D(x)/1000).quantize(D(1), ROUND_HALF_UP)*1000
def engine(d):
    tax = sum((D(l["ingreso"])-D(l["devoluciones"]))*RATES[str(l["codigo"])]/1000 for l in d["lineas"])
    tax = miles(tax); avisos = miles(tax*D("0.15")); bomb = miles((tax)*D("0.03"))
    total = tax+avisos+bomb-miles(d["retenciones"])
    if d["pronto_pago"]: total = total-miles(total*D("0.10"))
    return int(total)
f = lambda n: "$"+f"{n:,}".replace(",",".")
def make(i):
    r = random.Random(100+i); lines=[]
    for c in r.sample(sorted(RATES), r.choice([2,3,4])):
        ing = r.randint(8_000_000, 480_000_000); lines.append(dict(codigo=c, ingreso=ing, devoluciones=r.choice([0,0,r.randint(90_000, ing//20)])))
    d = dict(lineas=lines, retenciones=r.randint(0, 900_000), pronto_pago=r.random()<.5)
    parts=[]
    for l in lines:
        t = r.choice([f"Por {NAMES[l['codigo']]} (actividad {l['codigo']}) se facturaron {f(l['ingreso'])} en el año",
                      f"La actividad {l['codigo']}, {NAMES[l['codigo']]}, cerró con ingresos de {f(l['ingreso'])}",
                      f"{NAMES[l['codigo']].capitalize()}, código {l['codigo']}: {f(l['ingreso'])}"])
        t += f", de los que se devolvieron {f(l['devoluciones'])}." if l["devoluciones"] else ", sin devoluciones."
        parts.append(t)
    r.shuffle(parts)
    ruido = r.choice(["La bodega se trasladó en agosto y el arriendo quedó en $3.200.000 mensuales.","El año pasado el cliente pagó $1.145.000 por este concepto.","La nómina del último trimestre fue de $41.780.000."])
    parts.insert(r.randrange(len(parts)+1), ruido)
    parts.append(f"Los clientes le practicaron retenciones por {f(d['retenciones'])}." if d["retenciones"] else "No hubo retenciones.")
    parts.append("Va a pagar dentro del plazo de pronto pago." if d["pronto_pago"] else "Va a pagar después del plazo de pronto pago.")
    return dict(id=i, datos=d, texto=" ".join(parts), verdad=engine(d))
RULES = "Tarifas por mil: "+", ".join(f"actividad {k}: {v}" for k,v in RATES.items())+""".
Pasos: 1) Por cada actividad, (ingreso menos devoluciones) por tarifa, dividido en 1000. Suma todo y redondea al múltiplo de 1000 más cercano: ese es el impuesto.
2) Avisos: 15 % del impuesto, redondeado al múltiplo de 1000 más cercano. 3) Sobretasa bomberil: 3 % del impuesto, redondeada igual.
4) Total = impuesto + avisos + bomberil - retenciones (redondeadas al múltiplo de 1000 más cercano).
5) Si paga dentro del pronto pago, resta el 10 % del total, redondeado al múltiplo de 1000 más cercano."""
if __name__ == "__main__":
    model = sys.argv[1]; cases=[make(i) for i in range(40)]
    json.dump(cases, open("casos.json","w"), ensure_ascii=False, indent=1)
    def one(c):
        a,ms1,u1 = ask(f"{RULES}\n\nDocumento del cliente:\n{c['texto']}\n\nResponde solo con el total a pagar, en pesos, sin puntos ni signos.", "Eres un asistente que liquida un impuesto. Responde solo con un número entero.", model)
        n = re.findall(r"-?\d[\d.,]*", a.replace("$","")); a_val = int(re.sub(r"[.,]","",n[-1])) if n else None
        b,ms2,u2 = ask(f"Documento del cliente:\n{c['texto']}\n\nDevuelve solo un JSON con esta forma: {{\"lineas\":[{{\"codigo\":\"101\",\"ingreso\":0,\"devoluciones\":0}}],\"retenciones\":0,\"pronto_pago\":true}}. Los números van enteros, sin puntos.", "Extraes datos de documentos. Responde solo con JSON, sin explicación.", model)
        ext=None; b_val=None
        try: ext=json.loads(re.search(r"\{.*\}", b, re.S).group(0)); b_val=engine(ext)
        except Exception: pass
        key=lambda d: (sorted((str(l["codigo"]),int(l["ingreso"]),int(l["devoluciones"])) for l in d["lineas"]), int(d["retenciones"]), bool(d["pronto_pago"]))
        lee = ext is not None and key(ext)==key(c["datos"])
        return dict(id=c["id"], verdad=c["verdad"], solo_modelo=a_val, lee_y_programa=b_val, lectura_perfecta=lee, ms=[ms1,ms2], usd=u1+u2, n_lineas=len(c["datos"]["lineas"]))
    with ThreadPoolExecutor(6) as ex: rows=list(ex.map(one, cases))
    json.dump(dict(model=model, rows=rows), open(f"resultados_{model}.json","w"), indent=1)
    print(model, "solo modelo", sum(r["solo_modelo"]==r["verdad"] for r in rows), "| lee+programa", sum(r["lee_y_programa"]==r["verdad"] for r in rows), "| lectura perfecta", sum(r["lectura_perfecta"] for r in rows), "| usd", round(sum(r["usd"] for r in rows),3))
    e=sorted(abs(r["solo_modelo"]-r["verdad"]) for r in rows if r["solo_modelo"] is not None and r["solo_modelo"]!=r["verdad"]); print("errores en pesos:", e)
