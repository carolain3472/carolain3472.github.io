"""Second version of the voice prompt, after the first one invented what clients say."""
import json, runpy, pathlib, sys
sys.argv = ["x"]; src = (pathlib.Path(__file__).parent / "run.py").read_text().split("jobs =")[0]
exec(src.replace("__file__", repr(str(pathlib.Path(__file__)))))
def one(j):
    m, i = j; a, _, c = ask(fill("voice"), "Eres un asistente. Responde en español.", m); return dict(id="voice2", model=m, run=i, answer=a, cost=c)
out = list(ThreadPoolExecutor(4).map(one, [(m, i) for m in ("claude-haiku-5-5", "claude-sonnet-5-5") for i in range(10)]))
(H / "results_voice2.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
for o in out:
    a = o["answer"]; k = a.find("ublicaci"); print(o["model"][7:], o["run"], a[k:k+300].replace("\n", " "))
