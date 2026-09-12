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

    /* Somatic Wizard Styles */
    #wizard-panel {
      position: fixed;
      left: 10px;
      top: 54px;
      z-index: 3;
      width: min(320px, 45vw);
      max-height: calc(100vh - 70px);
      overflow-y: auto;
      padding: 14px 16px;
      background: rgba(26, 26, 28, 0.96);
      border: 1px solid #444;
      border-radius: 10px;
      font-size: 12px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.6);
      transition: transform 0.3s ease, opacity 0.3s ease;
    }
    #wizard-panel.collapsed {
      transform: translateX(-350px);
      opacity: 0;
      pointer-events: none;
    }
    .wiz-subtitle {
      font-size: 11px;
      color: #999;
      margin-bottom: 12px;
      line-height: 1.35;
    }
    .wiz-progress {
      height: 4px;
      background: #252528;
      border-radius: 2px;
      margin-bottom: 14px;
      overflow: hidden;
    }
    .wiz-progress-bar {
      height: 100%;
      background: #fdcb6e;
      border-radius: 2px;
      width: 0%;
      transition: width 0.3s ease;
    }
    .wiz-question {
      font-size: 12px;
      font-weight: 500;
      color: #ddd;
      margin-bottom: 10px;
      line-height: 1.4;
    }
    .wiz-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      margin-bottom: 12px;
    }
    .wiz-card {
      background: #202022;
      border: 1px solid #3d3d40;
      border-radius: 8px;
      padding: 8px 6px;
      text-align: center;
      cursor: pointer;
      transition: background 0.2s, border-color 0.2s, transform 0.15s;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 3px;
    }
    .wiz-card:hover {
      background: #2a2a2e;
      border-color: #5a5a60;
    }
    .wiz-card.selected {
      background: rgba(253, 203, 110, 0.1);
      border-color: #fdcb6e;
    }
    .wiz-card .emoji {
      font-size: 16px;
    }
    .wiz-card .label {
      font-size: 10px;
      font-weight: 600;
      color: #eee;
    }
    .wiz-card .desc {
      font-size: 8px;
      color: #777;
      line-height: 1.2;
    }
    .wiz-card.full-width {
      grid-column: span 2;
    }
    .wiz-actions {
      display: flex;
      justify-content: space-between;
      gap: 8px;
      margin-top: 14px;
    }
    .wiz-btn {
      flex: 1;
      padding: 5px 10px;
      font-size: 11px;
      font-weight: 500;
      border-radius: 5px;
      cursor: pointer;
      background: #38383c;
      color: #ddd;
      border: 1px solid #555;
      transition: background 0.2s, border-color 0.2s;
    }
    .wiz-btn:hover {
      background: #48484e;
    }
    .wiz-btn.primary {
      background: #fdcb6e;
      color: #1a1a1c;
      border-color: #fdcb6e;
      font-weight: 600;
    }
    .wiz-btn.primary:hover {
      background: #ffeaa7;
    }
    .wiz-list {
      display: flex;
      flex-direction: column;
      gap: 5px;
      margin-bottom: 12px;
    }
    .wiz-list-item {
      background: #202022;
      border: 1px solid #333;
      border-radius: 6px;
      padding: 6px 8px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: space-between;
      transition: background 0.2s, border-color 0.2s;
    }
    .wiz-list-item:hover {
      background: #2a2a2e;
      border-color: #555;
    }
    .wiz-list-item.selected {
      background: rgba(253, 203, 110, 0.08);
      border-color: #fdcb6e;
    }
    .wiz-list-item .item-text {
      font-weight: 500;
      color: #eee;
      font-size: 11px;
    }
    .wiz-list-item .item-sub {
      font-size: 9px;
      color: #888;
    }
    .wiz-results {
      max-height: 180px;
      overflow-y: auto;
      border: 1px solid #333;
      border-radius: 6px;
      padding: 4px;
      background: #141416;
      margin-bottom: 12px;
    }
    .wiz-results-item {
      padding: 5px 6px;
      border-radius: 4px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 3px;
      transition: background 0.2s;
    }
    .wiz-results-item:hover {
      background: #222;
    }
    .wiz-results-item .term-name {
      font-weight: 600;
      color: #fdcb6e;
      font-size: 11px;
    }
    .wiz-results-item .term-category {
      font-size: 8px;
      color: #888;
      background: #1e1e20;
      padding: 2px 5px;
      border-radius: 3px;
    }
  </style>
</head>
<body>
  <div id="toolbar">
    <button type="button" id="zoom-in">Zoom +</button>
    <button type="button" id="zoom-out">Zoom −</button>
    <button type="button" id="reset-view">Reset view</button>
    <button type="button" id="wizard-toggle-btn" style="background:#fdcb6e;color:#1e1e1e;border-color:#fdcb6e;font-weight:600;display:inline-flex;align-items:center;gap:4px;">✨ Somatic Wizard</button>
    <span id="hint">Wheel zoom · drag background to pan · drag nodes · click a category chip to show/hide · filters →</span>
  </div>

  <div id="wizard-panel" class="collapsed">
    <div class="panel-head" style="display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:8px;">
      <h2 class="wiz-title" style="margin:0;font-size:14px;font-weight:600;color:#fdcb6e;display:flex;align-items:center;gap:5px;">✨ Somatic Wizard</h2>
      <button type="button" class="panel-toggle" id="wizard-close-btn" style="padding:3px 7px;font-size:10px;">Close</button>
    </div>
    <div class="wiz-subtitle">Track your somatic state and clarify your exact feelings.</div>
    <div class="wiz-progress">
      <div class="wiz-progress-bar" id="wiz-progress-bar"></div>
    </div>
    <div id="wiz-content"></div>
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
      applyHighlightsAndWizard();
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
    initWizard();

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

    // ----------------------------------------------------
    // UNIFIED HIGHLIGHT & WIZARD RENDERING MANAGER
    // ----------------------------------------------------
    function applyHighlightsAndWizard() {
      if (!nodeSel || nodeSel.empty()) return;

      const selectedNode = ui.selectedId !== null ? nodes[ui.selectedId] : null;

      // Case 1: Active selection on map takes precedence
      if (selectedNode) {
        highlightConnectionsFor(selectedNode);
        return;
      }

      // Case 2: Wizard is active
      if (wizardState.active) {
        if (wizardState.step === 4) {
          const contenders = new Set(getWizardContenders().map((d) => d.id));
          const hoveredId = wizardState.hoveredNodeId;

          nodeSel.each(function (d) {
            const isContender = contenders.has(d.id);
            const isHovered = d.id === hoveredId;
            const g = d3.select(this);
            
            g.select("circle")
              .style("opacity", isContender ? (hoveredId === null || isHovered ? 1.0 : 0.3) : 0.05)
              .attr("stroke", isHovered ? "#fdcb6e" : (isContender ? "#fdcb6e" : "#0d0d0d"))
              .attr("stroke-width", isHovered ? "3.5px" : (isContender ? "1.8px" : "1.2px"))
              .style("stroke-dasharray", (d.is_archetype && !isHovered) ? "3, 2.5" : "none");

            g.select("text")
              .style("opacity", isContender ? (hoveredId === null || isHovered ? 1.0 : 0.3) : 0.02)
              .style("font-weight", isHovered ? "bold" : "normal");
          });

          if (linkSel && !linkSel.empty()) {
            linkSel.style("opacity", (e) => {
              const s = typeof e.source === "object" ? e.source.id : e.source;
              const t = typeof e.target === "object" ? e.target.id : e.target;
              const sCont = contenders.has(s);
              const tCont = contenders.has(t);
              
              if (hoveredId !== null) {
                const sHov = s === hoveredId;
                const tHov = t === hoveredId;
                if ((sHov && tCont) || (tHov && sCont)) return e.isSemantic ? 1.0 : 0.4;
                return 0.01;
              }
              
              if (sCont && tCont) return e.isSemantic ? 0.8 : 0.2;
              return 0.01;
            });
          }
        } else {
          // Steps 1, 2, or 3
          nodeSel.each(function (d) {
            const isMatch = isNodeWizardMatch(d);
            const g = d3.select(this);

            g.select("circle")
              .style("opacity", isMatch ? 0.9 : 0.03)
              .attr("stroke", d.is_archetype ? "#fdcb6e" : "#0d0d0d")
              .attr("stroke-width", d.is_archetype ? "1.8px" : "1.2px")
              .style("stroke-dasharray", d.is_archetype ? "3, 2.5" : "none");

            g.select("text")
              .style("opacity", isMatch ? labelOpacity(d) * 1.2 : 0.01);
          });

          if (linkSel && !linkSel.empty()) {
            linkSel.style("opacity", (e) => {
              const s = typeof e.source === "object" ? e.source.id : e.source;
              const t = typeof e.target === "object" ? e.target.id : e.target;
              const sMatch = isNodeWizardMatch(nodes[s]);
              const tMatch = isNodeWizardMatch(nodes[t]);
              if (sMatch && tMatch) {
                return e.isSemantic ? 0.7 : 0.15;
              }
              return 0.01;
            });
          }
        }
        return;
      }

      // Case 3: Default (no active selection and no active wizard)
      nodeSel.each(function (d) {
        const g = d3.select(this);
        g.select("circle")
          .style("opacity", null)
          .attr("stroke", d.is_archetype ? "#fdcb6e" : "#0d0d0d")
          .attr("stroke-width", d.is_archetype ? "1.8px" : "1.2px")
          .style("stroke-dasharray", d.is_archetype ? "3, 2.5" : "none");
        g.select("text")
          .style("opacity", (d) => labelOpacity(d));
      });

      if (linkSel && !linkSel.empty()) {
        linkSel.style("opacity", null);
      }
    }

    function isNodeWizardMatch(d) {
      const ep = scorePleasantness(d.pleasantness);
      const ee = scoreEnergy(d.energy);
      const cat = d.category;
      const isSoft = String(d.intensity).toLowerCase().includes("soft");
      
      // Check Step 1
      if (wizardState.quadrant) {
        let quadMatch = false;
        if (wizardState.quadrant === 'TR' && ep > 0 && ee > 0 && cat === "Happiness, Contentment, and Joy") quadMatch = true;
        if (wizardState.quadrant === 'BR' && ep > 0 && ee <= 0 && (cat === "Peace and Solitude" || cat === "Social Connection")) quadMatch = true;
        if (wizardState.quadrant === 'TL' && ep < 0 && ee > 0 && (cat === "Fear and Panic" || cat === "Anxiety" || cat === "Anger, Apathy, and Hatred")) quadMatch = true;
        if (wizardState.quadrant === 'BL' && ep < 0 && ee <= 0 && (cat === "Sadness and Grief" || cat === "Depression and Suicidal Urges" || cat === "Shame and Guilt")) quadMatch = true;
        if (wizardState.quadrant === 'C' && (ep === 0 || isSoft || cat === "Confusion" || cat === "Nonspecific" || cat === "Avoidance")) quadMatch = true;
        if (!quadMatch) return false;
      }
      
      // Check Step 2
      if (wizardState.step >= 2 && wizardState.bodyArea) {
        let bodyMatch = false;
        if (wizardState.bodyArea === 'head' && (cat === "Confusion" || cat === "Anxiety" || cat === "Shame and Guilt")) bodyMatch = true;
        if (wizardState.bodyArea === 'throat' && (cat === "Sadness and Grief" || cat === "Social Connection")) bodyMatch = true;
        if (wizardState.bodyArea === 'chest' && (cat === "Social Connection" || cat === "Happiness, Contentment, and Joy" || cat === "Sadness and Grief" || cat === "Fear and Panic")) bodyMatch = true;
        if (wizardState.bodyArea === 'gut' && (cat === "Fear and Panic" || cat === "Jealousy and Envy" || cat === "Anger, Apathy, and Hatred")) bodyMatch = true;
        if (wizardState.bodyArea === 'limbs' && (cat === "Anger, Apathy, and Hatred" || cat === "Anxiety" || cat === "Depression and Suicidal Urges")) bodyMatch = true;
        if (wizardState.bodyArea === 'whole' && (cat === "Peace and Solitude" || cat === "Happiness, Contentment, and Joy" || cat === "Depression and Suicidal Urges")) bodyMatch = true;
        if (!bodyMatch) return false;
      }
      
      // Check Step 3
      if (wizardState.step >= 3 && wizardState.need) {
        let needMatch = false;
        if (wizardState.need === 'S' && (cat === "Fear and Panic" || cat === "Anxiety" || cat === "Peace and Solitude")) needMatch = true;
        if (wizardState.need === 'A' && (cat === "Anger, Apathy, and Hatred" || (cat === "Happiness, Contentment, and Joy" && d.term.toLowerCase() === "pride"))) needMatch = true;
        if (wizardState.need === 'P' && (cat === "Happiness, Contentment, and Joy" || cat === "Depression and Suicidal Urges")) needMatch = true;
        if (wizardState.need === 'I' && (cat === "Shame and Guilt" || cat === "Confusion" || d.term.toLowerCase() === "the self")) needMatch = true;
        if (wizardState.need === 'E' && (cat === "Jealousy and Envy" || cat === "Happiness, Contentment, and Joy")) needMatch = true;
        if (wizardState.need === 'N' && (cat === "Social Connection" || cat === "Sadness and Grief")) needMatch = true;
        if (!needMatch) return false;
      }
      
      return true;
    }

    function getWizardContenders() {
      const vis = filteredNodes();
      const scored = vis.map((d) => {
        return { node: d, score: calculateWizardScore(d) };
      });
      scored.sort((a, b) => b.score - a.score || a.node.term.localeCompare(b.node.term));
      return scored.slice(0, 8).map(x => x.node);
    }

    function calculateWizardScore(d) {
      let score = 0;
      
      // 1. Quadrant Score
      if (wizardState.quadrant) {
        const ep = scorePleasantness(d.pleasantness);
        const ee = scoreEnergy(d.energy);
        const cat = d.category;
        const isSoft = String(d.intensity).toLowerCase().includes("soft");
        
        let match = false;
        if (wizardState.quadrant === 'TR' && ep > 0 && ee > 0 && cat === "Happiness, Contentment, and Joy") match = true;
        if (wizardState.quadrant === 'BR' && ep > 0 && ee <= 0 && (cat === "Peace and Solitude" || cat === "Social Connection")) match = true;
        if (wizardState.quadrant === 'TL' && ep < 0 && ee > 0 && (cat === "Fear and Panic" || cat === "Anxiety" || cat === "Anger, Apathy, and Hatred")) match = true;
        if (wizardState.quadrant === 'BL' && ep < 0 && ee <= 0 && (cat === "Sadness and Grief" || cat === "Depression and Suicidal Urges" || cat === "Shame and Guilt")) match = true;
        if (wizardState.quadrant === 'C' && (ep === 0 || isSoft || cat === "Confusion" || cat === "Nonspecific" || cat === "Avoidance")) match = true;
        
        if (match) score += 5;
      }
      
      // 2. Somatic Score
      if (wizardState.bodyArea) {
        const cat = d.category;
        let match = false;
        if (wizardState.bodyArea === 'head' && (cat === "Confusion" || cat === "Anxiety" || cat === "Shame and Guilt")) match = true;
        if (wizardState.bodyArea === 'throat' && (cat === "Sadness and Grief" || cat === "Social Connection")) match = true;
        if (wizardState.bodyArea === 'chest' && (cat === "Social Connection" || cat === "Happiness, Contentment, and Joy" || cat === "Sadness and Grief" || cat === "Fear and Panic")) match = true;
        if (wizardState.bodyArea === 'gut' && (cat === "Fear and Panic" || cat === "Jealousy and Envy" || cat === "Anger, Apathy, and Hatred")) match = true;
        if (wizardState.bodyArea === 'limbs' && (cat === "Anger, Apathy, and Hatred" || cat === "Anxiety" || cat === "Depression and Suicidal Urges")) match = true;
        if (wizardState.bodyArea === 'whole' && (cat === "Peace and Solitude" || cat === "Happiness, Contentment, and Joy" || cat === "Depression and Suicidal Urges")) match = true;
        
        if (match) score += 3;
      }
      
      // 3. Need Score
      if (wizardState.need) {
        const cat = d.category;
        let match = false;
        if (wizardState.need === 'S' && (cat === "Fear and Panic" || cat === "Anxiety" || cat === "Peace and Solitude")) match = true;
        if (wizardState.need === 'A' && (cat === "Anger, Apathy, and Hatred" || (cat === "Happiness, Contentment, and Joy" && d.term.toLowerCase() === "pride"))) match = true;
        if (wizardState.need === 'P' && (cat === "Happiness, Contentment, and Joy" || cat === "Depression and Suicidal Urges")) match = true;
        if (wizardState.need === 'I' && (cat === "Shame and Guilt" || cat === "Confusion" || d.term.toLowerCase() === "the self")) match = true;
        if (wizardState.need === 'E' && (cat === "Jealousy and Envy" || cat === "Happiness, Contentment, and Joy")) match = true;
        if (wizardState.need === 'N' && (cat === "Social Connection" || cat === "Sadness and Grief")) match = true;
        
        if (match) score += 4;
      }
      
      return score;
    }

    // ----------------------------------------------------
    // BIO-SOMATIC GRANULARITY WIZARD STATE & LOGIC
    // ----------------------------------------------------
    const wizardState = {
      active: false,
      step: 1, // 1 to 4
      quadrant: null, // 'TR', 'BR', 'TL', 'BL', 'C'
      bodyArea: null, // 'head', 'throat', 'chest', 'gut', 'limbs', 'whole'
      need: null,     // 'S', 'A', 'P', 'I', 'E', 'N'
      hoveredNodeId: null
    };

    function initWizard() {
      // Toggle button click listener
      document.getElementById("wizard-toggle-btn").addEventListener("click", () => {
        const wp = document.getElementById("wizard-panel");
        const active = wp.classList.contains("collapsed");
        if (active) {
          wp.classList.remove("collapsed");
          wizardState.active = true;
          // When wizard starts, clear regular selection
          clearSelection();
          renderWizardStep();
        } else {
          closeWizard();
        }
      });

      document.getElementById("wizard-close-btn").addEventListener("click", () => {
        closeWizard();
      });
    }

    function closeWizard() {
      const wp = document.getElementById("wizard-panel");
      wp.classList.add("collapsed");
      wizardState.active = false;
      wizardState.step = 1;
      wizardState.quadrant = null;
      wizardState.bodyArea = null;
      wizardState.need = null;
      wizardState.hoveredNodeId = null;
      applyHighlightsAndWizard();
    }

    function renderWizardStep() {
      const container = document.getElementById("wiz-content");
      if (!container) return;

      container.innerHTML = "";

      // Update progress bar
      const bar = document.getElementById("wiz-progress-bar");
      const pct = ((wizardState.step - 1) / 3) * 100;
      bar.style.width = pct + "%";

      if (wizardState.step === 1) {
        // Step 1: Valence-Energy Quadrants
        const qDiv = document.createElement("div");
        qDiv.innerHTML = `
          <div class="wiz-question">1. How are you feeling physically and emotionally right now? Select the quadrant that matches your state:</div>
          <div class="wiz-grid">
            <div class="wiz-card" id="wiz-q-tr">
              <span class="emoji">🌟</span>
              <span class="label">Vibrant & Inspired</span>
              <span class="desc">High Energy • Pleasant</span>
            </div>
            <div class="wiz-card" id="wiz-q-br">
              <span class="emoji">🌸</span>
              <span class="label">Serene & Grounded</span>
              <span class="desc">Low Energy • Pleasant</span>
            </div>
            <div class="wiz-card" id="wiz-q-tl">
              <span class="emoji">⚡</span>
              <span class="label">Tense & Reactive</span>
              <span class="desc">High Energy • Unpleasant</span>
            </div>
            <div class="wiz-card" id="wiz-q-bl">
              <span class="emoji">🌊</span>
              <span class="label">Heavy & Weary</span>
              <span class="desc">Low Energy • Unpleasant</span>
            </div>
            <div class="wiz-card full-width" id="wiz-q-c">
              <span class="emoji">🧘</span>
              <span class="label">Quiet, Reflective, or Transitional</span>
              <span class="desc">Neutral / Calm / Mindful State</span>
            </div>
          </div>
        `;
        container.appendChild(qDiv);

        // Bind clicks
        const map = { TR: 'wiz-q-tr', BR: 'wiz-q-br', TL: 'wiz-q-tl', BL: 'wiz-q-bl', C: 'wiz-q-c' };
        Object.entries(map).forEach(([q, id]) => {
          document.getElementById(id).addEventListener("click", () => {
            wizardState.quadrant = q;
            wizardState.step = 2;
            renderWizardStep();
            applyHighlightsAndWizard();
          });
        });
      }
      else if (wizardState.step === 2) {
        // Step 2: Body Tension Location
        const qDiv = document.createElement("div");
        qDiv.innerHTML = `
          <div class="wiz-question">2. Notice any physical tightness, tingling, or energy. Where in your body is this feeling most active?</div>
          <div class="wiz-list">
            <div class="wiz-list-item" id="wiz-b-head">
              <span class="item-text">🧠 Head, Face, or Jaw</span>
              <span class="item-sub">Racing mind • Clenched jaw • Blushing</span>
            </div>
            <div class="wiz-list-item" id="wiz-b-throat">
              <span class="item-text">🗣️ Throat or Neck</span>
              <span class="item-sub">Choked up • Difficulty speaking • Stiffness</span>
            </div>
            <div class="wiz-list-item" id="wiz-b-chest">
              <span class="item-text">🫁 Chest or Heart</span>
              <span class="item-sub">Tightness • Racing pulse • Warm expansion</span>
            </div>
            <div class="wiz-list-item" id="wiz-b-gut">
              <span class="item-text">🌀 Stomach or Gut</span>
              <span class="item-sub">Butterflies • Twisting knot • Sinking feeling</span>
            </div>
            <div class="wiz-list-item" id="wiz-b-limbs">
              <span class="item-text">👤 Shoulders, Arms, or Hands</span>
              <span class="item-sub">Heavy shoulders • Clenched fists • Defensive weight</span>
            </div>
            <div class="wiz-list-item" id="wiz-b-whole">
              <span class="item-text">🌊 Whole Body / Systemic</span>
              <span class="item-sub">Buzzing excitement • Systemic fatigue • Peaceful calm</span>
            </div>
          </div>
          <div class="wiz-actions">
            <button type="button" class="wiz-btn" id="wiz-back">Back</button>
          </div>
        `;
        container.appendChild(qDiv);

        // Bind clicks
        const map = { head: 'wiz-b-head', throat: 'wiz-b-throat', chest: 'wiz-b-chest', gut: 'wiz-b-gut', limbs: 'wiz-b-limbs', whole: 'wiz-b-whole' };
        Object.entries(map).forEach(([b, id]) => {
          document.getElementById(id).addEventListener("click", () => {
            wizardState.bodyArea = b;
            wizardState.step = 3;
            renderWizardStep();
            applyHighlightsAndWizard();
          });
        });

        document.getElementById("wiz-back").addEventListener("click", () => {
          wizardState.step = 1;
          wizardState.quadrant = null;
          renderWizardStep();
          applyHighlightsAndWizard();
        });
      }
      else if (wizardState.step === 3) {
        // Step 3: S.A.P.I.E.N. Needs model
        const qDiv = document.createElement("div");
        qDiv.innerHTML = `
          <div class="wiz-question">3. All feelings are indicators of needs. Which of your fundamental human needs is speaking loudest right now?</div>
          <div class="wiz-list">
            <div class="wiz-list-item" id="wiz-n-s">
              <span class="item-text">🛡️ Safety & Security</span>
              <span class="item-sub">Protection • Predictability • Physical safety</span>
            </div>
            <div class="wiz-list-item" id="wiz-n-a">
              <span class="item-text">🔓 Autonomy & Agency</span>
              <span class="item-sub">Choice • Free independence • Self-expression</span>
            </div>
            <div class="wiz-list-item" id="wiz-n-p">
              <span class="item-text">🎯 Purpose & Meaning</span>
              <span class="item-sub">Contribution • Curious learning • Creative progress</span>
            </div>
            <div class="wiz-list-item" id="wiz-n-i">
              <span class="item-text">🎭 Identity & Authenticity</span>
              <span class="item-sub">Self-worth • Alignment with values • Being real</span>
            </div>
            <div class="wiz-list-item" id="wiz-n-e">
              <span class="item-text">💎 Esteem & Status</span>
              <span class="item-sub">Mutual respect • Social standing • Accomplishment</span>
            </div>
            <div class="wiz-list-item" id="wiz-n-n">
              <span class="item-text">🤝 Nurture & Connection</span>
              <span class="item-sub">Intimate belonging • Care • Warm community</span>
            </div>
          </div>
          <div class="wiz-actions">
            <button type="button" class="wiz-btn" id="wiz-back">Back</button>
          </div>
        `;
        container.appendChild(qDiv);

        // Bind clicks
        const map = { S: 'wiz-n-s', A: 'wiz-n-a', P: 'wiz-n-p', I: 'wiz-n-i', E: 'wiz-n-e', N: 'wiz-n-n' };
        Object.entries(map).forEach(([n, id]) => {
          document.getElementById(id).addEventListener("click", () => {
            wizardState.need = n;
            wizardState.step = 4;
            renderWizardStep();
            applyHighlightsAndWizard();
          });
        });

        document.getElementById("wiz-back").addEventListener("click", () => {
          wizardState.step = 2;
          wizardState.bodyArea = null;
          renderWizardStep();
          applyHighlightsAndWizard();
        });
      }
      else if (wizardState.step === 4) {
        // Step 4: Constellation Reveal
        const contenders = getWizardContenders();

        const qDiv = document.createElement("div");
        qDiv.innerHTML = `
          <div class="wiz-question" style="margin-bottom:6px;">4. We found a matching emotional constellation! Hover to track, click to log:</div>
          <div class="wiz-results" id="wiz-res-list"></div>
          <div class="wiz-actions">
            <button type="button" class="wiz-btn primary" id="wiz-reset">Reset Wizard</button>
            <button type="button" class="wiz-btn" id="wiz-back">Back</button>
          </div>
        `;
        container.appendChild(qDiv);

        const listDiv = document.getElementById("wiz-res-list");
        if (contenders.length === 0) {
          listDiv.innerHTML = '<div style="color:#777;padding:10px;text-align:center;">No matching entries in the active filtered view. Change min/max radius or category checkboxes, or reset the wizard.</div>';
        } else {
          contenders.forEach((n) => {
            const item = document.createElement("div");
            item.className = "wiz-results-item";
            item.innerHTML = `
              <span class="term-name">${escapeHtml(n.term)}</span>
              <span class="term-category">${escapeHtml(n.category.split(',')[0].trim())}</span>
            `;

            // Hover effects on map
            item.addEventListener("mouseenter", () => {
              wizardState.hoveredNodeId = n.id;
              applyHighlightsAndWizard();
            });
            item.addEventListener("mouseleave", () => {
              wizardState.hoveredNodeId = null;
              applyHighlightsAndWizard();
            });

            // Click log & select node
            item.addEventListener("click", () => {
              selectNode(n);
              console.log(`[Biofeedback Log] Emotion Named: "${n.term}" | Somatic Area: "${wizardState.bodyArea}" | Core Need: "${wizardState.need}"`);
            });

            listDiv.appendChild(item);
          });
        }

        document.getElementById("wiz-reset").addEventListener("click", () => {
          wizardState.step = 1;
          wizardState.quadrant = null;
          wizardState.bodyArea = null;
          wizardState.need = null;
          wizardState.hoveredNodeId = null;
          renderWizardStep();
          applyHighlightsAndWizard();
        });

        document.getElementById("wiz-back").addEventListener("click", () => {
          wizardState.step = 3;
          wizardState.need = null;
          renderWizardStep();
          applyHighlightsAndWizard();
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
      applyHighlightsAndWizard();
      centerCameraOnNode(nodeObj);
    }

    function clearSelection() {
      ui.selectedId = null;
      applyHighlightsAndWizard();
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
