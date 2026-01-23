
import os

def build_six_step_node():
    """
    Creates a minimal 'node' folder with 6 subfolders:
    01_Potential, 02_Symmetry, 03_Flow, 04_Connectivity, 05_Emergence, 06_Recursion.
    Each subfolder gets a small 'init' file.
    """
    base_dir = "."
    node_dir = os.path.join(base_dir, "node")
    os.makedirs(node_dir, exist_ok=True)
    print(f"[build_node] Created/ensured node folder: {node_dir}")

    step_names = [
        "01_Potential",
        "02_Symmetry",
        "03_Flow",
        "04_Connectivity",
        "05_Emergence",
        "06_Recursion"
    ]

    for step in step_names:
        step_path = os.path.join(node_dir, step)
        os.makedirs(step_path, exist_ok=True)
        print(f"[build_node] Created/ensured step folder: {step_path}")

        init_file = os.path.join(step_path, "init")
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                f.write(f"# minimal placeholder for {step}\n")
            print(f"[build_node] Created {init_file}")

    print("[build_node] 6-step node structure built successfully.")

if __name__ == "__main__":
    build_six_step_node()
