#!/usr/bin/env python3
"""
Update existing marker files to Lean-Deep 3.3 compliance
"""
import os
import json
import datetime
import pathlib

# Configuration
base_dir = "/Users/benjaminpoersch/:Users:benjaminpoersch:claude/_STARTING_/LeanDeep3.3_Marker_Backend/project"
today = datetime.date(2025, 8, 19).isoformat()

def update_registry():
    """Update registry to LD-3.3 and add auto_generated flag"""
    registry_path = os.path.join(base_dir, "registry", "DETECT_registry.json")
    
    # Create registry directory if it doesn't exist
    os.makedirs(os.path.dirname(registry_path), exist_ok=True)
    
    if os.path.exists(registry_path):
        with open(registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)
    else:
        registry = []

    # Update existing entries
    for entry in registry:
        entry["schema_version"] = "LD-3.3"
        entry["last_updated"] = today
        entry["auto_generated"] = True

    # Add new entries for our updated markers
    marker_entries = [
        {
            "id": "ATO_GOTTMAN_DEFENSIVENESS",
            "schema_version": "LD-3.3",
            "category": "ATOMIC",
            "last_updated": today,
            "auto_generated": True,
            "path": "markers/ato/ATO_GOTTMAN_DEFENSIVENESS.yaml"
        },
        {
            "id": "ATO_GOTTMAN_CONTEMPT", 
            "schema_version": "LD-3.3",
            "category": "ATOMIC",
            "last_updated": today,
            "auto_generated": True,
            "path": "markers/ato/ATO_GOTTMAN_CONTEMPT.yaml"
        },
        {
            "id": "SEM_CONFLICT_MACRO",
            "schema_version": "LD-3.3", 
            "category": "SEMANTIC",
            "last_updated": today,
            "auto_generated": True,
            "path": "markers/sem/SEM_CONFLICT_MACRO.yaml"
        },
        {
            "id": "CLU_HOSTILE_DETACHED",
            "schema_version": "LD-3.3",
            "category": "CLUSTER", 
            "last_updated": today,
            "auto_generated": True,
            "path": "markers/clu/CLU_HOSTILE_DETACHED.yaml"
        }
    ]

    # Add new entries to registry if they don't exist
    existing_ids = {entry.get("id") for entry in registry}
    for new_entry in marker_entries:
        if new_entry["id"] not in existing_ids:
            registry.append(new_entry)

    # Write updated registry
    with open(registry_path, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)
    
    print(f"Registry updated: {registry_path}")
    return registry_path

def validate_marker_files():
    """Validate that all marker files exist and have correct structure"""
    marker_files = [
        "markers/ato/ATO_GOTTMAN_DEFENSIVENESS.yaml",
        "markers/ato/ATO_GOTTMAN_CONTEMPT.yaml", 
        "markers/sem/SEM_CONFLICT_MACRO.yaml",
        "markers/clu/CLU_HOSTILE_DETACHED.yaml"
    ]
    
    missing_files = []
    for marker_file in marker_files:
        full_path = os.path.join(base_dir, marker_file)
        if not os.path.exists(full_path):
            missing_files.append(full_path)
        else:
            print(f"✅ {marker_file}")
    
    if missing_files:
        print("❌ Missing files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    return True

if __name__ == "__main__":
    print("Updating LeanDeep 3.3 marker compliance...")
    
    # Validate marker files exist
    if validate_marker_files():
        print("All marker files validated successfully")
    else:
        print("Some marker files are missing")
        exit(1)
    
    # Update registry
    registry_path = update_registry()
    
    print("\n✅ LeanDeep 3.3 compliance update completed!")
    print(f"Registry: {registry_path}")
