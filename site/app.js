/* Ninety Six Wildcats brand kit site. Reads window.BRAND (site/data.js). */
(() => {
  const B = window.BRAND;
  const $ = (s, el = document) => el.querySelector(s);
  const el = (tag, attrs = {}, ...kids) => {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === "class") n.className = v;
      else if (k === "text") n.textContent = v;
      else if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
      else if (v !== false && v != null) n.setAttribute(k, v === true ? "" : v);
    }
    for (const kid of kids) if (kid != null) n.append(kid);
    return n;
  };

  /* ---------- color math ---------- */
  const lum = (hex) => {
    const c = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255)
      .map((v) => (v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4));
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
  };
  const ratio = (a, b) => {
    const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p);
    return (x + 0.05) / (y + 0.05);
  };
  const HEX = Object.fromEntries(B.colors.map((c) => [c.id, c.hex]));
  const BGS = [
    { id: "white", name: "White", hex: ["#FFFFFF"] },
    { id: "cream", name: "Cream", hex: [HEX.cream] },
    { id: "maroon", name: "Maroon", hex: [HEX.maroon] },
    { id: "gradient", name: "Gradient", hex: [B.gradient.top, B.gradient.bottom] },
    { id: "black", name: "Black", hex: ["#000000"] },
  ];
  // worst case across the background (the gradient's lightest or darkest end)
  const worst = (fg, bg) => Math.min(...bg.hex.map((h) => ratio(fg, h)));
  const fmt = (r) => `${r.toFixed(1)} : 1`;

  /* ---------- toast ---------- */
  let toastTimer;
  const toast = (msg) => {
    const t = $("#toast");
    t.textContent = msg;
    t.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => t.classList.remove("show"), 1600);
  };
  const copy = async (text) => {
    try { await navigator.clipboard.writeText(text); toast(`Copied ${text}`); }
    catch { toast(text); }
  };

  /* ---------- top-level links ---------- */
  $("#zip-link").href = B.zip;
  $("#pdf-link").href = B.guidelines;
  $("#pdf-link-2").href = B.guidelines;

  /* ---------- logo finder ---------- */
  const state = { mark: "primary", team: "", layout: "horizontal", color: "cream", bg: "maroon" };
  const markById = Object.fromEntries(B.marks.map((m) => [m.id, m]));
  const teamById = Object.fromEntries(B.teams.map((t) => [t.id, t]));

  // logo list, grouped
  const choices = $("#mark-choices");
  let group = null;
  for (const m of B.marks) {
    if (m.group !== group) {
      group = m.group;
      choices.append(el("p", { class: "group-label", text: group }));
    }
    choices.append(el("label", { class: "choice" },
      el("input", { type: "radio", name: "mark", value: m.id }),
      el("span", { text: m.name })));
  }
  const sel = $("#team-select");
  for (const t of B.teams) sel.append(el("option", { value: t.id, text: t.name }));

  const swatch = (name, id, label, css) =>
    el("label", { class: "swatch" },
      el("input", { type: "radio", name, value: id }),
      el("span", { class: "swatch-ring" }, el("b", { style: `background:${css}` })),
      el("em", { text: label }));
  for (const c of B.colors) $("#color-choices").append(swatch("color", c.id, c.name, c.hex));
  for (const b of BGS) {
    const css = b.hex.length > 1 ? `linear-gradient(${b.hex[0]}, ${b.hex[1]})` : b.hex[0];
    $("#bg-choices").append(swatch("bg", b.id, b.name, css));
  }

  const current = () => {
    if (state.team) {
      const t = teamById[state.team];
      return {
        name: `${t.name} (${state.layout})`,
        use: state.layout === "square"
          ? "Square layout for profile pictures and square spaces."
          : "Team logo for shirts, posters, schedules, and social media.",
        min: state.layout === "square" ? "1 in / 140 px" : "1 in / 110 px",
        path: (state.layout === "square" ? t.square : t.horizontal).replace("{color}", state.color),
      };
    }
    const m = markById[state.mark];
    return { name: m.name, use: m.use, min: m.min, path: m.path.replace("{color}", state.color) };
  };

  const render = (share = true) => {
    const f = $("#finder-form");
    if (!state.team) f.mark.value = state.mark;
    else for (const r of f.mark) r.checked = false;
    sel.value = state.team;
    sel.classList.toggle("active", !!state.team);
    $("#layout-seg").hidden = !state.team;
    f.layout.value = state.layout;
    f.color.value = state.color;
    f.bg.value = state.bg;

    const cur = current();
    const stage = $("#stage");
    stage.dataset.bg = state.bg;
    const img = $("#stage-img");
    img.src = `${cur.path}.svg`;
    img.alt = `${cur.name} logo in ${state.color}`;

    const bg = BGS.find((b) => b.id === state.bg);
    const r = worst(HEX[state.color], bg);
    const v = $("#verdict");
    const lightBg = ["white", "cream"].includes(state.bg);
    v.className = "verdict tag " + (r >= 4.5 ? (lightBg ? "ok-light" : "ok-dark") : "bad");
    v.textContent = r >= 4.5 ? `Approved · ${fmt(r)}` : `Not allowed · ${fmt(r)}`;

    $("#sel-name").textContent = cur.name;
    $("#sel-use").textContent = cur.use;
    $("#sel-min").textContent = `Minimum width: ${cur.min}`;
    const file = cur.path.split("/").pop();
    $("#sel-file").textContent = `${file}.svg / .pdf / .png`;
    const dl = $("#downloads");
    dl.replaceChildren(...["svg", "pdf", "png"].map((ext, i) =>
      el("a", { class: `btn btn-small ${i ? "btn-ink" : "btn-maroon"}`, href: `${cur.path}.${ext}`, download: `${file}.${ext}` },
        ext.toUpperCase())));

    if (!share) return;
    const params = new URLSearchParams({ color: state.color, bg: state.bg });
    if (state.team) { params.set("team", state.team); params.set("layout", state.layout); }
    else params.set("logo", state.mark);
    history.replaceState(null, "", `#logos?${params}`);
  };

  $("#finder-form").addEventListener("change", (e) => {
    const t = e.target;
    if (t.name === "mark") { state.mark = t.value; state.team = ""; }
    else if (t.id === "team-select") {
      state.team = t.value;
      if (!t.value) state.mark = state.mark || "primary";
    } else if (t.name === "layout") state.layout = t.value;
    else if (t.name === "color") state.color = t.value;
    else if (t.name === "bg") state.bg = t.value;
    render();
  });

  // restore from a shared link: #logos?logo=icon&color=maroon&bg=cream
  const fromHash = () => {
    const h = location.hash;
    if (!h.startsWith("#logos?")) return;
    const p = new URLSearchParams(h.slice(7));
    if (p.get("team") && teamById[p.get("team")]) {
      state.team = p.get("team");
      state.layout = p.get("layout") === "square" ? "square" : "horizontal";
    } else if (markById[p.get("logo")]) { state.mark = p.get("logo"); state.team = ""; }
    if (HEX[p.get("color")]) state.color = p.get("color");
    if (BGS.some((b) => b.id === p.get("bg"))) state.bg = p.get("bg");
  };
  fromHash();
  render(false);
  if (location.hash.startsWith("#logos?")) $("#logos").scrollIntoView();

  /* ---------- profile pictures ---------- */
  $("#profiles").append(...B.profiles.map((p) =>
    el("a", { class: "profile", href: p.path, download: true },
      el("img", { src: p.path, alt: "", loading: "lazy", width: 120, height: 120 }), p.name)));

  /* ---------- teams ---------- */
  const grid = $("#team-grid");
  const cards = B.teams.map((t) => {
    const card = el("article", { class: "team", "data-name": t.name.toLowerCase() },
      el("button", {
        class: "team-open", type: "button", "aria-label": `Open ${t.name} in the logo finder`,
        onclick: () => {
          Object.assign(state, { team: t.id, layout: "horizontal", color: "maroon", bg: "cream" });
          render();
          $("#logos").scrollIntoView();
        },
      }, el("img", { src: t.horizontal.replace("{color}", "maroon") + ".svg", alt: "", loading: "lazy" })),
      el("div", { class: "team-foot" },
        el("strong", { text: t.name }),
        el("a", { href: t.profile, download: true, text: "Profile picture" })));
    grid.append(card);
    return card;
  });
  const empty = el("p", { class: "empty", text: "No team or club matches that search.", hidden: true });
  grid.after(empty);
  const updateCount = (n) => {
    $("#team-count").textContent = `${n} of ${B.teams.length} teams and clubs`;
  };
  updateCount(B.teams.length);
  $("#team-search").addEventListener("input", (e) => {
    const q = e.target.value.trim().toLowerCase();
    let n = 0;
    for (const c of cards) {
      const hit = !q || c.dataset.name.includes(q);
      c.hidden = !hit;
      n += hit;
    }
    empty.hidden = n > 0;
    updateCount(n);
  });

  /* ---------- colors ---------- */
  const rgb = (hex) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16)).join(", ");
  const copyRow = (label, value) =>
    el("button", { class: "copy", type: "button", onclick: () => copy(value), "aria-label": `Copy ${label} ${value}` },
      el("span", { text: `${label}  ${value}` }), el("span", { text: "Copy" }));
  const cg = $("#color-grid");
  for (const c of B.colors) {
    cg.append(el("div", { class: "color" },
      el("div", { class: "color-chip", style: `background:${c.hex}` }),
      el("div", { class: "color-body" },
        el("strong", { text: c.name }), copyRow("HEX", c.hex), copyRow("RGB", rgb(c.hex)))));
  }
  cg.append(el("div", { class: "color" },
    el("div", { class: "color-chip", style: `background:linear-gradient(${B.gradient.top}, ${B.gradient.bottom})` }),
    el("div", { class: "color-body" },
      el("strong", { text: "TV gradient" }), copyRow("Top", B.gradient.top), copyRow("Bottom", B.gradient.bottom))));

  const pairs = [
    ["Cream", "cream", "Maroon", [HEX.maroon]], ["White", "white", "Maroon", [HEX.maroon]],
    ["Maroon", "maroon", "Cream", [HEX.cream]], ["Maroon", "maroon", "White", ["#FFFFFF"]],
    ["Black", "black", "Cream", [HEX.cream]], ["Cream", "cream", "TV gradient", [B.gradient.top, B.gradient.bottom]],
    ["Maroon", "maroon", "TV gradient", [B.gradient.top, B.gradient.bottom]], ["Maroon", "maroon", "Black", ["#000000"]],
    ["Cream", "cream", "White", ["#FFFFFF"]],
  ];
  const tb = $("#pairs tbody");
  for (const [fgName, fg, bgName, bgHex] of pairs) {
    const r = worst(HEX[fg], { hex: bgHex });
    const bgCss = bgHex.length > 1 ? `linear-gradient(${bgHex[0]}, ${bgHex[1]})` : bgHex[0];
    tb.append(el("tr", {},
      el("td", {}, el("span", { class: "pair" },
        el("span", { class: "pair-chip", style: `background:${bgCss};color:${HEX[fg]}`, text: "96" }),
        `${fgName} on ${bgName === "TV gradient" ? bgName : bgName.toLowerCase()}`)),
      el("td", { text: fmt(r) }),
      el("td", {}, el("span", { class: r >= 4.5 ? "use-ok" : "use-no", text: r >= 4.5 ? "Approved" : "Not allowed" }))));
  }

  /* ---------- templates ---------- */
  $("#template-grid").append(...B.templates.map((t) =>
    el("article", { class: "template" },
      el("div", { class: "template-frame" },
        el("img", { src: t.thumb, alt: `${t.name} example`, loading: "lazy", width: t.tw, height: t.th })),
      el("h3", { text: t.name }),
      el("p", { class: "meta", text: t.size }),
      el("div", { class: "template-links" },
        ...t.files.map((f) => el("a", { href: f.path, download: true, text: f.label }))))));

  /* ---------- guideline pages + viewer ---------- */
  const viewer = $("#viewer");
  let pageIdx = 0;
  const show = (i) => {
    pageIdx = (i + B.pages.length) % B.pages.length;
    const p = B.pages[pageIdx];
    $("#viewer-img").src = p.full;
    $("#viewer-img").alt = `Guidelines page ${p.n}: ${p.title}`;
    $("#viewer-title").textContent = `Page ${p.n} of ${B.pages.length}: ${p.title}`;
  };
  $("#pages").append(...B.pages.map((p, i) =>
    el("li", {}, el("button", {
      class: "page-btn", type: "button",
      onclick: () => { show(i); viewer.showModal(); },
    },
    el("img", { src: p.thumb, alt: "", loading: "lazy", width: 172, height: 222 }),
    el("span", {}, el("b", { text: String(p.n) }), p.title)))));
  $("#viewer-prev").addEventListener("click", () => show(pageIdx - 1));
  $("#viewer-next").addEventListener("click", () => show(pageIdx + 1));
  $("#viewer-close").addEventListener("click", () => viewer.close());
  viewer.addEventListener("click", (e) => { if (e.target === viewer) viewer.close(); });
  viewer.addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight") show(pageIdx + 1);
    if (e.key === "ArrowLeft") show(pageIdx - 1);
  });
})();
