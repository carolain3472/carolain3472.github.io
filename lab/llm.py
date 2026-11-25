"""One call to a cloud model through the Claude Code command line (no tools, short system prompt)."""
import json, subprocess, tempfile
def ask(prompt, system, model):
    for _ in range(3):
        r = subprocess.run(["claude","-p",prompt,"--model",model,"--tools","","--system-prompt",system,"--strict-mcp-config",
            "--setting-sources","","--disable-slash-commands","--no-session-persistence","--output-format","json"],
            capture_output=True, text=True, cwd=tempfile.gettempdir())
        try:
            d = json.loads(r.stdout); return d["result"], d["duration_api_ms"], d["total_cost_usd"]
        except Exception: pass
    return "", 0, 0.0
