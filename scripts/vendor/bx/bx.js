// BX kit: Branch-Education-style lesson scenes on one paused GSAP timeline. Shipped by learn.py (scripts/vendor/bx/).
// Every animated helper takes a start time t first (seconds, usually T(line, fraction)) and adds tweens to the timeline.
// Coordinates: geometry is in WORLD pixels (the camera moves and zooms the world). Text sizes (`size`) are SCREEN pixels
// at the camera zoom when the text appears, so labels read the same size at any zoom.
// Seek-safe: no timers, no unseeded randomness (BX.rand is seeded), counters write text in onUpdate.
const BX = (() => {
  const NS = "http://www.w3.org/2000/svg";
  const C = { cyan: "#38d6e6", green: "#4cf04a", yellow: "#f2e93a", orange: "#f29a1a", red: "#ff5a4d",
              copper: "#c8825a", steel: "#8b969e", text: "#e9eef2", muted: "#7f8a94", plate: "#3a3f44", blue: "#5b8fb0",
              silver: "#c9d1d7", beige: "#d8c35a" };
  // colour roles, the same for every topic: good/active, bad/failure, what moves, energy/heat/hazard, labels, structure
  Object.assign(C, { good: C.green, bad: C.red, move: C.orange, energy: C.yellow, label: C.cyan, structure: C.steel });
  let tl, art, labels, hud, front, defs;
  const placed = [];   // obstacles for auto-placement: {r: screen rect} or {w: world rect}, with their visible time span

  // init(tl, {bg: "studio"|"floor"|"board", section, basis}): builds background, world, HUD and footer layers inside #stage.
  // The vignette sits below every content layer (above text it trips HyperFrames' text_occluded error).
  function init(timeline, o) {
    tl = timeline; o = o || {};
    if (!document.getElementById("bx-world")) {
      const stage = document.getElementById("stage") || document.querySelector('[data-composition-id="main"]');
      const bg = { floor: '<div class="bx-sky"></div><div class="bx-floor"></div>', board: '<div class="bx-board"></div>', studio: '<div class="bx-studio"></div>' }[o.bg || "board"];
      const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");
      stage.insertAdjacentHTML("afterbegin", bg + '<div class="bx-vignette"></div>'
        + '<div class="bx-world" id="bx-world"><svg class="bx-layer" id="bx-art"></svg><div id="bx-labels"></div></div>'
        + '<div class="bx-hud" id="bx-hud"></div><svg class="bx-layer" id="bx-front"></svg>'
        + (o.section ? `<div class="bx-section">${esc(o.section)}</div>` : "")
        + (o.basis ? `<div class="bx-basis">${esc(o.basis)}</div>` : ""));
    }
    const fl = document.querySelector(".bx-floor"); if (fl && !fl.firstChild) floorGrid(fl);
    art = document.getElementById("bx-art"); labels = document.getElementById("bx-labels");
    hud = document.getElementById("bx-hud"); front = document.getElementById("bx-front");
    // the section tag orients the viewer during the first line, then fades so it never collides with the moving world
    if (o.section) { const tEnd = window.LEARN && LEARN.start.length > 1 ? LEARN.start[1] : 1e9;
      placed.push({ r: [0, 0, 760, 110], t0: 0, t1: tEnd });
      if (tEnd < 1e9) tl.to(stageEl().querySelector(".bx-section"), { opacity: 0, duration: 0.5 }, tEnd - 0.5); }
    if (o.basis) placed.push({ r: [0, 1020, 1920, 1080], t0: 0, t1: 1e9 });
  }
  // The grid floor as a flat SVG drawn in perspective (same geometry as CSS perspective(1100px) rotateX(64deg) from y = 330).
  // A real CSS 3D transform was composited above the world layer by the HyperFrames renderer (not by snapshot).
  function floorGrid(el) {
    const P = 1100, c = Math.cos(64 * Math.PI / 180), s = Math.sin(64 * Math.PI / 180), Y0 = 330, G = 120;
    const k = (v) => P / (P - v * s), Y = (v) => Y0 + v * c * k(v), X = (u, v) => 960 + (u - 960) * k(v);
    let vMax = 0; while (Y(vMax) < 1140) vMax += 4;
    const svg = document.createElementNS(NS, "svg"); svg.setAttribute("width", 1920); svg.setAttribute("height", 1080);
    const add = (tag, a) => { const e = document.createElementNS(NS, tag); for (const n in a) e.setAttribute(n, a[n]); svg.appendChild(e); };
    add("rect", { x: 0, y: Y0, width: 1920, height: 1080 - Y0, fill: "#2a2e31" });
    for (let v = G; v < vMax; v += G) add("line", { x1: 0, x2: 1920, y1: Y(v), y2: Y(v), stroke: "#3a3f43", "stroke-width": 2 * Math.min(2, k(v)) });
    for (let u = -1400 - 40 * G; u <= 3320 + 40 * G; u += G) { const x0 = X(u, 0), x1 = X(u, vMax);
      if (Math.max(x0, x1) < -200 || Math.min(x0, x1) > 2120) continue;
      add("line", { x1: x0, y1: Y0, x2: x1, y2: Y(vMax), stroke: "#3a3f43", "stroke-width": 2 }); }
    el.appendChild(svg);
  }
  const stageEl = () => document.getElementById("stage") || document.querySelector('[data-composition-id="main"]');
  function S(tag, a, parent) { const e = document.createElementNS(NS, tag); for (const k in a) e.setAttribute(k, a[k]); (parent || art).appendChild(e); return e; }
  function D(cls, css, html, parent) { const d = document.createElement("div"); d.className = cls; Object.assign(d.style, css || {}); if (html != null) d.innerHTML = html; (parent || labels).appendChild(d); return d; }
  function H(cls, css, html) { return D(cls, css, html, hud); }
  function FS(tag, a) { return S(tag, a, front); }   // svg drawn above labels (screen space)
  function def() { if (!defs) defs = S("defs", {}); return defs; }

  // ---- camera: one state on the world wrapper. It remembers every move, so helpers know the zoom at any time ----
  const keys = [];                         // {t, dur, ease, from: {x, y, s}, to: {x, y, s}}
  let base = { x: 0, y: 0, s: 1 };
  const st = (cx, cy, z) => ({ x: 960 - cx * z, y: 540 - cy * z, s: z });
  function state(t) {
    let s = base;
    for (const k of keys) {
      if (t >= k.t + k.dur) s = k.to;
      else if (t > k.t) { const p = gsap.parseEase(k.ease)((t - k.t) / k.dur); s = { x: k.from.x + (k.to.x - k.from.x) * p, y: k.from.y + (k.to.y - k.from.y) * p, s: k.from.s + (k.to.s - k.from.s) * p }; }
    }
    return s;
  }
  const cam = {
    set(cx, cy, z) { base = st(cx, cy, z); gsap.set("#bx-world", { x: base.x, y: base.y, scale: base.s }); },
    move(t, cx, cy, z, dur, ease) { dur = dur || 2; ease = ease || "power2.inOut";
      const to = st(cx, cy, z); keys.push({ t, dur, ease, from: state(t), to }); keys.sort((a, b) => a.t - b.t);
      tl.to("#bx-world", { x: to.x, y: to.y, scale: to.s, duration: dur, ease }, t); },
    // frame a world rect [x, y, w, h] (or an SVG/HTML element) so it fills the screen, with `pad` (0..1) margin
    frame(t, r, o) { o = o || {}; r = rectOf(r); const pad = o.pad == null ? 0.18 : o.pad;
      const z = Math.min(1920 * (1 - pad) / r[2], 1080 * (1 - pad) / r[3], o.max || 6);
      if (t == null) cam.set(r[0] + r[2] / 2, r[1] + r[3] / 2, z); else cam.move(t, r[0] + r[2] / 2, r[1] + r[3] / 2, z, o.dur, o.ease); },
    zoom(t) { return state(t).s; },
    // the zoom a label should be sized for: after any camera move running at t has finished
    settled(t) { let u = t; for (const k of keys) if (u >= k.t && u < k.t + k.dur) u = k.t + k.dur; return state(u).s; },
    toScreen(t, x, y) { const s = state(t); return [s.x + x * s.s, s.y + y * s.s]; },
  };
  function rectOf(r) {
    if (Array.isArray(r)) return r;
    if (r.getBBox) { const b = r.getBBox(); return [b.x, b.y, b.width, b.height]; }
    return [r.offsetLeft, r.offsetTop, r.offsetWidth, r.offsetHeight];
  }

  // ---- appearance ----
  function hideNow(els) { gsap.set(els, { opacity: 0 }); }
  function show(t, els, o) { o = o || {}; hideNow(els);
    if (o.pop) tl.fromTo(els, { opacity: 0, scale: 0.85, transformOrigin: "50% 50%" }, { opacity: 1, scale: 1, duration: o.dur || 0.4, ease: "back.out(1.8)", stagger: o.stagger || 0 }, t);
    else if (o.rise) tl.fromTo(els, { opacity: 0, y: o.rise }, { opacity: 1, y: 0, duration: o.dur || 0.45, ease: "power2.out", stagger: o.stagger || 0 }, t);
    else tl.to(els, { opacity: o.to == null ? 1 : o.to, duration: o.dur || 0.4, stagger: o.stagger || 0 }, t); }
  function hide(t, els, dur) { tl.to(els, { opacity: 0, duration: dur || 0.3 }, t); }
  function dim(t, els, to, dur) { tl.to(els, { opacity: to == null ? 0.25 : to, duration: dur || 0.4 }, t); }
  // color(t, els, c, dur, attr): HTML text colour, or an SVG attribute ("stroke"/"fill"). A "fill" on an unfilled path
  // (kit symbols are drawn as tubes) changes its stroke instead.
  function color(t, els, c, dur, attr) {
    if (attr === "fill") { const list = els.length != null && !els.getAttribute ? [...els] : [els];
      const tubes = list.filter((e) => e.getAttribute && e.getAttribute("fill") === "none");
      if (tubes.length) tl.to(tubes, { attr: { stroke: c }, duration: dur || 0.3 }, t);
      els = list.filter((e) => !tubes.includes(e)); if (!els.length) return; }
    tl.to(els, attr ? { attr: { [attr]: c }, duration: dur || 0.3 } : { color: c, duration: dur || 0.3 }, t); }
  // ---- a line that draws itself ----
  function draw(t, el, dur, ease) { const L = el.getTotalLength(); gsap.set(el, { attr: { "stroke-dasharray": L + " " + L, "stroke-dashoffset": L } });
    tl.to(el, { attr: { "stroke-dashoffset": 0 }, duration: dur || 0.6, ease: ease || "power2.out" }, t); return el; }

  // ---- label placement: score candidate rects against labels already on screen, the frame edges and `avoid` ----
  const area = (a, b) => Math.max(0, Math.min(a[2], b[2]) - Math.max(a[0], b[0])) * Math.max(0, Math.min(a[3], b[3]) - Math.max(a[1], b[1]));
  function screenRect(t, r) { const [x0, y0] = cam.toScreen(t, r[0], r[1]), [x1, y1] = cam.toScreen(t, r[0] + r[2], r[1] + r[3]); return [x0, y0, x1, y1]; }
  function cost(t, sr, avoid) {
    let c = 0;
    for (const p of placed) if (p.t0 < t + 1.2 && p.t1 > t) c += area(sr, p.w ? screenRect(t, p.w) : p.r) * 4;
    for (const a of avoid) c += area(sr, a);
    const m = 30; c += 50 * (Math.max(0, m - sr[0]) + Math.max(0, m - sr[1]) + Math.max(0, sr[2] - 1920 + m) + Math.max(0, sr[3] - 1080 + m)) * (sr[3] - sr[1]);
    return c;
  }
  function register(t, sr) { const p = { r: sr, t0: t, t1: 1e9 }; placed.push(p); return p; }          // screen rect [x0, y0, x1, y1]
  function registerW(t, wr) { const p = { w: wr, t0: t || 0, t1: 1e9 }; placed.push(p); return p; }    // world rect [x, y, w, h]
  const textW = (s, fs) => Math.round(s.length * fs * 0.5) + fs * 0.35;

  // ---- callout: dot on the part, leader line, underline, label sitting on the underline ----
  // callout(t, ax, ay, "Label", o)            picks a free side automatically (o.avoid: world rects/elements to keep clear)
  // callout(t, ax, ay, lx, ly, "Label", o)    elbow at (lx, ly), underline runs away from the anchor
  function callout(t, ax, ay, lx, ly, text, o) {
    if (typeof lx === "string") { o = ly; text = lx; lx = null; }
    o = o || {}; const col = o.color || C.cyan, z = cam.settled(t + 0.5), fs = (o.size || 72) / z;
    const w = textW(text, fs), sw = Math.max(3, (o.size || 72) / 15) / z;
    let dir;
    if (lx == null) {
      const L = (o.lead || 120) / z, avoid = (o.avoid || []).map((a) => screenRect(t, rectOf(a)));
      const sub = [ax - 14 / z, ay - 14 / z, 28 / z, 28 / z]; avoid.push(screenRect(t, sub));
      let best = null;
      for (const k of [1, 1.7, 2.5]) for (const [dx, dy] of [[1, -1], [-1, -1], [1, 1], [-1, 1], [1, 0], [-1, 0]]) {
        const ex = ax + dx * L * k * (dy ? 0.75 : 1), ey = ay + dy * L * k * 0.75;
        const r = [dx > 0 ? ex : ex - w, ey - fs * 1.18, w, fs * 1.18];
        const c = cost(t, screenRect(t, r), avoid) + k * 10;
        if (!best || c < best.c) best = { c, ex, ey, dx };
      }
      lx = best.ex; ly = best.ey; dir = best.dx;
    } else dir = lx >= ax ? 1 : -1;
    const g = S("g", {}, o.svg);
    const dot = S("circle", { cx: ax, cy: ay, r: Math.max(5, (o.size || 72) / 8) / z, fill: col }, g);
    const p = S("path", { d: `M${ax} ${ay} L${lx} ${ly} L${lx + dir * w} ${ly}`, stroke: col, "stroke-width": sw, fill: "none", "stroke-linejoin": "round", "stroke-linecap": "round" }, g);
    const lab = D("bx-lbl", { left: (dir > 0 ? lx + fs * 0.15 : lx - w + fs * 0.15) + "px", top: ly - fs * 1.12 + "px", color: col, fontSize: fs + "px" }, text, o.parent);
    const reg = registerW(t, [dir > 0 ? lx : lx - w, ly - fs * 1.18, w, fs * 1.18]);
    hideNow([dot, lab]);
    tl.to(dot, { opacity: 1, duration: 0.2 }, t);
    draw(t, p, 0.45);
    tl.fromTo(lab, { opacity: 0, y: fs * 0.2 }, { opacity: 1, y: 0, duration: 0.35, ease: "power2.out" }, t + 0.25);
    return { g, lab, els: [g, lab], hide(t2) { reg.t1 = t2; tl.to([g, lab], { opacity: 0, duration: 0.3 }, t2); } };
  }
  // ---- plain label at a world point (no leader; o.hud: screen point). t null = shown from the start. o.size screen px; o.anchor "left"|"center"|"right"; o.cls "bx-lbl"|"bx-big"|"bx-num"|"bx-small" ----
  function label(t, x, y, text, o) { o = o || {}; const z = o.parent === hud || o.hud ? 1 : cam.settled((t || 0) + 0.3), fs = (o.size || 60) / z, w = textW(text, fs);
    const left = o.anchor === "center" ? x - w / 2 : o.anchor === "right" ? x - w : x;
    const par = o.hud ? hud : o.parent, el = D(o.cls || "bx-lbl", { left: left + "px", top: y - fs + "px", fontSize: fs + "px", ...(o.color ? { color: o.color } : {}) }, text, par);
    const reg = par === hud ? register(t || 0, [left, y - fs, left + w, y]) : registerW(t || 0, [left, y - fs, w, fs]);
    if (t == null) return { el, hide(t2) { reg.t1 = t2; tl.to(el, { opacity: 0, duration: 0.3 }, t2); } };
    hideNow(el); tl.fromTo(el, { opacity: 0, y: fs * 0.2 }, { opacity: 1, y: 0, duration: 0.35, ease: "power2.out" }, t);
    return { el, hide(t2) { reg.t1 = t2; tl.to(el, { opacity: 0, duration: 0.3 }, t2); } }; }
  // ---- highlight lens over the part being named ----
  function lens(t, cx, cy, r, col, parent) { const c = S("circle", { cx, cy, r, fill: col || C.cyan, "fill-opacity": 0.26, stroke: col || C.cyan, "stroke-opacity": 0.7, "stroke-width": 3 }, parent);
    gsap.set(c, { opacity: 0, scale: 0.6, transformOrigin: "50% 50%" }); tl.to(c, { opacity: 1, scale: 1, duration: 0.4, ease: "back.out(1.8)" }, t); return c; }
  // ---- glowing outline box around a region ----
  function box(t, x, y, w, h, col, o) { o = o || {}; const r = S("rect", { x, y, width: w, height: h, rx: o.rx == null ? 8 : o.rx, fill: col, "fill-opacity": o.fill == null ? 0.12 : o.fill, stroke: col, "stroke-width": o.sw || 5 }, o.parent);
    if (o.dash) r.setAttribute("stroke-dasharray", o.dash); hideNow(r); tl.to(r, { opacity: 1, duration: 0.35 }, t); return r; }

  // ---- material ----
  // tube(d, o): a path drawn as a lit round wire: soft glow, dark edge, body colour, bright centre stripe.
  //   o.w body width (world px, default 14), o.color body (copper), o.glow halo colour (null = none), o.hi stripe opacity
  function tube(d, o) { o = o || {}; const w = o.w || 14, col = o.color || C.copper, g = S("g", {}, o.parent);
    const P = (sw, c, op, extra) => S("path", { d, stroke: c, "stroke-width": sw, fill: "none", "stroke-linecap": o.cap || "round", "stroke-linejoin": "round", opacity: op, ...(extra || {}) }, g);
    const glowCol = o.glow === undefined ? (col === C.copper ? "#ff5a2a" : col) : o.glow;
    const glows = glowCol ? [P(w * 3.2, glowCol, 0.10), P(w * 1.9, glowCol, 0.22)] : [];
    const edge = P(w + 4, "#0b0d0f", 0.75), body = P(w, col, 1), hi = P(Math.max(2, w * 0.3), o.hiColor || "#fff4ea", o.hi == null ? 0.55 : o.hi);
    return { g, body, hi, edge, glows, d,
      color(t, c, dur) { tl.to([body, ...glows], { attr: { stroke: c }, duration: dur || 0.3 }, t); } }; }
  // pipe(d, o): the same lit tube without a glow: pipes, blood vessels, ropes, roads, rivers
  function pipe(d, o) { return tube(d, { glow: null, ...(o || {}) }); }
  // a shaded straight wire (same as tube on a line)
  function wire(x1, y1, x2, y2, o) { o = o || {}; return tube(`M${x1} ${y1} L${x2} ${y2}`, { cap: "butt", w: o.w || 12, ...o }); }
  // gradient fill for solid parts: grad("copper"|"silver"|"beige"|"steel"|"green"|"plate"), o.dir "v"|"h"
  const GR = { copper: ["#6e3e26", "#e8a983", "#8c5034"], silver: ["#5d656c", "#eef2f5", "#7d868d"], beige: ["#7c6b4a", "#efe2c4", "#9c8a66"],
               steel: ["#3d444a", "#9aa4ac", "#4b535a"], green: ["#1f7a1d", "#9cff8a", "#2d9a2b"], plate: ["#2e3338", "#5a6168", "#33383d"] };
  //   or any "#rrggbb" colour: lit from above (dark edge, light middle, darker bottom), so every material works
  const mix = (hex, k) => { const n = parseInt(hex.slice(1), 16), c = [n >> 16, (n >> 8) & 255, n & 255];
    return "#" + c.map((v) => Math.round(k < 0 ? v * (1 + k) : v + (255 - v) * k).toString(16).padStart(2, "0")).join(""); };
  const FIN = { lit: [-0.5, 0.2, -0.35], matte: [-0.3, 0.06, -0.22] };
  function grad(name, o) { o = o || {}; const fin = FIN[o.finish] || FIN.lit, id = "bxg-" + String(name).replace("#", "c") + (o.dir === "h" ? "-h" : "") + (o.finish || "");
    if (!document.getElementById(id)) { const g = S("linearGradient", { id, x1: 0, y1: 0, x2: o.dir === "h" ? 1 : 0, y2: o.dir === "h" ? 0 : 1 }, def());
      (GR[name] || fin.map((k) => mix(name, k))).forEach((c, i) => S("stop", { offset: [0, 0.45, 1][i], "stop-color": c }, g)); }
    return `url(#${id})`; }
  // shape(d, kind, o): any SVG path as a solid lit object (a heart, a boat, a hill). kind is a preset or "#rrggbb"
  //   o.finish "lit" (default, metal/plastic/wet), "matte" (skin, stone, wood, cloth), "flat" (maps, large areas)
  function shape(d, kind, o) { o = o || {}; return S("path", { d, fill: o.finish === "flat" ? kind : grad(kind || "silver", o), stroke: o.rim || "rgba(255,255,255,0.35)", "stroke-width": o.sw || 2, "stroke-linejoin": "round" }, o.parent); }
  // a solid part: rounded rect with gradient fill and a thin light rim
  function part(x, y, w, h, kind, o) { o = o || {}; return S("rect", { x, y, width: w, height: h, rx: o.rx == null ? Math.min(w, h) * 0.18 : o.rx, fill: o.finish === "flat" ? kind : grad(kind || "silver", o), stroke: o.rim || "rgba(255,255,255,0.35)", "stroke-width": o.sw || 2 }, o.parent); }

  // prism(x, y, w, h, depth, col, o): a lit 2.5D box. Front face at (x, y, w, h); top and right faces recede up-right
  //   by `depth` (o.angle degrees, default 35). Top is lighter, side darker; o.shadow false hides the floor shadow.
  //   Returns {g, front, top, side}; move or show the group as one object.
  const shade = (hex, k) => { const n = parseInt(hex.slice(1), 16), f = (v) => Math.max(0, Math.min(255, Math.round(v * k)));
    return "#" + [f(n >> 16), f((n >> 8) & 255), f(n & 255)].map((v) => v.toString(16).padStart(2, "0")).join(""); };
  function prism(x, y, w, h, depth, col, o) { o = o || {}; col = col || "#5a6168"; const a = (o.angle == null ? 35 : o.angle) * Math.PI / 180, dx = depth * Math.cos(a), dy = -depth * Math.sin(a);
    const g = S("g", {}, o.parent);
    if (o.shadow !== false) S("ellipse", { cx: x + w / 2 + dx * 0.5, cy: y + h + 6, rx: w * 0.62 + dx * 0.4, ry: Math.max(10, h * 0.12), fill: "#000", opacity: 0.35 }, g);
    const side = S("path", { d: `M${x + w} ${y} l${dx} ${dy} v${h} l${-dx} ${-dy} z`, fill: shade(col, 0.62) }, g);
    const top = S("path", { d: `M${x} ${y} l${dx} ${dy} h${w} l${-dx} ${-dy} z`, fill: shade(col, 1.35), stroke: "rgba(255,255,255,0.35)", "stroke-width": 1.5 }, g);
    const front = S("rect", { x, y, width: w, height: h, fill: col, stroke: "rgba(255,255,255,0.18)", "stroke-width": 1.5 }, g);
    return { g, front, top, side }; }
  // beam(t, [x1, y1, x2, y2], [x3, y3, x4, y4], col): a translucent light beam joining a source edge to a target edge
  function beam(t, a, b, col, o) { o = o || {}; col = col || C.cyan; const id = "bxbeam" + (nBeam++);
    const gr = S("linearGradient", { id, x1: 0, y1: 1, x2: 0, y2: 0 }, def());
    S("stop", { offset: 0, "stop-color": col, "stop-opacity": 0.42 }, gr); S("stop", { offset: 1, "stop-color": col, "stop-opacity": 0.12 }, gr);
    const p = S("path", { d: `M${a[0]} ${a[1]} L${a[2]} ${a[3]} L${b[2]} ${b[3]} L${b[0]} ${b[1]} Z`, fill: `url(#${id})`, stroke: col, "stroke-opacity": 0.35, "stroke-width": 2 }, o.parent);
    if (t != null) { hideNow(p); tl.to(p, { opacity: 1, duration: 0.5 }, t); }
    return p; }
  let nBeam = 0;

  // ---- shared SVG patterns: hatch (charged) and hazard stripes (energised line) ----
  function hatch(id, col, bg) { const p = S("pattern", { id, width: 16, height: 16, patternUnits: "userSpaceOnUse", patternTransform: "rotate(45)" }, def());
    S("rect", { width: 16, height: 16, fill: bg || "#1d3a24" }, p); S("rect", { width: 7, height: 16, fill: col }, p); return `url(#${id})`; }
  function hazard(id, a, b) { const p = S("pattern", { id, width: 28, height: 28, patternUnits: "userSpaceOnUse", patternTransform: "rotate(45) translate(0,0)" }, def());
    S("rect", { width: 28, height: 28, fill: b || "#2a2410" }, p); S("rect", { width: 14, height: 28, fill: a || C.yellow }, p); return { fill: `url(#${id})`, p }; }
  // move a hazard/hatch pattern so its stripes crawl along (seek-safe attr tween)
  function crawl(t, pat, dur, dist) { tl.fromTo(pat, { attr: { patternTransform: "rotate(45) translate(0,0)" } }, { attr: { patternTransform: `rotate(45) translate(${dist || 28 * Math.ceil(dur * 2)},0)` }, duration: dur, ease: "none" }, t); }
  // stripes(t, tube, dur): energise a tube with moving yellow/black hazard stripes for dur seconds; returns {el, off(t)}
  let nStripe = 0;
  function stripes(t, tb, dur, o) { o = o || {}; const hz = hazard("bxhz" + nStripe++, o.color, o.bg);
    const w = +tb.body.getAttribute("stroke-width"), el = S("path", { d: tb.d, stroke: hz.fill, "stroke-width": w, fill: "none", "stroke-linecap": "butt", opacity: 0 }, tb.g);
    tl.to(el, { opacity: 1, duration: 0.3 }, t); crawl(t, hz.p, dur);
    return { el, off(t2) { tl.to(el, { opacity: 0, duration: 0.3 }, t2); } }; }

  // ---- flows ----
  // flow(t, d, col, dur, o): travelling dashes along path d (o.width, o.dash "18 22", o.speed, o.reverse, o.fade)
  function flow(t, d, col, dur, o) { o = o || {}; const p = S("path", { d, stroke: col, "stroke-width": o.width || 8, fill: "none", "stroke-linecap": "round", "stroke-linejoin": "round", "stroke-dasharray": o.dash || "18 22", opacity: 0 }, o.parent);
    const per = o.dash ? o.dash.split(" ").reduce((a, b) => a + +b, 0) : 40, dist = per * Math.ceil(dur * (o.speed || 2.5)) * (o.reverse ? 1 : -1);
    tl.to(p, { opacity: 1, duration: 0.25 }, t); tl.fromTo(p, { attr: { "stroke-dashoffset": 0 } }, { attr: { "stroke-dashoffset": dist }, duration: dur, ease: "none" }, t);
    if (o.fade !== false) tl.to(p, { opacity: 0, duration: 0.3 }, t + dur); return p; }
  // packet(t, [[x,y],...], col, dur, r): a dot that travels the points once
  function packet(t, pts, col, dur, r, parent) { const c = S("circle", { cx: pts[0][0], cy: pts[0][1], r: r || 12, fill: col }, parent); hideNow(c);
    tl.to(c, { opacity: 1, duration: 0.15 }, t); const seg = dur / (pts.length - 1);
    for (let i = 1; i < pts.length; i++) tl.to(c, { attr: { cx: pts[i][0], cy: pts[i][1] }, duration: seg, ease: "none" }, t + (i - 1) * seg);
    tl.to(c, { opacity: 0, duration: 0.2 }, t + dur); return c; }
  // particles(t, [x1,y1], [x2,y2], dur, o): a seeded stream of dots from one point to another (o.n, o.spread, o.color, o.r, o.seed, o.travel)
  function particles(t, a, b, dur, o) { o = o || {}; const R = rand(o.seed || 7), n = o.n || 40, travel = o.travel || 1.2, sp = o.spread || 40, g = S("g", {}, o.parent);
    for (let i = 0; i < n; i++) { const t0 = t + (dur - travel) * (i / n), j1 = (R() - 0.5) * sp, j2 = (R() - 0.5) * sp, j3 = (R() - 0.5) * sp, j4 = (R() - 0.5) * sp;
      const c = S("circle", { cx: a[0] + j1, cy: a[1] + j2, r: (o.r || 7) * (0.6 + R() * 0.8), fill: o.color || C.cyan, opacity: 0 }, g);
      tl.to(c, { opacity: 0.9, duration: 0.15 }, t0); tl.to(c, { attr: { cx: b[0] + j3, cy: b[1] + j4 }, duration: travel, ease: "power1.inOut" }, t0); tl.to(c, { opacity: 0, duration: 0.15 }, t0 + travel - 0.15); }
    return g; }

  // ---- instruments ----
  // counter(t, el, from, to, dur, fmt): live number readout written in onUpdate (seek-safe)
  function counter(t, el, from, to, dur, fmt, ease) { const o = { v: from }; if (!el.dataset.bxCounted) { el.textContent = fmt(from); el.dataset.bxCounted = "1"; }
    tl.fromTo(o, { v: from }, { v: to, duration: dur, ease: ease || "power1.inOut", immediateRender: false, onUpdate: () => { el.textContent = fmt(o.v); } }, t); }
  // readout(x, y, v0, fmt, o): a number that remembers its value; .to(t, v, dur) ticks to the next value. o.size screen px, o.hud: screen space
  function readout(x, y, v0, fmt, o) { o = o || {}; fmt = fmt || ((v) => v.toFixed(2)); const par = o.hud ? hud : (o.parent || labels), z = o.hud ? 1 : cam.settled(o.t || 0);
    const el = D("bx-num", { left: x + "px", top: y + "px", fontSize: (o.size || 56) / z + "px", ...(o.color ? { color: o.color } : {}) }, fmt(v0), par);
    let cur = v0; return { el, to(t, v, dur) { counter(t, el, cur, v, dur || 1, fmt); cur = v; } }; }
  // figure(t, x, y, to, o): headline number counting up in screen space (o.from, o.dur, o.fmt, o.size 100, o.unit text after it)
  function figure(t, x, y, to, o) { o = o || {}; const fmt = o.fmt || ((v) => Math.round(v).toLocaleString("en-US"));
    const el = D("bx-big", { left: x + "px", top: y + "px", fontSize: (o.size || 100) + "px", ...(o.color ? { color: o.color } : {}) }, "", hud);
    const num = document.createElement("span"); el.appendChild(num);
    if (o.unit) { const u = document.createElement("span"); u.className = "bx-unit"; u.textContent = " " + o.unit; el.appendChild(u); }
    hideNow(el); tl.to(el, { opacity: 1, duration: 0.3 }, t); counter(t, num, o.from || 0, to, o.dur || 1.6, fmt, "power2.out");
    return { el, hide(t2) { tl.to(el, { opacity: 0, duration: 0.3 }, t2); } }; }
  // gauge(x, y, h, o): vertical gauge in screen space for any quantity: o.min (0), o.max (1), o.unit ("V"), o.dp decimals (1),
  //   o.label name above it ("Oxygen"), o.bar one colour for the bar (default: green at the top to red at the bottom, i.e. "higher = better"), o.v start. .set(t, v, dur) moves the marker. (o.vmax is the old name for o.max)
  function gauge(x, y, h, o) { o = o || {}; const vmin = o.min || 0, vmax = o.max != null ? o.max : (o.vmax || 1.0), par = o.parent || hud, fs = Math.round(h * 0.13);
    const unit = o.unit == null ? "V" : o.unit, dp = o.dp == null ? 1 : o.dp, tk = (v) => v.toFixed(dp) + (unit.length > 1 ? " " : "") + unit;
    const gw = Math.round(Math.max(h * 0.52, h * 0.25 + Math.max(tk(vmin).length, tk(vmax).length) * fs * 0.52));
    const off = o.label ? Math.round(fs * 1.25) : 0;      // room for the name inside the panel
    const g = D("bx-gauge", { left: x + "px", top: y + "px", height: h + off + "px", width: gw + "px" }, "", par);
    const top = off + h * 0.09, bot = off + h * 0.91, bw = h * 0.07, bar = document.createElement("div"); bar.className = "bar";
    if (o.bar) Object.assign(bar.style, { background: o.bar, boxShadow: "0 0 14px " + o.bar });
    Object.assign(bar.style, { top: top + "px", height: bot - top + "px", width: bw + "px", left: h * 0.06 + "px" }); g.appendChild(bar);
    [[vmax, top], [(vmin + vmax) / 2, (top + bot) / 2], [vmin, bot]].forEach(([v, yy]) => {
      const tb = document.createElement("div"); tb.className = "tbar"; Object.assign(tb.style, { top: yy - 3 + "px", left: h * 0.04 + "px", width: bw + h * 0.04 + "px" }); g.appendChild(tb);
      const k = document.createElement("div"); k.className = "tick"; k.textContent = tk(v); Object.assign(k.style, { top: yy - fs * 0.55 + "px", left: h * 0.19 + "px", fontSize: fs + "px" }); g.appendChild(k); });
    const mark = document.createElement("div"); mark.className = "mark"; Object.assign(mark.style, { left: h * 0.03 + "px", width: bw + h * 0.06 + "px" }); g.appendChild(mark);
    const yOf = (v) => bot - ((v - vmin) / (vmax - vmin)) * (bot - top) - 4;
    gsap.set(mark, { y: yOf(o.v == null ? (vmin + vmax) / 2 : o.v) });
    if (o.label) { const n = document.createElement("div"); n.className = "tick"; n.textContent = o.label;
      Object.assign(n.style, { top: fs * 0.3 + "px", left: h * 0.06 + "px", fontSize: Math.round(fs * 0.8) + "px", color: "#e9eef2" }); g.appendChild(n); }
    register(0, [x, y, x + gw, y + h + off]);
    return { el: g, set(t, v, dur) { tl.to(mark, { y: yOf(v), duration: dur || 0.6, ease: "power2.inOut" }, t); }, now(v) { gsap.set(mark, { y: yOf(v) }); } }; }
  // bar(t, x, y, w, h, col, o): a bar that grows from its left edge to width w (o.dur, o.label text inside, o.size)
  function bar(t, x, y, w, h, col, o) { o = o || {}; const r = S("rect", { x, y, width: w, height: h, rx: Math.min(8, h / 4), fill: col || C.orange }, o.parent);
    gsap.set(r, { scaleX: 0, transformOrigin: "0% 50%" }); tl.to(r, { scaleX: 1, duration: o.dur || 0.8, ease: "power2.out" }, t);
    let lab = null; if (o.label) { lab = D("bx-small", { left: x + 14 + "px", top: y + h / 2 - (o.size || 34) * 0.55 + "px", fontSize: (o.size || 34) + "px", color: "#0b0e10", fontWeight: 600, textShadow: "none" }, o.label, o.labelParent); hideNow(lab); tl.to(lab, { opacity: 1, duration: 0.3 }, t + (o.dur || 0.8) * 0.6); }
    return { el: r, lab }; }

  // ---- diagram vocabulary ----
  // bits(x, y, "0101...", o): one span per bit (fixed cell width). .field(t, a, b, col) colours bits a..b-1; .bracket(t, a, b, "Row", col)
  function bits(x, y, str, o) { o = o || {}; const fs = o.size || 48, cw = fs * 0.62, el = D("bx-bits", { left: x + "px", top: y + "px", fontSize: fs + "px" }, "", o.parent || hud);
    const spans = [...str].map((ch) => { const s = document.createElement("span"); s.textContent = ch; s.style.width = cw + "px"; el.appendChild(s); return s; });
    return { el, spans, cw,
      field(t, a, b, col) { tl.to(spans.slice(a, b), { color: col, duration: 0.3 }, t); },
      bracket(t, a, b, text, col, below, size) { col = col || C.cyan; const bs = size || Math.round(fs * 0.62); const br = D("bx-bracket", { left: x + a * cw + 3 + "px", top: (below === false ? y - fs * 0.35 : y + fs * 1.15) + "px", width: (b - a) * cw - 6 + "px", borderColor: col, ...(below === false ? { borderTop: "4px solid " + col, borderBottom: "none" } : {}) }, "", o.parent || hud);
        const lw = Math.max((b - a) * cw, textW(text, bs));      // label box as wide as its text, so overlaps are measurable
        const par = o.parent || hud, lx0 = x + (a + b) / 2 * cw - lw / 2, lx = par === hud ? Math.max(12, Math.min(1908 - lw, lx0)) : lx0;   // keep screen labels in frame
        const lab = D("bx-small", { left: lx + "px", width: lw + "px", textAlign: "center", top: (below === false ? Math.max(par === hud ? 6 : -1e9, y - fs * 0.45 - bs * 1.1) : y + fs * 1.5) + "px", color: col, fontSize: bs + "px" }, text, o.parent || hud);
        hideNow([br, lab]); tl.to([br, lab], { opacity: 1, duration: 0.35, stagger: 0.12 }, t); return { br, lab }; } }; }
  // plate(x, y, w, h, "Row Decoder", o): grey block with a name (o.size text px, o.css extra style)
  function plate(x, y, w, h, text, o) { o = o || {}; (o.parent === hud ? register(0, [x, y, x + w, y + h]) : registerW(0, [x, y, w, h])); return D("bx-plate", { left: x + "px", top: y + "px", width: w + "px", height: h + "px", fontSize: (o.size || 40) + "px", ...(o.css || {}) }, text, o.parent); }
  // bus(t, [[x,y],...], o): a bundle of parallel signal wires along the points, drawn in; o.n wires (4), o.width "x16" label (cyan),
  //   o.labelSeg which segment carries the slash and label (0)
  function bus(t, pts, o) { o = o || {}; const n = o.n || 4, gap = o.gap || 9, col = o.color || C.orange, g = S("g", {}, o.parent), lines = [];
    for (let k = 0; k < n; k++) { const off = (k - (n - 1) / 2) * gap;
      const nrm = (a, b) => { const L = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1; return [-(b[1] - a[1]) / L, (b[0] - a[0]) / L]; };
      const d = pts.map(([x, y], i) => { const n1 = i > 0 ? nrm(pts[i - 1], pts[i]) : null, n2 = i < pts.length - 1 ? nrm(pts[i], pts[i + 1]) : null;
        const nx = (n1 ? n1[0] : 0) + (n2 ? n2[0] : 0), ny = (n1 ? n1[1] : 0) + (n2 ? n2[1] : 0), k = n1 && n2 ? 1 + (n1[0] * n2[0] + n1[1] * n2[1]) : 1;
        return `${i ? "L" : "M"}${x + off * nx / k} ${y + off * ny / k}`; }).join(" ");
      const p = S("path", { d, stroke: col, "stroke-width": o.w || 5, fill: "none", "stroke-linejoin": "miter" }, g); lines.push(p); if (t != null) draw(t + k * 0.04, p, o.dur || 0.7, "power1.inOut"); }
    let lab = null;
    if (o.width) { const sg = Math.min(o.labelSeg || 0, pts.length - 2), [x1, y1] = pts[sg], [x2, y2] = pts[sg + 1], mx = (x1 + x2) / 2, my = (y1 + y2) / 2, hz = Math.abs(y2 - y1) < Math.abs(x2 - x1), L = n * gap;
      const sl = S("line", hz ? { x1: mx - L * 0.5, y1: my + L, x2: mx + L * 0.5, y2: my - L } : { x1: mx - L, y1: my + L * 0.5, x2: mx + L, y2: my - L * 0.5 }, g);
      sl.setAttribute("stroke", C.text); sl.setAttribute("stroke-width", 4);
      lab = D("bx-small", { left: (hz ? mx + L * 0.8 : mx + L * 1.3) + "px", top: (hz ? my - L - (o.size || 36) * 1.05 : my - (o.size || 36) * 0.55) + "px", fontSize: (o.size || 40) + "px", color: C.cyan }, o.width, o.labelParent);
      if (t != null) { hideNow([sl, lab]); tl.to([sl, lab], { opacity: 1, duration: 0.3 }, t + 0.5); } }
    return { g, lines, lab, color(t2, c, dur) { tl.to(lines, { attr: { stroke: c }, duration: dur || 0.3 }, t2); } }; }
  // chain(x, y, ["Row close", "Precharge", ...], o): numbered process steps in a row (o.w, o.h, o.gap, o.size). .on(t, i, col) lights step i;
  // .arc(t, from, to, "Row miss", col, o) draws a curved arrow above (o.below for under) from step `from` back to step `to`
  function chain(x, y, steps, o) { o = o || {}; const w = o.w || 300, h = o.h || 150, gap = o.gap || 50, fs = o.size || 38;
    const plates = steps.map((s, i) => plate(x + i * (w + gap), y, w, h, `<span class="bx-step">${i + 1}</span>${s}`, { size: fs, parent: o.parent }));
    const arrows = steps.slice(1).map((_, i) => { const ax = x + (i + 1) * (w + gap) - gap + 8, ay = y + h / 2;
      return S("path", { d: `M${ax} ${ay} L${ax + gap - 16} ${ay} M${ax + gap - 30} ${ay - 12} L${ax + gap - 16} ${ay} L${ax + gap - 30} ${ay + 12}`, stroke: C.muted, "stroke-width": 5, fill: "none" }); });
    const cx = (i) => x + i * (w + gap) + w / 2;
    return { plates, arrows,
      on(t, i, col) { tl.to(plates[i], { borderColor: col || C.green, boxShadow: `0 0 26px ${col || C.green}`, duration: 0.3 }, t); },
      off(t, i) { tl.to(plates[i], { borderColor: "#5d646b", boxShadow: "0 10px 24px rgba(0,0,0,0.5)", duration: 0.3 }, t); },
      arc(t, from, to, text, col, ao) { ao = ao || {}; col = col || C.orange; const below = !!ao.below, y0 = below ? y + h + 12 : y - 12, lift = (ao.lift || 1) * (90 + 40 * Math.abs(from - to)) * (below ? 1 : -1);
        const x1 = cx(from), x2 = cx(to), d = `M${x1} ${y0} C${x1} ${y0 + lift}, ${x2} ${y0 + lift}, ${x2} ${y0}`;
        const p = S("path", { d, stroke: col, "stroke-width": 8, fill: "none", "stroke-linecap": "round" }, ao.parent);
        const head = S("path", { d: `M${x2 - 18} ${y0 + (below ? 26 : -26)} L${x2} ${y0} L${x2 + 18} ${y0 + (below ? 26 : -26)}`, stroke: col, "stroke-width": 8, fill: "none", "stroke-linecap": "round", "stroke-linejoin": "round" }, ao.parent);
        draw(t, p, 0.8, "power1.inOut"); hideNow(head); tl.to(head, { opacity: 1, duration: 0.2 }, t + 0.7);
        const lab = label(t + 0.4, (x1 + x2) / 2, y0 + lift * 0.75 + (below ? (ao.size || 52) * 1.2 : -10), text, { anchor: "center", size: ao.size || 52, color: col });
        return { p, head, lab, hide(t2) { lab.hide(t2); tl.to([p, head], { opacity: 0, duration: 0.3 }, t2); } }; } }; }
  // dimline(t, x1, y1, x2, y2, "64 nm", o): a dimension line with end bars, drawn in, label beside it (o.size, o.color, o.side ±1)
  function dimline(t, x1, y1, x2, y2, text, o) { o = o || {}; const col = o.color || C.text, g = S("g", {}, o.parent), L = Math.hypot(x2 - x1, y2 - y1), nx = -(y2 - y1) / L, ny = (x2 - x1) / L, e = 16;
    const p = S("path", { d: `M${x1} ${y1} L${x2} ${y2}`, stroke: col, "stroke-width": 4, fill: "none" }, g);
    const ends = S("path", { d: `M${x1 - nx * e} ${y1 - ny * e} L${x1 + nx * e} ${y1 + ny * e} M${x2 - nx * e} ${y2 - ny * e} L${x2 + nx * e} ${y2 + ny * e}`, stroke: col, "stroke-width": 4 }, g);
    hideNow(ends); tl.to(ends, { opacity: 1, duration: 0.2 }, t); draw(t, p, 0.5);
    const side = o.side || 1, z = cam.zoom(t), fs = (o.size || 44) / z, vert = Math.abs(y2 - y1) > Math.abs(x2 - x1);
    const mx = vert ? (x1 + x2) / 2 + side * (e + fs * 0.3) : (x1 + x2) / 2 + nx * side * (fs * 0.9), my = vert ? (y1 + y2) / 2 : (y1 + y2) / 2 + ny * side * (fs * 0.9);
    const lab = label(t + 0.3, mx, my + fs * 0.35, text, { anchor: vert ? (side > 0 ? "left" : "right") : "center", size: o.size || 44, color: col, cls: "bx-small" });
    return { g, lab, hide(t2) { lab.hide(t2); tl.to(g, { opacity: 0, duration: 0.3 }, t2); } }; }
  // compare(t, x, baseY, [{label, value, h, w, color}], o): blocks standing on one baseline, big value labels above (o.gap)
  function compare(t, x, baseY, items, o) { o = o || {}; let cx = x; const out = [];
    S("line", { x1: x - 40, y1: baseY, x2: x + items.reduce((a, it) => a + (it.w || 220) + (o.gap || 160), 0) - (o.gap || 160) + 40, y2: baseY, stroke: C.muted, "stroke-width": 4 });
    items.forEach((it, i) => { const w = it.w || 220, r = part(cx, baseY - it.h, w, it.h, it.kind || "steel"); gsap.set(r, { scaleY: 0, transformOrigin: "50% 100%" });
      tl.to(r, { scaleY: 1, duration: 0.7, ease: "power2.out" }, t + i * 0.5);
      const v = label(t + i * 0.5 + 0.4, cx + w / 2, baseY - it.h - 24, it.value, { anchor: "center", size: o.size || 72, color: it.color || C.cyan, cls: "bx-big" });
      const n = label(t + i * 0.5 + 0.2, cx + w / 2, baseY + 70, it.label, { anchor: "center", size: 44, color: C.text });
      out.push({ r, v, n }); cx += w + (o.gap || 160); });
    return out; }
  // title(t, "1T1C DRAM Memory Cell", o): a large title card in screen space with a drawn underline; .hide(t2). o.y, o.size (96), o.sub
  function title(t, text, o) { o = o || {}; const fs = o.size || 96, y = o.y || 140, w = textW(text, fs);
    const el = H("bx-title", { left: 960 - w / 2 + "px", top: y + "px", fontSize: fs + "px" }, text);
    const ln = FS("line", { x1: 960 - w / 2, y1: y + fs * 1.18, x2: 960 + w / 2, y2: y + fs * 1.18, stroke: C.cyan, "stroke-width": 6 });
    const sub = o.sub ? H("bx-small", { left: 960 - textW(o.sub, 40) / 2 + "px", top: y + fs * 1.4 + "px", fontSize: "40px", color: C.muted }, o.sub) : null;
    const reg = register(t, [960 - w / 2, y, 960 + w / 2, y + fs * 1.4 + (sub ? 60 : 0)]);
    const els = [el, ...(sub ? [sub] : [])]; hideNow([...els, ln]);
    tl.fromTo(el, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.5, ease: "power2.out" }, t); draw(t + 0.2, ln, 0.6); tl.to(ln, { opacity: 1, duration: 0.01 }, t + 0.2);
    if (sub) tl.to(sub, { opacity: 1, duration: 0.4 }, t + 0.5);
    return { el, hide(t2) { reg.t1 = t2; tl.to([...els, ln], { opacity: 0, duration: 0.4 }, t2); } }; }
  // progress(x, y, ["Reading", "Writing", "Refreshing"], o): a HUD list; .at(t, i) makes item i current (o.row for "1 2 3 4" in a row)
  function progress(x, y, items, o) { o = o || {}; const fs = o.size || 40;
    const el = H("bx-progress" + (o.row ? " row" : ""), { left: x + "px", top: y + "px", fontSize: fs + "px" }, items.map((s) => `<div class="it"><span class="box"></span>${s}</div>`).join(""));
    const its = [...el.querySelectorAll(".it")]; register(0, [x, y, x + (o.row ? items.length * fs * 1.6 : 480), y + (o.row ? fs * 1.3 : items.length * fs * 1.4)]);
    return { el, items: its, at(t, i, col) { its.forEach((it, k) => tl.to(it, { color: k === i ? (col || C.green) : C.muted, opacity: k === i ? 1 : 0.7, duration: 0.3 }, t)); },
      done(t, i) { tl.to(its[i].querySelector(".box"), { backgroundColor: C.green, borderColor: C.green, duration: 0.3 }, t); } }; }
  // inset(t, [wx, wy, ww, wh], o): "you are here" mini-map in a screen corner. The outline follows the camera from t on.
  //   o.x, o.y, o.w panel position/width (screen), o.draw(g, k) draws the miniature into svg group g at scale k (world*k), o.label
  function inset(t, area, o) { o = o || {}; const W = o.w || 300, k = W / area[2], Hh = area[3] * k, x = o.x == null ? 1920 - W - 48 : o.x, y = o.y == null ? 48 : o.y;
    const g = FS("g", { transform: `translate(${x} ${y})` });
    S("rect", { x: -8, y: -8, width: W + 16, height: Hh + 16, rx: 10, fill: "#0d1013", "fill-opacity": 0.85, stroke: "#4b5157", "stroke-width": 2 }, g);
    const inner = S("g", { transform: `translate(${-area[0] * k} ${-area[1] * k}) scale(${k})` }, g); if (o.draw) o.draw(inner, k);
    const view = (s) => ({ x: (-s.x / s.s - area[0]) * k, y: (-s.y / s.s - area[1]) * k, width: 1920 / s.s * k, height: 1080 / s.s * k });
    const box = S("rect", { ...view(state(t)), fill: "none", stroke: C.cyan, "stroke-width": 3 }, g);
    for (const kf of keys) if (kf.t + kf.dur > t) tl.to(box, { attr: view(kf.to), duration: kf.dur, ease: kf.ease }, Math.max(t, kf.t));
    const lab = o.label ? H("bx-small", { left: x + "px", top: y + Hh + 18 + "px", fontSize: "28px", color: C.muted }, o.label) : null;
    register(t, [x - 8, y - 8, x + W + 8, y + Hh + (lab ? 60 : 8)]);
    hideNow([g, ...(lab ? [lab] : [])]); tl.to([g, ...(lab ? [lab] : [])], { opacity: 1, duration: 0.4 }, t);
    return { g, box, hide(t2) { tl.to([g, ...(lab ? [lab] : [])], { opacity: 0, duration: 0.3 }, t2); } }; }

  // ---- state badge: plate with a big digit beside a storage element; set(t, "1" | "0") cross-fades ----
  function badge(x, y, o) { o = o || {}; const size = o.size || 64, par = o.parent || labels;
    const pl = D("bx-badge", { left: x + "px", top: y + "px", width: size * 1.0 + "px", height: size * 1.5 + "px", fontSize: size + "px" }, "", par);   // Saira glyph box is ~1.42 em tall
    if (par !== hud) registerW(0, [x, y, size * 1.0, size * 1.5]);
    pl.setAttribute("data-layout-allow-overlap", "");     // the 1 and 0 are stacked on purpose for the cross-fade
    const one = document.createElement("span"), zero = document.createElement("span"); one.textContent = "1"; zero.textContent = "0";
    one.style.color = C.green; zero.style.color = "#ff6b5e"; pl.appendChild(one); pl.appendChild(zero);
    const v0 = o.value == null ? "0" : o.value; gsap.set(one, { opacity: v0 === "1" ? 1 : 0 }); gsap.set(zero, { opacity: v0 === "1" ? 0 : 1 });
    return { el: pl, set(t, v) { tl.to(one, { opacity: v === "1" ? 1 : 0, duration: 0.25 }, t); tl.to(zero, { opacity: v === "1" ? 0 : 1, duration: 0.25 }, t); } }; }
  // ---- schematic symbols (centre x, y), drawn as lit tubes ----
  function ground(x, y, col, parent) { const g = S("g", {}, parent); [[30, 0], [22, 11], [14, 22], [7, 33]].forEach(([w, dy]) => tube(`M${x - w} ${y + dy} L${x + w} ${y + dy}`, { w: 5, color: col || C.copper, parent: g, glow: null, hi: 0.4 })); return g; }
  // capacitor symbol: two plates, top plate at y; .fill is the charge bar between them (green when charged)
  function capSym(x, y, o) { o = o || {}; const w = o.w || 90, gap = o.gap || 22, g = S("g", {}, o.parent);
    const fill = S("rect", { x: x - w / 2 + 6, y: y + 8, width: w - 12, height: Math.max(4, gap - 16), rx: 3, fill: C.green, opacity: o.charged ? 0.95 : 0 }, g);
    part(x - w / 2, y - 6, w, 14, "silver", { parent: g, rx: 6 });
    part(x - w / 2, y + gap, w, 14, "steel", { parent: g, rx: 6 });
    return { g, fill }; }
  // transistor symbol (horizontal channel, gate on top). Channel from (x-w/2, y) to (x+w/2, y).
  function fetSym(x, y, o) { o = o || {}; const w = o.w || 120, g = S("g", {}, o.parent), col = o.color || C.beige;
    const chD = `M${x - w / 2 - 30} ${y} H${x - w / 2} V${y - 18} H${x + w / 2} V${y} H${x + w / 2 + 30}`;
    const ch = tube(chD, { w: 8, color: col, parent: g, glow: col, cap: "butt" });
    const gate = tube(`M${x - w / 2 + 12} ${y - 36} H${x + w / 2 - 12}`, { w: 10, color: col, parent: g, glow: col, cap: "round" });
    return { g, ch: ch.body, chTube: ch, gate: gate.body, gateTube: gate }; }
  // ---- moving things. Coordinates are world px; every helper adds one tween at t ----
  // move(t, el, dx, dy, dur): slide by (dx, dy) from where it was drawn. Call again with new totals to move on.
  function move(t, el, dx, dy, dur, ease) { tl.to(el, { x: dx, y: dy, duration: dur || 1, ease: ease || "power2.inOut" }, t); }
  // turn(t, el, deg, [ox, oy], dur): rotate about a world point (a hinge, valve flap, gate, lever pivot). deg is absolute (0 = as drawn)
  function turn(t, el, deg, o, dur, ease) { tl.to(el, { rotation: deg, svgOrigin: `${o[0]} ${o[1]}`, duration: dur || 0.6, ease: ease || "power2.inOut" }, t); }
  // pulse(t, el, k, dur, n): grow to scale k and back, n times (a heartbeat, a squeeze, an emphasis)
  function pulse(t, el, k, dur, n) { n = n || 1; for (let i = 0; i < n; i++) tl.to(el, { scale: k || 1.06, transformOrigin: "50% 50%", duration: (dur || 0.5) / 2, yoyo: true, repeat: 1, ease: "power2.inOut" }, t + i * (dur || 0.5) * 1.6); }
  // liquid(x, yBottom, w, hMax, col, o): a container's contents seen in cut-away (water, blood, fuel, a level of anything).
  //   o.level 0..1 start (0.5), o.opacity (0.85). .to(t, level, dur) fills or drains it; .surface(level) = world y of the top.
  function liquid(x, yb, w, hMax, col, o) { o = o || {}; let lv = o.level == null ? 0.5 : o.level; const g = S("g", {}, o.parent);
    const body = S("rect", { x, y: yb - hMax * lv, width: w, height: hMax * lv, fill: col || C.blue, opacity: o.opacity || 0.85 }, g);
    const top = S("rect", { x, y: yb - hMax * lv - 2, width: w, height: 5, fill: mix(col || C.blue, 0.5), opacity: 0.9 }, g);
    return { g, body, top, surface: (l) => yb - hMax * l,
      to(t, l, dur) { const d = dur || 2; tl.to(body, { attr: { y: yb - hMax * l, height: hMax * l }, duration: d, ease: "power1.inOut" }, t);
        tl.to(top, { attr: { y: yb - hMax * l - 2 }, duration: d, ease: "power1.inOut" }, t); lv = l; } }; }
  // ---- obstacle(els|rects, t0, t1): tell label placement about shapes you drew yourself (world rects [x, y, w, h] or elements) ----
  function obstacle(rs, t0, t1) { const list = Array.isArray(rs) && (rs.length === 0 || Array.isArray(rs[0]) || rs[0].nodeType) ? rs : [rs];
    const ps = list.map((r) => { const p = registerW(t0 || 0, rectOf(r)); if (t1 != null) p.t1 = t1; return p; });
    return { hide(t2) { ps.forEach((p) => { p.t1 = t2; }); } }; }
  // ---- arrow(t, [[x,y], ...], o): a line that draws itself along the points and ends in a head. o.color (orange = movement),
  //   o.w width (8), o.head size (4.5 x w), o.dur (0.6), o.curve true = smooth curve through the points,
  //   o.dash true (or "20 14") = dashed (planned, possible, past) and fades in. Labels avoid the line (o.obstacle false: they don't).
  function arrow(t, pts, o) { o = o || {}; const col = o.color || C.orange, w = o.w || 8, hs = o.head || w * 4.5, g = S("g", {}, o.parent);
    const n = pts.length, [ex, ey] = pts[n - 1], [px, py] = pts[n - 2], L = Math.hypot(ex - px, ey - py) || 1, ux = (ex - px) / L, uy = (ey - py) / L;
    const end = [ex - ux * hs * 0.8, ey - uy * hs * 0.8];
    let d = `M${pts[0][0]} ${pts[0][1]}`;
    if (o.curve && n > 2) { for (let i = 1; i < n - 1; i++) { const m = i === n - 2 ? end : [(pts[i][0] + pts[i + 1][0]) / 2, (pts[i][1] + pts[i + 1][1]) / 2]; d += ` Q${pts[i][0]} ${pts[i][1]} ${m[0]} ${m[1]}`; } }
    else { for (let i = 1; i < n - 1; i++) d += ` L${pts[i][0]} ${pts[i][1]}`; d += ` L${end[0]} ${end[1]}`; }
    const line = S("path", { d, stroke: col, "stroke-width": w, fill: "none", "stroke-linecap": "round", "stroke-linejoin": "round" }, g);
    const head = S("path", { d: `M${ex} ${ey} L${ex - ux * hs - uy * hs * 0.55} ${ey - uy * hs + ux * hs * 0.55} L${ex - ux * hs + uy * hs * 0.55} ${ey - uy * hs - ux * hs * 0.55} Z`, fill: col }, g);
    // labels avoid the line itself: small boxes every ~60 px along it (a bounding box would block a whole map)
    const regs = [], LL = line.getTotalLength(), b = Math.max(w, hs * 0.6);
    if (o.obstacle !== false) for (let s = 0; s <= LL; s += 60) { const q = line.getPointAtLength(s); regs.push(registerW(t == null ? 0 : t, [q.x - b / 2, q.y - b / 2, b, b])); }
    if (o.obstacle !== false) regs.push(registerW(t == null ? 0 : t, [ex - hs, ey - hs, hs * 2, hs * 2]));
    if (o.dash) line.setAttribute("stroke-dasharray", o.dash === true ? `${w * 2.2} ${w * 1.6}` : o.dash);
    if (t != null) { const dur = o.dur || 0.6; hideNow(head);
      if (o.dash) { hideNow(line); tl.to(line, { opacity: 1, duration: dur }, t); } else draw(t, line, dur, "power1.inOut");
      tl.to(head, { opacity: 1, duration: 0.15 }, t + dur - 0.1); }
    const reg = { set t1(v) { regs.forEach((r) => { r.t1 = v; }); } };
    return { g, line, head, color(t2, c, dur) { tl.to(line, { attr: { stroke: c }, duration: dur || 0.3 }, t2); tl.to(head, { attr: { fill: c }, duration: dur || 0.3 }, t2); },
      hide(t2) { reg.t1 = t2; tl.to(g, { opacity: 0, duration: 0.3 }, t2); } }; }
  // ---- axis(t, x, y, len, o): a horizontal scale for timelines, distances or any quantity, drawn in at t.
  //   o.from, o.to (values at the two ends), o.step (tick every step), o.fmt (v => text), o.size (label px, 40), o.color.
  //   .at(v) = world x of value v. .mark(t, v, "Text", o) = a dot on the axis and a label above it (o.color, o.below).
  function axis(t, x, y, len, o) { o = o || {}; const from = o.from || 0, to = o.to == null ? 1 : o.to, step = o.step || (to - from) / 4, col = o.color || C.steel;
    const fmt = o.fmt || ((v) => String(Math.round(v * 100) / 100)), at = (v) => x + ((v - from) / (to - from)) * len, g = S("g", {}, o.parent);
    const line = S("path", { d: `M${x} ${y} H${x + len}`, stroke: col, "stroke-width": 5, fill: "none", "stroke-linecap": "round" }, g);
    const ticks = [], labs = [];
    for (let v = from, i = 0; v <= to + step * 1e-6; v = from + ++i * step) {
      ticks.push(S("path", { d: `M${at(v)} ${y - 14} V${y + 14}`, stroke: col, "stroke-width": 4 }, g));
      labs.push(label(t == null ? null : t + 0.3, at(v), y + 70, fmt(v), { anchor: "center", size: o.size || 40, color: C.text }));
    }
    if (t != null) { draw(t, line, 0.8, "power1.inOut"); hideNow(ticks); tl.to(ticks, { opacity: 1, duration: 0.2, stagger: 0.04 }, t + 0.2); }
    return { g, at, labels: labs, hide(t2) { tl.to(g, { opacity: 0, duration: 0.3 }, t2); labs.forEach((l) => l.hide(t2)); },
      mark(t2, v, text, m) { m = m || {}; const c = m.color || C.cyan, dot = S("circle", { cx: at(v), cy: y, r: 14, fill: c }, g);
        hideNow(dot); tl.to(dot, { opacity: 1, duration: 0.25 }, t2);
        const lb = label(t2 + 0.1, at(v), m.below ? y + 140 : y - 40, text, { anchor: "center", size: m.size || 52, color: c });
        return { dot, label: lb, hide(t3) { tl.to(dot, { opacity: 0, duration: 0.3 }, t3); lb.hide(t3); } }; } }; }
  // ---- seeded random (frames must repeat exactly, so no unseeded randomness) ----
  function rand(seed) { let s = seed >>> 0 || 1; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); }
  return { C, init, S, D, H, FS, cam, hatch, hazard, crawl, stripes, tube, wire, grad, part, shape, pipe, prism, beam, arrow, axis, obstacle, move, turn, pulse, liquid, badge, ground, capSym, fetSym,
           show, hide, dim, color, draw, callout, label, lens, box, flow, packet, particles, counter, readout, figure, gauge, bar,
           bits, plate, bus, chain, dimline, compare, title, progress, inset, rand, hideNow };
})();
