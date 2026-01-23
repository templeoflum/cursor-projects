import os

def create_seed_structure():
    """Creates the precise Synph file structure with steps, init files, and templates."""

    base_dir = "."
    node_dir = "node"
    templates_dir = os.path.join(node_dir, "templates")

    modules = {
        "el": "ElFoundation",
        "ua": "UniverseArchitect",
        "sc": "StoryComposer",
        "sd": "SensoryDesigner",
        "cd": "CharacterDesigner",
        "pm": "PromptManagementSystem",
        "ft": "FeedbackTestingSystem",
        "se": "SynthesisEngine",
        "io": "LiveInputOutputSystem",
        "pd": "PerformanceDirector",
        "rc": "RealTimeControlSystem",
        "dy": "DynamicSynthesis",
        "fi": "FeedbackLoopIntegrator",
        "dc": "DynamicCollaborationLayer",
        "tm": "TemporalModulation",
        "xd": "CrossDomainSystems",
        "ud": "UniversalDynamicFramework",
        "ir": "InteractiveResonanceEngine",
        "xx": "General",
        "gen": "General"
    }

    categories = {
        "fn": "foundation",
        "ap": "application",
        "im": "implementation",
        "ex": "execution",
        "ds": "design",
    }
    steps = ["01_Potential", "02_Symmetry", "03_Flow", "04_Connectivity", "05_Emergence", "06_Recursion"]

    # Create the "node" directory
    os.makedirs(os.path.join(base_dir, node_dir), exist_ok=True)
    print(f"Created directory: {os.path.join(base_dir, node_dir)}")

    # Create the "templates" directory
    os.makedirs(os.path.join(base_dir, templates_dir), exist_ok=True)
    print(f"Created directory: {os.path.join(base_dir, templates_dir)}")

    # Create template folders for each step and their init files
    for step in steps:
        step_template_dir = os.path.join(templates_dir, step)
        full_template_dir = os.path.join(base_dir, step_template_dir)
        os.makedirs(full_template_dir, exist_ok=True)
        init_file = os.path.join(step_template_dir, "init")
        full_init_file = os.path.join(base_dir, init_file)
        with open(full_init_file, "w") as f:
            f.write(f"# init file for template of {step}")
        print(f"Created template init file: {full_init_file}")


    # Create the 6 step directories, and category files in each of them
    for step in steps:
        step_dir = os.path.join(node_dir, step)
        full_step_dir = os.path.join(base_dir, step_dir)
        os.makedirs(full_step_dir, exist_ok=True)
        print(f"Created directory: {full_step_dir}")

        init_file = os.path.join(step_dir, "init")
        full_init_file = os.path.join(base_dir, init_file)
        with open(full_init_file, "w") as f:
            f.write(f"# init file for {step}")
        print(f"Created file: {full_init_file}")



        if step == "01_Potential":
            files = ["fn.xx.law", "fn.xx.dyn", "fn.xx.tag", "fn.xx.seed", "fn.xx.chr", "fn.xx.spn", "fn.xx.ene", "fn.xx.type", "fn.xx.explore"]
        elif step == "02_Symmetry":
            files = ["im.xx.pol", "im.xx.vib", "im.xx.align", "im.xx.cau", "im.xx.eff", "im.xx.text", "im.xx.lgt", "im.xx.snd",  "im.xx.formalize",  "im.xx.prob"]
        elif step == "03_Flow":
           files = ["im.xx.rhy", "im.xx.pls", "im.xx.bre", "im.xx.pace", "im.xx.cycle", "im.xx.spd", "im.xx.roll",  "im.xx.grn", "im.xx.flw","im.xx.convert", "im.xx.update"]
        elif step == "04_Connectivity":
            files = ["im.xx.convert", "im.xx.line", "im.xx.rule", "im.xx.frm", "im.xx.atm",  "im.xx.cha", "im.xx.add", "im.xx.divide",  "im.xx.mlt", "im.xx.key", "im.xx.cha", "im.xx.rlg", "im.xx.bridge"]
        elif step == "05_Emergence":
           files = [ "ex.xx.sty",  "ex.xx.modulate", "ex.xx.automate",  "ex.xx.glitch", "ex.xx.syn", "ex.xx.utl", "ex.xx.glt", "ex.xx.distill", "ex.xx.msh","ex.xx.per",  "ex.xx.seq",  "ex.xx.question"]
        elif step == "06_Recursion":
           files = ["ap.xx.reso", "ap.xx.tun",  "im.xx.clk",  "im.xx.rnd", "ex.xx.distill","ex.xx.fx",  "ex.xx.feedback", "ex.xx.cog","ex.xx.form", "ex.xx.seq", "ex.xx.size" ]

        for file_name in files:
            full_file_path = os.path.join(base_dir, step_dir, file_name)
            with open(full_file_path, "w") as f:
               f.write(f"# {file_name}")
            print(f"Created file: {full_file_path}")


    print("Seed file structure and init files created successfully.")



if __name__ == "__main__":
    create_seed_structure()