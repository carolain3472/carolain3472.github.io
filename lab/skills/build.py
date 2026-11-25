"""Writes the six skills in Spanish and English and zips them (folder at the root of each zip)."""
import pathlib, zipfile, json, textwrap
R = pathlib.Path(__file__).resolve().parents[2] / "skills"
D = textwrap.dedent
QUOTE = '''"""{doc}"""
import json, sys, pathlib
rules = json.loads((pathlib.Path(__file__).parent.parent / "{rf}").read_text(encoding="utf-8"))
order = json.load(sys.stdin)                      # {{"items": [["product", quantity], ...]}}
P = rules["{products}"]
sub, rows = 0, []
for name, qty in order["items"]:
    if name not in P:
        sys.exit("{unknown}: " + name)
    if not isinstance(qty, int) or qty <= 0:
        sys.exit("{badqty}: " + name)
    t = P[name] * qty; sub += t; rows.append((name, qty, P[name], t))
pct = max([p for start, p in rules["{discounts}"] if sub >= start], default=0)
disc = round(sub * pct / 100)
ship = 0 if sub >= rules["{freefrom}"] else rules["{shipping}"]
f = lambda n: f"{{n:,}}".replace(",", "{sep}")
for n, q, p, t in rows: print(f"{{n}} | {{q}} x {{f(p)}} = {{f(t)}}")
print(f"{subt}: {{f(sub)}}"); print(f"{dis} ({{pct}}%): -{{f(disc)}}"); print(f"{shi}: {{f(ship)}}"); print(f"TOTAL: {{f(sub - disc + ship)}}")
'''
COMPARE = '''"""{doc}"""
import csv, sys
def load(path):
    out = {{}}
    for r in csv.DictReader(open(path, encoding="utf-8-sig")):
        k = r["{c0}"].strip().lower()
        if k in out: sys.exit("{dup}: " + r["{c0}"])
        out[k] = (float(r["{c1}"]), float(r["{c2}"]))
    return out
a, b = load(sys.argv[1]), load(sys.argv[2])       # order.csv invoice.csv
diff, n = 0, 0
for k in sorted(set(a) | set(b)):
    if k not in b: print(f"{{k}}: {onlya}"); n += 1; diff -= a[k][0] * a[k][1]; continue
    if k not in a: print(f"{{k}}: {onlyb}"); n += 1; diff += b[k][0] * b[k][1]; continue
    (q1, p1), (q2, p2) = a[k], b[k]
    if q1 != q2: print(f"{{k}}: {qty} {{q1:g}} -> {{q2:g}}"); n += 1
    if p1 != p2: print(f"{{k}}: {price} {{p1:g}} -> {{p2:g}}"); n += 1
    diff += q2 * p2 - q1 * p1
print(f"{diffs}: {{n}}"); print(f"{extra}: {{diff:g}}")
'''
DUE = '''"""{doc}"""
import csv, sys, datetime as d
today = d.date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else d.date.today()
G = [("{g0}", -10**6, 0), ("{g1}", 1, 15), ("{g2}", 16, 45), ("{g3}", 46, 10**6)]
rows = list(csv.DictReader(open(sys.argv[1], encoding="utf-8-sig")))
tot = 0
for name, lo, hi in G:
    sel = []
    for r in rows:
        days = (today - d.date.fromisoformat(r["{c3}"])).days
        if lo <= days <= hi: sel.append((days, r))
    if not sel: continue
    s = sum(int(r["{c2}"]) for _, r in sel); tot += s
    print(f"\\n{{name}}: {{len(sel)}} | {{s:,}}")
    for days, r in sorted(sel, key=lambda x: -x[0]):
        print(f"  {{r['{c0}']}} | {{r['{c1}']}} | {{int(r['{c2}']):,}} | {{days}} {dd} | {{r.get('{c4}') or ''}}")
print(f"\\nTOTAL: {{tot:,}}")
'''
S = {"es": {}, "en": {}}
rules_es = {"productos": {"Café Montaña 500 g": 32000, "Café Río 500 g": 38000, "Café Montaña 2,5 kg": 145000}, "descuentos": [[1500000, 5], [3000000, 10]], "envio": 25000, "envio_gratis_desde": 1000000, "quien_aprueba_excepciones": "escribe aquí nombre y cargo"}
rules_en = {"products": {"Mountain Coffee 500 g": 32000, "River Coffee 500 g": 38000, "Mountain Coffee 2.5 kg": 145000}, "discounts": [[1500000, 5], [3000000, 10]], "shipping": 25000, "free_shipping_from": 1000000, "who_approves_exceptions": "write a name and position here"}
S["es"]["cotizar-con-regla"] = {
"SKILL.md": D("""\
    ---
    name: cotizar-con-regla
    description: Prepara una cotización con la lista de precios y la regla de descuentos del negocio. Úsala cuando llegue un pedido y haya que calcular un total.
    ---
    # Cotizar con regla

    Los precios y las reglas están en `reglas.json`. Cámbialos por los de tu negocio antes de usar esta skill.

    ## Pasos
    1. Lee el pedido. Anota cada producto y su cantidad tal como aparecen.
    2. Busca cada producto en `reglas.json`. Si el nombre no es claro, si falta una cantidad o si el producto no está, detente y pregunta. No lo reemplaces por uno parecido.
    3. Calcula con el programa. No hagas cuentas tú.
       `echo '{"items": [["Café Río 500 g", 12]]}' | python3 scripts/cotizar.py`
       Corre el comando desde la carpeta de esta skill.
    4. Copia las líneas que devuelve el programa, sin cambiar ninguna cifra.
    5. Escribe un mensaje corto para el cliente con esas cifras.

    ## Lo que no puedes hacer
    - Seguir si el programa no corre. Dilo, muestra los datos que leíste y detente. No hagas las cuentas a mano.
    - Dar un descuento que no salga del programa. Si el cliente lo pide, o si alguien dice que siempre se lo dan, escribe: "Eso lo decide" y la persona de `quien_aprueba_excepciones`.
    - Prometer una fecha de entrega. No está en las reglas.
    - Enviar el mensaje. Es un borrador.

    ## Qué entregas
    Las líneas del cálculo, el borrador y una lista con lo que una persona tiene que decidir. Si no hay nada que decidir, dilo.
    """),
"reglas.json": json.dumps(rules_es, ensure_ascii=False, indent=2),
"scripts/cotizar.py": QUOTE.format(doc="Aplica la regla escrita en reglas.json. Los totales salen de aquí, no del modelo.", rf="reglas.json", products="productos", unknown="No está en la lista", badqty="Cantidad no válida", discounts="descuentos", freefrom="envio_gratis_desde", shipping="envio", sep=".", subt="Subtotal", dis="Descuento", shi="Envío")}
S["en"]["quote-by-rule"] = {
"SKILL.md": D("""\
    ---
    name: quote-by-rule
    description: Prepares a quote with the price list and the discount rule of the business. Use it when an order arrives and a total has to be calculated.
    ---
    # Quote by rule

    Prices and rules are in `rules.json`. Change them for the ones of your business before you use this skill.

    ## Steps
    1. Read the order. Write down each product and its quantity as they appear.
    2. Look for each product in `rules.json`. If the name is not clear, a quantity is missing or the product is not there, stop and ask. Don't replace it with a similar one.
    3. Calculate with the program. Don't do the math yourself.
       `echo '{"items": [["River Coffee 500 g", 12]]}' | python3 scripts/quote.py`
       Run the command from the folder of this skill.
    4. Copy the lines the program returns, without changing any figure.
    5. Write a short message for the client with those figures.

    ## What you can't do
    - Go on if the program doesn't run. Say so, show the data you read and stop. Don't do the math by hand.
    - Give a discount that doesn't come from the program. If the client asks for it, or someone says they always get it, write: "That is decided by" and the person in `who_approves_exceptions`.
    - Promise a delivery date. It is not in the rules.
    - Send the message. It is a draft.

    ## What you hand in
    The lines of the calculation, the draft, and a list of what a person has to decide. If there is nothing to decide, say so.
    """),
"rules.json": json.dumps(rules_en, ensure_ascii=False, indent=2),
"scripts/quote.py": QUOTE.format(doc="Applies the rule written in rules.json. Totals come from here, not from the model.", rf="rules.json", products="products", unknown="Not in the list", badqty="Invalid quantity", discounts="discounts", freefrom="free_shipping_from", shipping="shipping", sep=",", subt="Subtotal", dis="Discount", shi="Shipping")}
S["es"]["factura-contra-pedido"] = {
"SKILL.md": D("""\
    ---
    name: factura-contra-pedido
    description: Compara la factura de un proveedor con el pedido y muestra las diferencias de producto, cantidad y precio. Úsala antes de pagar.
    ---
    # Factura contra pedido

    ## Pasos
    1. Pasa el pedido a `pedido.csv` y la factura a `factura.csv`, con las columnas `producto,cantidad,precio`. El precio es por unidad y sin separador de miles.
    2. Usa el mismo nombre en los dos archivos solo cuando estés seguro de que es el mismo producto. Si los nombres no coinciden y dudas, déjalos distintos y anota la duda.
    3. Muestra las dos tablas a la persona, para que pueda revisar la lectura.
    4. Corre `python3 scripts/comparar.py pedido.csv factura.csv` y copia el resultado. No compares de memoria.
    5. Escribe un borrador corto para el proveedor que mencione solo las diferencias del programa.

    ## Lo que no puedes hacer
    - Seguir si el programa no corre. Dilo, muestra los datos que leíste y detente. No hagas las cuentas a mano.
    - Decir "puedes pagar". Di qué coincide y qué no. Pagar lo decide una persona.
    - Adivinar una cifra que no se lee. Escribe "no se lee" y detente.
    - Incluir impuestos, fletes o descuentos que no estén en los dos documentos. Anótalos aparte.

    ## Qué entregas
    Las dos tablas, el resultado del programa, las dudas y el borrador.
    """),
"scripts/comparar.py": COMPARE.format(doc="Compara dos CSV con columnas producto,cantidad,precio.", c0="producto", c1="cantidad", c2="precio", dup="Producto repetido", onlya="está en el pedido y no en la factura", onlyb="está en la factura y no en el pedido", qty="cantidad", price="precio", diffs="Diferencias", extra="La factura menos el pedido")}
S["en"]["invoice-against-order"] = {
"SKILL.md": D("""\
    ---
    name: invoice-against-order
    description: Compares a supplier's invoice with the order and shows the differences in product, quantity and price. Use it before paying.
    ---
    # Invoice against order

    ## Steps
    1. Write the order as `order.csv` and the invoice as `invoice.csv`, with the columns `product,quantity,price`. The price is per unit, without thousands separators.
    2. Use the same name in both files only when you are sure it is the same product. If the names don't match and you doubt, keep them different and write the doubt down.
    3. Show both tables to the person, so they can check the reading.
    4. Run `python3 scripts/compare.py order.csv invoice.csv` and copy the result. Don't compare from memory.
    5. Write a short draft for the supplier that mentions only the differences from the program.

    ## What you can't do
    - Go on if the program doesn't run. Say so, show the data you read and stop. Don't do the math by hand.
    - Say "you can pay". Say what matches and what doesn't. A person decides about paying.
    - Guess a figure that can't be read. Write "can't be read" and stop.
    - Include taxes, freight or discounts that are not in both documents. List them apart.

    ## What you hand in
    The two tables, the result of the program, the doubts and the draft.
    """),
"scripts/compare.py": COMPARE.format(doc="Compares two CSV files with columns product,quantity,price.", c0="product", c1="quantity", c2="price", dup="Repeated product", onlya="is in the order and not in the invoice", onlyb="is in the invoice and not in the order", qty="quantity", price="price", diffs="Differences", extra="Invoice minus order")}
S["es"]["cartera-del-lunes"] = {
"SKILL.md": D("""\
    ---
    name: cartera-del-lunes
    description: Ordena las facturas por cobrar según los días de vencidas y prepara un borrador de cobro para cada cliente. Úsala una vez a la semana.
    ---
    # Cartera del lunes

    ## Pasos
    1. Pide un archivo `cartera.csv` con las columnas `cliente,factura,valor,vence,nota`. La fecha va como 2026-11-25 y el valor sin puntos. Con códigos en lugar de nombres funciona igual.
    2. Corre `python3 scripts/cartera.py cartera.csv 2026-11-25`, con la fecha de hoy, y copia el resultado sin cambiar cifras.
    3. Escribe un borrador por cliente que deba algo vencido. Si tiene varias facturas, un solo mensaje.
       - 1 a 15 días: un recordatorio. Supón que se le pasó.
       - 16 a 45 días: pregunta si hubo un problema y pide una fecha.
       - Más de 45 días: no escribas el mensaje. Ponlo en la lista para llamar.
    4. Si la nota habla de un reclamo, un acuerdo o una enfermedad, no escribas cobro. Ponlo en la lista para decidir.

    ## Lo que no puedes hacer
    - Seguir si el programa no corre. Dilo, muestra los datos que leíste y detente. No hagas las cuentas a mano.
    - Amenazar, hablar de reportes o de abogados, o inventar intereses.
    - Ofrecer descuentos o plazos.
    - Enviar mensajes.

    ## Qué entregas
    La tabla del programa, los borradores, la lista para llamar y la lista para decidir.
    """),
"scripts/cartera.py": DUE.format(doc="Agrupa facturas por días de vencidas. Uso: cartera.py archivo.csv AAAA-MM-DD", g0="Sin vencer", g1="1 a 15 días", g2="16 a 45 días", g3="Más de 45 días", c0="cliente", c1="factura", c2="valor", c3="vence", c4="nota", dd="días")}
S["en"]["monday-collections"] = {
"SKILL.md": D("""\
    ---
    name: monday-collections
    description: Sorts unpaid invoices by days overdue and prepares a collection draft for each client. Use it once a week.
    ---
    # Monday collections

    ## Steps
    1. Ask for a file `invoices.csv` with the columns `client,invoice,amount,due,note`. Dates look like 2026-11-25 and amounts have no separators. It works the same with codes instead of names.
    2. Run `python3 scripts/overdue.py invoices.csv 2026-11-25`, with today's date, and copy the result without changing figures.
    3. Write one draft for each client with something overdue. Several invoices, one message.
       - 1 to 15 days: a reminder. Assume they forgot.
       - 16 to 45 days: ask if there was a problem and ask for a date.
       - Over 45 days: don't write the message. Put it in the list to call.
    4. If the note mentions a claim, an agreement or an illness, don't write a collection message. Put it in the list to decide.

    ## What you can't do
    - Go on if the program doesn't run. Say so, show the data you read and stop. Don't do the math by hand.
    - Threaten, mention credit reports or lawyers, or make up interest.
    - Offer discounts or more time.
    - Send messages.

    ## What you hand in
    The table from the program, the drafts, the list to call and the list to decide.
    """),
"scripts/overdue.py": DUE.format(doc="Groups invoices by days overdue. Use: overdue.py file.csv YYYY-MM-DD", g0="Not due", g1="1 to 15 days", g2="16 to 45 days", g3="Over 45 days", c0="client", c1="invoice", c2="amount", c3="due", c4="note", dd="days")}
S["es"]["reunion-a-tareas"] = {"SKILL.md": D("""\
    ---
    name: reunion-a-tareas
    description: Convierte las notas o la transcripción de una reunión en decisiones, tareas con responsable y fecha, y preguntas abiertas. Úsala al terminar.
    ---
    # Reunión a tareas

    ## Pasos
    1. Separa lo que se decidió, lo que alguien se comprometió a hacer y lo que quedó abierto.
    2. Para cada tarea anota qué, quién y cuándo, y la frase de las notas de donde sale.
    3. Si nadie la tomó, escribe **sin responsable**. Si no hay fecha, escribe **sin fecha**. No asignes tú.
    4. "Habría que", "sería bueno" y "toca mirar" no son tareas. Van en preguntas abiertas.
    5. Si alguien cambió de opinión durante la reunión, vale lo último. Menciona el cambio.

    ## Lo que no puedes hacer
    - Agregar tareas que te parezcan buena idea.
    - Cambiar "a fin de mes" por un día exacto.
    - Repetir comentarios sobre personas que no tengan que ver con el trabajo.

    ## Qué entregas
    Tres partes: **Decisiones**, **Tareas** (tabla: qué, quién, cuándo, frase) y **Abierto**. Al final, un mensaje de menos de 80 palabras para el equipo.
    """)}
S["en"]["meeting-to-tasks"] = {"SKILL.md": D("""\
    ---
    name: meeting-to-tasks
    description: Turns meeting notes or a transcript into decisions, tasks with owner and date, and open questions. Use it when a meeting ends.
    ---
    # Meeting to tasks

    ## Steps
    1. Separate what was decided, what someone committed to do, and what was left open.
    2. For each task write what, who and when, and the sentence of the notes it comes from.
    3. If nobody took it, write **no owner**. If there is no date, write **no date**. Don't assign it yourself.
    4. "We should", "it would be good" and "someone has to look at" are not tasks. They go in open questions.
    5. If someone changed their mind during the meeting, the last thing counts. Mention the change.

    ## What you can't do
    - Add tasks that seem like a good idea to you.
    - Change "end of the month" for an exact day.
    - Repeat comments about people that have nothing to do with the work.

    ## What you hand in
    Three parts: **Decisions**, **Tasks** (table: what, who, when, sentence) and **Open**. At the end, a message of under 80 words for the team.
    """)}
POL_ES = "# Política de reclamos\nCambia esto por la tuya. La skill solo puede ofrecer lo que está escrito aquí.\n\n- Producto defectuoso: cambio por uno igual, dentro de los 8 días después de la entrega, con una foto.\n- Pedido equivocado: lo recogemos y enviamos el correcto, sin costo.\n- Entrega tarde: pedimos disculpas. No hay compensación.\n- Devolución de dinero: la decide la persona encargada.\n- Persona encargada: escribe aquí nombre y cargo.\n"
POL_EN = "# Claims policy\nChange this for yours. The skill can only offer what is written here.\n\n- Faulty product: exchange for the same one, within 8 days after delivery, with a photo.\n- Wrong order: we pick it up and send the right one, at no cost.\n- Late delivery: we apologize. There is no compensation.\n- Refunds: the person in charge decides.\n- Person in charge: write a name and position here.\n"
S["es"]["responder-reclamo"] = {"SKILL.md": D("""\
    ---
    name: responder-reclamo
    description: Prepara la respuesta a un reclamo usando solo la política escrita del negocio. Úsala cuando un cliente se queje de un producto, una entrega o un cobro.
    ---
    # Responder un reclamo

    La política está en `politica.md`. Cámbiala por la de tu negocio antes de usar esta skill.

    ## Pasos
    1. Resume en una línea qué pasó y qué pide el cliente.
    2. Busca en `politica.md` qué punto aplica y cítalo. Si ninguno aplica, di "no está en la política" y pásalo a la persona encargada.
    3. Revisa qué falta para aplicarlo, como la fecha de entrega o una foto, y pídelo.
    4. Escribe un borrador de menos de 90 palabras: reconoce lo que pasó, di qué sigue y quién responde. Sin excusas.

    ## Lo que no puedes hacer
    - Prometer plata, descuentos, regalos o fechas que no estén en la política.
    - Aceptar o negar culpa cuando alguien se lastimó, se enfermó, o menciona abogados o prensa. Ahí no escribas respuesta: avisa a la persona encargada.
    - Enviar el mensaje.

    ## Qué entregas
    El resumen, el punto de la política, lo que falta, el borrador y lo que una persona debe decidir.
    """), "politica.md": POL_ES}
S["en"]["answer-a-claim"] = {"SKILL.md": D("""\
    ---
    name: answer-a-claim
    description: Prepares the answer to a claim using only the written policy of the business. Use it when a client complains about a product, a delivery or a charge.
    ---
    # Answer a claim

    The policy is in `policy.md`. Change it for the one of your business before you use this skill.

    ## Steps
    1. Sum up in one line what happened and what the client asks for.
    2. Find in `policy.md` which point applies and quote it. If none applies, say "not in the policy" and pass it to the person in charge.
    3. Check what is missing to apply it, like the delivery date or a photo, and ask for it.
    4. Write a draft of under 90 words: acknowledge what happened, say what comes next and who answers. No excuses.

    ## What you can't do
    - Promise money, discounts, gifts or dates that are not in the policy.
    - Accept or deny fault when someone got hurt or sick, or mentions lawyers or the press. Don't write an answer there: tell the person in charge.
    - Send the message.

    ## What you hand in
    The summary, the point of the policy, what is missing, the draft, and what a person has to decide.
    """), "policy.md": POL_EN}
S["es"]["revisar-antes-de-enviar"] = {"SKILL.md": D("""\
    ---
    name: revisar-antes-de-enviar
    description: Revisa un texto antes de que salga. Busca de dónde sale cada cifra, fecha, nombre y promesa. Úsala con correos, propuestas y publicaciones.
    ---
    # Revisar antes de enviar

    ## Pasos
    1. Pide el texto y las fuentes de donde salió (notas, correo, lista de precios). Si no hay fuentes, dilo y marca todo como "sin fuente".
    2. Haz una tabla con cada cifra, fecha, nombre propio y promesa del texto, y la frase exacta de la fuente que la respalda.
    3. Marca cada fila: **está**, **distinto** (la fuente dice otra cosa) o **no está**.
    4. Busca datos personales que no deberían salir, como cédulas, teléfonos, cuentas o información de salud.
    5. Busca compromisos: "garantizamos", "siempre", "sin costo", "antes del viernes". Anota quién tendría que cumplirlos.

    ## Lo que no puedes hacer
    - Corregir el texto sin que te lo pidan. Primero muestra la tabla.
    - Dar algo por cierto porque suena razonable.
    - Decir que el texto está aprobado. Aprobar le toca a una persona.

    ## Qué entregas
    La tabla, los datos personales, los compromisos y las tres cosas que tú mirarías primero.
    """)}
S["en"]["check-before-sending"] = {"SKILL.md": D("""\
    ---
    name: check-before-sending
    description: Checks a text before it goes out. Looks for the source of each figure, date, name and promise. Use it with emails, proposals and posts.
    ---
    # Check before sending

    ## Steps
    1. Ask for the text and the sources it came from (notes, email, price list). If there are no sources, say so and mark everything as "no source".
    2. Make a table with each figure, date, proper name and promise in the text, and the exact sentence of the source that supports it.
    3. Mark each row: **there**, **different** (the source says something else) or **not there**.
    4. Look for personal data that should not go out, like ID numbers, phones, accounts or health information.
    5. Look for commitments: "we guarantee", "always", "at no cost", "before Friday". Write down who would have to keep them.

    ## What you can't do
    - Fix the text without being asked. Show the table first.
    - Take something as true because it sounds reasonable.
    - Say the text is approved. A person approves.

    ## What you hand in
    The table, the personal data, the commitments, and the three things you would look at first.
    """)}
if __name__ == "__main__":
    for lang, sk in S.items():
        for name, files in sk.items():
            desc = files["SKILL.md"].split("description: ")[1].split("\n")[0]
            assert len(desc) <= 200, (name, len(desc))
            z = zipfile.ZipFile(R / lang / f"{name}.zip", "w", zipfile.ZIP_DEFLATED)
            for fn, txt in files.items():
                p = R / lang / name / fn; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(txt, encoding="utf-8"); z.writestr(f"{name}/{fn}", txt)
            z.close()
    print("ok")
