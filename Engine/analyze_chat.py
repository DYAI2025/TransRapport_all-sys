#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze chat with marker schemas -> scores, donuts, tables, HTML report.
Strictly rule-based: only uses patterns/sets/weights defined in your bundles (+ optional extra YAMLs).
Charts: matplotlib (single-plot per chart), with explicit colors (requested by user).
"""

import argparse, base64, io, json, math, os, re, sys, textwrap, zipfile
from datetime import datetime
from pathlib import Path
from collections import defaultdict, Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import yaml

# Import Absence Detection Module
from DETECT_absence_meta import integrate_absence_detection

# -------------------------
# Paths & defaults
# -------------------------
DEFAULT_ZIP_SCHEMA = Path("/mnt/data/ALL_SCH.SCR_,CAL.zip")
DEFAULT_ZIP_MARKERS = Path("/mnt/data/FIXED_Marker_4.0.zip")
DEFAULT_ZIP_DETECTORS = Path("/mnt/data/ALL_DETECTORS.zip")  # optional

# Extra configs delivered below in this message (copy as files next to this script)
THEMES_MAP_PATH = Path("themes_map.yaml")
ACTIONS_MAP_PATH = Path("balancing_actions.yaml")
EXTRA_MARKERS_PATH = Path("extra_markers.yaml")
REPORT_TEMPLATE_PATH = Path("report_template.html")
ABSENCE_CONFIG_PATH = Path("absence_meta_config.yaml")

# Color palette (explicitly colorful as requested)
PALETTE = [
    "#5B8FF9", "#5AD8A6", "#5D7092", "#F6BD16", "#E8684A",
    "#6DC8EC", "#9270CA", "#FF9D4D", "#269A99", "#FF99C3"
]
BAR_POS = "#5B8FF9"
BAR_NEG = "#E8684A"
BAR_NEU = "#5D7092"

# -------------------------
# Robust ZIP loader helpers
# -------------------------
def _zip_namelist(zp: Path):
    if not zp.exists():
        return []
    with zipfile.ZipFile(zp, "r") as z:
        return z.namelist()

def read_text_from_zip(zp: Path, name_contains: str, fallback_exact: str = None, encoding="utf-8"):
    """Read the first file in zip that contains substring; fallback to exact name if given."""
    if not zp.exists():
        return None
    with zipfile.ZipFile(zp, "r") as z:
        target = None
        for n in z.namelist():
            if name_contains in n and not n.endswith("/"):
                target = n; break
        if not target and fallback_exact and fallback_exact in z.namelist():
            target = fallback_exact
        if not target:
            return None
        data = z.read(target)
    try:
        return data.decode(encoding, errors="ignore")
    except Exception:
        return data.decode("utf-8", errors="ignore")

def read_all_yaml_from_zip(zp: Path):
    out = []
    if not zp.exists():
        return out
    with zipfile.ZipFile(zp, "r") as z:
        for n in z.namelist():
            if n.lower().endswith((".yml", ".yaml")) and not n.endswith("/"):
                try:
                    obj = yaml.safe_load(z.read(n))
                    if obj:
                        out.append(obj)
                except Exception:
                    pass
    return out

def read_all_json_from_zip(zp: Path):
    out = {}
    if not zp.exists():
        return out
    with zipfile.ZipFile(zp, "r") as z:
        for n in z.namelist():
            if n.lower().endswith(".json") and not n.endswith("/"):
                try:
                    txt = z.read(n).decode("utf-8", errors="ignore")
                    obj = json.loads(txt)
                    out[n] = obj
                except Exception:
                    pass
    return out

# -------------------------
# Resource loading
# -------------------------
class Resources:
    def __init__(self, zip_schema: Path, zip_markers: Path, zip_detectors: Path,
                 themes_map: Path, actions_map: Path, extra_markers: Path, absence_config: Path):
        self.zip_schema = zip_schema
        self.zip_markers = zip_markers
        self.zip_detectors = zip_detectors
        self.themes_map = self._load_yaml(themes_map) or {}
        self.actions_map = self._load_yaml(actions_map) or {}
        self.extra_markers = self._load_yaml(extra_markers) or []
        self.absence_config = self._load_yaml(absence_config) or {}

        # Try to load canonical files from schema zip
        self.schema_bundle = self._load_schema_bundle()
        self.sets_cfg = self._load_sets_cfg()
        self.weights = self._load_weights()

        # Build regex marker registry from: schema bundle groups + markers zip + extras
        self.regex_markers = self._build_regex_registry()

        # Map: marker_id -> primary axis/category (best-effort, uses schema metrics.primaryOrder + descriptions/tags)
        self.primary_axes = self._extract_primary_axes()
        self.marker_to_primary = self._map_marker_to_primary()

        # E/D sets (fallback-safe)
        self.E_SET, self.D_SET = self._extract_ED_sets()

        # Optional: human labels for markers (from YAML 'frame.*')
        self.marker_labels = self._build_marker_labels()

        # Optional: narratives/categories for theme resonance
        self.marker_to_narr = self._map_marker_to_narrative()

        # Build complete marker registry for absence detection
        self.complete_marker_registry = self._build_complete_marker_registry()

    def _load_yaml(self, p: Path):
        if not p or not p.exists():
            return None
        with open(p, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _load_schema_bundle(self):
        # Prefer an obvious file
        txt = read_text_from_zip(self.zip_schema, "schema_full_bundle.json", fallback_exact="schema_full_bundle.json")
        if txt:
            try:
                return json.loads(txt)
            except Exception:
                pass
        # Fallback: pick the largest json in schema zip
        allj = read_all_json_from_zip(self.zip_schema)
        if allj:
            # choose by size
            name = max(allj.keys(), key=lambda n: len(json.dumps(allj[n])))
            return allj[name]
        return {"ATO": [], "SEM": [], "CLU": [], "MEMA": [], "metrics": {"primaryOrder": []}}

    def _load_sets_cfg(self):
        txt = read_text_from_zip(self.zip_schema, "sets_config.json", fallback_exact="sets_config.json")
        if txt:
            try: return json.loads(txt)
            except Exception: pass
        return {"E": [], "D": []}

    def _load_weights(self):
        txt = read_text_from_zip(self.zip_schema, "weights.json", fallback_exact="weights.json")
        if txt:
            try: return json.loads(txt)
            except Exception: pass
        return {"marker_weights": {}, "models": {}}

    def _build_regex_registry(self):
        reg = {}
        # 1) From schema bundle groups (pattern field)
        for group in ["ATO","SEM","CLU","MEMA","EMO","ACT"]:
            for e in self.schema_bundle.get(group, []) or []:
                mid = e.get("id")
                pat = e.get("pattern")
                if mid and pat:
                    try: reg[mid] = re.compile(pat, re.IGNORECASE)
                    except re.error: pass
        # 2) From markers zip YAML files (pattern field)
        for y in read_all_yaml_from_zip(self.zip_markers):
            mid = y.get("id")
            pat = y.get("pattern") or (y.get("frame", {}) if isinstance(y.get("frame"), str) else None)
            if mid and isinstance(pat, str):
                try: reg[mid] = re.compile(pat, re.IGNORECASE)
                except re.error: pass
        # 3) From extra markers (provided below)
        for y in self.extra_markers:
            mid = y.get("id"); pat = y.get("pattern")
            if mid and pat:
                try: reg[mid] = re.compile(pat, re.IGNORECASE)
                except re.error: pass
        return reg

    def _extract_primary_axes(self):
        axes = []
        try:
            axes = list(self.schema_bundle.get("metrics", {}).get("primaryOrder", []))
        except Exception:
            axes = []
        return axes

    def _map_marker_to_primary(self):
        """Best-effort mapping: explicit in schema descriptions, else tag heuristics."""
        m = {}
        axes = self.primary_axes
        if not axes:
            return m
        # From schema bundle description/tags
        for group in ["ATO","SEM","CLU","MEMA","EMO","ACT"]:
            for e in self.schema_bundle.get(group, []) or []:
                mid = e.get("id"); desc = (e.get("description") or "") + " " + " ".join(e.get("tags") or [])
                if not mid: continue
                for ax in axes:
                    if re.search(rf"\b{re.escape(ax)}\b", desc, flags=re.IGNORECASE):
                        m[mid] = ax; break
        # From extra markers tags
        for y in self.extra_markers:
            mid = y.get("id"); tags = " ".join(y.get("tags") or [])
            if not mid: continue
            for ax in axes:
                if re.search(rf"\b{re.escape(ax)}\b", tags, flags=re.IGNORECASE):
                    m[mid] = ax; break
        return m

    def _extract_ED_sets(self):
        e = set(self.sets_cfg.get("E", []) or [])
        d = set(self.sets_cfg.get("D", []) or [])
        # Fallback heuristic: tags containing "escalation"/"deescalation"
        if not e or not d:
            for group in ["ATO","SEM","CLU","MEMA","EMO","ACT"]:
                for x in self.schema_bundle.get(group, []) or []:
                    mid = x.get("id"); tags = [t.lower() for t in (x.get("tags") or [])]
                    if not mid: continue
                    if any("escal" in t for t in tags): e.add(mid)
                    if any("deescal" in t or "de-esk" in t or "deesk" in t for t in tags): d.add(mid)
        return e, d

    def _build_marker_labels(self):
        lab = {}
        def add(mid, label):
            if mid and label and mid not in lab:
                lab[mid] = label
        for group in ["ATO","SEM","CLU","MEMA","EMO","ACT"]:
            for e in self.schema_bundle.get(group, []) or []:
                mid = e.get("id")
                frame = e.get("frame") or {}
                sig = frame.get("signal") if isinstance(frame, dict) else None
                concept = frame.get("concept") if isinstance(frame, dict) else None
                label = concept or (sig[0] if isinstance(sig, list) and sig else None) or e.get("id")
                add(mid, label)
        for y in self.extra_markers:
            add(y.get("id"), (y.get("frame", {}) or {}).get("concept") or y.get("id"))
        return lab

    def _map_marker_to_narrative(self):
        m = {}
        for group in ["ATO","SEM","CLU","MEMA","EMO","ACT"]:
            for e in self.schema_bundle.get(group, []) or []:
                mid = e.get("id")
                frame = e.get("frame") or {}
                narr = frame.get("narrative") if isinstance(frame, dict) else None
                if mid and narr:
                    m[mid] = narr
        for y in self.extra_markers:
            mid = y.get("id")
            narr = (y.get("frame", {}) or {}).get("narrative")
            if mid and narr:
                m[mid] = narr
        return m

    def _build_complete_marker_registry(self):
        """Erstelle komplette Marker-Registry für Absence-Detection"""
        registry = []
        
        # Aus schema bundle
        for group in ["ATO","SEM","CLU","MEMA","EMO","ACT"]:
            for e in self.schema_bundle.get(group, []) or []:
                if e.get("id"):
                    registry.append(e)
        
        # Aus markers zip YAMLs
        for y in read_all_yaml_from_zip(self.zip_markers):
            if y.get("id"):
                registry.append(y)
        
        # Aus extra markers
        for y in self.extra_markers:
            if y.get("id"):
                registry.append(y)
        
        return registry

# -------------------------
# Core analysis
# -------------------------
def chunk_messages(text: str):
    """Very simple: 'Name: message' or lines -> messages with 'Unknown' speaker."""
    msgs = []
    for i, line in enumerate([l.strip() for l in text.splitlines() if l.strip()]):
        m = re.match(r"^([^:]{1,40}):\s*(.+)$", line)
        if m:
            spk, msg = m.group(1), m.group(2)
        else:
            spk, msg = "Unknown", line
        msgs.append({"i": i, "speaker": spk, "text": msg})
    return msgs

def match_markers(msgs, regex_markers):
    """Return list of hits: {i, speaker, marker}"""
    hits = []
    for m in msgs:
        txt = m["text"]
        for mid, creg in regex_markers.items():
            try:
                if creg.search(txt):
                    hits.append({"i": m["i"], "speaker": m["speaker"], "marker": mid})
            except Exception:
                pass
    return hits

def rolling_windows(n, win):
    i = 0
    while i < n:
        j = min(n, i+win)
        yield i, j
        i += win

def compute_primary_counts(hits, marker_to_primary):
    prim = Counter()
    for h in hits:
        ax = marker_to_primary.get(h["marker"])
        if ax:
            prim[ax] += 1
    return prim

def weighted_sum(hits, weights):
    w = weights.get("marker_weights", {}) if isinstance(weights, dict) else {}
    s = 0.0
    for h in hits:
        s += float(w.get(h["marker"], 1.0))
    return s

def ed_counts(hits, E_SET, D_SET):
    E = sum(1 for h in hits if h["marker"] in E_SET)
    D = sum(1 for h in hits if h["marker"] in D_SET)
    return E, D

def hits_by_speaker(hits):
    per = defaultdict(list)
    for h in hits:
        per[h["speaker"]].append(h)
    return per

def theme_resonance(hits, R: Resources):
    """Compute resonance across:
       - narratives (frame.narrative)
       - primary axes
       -> merge via THEMES_MAP for human-readable names
    """
    # raw tallies
    narr = Counter()
    prim = Counter()
    for h in hits:
        mid = h["marker"]
        if mid in R.marker_to_narr:
            narr[R.marker_to_narr[mid]] += 1
        ax = R.marker_to_primary.get(mid)
        if ax:
            prim[ax] += 1

    # normalized scores
    total = sum(narr.values()) + sum(prim.values()) or 1
    narr_score = {k: v/total for k,v in narr.items()}
    prim_score = {k: v/total for k,v in prim.items()}

    # combine using themes_map rule (weights)
    themes_cfg = R.themes_map.get("themes", {})
    theme_scores = {}
    for theme_key, cfg in themes_cfg.items():
        score = 0.0
        for na, w in (cfg.get("narratives") or {}).items():
            score += w * narr_score.get(na, 0.0)
        for ax, w in (cfg.get("primary_axes") or {}).items():
            score += w * prim_score.get(ax, 0.0)
        theme_scores[theme_key] = score

    # pick best theme
    if theme_scores:
        best_key = max(theme_scores, key=lambda k: theme_scores[k])
        best_label = themes_cfg.get(best_key, {}).get("label", best_key)
        return {"theme_key": best_key, "theme_label": best_label,
                "theme_scores": theme_scores, "narr_score": narr_score, "prim_score": prim_score}
    else:
        # Fallback: highest primary axis as theme
        if prim:
            best_ax, _ = prim.most_common(1)[0]
            return {"theme_key": best_ax, "theme_label": best_ax,
                    "theme_scores": {best_ax: 1.0}, "narr_score": narr_score, "prim_score": prim_score}
        return {"theme_key":"Unbestimmt","theme_label":"Unbestimmt",
                "theme_scores":{}, "narr_score": narr_score, "prim_score": prim_score}

def build_objective_tips(per_speaker_hits, R: Resources):
    """
    Objective suggestions: for each speaker we look at top E markers they trigger
    and propose balancing markers (D/Transparency etc.) using ACTIONS_MAP.
    No free semantics, only marker IDs -> labels.
    """
    tips = {}
    act = R.actions_map or {}
    balance_table = act.get("balance", {})
    for spk, hits in per_speaker_hits.items():
        cnt = Counter([h["marker"] for h in hits])
        # Top-3 escalation markers of this speaker
        top_e = [mid for mid, c in cnt.most_common() if mid in R.E_SET][:3]
        suggestions = []
        for mid in top_e:
            # candidates
            cand = balance_table.get(mid) or []
            # If no explicit mapping, suggest generic D markers with highest weights
            if not cand:
                d_weighted = sorted([(m, float(R.weights.get("marker_weights", {}).get(m, 1.0)))
                                    for m in R.D_SET],
                                    key=lambda x: -x[1])[:3]
                cand = [m for m,_ in d_weighted]
            suggestions.append({
                "problem_marker": mid,
                "problem_label": R.marker_labels.get(mid, mid),
                "suggest_markers": cand,
                "suggest_labels": [R.marker_labels.get(m, m) for m in cand]
            })
        tips[spk] = suggestions
    return tips

# -------------------------
# Charts (one plot per chart, with colors)
# -------------------------
def _fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("ascii")

def chart_donut(counts: dict, title: str):
    if not counts:
        return None
    labels = list(counts.keys())
    sizes = list(counts.values())
    fig, ax = plt.subplots()
    cols = (PALETTE * ((len(labels)//len(PALETTE))+1))[:len(labels)]
    wedges, _ = ax.pie(sizes, labels=labels, wedgeprops=dict(width=0.4), colors=cols, startangle=90)
    ax.set_title(title)
    return _fig_to_base64(fig)

def chart_bar_compare(rows, title: str):
    """rows: list of (label, value)"""
    if not rows: return None
    labels = [r[0] for r in rows]; values = [r[1] for r in rows]
    fig, ax = plt.subplots()
    ax.bar(labels, values, color=PALETTE[0:len(labels)])
    ax.set_title(title); ax.set_ylabel("Count")
    ax.set_xticklabels(labels, rotation=20, ha="right")
    return _fig_to_base64(fig)

def chart_ed_bars(E, D, title="E vs D (gesamt)"):
    fig, ax = plt.subplots()
    ax.bar(["Eskalation (E)"], [E], color=BAR_NEG)
    ax.bar(["Deeskalation (D)"], [D], color=BAR_POS)
    ax.set_title(title)
    ax.set_ylabel("Treffer")
    return _fig_to_base64(fig)

def chart_timeseries_ed(msgs, hits, E_SET, D_SET, window=20, title="E/D über Zeit (rollierend)"):
    """Simple block windows (non-overlapping) to keep it transparent and fast."""
    n = len(msgs); if n == 0: return None
    xs, e_vals, d_vals = [], [], []
    for i,j in rolling_windows(n, max(1, window)):
        xs.append(f"{i}-{j-1}")
        seg = [h for h in hits if i <= h["i"] < j]
        e = sum(1 for h in seg if h["marker"] in E_SET)
        d = sum(1 for h in seg if h["marker"] in D_SET)
        e_vals.append(e); d_vals.append(d)
    fig, ax = plt.subplots()
    ax.plot(xs, e_vals, marker="o", label="E", color=BAR_NEG)
    ax.plot(xs, d_vals, marker="o", label="D", color=BAR_POS)
    ax.set_title(title); ax.set_xlabel("Nachrichten-Fenster"); ax.set_ylabel("Treffer")
    ax.legend()
    return _fig_to_base64(fig)

def chart_theme_resonance(theme_scores: dict, title="Themen-Resonanz (gesamt)"):
    if not theme_scores: return None
    items = sorted(theme_scores.items(), key=lambda kv: -kv[1])[:8]
    labels = [R if isinstance(R, str) else str(R) for R,_ in items]
    values = [v for _,v in items]
    fig, ax = plt.subplots()
    ax.bar(labels, values, color=PALETTE[:len(labels)])
    ax.set_title(title); ax.set_ylabel("Score (normiert)")
    ax.set_xticklabels(labels, rotation=20, ha="right")
    return _fig_to_base64(fig)

def chart_top_markers_per_speaker(per_speaker_hits, marker_labels, topk=8):
    imgs = {}
    for spk, hits in per_speaker_hits.items():
        cnt = Counter([h["marker"] for h in hits])
        top = cnt.most_common(topk)
        labels = [marker_labels.get(mid, mid) for mid,_ in top]
        values = [v for _,v in top]
        fig, ax = plt.subplots()
        ax.barh(range(len(top))[::-1], list(values)[::-1], color=PALETTE[:len(top)])
        ax.set_yticks(range(len(top))[::-1], labels[::-1])
        ax.set_title(f"Top-Marker: {spk}")
        ax.set_xlabel("Treffer")
        imgs[spk] = _fig_to_base64(fig)
    return imgs

# -------------------------
# Reporting
# -------------------------
def render_html_report(template_html: str, context: dict) -> str:
    # naive templating: {{key}} and {{#section}}..{{/section}} for simple loops
    out = template_html

    # simple replace for scalar values
    for k,v in context.items():
        if isinstance(v, (str,int,float)):
            out = out.replace("{{"+k+"}}", str(v))

    # sections: dicts of base64 images or arrays
    # images: context["images"] is dict name->dataurl
    images = context.get("images", {})
    for k, b64 in images.items():
        out = out.replace("{{img:"+k+"}}", f"data:image/png;base64,{b64}")

    # tables: context["tables"] : dict name -> HTML table
    tables = context.get("tables", {})
    for k, html in tables.items():
        out = out.replace("{{table:"+k+"}}", html)

    # text blocks
    blocks = context.get("text", {})
    for k, s in blocks.items():
        out = out.replace("{{text:"+k+"}}", s)

    # small lists
    lists = context.get("lists", {})
    for k, arr in lists.items():
        if isinstance(arr, list):
            li = "".join(f"<li>{mat_html(str(x))}</li>" for x in arr)
            out = out.replace("{{list:"+k+"}}", f"<ul>{li}</ul>")

    return out

def mat_html(s):  # minimal escape
    return (s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;"))

def df_to_table(df: pd.DataFrame):
    if df is None or df.empty:
        return "<em>Keine Daten</em>"
    # light styling inline
    return df.to_html(index=False, border=0, classes="table table-striped")

# -------------------------
# Scenario profiles
# -------------------------
SCENARIOS = {
    "beziehung": {
        "window": 30,
        "focus": ["Misstrauen","Defensive","Transparenz","Deeskalation","Grenzsetzung","Themenwechsel"]
    },
    "neuanfang": {
        "window": 20,
        "focus": ["Transparenz","Vulnerabilität","Ambivalenz","Validation","Grenzsetzung leicht"]
    },
    "freundschaft": {
        "window": 25,
        "focus": ["Support","Empathie","Alltag","Grenzsetzung leicht","Themenwechsel"]
    },
    "undefiniert": {
        "window": 40,
        "focus": ["Ambivalenz","Rollenwechsel","Misstrauen","Transparenz","Manipulation"]
    }
}

# -------------------------
# Main
# -------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", "-i", type=Path, required=True, help="Chat-Textdatei ('Name: Nachricht' pro Zeile empfohlen)")
    ap.add_argument("--scenario", "-s", choices=list(SCENARIOS.keys()), default="beziehung")
    ap.add_argument("--outdir", "-o", type=Path, default=Path("out_report"))
    ap.add_argument("--zip-schema", type=Path, default=DEFAULT_ZIP_SCHEMA)
    ap.add_argument("--zip-markers", type=Path, default=DEFAULT_ZIP_MARKERS)
    ap.add_argument("--zip-detectors", type=Path, default=DEFAULT_ZIP_DETECTORS)
    ap.add_argument("--window", type=int, default=None, help="Override rollierendes Fenster (Anzahl Nachrichten)")
    args = ap.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)

    # Load text
    chat_text = args.input.read_text(encoding="utf-8", errors="ignore")

    # Load resources
    R = Resources(args.zip_schema, args.zip_markers, args.zip_detectors,
                  THEMES_MAP_PATH, ACTIONS_MAP_PATH, EXTRA_MARKERS_PATH, ABSENCE_CONFIG_PATH)

    # Messages & hits
    msgs = chunk_messages(chat_text)
    hits = match_markers(msgs, R.regex_markers)
    
    # ABSENCE DETECTION: Insert after regular matching, before scoring
    if R.absence_config:
        hits = integrate_absence_detection(msgs, hits, R.absence_config, R.complete_marker_registry, R.E_SET)
    
    per_speaker = hits_by_speaker(hits)
    prim_counts = compute_primary_counts(hits, R.marker_to_primary)
    E, D = ed_counts(hits, R.E_SET, R.D_SET)
    wsum = weighted_sum(hits, R.weights)

    # Resonance / Core Theme
    theme = theme_resonance(hits, R)  # returns best theme + scores dicts

    # Scenario window
    conf = SCENARIOS[args.scenario]
    window = args.window or conf["window"]

    # Build tables
    # per-speaker basiswerte:
    rows = []
    for spk, hlist in per_speaker.items():
        cnt = Counter([h["marker"] for h in hlist])
        total = sum(cnt.values())
        Es = sum(v for mid, v in cnt.items() if mid in R.E_SET)
        Ds = sum(v for mid, v in cnt.items() if mid in R.D_SET)
        rows.append({
            "Person": spk,
            "Marker gesamt": total,
            "E": Es, "D": Ds,
            "E-Anteil": round((Es/total) if total else 0.0, 3)
        })
    df_compare = pd.DataFrame(rows).sort_values(by="Marker gesamt", ascending=False)

    # Text blocks (strictly marker-based)
    overview_txt = textwrap.dedent(f"""
    <b>Übersicht.</b> Es wurden <b>{len(hits)}</b> Marker-Treffer in <b>{len(msgs)}</b> Nachrichten erkannt.
    E/D gesamt: E=<b>{E}</b>, D=<b>{D}</b>. Gewichtete Summe (modellabhängig): <b>{round(wsum,2)}</b>.
    """).strip()

    theme_key = theme.get("theme_key", "Unbestimmt")
    theme_label = theme.get("theme_label", "Unbestimmt")
    core_txt = textwrap.dedent(f"""
    <b>Kern-Thema (markerbasiert):</b> <span class="chip">{mat_html(theme_label)}</span>
    (bestimmt aus Narrativen/Primärachsen-Resonanz; ohne freie Interpretation).
    """).strip()

    # Objective suggestions
    tips = build_objective_tips(per_speaker, R)
    tips_txt = ""
    for spk, suggs in tips.items():
        tips_txt += f"<h4>Objektive Hinweise für: {mat_html(spk)}</h4>\n"
        if not suggs:
            tips_txt += "<p>Keine dominanten Eskalationsmarker erkennbar.</p>"
        for s in suggs:
            pm = mat_html(s['problem_label'])
            cands = ", ".join([mat_html(x) for x in s["suggest_labels"]])
            tips_txt += f"<p>Häufiger Marker: <b>{pm}</b> → balancierende Marker anstreben: <b>{cands}</b>.</p>\n"

    # Build charts
    img_primary = chart_donut(dict(prim_counts), "Primär-Achsen (gesamt)")
    img_ed = chart_ed_bars(E, D, "E vs D (gesamt)")
    img_ts = chart_timeseries_ed(msgs, hits, R.E_SET, R.D_SET, window=window, title=f"E/D über Zeit (Fenster={window})")
    # Per speaker top markers (horizontal bars)
    img_tops = chart_top_markers_per_speaker(per_speaker, R.marker_labels, topk=8)

    # Theme resonance chart
    theme_chart = chart_theme_resonance(theme.get("theme_scores", {}), title="Themen-Resonanz (gesamt)")

    # Tables
    tables = {
        "compare": df_to_table(df_compare)
    }

    # Images to embed
    images = {
        "primary": img_primary or "",
        "ed": img_ed or "",
        "timeseries": img_ts or "",
        "theme": theme_chart or ""
    }
    # add per-speaker images
    for spk, b64 in img_tops.items():
        images[f"tops:{spk}"] = b64

    # Per-speaker sections (plain, marker-described)
    profiles = []
    for spk, hlist in per_speaker.items():
        cnt = Counter([R.marker_labels.get(h["marker"], h["marker"]) for h in hlist])
        top = ", ".join([f"{lab} ({n})" for lab,n in cnt.most_common(10)])
        profiles.append(f"<h4>{mat_html(spk)}</h4><p>Häufigste Marker (Top10): {mat_html(top)}</p><img class='img' src='{{{{img:tops:{spk}}}}}' alt='Top {spk}'/>")

    profiles_html = "\n".join(profiles)

    # Interpretable dynamics paragraph (still marker-based)
    dynamics_txt = textwrap.dedent("""
    <b>Was entsteht hier (markerbasiert)?</b><br/>
    Die Dynamik wird über die Verteilung der Primärachsen und die E/D-Balance sichtbar. 
    Erhöhte E-Anteile deuten auf mehr eskalierende Marker-Häufungen hin; eine Zunahme der D-Anteile im Zeitverlauf spricht für deeskalierende Sequenzen. 
    Die oben gezeigten Fenster-Verläufe zeigen, <i>wann</i> Cluster von E- bzw. D-Markern auftraten (rein aus Treffern, ohne zusätzliche Deutung).
    """).strip()

    # Put together HTML
    template = REPORT_TEMPLATE_PATH.read_text(encoding="utf-8")
    html = render_html_report(template, {
        "project_title": "Chat-Analyse (markerbasiert)",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "scenario": args.scenario.title(),
        "images": images,
        "tables": tables,
        "text": {
            "overview": overview_txt,
            "core": core_txt,
            "dynamics": dynamics_txt,
            "tips": tips_txt,
            "profiles": profiles_html
        }
    })

    # Save files
    out_html = args.outdir / "report.html"
    out_html.write_text(html, encoding="utf-8")

    # Also dump raw JSON (for reproducibility)
    dump = {
        "messages": msgs,
        "hits": hits,
        "per_speaker": {k: [h for h in v] for k,v in per_speaker.items()},
        "prim_counts": dict(prim_counts),
        "E": E, "D": D,
        "weighted_sum": wsum,
        "theme": theme
    }
    (args.outdir / "results.json").write_text(json.dumps(dump, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[OK] Report: {out_html}")
    print(f"[OK] Raw data: {args.outdir / 'results.json'}")

if __name__ == "__main__":
    main()
