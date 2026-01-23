
"""
update_files.py
----------------------------------------------------------------------
Overwrites each step's main init.* file AND any expansions in expansions/
subfolder with new placeholder content. We have two sets of content:

1) MAIN_FILE_TEMPLATE: For the 'init.*' file (includes a YAML snippet referencing synergy).
2) EXPANSION_FILE_TEMPLATE: For expansions placeholder with minimal synergy instructions or references.

Usage:
  python update_files.py

Caution:
  This forcibly overwrites the content of each file it finds that matches
  the known patterns. Ensure you have backups or are comfortable overwriting.
----------------------------------------------------------------------
"""

import os

# Mapping of step folder => step name for synergy placeholders
STEP_INFO = {
    "01_Potential": "Potential",
    "02_Symmetry": "Symmetry",
    "03_Flow": "Flow",
    "04_Connectivity": "Connectivity",
    "05_Emergence": "Emergence",
    "06_Recursion": "Recursion",
}

# 1) The snippet for each main init.* file
# referencing your universal .reso template, synergy measures, etc.
MAIN_FILE_TEMPLATE = """version: 1.0
inheritsFrom:
  - "../../synergy_core/universal_template.reso"

meta:
  stepName: "{stepName}"
  synergyMeasure: "E_total"

dynamic_references:
  expansions: false
  offset_range: "-0.05 to 0.05"

workflow_instructions:
  onLoad:
    - "If synergy < 0.6, remain minimal seed"
  onComplete:
    - "If expansions not used, finalize {stepName}"
"""

# 2) The snippet for expansions in expansions/ subfolder
# could be the same for every expansions file, or slightly different.
EXPANSION_FILE_TEMPLATE = """# expansions file for step: {stepName}
# This is an advanced expansions placeholder for synergy above threshold.
# Overwrite or merge as needed.

expansion_logic:
  synergy_override: false
  offset_range: "-0.1 to 0.1"
  notes:
    - "Adjust expansions if synergy measure > 0.6"
"""

def find_step_dirs(base_dir="steps"):
    """
    Finds directories named 01_Potential, 02_Symmetry, etc. matching STEP_INFO keys.
    Returns a list of (folder_name, step_path).
    """
    results = []
    if not os.path.isdir(base_dir):
        print(f"No '{base_dir}' directory found. Exiting.")
        return results

    for item in os.listdir(base_dir):
        step_dir = os.path.join(base_dir, item)
        if os.path.isdir(step_dir) and item in STEP_INFO:
            # e.g. '01_Potential'
            results.append((item, step_dir))
    return results

def find_init_file(step_dir):
    """
    Finds exactly one 'init.' file in step_dir. If multiple or none, we skip to avoid confusion.
    """
    init_files = []
    for fname in os.listdir(step_dir):
        if fname.startswith("init.") and not os.path.isdir(os.path.join(step_dir, fname)):
            init_files.append(fname)

    if len(init_files) == 1:
        return init_files[0]
    elif len(init_files) == 0:
        print(f"[WARNING] No init.* found in {step_dir}, skipping main file overwrite.")
        return None
    else:
        print(f"[WARNING] Multiple init.* found in {step_dir}: {init_files}, skipping main file to avoid confusion.")
        return None

def get_expansion_files(exp_dir):
    """
    Returns all filenames in expansions/ subfolder that are not directories.
    """
    expansions = []
    if not os.path.isdir(exp_dir):
        return expansions

    for fname in os.listdir(exp_dir):
        fpath = os.path.join(exp_dir, fname)
        if os.path.isfile(fpath):
            expansions.append(fname)
    return expansions

def overwrite_file(file_path, content):
    """
    Overwrites a file with the provided content.
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[OVERWRITE] {file_path}")

def main():
    steps_list = find_step_dirs(base_dir="steps")
    if not steps_list:
        return

    for folder_name, step_path in steps_list:
        step_name = STEP_INFO[folder_name]

        # 1) Overwrite main init.* file
        init_fname = find_init_file(step_path)
        if init_fname:
            file_path = os.path.join(step_path, init_fname)
            main_content = MAIN_FILE_TEMPLATE.format(stepName=step_name)
            overwrite_file(file_path, main_content)

        # 2) Overwrite expansions
        expansions_dir = os.path.join(step_path, "expansions")
        if os.path.isdir(expansions_dir):
            expansions_files = get_expansion_files(expansions_dir)
            for exp_fname in expansions_files:
                exp_path = os.path.join(expansions_dir, exp_fname)
                expansions_content = EXPANSION_FILE_TEMPLATE.format(stepName=step_name)
                overwrite_file(exp_path, expansions_content)
        else:
            print(f"[INFO] No expansions/ folder found in {step_path}")

    print("\nUpdate process complete!")
    print("All init.* and expansions in recognized steps subfolders have been overwritten.\n")

if __name__ == "__main__":
    main()
