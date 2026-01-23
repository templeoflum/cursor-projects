
"""
node.py
-------
Generates the "node" directory structure (as the top-level) and populates the Fryng architecture.
Run:
    python node.py

Creates directories and files under ./node/ as specified.
"""

import os

# Define the new architecture tree.
# Each key is a folder path (relative to ./node),
# and its value is a list of files or subfolders to create in that folder.
DIRECTORY_STRUCTURE = {
    "node/Fryng_Core": [
        "seeds/",        # subfolder
        "tune/",         # subfolder
        "synergy.flow",
        "synergy_utils.doc",
        "version.log"
    ],
    "node/Fryng_Core/seeds": [
        "default.seed"
    ],
    "node/Fryng_Core/tune": [
        "exponential.tune",
        "logistic.tune",
        "polynomial.tune"
    ],
    "node/Fryng_Foundation": [
        "universal.axis",
        "default.span",
        "cosmic.span",
        "readme.doc"
    ],
    "node/Fryng_Expanse": [
        "01_Potential.step",
        "02_Symmetry.step",
        "cosmic_unfolding.arc",
        "expand_realm.task",
        "synergy_paths.log"
    ],
    "node/Fryng_Stories": [
        "realm/",        # subfolder
        "culture/",      # subfolder
        "char/",         # subfolder
        "scene1.scribe"
    ],
    "node/Fryng_Stories/realm": [
        "auralis.realm",
        "sylph.realm"
    ],
    "node/Fryng_Stories/culture": [
        "forest_tribe.cult",
        "desert_folk.cult"
    ],
    "node/Fryng_Stories/char": [
        "hero.char",
        "mentor.char"
    ],
    "node/docs": [
        "design_philosophy.doc",
        "usage.how",
        "v1.0_arch.log"
    ]
}

def create_project_structure():
    """
    Creates directories and files based on DIRECTORY_STRUCTURE.
    Subfolders are indicated by a trailing slash in the list entries.
    Files are indicated by normal names.
    """
    for folder, contents in DIRECTORY_STRUCTURE.items():
        # Create the folder
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created directory: {folder}")
        else:
            print(f"Directory already exists: {folder}")

        # Create subfolders/files
        for item in contents:
            if item.endswith("/"):
                # It's a subfolder
                subfolder_path = os.path.join(folder, item)
                if not os.path.exists(subfolder_path):
                    os.makedirs(subfolder_path)
                    print(f"Created directory: {subfolder_path}")
                else:
                    print(f"Directory already exists: {subfolder_path}")
            else:
                # It's a file
                file_path = os.path.join(folder, item)
                if not os.path.exists(file_path):
                    with open(file_path, "w", encoding="utf-8") as f:
                        # Simple placeholder content
                        f.write(f"# Placeholder content for {item}\n")
                    print(f"Created file: {file_path}")
                else:
                    print(f"File already exists: {file_path}")

def main():
    create_project_structure()
    print("\nMinimal seed file tree generation complete!\n")
    print("Steps directory structure is ready for the fractal pilgrim's journey. 🚀")

if __name__ == "__main__":
    main()
