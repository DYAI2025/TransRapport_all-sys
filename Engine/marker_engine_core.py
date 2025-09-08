#!/usr/bin/env python3
"""
marker_engine_core.py
─────────────────────────────────────────────────────────────────
Lean-Deep 3.4-konformer Engine-Kern.
Lädt Marker-Definitionen (ATO_/SEM_/CLU_/MEMA_ Präfix), wendet Detektoren aus Registry an,
führt Scoring und Fusion nach Master-Schema durch. Gibt strukturierte Ergebnisse.
"""

from pathlib import Path
import yaml
import json
import importlib
import re
import datetime
from typing import Dict, List, Any

# --------------------------------------------------------------
PRFX_LEVELS = ("ATO_", "SEM_", "CLU_", "MEMA_")

class MarkerEngine:
    def __init__(self,
                 marker_root: str = "markers",
                 schema_root: str = "schemata",
                 detect_registry: str = "DETECT_registry.json",
                 plugin_root: str = "plugins"):

        self.marker_path   = Path(marker_root)
        self.schema_path   = Path(schema_root)
        self.plugin_root   = Path(plugin_root)
        self.detect_registry = Path(detect_registry)

        # interne Caches
        self.markers : Dict[str, Dict[str, Any]] = {}
        self.schemas : Dict[str, Dict[str, Any]] = {}
        self.active_schemas : List[Dict[str, Any]] = []
        self.schema_priority : Dict[str, float] = {}
        self.fusion_mode : str = "multiply"
        self.detectors: List[Dict[str, Any]]     = []
        self.plugins  : Dict[str, Any]           = {}

        self._load_markers()
        self._load_schemata()
        self._load_detectors()

    # ----------------------------------------------------------
    # Loader
    # ----------------------------------------------------------
    def _load_markers(self):
        """Lädt alle Marker aus atomic/semantic/cluster/meta und prüft Präfix."""
        for sub in ["atomic", "semantic", "cluster", "meta"]:
            sub_path = self.marker_path / sub
            if not sub_path.exists():
                continue
            for file in sub_path.glob("*.yaml"):
                data = yaml.safe_load(file.read_text("utf-8"))
                marker_id = data.get("id")
                if marker_id and marker_id[:4] in PRFX_LEVELS:
                    self.markers[marker_id] = data

    def _load_schemata(self):
        """Lädt alle Schemata + Master-Schema für Fusion/Prioritäten."""
        for file in self.schema_path.glob("SCH_*.json"):
            data = json.loads(file.read_text("utf-8"))
            self.schemas[data["id"]] = data
        master_path = self.schema_path / "MASTER_SCH_CORE.json"
        if master_path.exists():
            master = json.loads(master_path.read_text("utf-8"))
            self.active_schemas = [self.schemas[sch] for sch in master["active_schemata"]]
            self.schema_priority = master.get("priority", {})
            self.fusion_mode = master.get("fusion", "multiply")

    def _load_detectors(self):
        """Lädt alle Detektoren aus Registry, inkl. optionaler Plugins."""
        if not self.detect_registry.exists():
            raise FileNotFoundError("Detector-Registry nicht gefunden!")
        reg = json.loads(self.detect_registry.read_text("utf-8"))
        for entry in reg:
            self.detectors.append(entry)
            if entry["module"] == "plugin":
                plugin_path = (self.plugin_root / Path(entry["file_path"]).name)
                spec = importlib.util.spec_from_file_location(entry["id"], plugin_path)
                mod  = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)  # type: ignore
                self.plugins[entry["id"]] = mod

    # ----------------------------------------------------------
    # Haupt­methode
    # ----------------------------------------------------------
    def analyze(self, text: str) -> Dict[str, Any]:
        hits: List[Dict[str, Any]] = []

        # 1) Detector-Registry anwenden (Präfix-Fire)
        for det in self.detectors:
            if det["module"] == "regex":
                spec = json.loads(Path(det["file_path"]).read_text("utf-8"))
                pattern = re.compile(spec["rule"]["pattern"], re.IGNORECASE)
                if pattern.search(text):
                    hits.append({"marker": spec["fires_marker"], "source": det["id"]})

            elif det["module"] == "plugin":
                plugin = self.plugins[det["id"]]
                result = plugin.run(text)
                hits.extend({"marker": m, "source": det["id"]} for m in result.get("fires", []))

        # 2) Pattern-basierte Marker (nur Level 1, atomic)
        for marker_id, marker in self.markers.items():
            if marker_id.startswith("ATO_") and "pattern" in marker:
                pats = marker["pattern"]
                if isinstance(pats, str): pats = [pats]
                for pat in pats:
                    if re.search(pat, text, re.IGNORECASE):
                        hits.append({"marker": marker_id, "source": "pattern"})
                        break

        # 3) Schema-Fusion (Scoring/Priorisierung)
        final_scores: Dict[str, float] = {}
        for hit in hits:
            m = self.markers.get(hit["marker"])
            if not m: continue
            weight = m.get("scoring", {}).get("weight", 1.0)
            raw = 1.0 * weight

            for sch in self.active_schemas:
                prio = self.schema_priority.get(Path(sch["id"]).name + ".json", 1.0)
                if self.fusion_mode == "multiply":
                    raw *= prio
                elif self.fusion_mode == "sum":
                    raw += prio

            final_scores[hit["marker"]] = final_scores.get(hit["marker"], 0) + raw

        return {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "hits": hits,
            "scores": final_scores
        }

# -----------------------------------------------------------------
if __name__ == "__main__":
    eng = MarkerEngine()
    sample = "Ich weiß normalerweise, was ich will, aber hier bin ich mir nicht sicher."
    import pprint
    pprint.pprint(eng.analyze(sample))
