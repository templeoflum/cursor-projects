import time
import os
import subprocess
import sys

def ensure_dependencies():
    try:
        import watchdog
    except ImportError:
        print("Installing watchdog package...")
        subprocess.check_call(['pip', 'install', 'watchdog'])
        print("Watchdog installed successfully!")

# Install dependencies first
ensure_dependencies()

# Now import watchdog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class DocxHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_modified = 0
        self.cooldown = 1

    def on_modified(self, event):
        if event.src_path.endswith('.docx'):
            current_time = time.time()
            if current_time - self.last_modified > self.cooldown:
                self.last_modified = current_time
                self.process_files()

    def run_script(self, script_name, timeout=30):
        """Run a Python script with timeout"""
        print(f"\nRunning {script_name}...")
        try:
            # Run script with longer timeout
            result = subprocess.run(
                [sys.executable, script_name],
                timeout=timeout,
                capture_output=True,
                text=True
            )
            print(result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            print(f"Error: {script_name} timed out after {timeout} seconds!")
            return False
        except Exception as e:
            print(f"Error running {script_name}: {e}")
            return False

    def process_files(self):
        print("\n" + "="*50)
        print("Changes detected! Processing files...")
        
        # Clean up previous output files
        for file in os.listdir('.'):
            if file.endswith('.md') or file.endswith('.pdf'):
                try:
                    os.remove(file)
                    print(f"Cleaned up: {file}")
                except Exception as e:
                    print(f"Error removing {file}: {e}")

        # Run conversion scripts with longer timeouts
        if not self.run_script('convert_to_md.py', timeout=30):
            print("DOCX to MD conversion failed!")
            return

        if not self.run_script('md_to_pdf.py', timeout=60):
            print("MD to PDF conversion failed!")
            return

        print("\nConversion complete!")
        print("="*50 + "\n")

def watch_directory():
    event_handler = DocxHandler()
    observer = Observer()
    observer.schedule(event_handler, '.', recursive=False)
    observer.start()
    
    print("Watching for changes in DOCX files...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nStopped watching for changes")
    
    observer.join()

def run_conversion(script_name, timeout=30):
    print(f"\nTesting {script_name}...")
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            check=True,
            timeout=timeout,
            capture_output=True,
            text=True
        )
        print(f"Success: {script_name}")
        print(result.stdout)
        return True
    except subprocess.TimeoutExpired:
        print(f"Error: {script_name} timed out after {timeout} seconds!")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}: {e}")
        if e.output:
            print("Output:", e.output)
        if e.stderr:
            print("Errors:", e.stderr)
        return False
    except Exception as e:
        print(f"Unexpected error in {script_name}: {e}")
        return False

def test_conversions():
    print("Testing conversion scripts individually...")
    
    # Test DOCX to MD
    if not run_conversion('convert_to_md.py', timeout=10):
        print("DOCX to MD conversion failed!")
        return False
        
    # Test MD to PDF
    if not run_conversion('md_to_pdf.py', timeout=10):
        print("MD to PDF conversion failed!")
        return False
        
    return True

if __name__ == "__main__":
    try:
        import watchdog
    except ImportError:
        print("Installing required packages...")
        subprocess.run(['pip', 'install', 'watchdog'])
        print("Packages installed!")
    
    print("Starting conversion test...")
    
    # Initial conversion
    handler = DocxHandler()
    handler.process_files()
    
    # Start watching for changes
    watch_directory() 