#!/usr/bin/env python3
"""
LeanDeep 3.3 Core Bundle Generator
Builds validated core bundles from marker collections with strict compliance checking.
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Set
from datetime import datetime
import hashlib
import argparse
from collections import defaultdict

ALLOWED_PREFIXES = ("ATO_", "SEM_", "CLU_", "MEMA_")

def load_yaml_files(folder: Path, skip_bad_yaml=False):
    """Robust YAML loader that handles syntax errors gracefully."""
    out = []
    files = sorted(list(folder.rglob("*.yml"))) + sorted(list(folder.rglob("*.yaml")))
    for p in files:
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
            data = yaml.safe_load(txt)
        except yaml.YAMLError as e:
            if skip_bad_yaml:
                print(f"[YAML WARN] {p}: {e.__class__.__name__}: {e}")
                continue
            raise SystemExit(f"[YAML ERROR] {p}: {e}")
        except Exception as e:
            if skip_bad_yaml:
                print(f"[FILE WARN] {p}: {e}")
                continue
            raise SystemExit(f"[FILE ERROR] {p}: {e}")
            
        if data is None:
            continue
        if isinstance(data, list):
            for obj in data:
                out.append((p, obj))
        elif isinstance(data, dict):
            out.append((p, data))
        else:
            print(f"[YAML WARN] {p}: root should be mapping or list; got {type(data).__name__}, skipping.")
    return out

def norm_version(v, accept_prefix=None):
    """Normalize version numbers with optional prefix acceptance."""
    if v is None:
        return None
    s = str(v).strip()
    if accept_prefix and s.startswith(accept_prefix):
        return "3.3"  # normalize
    return s

def norm_composed_of(obj):
    """Normalize composed_of field with various naming variants."""
    for key in ("composed_of", "composedOf", "compose_of"):
        if key in obj and isinstance(obj[key], list):
            return obj[key]
    return obj.get("composed_of") or []

def norm_pattern(obj):
    """Normalize pattern field - accept pattern as str or list, also patterns."""
    if "pattern" in obj:
        pat = obj["pattern"]
        if isinstance(pat, str): 
            return [pat]
        if isinstance(pat, list): 
            return pat
    if "patterns" in obj and isinstance(obj["patterns"], list):
        return obj["patterns"]
    return None

def derive_display_title(obj):
    """Derive display title from various sources."""
    # Check for existing display_title first
    if obj.get("display_title"):
        return str(obj["display_title"])
    
    title = obj.get("title")
    if title: 
        return str(title)
    frame = obj.get("frame") or {}
    concept = frame.get("concept")
    if isinstance(concept, str) and concept.strip():
        return concept.strip()
    signal = frame.get("signal")
    if isinstance(signal, list) and signal:
        # prefer first non-empty string
        for s in signal:
            if isinstance(s, str) and s.strip():
                return s.strip()
    return obj.get("id") or "UNKNOWN"

def normalize_marker_structure(obj):
    """Normalize marker structure to support _id and other MongoDB conventions."""
    # Handle _id field (MongoDB convention)
    if "_id" in obj and "id" not in obj:
        obj["id"] = obj["_id"]
    elif "id" in obj and "_id" not in obj:
        obj["_id"] = obj["id"]
    
    # Ensure display_title is present
    if "display_title" not in obj:
        obj["display_title"] = derive_display_title(obj)
    
    # Add updated_at if missing
    if "updated_at" not in obj:
        obj["updated_at"] = datetime.now().isoformat() + "Z"
    
    return obj

def sanitize_examples(ex, min_examples=5):
    """Only strings, no meta window notes like [0–29], no bracketed annotations."""
    if not isinstance(ex, list):
        return []
    out = []
    for s in ex:
        if isinstance(s, str):
            s_clean = s.strip()
            if "[" in s_clean and "]" in s_clean:
                # likely meta annotation, skip
                continue
            out.append(s_clean)
    return out[:9999]  # just a guard

def collect_markers(src_dir: Path, include_manifest: Path | None = None, relaxed=False, skip_bad_yaml=False, accept_prefix=None, min_examples=5):
    """Collect and validate markers with relaxed mode support."""
    all_items = load_yaml_files(src_dir, skip_bad_yaml=skip_bad_yaml)
    allow = None
    if include_manifest and include_manifest.exists():
        allow = set()
        man = yaml.safe_load(include_manifest.read_text(encoding="utf-8"))
        for mid in man.get("include_ids", []):
            allow.add(mid)

    by_id = {}
    by_prefix = defaultdict(dict)
    validation_errors = []
    
    for path, obj in all_items:
        if not isinstance(obj, dict):
            print(f"[VALIDATION WARN] {path}: item is not a mapping, skipping.")
            continue

        mid = obj.get("id")
        if not mid:
            if relaxed:
                print(f"[VALIDATION WARN] {path}: missing id → skipping")
                continue
            validation_errors.append(f"Missing id in {path}")
            continue

        if allow and mid not in allow:
            continue

        # Prefix validation
        if not any(mid.startswith(prefix) for prefix in ALLOWED_PREFIXES):
            validation_errors.append(f"{mid}: disallowed prefix (allowed: {'/'.join(ALLOWED_PREFIXES)})")
            continue

        # Version validation
        v = norm_version(obj.get("version"), accept_prefix=accept_prefix)
        if v != "3.3":
            if relaxed:
                print(f"[VALIDATION WARN] {mid}: version not '3.3', but continuing due to --relaxed")
            else:
                validation_errors.append(f"{mid}: version must be '3.3'")
                continue

        # Normalize marker structure
        obj = normalize_marker_structure(obj)
        
        # Normalize composed_of & pattern
        comp = norm_composed_of(obj)
        pat = norm_pattern(obj)
        if pat is not None:
            obj["pattern"] = pat  # ensure list
        if comp:
            obj["composed_of"] = comp

        # Examples validation
        ex = sanitize_examples(obj.get("examples") or [], min_examples or 5)
        min_needed = int(min_examples) if min_examples is not None else 5
        if len(ex) < min_needed:
            if relaxed:
                print(f"[VALIDATION WARN] {mid}: has only {len(ex)} examples (<{min_needed}); continuing due to --relaxed")
            else:
                validation_errors.append(f"{mid}: need ≥{min_needed} purely textual examples")
                continue
        obj["examples"] = ex

        # Derive display title (already done in normalize_marker_structure)
        # obj["display_title"] = derive_display_title(obj)

        # Lang default
        if "lang" not in obj and relaxed:
            obj["lang"] = "de"

        if mid in by_id:
            validation_errors.append(f"Duplicate id {mid}")
            continue

        pre = mid.split("_", 1)[0]
        by_id[mid] = obj
        by_prefix[pre][mid] = obj

    return by_id, by_prefix, validation_errors

def validate_relations(by_prefix, relaxed=False):
    """Validate hierarchical relationships between markers."""
    validation_errors = []
    
    # SEM → needs composed_of >=2 ATO_
    for mid, m in by_prefix.get("SEM", {}).items():
        comp = m.get("composed_of") or []
        if not (isinstance(comp, list) and len(comp) >= 2 and all(str(r).startswith("ATO_") for r in comp)):
            if relaxed:
                print(f"[VALIDATION WARN] {mid}: SEM should have composed_of >=2 ATO_")
            else:
                validation_errors.append(f"{mid}: SEM needs composed_of >=2 ATO_")

    # CLU → composed_of >=2 SEM_ or explicit activation rule
    for mid, m in by_prefix.get("CLU", {}).items():
        comp = m.get("composed_of") or []
        has_rule = m.get("activation") is not None
        if not ((isinstance(comp, list) and len(comp) >= 2 and all(str(r).startswith("SEM_") for r in comp)) or has_rule):
            if relaxed:
                print(f"[VALIDATION WARN] {mid}: CLU should have composed_of >=2 SEM_ or activation rule")
            else:
                validation_errors.append(f"{mid}: CLU needs composed_of >=2 SEM_ or activation rule")

    # MEMA → must have criteria or detect_class
    for mid, m in by_prefix.get("MEMA", {}).items():
        if not (m.get("criteria") or m.get("detect_class")):
            validation_errors.append(f"{mid}: MEMA must define criteria or detect_class")
    
    return validation_errors

class LeanDeep33BundleGenerator:
    def __init__(self, project_root: str, relaxed=False, skip_bad_yaml=False, accept_prefix=None, min_examples=5):
        self.project_root = Path(project_root)
        self.markers_dir = self.project_root / "markers"
        self.config_dir = self.project_root / "config"
        self.output_dir = self.project_root / "out_bundle"
        
        # Configuration options
        self.relaxed = relaxed
        self.skip_bad_yaml = skip_bad_yaml
        self.accept_prefix = accept_prefix
        self.min_examples = min_examples
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
        
        # Load all markers into memory
        self.all_markers = {}
        self.validation_errors = []
        
    def load_all_markers(self):
        """Load all YAML markers using the new robust collector."""
        print("Loading markers from categorized folders...")
        
        include_manifest_path = self.config_dir / "core_bundle_manifest.yaml"
        by_id, by_prefix, validation_errors = collect_markers(
            self.markers_dir,
            include_manifest_path,
            relaxed=self.relaxed,
            skip_bad_yaml=self.skip_bad_yaml,
            accept_prefix=self.accept_prefix,
            min_examples=self.min_examples
        )
        
        # Additional relation validation
        relation_errors = validate_relations(by_prefix, relaxed=self.relaxed)
        validation_errors.extend(relation_errors)
        
        self.all_markers = by_id
        self.validation_errors = validation_errors
        
        print(f"Loaded {len(self.all_markers)} total markers")
        return len(self.all_markers) > 0
    
    def load_config_file(self, filename: str) -> Dict[str, Any]:
        """Load a configuration YAML file."""
        config_path = self.config_dir / filename
        if not config_path.exists():
            self.validation_errors.append(f"Missing config file: {filename}")
            return {}
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            self.validation_errors.append(f"Error loading config {filename}: {str(e)}")
            return {}
    
    def generate_schema_full_bundle(self, core_manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Generate the complete schema bundle with all included markers."""
        include_ids = set(core_manifest.get('include_ids', []))
        
        # Validate all included IDs exist
        missing_ids = include_ids - set(self.all_markers.keys())
        if missing_ids:
            for missing_id in missing_ids:
                self.validation_errors.append(f"Core manifest references missing marker: {missing_id}")
        
        # Build the schema bundle - markers are already validated by collect_markers
        bundle_markers = {}
        for marker_id in include_ids:
            if marker_id in self.all_markers:
                bundle_markers[marker_id] = self.all_markers[marker_id]
        
        # Generate metadata
        timestamp = datetime.now().isoformat()
        bundle_hash = hashlib.sha256(json.dumps(bundle_markers, sort_keys=True).encode()).hexdigest()[:16]
        
        schema_bundle = {
            "metadata": {
                "bundle_type": "LeanDeep_3.3_Core_Bundle",
                "generated_at": timestamp,
                "bundle_hash": bundle_hash,
                "total_markers": len(bundle_markers),
                "version": "3.3.0"
            },
            "markers": bundle_markers,
            "validation": {
                "leandeep33_compliant": len(self.validation_errors) == 0,
                "validation_errors": self.validation_errors
            }
        }
        
        return schema_bundle
    
    def generate_sets_config(self, sets_overrides: Dict[str, Any]) -> Dict[str, Any]:
        """Generate the sets configuration file with conflict_gating support."""
        timestamp = datetime.now().isoformat()
        
        # Build the enhanced sets configuration
        sets_config = {
            "metadata": {
                "config_type": "LeanDeep_3.3_Sets_Configuration",
                "generated_at": timestamp,
                "version": "3.3.0"
            },
            "version": "3.3",
            "resolve_order": ["marker_to_class", "tag_to_class"],
            "marker_sets": sets_overrides,
            "conflict_gating": {
                "window": {"messages": 30},
                "min_E_hits": 3
            }
        }
        
        return sets_config
    
    def generate_weights_config(self, weights_overrides: Dict[str, Any]) -> Dict[str, Any]:
        """Generate the weights configuration file."""
        timestamp = datetime.now().isoformat()
        
        weights_config = {
            "metadata": {
                "config_type": "LeanDeep_3.3_Weights_Configuration", 
                "generated_at": timestamp,
                "version": "3.3.0"
            },
            "weights": weights_overrides
        }
        
        return weights_config
    
    def generate_primary_axes_config(self, primary_axes: Dict[str, Any]) -> Dict[str, Any]:
        """Generate the primary axes configuration file."""
        timestamp = datetime.now().isoformat()
        
        axes_config = {
            "metadata": {
                "config_type": "LeanDeep_3.3_Primary_Axes_Configuration",
                "generated_at": timestamp, 
                "version": "3.3.0"
            },
            "primary_axes": primary_axes.get('primary_axes', [])
        }
        
        return axes_config
    
    def save_json_file(self, data: Dict[str, Any], filename: str):
        """Save data as a formatted JSON file."""
        output_path = self.output_dir / filename
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Generated: {filename}")
        except Exception as e:
            self.validation_errors.append(f"Error saving {filename}: {str(e)}")
    
    def generate_bundles(self):
        """Main method to generate all core bundles."""
        print("=== LeanDeep 3.3 Core Bundle Generator ===")
        print(f"Project root: {self.project_root}")
        print()
        
        # Load all markers
        if not self.load_all_markers():
            print("ERROR: Failed to load markers")
            return False
        
        # Load configuration files
        core_manifest = self.load_config_file("core_bundle_manifest.yaml")
        sets_overrides = self.load_config_file("sets_overrides.yaml")
        weights_overrides = self.load_config_file("weights_overrides.yaml")
        primary_axes = self.load_config_file("primary_axes.yaml")
        
        # Check if we have essential config
        if not core_manifest:
            print("ERROR: Missing core bundle manifest")
            return False
        
        print("Generating bundle files...")
        
        # Generate schema full bundle
        schema_bundle = self.generate_schema_full_bundle(core_manifest)
        self.save_json_file(schema_bundle, "schema_full_bundle.json")
        
        # Generate sets config
        if sets_overrides:
            sets_config = self.generate_sets_config(sets_overrides)
            self.save_json_file(sets_config, "sets_config.json")
        
        # Generate weights config
        if weights_overrides:
            weights_config = self.generate_weights_config(weights_overrides)
            self.save_json_file(weights_config, "weights.json")
        
        # Generate primary axes config
        if primary_axes:
            axes_config = self.generate_primary_axes_config(primary_axes)
            self.save_json_file(axes_config, "primary_axes.json")
        
        # Final validation report
        print()
        print("=== VALIDATION REPORT ===")
        if self.validation_errors:
            print(f"❌ {len(self.validation_errors)} validation errors found:")
            for error in self.validation_errors:
                print(f"  - {error}")
            return False
        else:
            print("✅ All validations passed")
            print(f"✅ Generated {len(schema_bundle['markers'])} compliant markers")
            print("✅ LeanDeep 3.3 bundle generation complete")
            return True

def main():
    parser = argparse.ArgumentParser(description="LeanDeep 3.3 Core Bundle Generator")
    parser.add_argument("project_root", help="Path to project root directory")
    parser.add_argument("--relaxed", action="store_true", help="Be lenient with structure, derive display_title, etc.")
    parser.add_argument("--allow-short-examples", type=int, default=None, help="Allow >=N examples instead of >=5")
    parser.add_argument("--accept-version-prefix", type=str, default=None, help="Accept versions that start with this prefix (e.g. 3.3)")
    parser.add_argument("--skip-bad-yaml", action="store_true", help="Continue on YAML syntax errors, just warn and skip file")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.project_root):
        print(f"ERROR: Project root does not exist: {args.project_root}")
        sys.exit(1)
    
    generator = LeanDeep33BundleGenerator(
        args.project_root,
        relaxed=args.relaxed,
        skip_bad_yaml=args.skip_bad_yaml,
        accept_prefix=args.accept_version_prefix,
        min_examples=args.allow_short_examples or 5
    )
    success = generator.generate_bundles()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
