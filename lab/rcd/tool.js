// Read, calculate, decide: a small board to sort the steps of a process.
// Everything stays in the page. Nothing is sent or stored.
(() => {
  const es = document.documentElement.lang.startsWith("es");
  const X = es ? {
    keys: ["L", "C", "D"], names: ["Leer", "Calcular", "Decidir"],
    tips: ["Prueba la IA aquí primero, y deja el original al lado de la respuesta para que alguien pueda revisarla.", "Usa un programa. Puede que ya exista en una hoja de cálculo.", "Aquí se queda una persona, con nombre y cargo. La IA puede prepararle la información."],
    ex: [["Leer el pedido que llega por correo", 0], ["Calcular el total con descuentos e impuestos", 1], ["Aprobar el precio para un cliente nuevo", 2], ["Escribir la respuesta al cliente", 0]],
    of: "de", kind: "Tipo de paso: ", rm: "Quitar paso: ", none: "Ningún paso",
    warn: t => `Después de «${t}» nadie revisa nada. Si ese texto le va a llegar a alguien, agrega una persona al final.`,
    copy: "Copiar el resultado", ok: "Copiado", no: "No se pudo copiar"
  } : {
    keys: ["R", "C", "D"], names: ["Read", "Calculate", "Decide"],
    tips: ["Try AI here first, and keep the original next to the answer so someone can check it.", "Use a program. It may already exist in a spreadsheet.", "Keep a person here, with a name and a position. AI can prepare the information."],
    ex: [["Read the order that arrives by email", 0], ["Calculate the total with discounts and taxes", 1], ["Approve the price for a new client", 2], ["Write the answer to the client", 0]],
    of: "of", kind: "Type of step: ", rm: "Remove step: ", none: "No steps",
    warn: t => `After “${t}” nobody checks anything. If that text goes out to someone, add a person at the end.`,
    copy: "Copy the result", ok: "Copied", no: "Could not copy"
  };
  const $ = id => document.getElementById(id);
  const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
  let S = X.ex.map(x => [...x]);

  function line() {
    const svg = $("path"), box = $("board").getBoundingClientRect();
    const pts = [...document.querySelectorAll("#steps [aria-pressed=true] i")].map(d => { const r = d.getBoundingClientRect(); return [r.x + r.width / 2 - box.x, r.y + r.height / 2 - box.y]; });
    svg.setAttribute("viewBox", `0 0 ${box.width} ${box.height}`);
    svg.firstElementChild.setAttribute("d", pts.map(([x, y], i) => {
      if (!i) return `M${x} ${y}`;
      const [a, b] = pts[i - 1], m = (b + y) / 2;
      return `C${a} ${m} ${x} ${m} ${x} ${y}`;
    }).join(" "));
  }

  function draw() {
    const ol = $("steps"); ol.textContent = "";
    S.forEach((s, i) => {
      const li = el("li"), t = el("div", "t"), x = el("button", "x", "×");
      t.append(el("span", "", s[0]));
      x.type = "button"; x.setAttribute("aria-label", X.rm + s[0]);
      x.onclick = () => { S.splice(i, 1); draw(); $("new").focus(); };
      t.append(x); li.append(t);
      X.names.forEach((n, k) => {
        const b = el("button", "c k" + k), d = el("i", "", s[1] === k ? i + 1 : "");
        b.type = "button"; b.setAttribute("aria-label", X.kind + s[0] + ". " + n); b.setAttribute("aria-pressed", s[1] === k);
        b.append(d); b.onclick = () => { s[1] = k; draw(); $("steps").children[i].querySelectorAll(".c")[k].focus({ preventScroll: true }); };
        li.append(b);
      });
      ol.append(li);
    });
    X.names.forEach((n, k) => {
      const c = S.filter(s => s[1] === k).length, f = $("sum" + k);
      f.textContent = ""; f.classList.toggle("off", !c);
      f.append(el("b", "", c ? `${c} ${X.of} ${S.length}` : X.none), el("span", "", X.tips[k]));
    });
    const w = $("warn"), j = S.findIndex((s, a) => s[1] === 0 && !S.slice(a + 1).some(z => z[1] !== 0));
    w.hidden = j < 0; w.textContent = j < 0 ? "" : X.warn(S[j][0]);
    line();
  }
  $("add").onsubmit = e => { e.preventDefault(); const v = $("new").value.trim(); if (v) { S.push([v, 0]); $("new").value = ""; draw(); } };
  $("clear").onclick = () => { S = []; draw(); $("new").focus(); };
  $("copy").onclick = async () => {
    const used = X.names.map((n, k) => [n, S.filter(s => s[1] === k).length, X.tips[k]]).filter(u => u[1]);
    const txt = S.map((s, i) => `${i + 1}. ${s[0]} [${X.names[s[1]]}]`).join("\n") + "\n\n" + used.map(u => `${u[0]} (${u[1]} ${X.of} ${S.length}). ${u[2]}`).join("\n") + ($("warn").hidden ? "" : "\n\n" + $("warn").textContent);
    try { await navigator.clipboard.writeText(txt); $("copy").textContent = X.ok; } catch { $("copy").textContent = X.no; }
    setTimeout(() => $("copy").textContent = X.copy, 1600);
  };
  new ResizeObserver(line).observe($("board"));
  document.fonts && document.fonts.ready.then(line);
  draw();
})();
