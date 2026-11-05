// Injected by learn.py into every HyperFrames scene. Runs once in the page after fonts load, then puts the timeline back.
// - Label overlap: steps the main timeline every 0.2 s; two visible BX text items (or plates) that overlap,
//   or a label cut off by the frame edge -> console.error
//   (HyperFrames check reports it as a console_error error, so `learn figure` fails).
// - Hold gap: the longest stretch of narration with no new timeline event; over 6 s -> console.warn
//   (reported as a warning; the engine prints it).
(() => {
  const TEXT = ".bx-plate,.bx-lbl,.bx-big,.bx-num,.bx-small,.bx-section,.bx-basis,.bx-bits,.bx-badge,.bx-title,.bx-gauge .tick";
  const r1 = (x) => Math.round(x * 10) / 10;
  function shown(el) {
    let o = 1;
    for (let e = el; e && e.nodeType === 1; e = e.parentElement) {
      const cs = getComputedStyle(e);
      if (cs.display === "none" || cs.visibility === "hidden") return false;
      o *= parseFloat(cs.opacity);
    }
    return o > 0.5;
  }
  function audit() {
    const tl = window.__timelines && window.__timelines.main;
    if (!tl || !window.LEARN) return;
    const speechEnd = LEARN.start[LEARN.start.length - 1] + LEARN.dur[LEARN.dur.length - 1];
    const starts = tl.getChildren(false, true, true).map((c) => c.startTime()).filter((t) => t <= speechEnd);
    const pts = [...new Set([0, ...starts.map(r1), r1(speechEnd)])].sort((a, b) => a - b);
    let gap = 0, from = 0;
    for (let i = 1; i < pts.length; i++) if (pts[i] - pts[i - 1] > gap) { gap = pts[i] - pts[i - 1]; from = pts[i - 1]; }
    if (gap > 6) console.warn(`BX hold: no new visual event from ${r1(from)}s to ${r1(from + gap)}s (${r1(gap)}s). ` +
      "Add a change every 3-5 s: a callout, a camera move, a colour change, a counter.");
    const els = [...document.querySelectorAll(TEXT)];
    if (els.length < 2) return;
    const t0 = tl.time(), seen = new Set(), found = [];
    for (let t = 0; t <= LEARN.total && found.length < 5; t += 0.2) {
      tl.seek(t, false);
      const vis = els.filter((e) => e.textContent.trim() && shown(e)).map((e) => [e, e.getBoundingClientRect()])
        .filter(([, r]) => r.right > 0 && r.left < 1920 && r.bottom > 0 && r.top < 1080);
      for (const [e, r] of vis) {           // a label cut by the frame edge cannot be read
        if (e.matches(".bx-plate,.bx-badge")) continue;
        if (r.left < -6 || r.right > 1926 || r.top < -6 || r.bottom > 1086) {
          const key = "edge|" + els.indexOf(e);
          if (!seen.has(key)) { seen.add(key); found.push(`at ${r1(t)}s "${e.textContent.trim().slice(0, 40)}" is cut off by the frame edge`); }
        }
      }
      for (let i = 0; i < vis.length; i++) for (let j = i + 1; j < vis.length; j++) {
        const [a, ra] = vis[i], [b, rb] = vis[j];
        if (a.contains(b) || b.contains(a)) continue;
        const ix = Math.min(ra.right, rb.right) - Math.max(ra.left, rb.left), iy = Math.min(ra.bottom, rb.bottom) - Math.max(ra.top, rb.top);
        if (ix > 4 && iy > 4) {
          const key = els.indexOf(a) + "|" + els.indexOf(b);          // per element pair, so a ticking counter reports once
          if (seen.has(key)) continue;
          seen.add(key);
          found.push(`at ${r1(t)}s "${a.textContent.trim().slice(0, 40)}" overlaps "${b.textContent.trim().slice(0, 40)}"`);
        }
      }
    }
    tl.seek(t0, false);
    found.forEach((f) => console.error("BX label overlap " + f + (f.includes("frame edge")
      ? ". Move it inside the frame at that moment: a different elbow point, a smaller size, or a camera that shows it."
      : ". Move one of them (leave out the callout elbow point so BX.callout picks a free side; pass shapes in `avoid`), or hide the first before the second appears.")));
  }
  (document.fonts ? document.fonts.ready : Promise.resolve()).then(audit);
})();
