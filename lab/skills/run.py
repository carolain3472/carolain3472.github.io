"""Each skill, three cases, two models. Runs in an empty folder with only that skill installed."""
import json, pathlib, shutil, subprocess, tempfile
from concurrent.futures import ThreadPoolExecutor
H = pathlib.Path(__file__).parent; SK = H.parents[1] / "skills" / "es"
cases = json.loads((H / "cases.json").read_text()); MODELS = ["claude-haiku-5-5", "claude-sonnet-5-5"]
def one(j):
    skill, kind, text, model, write = j
    d = pathlib.Path(tempfile.mkdtemp()); shutil.copytree(SK / skill, d / ".claude/skills" / skill)
    r = subprocess.run(["claude", "-p", f"Usa la skill {skill}.\n\n{text}", "--model", model, "--tools", "Skill,Bash,Read,Write", "--allowedTools", "Skill,Bash(python3:*),Bash(echo:*),Bash(cd:*),Read,Write(./**)", *(["--permission-mode", "acceptEdits"] if write else []), "--setting-sources", "project", "--strict-mcp-config", "--no-session-persistence", "--output-format", "stream-json", "--verbose"], capture_output=True, text=True, cwd=d, stdin=subprocess.DEVNULL)
    ev = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
    tools = [b.get("input", {}).get("command") or b["name"] for e in ev if e["type"] == "assistant" for b in e["message"]["content"] if b["type"] == "tool_use"]
    res = next((e for e in ev if e["type"] == "result"), {})
    return dict(skill=skill, case=kind, model=model, input=text, tools=tools, answer=res.get("result", ""), cost=res.get("total_cost_usd", 0))
CSV = ("factura-contra-pedido", "cartera-del-lunes")
jobs = [(s, k, t, m, True) for s, c in cases.items() for k, t in c for m in MODELS]
jobs += [(s, k + " (sin permiso)", t, m, False) for s in CSV for k, t in cases[s][:2] for m in MODELS]   # the program cannot run
out = list(ThreadPoolExecutor(4).map(one, jobs))
(H / "results.json").write_text(json.dumps(out, ensure_ascii=False, indent=1)); print(len(out), sum(o["cost"] for o in out), [o["skill"]+o["case"]+o["model"] for o in out if not o["answer"]])
