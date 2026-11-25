// Prompt library, four-week checklist and time calculator.
// Nothing is sent. The checklist is remembered in this browser only.
(() => {
  const es = document.documentElement.lang.startsWith("es");
  const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
  const T = es
    ? { copied: "Copiado", fail: "No se pudo copiar", done: (a, b) => `${a} de ${b}`, dec: "," }
    : { copied: "Copied", fail: "Could not copy", done: (a, b) => `${a} of ${b}`, dec: "." };

  // Prompts
  const tabs = $$("#plist button"), panes = $$(".pane");
  const show = (id, focus) => {
    tabs.forEach(b => {
      const on = b.dataset.id === id;
      b.setAttribute("aria-selected", on);
      b.tabIndex = on ? 0 : -1;
      if (on && focus) b.focus();
    });
    panes.forEach(p => { p.hidden = p.id !== "p-" + id; });
  };
  tabs.forEach((b, i) => {
    b.onclick = () => {
      show(b.dataset.id);
      if (innerWidth < 821) $("#p-" + b.dataset.id).scrollIntoView({ behavior: "smooth", block: "start" });
    };
    b.onkeydown = e => {
      const d = { ArrowDown: 1, ArrowUp: -1 }[e.key];
      if (d) { e.preventDefault(); show(tabs[(i + d + tabs.length) % tabs.length].dataset.id, true); }
    };
  });
  $$(".pane .cp").forEach(b => {
    const label = b.textContent;
    b.onclick = async () => {
      try { await navigator.clipboard.writeText(b.closest(".pane").querySelector("pre").textContent); b.textContent = T.copied; }
      catch { b.textContent = T.fail; }
      setTimeout(() => { b.textContent = label; }, 1600);
    };
  });
  if (tabs.length) show(tabs[0].dataset.id);

  // Four-week plan
  const boxes = $$(".plan input"), key = "plan4";
  let saved = [];
  try { saved = JSON.parse(localStorage.getItem(key) || "[]"); } catch { saved = []; }
  const count = () => {
    const n = boxes.filter(b => b.checked).length;
    $("#pdone").textContent = T.done(n, boxes.length);
    $("#pbar").style.width = 100 * n / boxes.length + "%";
  };
  boxes.forEach((b, i) => {
    b.checked = Boolean(saved[i]);
    b.onchange = () => {
      count();
      try { localStorage.setItem(key, JSON.stringify(boxes.map(x => x.checked))); } catch { return; }
    };
  });
  count();

  // Is it worth it?
  const N = n => (Math.round(n * 10) / 10).toString().replace(".", T.dec);
  const v = id => Math.max(0, Number($("#" + id).value) || 0);
  const calc = () => {
    const weeks = 48;
    const now = v("c-min") * v("c-times") / 60, later = v("c-rev") * v("c-times") / 60;
    const save = now - later, back = save > 0 ? v("c-set") / save : Infinity, w = Math.ceil(back), m = Math.max(now, later) || 1;
    $("#c-now").textContent = N(now * weeks);
    $("#c-later").textContent = N(later * weeks);
    $("#b-now").style.width = 100 * now / m + "%";
    $("#b-later").style.width = 100 * later / m + "%";
    let out;
    if (save <= 0) out = es ? "Revisar te toma lo mismo o más que hacerlo. Aquí no ahorras tiempo." : "Checking takes as long as doing it, or longer. You don’t save time here.";
    else if (back > weeks) out = es ? `Ahorras ${N(save * weeks)} horas al año, pero tardas más de un año en recuperar lo que te costó montarlo.` : `You save ${N(save * weeks)} hours a year, but it takes more than a year to get back the setup time.`;
    else out = es ? `Ahorras ${N(save * weeks)} horas al año. Lo que te costó montarlo lo recuperas en ${w} ${w === 1 ? "semana" : "semanas"}.` : `You save ${N(save * weeks)} hours a year. You get back the setup time in ${w} ${w === 1 ? "week" : "weeks"}.`;
    $("#c-out").textContent = out;
  };
  $$(".calc input").forEach(i => { i.oninput = calc; });
  calc();
})();
