import tkinter as tk
from tkinter import ttk
import logging
from pathlib import Path
import sys
import os
import shutil
import subprocess
import time
import threading
from backup import BackupManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProjectManager:
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path.cwd()
        self.node_dir = self.base_dir / "node"
        self.callback = None
        self.participate_process = None

    def set_callback(self, callback):
        self.callback = callback

    def log(self, message: str, level: str = "INFO"):
        if self.callback:
            self.callback(f"[{level}] {message}")
        logger.info(message)

    def run_subprocess(self, command: list, action_name: str) -> bool:
        """Run a subprocess with proper logging"""
        try:
            self.log(f"Starting {action_name}...")
            
            # Special handling for participate
            if action_name == "Participate":
                if self.participate_process:
                    self.log("Stopping existing participate process...")
                    self.participate_process.terminate()
                    self.participate_process = None
                
                # Start participate in a new process
                self.participate_process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1
                )
                
                # Start a thread to read the output
                def read_output():
                    while True:
                        line = self.participate_process.stdout.readline()
                        if not line and self.participate_process.poll() is not None:
                            break
                        if line:
                            self.log(line.strip())
                
                threading.Thread(target=read_output, daemon=True).start()
                return True
                
            else:
                # Normal subprocess handling for other commands
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True
                )
                
                # Log output
                if result.stdout:
                    self.log(result.stdout)
                if result.stderr:
                    self.log(result.stderr, "ERROR")
                    
                success = result.returncode == 0
                self.log(f"{action_name} {'succeeded' if success else 'failed'}")
                return success
                
        except Exception as e:
            self.log(f"{action_name} failed: {str(e)}", "ERROR")
            return False

    def kill_all_processes(self):
        """Kill all running processes"""
        try:
            # Kill any running npm processes
            if os.name == 'nt':  # Windows
                # Kill node processes
                subprocess.run(['taskkill', '/F', '/IM', 'node.exe'], 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE)
                # Kill npm processes
                subprocess.run(['taskkill', '/F', '/IM', 'npm.cmd'], 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE)
            else:  # Unix/Linux/Mac
                subprocess.run(['pkill', 'node'], 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE)
                subprocess.run(['pkill', 'npm'], 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE)
            
            # Terminate our own participate process if it exists
            if self.participate_process:
                self.participate_process.terminate()
                self.participate_process = None
                
            # Give processes time to fully terminate
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"Error killing processes: {e}")

    def clean(self) -> bool:
        """Clean the project by removing the node directory"""
        self.log("Starting cleanup process...")
        try:
            # First kill all processes
            self.kill_all_processes()
            
            # Try to remove directory multiple times
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    if self.node_dir.exists():
                        shutil.rmtree(self.node_dir)
                    break
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    self.log(f"Retry {attempt + 1}/{max_attempts}: {str(e)}")
                    time.sleep(2)
                    
            self.log("Cleanup completed successfully")
            return True
        except Exception as e:
            self.log(f"Clean failed: {str(e)}", "ERROR")
            return False

    def build(self) -> bool:
        return self.run_subprocess([sys.executable, "01_build.py"], "Build")

    def connect(self) -> bool:
        return self.run_subprocess([sys.executable, "02_connect.py"], "Connect")

    def focus(self) -> bool:
        return self.run_subprocess([sys.executable, "03_focus.py"], "Focus")

    def participate(self) -> bool:
        return self.run_subprocess([sys.executable, "04_participate.py"], "Participate")

class ManagerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Project Manager")
        self.geometry("400x300")
        
        self.manager = ProjectManager()
        self.backup_manager = BackupManager()
        self.manager.set_callback(self.add_log_message)
        
        self.create_gui()
        
        # Add window close handler
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Set minimum window size to prevent too small resizing
        self.minsize(500, 300)

    def on_closing(self):
        """Handle window closing"""
        if self.manager.participate_process:
            self.manager.participate_process.terminate()
        self.destroy()

    def create_gui(self):
        """Create the GUI elements"""
        # Create main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Create primary buttons frame
        primary_frame = ttk.Frame(main_frame)
        primary_frame.pack(fill="x", padx=5, pady=5)
        
        # Create primary action buttons
        buttons = [
            ("Build", self.build_action),
            ("Connect", self.connect_action),
            ("Focus", self.focus_action),
            ("Participate", self.participate_action),
            ("Clean", self.clean_action)
        ]
        
        for text, command in buttons:
            btn = ttk.Button(primary_frame, text=text, command=command)
            btn.pack(side="left", padx=5)

        # Create utility buttons frame
        util_frame = ttk.LabelFrame(main_frame, text="Utilities")
        util_frame.pack(fill="x", padx=5, pady=5)
        
        # Add utility buttons
        ttk.Button(util_frame, text="Show Files", 
                  command=self.show_files).pack(side="left", padx=2)
        ttk.Button(util_frame, text="Copy Log", 
                  command=self.copy_log).pack(side="left", padx=2)
        ttk.Button(util_frame, text="Clear Log", 
                  command=self.clear_log).pack(side="left", padx=2)
        ttk.Button(util_frame, text="Backup", 
                  command=self.create_backup).pack(side="left", padx=2)
        
        # Create log frame
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(expand=True, fill="both", padx=5, pady=5)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(log_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Create log display
        self.log_text = tk.Text(log_frame, height=20, yscrollcommand=scrollbar.set)
        self.log_text.pack(expand=True, fill="both")
        
        scrollbar.config(command=self.log_text.yview)

    def add_log_message(self, message: str):
        """Add message to log display"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.update_idletasks()

    def clear_log(self):
        """Clear the log display"""
        self.log_text.delete(1.0, tk.END)

    def clean_action(self):
        """Handle Clean button click"""
        success = self.manager.clean()
        if success:
            self.add_log_message("Clean succeeded")
        else:
            self.add_log_message("Clean failed", "ERROR")

    def build_action(self):
        """Handle Build button click"""
        success = self.manager.build()
        if success:
            self.add_log_message("Build succeeded")
        else:
            self.add_log_message("Build failed", "ERROR")

    def connect_action(self):
        """Handle Connect button click"""
        success = self.manager.connect()
        if success:
            self.add_log_message("Connect succeeded")
        else:
            self.add_log_message("Connect failed", "ERROR")

    def focus_action(self):
        """Handle Focus button click"""
        success = self.manager.focus()
        if success:
            self.add_log_message("Focus succeeded")
        else:
            self.add_log_message("Focus failed", "ERROR")

    def participate_action(self):
        """Handle Participate button click"""
        success = self.manager.participate()
        if success:
            self.add_log_message("Participate succeeded")
        else:
            self.add_log_message("Participate failed", "ERROR")

    def show_files(self):
        """Display current file tree"""
        def get_tree(path: Path, prefix: str = "") -> str:
            tree = ""
            for item in sorted(path.iterdir()):
                tree += f"{prefix}├── {item.name}\n"
                if item.is_dir():
                    tree += get_tree(item, prefix + "│   ")
            return tree
            
        try:
            tree = f"Project Directory: {self.manager.base_dir}\n"
            tree += get_tree(self.manager.base_dir)
            self.add_log_message("\nFile Tree:")
            self.add_log_message(tree)
        except Exception as e:
            self.add_log_message(f"Error showing files: {e}")

    def copy_log(self):
        """Copy log contents to clipboard"""
        try:
            log_content = self.log_text.get(1.0, tk.END)
            self.clipboard_clear()
            self.clipboard_append(log_content)
            self.add_log_message("Log copied to clipboard")
        except Exception as e:
            self.add_log_message(f"Error copying log: {e}")

    def create_backup(self):
        """Create a backup with optional note"""
        try:
            if self.backup_manager.create_backup("Manual backup"):
                self.add_log_message("Backup created successfully")
            else:
                self.add_log_message("Backup failed")
        except Exception as e:
            self.add_log_message(f"Error creating backup: {e}")

    def list_backups(self):
        """Show list of backups"""
        try:
            backups = self.backup_manager.list_backups()
            if backups:
                self.add_log_message("\nAvailable backups:")
                for backup in backups:
                    self.add_log_message(
                        f"Timestamp: {backup['timestamp']}, "
                        f"Files: {backup['file_count']}, "
                        f"Note: {backup['note']}"
                    )
            else:
                self.add_log_message("No backups found")
        except Exception as e:
            self.add_log_message(f"Error listing backups: {e}")

    def restore_backup(self, timestamp: str):
        """Restore a specific backup"""
        try:
            if self.backup_manager.restore_backup(timestamp):
                self.add_log_message(f"Backup {timestamp} restored successfully")
            else:
                self.add_log_message(f"Failed to restore backup {timestamp}")
        except Exception as e:
            self.add_log_message(f"Error restoring backup: {e}")

def main():
    app = ManagerGUI()
    app.mainloop()

if __name__ == "__main__":
    main()