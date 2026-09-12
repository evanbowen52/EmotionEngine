"""Emit emotion-polar-map.html — single file with embedded emotions.json + filter UI."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "emotions.json"
OUT_PATH = ROOT / "emotion-polar-map.html"


def main() -> None:
    with JSON_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    blob = json.dumps(data, ensure_ascii=False)

    html = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Emotion map (polar)</title>
  <style>
    * { box-sizing: border-box; }
    html, body {
      margin: 0;
      height: 100%;
      background: #1e1e1e;
      color: #c8c8c8;
      font-family: system-ui, Segoe UI, Roboto, sans-serif;
      overflow: hidden;
    }
    #toolbar {
      position: fixed;
      top: 10px;
      left: 10px;
      z-index: 2;
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
      align-items: center;
      max-width: min(420px, 46vw);
    }
    #toolbar button {
      background: #333;
      color: #ddd;
      border: 1px solid #555;
      border-radius: 6px;
      padding: 5px 9px;
      cursor: pointer;
      font-size: 12px;
    }
    #toolbar button:hover { background: #444; }
    #hint {
      font-size: 11px;
      color: #777;
      width: 100%;
      margin-top: 2px;
    }
    #controls {
      position: fixed;
      top: 10px;
      right: 10px;
      z-index: 3;
      width: min(300px, 42vw);
      max-height: calc(100vh - 20px);
      overflow: auto;
      padding: 12px 14px;
      background: rgba(30,30,32,0.94);
      border: 1px solid #444;
      border-radius: 10px;
      font-size: 12px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.5);
    }
    #controls .panel-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      margin: 0 0 10px 0;
    }
    #controls .panel-head h2 {
      margin: 0;
      font-size: 14px;
      font-weight: 600;
      color: #eee;
    }
    #controls.collapsed .panel-head {
      margin-bottom: 0;
    }
    #controls.collapsed .panel-body {
      display: none;
    }
    #controls.collapsed {
      width: auto;
      max-height: none;
      overflow: visible;
    }
    .panel-toggle {
      background: #38383c;
      color: #eee;
      border: 1px solid #5a5a62;
      border-radius: 6px;
      padding: 4px 10px;
      font-size: 11px;
      cursor: pointer;
      flex-shrink: 0;
      white-space: nowrap;
    }
    .panel-toggle:hover { background: #48484e; }
    #controls section { margin-bottom: 14px; }
    #controls label.row {
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 6px 0;
      cursor: pointer;
      color: #ccc;
    }
    #controls input[type="checkbox"] { accent-color: #6ad; }
    #controls input[type="search"], #controls input[type="text"] {
      width: 100%;
      padding: 7px 9px;
      border-radius: 6px;
      border: 1px solid #555;
      background: #2a2a2c;
      color: #eee;
      font-size: 12px;
    }
    #controls .range-row { margin: 8px 0; }
    #controls .range-row label { display: block; color: #999; margin-bottom: 4px; }
    #controls input[type="range"] { width: 100%; accent-color: #6ad; }
    #cat-boxes {
      max-height: 200px;
      overflow-y: auto;
      border: 1px solid #3a3a3c;
      border-radius: 6px;
      padding: 6px 8px;
      background: #252528;
    }
    #cat-actions { display: flex; gap: 6px; margin-top: 8px; flex-wrap: wrap; }
    #cat-actions button {
      flex: 1;
      min-width: 80px;
      padding: 5px 8px;
      font-size: 11px;
      background: #38383c;
      color: #ddd;
      border: 1px solid #555;
      border-radius: 5px;
      cursor: pointer;
    }
    #cat-actions button:hover { background: #48484c; }
    #viz {
      width: 100vw;
      height: 100vh;
      display: block;
    }
    .legend text { font-size: 11px; fill: #999; }
    .ring-label { font-size: 10px; fill: #666; }
    .legend-box-bg {
      fill: rgba(28, 32, 42, 0.92);
      stroke-width: 1.25;
    }
    .legend-box-text {
      font-size: 10px;
      font-weight: 500;
      fill: #ececf0;
    }
    .legend-box-text.ring-tier {
      fill: #c4c4cc;
      font-weight: 500;
    }
    .legend-hit { cursor: pointer; }
    .legend-category-box { pointer-events: auto; }
    .node circle {
      stroke: #0d0d0d;
      stroke-width: 1.2px;
      cursor: grab;
    }
    .node.highlight circle {
      stroke: #fdcb6e;
      stroke-width: 2.5px;
    }
    .node.orbit-focus circle {
      stroke: #dfe6e9;
      stroke-width: 2.5px;
    }
    .node.archetypal circle {
      stroke: #fdcb6e;
      stroke-width: 1.8px;
      stroke-dasharray: 3, 2.5;
    }
    .node.archetypal.highlight circle,
    .node.archetypal.orbit-focus circle {
      stroke-dasharray: none;
      stroke-width: 2.5px;
    }
    .node:active circle { cursor: grabbing; }
    .node text {
      font-size: 8.5px;
      fill: #bbb;
      pointer-events: none;
      text-shadow: 0 0 3px #000, 0 0 6px #000;
    }
    .link { stroke: #444; stroke-opacity: 0.35; stroke-dasharray: none; transition: stroke-opacity 0.25s, stroke 0.25s, stroke-width 0.25s; }
    .link.hidden { stroke-opacity: 0 !important; }
    .link.semantic {
      stroke-opacity: 0.65;
      stroke-width: 2px;
    }
    .link.semantic.confused_with {
      stroke: #e17055;
      stroke-dasharray: 4, 3;
    }
    .link.semantic.triggered_by {
      stroke: #0984e3;
      stroke-dasharray: 6, 2;
    }
    .link.semantic.triggers {
      stroke: #0984e3;
    }
    .link.semantic.adjacent {
      stroke: #00cec9;
    }
    .link.semantic.leads_to {
      stroke: #9b59b6;
    }
    .link.semantic.opposite_of {
      stroke: #fdcb6e;
      stroke-dasharray: 4, 4;
    }
    .conn-chip {
      background: #2a2a2c;
      color: #ccc;
      border: 1px solid #4a4a52;
      border-radius: 12px;
      padding: 3px 8px;
      font-size: 11px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 5px;
      transition: background 0.2s, border-color 0.2s, color 0.2s;
    }
    .conn-chip:hover {
      background: #38383c;
      color: #fff;
      border-color: #fdcb6e;
    }
    .conn-chip .relation-tag {
      font-size: 8px;
      text-transform: uppercase;
      color: #fdcb6e;
      font-weight: 600;
      background: rgba(253, 203, 110, 0.1);
      padding: 1px 4px;
      border-radius: 4px;
    }
    .conn-chip.confused_with .relation-tag { color: #e17055; background: rgba(225, 112, 85, 0.1); }
    .conn-chip.triggered_by .relation-tag, .conn-chip.triggers .relation-tag { color: #0984e3; background: rgba(9, 132, 227, 0.1); }
    .conn-chip.adjacent .relation-tag { color: #00cec9; background: rgba(0, 206, 201, 0.1); }
    .tooltip {
      position: fixed;
      pointer-events: none;
      z-index: 10;
      max-width: 320px;
      padding: 10px 12px;
      background: rgba(35,35,38,0.96);
      border: 1px solid #555;
      border-radius: 8px;
      font-size: 13px;
      line-height: 1.45;
      color: #e8e8e8;
      box-shadow: 0 6px 24px rgba(0,0,0,0.45);
      display: none;
    }
    .tooltip h3 {
      margin: 0 0 6px 0;
      font-size: 15px;
      font-weight: 600;
      color: #fff;
    }
    .tooltip .meta { color: #9aa; font-size: 11px; margin-bottom: 8px; }
    .tooltip .desc { color: #ccc; font-size: 12px; }
    .zoom-bg { fill: transparent; cursor: grab; }
    .zoom-bg:active { cursor: grabbing; }
    #spotlight {
      position: fixed;
      left: 12px;
      right: 12px;
      bottom: 12px;
      z-index: 4;
      max-width: min(720px, calc(100vw - 24px));
      margin: 0 auto;
      padding: 12px 14px 14px;
      background: rgba(26, 26, 28, 0.95);
      border: 1px solid #4a4a52;
      border-radius: 10px;
      box-shadow: 0 -4px 28px rgba(0,0,0,0.45);
      font-size: 13px;
      line-height: 1.45;
      color: #d0d0d4;
      max-height: min(34vh, 320px);
      overflow: auto;
    }
    #spotlight .spot-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 8px;
      flex-wrap: wrap;
    }
    #spotlight .spot-actions {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-shrink: 0;
    }
    #spotlight.collapsed .spot-inner {
      display: none;
    }
    #spotlight.collapsed .spot-head {
      margin-bottom: 0;
    }
    #spotlight.collapsed #spot-refresh {
      display: none;
    }
    #spotlight.collapsed {
      max-height: none;
      padding: 10px 14px;
    }
    #spotlight h2 {
      margin: 0;
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: #888;
    }
    #spotlight #spot-refresh {
      flex-shrink: 0;
      background: #38383c;
      color: #eee;
      border: 1px solid #5a5a62;
      border-radius: 6px;
      padding: 5px 12px;
      font-size: 12px;
      cursor: pointer;
    }
    #spotlight #spot-refresh:hover { background: #48484e; }
    #spotlight #spot-term {
      margin: 0 0 8px 0;
      font-size: 18px;
      font-weight: 600;
      color: #fff;
    }
    #spotlight dl {
      margin: 0 0 10px 0;
      display: grid;
      grid-template-columns: auto 1fr;
      gap: 4px 14px;
      font-size: 12px;
    }
    #spotlight dt {
      margin: 0;
      color: #888;
      font-weight: 500;
    }
    #spotlight dd {
      margin: 0;
      color: #c8c8ce;
    }
    #spotlight #spot-desc {
      margin: 0;
      color: #b8b8c0;
      font-size: 12px;
    }
    #spotlight .orbit-controls {
      margin-bottom: 12px;
      padding-bottom: 10px;
      border-bottom: 1px solid #3a3a42;
    }
    #spotlight .orbit-controls .range-row label {
      display: block;
      margin-bottom: 4px;
      color: #9a9aa2;
      font-size: 11px;
    }
    #spotlight .orbit-controls input[type="range"] {
      width: 100%;
    }
  </style>
</head>
<body>
  <div id="toolbar">
    <button type="button" id="zoom-in">Zoom +</button>
    <button type="button" id="zoom-out">Zoom −</button>
    <button type="button" id="reset-view">Reset view</button>
    <span id="hint">Wheel zoom · drag background to pan · drag nodes · click a category chip to show/hide · filters →</span>
  </div>

  <aside id="controls">
    <div class="panel-head">
      <h2>Map filters</h2>
      <button type="button" class="panel-toggle" id="controls-toggle" aria-expanded="true" aria-controls="controls-body">Hide</button>
    </div>
    <div id="controls-body" class="panel-body">
    <section>
      <input type="search" id="search" placeholder="Find term…" autocomplete="off" />
    </section>
    <section>
      <label class="row"><input type="checkbox" id="opt-english-only" /> English terms only</label>
      <label class="row"><input type="checkbox" id="opt-edges" checked /> Show edges (links)</label>
      <label class="row"><input type="checkbox" id="opt-labels" /> Always show labels (else zoom in)</label>
    </section>
    <section>
      <div class="range-row">
        <label>Intensity radius · min <span id="r-min-v"></span></label>
        <input type="range" id="r-min" min="0" max="100" value="0" />
      </div>
      <div class="range-row">
        <label>Intensity radius · max <span id="r-max-v"></span></label>
        <input type="range" id="r-max" min="0" max="100" value="100" />
      </div>
      <div style="color:#777;font-size:11px;margin-top:4px;">Soft ring ≈0.34 · Medium ≈0.58 · Intense ≈0.86</div>
    </section>
    <section>
      <div style="color:#999;margin-bottom:6px;">Categories</div>
      <div id="cat-boxes"></div>
      <div id="cat-actions">
        <button type="button" id="cat-all">All</button>
        <button type="button" id="cat-none">None</button>
      </div>
    </section>
    </div>
  </aside>

  <div class="tooltip" id="tip"></div>
  <svg id="viz" aria-label="Emotion polar graph"></svg>

  <aside id="spotlight" aria-live="polite">
    <div class="spot-head">
      <h2>Random term</h2>
      <div class="spot-actions">
        <button type="button" class="panel-toggle" id="spot-toggle" aria-expanded="true" aria-controls="spotlight-inner">Hide</button>
        <button type="button" id="spot-refresh">Pick another</button>
      </div>
    </div>
    <div id="spotlight-inner" class="spot-inner">
    <div class="orbit-controls">
      <label class="row"><input type="checkbox" id="orbit-enable" /> Orbit (follow circle by angle)</label>
      <label class="row"><input type="checkbox" id="orbit-loop" checked /> Loop</label>
      <div class="range-row">
        <label>Orbit pace · <span id="orbit-pace-v">—</span></label>
        <input type="range" id="orbit-pace" min="0" max="100" value="35" />
      </div>
    </div>
    <h3 id="spot-term"></h3>
    <dl id="spot-meta"></dl>
    <p id="spot-desc"></p>
    <div id="spot-connections-container" style="margin-top: 12px; border-top: 1px solid #3a3a42; padding-top: 10px; display: none;">
      <h4 style="margin: 0 0 8px 0; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: #888;">Connected Emotions</h4>
      <div id="spot-connections" style="display: flex; gap: 6px; flex-wrap: wrap;"></div>
    </div>
    </div>
  </aside>

  <script type="application/json" id="emotion-data">__BLOB__</script>
  <script src="https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js"></script>
  <script>
  (function () {
    const RAW = JSON.parse(document.getElementById("emotion-data").textContent);

    const ui = {
      cat: Object.fromEntries([...new Set(RAW.map((d) => d.category))].sort().map((c) => [c, true])),
      rMin: 0.1,
      rMax: 0.95,
      edges: true,
      labelsAlways: false,
      search: "",
      zoomK: 1,
      selectedId: null,
      englishOnly: false,
    };

    function scorePleasantness(s) {
      if (!s) return 0;
      const t = String(s).toLowerCase();
      const parts = t.split(/[/\s]+/).filter(Boolean);
      const scoreWord = (w) => {
        if (w.includes("very") && w.includes("high")) return 1;
        if (w.includes("very") && w.includes("low")) return -1;
        if (w.includes("high")) return 0.85;
        if (w.includes("low")) return -0.85;
        if (w.includes("neutral")) return 0;
        if (w.includes("bittersweet")) return 0;
        if (w.includes("conflicted")) return 0;
        return 0;
      };
      if (parts.length <= 1) return scoreWord(t);
      return parts.reduce((a, w) => a + scoreWord(w), 0) / parts.length;
    }

    function scoreEnergy(s) {
      if (!s) return 0;
      const t = String(s).toLowerCase();
      const parts = t.split(/[/\s]+/).filter(Boolean);
      const scoreWord = (w) => {
        if (w.includes("very") && w.includes("high")) return 1;
        if (w.includes("very") && w.includes("low")) return -1;
        if (w.includes("internalized")) return 0.3;
        if (w.includes("high")) return 0.8;
        if (w.includes("medium")) return 0.35;
        if (w.includes("low")) return -0.55;
        if (w === "variable") return 0;
        return 0;
      };
      if (parts.length <= 1) return scoreWord(t);
      return parts.reduce((a, w) => a + scoreWord(w), 0) / parts.length;
    }

    function intensityRadius(intensity) {
      const s = String(intensity || "").toLowerCase();
      if (s.includes("intense")) return 0.86;
      if (s.includes("soft") && s.includes("medium")) return 0.42;
      if (s.includes("soft")) return 0.34;
      if (s.includes("medium")) return 0.58;
      if (s.includes("variable")) return 0.5;
      if (s.includes("low")) return 0.24;
      return 0.5;
    }

    const categories = [...new Set(RAW.map((d) => d.category))].sort();
    const nCat = categories.length;
    const catIndex = Object.fromEntries(categories.map((c, i) => [c, i]));
    const color = d3.scaleOrdinal(d3.quantize(d3.interpolateSinebow, nCat + 1));

    const byTerm = d3.group(RAW, (d) => d.term.trim().toLowerCase());

    const TWO_PI = Math.PI * 2;
    const nodes = RAW.map((d, i) => {
      const ci = catIndex[d.category];
      const sector = TWO_PI / nCat;
      const mid = (ci + 0.5) * sector - Math.PI / 2;
      const ep = scorePleasantness(d.pleasantness);
      const ee = scoreEnergy(d.energy);
      const jitter = (ep * 0.22 + ee * 0.18) * sector * 0.45;
      const angle = mid + jitter + Math.sin(i * 12.9898) * 0.03 * sector;
      const r = intensityRadius(d.intensity);
      const sisters = byTerm.get(d.term.trim().toLowerCase()) || [];
      const distinctCats = new Set(sisters.map((x) => x.category));
      let labelText = d.term;
      if (distinctCats.size > 1) {
        const head = d.category.split(",")[0].trim();
        const short = head.length > 14 ? head.slice(0, 13) + "…" : head;
        labelText = d.term + " · " + short;
      }
      return {
        id: i,
        term: d.term,
        labelText,
        category: d.category,
        intensity: d.intensity,
        origin: d.origin,
        description: d.description,
        is_archetype: d.is_archetype,
        rNorm: r,
        theta: angle,
        sector,
        catI: ci,
      };
    });

    const nodesByTerm = d3.group(nodes, (d) => d.term.trim().toLowerCase());

    const W = window.innerWidth;
    const H = window.innerHeight;
    const cx = W / 2;
    const cy = H / 2;
    const R_chart = Math.min(W, H) * 0.42;
    const R = R_chart * 0.86;
    const catBox = document.getElementById("cat-boxes");

    nodes.forEach((d) => {
      d.tx = cx + d.rNorm * R * Math.cos(d.theta);
      d.ty = cy + d.rNorm * R * Math.sin(d.theta);
      d.x = d.tx;
      d.y = d.ty;
    });

    function buildCategoryLinks(subset) {
      const byCat = d3.group(subset, (d) => d.category);
      const L = [];
      byCat.forEach((list) => {
        const sorted = [...list].sort((a, b) => a.theta - b.theta || a.rNorm - b.rNorm);
        const n = sorted.length;
        for (let i = 0; i < n; i++) {
          const a = sorted[i];
          const b = sorted[(i + 1) % n];
          if (a.id !== b.id) L.push({ source: a.id, target: b.id });
          if (n > 2) {
            const c = sorted[(i + 2) % n];
            if (a.id !== c.id) L.push({ source: a.id, target: c.id });
          }
        }
      });
      return L;
    }

    function buildSemanticLinks(subset) {
      const subsetIds = new Set(subset.map((d) => d.id));
      const L = [];
      subset.forEach((d) => {
        const rawItem = RAW[d.id];
        if (rawItem && Array.isArray(rawItem.connections)) {
          rawItem.connections.forEach((conn) => {
            const targetTerm = conn.term.trim().toLowerCase();
            const targets = nodesByTerm.get(targetTerm) || [];
            targets.forEach((targetNode) => {
              if (subsetIds.has(targetNode.id)) {
                L.push({
                  source: d.id,
                  target: targetNode.id,
                  relation: conn.relation,
                  notes: conn.notes,
                  isSemantic: true
                });
              }
            });
          });
        }
      });
      return L;
    }

    function normVisible(d) {
      return d.rNorm >= ui.rMin && d.rNorm <= ui.rMax;
    }

    function catVisible(d) {
      return !!ui.cat[d.category];
    }

    function searchMatch(d) {
      const q = ui.search.trim().toLowerCase();
      if (!q) return false;
      return String(d.term).toLowerCase().includes(q);
    }

    function originVisible(d) {
      if (!ui.englishOnly) return true;
      const raw = RAW[d.id];
      const origin = raw && raw.origin ? raw.origin.trim().toLowerCase() : "english";
      return origin === "english";
    }

    function filteredNodes() {
      return nodes.filter((d) => catVisible(d) && normVisible(d) && originVisible(d));
    }

    let orbitTimer = null;
    let orbitIndex = 0;
    let orbitList = [];

    function buildOrbitList() {
      return filteredNodes()
        .slice()
        .sort((a, b) => a.theta - b.theta || a.rNorm - b.rNorm || a.id - b.id);
    }

    function clearOrbitTimer() {
      if (orbitTimer != null) {
        clearTimeout(orbitTimer);
        orbitTimer = null;
      }
    }

    function orbitPaceMs() {
      const el = document.getElementById("orbit-pace");
      const pct = el ? +el.value : 35;
      return Math.round(600 + (pct / 100) * 4400);
    }

    function syncOrbitPaceLabel() {
      const lab = document.getElementById("orbit-pace-v");
      if (lab) lab.textContent = (orbitPaceMs() / 1000).toFixed(1) + " s";
    }

    function pauseOrbitFromUser() {
      clearOrbitTimer();
      const cb = document.getElementById("orbit-enable");
      if (cb && cb.checked) cb.checked = false;
      if (nodeSel) nodeSel.classed("orbit-focus", false);
    }

    function showCurrentOrbitStep() {
      orbitList = buildOrbitList();
      if (!orbitList.length) return;
      orbitIndex = Math.max(0, Math.min(orbitIndex, orbitList.length - 1));
      const d = orbitList[orbitIndex];
      renderSpotlight(RAW[d.id]);
      if (!nodeSel || nodeSel.empty()) return;
      nodeSel.classed("orbit-focus", (n) => n.id === d.id);
      const g = nodeSel.filter((n) => n.id === d.id);
      g.select("circle")
        .interrupt()
        .attr("r", 5)
        .transition()
        .duration(180)
        .attr("r", 9)
        .transition()
        .duration(220)
        .attr("r", 5);
    }

    function scheduleNextOrbit() {
      clearOrbitTimer();
      const cb = document.getElementById("orbit-enable");
      if (!cb || !cb.checked) return;
      const dwell = orbitPaceMs();
      orbitTimer = setTimeout(() => {
        orbitTimer = null;
        if (!document.getElementById("orbit-enable").checked) return;
        orbitList = buildOrbitList();
        if (!orbitList.length) {
          pauseOrbitFromUser();
          return;
        }
        const loop = document.getElementById("orbit-loop").checked;
        if (orbitIndex >= orbitList.length - 1) {
          if (loop) orbitIndex = 0;
          else {
            pauseOrbitFromUser();
            return;
          }
        } else orbitIndex++;

        orbitIndex = Math.min(orbitIndex, orbitList.length - 1);
        showCurrentOrbitStep();
        scheduleNextOrbit();
      }, dwell);
    }

    function syncOrbitAfterGraphChange() {
      const cb = document.getElementById("orbit-enable");
      if (!cb || !cb.checked) return;
      clearOrbitTimer();
      const prevId =
        orbitList.length && orbitIndex >= 0 && orbitIndex < orbitList.length
          ? orbitList[orbitIndex].id
          : null;
      orbitList = buildOrbitList();
      if (!orbitList.length) {
        cb.checked = false;
        return;
      }
      if (prevId != null) {
        const j = orbitList.findIndex((n) => n.id === prevId);
        orbitIndex = j >= 0 ? j : Math.min(orbitIndex, orbitList.length - 1);
      } else orbitIndex = Math.min(orbitIndex, orbitList.length - 1);
      showCurrentOrbitStep();
      scheduleNextOrbit();
    }

    function startOrbitFromCheckbox() {
      orbitList = buildOrbitList();
      const cb = document.getElementById("orbit-enable");
      if (!orbitList.length) {
        if (cb) cb.checked = false;
        return;
      }
      orbitIndex = Math.min(orbitIndex, orbitList.length - 1);
      showCurrentOrbitStep();
      scheduleNextOrbit();
    }

    const svg = d3.select("#viz").attr("width", W).attr("height", H);
    svg.on("click", () => {
      clearSelection();
    });
    const gRoot = svg.append("g");
    gRoot
      .append("rect")
      .attr("class", "zoom-bg")
      .attr("width", W)
      .attr("height", H)
      .attr("x", 0)
      .attr("y", 0);

    function legendTextBox(gParent, x, y, label, strokeColor, meta) {
      const padX = 7;
      const padY = 4;
      const g = gParent.append("g").attr("transform", `translate(${x},${y})`);
      if (meta && meta.category) g.attr("class", "legend-category-box");
      const text = g
        .append("text")
        .attr("class", strokeColor ? "legend-box-text" : "legend-box-text ring-tier")
        .attr("text-anchor", "middle")
        .attr("dominant-baseline", "middle")
        .attr("pointer-events", "none")
        .text(label);
      const bb = text.node().getBBox();
      const rx = bb.x - padX;
      const ry = bb.y - padY;
      const rw = bb.width + 2 * padX;
      const rh = bb.height + 2 * padY;
      g.insert("rect", "text")
        .attr("class", "legend-box-bg")
        .attr("x", rx)
        .attr("y", ry)
        .attr("width", rw)
        .attr("height", rh)
        .attr("rx", 5)
        .attr("ry", 5)
        .attr("stroke", strokeColor || "#5c6478")
        .attr("pointer-events", "none");
      if (meta && meta.category) {
        g.append("rect")
          .attr("class", "legend-hit")
          .attr("x", rx)
          .attr("y", ry)
          .attr("width", rw)
          .attr("height", rh)
          .attr("rx", 5)
          .attr("ry", 5)
          .attr("fill", "transparent")
          .attr("pointer-events", "all")
          .attr("title", "Show or hide: " + meta.category)
          .on("click", (e) => {
            e.stopPropagation();
            const cat = meta.category;
            ui.cat[cat] = !ui.cat[cat];
            const inp = [...catBox.querySelectorAll('input[type="checkbox"]')].find(
              (el) => el.dataset.cat === cat
            );
            if (inp) inp.checked = ui.cat[cat];
            applyGraph();
          });
      }
      return g;
    }

    const legendCategoryState = [];

    const ringLabels = [
      { r: 0.34, t: "Soft" },
      { r: 0.58, t: "Medium" },
      { r: 0.86, t: "Intense" },
    ];
    const legendG = gRoot.append("g").attr("class", "legend");
    ringLabels.forEach((ring) => {
      legendG
        .append("circle")
        .attr("cx", cx)
        .attr("cy", cy)
        .attr("r", ring.r * R)
        .attr("fill", "none")
        .attr("stroke", "#333")
        .attr("stroke-dasharray", "4 6");
      const lx = cx + ring.r * R + 6;
      const ly = cy - ring.r * R + 4;
      legendTextBox(legendG, lx, ly, ring.t, null, null);
    });

    const lr = R + Math.max(52, R_chart * 0.13);
    categories.forEach((c, i) => {
      const a0 = (i / nCat) * TWO_PI - Math.PI / 2;
      const a1 = ((i + 1) / nCat) * TWO_PI - Math.PI / 2;
      const arc = d3.path();
      arc.moveTo(cx, cy);
      arc.arc(cx, cy, R + 14, a0, a1);
      arc.closePath();
      const wedge = legendG
        .append("path")
        .attr("d", arc.toString())
        .attr("fill", color(c))
        .attr("fill-opacity", 0.07)
        .attr("stroke", "none")
        .attr("pointer-events", "none");
      const mid = (a0 + a1) / 2;
      const label = c.length > 22 ? c.slice(0, 20) + "…" : c;
      const labelG = legendTextBox(
        legendG,
        cx + lr * Math.cos(mid),
        cy + lr * Math.sin(mid),
        label,
        color(c),
        { category: c }
      );
      legendCategoryState.push({ category: c, wedge, labelG });
    });

    function refreshLegendCategoryStyles() {
      legendCategoryState.forEach(({ category, wedge, labelG }) => {
        const on = ui.cat[category];
        wedge.attr("fill-opacity", on ? 0.07 : 0.02);
        labelG
          .select(".legend-box-bg")
          .attr("opacity", on ? 1 : 0.4)
          .attr("stroke-opacity", on ? 1 : 0.35);
        labelG.select(".legend-box-text").attr("opacity", on ? 1 : 0.48);
      });
    }

    const gLinks = gRoot.append("g").attr("class", "links");
    const gNodes = gRoot.append("g").attr("class", "nodes");

    const tip = d3.select("#tip");

    function escapeHtml(s) {
      return String(s)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
    }

    function labelOpacity(d) {
      if (ui.labelsAlways) return 1;
      if (searchMatch(d)) return 1;
      return ui.zoomK >= 1.35 ? 1 : 0;
    }

    function updateLabelVisibility() {
      gNodes.selectAll(".node text").attr("opacity", (d) => labelOpacity(d));
    }

    let sim = null;
    let linkSel = null;
    let nodeSel = null;

    function positionNodeLabels() {
      if (!nodeSel || nodeSel.empty()) return;
      const z = ui.zoomK;
      const baseR = 10 + Math.min(7, (z - 1) * 4);
      nodeSel.each(function (d) {
        const ang = Math.atan2(d.y - cy, d.x - cx);
        const c = Math.cos(ang);
        const s = Math.sin(ang);
        const px = -s;
        const py = c;
        const tang = (((d.id * 31) % 13) - 6) * 1.25;
        const dx = c * baseR + px * tang;
        const dy = s * baseR + py * tang;
        d3.select(this)
          .select("text")
          .attr("dx", dx)
          .attr("dy", dy)
          .attr("text-anchor", "middle")
          .attr("dominant-baseline", "middle");
      });
    }

    function ticked() {
      linkSel
        .attr("x1", (d) => d.source.x)
        .attr("y1", (d) => d.source.y)
        .attr("x2", (d) => d.target.x)
        .attr("y2", (d) => d.target.y);
      nodeSel.attr("transform", (d) => `translate(${d.x},${d.y})`);
      positionNodeLabels();
    }

    const dragBehav = d3
      .drag()
      .on("start", (ev, d) => {
        pauseOrbitFromUser();
        if (!sim) return;
        sim.alphaTarget(0.35).restart();
        d.fx = d.x;
        d.fy = d.y;
      })
      .on("drag", (ev, d) => {
        const t = d3.zoomTransform(svg.node());
        const [px, py] = d3.pointer(ev, gRoot.node());
        d.fx = (px - t.x) / t.k;
        d.fy = (py - t.y) / t.k;
      })
      .on("end", (ev, d) => {
        if (!sim) return;
        sim.alphaTarget(0);
        d.fx = null;
        d.fy = null;
      });

    function applyGraph() {
      const vis = filteredNodes();
      const catLinks = buildCategoryLinks(vis);
      const semLinks = buildSemanticLinks(vis);
      const links = [...catLinks, ...semLinks];

      vis.forEach((d) => {
        if (d.x == null || Number.isNaN(d.x)) {
          d.x = d.tx;
          d.y = d.ty;
        }
      });

      if (sim) {
        sim.stop();
        sim = null;
      }

      linkSel = gLinks
        .selectAll("line")
        .data(links, (e) => {
          const s = typeof e.source === "object" ? e.source.id : e.source;
          const t = typeof e.target === "object" ? e.target.id : e.target;
          return s + "-" + t;
        })
        .join("line")
        .attr("class", (e) => "link" + (e.isSemantic ? " semantic " + (e.relation || "adjacent") : ""));

      nodeSel = gNodes
        .selectAll("g")
        .data(vis, (d) => d.id)
        .join(
          (enter) => {
            const g = enter.append("g").attr("class", "node");
            g.append("circle").attr("r", 5);
            g.append("text").attr("dx", 0).attr("dy", 0);
            return g;
          },
          (update) => update,
          (exit) => exit.remove()
        );

      nodeSel
        .select("circle")
        .attr("fill", (d) => color(d.category));

      nodeSel
        .select("text")
        .text((d) => {
          const t = d.labelText || d.term;
          return t.length > 22 ? t.slice(0, 20) + "…" : t;
        })
        .attr("opacity", (d) => labelOpacity(d));

      nodeSel.classed("highlight", (d) => searchMatch(d));
      nodeSel.classed("archetypal", (d) => d.is_archetype);

      nodeSel.call(dragBehav);
      nodeSel
        .on("mouseenter", (ev, d) => {
          tip.style("display", "block")
            .html(
              "<h3>" +
                escapeHtml(d.term) +
                '</h3><div class="meta">' +
                escapeHtml(d.category) +
                " · " +
                escapeHtml(d.intensity) +
                (d.origin ? " · " + escapeHtml(d.origin) : "") +
                '</div><div class="desc">' +
                escapeHtml((d.description || "").slice(0, 420)) +
                ((d.description || "").length > 420 ? "…" : "") +
                "</div>"
            );
        })
        .on("mousemove", (ev) => {
          tip
            .style("left", ev.clientX + 14 + "px")
            .style("top", ev.clientY + 14 + "px");
        })
        .on("mouseleave", () => tip.style("display", "none"))
        .on("click", (ev, d) => {
          ev.stopPropagation();
          pauseOrbitFromUser();
          selectNode(d);
        });

      if (vis.length === 0) {
        linkSel.style("display", "none");
        refreshEdgesVisibility();
        updateLabelVisibility();
        refreshLegendCategoryStyles();
        pauseOrbitFromUser();
        return;
      }

      linkSel.style("display", null);

      sim = d3
        .forceSimulation(vis)
        .force(
          "link",
          d3
            .forceLink(links)
            .id((d) => d.id)
            .distance(32)
            .strength(0.35)
        )
        .force("charge", d3.forceManyBody().strength(-48))
        .force("collision", d3.forceCollide().radius(13).strength(0.92))
        .force("x", d3.forceX((d) => d.tx).strength(0.4))
        .force("y", d3.forceY((d) => d.ty).strength(0.4))
        .on("tick", ticked);

      refreshEdgesVisibility();
      updateLabelVisibility();
      positionNodeLabels();
      refreshLegendCategoryStyles();
      syncOrbitAfterGraphChange();
    }

    function refreshEdgesVisibility() {
      const on = ui.edges;
      linkSel.classed("hidden", !on);
    }

    function syncSlidersFromUi() {
      const toPct = (v) => Math.round(((v - 0.1) / 0.85) * 100);
      document.getElementById("r-min").value = String(toPct(ui.rMin));
      document.getElementById("r-max").value = String(toPct(ui.rMax));
      document.getElementById("r-min-v").textContent = ui.rMin.toFixed(2);
      document.getElementById("r-max-v").textContent = ui.rMax.toFixed(2);
    }

    function readSliders() {
      const rv = (id) => {
        const v = +document.getElementById(id).value;
        return 0.1 + (v / 100) * 0.85;
      };
      let a = rv("r-min");
      let b = rv("r-max");
      if (a > b) [a, b] = [b, a];
      ui.rMin = a;
      ui.rMax = b;
      syncSlidersFromUi();
    }

    categories.forEach((c) => {
      const row = document.createElement("label");
      row.className = "row";
      const inp = document.createElement("input");
      inp.type = "checkbox";
      inp.checked = true;
      inp.dataset.cat = c;
      const span = document.createElement("span");
      span.style.flex = "1";
      span.textContent = c.length > 36 ? c.slice(0, 34) + "…" : c;
      span.title = c;
      row.appendChild(inp);
      row.appendChild(span);
      catBox.appendChild(row);
    });

    catBox.addEventListener("change", (ev) => {
      const t = ev.target;
      if (!(t instanceof HTMLInputElement) || t.type !== "checkbox") return;
      const name = t.dataset.cat;
      if (!name) return;
      ui.cat[name] = t.checked;
      applyGraph();
    });

    document.getElementById("cat-all").addEventListener("click", () => {
      catBox.querySelectorAll('input[type="checkbox"]').forEach((el) => {
        el.checked = true;
        const n = el.dataset.cat;
        if (n) ui.cat[n] = true;
      });
      applyGraph();
    });

    document.getElementById("cat-none").addEventListener("click", () => {
      catBox.querySelectorAll('input[type="checkbox"]').forEach((el) => {
        el.checked = false;
        const n = el.dataset.cat;
        if (n) ui.cat[n] = false;
      });
      applyGraph();
    });

    document.getElementById("opt-english-only").addEventListener("change", (ev) => {
      ui.englishOnly = ev.target.checked;
      applyGraph();
    });

    document.getElementById("opt-edges").addEventListener("change", (ev) => {
      ui.edges = ev.target.checked;
      refreshEdgesVisibility();
    });

    document.getElementById("opt-labels").addEventListener("change", (ev) => {
      ui.labelsAlways = ev.target.checked;
      updateLabelVisibility();
      nodeSel && nodeSel.select("text").attr("opacity", (d) => labelOpacity(d));
    });

    ["r-min", "r-max"].forEach((id) =>
      document.getElementById(id).addEventListener("input", () => {
        readSliders();
        applyGraph();
      })
    );

    document.getElementById("search").addEventListener("input", (ev) => {
      ui.search = ev.target.value;
      if (nodeSel)
        nodeSel.classed("highlight", (d) => searchMatch(d));
      updateLabelVisibility();
      if (nodeSel) nodeSel.select("text").attr("opacity", (d) => labelOpacity(d));
    });

    syncSlidersFromUi();
    applyGraph();

    const zoom = d3
      .zoom()
      .scaleExtent([0.12, 10])
      .filter((ev) => {
        if (ev.type === "wheel") return true;
        if (ev.button !== 0) return false;
        return ev.target.classList.contains("zoom-bg");
      })
      .on("zoom", (ev) => {
        pauseOrbitFromUser();
        ui.zoomK = ev.transform.k;
        gRoot.attr("transform", ev.transform);
        updateLabelVisibility();
        positionNodeLabels();
        if (nodeSel)
          nodeSel.select("text").attr("opacity", (d) => labelOpacity(d));
      });

    svg.call(zoom).call(zoom.transform, d3.zoomIdentity);

    document.getElementById("zoom-in").addEventListener("click", () =>
      svg.transition().duration(200).call(zoom.scaleBy, 1.25)
    );
    document.getElementById("zoom-out").addEventListener("click", () =>
      svg.transition().duration(200).call(zoom.scaleBy, 0.8)
    );
    document.getElementById("reset-view").addEventListener("click", () =>
      svg.transition().duration(300).call(zoom.transform, d3.zoomIdentity)
    );

    function pickRandomIndex(n) {
      if (n <= 0) return 0;
      if (typeof crypto !== "undefined" && crypto.getRandomValues) {
        const buf = new Uint32Array(1);
        crypto.getRandomValues(buf);
        return buf[0] % n;
      }
      return Math.floor(Math.random() * n);
    }

    function centerCameraOnNode(nodeObj) {
      if (!nodeObj) return;
      const transform = d3.zoomTransform(svg.node());
      const k = transform.k;
      const tx = cx - nodeObj.x * k;
      const ty = cy - nodeObj.y * k;
      svg.transition()
        .duration(450)
        .call(zoom.transform, d3.zoomIdentity.translate(tx, ty).scale(k));
    }

    function highlightConnectionsFor(selectedNode) {
      if (!nodeSel || nodeSel.empty()) return;

      if (!selectedNode) {
        nodeSel.selectAll("circle")
          .style("opacity", null)
          .attr("stroke", (d) => d.is_archetype ? "#fdcb6e" : "#0d0d0d")
          .attr("stroke-width", (d) => d.is_archetype ? "1.8px" : "1.2px")
          .style("stroke-dasharray", (d) => d.is_archetype ? "3, 2.5" : "none");
        nodeSel.selectAll("text")
          .style("opacity", null);
        if (linkSel && !linkSel.empty()) {
          linkSel.style("opacity", null);
        }
        updateLabelVisibility();
        return;
      }

      const connectedIds = new Set([selectedNode.id]);
      const rawItem = RAW[selectedNode.id];
      if (rawItem && Array.isArray(rawItem.connections)) {
        rawItem.connections.forEach((conn) => {
          const targetTerm = conn.term.trim().toLowerCase();
          const targets = nodesByTerm.get(targetTerm) || [];
          targets.forEach((targetNode) => {
            connectedIds.add(targetNode.id);
          });
        });
      }

      nodeSel.each(function (d) {
        const isConnected = connectedIds.has(d.id);
        const isSelf = d.id === selectedNode.id;
        const g = d3.select(this);
        g.select("circle")
          .style("opacity", isConnected ? 1.0 : 0.15)
          .attr("stroke", isSelf ? "#fdcb6e" : (isConnected ? "#dfe6e9" : (d.is_archetype ? "#fdcb6e" : "#0d0d0d")))
          .attr("stroke-width", isSelf ? "3px" : (isConnected ? "2px" : (d.is_archetype ? "1.8px" : "1.2px")))
          .style("stroke-dasharray", (d.is_archetype && !isSelf && !isConnected) ? "3, 2.5" : "none");
        g.select("text")
          .style("opacity", isConnected ? 1.0 : 0.05);
      });

      if (linkSel && !linkSel.empty()) {
        linkSel.style("opacity", (e) => {
          const s = typeof e.source === "object" ? e.source.id : e.source;
          const t = typeof e.target === "object" ? e.target.id : e.target;
          const isConnected = (s === selectedNode.id || t === selectedNode.id);
          if (isConnected) {
            return e.isSemantic ? 1.0 : 0.4;
          }
          return 0.03;
        });
      }
    }

    function selectNode(nodeObj) {
      if (!nodeObj) {
        clearSelection();
        return;
      }
      ui.selectedId = nodeObj.id;
      renderSpotlight(RAW[nodeObj.id], nodeObj);
      highlightConnectionsFor(nodeObj);
      centerCameraOnNode(nodeObj);
    }

    function clearSelection() {
      ui.selectedId = null;
      highlightConnectionsFor(null);
    }

    function renderSpotlight(d, nodeObj = null) {
      if (!d) return;

      if (!nodeObj) {
        const list = nodesByTerm.get(d.term.trim().toLowerCase()) || [];
        if (list.length > 0) {
          nodeObj = list[0];
        }
      }

      document.getElementById("spot-term").textContent = d.term || "";
      const origin = d.origin != null && d.origin !== "" ? d.origin : "English";
      const meta = document.getElementById("spot-meta");
      meta.innerHTML =
        "<dt>Origin</dt><dd>" +
        escapeHtml(origin) +
        "</dd><dt>Category</dt><dd>" +
        escapeHtml(d.category || "") +
        "</dd><dt>Intensity</dt><dd>" +
        escapeHtml(d.intensity || "") +
        "</dd><dt>Energy</dt><dd>" +
        escapeHtml(d.energy || "—") +
        "</dd><dt>Pleasantness</dt><dd>" +
        escapeHtml(d.pleasantness || "—") +
        "</dd>";
      document.getElementById("spot-desc").textContent = d.description || "";

      const connContainer = document.getElementById("spot-connections-container");
      const connDiv = document.getElementById("spot-connections");
      if (connContainer && connDiv) {
        connDiv.innerHTML = "";
        if (Array.isArray(d.connections) && d.connections.length > 0) {
          connContainer.style.display = "block";
          d.connections.forEach((conn) => {
            const chip = document.createElement("button");
            chip.type = "button";
            chip.className = "conn-chip " + (conn.relation || "adjacent");

            const termSpan = document.createElement("span");
            termSpan.textContent = conn.term;

            const relSpan = document.createElement("span");
            relSpan.className = "relation-tag";
            relSpan.textContent = conn.relation ? conn.relation.replace("_", " ") : "adjacent";

            chip.appendChild(termSpan);
            chip.appendChild(relSpan);

            if (conn.notes) {
              chip.title = conn.notes;
            }

            chip.addEventListener("click", (ev) => {
              ev.stopPropagation();
              const targets = nodesByTerm.get(conn.term.trim().toLowerCase()) || [];
              if (targets.length > 0) {
                const visible = targets.filter((n) => catVisible(n) && normVisible(n));
                const targetNode = visible.length > 0 ? visible[0] : targets[0];
                selectNode(targetNode);
              }
            });
            connDiv.appendChild(chip);
          });
        } else {
          connContainer.style.display = "none";
        }
      }
    }

    function refreshSpotlight() {
      if (!RAW.length) return;
      renderSpotlight(RAW[pickRandomIndex(RAW.length)]);
    }

    function syncPanelToggleButtons() {
      const c = document.getElementById("controls");
      const ct = document.getElementById("controls-toggle");
      const cCollapsed = c.classList.contains("collapsed");
      ct.setAttribute("aria-expanded", cCollapsed ? "false" : "true");
      ct.textContent = cCollapsed ? "Show" : "Hide";

      const s = document.getElementById("spotlight");
      const st = document.getElementById("spot-toggle");
      const sCollapsed = s.classList.contains("collapsed");
      st.setAttribute("aria-expanded", sCollapsed ? "false" : "true");
      st.textContent = sCollapsed ? "Show" : "Hide";
    }

    try {
      if (localStorage.getItem("emotionPolar.controlsCollapsed") === "1")
        document.getElementById("controls").classList.add("collapsed");
      if (localStorage.getItem("emotionPolar.spotlightCollapsed") === "1")
        document.getElementById("spotlight").classList.add("collapsed");
    } catch (e) {}

    document.getElementById("controls-toggle").addEventListener("click", () => {
      const el = document.getElementById("controls");
      el.classList.toggle("collapsed");
      try {
        localStorage.setItem(
          "emotionPolar.controlsCollapsed",
          el.classList.contains("collapsed") ? "1" : "0"
        );
      } catch (e) {}
      syncPanelToggleButtons();
    });
    document.getElementById("spot-toggle").addEventListener("click", () => {
      const el = document.getElementById("spotlight");
      el.classList.toggle("collapsed");
      if (el.classList.contains("collapsed")) pauseOrbitFromUser();
      try {
        localStorage.setItem(
          "emotionPolar.spotlightCollapsed",
          el.classList.contains("collapsed") ? "1" : "0"
        );
      } catch (e) {}
      syncPanelToggleButtons();
    });

    syncOrbitPaceLabel();
    document.getElementById("orbit-pace").addEventListener("input", () => {
      syncOrbitPaceLabel();
      if (document.getElementById("orbit-enable").checked) {
        clearOrbitTimer();
        scheduleNextOrbit();
      }
    });
    document.getElementById("orbit-enable").addEventListener("change", (ev) => {
      if (ev.target.checked) {
        startOrbitFromCheckbox();
      } else {
        clearOrbitTimer();
        if (nodeSel) nodeSel.classed("orbit-focus", false);
      }
    });

    refreshSpotlight();
    syncPanelToggleButtons();
    document
      .getElementById("spot-refresh")
      .addEventListener("click", () => {
        pauseOrbitFromUser();
        refreshSpotlight();
      });

    window.addEventListener("resize", () => location.reload());
  })();
  </script>
</body>
</html>
"""

    html = html.replace("__BLOB__", blob)
    OUT_PATH.write_text(html, encoding="utf-8")
    print("Wrote", OUT_PATH, len(html.encode("utf-8")), "bytes")


if __name__ == "__main__":
    main()
