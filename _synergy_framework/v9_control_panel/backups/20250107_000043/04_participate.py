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
        npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
        return shutil.which(npm_cmd) is not None

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
        while self.process:
            output = self.process.stdout.readline()
            if output:
                logger.info(output.strip())
            if self.process.poll() is not None:
                break
        
    def _kill_process_on_port(self, port: int) -> bool:
        """Kill any process running on the specified port"""
        try:
            if os.name == 'nt':  # Windows
                # First try netstat
                result = subprocess.run(
                    f'netstat -ano | findstr :{port}',
                    shell=True,
                    capture_output=True,
                    text=True
                )
                
                if result.stdout:
                    for line in result.stdout.split('\n'):
                        if f':{port}' in line and 'LISTENING' in line:
                            try:
                                pid = line.strip().split()[-1]
                                logger.info(f"Found process {pid} on port {port}")
                                subprocess.run(f'taskkill /F /PID {pid}', shell=True)
                                logger.info(f"Killed process {pid}")
                            except Exception as e:
                                logger.error(f"Failed to kill PID {pid}: {e}")

                # Also try to kill any node processes
                subprocess.run('taskkill /F /IM node.exe', shell=True)
                
            else:  # Unix/Linux/Mac
                subprocess.run(
                    f'lsof -ti tcp:{port} | xargs kill -9',
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
            # Wait for port to be freed
            time.sleep(3)
            
            # Verify port is free
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('localhost', port))
                    s.close()
                    logger.info(f"Port {port} is now free")
                    return True
                except socket.error:
                    logger.error(f"Port {port} is still in use")
                    return False
                
        except Exception as e:
            logger.error(f"Error killing process on port {port}: {e}")
            return False

    def start(self) -> bool:
        try:
            logger.info("Starting development server...")
            
            # Check for npm
            if not self._check_npm():
                raise RuntimeError("npm is not installed. Please install Node.js and npm first.")

            # Kill any process using port 3000
            self._kill_process_on_port(3000)

            # Change to UI directory
            os.chdir(self.config.ui_core_path)
            logger.debug(f"Changed directory to: {os.getcwd()}")
            
            # Create or update package.json
            package_json = {
                "name": "fryng-ui",
                "version": "1.0.0",
                "private": True,
                "dependencies": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0",
                    "react-scripts": "5.0.1",
                    "express": "^4.18.2",
                    "cors": "^2.8.5"
                },
                "scripts": {
                    "start": "react-scripts start",
                    "build": "react-scripts build",
                    "server": "node server.js"
                }
            }
            
            with open("package.json", 'w') as f:
                json.dump(package_json, f, indent=2)
            
            # Create server.js for API endpoints
            server_js = '''
const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(cors());
app.use(express.json());

// Serve static files from public directory
app.use(express.static('public'));

// API endpoint to update tuning
app.post('/api/update-tuning', (req, res) => {
    try {
        const configPath = path.join(__dirname, 'public', 'data', 'tuning_config.json');
        const config = JSON.parse(fs.readFileSync(configPath));
        
        config.current_seed = req.body.value;
        
        fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
        
        // Update synergy data
        const synergyPath = path.join(__dirname, 'public', 'data', 'synergy_data.json');
        const synergyData = JSON.parse(fs.readFileSync(synergyPath));
        
        // Update synergy values based on new tuning
        synergyData.steps = synergyData.steps.map(step => ({
            harmony: Math.min(1, Math.max(0, step.harmony * req.body.value)),
            resonance: Math.min(1, Math.max(0, step.resonance * req.body.value)),
            balance: Math.min(1, Math.max(0, step.balance * req.body.value))
        }));
        
        fs.writeFileSync(synergyPath, JSON.stringify(synergyData, null, 2));
        
        res.json({ success: true });
    } catch (error) {
        console.error('Error updating tuning:', error);
        res.status(500).json({ error: error.message });
    }
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
    console.log(`API server running on port ${PORT}`);
});
'''
            
            with open("server.js", 'w') as f:
                f.write(server_js)
            
            # Install dependencies
            npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
            subprocess.run([npm_cmd, "install"], check=True)
            
            # Start both the React app and API server
            self.process = subprocess.Popen(
                [npm_cmd, "start"],
                env={**os.environ, **self.config.env_vars, "PORT": "3000"},
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            
            # Start API server in a separate process
            self.api_process = subprocess.Popen(
                [npm_cmd, "run", "server"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            
            # Start output streaming in separate threads
            threading.Thread(target=self._stream_output, daemon=True).start()
            threading.Thread(target=lambda: self._stream_output(self.api_process), daemon=True).start()
            
            # Wait for compilation
            success = False
            start_time = time.time()
            while time.time() - start_time < 120:
                if self.process.poll() is not None:
                    error_output = self.process.stderr.read()
                    if error_output:
                        logger.error(f"Server process failed: {error_output}")
                    break
                    
                output = self.process.stdout.readline()
                if output:
                    logger.debug(f"Server output: {output.strip()}")
                
                if "Compiled successfully!" in output:
                    success = True
                    time.sleep(3)
                    try:
                        logger.info("Opening browser...")
                        webbrowser.open('http://localhost:3000')
                    except Exception as e:
                        logger.error(f"Failed to open browser: {e}")
                    break
                    
            if not success:
                raise TimeoutError("Server failed to compile within timeout period")
            
            logger.info("Development server started successfully")
            
            while True:
                if self.process.poll() is not None:
                    break
                time.sleep(1)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            if self.process:
                self.stop()
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
