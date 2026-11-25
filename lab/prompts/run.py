"""Eight of the ten prompts (the two interviews need a conversation), one invented case, two models, 5 times each."""
import json, pathlib, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1])); from llm import ask
H = pathlib.Path(__file__).parent
P = {p["id"]: p["es"]["p"] for p in json.loads((H / "prompts.json").read_text())}
COM = ["El pan rico pero la fila es eterna","Me tocó esperar 25 minutos","Muy amable la señora de la caja","No había datáfono, tocó irme a sacar plata","El croissant estaba frío","Demoran mucho los sábados","Delicioso todo","No reciben tarjeta","La fila otra vez. Y sin sillas","Precio justo","El pan de chocolate llegó aplastado en el domicilio","Esperé media hora y no me atendían","Ojalá pusieran datáfono","Buen café","Domicilio tarde y frío","Me encantó","Solo efectivo, en 2026","Los sábados no se puede entrar","Nadie contesta el teléfono","Rico pero caro"]
C = {
"doubt": {"[decisión]":"abrir un segundo local de mi panadería","[datos]":"el primero vende bien los fines de semana; tengo 40 millones ahorrados; el arriendo nuevo cuesta 3 millones al mes","[supuestos]":"que la gente del otro barrio compra lo mismo; que mi hermana puede manejarlo"},
"order": {"[pégalo sin nombres ni teléfonos]":"Hola buenas, mira, yo quería como 3 o 4 docenas de las empanadas, las de siempre, y también dos tortas, una de las grandes y la otra normal, es para el sábado en la tarde, es por el parque donde la vez pasada, me dices cuánto es"},
"price": {"[producto y precio]":"mantenimiento de jardín, 380.000 al mes","[lista]":"cuatro visitas, poda, abono, recolección de residuos","[escríbela, o «no doy»]":"no doy","[mensaje]":"uy no, muy caro, a mi vecino le cobran menos, ¿en cuánto me lo deja?"},
"voice": {"[pégalos]":"1) Hoy cerramos tarde. Se acabó el pan de yuca a las cuatro y la gente siguió llegando. 2) El horno nuevo quema por la izquierda. Ya aprendimos a girar la bandeja. 3) Si van a pedir torta, pidan el jueves. El viernes ya es puro afán.","[tema]":"vamos a abrir los domingos","[datos]":"desde el 6 de diciembre, de 7 a 12, solo pan y café"},
"claim": {"[mensaje]":"pedí las cortinas hace un mes, me dijeron 15 días, no me contestan y ya tengo visita en la casa este fin de semana. pésimo","[hechos]":"la tela llegó tarde del proveedor; nadie le avisó; las cortinas están listas para instalar","[lista, o «nada todavía»]":"instalar el jueves en la mañana o el viernes en la tarde"},
"comments": {"[pégalos sin nombres]":"\n"+"\n".join(f"{i+1}. {c}" for i,c in enumerate(COM))},
"collect": {"[valor]":"1.840.000","[días]":"22","[cuéntala]":"me compra hace tres años y nunca se había atrasado","[medios]":"transferencia"},
"suppliers": {"[pégalas]":"A) Bolsas kraft 250 g, millar 310.000 + IVA. Entrega 8 días. 50 % anticipo. B) Bolsa kraft de media libra, paquete x 500: $168.000 IVA incluido. Pago a 30 días. C) Bolsas: 290 pesos la unidad desde 2.000 unidades, impresión a 1 tinta incluida. Válida hasta el 10 de diciembre."}}
def fill(k):
    t = P[k]
    for a, b in C[k].items(): assert a in t, (k, a); t = t.replace(a, b)
    return t
jobs = [(k, m, i) for k in C for m in ("claude-haiku-5-5", "claude-sonnet-5-5") for i in range(5)]
def one(j):
    k, m, i = j; a, _, c = ask(fill(k), "Eres un asistente. Responde en español.", m); return dict(id=k, model=m, run=i, answer=a, cost=c)
out = list(ThreadPoolExecutor(4).map(one, jobs))
(H / "results.json").write_text(json.dumps(out, ensure_ascii=False, indent=1)); print(len(out), sum(o["cost"] for o in out), sum(not o["answer"] for o in out))
