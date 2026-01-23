import os
import yaml

def populate_init_files():
    """Populates 'init' files with a default .reso template equivalent."""

    base_dir = "."
    node_dir = "node"

    # Define a basic .reso template
    reso_template = {
        "version": "1.0",
        "name": "Default Node Init",
        "stepNumber": None,  # will be dynamically set
        "universeID": "Universal",
        "inheritsFrom": "archetype-default",
        "relationships": [
            {
                "type": "supports",
                "target": "laws-universal-001",
                "description": "Aligns with universal principles to explore balanced interactions in dynamic systems."
            }
        ],
        "author": "System Designer",
        "keywords": ["default", "framework", "dynamic", "balance"],
        "abstract": "This document provides a neutral baseline for dynamic systems, emphasizing adaptability and coherence.",
        "dynamic_attributes": {  # Place to add attributes dynamically
        },
         "tuning": {
            "file": None,
            "mode": "Default"
          },
        "purpose": "To establish a neutral baseline for exploring dynamic system interactions.",
        "values": ["Adaptability", "Stability", "Balance"],
        "scope": "Applicable to general workflows, design systems, and narrative frameworks.",
        "future_orientation": "This document serves as a foundation for future iterations and enhancements.",
        "lexicon": [
            {
                "concept": "Dynamic Balance",
                "description": "Maintaining equilibrium while enabling dynamic fluctuations in key attributes."
            }
        ],
        "patterns": [
            {
                "pattern": "Iterative Refinement",
                "description": "Enhancing outputs through repeated modulation of dynamic parameters."
            }
        ],
        "master_key": {
            "integrators": [
                {
                    "integrator": "Harmonic Flow",
                    "role": "Ensures alignment between dynamic attributes and system cycles."
                }
            ]
        },
        "text_narratives": [
            "Incorporate polarity shifts to create variation in tone and structure.",
            "Align narrative progression with rhythmic cycles for coherence."
        ],
        "visual_concepts": [
            "Balance creative-receptive dynamics in visual compositions.",
            "Adapt color palettes dynamically based on phase transitions."
        ],
         "interactive_design": [
            "Design systems that respond dynamically to user engagement, reflecting modulated values."
        ],
        "content": "The Default Dynamic Framework offers a neutral starting point for exploring dynamic systems. By integrating polarity, rhythm, and energy, it ensures a stable yet adaptable approach for general workflows and modular systems.",
          "implementation_strategies": [
            "Integrate dynamic attributes into core processes to ensure flexibility and balance.",
            "Use phase-driven modulation to adapt outputs to changing contexts."
        ],
        "related_items": [
            {
                "type": "inspired by",
                "target": "framework-universal-flow-001",
                "description": "Shares principles with foundational universal frameworks for dynamic systems."
            }
        ],
          "binary_attachments": [
            {
                "name": "Default Dynamics Diagram",
                "type": "image/png",
                "url": "https://example.com/default-dynamics-diagram.png"
            }
        ]
    }

    # Search for init files and populate
    for root, _, files in os.walk(os.path.join(base_dir, node_dir)):
        for file in files:
            if file == "init":
                full_init_file = os.path.join(root, file)
                step_name = os.path.basename(root)
                step_number = int(step_name.split("_")[0])
                reso_template["stepNumber"] = step_number

                with open(full_init_file, "w") as f:
                  yaml.dump(reso_template, f, default_flow_style=False)
                  print(f"Populated: {full_init_file}")


    print("init files populated with .reso template successfully.")

if __name__ == "__main__":
    populate_init_files()