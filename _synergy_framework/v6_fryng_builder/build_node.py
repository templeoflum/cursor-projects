"""
node_all.py
-----------
Generates a single 'node/' folder containing:
  - fryng_core/ (which itself contains expansions/, foundation/, stories/, docs/, seeds/, tune/ etc.)
  - steps/, data/, logs/, ui_core/ at node/ root if you want them separate

Run:
    python node_all.py

The script prints each creation step to console.

Modify as needed for your final arrangement.
"""

import os

NODE_FOLDER = "node"

# This dictionary describes the entire structure under "node/".
# We will nest expansions, foundation, stories, docs, seeds, tune, etc. inside "fryng_core/".
# Meanwhile, steps/, data/, logs/, and ui_core/ remain at the top-level of "node/" itself.
NODE_STRUCTURE = {
    # Empty key => top-level of node/
    "": [
        # If you want a top-level file in node/, add it here (e.g. "README.md").
        # e.g. "README.md"
    ],

    # Some optional top-level subfolders: steps, data, logs, ui_core
    "steps": [
        # example placeholders
        "step1_seed.py",
        "step2_branch_merge.py",
        "step3_feedback.py",
        "step4_resonance.py",
        "step5_replication.py",
        "step6_pruning.py"
    ],
    "data": [
        "node_state.json",
        "synergy_attrs.json"
    ],
    "logs": [
        "fryng_actions.log",
        "node_updates.log"
    ],
    "ui_core": [
        # typical UI scripts
        "main_ui.py",
        "fryng_gui.py",
        "fryng_controls.py",
        "fryng_debug.py",
        "fryng_hex.py",
        "fryng_visuals.py",
        "fryng_events.py",
        "fryng_config.json",
        "README.md"
    ],

    # Now define fryng_core/ as one giant subfolder inside node/
    "fryng_core": [
        # We'll store expansions, foundation, stories, docs, seeds, tune, synergy etc. inside here
        "expansions/",       # put expansions inside
        "foundation/",       # foundation
        "stories/",          # stories
        "docs/",             # docs
        "seeds/",            # seeds subfolder
        "tune/",             # tune subfolder
        "fryng.flow",        # synergy blueprint
        "synergy_utils.doc", # synergy logic doc
        "version.log"        # version log
    ],

    # expansions under fryng_core/expansions
    "fryng_core/expansions": [
        "01_Potential.step",
        "02_Symmetry.step",
        "03_Flow.step",
        "04_Connectivity.step",
        "05_Emergence.step",
        "06_Recursion.step",
        "expansions.task",
        "expansions.log"
    ],

    # foundation under fryng_core/foundation
    "fryng_core/foundation": [
        "cosmic.axis",
        "default.span",
        "fryng.law",
        "readme.doc"
    ],

    # stories under fryng_core/stories
    "fryng_core/stories": [
        "realms/",
        "cultures/",
        "characters/",
        "scenes/"
    ],
    # subfolders in stories
    "fryng_core/stories/realms": [
        "auralis.realm",
        "sylph.realm"
    ],
    "fryng_core/stories/cultures": [
        "forest_tribe.cult",
        "desert_folk.cult"
    ],
    "fryng_core/stories/characters": [
        "hero.char",
        "mentor.char"
    ],
    "fryng_core/stories/scenes": [
        "scene1.scribe"
    ],

    # docs under fryng_core/docs
    "fryng_core/docs": [
        "design_philosophy.md",
        "usage_instructions.md",
        "version_logs/"
    ],
    "fryng_core/docs/version_logs": [
        # e.g. "changelog_1.0.txt" if you like
    ],

    # seeds and tune subfolders
    "fryng_core/seeds": [
        "default.seed"
    ],
    "fryng_core/tune": [
        "exponential.tune",
        "logistic.tune",
        "polynomial.tune"
    ]
}


def create_dirs_and_files(base_folder: str, structure: dict):
    """
    Creates the directory 'base_folder' if needed, then iterates over 'structure' to
    build subfolders/files inside it. 'structure' is a dict:
      key: subfolder path relative to base_folder ("" means top-level in base_folder)
      value: list of items (files or subfolders).
    """
    if not os.path.exists(base_folder):
        os.makedirs(base_folder)
        print(f"Created main folder: {base_folder}")
    else:
        print(f"Folder already exists: {base_folder}")

    # Now iterate each subfolder or top-level definition:
    for folder_rel, items in structure.items():
        # If folder_rel is "", that means place items in base_folder directly.
        if folder_rel == "":
            current_folder_abs = base_folder
        else:
            current_folder_abs = os.path.join(base_folder, folder_rel)

        # ensure the folder
        if not os.path.exists(current_folder_abs):
            os.makedirs(current_folder_abs, exist_ok=True)
            print(f"  Created directory: {current_folder_abs}")
        else:
            print(f"  Directory already exists: {current_folder_abs}")

        # Now create or ensure the items
        for item in items:
            if item.endswith("/"):
                # subfolder
                subfolder_abs = os.path.join(current_folder_abs, item)
                if not os.path.exists(subfolder_abs):
                    os.makedirs(subfolder_abs, exist_ok=True)
                    print(f"    Created sub-directory: {subfolder_abs}")
                else:
                    print(f"    Sub-directory already exists: {subfolder_abs}")
            else:
                # file
                file_abs = os.path.join(current_folder_abs, item)
                if not os.path.exists(file_abs):
                    with open(file_abs, "w", encoding="utf-8") as f:
                        f.write(f"# Placeholder for {item}\n")
                    print(f"    Created file: {file_abs}")
                else:
                    print(f"    File already exists: {file_abs}")


def main():
    # We'll create a top-level "node" folder.
    # Then place everything inside it as specified by NODE_STRUCTURE.
    node_folder = NODE_FOLDER
    print(f"\n=== Generating multi-core structure inside '{node_folder}/' ===\n")

    create_dirs_and_files(node_folder, NODE_STRUCTURE)

    print("\nAll set! The 'node' folder now has subfolders:\n"
          "    fryng_core/ (with expansions,foundation,stories,docs,seeds,tune,...)\n"
          " plus 'steps', 'data', 'logs', 'ui_core' at the top level if defined,\n"
          " each with placeholders. Enjoy your fractal synergy!\n")


if __name__ == "__main__":
    main()
