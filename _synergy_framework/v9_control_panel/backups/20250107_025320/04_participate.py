import os
import sys
import json
import subprocess
import logging
import webbrowser
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
import time
import threading
import shutil
import socket

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ProjectConfig:
    """Project configuration settings"""
    project_dir: Path
    ui_core_path: Path
    env_vars: Dict[str, str]

def is_port_in_use(port: int) -> bool:
    """Check if port is in use (reverse of previous logic)"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect(('localhost', port))
            return True
        except socket.error:
            return False

def wait_for_server(port: int, timeout: int = 60) -> bool:
    """Wait for server to be ready"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_port_in_use(port):  # Changed to check if port is in use
            return True
        time.sleep(1)
    return False

class ParticipationServer:
    def __init__(self):
        # Load project configuration
        self.node_dir = Path.cwd() / "node"
        config_path = self.node_dir / "project_config.json"
        
        with open(config_path) as f:
            config = json.load(f)
            
        self.config = ProjectConfig(
            project_dir=Path(config["project_dir"]),
            ui_core_path=Path(config["ui_core_path"]),
            env_vars={
                "BROWSER": "none",  # Prevent auto-opening browser
                "PORT": "3000"
            }
        )
        self.process = None
        self.port = 3000

    def _check_npm(self) -> bool:
        """Check if npm is installed"""
        try:
            # On Windows, check both npm and npm.cmd in Node.js directory
            if os.name == "nt":
                node_path = shutil.which('node')
                if node_path:
                    node_dir = Path(node_path).parent
                    npm_paths = [
                        node_dir / "npm.cmd",
                        node_dir / "npm",
                        Path(os.environ.get('APPDATA', '')) / "npm" / "npm.cmd"
                    ]
                    
                    for npm_path in npm_paths:
                        if npm_path.exists():
                            # Add both Node.js and npm directories to PATH
                            os.environ["PATH"] = f"{node_dir};{npm_path.parent};{os.environ['PATH']}"
                            return True
                            
                    # If we get here, npm wasn't found in expected locations
                    logger.error("npm not found in Node.js directory. Please reinstall Node.js")
                    return False
                else:
                    # If we get here, npm wasn't found in expected locations
                    logger.error("npm not found in Node.js directory. Please reinstall Node.js")
                    return False
            else:
                # For non-Windows systems, use simple check
                return shutil.which("npm") is not None
            
        except Exception as e:
            logger.error(f"Error checking npm: {e}")
            return False

    def _run_npm_command(self, command: str) -> subprocess.CompletedProcess:
        """Run an npm command"""
        npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
        full_command = [npm_cmd] + command.split()
        
        logger.debug(f"Running command: {full_command}")
        return subprocess.run(
            full_command,
            check=True,
            capture_output=True,
            text=True
        )

    def _stream_output(self):
        """Stream server output to logger"""
        def stream_lines(pipe, prefix=''):
            for line in iter(pipe.readline, ''):
                logger.info(f"{prefix}{line.strip()}")
                
                # If we see the "compiled successfully" message, try to open browser
                if "Compiled successfully!" in line:
                    try:
                        import webbrowser
                        webbrowser.open('http://localhost:3000')
                        logger.info("Opened browser to http://localhost:3000")
                    except Exception as e:
                        logger.error(f"Failed to open browser: {e}")

        if self.process:
            threading.Thread(
                target=stream_lines,
                args=(self.process.stdout,),
                daemon=True
            ).start()
            threading.Thread(
                target=stream_lines,
                args=(self.process.stderr, 'ERR: '),
                daemon=True
            ).start()

        if self.api_process:
            threading.Thread(
                target=stream_lines,
                args=(self.api_process.stdout, 'API: '),
                daemon=True
            ).start()
            threading.Thread(
                target=stream_lines,
                args=(self.api_process.stderr, 'API ERR: '),
                daemon=True
            ).start()

    def _kill_process_on_port(self, port: int) -> bool:
        """Kill any process running on the specified port"""
        try:
            if os.name == 'nt':  # Windows
                # Use more reliable Windows commands
                try:
                    # Find PID using netstat
                    result = subprocess.run(
                        ['netstat', '-ano', '|', 'findstr', f':{port}'],
                        capture_output=True,
                        text=True,
                        shell=True
                    )
                    
                    if result.stdout:
                        for line in result.stdout.split('\n'):
                            if f':{port}' in line and 'LISTENING' in line:
                                pid = line.strip().split()[-1]
                                subprocess.run(['taskkill', '/F', '/PID', pid], check=True)
                    
                    # Also try to kill node processes more carefully
                    subprocess.run(['tasklist', '/FI', 'IMAGENAME eq node.exe'], capture_output=True)
                    subprocess.run(['taskkill', '/IM', 'node.exe', '/F'], capture_output=True)
                    
                except subprocess.CalledProcessError:
                    pass  # Ignore errors if process not found
                    
            else:  # Unix/Linux/Mac
                subprocess.run(
                    ['lsof', '-ti', f'tcp:{port}', '|', 'xargs', 'kill', '-9'],
                    shell=True
                )
                
            time.sleep(2)  # Give processes time to fully terminate
            return True
                
        except Exception as e:
            logger.error(f"Error killing process on port {port}: {e}")
            return False

    def _check_node_installation(self) -> bool:
        """Check if Node.js and npm are installed"""
        try:
            # Check for Node.js first
            node_path = shutil.which('node')
            if not node_path:
                logger.error("Node.js not found in PATH")
                return False
            
            # Check for npm specifically
            npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
            npm_path = shutil.which(npm_cmd)
            
            if not npm_path:
                # On Windows, try to find npm relative to node path
                if os.name == "nt":
                    node_dir = Path(node_path).parent
                    possible_npm = node_dir / "npm.cmd"
                    if possible_npm.exists():
                        # Add node directory to PATH if npm exists there
                        os.environ["PATH"] = f"{node_dir};{os.environ['PATH']}"
                        return True
            
                logger.error("""
npm not found. Please try the following:
1. Uninstall Node.js completely
2. Download Node.js LTS from https://nodejs.org/
3. During installation:
   - Check 'Automatically install necessary tools'
   - Run as administrator
4. Restart your computer
5. Open a NEW Command Prompt and verify both work:
   node --version
   npm --version
""")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking Node.js/npm installation: {e}")
            return False

    def start(self) -> bool:
        try:
            logger.info("Starting development server...")
            
            # Kill any existing processes first
            self._kill_process_on_port(3000)
            self._kill_process_on_port(3001)
            
            # Change to UI directory
            os.chdir(self.config.ui_core_path)
            logger.debug(f"Changed directory to: {os.getcwd()}")

            # Use npm.cmd directly with full path
            npm_path = Path(os.environ.get('APPDATA', '')) / "npm" / "npm.cmd"
            if not npm_path.exists():
                npm_path = Path(r"C:\Program Files\nodejs\npm.cmd")
            
            if not npm_path.exists():
                raise RuntimeError(f"npm not found at {npm_path}")
            
            # Install dependencies
            subprocess.run([str(npm_path), "install"], check=True)
            
            # Start both servers using the full npm path
            self.process = subprocess.Popen(
                [str(npm_path), "start"],
                env={**os.environ, **self.config.env_vars},
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            self.api_process = subprocess.Popen(
                [str(npm_path), "run", "server"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Start output streaming
            threading.Thread(target=self._stream_output, daemon=True).start()
            
            # Wait a bit for the server to start
            time.sleep(5)
            
            # Open browser
            try:
                import webbrowser
                webbrowser.open('http://localhost:3000')
                logger.info("Opened browser to http://localhost:3000")
            except Exception as e:
                logger.error(f"Failed to open browser: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting development server: {e}")
            if hasattr(self, 'process') and self.process:
                self.process.terminate()
            if hasattr(self, 'api_process') and self.api_process:
                self.api_process.terminate()
            return False

    def stop(self):
        """Stop the development server"""
        if self.process:
            self.process.terminate()
        if hasattr(self, 'api_process') and self.api_process:
            self.api_process.terminate()

def main():
    try:
        server = ParticipationServer()
        success = server.start()
        if success:
            try:
                # Keep the script running
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                server.stop()
        return 0 if success else 1
    except Exception as e:
        logger.error(f"Participation failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
