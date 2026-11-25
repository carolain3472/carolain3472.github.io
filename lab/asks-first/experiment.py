"""Advice with and without asking first. Six invented businesses, each with a sheet the adviser cannot see.
Usage: python3 experiment.py ADVISER_MODEL"""
import sys, json, re
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, ".."); from llm import ask
K = ["drain", "second", "root", "tried", "limit", "goal"]
B = {
"bakery": ("Tengo una panadería con domicilios en un barrio. Somos cuatro. Siento que no me alcanza el día y todo el mundo me dice que use inteligencia artificial.",
 dict(drain="Cada noche pasa hora y media copiando pedidos de WhatsApp a un cuaderno para saber qué hornear.", second="Dos veces por semana llama uno por uno a los clientes de tortas para confirmar la hora.", root="Los pedidos llegan por tres números de WhatsApp distintos, el de ella y el de dos empleados.", tried="Pagó un chatbot hace un año y lo quitó al mes porque les confirmaba a los clientes productos agotados.", limit="La persona que hornea tiene 64 años y no usa computador, necesita la lista impresa en papel a las 4 de la mañana.", goal="En tres meses quiere poder cerrar los domingos sin perder pedidos.")),
"clinic": ("Soy dueña de un consultorio odontológico pequeño. Tenemos dos sillas y una recepcionista. Quiero ver cómo me ayuda la IA porque se me va la plata y no sé por dónde.",
 dict(drain="La recepcionista gasta dos horas diarias llamando a confirmar citas del día siguiente.", second="Cada viernes la doctora escribe a mano los informes para las aseguradoras, unos doce, de veinte minutos cada uno.", root="La agenda está en un Excel que solo se abre en un computador y nadie registra por qué cancelan los pacientes.", tried="Mandaron mensajes automáticos de recordatorio y muchos pacientes mayores no los leían, la inasistencia no cambió.", limit="Por protección de datos no pueden subir historias clínicas a ninguna herramienta externa.", goal="En tres meses quiere bajar las sillas vacías de diez a tres por semana.")),
"hardware": ("Tengo una ferretería que heredé de mi papá. Vendemos a constructoras y al público. Me dijeron que con IA podía vender más pero no sé ni qué pedir.",
 dict(drain="Cotizar a las constructoras le toma las mañanas completas, porque mandan listas escritas a mano en fotos.", second="Los sábados cuenta el inventario de tornillería a mano durante tres horas.", root="Los precios de los proveedores llegan en PDF distintos cada semana y solo él sabe cuál es el vigente.", tried="Compró un programa de inventario hace dos años y nadie lo alimentó después del primer mes.", limit="Los dos vendedores atienden de pie y solo tienen celular, no hay computador en el mostrador.", goal="En tres meses quiere responder cualquier cotización el mismo día.")),
"tourism": ("Organizo caminatas y avistamiento de aves. Somos mi hermano y yo. Tengo clientes extranjeros y siento que estoy perdiendo oportunidades.",
 dict(drain="Responde correos en inglés con traductor, cuarenta minutos cada uno, unos seis al día en temporada.", second="Arma a mano los itinerarios de cada grupo en Word, casi una hora por grupo.", root="Las condiciones como clima, dificultad, qué incluye y cancelaciones no están escritas en ninguna parte y las explica cada vez.", tried="Contrató a alguien para redes sociales seis meses y llegaron seguidores pero ninguna reserva.", limit="En la finca no hay internet de lunes a jueves cuando está con grupos.", goal="En tres meses quiere tener cerrados ocho grupos para la temporada de migración.")),
"school": ("Dirijo una academia de música con noventa estudiantes. Todo es un desorden y no sé si la IA sirva para esto.",
 dict(drain="Cada fin de mes pasa dos días revisando comprobantes de pago en fotos para saber quién pagó.", second="Reprograma clases por mensajes, unas quince por semana, hablando por separado con profesor y familia.", root="Cada profesor lleva su propia lista de estudiantes en su celular.", tried="Intentó que las familias pagaran por una aplicación y casi la mitad no la usó.", limit="Los estudiantes son menores de edad y sus datos y fotos no se pueden compartir sin permiso de las familias.", goal="En tres meses quiere que la mora baje de 30 a 10 por ciento.")),
"textile": ("Hacemos uniformes para empresas pequeñas, tengo un taller con nueve operarias. Vendemos bien pero los clientes se quejan.",
 dict(drain="Cada pedido se retrasa porque hay que escribirle varias veces al cliente para completar tallas y logos, cerca de una hora por pedido.", second="Hace a mano la ficha técnica de cada prenda, media hora cada una.", root="El pedido entra por donde el cliente quiera, audio, correo o llamada, y no hay un formato único.", tried="Pidió a las operarias llenar un tablero en el computador y lo dejaron porque interrumpía la costura.", limit="El logo de cada cliente está firmado con un acuerdo de confidencialidad y no puede salir a herramientas públicas.", goal="En tres meses quiere entregar a tiempo nueve de cada diez pedidos."))}
SYS = "Eres asesora de negocios y experta en IA para pequeñas empresas. Hablas claro y sin palabras técnicas."
END = "Dame las 3 oportunidades donde la IA más me ayudaría, de la más fácil a la más difícil, en máximo 220 palabras."
OWNER = "Haces el papel de la persona dueña de este negocio. Contesta en una o dos frases solo lo que te preguntan, con lo que dice tu ficha. No des información que no te pidieron. Si la ficha no lo dice, di que no sabes o que no lo has pensado.\n\nFICHA\n"
JUDGE = "Lees una recomendación para un negocio y una ficha con seis datos que quien asesora no conocía de antemano. Para cada dato di si la recomendación lo tiene en cuenta de forma concreta (menciona ese dato o propone algo que solo tiene sentido si lo conoce). Un consejo general que coincide por casualidad no cuenta. Para 'tried' y 'limit' cuenta solo si lo menciona o lo respeta de forma explícita. Responde solo JSON con true o false: " + json.dumps({k: True for k in K})
BAD = re.compile(r"c[oó]digo|ejecutar|simular|experimento|\bcode\b", re.I)
def clean_ask(p, s, m):
    for _ in range(4):
        o, ms, c = ask(p, s, m)
        if o and not BAD.search(o): return o, ms, c
    return o, ms, c
def talk(h): return "\n".join(f"{w}: {t}" for w, t in h)
def run(job):
    b, cond, rep, model = job; intro, sheet = B[b]; h = [("Dueña", intro)]; cost = 0
    if cond in ("asks", "asks_better"):
        extra = " Entre tus 5 preguntas tienen que estar: qué he intentado antes y cómo me fue, qué cosas no puedo cambiar (personas, datos, dinero, conexión) y qué quiero haber logrado en tres meses." if cond == "asks_better" else ""
        for n in range(5):
            q, _, c = clean_ask(f"{talk(h)}\n\nAntes de proponer nada, hazme la pregunta {n+1} de 5.{extra} Escribe una sola pregunta, corta.", SYS, model); cost += c
            a, _, c = clean_ask(f"Conversación hasta ahora:\n{talk(h)}\nAsesora: {q}\n\nContesta como la dueña.", OWNER + "\n".join(sheet.values()), "claude-haiku-5-5"); cost += c
            h += [("Asesora", q.strip()), ("Dueña", a.strip())]
    adv, _, c = clean_ask(f"{talk(h)}\n\n{END}", SYS, model); cost += c
    j, _, c = ask("FICHA\n" + "\n".join(f"{k}: {v}" for k, v in sheet.items()) + f"\n\nRECOMENDACIÓN\n{adv}", JUDGE, "claude-sonnet-5-5"); cost += c
    try: s = json.loads(re.search(r"\{.*\}", j, re.S).group(0))
    except Exception: s = None
    return dict(business=b, cond=cond, rep=rep, talk=h, advice=adv, seen=s, cost=cost)
if __name__ == "__main__":
    model = sys.argv[1]; conds = sys.argv[2].split(",") if len(sys.argv) > 2 else ["direct", "asks"]
    jobs = [(b, c, r, model) for b in B for c in conds for r in range(4)]
    with ThreadPoolExecutor(8) as ex: R = list(ex.map(run, jobs))
    json.dump(R, open(f"results_{model}" + ("" if len(sys.argv) < 3 else "_" + sys.argv[2].replace(",", "_")) + ".json", "w"), ensure_ascii=False, indent=0); print(model, "cost", round(sum(r["cost"] for r in R), 3))
