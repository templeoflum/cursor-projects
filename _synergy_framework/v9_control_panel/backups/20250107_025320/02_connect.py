import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CodeInjector:
    def __init__(self):
        try:
            # Load project configuration
            self.node_dir = Path.cwd() / "node"
            config_path = self.node_dir / "project_config.json"
            
            if not config_path.exists():
                raise FileNotFoundError("Project config not found. Run build first.")
                
            with open(config_path) as f:
                config = json.load(f)
                
            self.fryng_core_path = Path(config["fryng_core_path"])
            self.ui_core_path = Path(config["ui_core_path"])
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            raise

    def connect(self) -> bool:
        """Main connection process"""
        try:
            logger.info("Starting connection process...")
            
            # Inject all necessary code
            self.inject_fractal_logic()
            self.inject_steps()
            self.update_index()
            self.create_app_component()
            
            logger.info("Connection process completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    def inject_fractal_logic(self) -> None:
        """Inject fractal logic implementation"""
        fractal_logic_content = '''import random
from typing import Dict, Any

# Define the dynamic attributes that will be used in synergy calculations
DYNAMIC_ATTRIBUTES = {
    'potential': 0.0,
    'symmetry': 0.0,
    'flow': 0.0,
    'connectivity': 0.0,
    'emergence': 0.0,
    'recursion': 0.0
}

def fractal_synergy_core(value: float, iteration: int = 1) -> float:
    """
    Core fractal synergy calculation function.
    
    Args:
        value: Input value to process
        iteration: Current iteration number
    
    Returns:
        Processed value with fractal transformations applied
    """
    # Apply fractal transformations based on dynamic attributes
    transformation = sum(
        attr_value * random.random() 
        for attr_value in DYNAMIC_ATTRIBUTES.values()
    ) / len(DYNAMIC_ATTRIBUTES)
    
    return value * (1 + transformation)

def update_dynamic_attributes(feedback_signal: float) -> None:
    """
    Update dynamic attributes based on feedback signal.
    
    Args:
        feedback_signal: Signal value to influence attribute updates
    """
    for attr in DYNAMIC_ATTRIBUTES:
        current_value = DYNAMIC_ATTRIBUTES[attr]
        # Apply feedback with some randomization
        adjustment = feedback_signal * (1 + random.random() * 0.1)
        DYNAMIC_ATTRIBUTES[attr] = max(0.0, min(1.0, current_value + adjustment))
'''
        self._write_to_file(self.fryng_core_path / "src" / "fractal_logic.py", fractal_logic_content)

    def inject_steps(self) -> None:
        """Inject steps implementation"""
        steps_content = '''import random
from typing import Dict, Any
import fractal_logic

def execute_step_system(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a single step in the synergy system.
    
    Args:
        input_data: Current system state and value
        
    Returns:
        Updated system state
    """
    current_value = input_data["value"]
    
    # Apply fractal transformation
    transformed_value = fractal_logic.fractal_synergy_core(current_value)
    
    # Update feedback in fractal system
    fractal_logic.update_dynamic_attributes(transformed_value - current_value)
    
    # Return updated state
    return {
        "value": transformed_value,
        "description": input_data.get("description", "Step completed")
    }
'''
        self._write_to_file(self.fryng_core_path / "src" / "steps.py", steps_content)

    def update_index(self) -> None:
        """Update index file and create necessary React files"""
        # Create index.html with proper React setup
        index_content = '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="Fryng Control Panel" />
    <title>Fryng Control Panel</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>'''

        # Create manifest.json
        manifest_content = '''{
  "short_name": "Fryng",
  "name": "Fryng Control Panel",
  "start_url": ".",
  "display": "standalone",
  "theme_color": "#000000",
  "background_color": "#ffffff"
}'''

        # Create index.js with proper React 18 setup
        index_js_content = '''import React from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App';

const container = document.getElementById('root');
const root = createRoot(container);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);'''

        # Create index.css
        index_css_content = '''body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}'''

        # Create App.js
        app_content = '''import React, { useState, useEffect } from 'react';

function App() {
    const [tuningValue, setTuningValue] = useState(0.5);
    const [status, setStatus] = useState('Ready');
    const [synergyData, setSynergyData] = useState({ steps: [], currentStep: 0 });

    useEffect(() => {
        fetchSynergyData();
    }, []);

    const fetchSynergyData = async () => {
        try {
            const response = await fetch('/api/synergy-data');
            if (!response.ok) throw new Error('Failed to fetch synergy data');
            const data = await response.json();
            setSynergyData(data);
        } catch (error) {
            setStatus(`Error loading synergy data: ${error.message}`);
        }
    };

    const updateTuning = async (value) => {
        try {
            const response = await fetch('/api/update-tuning', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ value }),
            });
            
            if (response.ok) {
                setStatus('Updated successfully');
                setTuningValue(value);
                await fetchSynergyData();
            } else {
                setStatus('Update failed');
            }
        } catch (error) {
            setStatus(`Error: ${error.message}`);
        }
    };

    return (
        <div className="App" style={{ padding: '20px' }}>
            <h1>Fryng Control Panel</h1>
            <div style={{ marginBottom: '20px' }}>
                <label>
                    Tuning Value: {tuningValue}
                    <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.01"
                        value={tuningValue}
                        onChange={(e) => updateTuning(parseFloat(e.target.value))}
                        style={{ display: 'block', width: '100%', maxWidth: '300px' }}
                    />
                </label>
            </div>
            <div>Status: {status}</div>
            
            <div style={{ marginTop: '20px' }}>
                <h2>Synergy Values</h2>
                {synergyData.steps.map((step, index) => (
                    <div key={index} style={{ 
                        padding: '10px',
                        margin: '10px 0',
                        backgroundColor: index === synergyData.currentStep ? '#f0f0f0' : 'transparent',
                        border: '1px solid #ddd',
                        borderRadius: '4px'
                    }}>
                        <h3>Step {index + 1}</h3>
                        <div>Harmony: {step.harmony.toFixed(4)}</div>
                        <div>Resonance: {step.resonance.toFixed(4)}</div>
                        <div>Balance: {step.balance.toFixed(4)}</div>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default App;'''

        # Ensure directories exist
        public_dir = self.ui_core_path / "public"
        src_dir = self.ui_core_path / "src"
        public_dir.mkdir(exist_ok=True)
        src_dir.mkdir(exist_ok=True)
        (public_dir / "data").mkdir(exist_ok=True)

        # Write files
        with open(public_dir / "index.html", 'w') as f:
            f.write(index_content)
        with open(public_dir / "manifest.json", 'w') as f:
            f.write(manifest_content)
        with open(src_dir / "index.js", 'w') as f:
            f.write(index_js_content)
        with open(src_dir / "index.css", 'w') as f:
            f.write(index_css_content)
        with open(src_dir / "App.js", 'w') as f:
            f.write(app_content)

        # Create sample synergy data
        synergy_data = {
            "steps": [
                {"harmony": 0.75, "resonance": 0.85, "balance": 0.65},
                {"harmony": 0.82, "resonance": 0.78, "balance": 0.70},
                {"harmony": 0.90, "resonance": 0.88, "balance": 0.85}
            ],
            "currentStep": 1
        }

        # Save synergy data
        with open(public_dir / "data" / "synergy_data.json", 'w') as f:
            json.dump(synergy_data, f, indent=2)

        # Create initial tuning config if it doesn't exist
        tuning_config = {
            "current_seed": 0.5,
            "min_value": 0.0,
            "max_value": 1.0
        }
        
        with open(public_dir / "data" / "tuning_config.json", 'w') as f:
            json.dump(tuning_config, f, indent=2)

    def create_app_component(self) -> None:
        """Create main App component"""
        app_content = '''import React, { useState, useEffect } from 'react';

function App() {
    const [tuningValue, setTuningValue] = useState(0.5);
    const [status, setStatus] = useState('Ready');
    const [synergyData, setSynergyData] = useState({ steps: [], currentStep: 0 });

    useEffect(() => {
        fetchSynergyData();
    }, []);

    const fetchSynergyData = async () => {
        try {
            // Use absolute URL to ensure we're hitting the correct endpoint
            const response = await fetch('http://localhost:3001/api/synergy-data');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            setSynergyData(data);
            setStatus('Data loaded successfully');
        } catch (error) {
            console.error('Fetch error:', error);
            setStatus(`Error loading synergy data: ${error.message}`);
        }
    };

    const updateTuning = async (value) => {
        try {
            const response = await fetch('http://localhost:3001/api/update-tuning', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ value }),
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            if (result.success) {
                setStatus('Updated successfully');
                setTuningValue(value);
                await fetchSynergyData();
            } else {
                setStatus('Update failed: ' + (result.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Update error:', error);
            setStatus(`Error: ${error.message}`);
        }
    };

    return (
        <div className="App" style={{ padding: '20px' }}>
            <h1>Fryng Control Panel</h1>
            <div style={{ marginBottom: '20px' }}>
                <label>
                    Tuning Value: {tuningValue}
                    <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.01"
                        value={tuningValue}
                        onChange={(e) => updateTuning(parseFloat(e.target.value))}
                        style={{ display: 'block', width: '100%', maxWidth: '300px' }}
                    />
                </label>
            </div>
            <div>Status: {status}</div>
            
            <div style={{ marginTop: '20px' }}>
                <h2>Synergy Values</h2>
                {synergyData.steps && synergyData.steps.length > 0 ? (
                    synergyData.steps.map((step, index) => (
                        <div key={index} style={{ 
                            padding: '10px',
                            margin: '10px 0',
                            backgroundColor: index === synergyData.currentStep ? '#f0f0f0' : 'transparent',
                            border: '1px solid #ddd',
                            borderRadius: '4px'
                        }}>
                            <h3>Step {index + 1}</h3>
                            <div>Harmony: {step.harmony.toFixed(4)}</div>
                            <div>Resonance: {step.resonance.toFixed(4)}</div>
                            <div>Balance: {step.balance.toFixed(4)}</div>
                        </div>
                    ))
                ) : (
                    <div>No synergy data available</div>
                )}
            </div>
        </div>
    );
}

export default App;'''
        
        with open(self.ui_core_path / "src" / "App.js", 'w') as f:
            f.write(app_content)

    def _write_to_file(self, path: Path, content: str) -> None:
        """Helper method to write content to file with proper error handling"""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            logger.info(f"Successfully wrote to {path}")
        except Exception as e:
            logger.error(f"Failed to write to {path}: {e}")
            raise

def main():
    try:
        injector = CodeInjector()
        success = injector.connect()
        return 0 if success else 1
    except Exception as e:
        logger.error(f"Connection process failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
