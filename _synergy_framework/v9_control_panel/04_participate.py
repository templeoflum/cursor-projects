import os
import sys
import json
import time
import logging
import subprocess
import webbrowser
import threading
from pathlib import Path

logger = logging.getLogger(__name__)

class ParticipationServer:
    def __init__(self, config_path: str = "project_config.json"):
        """Initialize participation server"""
        logger.info("Initializing ParticipationServer...")
        try:
            with open(config_path) as f:
                self.config = json.load(f)
            self.ui_core_path = Path(self.config["ui_core_path"])
            logger.debug(f"UI core path: {self.ui_core_path}")
            self.process = None
            self.api_process = None
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            raise

    def _stream_output(self, stream, prefix=''):
        """Stream output from a subprocess with a prefix"""
        try:
            for line in stream:
                print(f"{prefix}{line.strip()}")
                sys.stdout.flush()  # Ensure output is displayed immediately
                if "Compiled successfully" in line:
                    logger.info("React compilation successful, opening browser...")
                    webbrowser.open('http://localhost:3000')
        except Exception as e:
            logger.error(f"Error in output streaming: {e}")

    def start(self) -> bool:
        try:
            logger.info("Starting development server...")
            
            # Kill any existing processes first
            logger.info("Killing existing processes...")
            self._kill_process_on_port(3000)
            self._kill_process_on_port(3001)
            
            # Change to UI directory
            logger.info(f"Changing to UI directory: {self.ui_core_path}")
            os.chdir(self.ui_core_path)
            
            # Initialize data directory
            data_dir = Path("public/data")
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Create initial synergy data
            logger.info("Creating initial synergy data...")
            synergy_data = {
                "currentStep": 0,
                "steps": [
                    {
                        "potential": 0.5,
                        "symmetry": 0.5,
                        "flow": 0.5,
                        "connectivity": 0.5,
                        "emergence": 0.5,
                        "recursion": 0.5
                    } for _ in range(6)
                ]
            }
            
            with open(data_dir / "synergy_data.json", 'w') as f:
                json.dump(synergy_data, f, indent=2)

            # Create server.js
            logger.info("Creating server.js...")
            server_js = '''
const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// API endpoints
app.get('/api/synergy-data', (req, res) => {
    try {
        const synergyPath = path.join(__dirname, 'public', 'data', 'synergy_data.json');
        const synergyData = JSON.parse(fs.readFileSync(synergyPath));
        res.json(synergyData);
    } catch (error) {
        console.error('Error reading synergy data:', error);
        res.status(500).json({ error: error.message });
    }
});

app.post('/api/update-tuning', (req, res) => {
    try {
        const configPath = path.join(__dirname, 'public', 'data', 'tuning_config.json');
        const config = JSON.parse(fs.readFileSync(configPath));
        
        config.current_seed = req.body.value;
        fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
        
        const synergyPath = path.join(__dirname, 'public', 'data', 'synergy_data.json');
        const synergyData = JSON.parse(fs.readFileSync(synergyPath));
        
        synergyData.steps = synergyData.steps.map((step, index) => ({
            potential: Math.min(1, Math.max(0, req.body.value * (1 + index * 0.1))),
            symmetry: Math.min(1, Math.max(0, req.body.value * (1 + index * 0.1))),
            flow: Math.min(1, Math.max(0, req.body.value * (1 + index * 0.1))),
            connectivity: Math.min(1, Math.max(0, req.body.value * (1 + index * 0.1))),
            emergence: Math.min(1, Math.max(0, req.body.value * (1 + index * 0.1))),
            recursion: Math.min(1, Math.max(0, req.body.value * (1 + index * 0.1)))
        }));
        
        fs.writeFileSync(synergyPath, JSON.stringify(synergyData, null, 2));
        res.json({ success: true, data: synergyData });
    } catch (error) {
        console.error('Error updating tuning:', error);
        res.status(500).json({ error: error.message });
    }
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
    console.log(`API server running on port ${PORT}`);
});'''

            with open("server.js", 'w') as f:
                f.write(server_js)

            logger.info("Starting React development server...")
            self.process = subprocess.Popen(
                ["npm", "start"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                shell=True  # Add shell=True for Windows
            )

            logger.info("Starting API server...")
            self.api_process = subprocess.Popen(
                ["npm", "run", "server"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                shell=True  # Add shell=True for Windows
            )

            # Stream output in separate threads
            threading.Thread(
                target=self._stream_output,
                args=(self.process.stdout, 'React: '),
                daemon=True
            ).start()
            
            threading.Thread(
                target=self._stream_output,
                args=(self.process.stderr, 'React Error: '),
                daemon=True
            ).start()

            threading.Thread(
                target=self._stream_output,
                args=(self.api_process.stdout, 'API: '),
                daemon=True
            ).start()

            logger.info("Waiting for servers to start...")
            time.sleep(5)  # Increased wait time
            
            logger.info("Opening browser...")
            webbrowser.open('http://localhost:3000')

            return True

        except Exception as e:
            logger.error(f"Error starting development server: {e}")
            return False

    def _kill_process_on_port(self, port: int) -> None:
        """Kill any process using the specified port"""
        try:
            subprocess.run(f"npx kill-port {port}", shell=True, check=True)
            logger.info(f"Port {port} is now free")
        except Exception as e:
            logger.warning(f"Error killing process on port {port}: {e}")
