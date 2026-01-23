
import os
import yaml
import math

def load_yaml(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data if data else {}
    except:
        return {}

def save_yaml(path, data):
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False)


def refine_fryng_core():
    expansions_dir = "node/fryng_core/expansions"
    step_rules = {
        "01_Potential.step": {
            "steps": {
                "potential": {
                    "desc": "Initialization impetus",
                    "energy": 0.7
                }
            },
            "dynamic_attributes": {"coherence": 0.5}
        },
        "02_Symmetry.step": {
            "steps": {
                "symmetry": {
                    "desc": "Balancing and alignment"
                }
            },
            "dynamic_attributes": {"alignment": 0.6}
        }
        # etc. for the other steps
    }

    if os.path.exists(expansions_dir):
        for fn in os.listdir(expansions_dir):
            full_path = os.path.join(expansions_dir, fn)
            if fn in step_rules:
                data = load_yaml(full_path)
                rule = step_rules[fn]
                # For each top-level key (like steps, dynamic_attributes),
                # we unify with data
                for k, v in rule.items():
                    if k not in data:
                        data[k] = {}
                    if isinstance(v, dict) and isinstance(data[k], dict):
                        data[k].update(v)
                    else:
                        data[k] = v
                save_yaml(full_path, data)
                print(f"[refine] refined expansions: {full_path}")

def refine_top_level_steps():
    steps_dir = "node/steps"
    # Suppose we do a similar approach for subfolder "01_Potential" etc.
    # We'll define a dictionary keyed by the subfolder name
    step_folder_rules = {
        "01_Potential": {
            "steps": {
                "potential": {
                    "purpose": "From top-level synergy subfolder"
                }
            }
        }
        # etc...
    }
    if os.path.exists(steps_dir):
        for step_name in step_folder_rules:
            init_file = os.path.join(steps_dir, step_name, "init")
            if os.path.exists(init_file):
                data = load_yaml(init_file)
                rule = step_folder_rules[step_name]
                for k, v in rule.items():
                    if k not in data:
                        data[k] = {}
                    if isinstance(v, dict) and isinstance(data[k], dict):
                        data[k].update(v)
                    else:
                        data[k] = v
                save_yaml(init_file, data)
                print(f"[refine] refined top-level steps: {init_file}")

def refine_all():
    refine_fryng_core()
    refine_top_level_steps()
    print("[refine] refine pass done.")

if __name__ == "__main__":
    refine_all()
