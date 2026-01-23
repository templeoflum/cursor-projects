import os
import yaml
import glob
import sys

def get_user_input(prompt):
    """Reads characters from stdin until a number or enter is detected."""
    print(prompt, end="", flush=True)  # Keep prompt on the same line and show now
    input_buffer = ""
    while True:
        char = sys.stdin.read(1) #read input character by character
        if char == '\n': #check for endline
            return input_buffer.strip()
        if char.isdigit(): #if digit is entered add to buffer
           input_buffer += char
        elif char != '' and char !='\r': # if any other character is entered let user know it must be a number and reset buffer
            print (f"\nInput must be a digit. Please try again:")
            input_buffer = ""
        if len(input_buffer) > 3:
            print(f"\nInput limited to 3 digits. Please try again:")
            input_buffer = "" # limit input to 3 char to stop extreme number errors
        continue # continue if not enter, or digit


def select_files_for_steps():
    """Allows users to select files for each step via the console and prints the selections."""

    base_dir = "."
    node_dir = "node"
    steps = ["01_Potential", "02_Symmetry", "03_Flow", "04_Connectivity", "05_Emergence", "06_Recursion"]
    file_types = {
        "01_Potential": {
            "Seed/Law": ["fn.xx.law"],
            "Energy/Dynamics": ["fn.xx.dyn"]
        },
         "02_Symmetry": {
            "Constraints/Resonance": ["im.xx.pol", "ap.xx.reso"],
             "Tuning/Harmony": ["im.xx.vib", "ap.xx.tun"]
        },
        "03_Flow": {
            "Expansion/Logic": ["im.xx.flw", "im.xx.rhy"],
            "Transformation/Rule": ["im.xx.convert", "im.xx.update"]
        },
        "04_Connectivity": {
           "Bridging/Rule": ["im.xx.bridge", "im.xx.rule"],
           "Style/Mapping": ["im.xx.atm", "im.xx.cha"]
        },
         "05_Emergence": {
           "Synthesis/Design": ["ex.xx.syn", "ds.xx.sheet"],
             "Insights/Utility": ["ex.xx.utl", "ex.xx.per"]
        },
         "06_Recursion": {
            "Feedback": ["ex.xx.feedback", "ap.xx.reso"],
            "Control": ["im.xx.clk", "im.xx.rnd", "ex.xx.size"]
        }

    }

    available_files = {}
    #Gather all files
    for step in steps:
        available_files[step] = {}
        step_dir = os.path.join(base_dir, node_dir, step)
        for sub_step, types in file_types[step].items():
            available_files[step][sub_step] = []
            for file_type in types:
                available_files[step][sub_step].extend(glob.glob(os.path.join(step_dir, f"*{file_type}")))

    # Display all available files for each step
    print("--- Available Files ---")
    for step in steps:
        print(f"\n-- {step} --")
        for sub_step, files in available_files[step].items():
           if files:
            print (f"  {sub_step}:")
            for i, file in enumerate(files):
                print (f"     {i + 1}. {file}")
           else:
                print (f"    {sub_step}: No files available")


    selected_files = {}
    # Collect user input for each step with a single selection prompt per step
    for step in steps:
        print(f"\n--- {step} Selection ---")
        selected_files[step] = {}
        step_files = available_files[step]

        for sub_step, files in step_files.items():
            while True:
                if not files:
                    print (f"  {sub_step}: No files available, skipping selection")
                    selected_files[step][sub_step] = None
                    break
                else:
                    choice = get_user_input(f"Select file for {sub_step} (1-{len(files)}) or leave blank for none : ")
                    if not choice:
                        selected_files[step][sub_step] = None
                        print(f"  {sub_step}: No file selected")
                        break
                    try:
                        choice = int(choice)
                        if 1 <= choice <= len(files):
                            selected_files[step][sub_step] = files[choice - 1]
                            print (f"  {sub_step}: {files[choice - 1]}")
                            break
                        else:
                            print("Invalid choice. Please try again.")
                    except ValueError:
                        print("Invalid input. Please enter a number.")

    print("\n--- Final Selected Files ---")
    for step, sub_steps in selected_files.items():
        print(f"\n-- {step} --")
        for sub_step, file_path in sub_steps.items():
            print(f"   {sub_step}: {file_path if file_path else 'None'}")

    return selected_files



def refine_init_files():
    """Refines 'init' files with file references based on user selections."""

    base_dir = "."
    node_dir = "node"
    selected_files = select_files_for_steps()

    # Search for init files and update with selected file paths
    for root, _, files in os.walk(os.path.join(base_dir, node_dir)):
        for file in files:
            if file == "init":
                full_init_file = os.path.join(root, file)
                step_name = os.path.basename(root)
                if step_name in selected_files:
                   try:
                      with open(full_init_file, 'r') as f:
                            data = yaml.safe_load(f)
                            if not data:
                                data = {}  # Initialize an empty dictionary if no data
                      # Ensure "dynamic_attributes" and "tuning" sections exist
                      data.setdefault("dynamic_attributes", {})
                      data.setdefault("tuning", {})

                       # Add the selected files to reso template
                      step_files = selected_files[step_name]
                      for sub_step, file_path in step_files.items():
                            if file_path:
                                if "Seed" in sub_step or "Energy" in sub_step:
                                  if "dynamic_attributes" not in data:
                                    data["dynamic_attributes"] = {}
                                  data["dynamic_attributes"]["source"] = file_path
                                if "Constraints" in sub_step or "Tuning" in sub_step:
                                   if "tuning" not in data:
                                     data["tuning"] = {}
                                   data["tuning"]["file"] = file_path
                                if "Expansion" in sub_step or "Transformation" in sub_step:
                                     if "expansion" not in data:
                                          data["expansion"] = {}
                                     data["expansion"]["file"] = file_path
                                if "Bridging" in sub_step or "Style" in sub_step:
                                   if "connectivity" not in data:
                                       data["connectivity"] = {}
                                   data["connectivity"]["file"] = file_path
                                if "Synthesis" in sub_step or "Insights" in sub_step:
                                   if "emergence" not in data:
                                       data["emergence"] = {}
                                   data["emergence"]["file"] = file_path
                                if "Feedback" in sub_step or "Control" in sub_step:
                                   if "recursion" not in data:
                                      data["recursion"] = {}
                                   data["recursion"]["file"] = file_path

                      with open(full_init_file, 'w') as f:
                          yaml.dump(data, f, default_flow_style=False)
                      print(f"Refined: {full_init_file} with selected file paths")


                   except yaml.YAMLError:
                        print(f"Warning: Could not load {full_init_file} as YAML")

    print("init files refined with selected file paths successfully.")


if __name__ == "__main__":
    refine_init_files()