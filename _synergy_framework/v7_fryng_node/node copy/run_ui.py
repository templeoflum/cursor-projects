# run_ui.py

import sys
import os
import tkinter

# minimal approach:
try:
    from ui_core.main_ui import launch_ui
except ImportError as e:
    print("Could not import main_ui:", e)
    def launch_ui():
        print("No UI found - placeholder.")

if __name__ == "__main__":
    launch_ui()
