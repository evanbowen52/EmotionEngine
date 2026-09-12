# 🌀 Emotion Engine: Polar Map Explorer

Welcome to the **Emotion Engine Polar Map Explorer**—an interactive, highly detailed emotional vocabulary and relationship engine. It arranges emotional states radially across polar coordinates by **pleasantness** (polar angle) and **intensity/energy** (radial distance), clustering related concepts into color-coded semantic sectors.

This project merges traditional psychology vocabulary, Brené Brown's *Atlas of the Heart* research, and Tim Lomas's *Positive Lexicography Project* into a single, cohesive interactive map.

---

## 🗺️ Architectural Structure & File Interactions

The application is structured for high portable efficiency, compiling a massive, rich dataset of **1,874 emotional terms** directly into a single, zero-dependency standalone HTML file.

```
                  ┌──────────────────────────────┐
                  │        emotions.json         │ (Single Source of Truth)
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │      build_polar_map.py      │ (Python Template Compiler)
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │    emotion-polar-map.html    │ (Standalone Interactive App)
                  └──────────────────────────────┘
```

### 1. Active Runtime Files (Production Stack)
* **`emotions.json` (Single Source of Truth):** 
  The global taxonomy of 1,874 emotional states. Each emotion is stored as an object containing its name (`term`), language of `origin`, radial coordinate data (`intensity`, `energy`, `pleasantness`), `description`, and custom semantic `connections`.
* **`build_polar_map.py` (The Compiler):** 
  A Python utility that reads `emotions.json`, escapes and NFC-normalizes the strings, embeds the entire JSON blob into an inline `<script>` tag, and writes out `emotion-polar-map.html`.
* **`emotion-polar-map.html` (Interactive Client):** 
  The single standalone web interface. It runs entirely on the client side, loads D3.js via CDN, and simulates forces locally. It can be double-clicked and run in any browser offline.

---

## 🎨 Visual Dictionary: What Do the Nodes and Lines Mean?

There are distinct visual families of nodes and lines rendered on the map.

### A. Constellation Nodes (Jungian Archetypes & Deities)
* **Visual Style:** Glowing, dashed gold outer rings (`#fdcb6e`, dash pattern: `3, 2.5`).
* **Behavior:** Applied to core Jungian psychic structures (*The Self*, *The Shadow*, *Anima/Animus*, *Persona*) and mythological archetypes from world cultures (*Poseidon*, *Apollo*, *Dionysus*, *Hades*, etc.) whose descriptions have been enriched with depth-psychological insights.
* **Purpose:** Acts as rare, luminous "celestial constellations" on the polar wheel, allowing users to instantly track the deeper psychological blueprints underpinning our emotional spectrum. When selected, their dashed rings seamlessly transition into solid, bright focus highlights.

### B. Standard Nodes
* **Visual Style:** Solid, color-coded circles matching their respective emotional sector (e.g. orange for Anxiety, purple for Sadness and Grief).

### C. Structural Mesh Lines (Intra-Category Cluster Edges)
* **Visual Style:** Thin, dark grey, solid lines (`#444` at 35% opacity).
* **Behavior:** Generated automatically in the client via `buildCategoryLinks()`. It sorts emotions in each category by angle and radius and connects them to their nearest 1st and 2nd neighbors.
* **Purpose:** Purely geometric cluster forces. These lines act as an organic "skeleton" within the D3 simulation, forcing nodes in the same category to stick together as clean, tight, wedge-shaped clusters. **These do not represent real emotional relationships.**

### D. Semantic Relationship Lines (Emotional Connections)
* **Visual Style:** Bright, thick (`2px`), highly interactive colored lines that cut across categories or radial tiers.
* **Behavior:** Read directly from the `connections` array in `emotions.json` and styled dynamically based on the `relation` type.
* **Line Style Dictionary:**
  1. **Confused With (`confused_with`):** **Dashed Orange/Coral lines** (`#e17055`, `4px dash, 3px gap`). Represents emotions that are commonly conflated but have key cognitive differences.
     * *Example:* **Anxious** (future-focused) ⇄ **Afraid** (present-focused).
  2. **Triggered By (`triggered_by`):** **Dashed Blue lines** (`#0984e3`, `6px dash, 2px gap`).
     * *Example:* **Jealous** is triggered by **Threatened**.
  3. **Triggers (`triggers`):** **Solid Blue lines** (`#0984e3`). Shows direct triggering pathways.
     * *Example:* **Threatened** triggers **Jealous**.
  4. **Adjacent (`adjacent`):** **Solid Turquoise/Cyan lines** (`#00cec9`). Shows close cousin-states with high psychological affinity.
     * *Example:* **Worried** is adjacent to **Anxious**.
  5. **Leads To (`leads_to`):** **Solid Purple/Lavender lines** (`#9b59b6`). Signifies a progressive emotional flow or transition.
     * *Example:* **Envious** leads to **Resentful**, or **Stress** leads to **Overwhelmed**.
  6. **Opposite Of (`opposite_of`):** **Dashed Gold/Yellow lines** (`#fdcb6e`, `4px dash, 4px gap`). Signifies a profound tension, conflict, or direct counter-state.
     * *Example:* **Belonging** ⇄ **Fitting In**, or **Freudenfreude** ⇄ **Schadenfreude**.

---

## ⚙️ Interactive Features & UX Modes

* **English Terms Only Toggle:** 
  Checking the **"English terms only"** checkbox in the sidebar hides the 1,400+ foreign, untranslatable, and coined terms. The remaining English nodes smoothly float together to form a highly familiar, standard **English Emotion Wheel**. Toggling it off expands the map into an international philosophical landscape.
* **Click Highlight (Spotlight):** 
  Clicking any node dims the rest of the map to `15%` opacity, highlights the selected node in gold, highlights all its semantic neighbors in light-grey at `100%` opacity, and populates interactive, color-coded connection chips in the sidebar for quick traversal.
* **Orbit Tour Spotlight:** 
  The "Orbit" control in the sidebar acts as a slideshow tour. It sweeps a celestial spotlight from node to node in polar angular order, allowing users to sit back and savor the definitions in a structured cycle.

---

## 🛠️ Auxiliary & Administrative Scripts (Maintenance Ledger)

These Python and JS scripts are auxiliary utilities used to populate, normalize, and manage the database. They are **not** needed to run the interactive map, but are kept to maintain the pipeline:

* **`expand_emotion_dataset.py`:** 
  The master ingestion pipeline script. It merges custom *Atlas of the Heart* pairs and compiles/spins up a temporary Node.js fetch child-process to parse and translate 1,420 words from the Positive Lexicography Project.
* **`enrich_archetypes.py`:** 
  Integrates core Jungian analytical psychology archetypes (*The Self*, *The Shadow*, etc.) and enriches existing mythological deities with depth-psychological insights.
* **`append_untranslatable_words.py`:** 
  An older script that appends manual listicle/Dictionary of Obscure Sorrows untranslatable concepts. (Superceded by `expand_emotion_dataset.py` but kept for archival references).
* **`_fill_definitions.py`:** 
  An automated utility that connects to WordNet and online dictionary APIs to sync missing descriptions or definitions.
* **`normalize_emotions.py`:** 
  Ensures all records adhere to the global sector name taxonomy (e.g. mapping "Social Comparison" ➔ "Jealousy and Envy").
* **`fix_anxiety_categories.py`:** 
  Utility script that moves specific DEI-aligned vocabulary words into the Anxiety category.
* **`update_untranslatable.py`:** 
  Re-maps internal categories inside appending scripts to match category modifications.

