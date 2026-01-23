import os
import webbrowser
import subprocess
import time
import platform
from pathlib import Path

def activate_venv_and_launch():
    # Get the current directory
    current_dir = Path.cwd()
    venv_path = current_dir / "venv"
    
    if platform.system().lower() == "windows":
        # Quote the path to handle spaces
        activate_script = str(venv_path / "Scripts" / "activate.bat")
        activate_command = f'"{activate_script}" && open-webui serve'
        
        process = subprocess.Popen(activate_command,
                                 shell=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 universal_newlines=True)
        
        print("Starting server...")
        # Wait for the server to start
        time.sleep(8)  # Increased wait time
        
        # Print startup messages
        while True:
            line = process.stderr.readline()
            if not line and process.poll() is not None:
                print("Server failed to start")
                return
            if "Application startup complete" in line:
                break
            print(line.strip())
            
        # Open the browser
        print("Opening browser...")
        webbrowser.open('http://localhost:8080')
        
        print("Web UI is starting...")
        print("If the browser doesn't open automatically, visit: http://localhost:8080")
        
        try:
            # Keep the script running and show output
            while True:
                output = process.stdout.readline()
                if output:
                    print(output.strip())
                if process.poll() is not None:
                    break
        except KeyboardInterrupt:
            print("\nShutting down...")
            process.terminate()

if __name__ == "__main__":
    activate_venv_and_launch() 