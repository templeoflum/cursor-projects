#!/usr/bin/env python3
import os
import sys

# ---------------------------------------------------------------------------
# If you want a different top-level folder name, change BASE_DIR here:
# ---------------------------------------------------------------------------
BASE_DIR = "node"

# ---------------------------------------------------------------------------
# Minimal structure with synergy placeholders:
#  - For JavaScript files, we use "//" markers to avoid Babel parse errors.
#  - For Python synergy files, we use "# FRACTAL_INSERT_MARKER".
#  - We create just enough so that connect/focus/participate scripts can run next.
# ---------------------------------------------------------------------------
PROJECT_STRUCTURE = {
    "": [
        ("README.md", "# Node Project\n\nCreated by build.py."),
        ("LICENSE", "MIT License Placeholder"),
        (".gitignore", "# Add files and directories to ignore\n"),
        ("Dockerfile", "# Basic Dockerfile placeholder\n"),
        ("requirements.txt", "# Global Python dependencies (optional)\n"),
        ("package.json", "{\n  \"name\": \"node-project\",\n  \"version\": \"1.0.0\"\n}\n"),
    ],
    "docs": [
        ("architecture.md", "# System Architecture\n\nPlaceholder."),
        ("user-guide.md", "# User Guide\n\nPlaceholder."),
        ("api-documentation.md", "# API Documentation\n\nPlaceholder.")
    ],
    "config": {
        "default": [
            ("fryng-core.yaml", "fryng-core:\n  default-coefficient: 0.5\n"),
            ("ui-core.yaml", "ui-core:\n  theme: default\n"),
            ("performance.yaml", "performance:\n  initial-tempo: 120\n")
        ],
        "environments": [
            ("development.yaml", "# Dev environment config"),
            ("staging.yaml", "# Staging environment config"),
            ("production.yaml", "# Production environment config")
        ]
    },
    "src": {
        "fryng-core": {
            "src": [
                ("__init__.py", "# __init__ for fryng-core\n"),
                ("fractal_logic.py", "# FRACTAL_INSERT_MARKER\n"),
                ("feedback_loops.py", "# FRACTAL_INSERT_MARKER\n"),
                ("steps.py", "# FRACTAL_INSERT_MARKER\n"),
            ],
            "tests": [
                ("test_fractal_logic.py", "# Placeholder test\n"),
                ("test_feedback_loops.py", "# Placeholder test\n"),
                ("test_steps.py", "# Placeholder test\n")
            ],
            "": [
                ("requirements.txt", "# Python deps for Fryng Core\n"),
                ("README.md", "# Fryng Core\n\nPlaceholder for fractal synergy logic.")
            ]
        },
        "ui-core": {
            "public": {
                "assets": {
                    "styles": [],
                    "images": []
                },
                "": [
                    # Basic index.html with <div id="root"></div> so React can mount
                    ("index.html", """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Synergy App</title>
</head>
<body>
  <!-- React will mount here -->
  <div id="root"></div>
</body>
</html>
""")
                ]
            },
            "src": {
                "components": [],
                "hooks": [],
                "services": [],
                "": [
                    # We use valid JS comment markers to avoid Babel syntax errors
                    ("index.js", "// UI_INDEX_MARKER\n"),
                    ("App.js", "// UI_INSERT_MARKER\n")
                ]
            },
            "tests": [],
            "": [
                # Minimal React-based package.json with a "start" script
                ("package.json", """{
  "name": "ui-core",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start"
  }
}
"""),
                ("README.md", "# UI Core\n\nPlaceholder for UI synergy.")
            ]
        },
        "live-performance-integration": {
            "src": [
                ("__init__.py", ""),
                ("performance_engine.py", "# Placeholder for performance engine\n"),
                ("integration_module.py", "# Placeholder for performance integration\n")
            ],
            "tests": [
                ("test_performance_engine.py", "# Placeholder test\n"),
                ("test_integration_module.py", "# Placeholder test\n")
            ],
            "": [
                ("requirements.txt", "# Python deps for live performance\n"),
                ("README.md", "# Live Performance Integration\nPlaceholder.")
            ]
        },
        "api": {
            "src": {
                "": [
                    ("__init__.py", "# __init__ for API\n"),
                    ("main.py", "# Placeholder main\n"),
                    ("utils.py", "# Placeholder utils\n")
                ],
                "endpoints": [
                    ("fryng_core.py", "# Placeholder for Fryng Core endpoints\n"),
                    ("ui_core.py", "# Placeholder for UI Core endpoints\n"),
                    ("performance_integration.py", "# Placeholder for performance integration endpoints\n")
                ]
            },
            "tests": [
                ("test_fryng_core.py", "# Placeholder test\n"),
                ("test_ui_core.py", "# Placeholder test\n"),
                ("test_performance_integration.py", "# Placeholder test\n")
            ],
            "": [
                ("requirements.txt", "# Python deps for API\n"),
                ("README.md", "# API\n\nPlaceholder for API logic.")
            ]
        },
        "common": {
            "utils": [
                ("logger.py", "# Placeholder logger\n"),
                ("config_loader.py", "# Placeholder config loader\n"),
                ("helpers.js", "// Placeholder JS helpers\n")
            ],
            "schemas": [
                ("node_schema.json", "{ \"$schema\": \"http://json-schema.org/draft-07/schema\" }\n"),
                ("event_schema.json", "{ \"$schema\": \"http://json-schema.org/draft-07/schema\" }\n")
            ],
            "libraries": [
                ("fractal_algorithms.py", "# Placeholder fractal algorithms\n"),
                ("transformation_functions.js", "// Placeholder transformations\n")
            ]
        }
    },
    "scripts": {
        "maintenance": [
            ("backup.sh", "#!/usr/bin/env bash\n# Backup script placeholder\n"),
            ("restore.sh", "#!/usr/bin/env bash\n# Restore script placeholder\n")
        ],
        "": [
            ("setup.sh", "#!/usr/bin/env bash\n# Setup script placeholder\n"),
            ("deploy.sh", "#!/usr/bin/env bash\n# Deploy script placeholder\n")
        ]
    },
    "databases": {
        "seed_data": [
            ("initial_nodes.json", "[ { \"id\": 1, \"type\": \"seed\" } ]"),
            ("transformations.json", "[ { \"name\": \"default_transformation\", \"params\": {} } ]")
        ],
        "": [
            ("schema.sql", "-- SQL schema placeholder\n")
        ]
    },
    "logs": [
        ("fryng-core.log", ""),
        ("ui-core.log", ""),
        ("performance.log", ""),
        ("api.log", "")
    ],
    "tests": {
        "integration": [],
        "end-to-end": []
    }
}


def create_structure(base_path, structure):
    """
    Recursively creates directories and files based on 'structure'.
    If an item is a tuple (file_name, file_content), we create a file with that content.
    If an item is a plain string, we create an empty file.
    If an item is a dict, the key is a folder name and the value is another structure.
    """
    if isinstance(structure, list):
        # It's a list of items (files or file tuples)
        for item in structure:
            if isinstance(item, tuple):
                file_name, file_content = item
                file_path = os.path.join(base_path, file_name)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(file_content)
                print(f"Created file: {file_path}")
            else:
                # Create empty file
                file_path = os.path.join(base_path, item)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("")
                print(f"Created empty file: {file_path}")
        return

    if isinstance(structure, dict):
        # It's a dict: keys are folder names, values are sub-structures
        for folder_name, contents in structure.items():
            if folder_name == "":
                # Means these items belong directly in the current 'base_path'
                create_structure(base_path, contents)
            else:
                # Create subdirectory
                new_dir_path = os.path.join(base_path, folder_name)
                os.makedirs(new_dir_path, exist_ok=True)
                print(f"Created directory: {new_dir_path}")
                create_structure(new_dir_path, contents)


def main():
    """
    Main function that:
    1. Creates or reuses a folder named 'node/'.
    2. Builds the minimal structure with synergy placeholders:
       - # FRACTAL_INSERT_MARKER for Python
       - // UI_INDEX_MARKER, // UI_INSERT_MARKER for JS
       - Basic package.json for ui-core with a "start" script
       - Enough placeholders for subsequent connect/focus/participate steps.
    """
    if len(sys.argv) > 1:
        chosen_dir = sys.argv[1]
    else:
        chosen_dir = BASE_DIR

    base_path = os.path.abspath(chosen_dir)
    os.makedirs(base_path, exist_ok=True)
    print(f"Created or reused main project directory: {base_path}")

    create_structure(base_path, PROJECT_STRUCTURE)

    print("\nBuild script complete. Your 'node/' folder now has the minimal structure with synergy placeholders.")
    print("You can proceed with connect/focus/participate scripts as needed.")


if __name__ == "__main__":
    main()
