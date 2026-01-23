import os
import json

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "..", "data")
SYNERGY_FILE = os.path.join(DATA_FOLDER, "synergy_attrs.json")

# A universal “starting point” for synergy data:
DEFAULT_SYNERGY = {
    "potential": 0.0,
    "symmetry": 0.0,
    "flow": 0.0,
    "connectivity": 0.0,
    "emergence": 0.0,
    "recursion": 0.0,
    "current_seed": "default.seed",
    "expansions": {
        "01_Potential": True,
        "02_Symmetry": True,
        "03_Flow": True,
        "04_Connectivity": False,
        "05_Emergence": False,
        "06_Recursion": False
    }
}


def init_synergy_file():
    """
    Ensures synergy_attrs.json exists and has our 6-step synergy keys.
    If missing or incomplete, populate with default values.
    """
    if not os.path.exists(SYNERGY_FILE):
        # Create synergy_attrs from scratch
        print("[init_synergy_file] synergy_attrs.json missing; creating default.")
        with open(SYNERGY_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_SYNERGY, f, indent=2)
        return

    # If synergy_attrs.json exists, we ensure all the required keys exist
    with open(SYNERGY_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {}

    changed = False
    # For each key in DEFAULT_SYNERGY, if missing, populate
    for k, v in DEFAULT_SYNERGY.items():
        if k not in data:
            data[k] = v
            changed = True
        else:
            # If it's expansions or some sub-structure, ensure subkeys exist
            if isinstance(v, dict) and isinstance(data[k], dict):
                for sub_k, sub_v in v.items():
                    if sub_k not in data[k]:
                        data[k][sub_k] = sub_v
                        changed = True

    if changed:
        print("[init_synergy_file] synergy_attrs.json was incomplete; updated.")
        with open(SYNERGY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


def load_synergy_data():
    """
    Reads synergy_attrs.json and returns it as a dict.
    Call init_synergy_file() first to ensure the file is consistent.
    """
    init_synergy_file()  # ensure file & keys exist
    with open(SYNERGY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def save_synergy_data(new_data: dict):
    """
    Writes synergy data back to synergy_attrs.json, ensuring 6-step structure remains.
    Usually you'd call load_synergy_data(), manipulate the dict, then save.
    """
    # optional: we can re-check keys or clamp values if needed
    with open(SYNERGY_FILE, "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=2)
    print("[save_synergy_data] synergy_attrs.json updated.")


def update_synergy_step(step_name: str, new_value: float):
    """
    A helper to set synergy_attrs[step_name] = new_value,
    while ensuring it's one of the 6 recognized steps.
    """
    valid_steps = ["potential", "symmetry", "flow", "connectivity", "emergence", "recursion"]
    if step_name not in valid_steps:
        print(f"[update_synergy_step] Unknown synergy step: {step_name}")
        return

    data = load_synergy_data()
    data[step_name] = new_value
    save_synergy_data(data)


def get_seed_path():
    """
    Example function to get the currently active seed path from synergy data.
    """
    data = load_synergy_data()
    seed_name = data.get("current_seed", "default.seed")
    # Then you might do something like building a path:
    seeds_folder = os.path.join(os.path.dirname(__file__), "seeds")
    return os.path.join(seeds_folder, seed_name)


def run_synergy_logic():
    """
    Here is where we might interpret synergy steps + expansions + seed to do something more advanced.
    For now, let's just load synergy and print it out.
    """
    synergy = load_synergy_data()
    print("[run_synergy_logic] synergy states:")
    for k, v in synergy.items():
        print(f"  {k} => {v}")

    # Potential advanced logic:
    # - check expansions flags
    # - read seed content
    # - perform iterative transformations, etc.
