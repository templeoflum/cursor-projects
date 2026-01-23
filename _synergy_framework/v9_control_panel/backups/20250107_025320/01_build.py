import os
import sys
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, Any
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProjectBuilder:
    def __init__(self):
        self.base_dir = Path.cwd()
        self.node_dir = self.base_dir / "node"
        
        # Define core paths
        self.fryng_core_path = self.node_dir / "fryng-core"
        self.ui_core_path = self.node_dir / "ui-core"
        
        # Define initial config
        self.initial_config = {
            "project_dir": str(self.base_dir),
            "node_dir": str(self.node_dir),
            "fryng_core_path": str(self.fryng_core_path),
            "ui_core_path": str(self.ui_core_path),
            "version": "1.0.0"
        }

    def build(self) -> bool:
        """Main build process"""
        try:
            logger.info("Starting build process...")
            
            # Create main directories
            self._create_directory_structure()
            
            # Create configuration file
            self._create_config_file()
            
            # Initialize UI files
            self._initialize_ui_files()
            
            # Initialize core files
            self._initialize_core_files()
            
            logger.info("Build completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Build failed: {e}")
            return False

    def _create_directory_structure(self):
        """Create all necessary directories"""
        # Create main directories
        self.node_dir.mkdir(exist_ok=True)
        self.fryng_core_path.mkdir(exist_ok=True)
        self.ui_core_path.mkdir(exist_ok=True)
        
        # Create UI subdirectories
        (self.ui_core_path / "src").mkdir(exist_ok=True)
        (self.ui_core_path / "public").mkdir(exist_ok=True)
        (self.ui_core_path / "public" / "data").mkdir(exist_ok=True)
        
        # Create core subdirectories
        (self.fryng_core_path / "src").mkdir(exist_ok=True)
        (self.fryng_core_path / "tests").mkdir(exist_ok=True)

    def _create_config_file(self):
        """Create project configuration file"""
        config_path = self.node_dir / "project_config.json"
        with open(config_path, 'w') as f:
            json.dump(self.initial_config, f, indent=2)
        logger.info(f"Created config file at {config_path}")

    def _initialize_ui_files(self):
        """Initialize essential UI files"""
        try:
            # Create UI core directory
            self.ui_core_path.mkdir(parents=True, exist_ok=True)
            
            # Create package.json
            package_json = {
                "name": "fryng-ui",
                "version": "1.0.0",
                "private": True,
                "dependencies": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0",
                    "react-scripts": "5.0.1"
                },
                "scripts": {
                    "start": "react-scripts start",
                    "build": "react-scripts build"
                },
                "browserslist": {
                    "production": [
                        ">0.2%",
                        "not dead",
                        "not op_mini all"
                    ],
                    "development": [
                        "last 1 chrome version",
                        "last 1 firefox version",
                        "last 1 safari version"
                    ]
                }
            }
            
            with open(self.ui_core_path / "package.json", 'w') as f:
                json.dump(package_json, f, indent=2)
            
            # Create public directory
            public_dir = self.ui_core_path / "public"
            public_dir.mkdir(exist_ok=True)
            
            # Create src directory
            src_dir = self.ui_core_path / "src"
            src_dir.mkdir(exist_ok=True)
            
            # Create initial tuning config
            tuning_config = {
                "current_seed": 0.5,
                "min_value": 0.0,
                "max_value": 1.0
            }
            
            tuning_path = public_dir / "data"
            tuning_path.mkdir(exist_ok=True)
            with open(tuning_path / "tuning_config.json", 'w') as f:
                json.dump(tuning_config, f, indent=2)
            
            # Install dependencies using npm
            try:
                logger.info("Installing React dependencies...")
                os.chdir(self.ui_core_path)
                npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
                subprocess.run(
                    [npm_cmd, "install"],
                    check=True,
                    capture_output=True,
                    text=True
                )
                logger.info("React dependencies installed successfully")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install dependencies: {e.stdout}\n{e.stderr}")
                raise
            finally:
                os.chdir(self.base_dir)
            
        except Exception as e:
            logger.error(f"Failed to initialize UI files: {e}")
            raise

    def _initialize_core_files(self):
        """Initialize core Python files"""
        # Create __init__.py
        (self.fryng_core_path / "src" / "__init__.py").touch()
        
        # Create placeholder files for later injection
        placeholders = [
            "fractal_logic.py",
            "steps.py",
            "tuning.py"
        ]
        
        for file in placeholders:
            path = self.fryng_core_path / "src" / file
            path.write_text("# INJECTION_MARKER")
            logger.info(f"Created placeholder file: {file}")

def main():
    try:
        builder = ProjectBuilder()
        success = builder.build()
        return 0 if success else 1
    except Exception as e:
        logger.error(f"Build failed with exception: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())