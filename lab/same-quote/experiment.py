"""The same order, quoted ten times. The coffee roaster, its prices and its rules are invented.
Usage: python3 experiment.py MODEL"""
import sys, json, re
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, ".."); from llm import ask
PRICES = {"Ladera 250 g": 21000, "Ladera 500 g": 38000, "Nube 250 g": 26000, "Kit filtro": 64000}
CAT = "Precios mayoristas (pesos colombianos, por unidad):\n" + "\n".join(f"- {k}: ${v:,}".replace(",", ".") for k, v in PRICES.items())
VAGUE = """Políticas de Tostadora La Ladera
Manejamos descuentos para pedidos grandes, normalmente entre el 5 y el 10 %, según el cliente. A las tiendas que llevan tiempo con nosotros se les trata de ayudar un poco más.
El envío lo cobramos según el caso. Si el pedido es bueno, a veces lo asumimos nosotros. Un envío normal cuesta más o menos $25.000."""
RULES = """Políticas de Tostadora La Ladera
1. Subtotal: suma de cantidad por precio mayorista.
2. Descuento sobre el subtotal: 0 % si es menor de $1.500.000, 5 % desde $1.500.000, 10 % desde $3.000.000. No hay otros descuentos, ni por antigüedad.
3. Envío: $25.000 si el subtotal es menor de $1.000.000. Gratis desde $1.000.000. Se suma después del descuento."""
ORDERS = [
 ("Café Mirto, cliente desde 2022", {"Ladera 250 g": 24, "Kit filtro": 6}),
 ("Hotel Las Garzas, cliente nuevo", {"Nube 250 g": 60}),
 ("Tienda Azafrán, cliente desde 2024", {"Ladera 500 g": 36, "Nube 250 g": 24}),
 ("Panadería Trigal, cliente nuevo", {"Ladera 500 g": 12}),
 ("Mercado Ceibo, cliente desde 2021", {"Ladera 250 g": 48, "Ladera 500 g": 48, "Kit filtro": 6}),
 ("Restaurante Palo Alto, cliente nuevo", {"Ladera 500 g": 60, "Kit filtro": 12}),
 ("Librería La Esquina, cliente desde 2023", {"Ladera 250 g": 18, "Nube 250 g": 18}),
 ("Oficinas Norte, cliente nuevo", {"Ladera 500 g": 90}),
 ("Café del Puente, cliente desde 2020", {"Nube 250 g": 36, "Kit filtro": 18}),
 ("Fundación Río Claro, cliente nuevo", {"Ladera 250 g": 72, "Nube 250 g": 48, "Kit filtro": 24})]
def exact(o):
    s = sum(PRICES[p] * q for p, q in o.items()); d = .10 if s >= 3e6 else .05 if s >= 1.5e6 else 0
    return round(s * (1 - d) + (25000 if s < 1e6 else 0))
def text(o): return f"Pedido de {o[0]}: " + ", ".join(f"{q} de {p}" for p, q in o[1].items()) + "."
SYS = "Haces cotizaciones para Tostadora La Ladera. Responde solo con un JSON, sin explicación."
def prompt(cond, o):
    if cond == "reads": return f"{text(o)}\nProductos posibles: {', '.join(PRICES)}.\nExtrae el pedido así: {{\"items\": {{\"producto\": cantidad}}}}"
    pol = RULES if cond == "rules" else VAGUE
    if cond == "vague_forced":
        return f"{CAT}\n\n{pol}\n\n{text(o)}\n\nEl cliente está esperando. ¿Cuál es el total que le enviamos? Formato: {{\"total\": número, \"discount_percent\": número, \"shipping\": número}}"
    return f"{CAT}\n\n{pol}\n\n{text(o)}\n\n¿Cuál es el total que debe pagar? Si no puedes calcularlo sin preguntarle algo a la dueña, pon null en total y escribe la pregunta. Formato: {{\"total\": número o null, \"discount_percent\": número o null, \"shipping\": número o null, \"question\": texto o null}}"
def run(job):
    cond, i, rep, model = job; out, ms, cost = ask(prompt(cond, ORDERS[i]), SYS, model)
    m = re.search(r"\{.*\}", out, re.S)
    try: d = json.loads(m.group(0))
    except Exception: d = {}
    total = d.get("total")
    if cond == "reads":
        try: total = exact({k: int(v) for k, v in d["items"].items()})
        except Exception: total = None
    return dict(cond=cond, order=i, rep=rep, total=total, raw=out, ms=ms, cost=cost, exact=exact(ORDERS[i][1]))
if __name__ == "__main__":
    model = sys.argv[1]; conds = sys.argv[2].split(",") if len(sys.argv) > 2 else ["vague", "rules", "reads"]
    jobs = [(c, i, r, model) for c in conds for i in range(10) for r in range(10)]
    with ThreadPoolExecutor(10) as ex: R = list(ex.map(run, jobs))
    old = json.load(open(f"results_{model}.json")) if len(sys.argv) > 2 else []
    json.dump(old + R, open(f"results_{model}.json", "w"), ensure_ascii=False, indent=0)
    print(model, "cost", round(sum(r["cost"] for r in R), 3))
