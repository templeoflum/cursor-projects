import os

def create_node_structure():
    """Creates the node file structure with six steps and init files."""

    base_dir = "."  # Current directory
    node_dir = "node"

    # Create the "node" directory
    os.makedirs(os.path.join(base_dir, node_dir), exist_ok=True)
    print(f"Created directory: {os.path.join(base_dir, node_dir)}")

    # Create six step directories and init files
    steps = [
        "01_Potential",
        "02_Symmetry",
        "03_Flow",
        "04_Connectivity",
        "05_Emergence",
        "06_Recursion"
    ]

    for step in steps:
        step_dir = os.path.join(node_dir, step)
        full_step_dir = os.path.join(base_dir, step_dir)
        os.makedirs(full_step_dir, exist_ok=True)
        print(f"Created directory: {full_step_dir}")

        # Create "init" file in each step directory
        init_file = os.path.join(step_dir, "init")
        full_init_file = os.path.join(base_dir, init_file)
        with open(full_init_file, "w") as f:
            f.write(f"# init file for {step}")
        print(f"Created file: {full_init_file}")

    print("Node file structure and init files created successfully.")


if __name__ == "__main__":
    create_node_structure()