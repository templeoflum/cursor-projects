
import os
import yaml

UNIVERSAL_BASE_DICT = {
    "version": "1.0",
    "name": "Universal 6-Step Base",
    "steps": {
        "potential": {},
        "symmetry": {},
        "flow": {},
        "connectivity": {},
        "emergence": {},
        "recursion": {}
    },
    "notes": "Base synergy skeleton."
}

def deep_merge(base, updates):
    for k, v in updates.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            deep_merge(base[k], v)
        else:
            base[k] = v
    return base

def load_yaml(path) -> dict:
    if not os.path.exists(path):
        return {}
    try:
        import yaml
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data if data else {}
    except:
        return {}

def save_yaml(path, data):
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False)

def update_file(file_path: str):
    existing = load_yaml(file_path)
    final = deep_merge(UNIVERSAL_BASE_DICT.copy(), existing)
    save_yaml(file_path, final)
    print(f"[update] Merged synergy base into {file_path}")

def run_update():
    # 1) expansions
    expansions_dir = "node/fryng_core/expansions"
    if os.path.exists(expansions_dir):
        for fn in os.listdir(expansions_dir):
            if fn.lower().endswith(".step"):
                fp = os.path.join(expansions_dir, fn)
                update_file(fp)

    # 2) seeds
    seeds_dir = "node/fryng_core/seeds"
    if os.path.exists(seeds_dir):
        for fn in os.listdir(seeds_dir):
            if fn.lower().endswith(".seed"):
                fp = os.path.join(seeds_dir, fn)
                update_file(fp)

    # 3) top-level 6-step subfolders in node/steps
    steps_top = "node/steps"
    if os.path.exists(steps_top):
        for step_name in os.listdir(steps_top):
            step_path = os.path.join(steps_top, step_name)
            if os.path.isdir(step_path):
                init_file = os.path.join(step_path, "init")
                if os.path.exists(init_file):
                    update_file(init_file)

    print("[update] universal synergy updates done.")

if __name__ == "__main__":
    run_update()
