import os

# -------------------------------------------------------
# Define the desired directory and file structure
# -------------------------------------------------------
DIRECTORY_STRUCTURE = {
    "node": {
        "data": [
            "node_state.json",
            "synergy_attrs.json"
        ],
        "logs": [
            "fryng_actions.log",
            "node_updates.log"
        ],
        "steps": [
            "step1_seed.py",
            "step2_branch_merge.py",
            "step3_feedback.py",
            "step4_resonance.py",
            "step5_replication.py",
            "step6_pruning.py"
        ],
        "fryng_core": {
            "docs": {
                "version_logs": [
                    "design_philosophy.md",
                    "usage_instructions.md"
                ]
            },
            "expansions": [
                "01_Potential.step",
                "02_Symmetry.step",
                "03_Flow.step",
                "04_Connectivity.step",
                "05_Emergence.step",
                "06_Recursion.step",
                "expansions.log",
                "expansions.task"
            ],
            "foundation": [
                "cosmic.axis",
                "default.span",
                "fryng.law",
                "readme.doc"
            ],
            "seeds": [
                "default.seed"
            ],
            "stories": {
                "characters": [
                    "hero.char",
                    "mentor.char"
                ],
                "cultures": [
                    "desert_folk.cult",
                    "forest_tribe.cult"
                ],
                "realms": [
                    "auralis.realm",
                    "sylph.realm"
                ],
                "scenes": [
                    "scene1.scribe"
                ]
            },
            "tune": [
                "exponential.tune",
                "logistic.tune",
                "polynomial.tune"
            ],
            "_files": [
                "__inti__.py",  # rename to __init__.py if you prefer
                "fryng.flow",
                "fryng_run.py",
                "fryng_utils.py",
                "version.log"
            ]
        },
        "ui_core": {
            "__pycache__": [],
            "_files": [
                "README.md",
                "__inti__.py",
                "debug_ui.py",
                "dflt_ui.py",
                "fryng_canvas_demo.py",
                "fryng_config.json",
                "fryng_controls.py",
                "fryng_debug.py",
                "fryng_events.py",
                "fryng_gui.py",
                "fryng_hex.py",
                "fryng_visuals.py",
                "log_viewer_demo.py",
                "main_ui.py",
                "polar_slider_demo.py",
                "polar_slider_display.py",
                "slider_demo.py",
                "tkk.style"
            ]
        },
        "_files": [
            "README.md",
            "__init__.py",
            "build_node.py",
            "run_ui.py"
        ]
    }
}


def create_structure(base_path, structure):
    """
    Recursively create directories and files as defined in the `structure` dict.
    Each key in `structure` can be:
      - A dict (subfolder),
      - A list of files/subfolders,
      - Or a special "_files" list for direct file creation in the current folder.
    """
    for key, value in structure.items():
        # If value is a dict, we treat key as a subfolder name
        if isinstance(value, dict):
            # "key" is the subfolder name
            dir_path = os.path.join(base_path, key)
            print(f"Creating directory: {dir_path}")
            os.makedirs(dir_path, exist_ok=True)
            # Recursively build inside
            create_structure(dir_path, value)

        elif isinstance(value, list):
            # If key starts with "_files", these are direct files in base_path
            if key.startswith("_files"):
                for filename in value:
                    file_path = os.path.join(base_path, filename)
                    if not os.path.exists(file_path):
                        print(f"Creating file: {file_path}")
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(f"# placeholder for {filename}\n")
            else:
                # Otherwise, key is a directory that holds these files
                dir_path = os.path.join(base_path, key)
                print(f"Creating directory: {dir_path}")
                os.makedirs(dir_path, exist_ok=True)
                # For each item in the list, it might be a file or a sub-dict
                for item in value:
                    if isinstance(item, dict):
                        # Sub-dict structure within a list
                        create_structure(dir_path, item)
                    else:
                        # It's a filename
                        file_path = os.path.join(dir_path, item)
                        if not os.path.exists(file_path):
                            print(f"Creating file: {file_path}")
                            with open(file_path, "w", encoding="utf-8") as f:
                                f.write(f"# placeholder for {item}\n")
        else:
            # Unexpected type or structure
            print(f"Skipping unexpected entry: {key} => {value}")


if __name__ == "__main__":
    # We'll create everything in the current working directory
    root_path = os.getcwd()
    print("Current working directory:", root_path)

    # Build the structure
    create_structure(root_path, DIRECTORY_STRUCTURE)

    print("\nFryng Node structure built successfully!")
