#!/usr/bin/env python3
import os
import yaml

EXPANSIONS_DIR = "node/fryng_core/expansions"

def load_yaml(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data if data else {}
    except:
        return {}

def aggregate_synergy():
    synergy_data = {}
    print(f"[aggregate_synergy] expansions_dir = {EXPANSIONS_DIR}")

    if not os.path.exists(EXPANSIONS_DIR):
        print("[aggregate_synergy] expansions folder not found.")
        return synergy_data

    files_found = [fn for fn in os.listdir(EXPANSIONS_DIR) if fn.lower().endswith(".step")]
    if not files_found:
        print("[aggregate_synergy] No .step files found. synergy_data empty.")
        return synergy_data

    for fn in files_found:
        path = os.path.join(EXPANSIONS_DIR, fn)
        print(f"[aggregate_synergy] reading {path}")
        data = load_yaml(path)
        print("  -> loaded data:", data)

        # get step key from filename: e.g. "01_Potential.step" => "potential"
        step_parts = fn.split("_", 1)
        if len(step_parts) < 2:
            step_key = fn.rsplit(".", 1)[0].lower()
        else:
            step_key = step_parts[1].split(".")[0].lower()

        step_info = data.get("steps", {}).get(step_key, {})
        for k, v in step_info.items():
            if isinstance(v, (int, float)):
                synergy_data[f"{step_key}_{k}"] = v
                print(f"     numeric: {step_key}_{k} = {v}")

        dyn = data.get("dynamic_attributes", {})
        for k, v in dyn.items():
            if isinstance(v, (int, float)):
                synergy_data[f"{step_key}_{k}"] = v
                print(f"     dynamic: {step_key}_{k} = {v}")

    print("[aggregate_synergy] final synergy_data:", synergy_data)
    return synergy_data


if __name__ == "__main__":
    synergy = aggregate_synergy()
    print("aggregator test synergy =>", synergy)
