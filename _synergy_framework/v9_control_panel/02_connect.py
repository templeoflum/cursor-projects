import json
import sys
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class CodeInjector:
    def __init__(self, ui_core_path: Path):
        self.ui_core_path = ui_core_path

    def update_index(self) -> None:
        """Update or create all necessary UI files"""
        
        # Create index.html
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

        # Create index.js
        index_js_content = '''import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
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
            const response = await fetch('http://localhost:3001/api/synergy-data');
            if (!response.ok) throw new Error('Failed to fetch synergy data');
            const data = await response.json();
            setSynergyData(data);
        } catch (error) {
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
                        <div>Potential: {step.potential.toFixed(4)}</div>
                        <div>Symmetry: {step.symmetry.toFixed(4)}</div>
                        <div>Flow: {step.flow.toFixed(4)}</div>
                        <div>Connectivity: {step.connectivity.toFixed(4)}</div>
                        <div>Emergence: {step.emergence.toFixed(4)}</div>
                        <div>Recursion: {step.recursion.toFixed(4)}</div>
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

        # Create initial tuning config
        tuning_config = {
            "current_seed": 0.5,
            "min_value": 0.0,
            "max_value": 1.0
        }

        # Save tuning config
        with open(public_dir / "data" / "tuning_config.json", 'w') as f:
            json.dump(tuning_config, f, indent=2)

def main():
    try:
        # Load project configuration
        config_path = Path.cwd() / "node" / "project_config.json"
        if not config_path.exists():
            raise FileNotFoundError("Project config not found. Run build first.")
            
        with open(config_path) as f:
            config = json.load(f)
            
        ui_core_path = Path(config["ui_core_path"])
        
        # Initialize and run code injector
        injector = CodeInjector(ui_core_path)
        injector.update_index()
        logger.info("Connection process completed successfully")
        return 0
            
    except Exception as e:
        logger.error(f"Connection process failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
