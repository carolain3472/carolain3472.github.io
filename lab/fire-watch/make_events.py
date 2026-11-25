"""Builds events.json: 24 sensor events, each written in 3 ways. The label comes from a fixed rule."""
import json, random
R = random.Random(7)

def label(hot, dry, smoke):
    if smoke: return "brigade"
    if hot and dry: return "drone"
    return "monitor" if hot or dry else "ignore"

kinds = ([(h, d, True) for h, d in [(0,0),(1,0),(0,1),(1,1),(0,0),(1,1)]] + [(1,1,False)]*6 +
         [(1,0,False)]*3 + [(0,1,False)]*3 + [(0,0,False)]*6)
places = ["north ridge","river bend","old quarry","pine slope","east gate","lake path"]
lugares = ["el filo norte","la curva del río","la cantera vieja","la ladera de pinos","la puerta este","el camino del lago"]
extra = ["A family of deer walked by this morning.","The path was repainted last week.","A school group visited yesterday.",
         "The sign near the post is loose.","Somebody left a blue jacket on the bench.","The battery was changed on Monday."]
events = []
for i, (h, d, s) in enumerate(kinds):
    t = R.randint(46, 58) if h else R.randint(19, 40)
    u = R.randint(8, 19) if d else R.randint(28, 75)
    p = R.randrange(6)
    x = extra[R.randrange(6)]
    plain = (f"{x} At the {places[p]} the air is {'very hot' if h else 'at a normal temperature'} and "
             f"{'very dry' if d else 'humid as usual'}, and the camera {'shows smoke' if s else 'shows %s'}.")
    events.append(dict(id=i, label=label(h, d, s), text=dict(
        numbers=f"Sensor at the {places[p]}. Temperature {t} °C. Humidity {u}%. Camera: {'smoke visible' if s else 'no smoke'}.",
        spanish=f"Sensor en {lugares[p]}. Temperatura {t} °C. Humedad {u} %. Cámara: {'se ve humo' if s else 'sin humo'}.",
        words=plain if s else plain % "nothing unusual",
        words_no_echo=plain if s else plain % "no smoke")))
R.shuffle(events)
schema = dict(
    prompt="Which action does the rule book say to take?",
    options=[
        dict(label="ignore", description="No smoke, temperature below 45 °C and humidity above 20%. Nothing is unusual."),
        dict(label="monitor", description="No smoke, and only one problem: very hot (45 °C or more) or very dry (20% or less), but not both."),
        dict(label="drone", description="No smoke, and both problems at once: very hot (45 °C or more) and very dry (20% or less)."),
        dict(label="brigade", description="The camera sees smoke, whatever the temperature and the humidity are.")])
json.dump(dict(schema=schema, events=events), open("events.json", "w"), ensure_ascii=False, indent=1)
