"""Cloud side of the test. Uses the Claude Code command line, one call per decision."""
import json, subprocess, sys, time, tempfile
from concurrent.futures import ThreadPoolExecutor
model = sys.argv[1]
STYLES = ("numbers","spanish","words","words_no_echo")
D = json.load(open("events.json")); opts = D["schema"]["options"]
def ask(job):
    e, style = job
    q = (f"{e['text'][style]}\n\n{D['schema']['prompt']}\n" +
         "\n".join(f"{o['label']}: {o['description']}" for o in opts) + "\n\nReply with one word: " + ", ".join(o["label"] for o in opts) + ".")
    r = subprocess.run(["claude","-p",q,"--model",model,"--tools","","--system-prompt","You pick one option from a closed list. Reply with the option name only.",
        "--strict-mcp-config","--setting-sources","","--disable-slash-commands","--no-session-persistence","--output-format","json"],
        capture_output=True, text=True, cwd=tempfile.gettempdir())
    d = json.loads(r.stdout); a = d["result"].strip().lower().strip(".")
    return dict(id=e["id"], style=style, truth=e["label"], answer=a, ms=d["duration_api_ms"], usd=d["total_cost_usd"])
jobs = [(e, s) for e in D["events"] for s in STYLES]
with ThreadPoolExecutor(4) as ex: rows = list(ex.map(ask, jobs))
json.dump(dict(engine=model, where="cloud", rows=rows), open(f"results_{model}.json","w"), indent=1)
for s in STYLES:
    x=[r for r in rows if r["style"]==s]; print(model, s, sum(r["answer"]==r["truth"] for r in x), "/", len(x))
import statistics as st; print("median ms", st.median(r["ms"] for r in rows), "usd", round(sum(r["usd"] for r in rows),4))
