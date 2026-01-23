import os
import yaml
import math

def refine_init_files():
    """Alters init files to fit their respective step categories with dynamic attributes."""

    base_dir = "."
    node_dir = "node"

    # Define base attributes with default of 0.5
    default_attributes = {
        "potential": 0.5,
        "symmetry": 0.5,
        "flow": 0.5,
        "connectivity": 0.5,
        "emergence": 0.5,
        "recursion": 0.5,
         "alignment": 0.5,
        "vibration": 0.5,
        "polarity": 0.5,
         "rhythm": 0.5,
         "energy": 0.5,
        "axis": 0.5,
        "tension": 0.5,
        "coherence": 0.5,
    }

    # Rules for dynamic attribute population
    step_rules = {
        "01_Potential": {
            "dynamic_attributes": {
                "potential": 0.6,  # Slight offset for exploration
                "energy": 0.7, # High initial energy
                 "polarity": 0.5 + math.cos(math.pi / 3) * 0.2, #Polarity
                 "vibration": 0.5 + math.sin(math.pi / 3) * 0.2, #Vibration
                "axis": 0.5,
            },
            "tuning": {
                 "file": "potential.tune",
                 "mode": "potential"
            }
        },
        "02_Symmetry": {
             "dynamic_attributes": {
                "symmetry": 0.7,   # Higher symmetry emphasis
                "alignment": 0.6, #Higher focus on symmetry
                 "tension": 0.5 - math.cos(math.pi / 3) * 0.2, #Tension
                 "coherence": 0.5 + math.sin(math.pi / 3) * 0.2, #Coherence
                 "axis": 0.5 + math.sin(math.pi/5) * 0.1 #Axis
                },
            "tuning": {
                 "file": "symmetry.tune",
                 "mode": "symmetry"
            }
        },
        "03_Flow": {
            "dynamic_attributes": {
                "flow": 0.8, #High emphasis on flow
                "energy": 0.4,
                "vibration": 0.5 + math.sin(math.pi / 6) * 0.3,
               "rhythm": 0.5 + math.cos(math.pi / 6) * 0.3, #Flow has a rhythm and vibration
                 "axis": 0.5
            },
            "tuning": {
                 "file": "flow.tune",
                 "mode": "flow"
            }
        },
        "04_Connectivity": {
            "dynamic_attributes": {
                 "connectivity": 0.7, #Higher emphasis on connectivity
                "alignment": 0.6,
                 "tension": 0.5 + math.cos(math.pi / 4) * 0.2, #tension in connectivity
                 "coherence": 0.5 - math.sin(math.pi / 4) * 0.2,
                "axis": 0.5
            },
            "tuning": {
                 "file": "connectivity.tune",
                 "mode": "connectivity"
            }
        },
        "05_Emergence": {
            "dynamic_attributes": {
               "emergence": 0.7, #High emphasis on emergence
                "rhythm": 0.6,
                "vibration": 0.6,
                 "polarity": 0.5 + math.cos(math.pi / 5) * 0.3,
                 "energy": 0.5 + math.sin(math.pi / 5) * 0.3, #energy coming from new insights
                 "axis": 0.5 + math.sin(math.pi/3)*0.1 #axis of emergence
            },
             "tuning": {
                 "file": "emergence.tune",
                 "mode": "emergence"
            }
        },
        "06_Recursion": {
            "dynamic_attributes": {
                "recursion": 0.6, #moderate recursion emphasis
                  "vibration": 0.5 - math.cos(math.pi / 5) * 0.2,
               "rhythm": 0.5 - math.sin(math.pi / 5) * 0.2,
              "tension": 0.5,
               "coherence": 0.5,
                "axis": 0.5 + math.cos(math.pi/5) * 0.1 #axis of the recursion
            },
            "tuning": {
                 "file": "recursion.tune",
                 "mode": "recursion"
            }
        }
    }

    # Search for init files and apply rules
    for root, _, files in os.walk(os.path.join(base_dir, node_dir)):
        for file in files:
            if file == "init":
                full_init_file = os.path.join(root, file)
                step_name = os.path.basename(root)
                if step_name in step_rules:
                    try:
                       with open(full_init_file, 'r') as f:
                          data = yaml.safe_load(f)
                          if not data:
                              data = {} #Initialize an empty dict if nothing there

                       # Ensure dynamic_attributes and tuning sections exist
                       data.setdefault("dynamic_attributes", {})
                       data.setdefault("tuning", {})


                       # Apply rules from step_rules
                       step_data = step_rules[step_name]

                       for attr, value in step_data.get("dynamic_attributes", {}).items():
                            data["dynamic_attributes"][attr] = value
                       for attr, value in step_data.get("tuning", {}).items():
                             data["tuning"][attr] = value



                       with open(full_init_file, 'w') as f:
                            yaml.dump(data, f, default_flow_style=False)
                       print(f"Refined: {full_init_file} based on {step_name}")
                    except yaml.YAMLError:
                        print(f"Warning: Could not load {full_init_file} as YAML")


    print("init files refined with dynamic attributes and tuning successfully.")


if __name__ == "__main__":
    refine_init_files()