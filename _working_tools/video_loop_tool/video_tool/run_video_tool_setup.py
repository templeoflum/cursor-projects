#!/usr/bin/env python3
import os
import subprocess
import sys
import platform
import venv # To create virtual environments
import shutil # For potentially copying ffmpeg if we extend it

# --- Configuration ---
PROJECT_ROOT_DIR_NAME = "VideoLoopTool_Project" # Name of the main folder to be created
VENV_DIR_NAME = "venv" # Name of the virtual environment folder
APP_SCRIPT_FILENAME = "video_tool_app_ui.py" # Name of the UI script that will be written
FFMPEG_BIN_SUBDIR = "ffmpeg_executables" # Subdirectory within project to look for/place ffmpeg

# --- Embedded Main Application UI Code ---
# This entire multi-line string will contain the Tkinter application code
# (as developed in previous responses, focusing on quality, no audio,
# and expecting FFMPEG_PATH and FFPROBE_PATH to be set via environment variables)
VIDEO_TOOL_APP_CODE = """
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import shutil
import tempfile
import threading
import sys # For PyInstaller path bundling

# --- Helper Function to Find Bundled Executables (for PyInstaller) ---
def resource_path(relative_path):
    \"\"\" Get absolute path to resource, works for dev and for PyInstaller \"\"\" # This line too
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # In development, _MEIPASS is not set, use script's directory
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# --- Global Configuration ---
# Determine if running as a bundled executable (PyInstaller)
IS_BUNDLED = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

FFMPEG_PATH = os.environ.get('BOOTSTRAP_FFMPEG_PATH', 'ffmpeg')
FFPROBE_PATH = os.environ.get('BOOTSTRAP_FFPROBE_PATH', 'ffprobe')

# --- Helper Function to Run FFmpeg/ffprobe Commands ---
def run_command(command_list, app_status_update_func, operation_name="FFmpeg"):
    app_status_update_func(f"Running: {operation_name}...")
    try:
        creationflags = 0
        if os.name == 'nt': # Hide console window on Windows
            creationflags = subprocess.CREATE_NO_WINDOW

        process = subprocess.Popen(command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True, encoding='utf-8', errors='replace', creationflags=creationflags)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            _raw_error_output = stderr or stdout or ""
            error_msg = f"{operation_name} Error (Code {process.returncode}):\\n{_raw_error_output!r}"
            print(error_msg)
            messagebox.showerror(f"{operation_name} Error", error_msg)
            app_status_update_func(f"{operation_name} failed.")
            return False, stderr or stdout
        app_status_update_func(f"{operation_name} successful.")
        return True, stdout
    except FileNotFoundError:
        error_msg = f"{operation_name} (e.g., {command_list[0]}) not found. Please ensure it's installed correctly."
        if IS_BUNDLED:
             error_msg += f"\\nExpected at: {command_list[0]}"
        else:
            error_msg += "\\nEnsure it's in your system PATH for development."
        messagebox.showerror("Error", error_msg)
        app_status_update_func(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"An unexpected error occurred with {operation_name}: {str(e)}"
        messagebox.showerror("Error", error_msg)
        app_status_update_func(error_msg)
        return False, error_msg

# --- Concatenation Logic (Quality, Same Codec Inputs, No Audio) ---
def concatenate_videos(file_list, output_file, status_update_func):
    if not file_list:
        messagebox.showerror("Error", "No videos selected for concatenation.")
        return

    status_update_func("Preparing for concatenation...")
    temp_concat_list_file = None
    try:
        # Use a context manager for the temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".txt", prefix="concat_", encoding='utf-8') as tmp_f:
            temp_concat_list_file = tmp_f.name
            for video_file in file_list:
                safe_path = video_file.replace("\\\\", "/")
                tmp_f.write(f"file '{safe_path}'\\n")

        cmd = [FFMPEG_PATH, "-f", "concat", "-safe", "0", "-i", temp_concat_list_file,
               "-c", "copy",   # Copy video codec (fast, preserves quality)
               "-an",          # No audio
               "-y", output_file] # Overwrite output without asking

        success, _ = run_command(cmd, status_update_func, "Concatenation")
        if success:
            messagebox.showinfo("Success", f"Videos concatenated successfully to:\\n{output_file}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to concatenate videos: {str(e)}")
        status_update_func(f"Concatenation error: {str(e)}")
    finally:
        if temp_concat_list_file and os.path.exists(temp_concat_list_file):
            os.remove(temp_concat_list_file)

# --- Seamless Loop Logic (Quality Prio, Same Codec, No Audio) ---
def create_seamless_loop(video_inputs, output_file, status_update_func, keep_temp_files=False):
    if len(video_inputs) != 4 or not all(video_inputs):
        messagebox.showerror("Error", "Please select exactly 4 video files for the loop.")
        return

    status_update_func("Starting seamless loop creation...")
    temp_dir = tempfile.mkdtemp(prefix="seamless_loop_")
    base_names = ["V1", "V2", "V3", "V4"]
    processed_parts_paths = {}
    safe_files = []

    try:
        # Step 1: Re-encode all input videos to safe intermediate files
        for i, video_path in enumerate(video_inputs):
            base_name = base_names[i]
            safe_path = os.path.join(temp_dir, f"{base_name}_SAFE.mp4")
            status_update_func(f"Re-encoding {base_name} to safe format...")
            cmd_safe = [FFMPEG_PATH, "-i", video_path, "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-r", "30", "-an", "-y", safe_path]
            print("Running re-encode command:", ' '.join(cmd_safe))
            success, out = run_command(cmd_safe, status_update_func, f"Re-encode {base_name}")
            print("FFmpeg output:", out)
            if not success:
                messagebox.showerror("Error", f"Failed to re-encode {base_name}. Aborting.")
                return
            safe_files.append(safe_path)

        # Step 2: Split and reverse as before, but use safe files
        for i, safe_path in enumerate(safe_files):
            base_name = base_names[i]
            status_update_func(f"Processing {base_name}: Getting duration...")
            cmd_duration = [FFPROBE_PATH, "-v", "error", "-show_entries", "format=duration",
                            "-of", "default=noprint_wrappers=1:nokey=1", safe_path]
            success, duration_out = run_command(cmd_duration, status_update_func, f"Duration Check ({base_name})")
            if not success: return
            total_duration = float(duration_out.strip())
            midpoint_duration = total_duration / 2.0

            vxa_path = os.path.join(temp_dir, f"{base_name}A.mp4")
            vxb_path = os.path.join(temp_dir, f"{base_name}B.mp4")
            vxar_path = os.path.join(temp_dir, f"{base_name}AR.mp4")
            vxbr_path = os.path.join(temp_dir, f"{base_name}BR.mp4")

            processed_parts_paths[f"{base_name}A"] = vxa_path
            processed_parts_paths[f"{base_name}B"] = vxb_path
            processed_parts_paths[f"{base_name}AR"] = vxar_path
            processed_parts_paths[f"{base_name}BR"] = vxbr_path

            split_opts = ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-an", "-y"]
            status_update_func(f"Processing {base_name}: Splitting...")
            cmd_split_a = [FFMPEG_PATH, "-i", safe_path, "-t", str(midpoint_duration)] + split_opts + [vxa_path]
            cmd_split_b = [FFMPEG_PATH, "-i", safe_path, "-ss", str(midpoint_duration)] + split_opts + [vxb_path]
            print("Splitting A command:", ' '.join(cmd_split_a))
            print("Splitting B command:", ' '.join(cmd_split_b))
            if not run_command(cmd_split_a, status_update_func, f"Splitting {base_name}A")[0]: return
            if not run_command(cmd_split_b, status_update_func, f"Splitting {base_name}B")[0]: return

            status_update_func(f"Processing {base_name}: Reversing...")
            reverse_encode_opts = ["-vf", "reverse",
                                   "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                                   "-an", "-y"]
            cmd_reverse_a = [FFMPEG_PATH, "-i", vxa_path] + reverse_encode_opts + [vxar_path]
            cmd_reverse_b = [FFMPEG_PATH, "-i", vxb_path] + reverse_encode_opts + [vxbr_path]
            print("Reversing A command:", ' '.join(cmd_reverse_a))
            print("Reversing B command:", ' '.join(cmd_reverse_b))
            if not run_command(cmd_reverse_a, status_update_func, f"Reversing {base_name}A")[0]: return
            if not run_command(cmd_reverse_b, status_update_func, f"Reversing {base_name}B")[0]: return

        status_update_func("All parts processed. Assembling final loop...")
        segment_order_keys = [
            "V1A", "V2B", "V2BR", "V3AR", "V3A", "V4B", "V4BR",
            "V1B", "V1BR", "V2AR", "V2A", "V3B", "V3BR", "V4AR", "V4A", "V1AR"
        ]
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".txt", prefix="loop_concat_", encoding='utf-8') as tmp_f:
            temp_concat_list_file = tmp_f.name
            for key in segment_order_keys:
                safe_path = processed_parts_paths[key].replace("\\\\", "/")
                tmp_f.write(f"file '{safe_path}'\\n")
        
        final_concat_opts = ["-c:v", "libx264", "-preset", "medium", "-crf", "20",
                             "-an", "-movflags", "+faststart", "-y"]
        cmd_final_concat = [FFMPEG_PATH, "-f", "concat", "-safe", "0", "-i", temp_concat_list_file] + final_concat_opts + [output_file]

        print("Final concat command:", ' '.join(cmd_final_concat))
        success, _ = run_command(cmd_final_concat, status_update_func, "Final Loop Assembly")
        if success:
            messagebox.showinfo("Success", f"Seamless loop created successfully:\\n{output_file}")
            status_update_func("Loop creation complete!")
        else:
            status_update_func("Loop creation failed during final assembly.")

    except Exception as e:
        error_msg = f"An unexpected error occurred during loop creation: {str(e)}"
        messagebox.showerror("Loop Creation Error", error_msg)
        status_update_func(error_msg)
        print(error_msg) # For console debugging
        import traceback
        traceback.print_exc() # For more detailed console debugging
    finally:
        if not keep_temp_files and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                status_update_func("Temporary files cleaned up.")
            except Exception as e:
                print(f"Warning: Could not delete temporary directory {temp_dir}: {e}")
                status_update_func(f"Warning: Could not delete temp files in {temp_dir}")
        if 'temp_concat_list_file' in locals() and os.path.exists(temp_concat_list_file):
             os.remove(temp_concat_list_file)


# --- Main Application Class (UI setup as before) ---
class VideoEditorApp:
    def __init__(self, master):
        self.master = master
        master.title(f"Video Loop & Concat Tool (FFmpeg: {'Bundled' if IS_BUNDLED else 'System PATH'})")
        master.geometry("600x520")

        self.notebook = ttk.Notebook(master)
        self.concat_tab = ttk.Frame(self.notebook)
        self.setup_concat_tab()
        self.notebook.add(self.concat_tab, text='Concatenate Videos')

        self.loop_tab = ttk.Frame(self.notebook)
        self.video_loop_paths = [tk.StringVar() for _ in range(4)]
        self.video_loop_labels = [None] * 4
        self.setup_loop_tab()
        self.notebook.add(self.loop_tab, text='Create Seamless Loop (4 Videos)')

        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        self.status_var = tk.StringVar()
        self.status_var.set("Ready. Ensure FFmpeg and FFprobe are accessible.")
        status_bar = tk.Label(master, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padx=5, wraplength=580)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.keep_temp_files_var = tk.BooleanVar(value=False)
        keep_temp_check = tk.Checkbutton(master, text="Keep temporary files", variable=self.keep_temp_files_var)
        keep_temp_check.pack(side=tk.BOTTOM, anchor=tk.E, padx=5, before=status_bar) # Place before status bar

        # Initial check for FFmpeg/FFprobe
        if not self.check_ffmpeg_tools_on_startup():
            # Optionally disable buttons if tools are missing
            pass


    def update_status(self, message):
        self.status_var.set(message)
        self.master.update_idletasks()

    def check_ffmpeg_tools_on_startup(self):
        self.update_status("Checking for FFmpeg and FFprobe...")
        creationflags = 0
        if os.name == 'nt': creationflags = subprocess.CREATE_NO_WINDOW
        try:
            # Check FFMPEG_PATH
            ffmpeg_check_cmd = [FFMPEG_PATH, "-version"]
            ffmpeg_process = subprocess.run(ffmpeg_check_cmd, capture_output=True, text=True, check=True, encoding='utf-8', errors='replace', creationflags=creationflags)
            if "ffmpeg version" not in ffmpeg_process.stdout.lower(): # Basic check
                raise FileNotFoundError("FFmpeg version string not found.")
            
            # Check FFPROBE_PATH
            ffprobe_check_cmd = [FFPROBE_PATH, "-version"]
            ffprobe_process = subprocess.run(ffprobe_check_cmd, capture_output=True, text=True, check=True, encoding='utf-8', errors='replace', creationflags=creationflags)
            if "ffprobe version" not in ffprobe_process.stdout.lower(): # Basic check
                raise FileNotFoundError("FFprobe version string not found.")

            self.update_status(f"FFmpeg & FFprobe found. Ready. (Using: {'Bundled' if IS_BUNDLED else 'System'})")
            return True
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            error_msg = f"FFmpeg/FFprobe not found or not working.\\nUsing paths:\\nFFMPEG: {FFMPEG_PATH}\\nFFPROBE: {FFPROBE_PATH}\\nError: {e}"
            if isinstance(e, subprocess.CalledProcessError):
                error_msg += f"\\nOutput:\\n{e.stdout}\\n{e.stderr}"
            messagebox.showwarning("Missing Tools", error_msg)
            self.update_status("FFmpeg/FFprobe not found! Please install/configure or check bundled files.")
            return False

    # ... (setup_concat_tab, add_concat_video, remove_concat_video, move_concat_video as before) ...
    def setup_concat_tab(self): # Copied from previous, ensure it's complete
        frame = self.concat_tab
        tk.Label(frame, text="Selected Videos for Concatenation:").pack(pady=(10,0), anchor="w", padx=5)

        self.concat_listbox_frame = tk.Frame(frame)
        self.concat_listbox_frame.pack(pady=5, fill=tk.BOTH, expand=True, padx=5)
        
        self.concat_listbox_scrollbar = tk.Scrollbar(self.concat_listbox_frame, orient=tk.VERTICAL)
        self.concat_listbox = tk.Listbox(self.concat_listbox_frame, selectmode=tk.SINGLE, height=10, yscrollcommand=self.concat_listbox_scrollbar.set)
        self.concat_listbox_scrollbar.config(command=self.concat_listbox.yview)
        
        self.concat_listbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.concat_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.concat_files = []

        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=5, padx=5)

        ttk.Button(btn_frame, text="Add Video(s)", command=self.add_concat_video).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Remove Selected", command=self.remove_concat_video).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Move Up", command=lambda: self.move_concat_video(-1)).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Move Down", command=lambda: self.move_concat_video(1)).pack(side=tk.LEFT, padx=2)

        ttk.Button(frame, text="Concatenate & Save As...", command=self.start_concatenate_thread).pack(pady=10, fill=tk.X, padx=5)

    def add_concat_video(self): # Copied from previous
        files = filedialog.askopenfilenames(title="Select Videos",
                                             filetypes=(("Video Files", "*.mp4 *.avi *.mov *.mkv"),
                                                        ("All files", "*.*")))
        if files:
            for f_path in files:
                if f_path not in self.concat_files:
                    self.concat_files.append(f_path)
                    self.concat_listbox.insert(tk.END, os.path.basename(f_path))
            self.update_status(f"{len(files)} video(s) added to concatenation list.")

    def remove_concat_video(self): # Copied from previous
        selected_indices = self.concat_listbox.curselection()
        if selected_indices:
            # Remove from bottom up to avoid index shifting issues
            for index in sorted(selected_indices, reverse=True):
                self.concat_listbox.delete(index)
                del self.concat_files[index]
            self.update_status("Video(s) removed from concatenation list.")

    def move_concat_video(self, direction): # Copied from previous, improved for multi-selection (though listbox is single)
        selected_indices = self.concat_listbox.curselection()
        if not selected_indices:
            return
        idx = selected_indices[0] # Listbox is single select
        new_idx = idx + direction

        if 0 <= new_idx < len(self.concat_files):
            self.concat_files[idx], self.concat_files[new_idx] = self.concat_files[new_idx], self.concat_files[idx]
            
            item_text = self.concat_listbox.get(idx)
            self.concat_listbox.delete(idx)
            self.concat_listbox.insert(new_idx, item_text)
            
            self.concat_listbox.selection_clear(0, tk.END)
            self.concat_listbox.selection_set(new_idx)
            self.concat_listbox.activate(new_idx)
            self.update_status("Video moved in list.")

    def start_concatenate_thread(self): # Updated for clarity
        if not self.concat_files:
            messagebox.showerror("Error", "No videos selected to concatenate.")
            return
        output_file = filedialog.asksaveasfilename(title="Save Concatenated Video As",
                                                   defaultextension=".mp4",
                                                   filetypes=(("MP4 Video", "*.mp4"), ("All files", "*.*")))
        if output_file:
            # Make a copy of the list for the thread to prevent modification issues if UI is interacted with
            files_to_process = list(self.concat_files)
            thread = threading.Thread(target=concatenate_videos,
                                      args=(files_to_process, output_file, self.update_status))
            thread.daemon = True
            thread.start()

    # ... (setup_loop_tab, select_loop_video as before) ...
    def setup_loop_tab(self): # Copied from previous
        frame = self.loop_tab
        tk.Label(frame, text="Select 4 videos for the seamless loop:").pack(pady=(10,5), anchor="w", padx=5)

        # New: Button to select all 4 videos at once
        def select_all_4_videos():
            files = filedialog.askopenfilenames(title="Select 4 Videos",
                                                filetypes=(("Video Files", "*.mp4 *.avi *.mov *.mkv"), ("All files", "*.*")))
            if len(files) != 4:
                messagebox.showwarning("Input Error", "Please select exactly 4 video files.")
                return
            for i in range(4):
                self.video_loop_paths[i].set(files[i])
                self.update_status(f"Video {i+1} selected: {os.path.basename(files[i])}")

        ttk.Button(frame, text="Select 4 Videos...", command=select_all_4_videos).pack(pady=(0,8), fill=tk.X, padx=5)

        for i in range(4):
            row_frame = tk.Frame(frame)
            row_frame.pack(fill=tk.X, pady=2, padx=5)
            ttk.Button(row_frame, text=f"Select Video {i+1}",
                       command=lambda idx=i: self.select_loop_video(idx)).pack(side=tk.LEFT, padx=5)
            # Using Entry with readonly state to make it look like a label but allow text copying
            self.video_loop_labels[i] = ttk.Entry(row_frame, textvariable=self.video_loop_paths[i], state="readonly", width=60)
            self.video_loop_labels[i].pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(frame, text="Create Loop & Save As...", command=self.start_create_loop_thread).pack(pady=20, fill=tk.X, padx=5)

    def select_loop_video(self, index): # Modified to show full path in readonly Entry
        file = filedialog.askopenfilename(title=f"Select Video {index+1}",
                                          filetypes=(("Video Files", "*.mp4 *.avi *.mov *.mkv"),
                                                     ("All files", "*.*")))
        if file:
            self.video_loop_paths[index].set(file) # StringVar updated, Entry updates
            self.update_status(f"Video {index+1} selected: {os.path.basename(file)}")

    def start_create_loop_thread(self): # Updated for clarity
        selected_videos = [var.get() for var in self.video_loop_paths]
        if not all(p and os.path.exists(p) for p in selected_videos) or len(selected_videos) != 4:
            messagebox.showerror("Input Error", "Please select 4 valid video files.")
            return

        output_file = filedialog.asksaveasfilename(title="Save Seamless Loop As",
                                                   defaultextension=".mp4",
                                                   filetypes=(("MP4 Video", "*.mp4"), ("All files", "*.*")))
        if output_file:
            thread = threading.Thread(target=create_seamless_loop,
                                      args=(selected_videos, output_file, self.update_status, self.keep_temp_files_var.get()))
            thread.daemon = True
            thread.start()


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoEditorApp(root)
    root.mainloop()
""" # End of VIDEO_TOOL_APP_CODE string


# --- Bootstrapper Helper Functions ---
def get_platform_specific_paths(project_root_dir, venv_name_local):
    """Gets platform-specific paths for venv python."""
    if platform.system() == "Windows":
        python_executable = os.path.join(project_root_dir, venv_name_local, "Scripts", "python.exe")
    else:
        python_executable = os.path.join(project_root_dir, venv_name_local, "bin", "python")
    return python_executable

def run_bootstrap_subprocess(command_list, cwd=None, env_vars=None, desc="command"):
    """Helper to run subprocess commands for bootstrapping, prints stdout/stderr."""
    print(f"Bootstrapper: Running {desc}: {' '.join(command_list)}")
    try:
        # For bootstrapping, show output directly
        process = subprocess.run(command_list, cwd=cwd, env=env_vars, capture_output=True, text=True, encoding='utf-8', errors='replace')
        if process.stdout:
            print(f"Output of {desc}:\n{process.stdout}")
        if process.stderr:
            print(f"Error output of {desc}:\n{process.stderr}", file=sys.stderr)
        
        if process.returncode != 0:
            print(f"Bootstrapper Error: {desc} failed with code {process.returncode}", file=sys.stderr)
            return False
        print(f"Bootstrapper: {desc} completed successfully.")
        return True
    except FileNotFoundError:
        print(f"Bootstrapper Error: Command not found - {command_list[0]}. Is Python/venv module available?", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Bootstrapper Exception running {desc}: {e}", file=sys.stderr)
        return False

def locate_ffmpeg_executables(project_root_dir, ffmpeg_subdir_name):
    """
    Locates FFmpeg and FFprobe.
    Priority:
    1. Predefined subdirectory within the project (`ffmpeg_subdir_name`).
    2. System PATH.
    Returns (ffmpeg_path, ffprobe_path) or (None, None).
    """
    ffmpeg_exe = "ffmpeg.exe" if platform.system() == "Windows" else "ffmpeg"
    ffprobe_exe = "ffprobe.exe" if platform.system() == "Windows" else "ffprobe"

    # 1. Check local project subdirectory
    local_ffmpeg = os.path.join(project_root_dir, ffmpeg_subdir_name, ffmpeg_exe)
    local_ffprobe = os.path.join(project_root_dir, ffmpeg_subdir_name, ffprobe_exe)

    if os.path.isfile(local_ffmpeg) and os.path.isfile(local_ffprobe):
        print(f"Bootstrapper: Found FFmpeg/FFprobe in local directory: {os.path.join(project_root_dir, ffmpeg_subdir_name)}")
        return os.path.abspath(local_ffmpeg), os.path.abspath(local_ffprobe)

    # 2. Check system PATH
    print(f"Bootstrapper: FFmpeg/FFprobe not in local '{ffmpeg_subdir_name}'. Checking system PATH...")
    try:
        # Use shutil.which to reliably find executables in PATH
        system_ffmpeg = shutil.which(ffmpeg_exe)
        system_ffprobe = shutil.which(ffprobe_exe)

        if system_ffmpeg and system_ffprobe:
            print(f"Bootstrapper: Found FFmpeg ({system_ffmpeg}) and FFprobe ({system_ffprobe}) in system PATH.")
            return system_ffmpeg, system_ffprobe # Return full paths found
        else:
            missing = []
            if not system_ffmpeg: missing.append("ffmpeg")
            if not system_ffprobe: missing.append("ffprobe")
            print(f"Bootstrapper Error: {', '.join(missing)} not found in system PATH.", file=sys.stderr)
            return None, None
    except Exception as e:
        print(f"Bootstrapper Error: Could not verify FFmpeg/FFprobe in system PATH: {e}", file=sys.stderr)
        return None, None

# --- Main Bootstrapper Logic ---
def main():
    print("--- Video Tool Bootstrapper ---")

    # 1. Define and Create Project Structure
    # Project root will be created in the same directory as this bootstrapper script
    bootstrapper_script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(bootstrapper_script_dir, PROJECT_ROOT_DIR_NAME)
    venv_dir = os.path.join(project_root, VENV_DIR_NAME)
    app_script_target_path = os.path.join(project_root, APP_SCRIPT_FILENAME)
    ffmpeg_bin_dir = os.path.join(project_root, FFMPEG_BIN_SUBDIR)

    print(f"Target project directory: {project_root}")
    if not os.path.exists(project_root):
        print(f"Creating project directory: {project_root}")
        os.makedirs(project_root)
    
    if not os.path.exists(ffmpeg_bin_dir):
        print(f"Creating FFmpeg/FFprobe subdirectory: {ffmpeg_bin_dir}")
        os.makedirs(ffmpeg_bin_dir)
        print(f"INFO: If FFmpeg/FFprobe are not in your system PATH, please place the executables"
              f"\n      (ffmpeg.exe & ffprobe.exe for Windows, or ffmpeg & ffprobe for Linux/macOS)"
              f"\n      into this directory: {ffmpeg_bin_dir}")


    # 2. Locate FFmpeg/FFprobe
    print("\nBootstrapper: Locating FFmpeg and FFprobe...")
    ffmpeg_path_resolved, ffprobe_path_resolved = locate_ffmpeg_executables(project_root, FFMPEG_BIN_SUBDIR)

    if not (ffmpeg_path_resolved and ffprobe_path_resolved):
        print("\nBootstrapper Critical Error: FFmpeg/FFprobe could not be located.", file=sys.stderr)
        print("Please ensure they are in your system PATH, or place the executables "
              f"(e.g., ffmpeg.exe, ffprobe.exe) into the '{ffmpeg_bin_dir}' directory "
              "that was just created (if it wasn't already present), and then re-run this script.", file=sys.stderr)
        return 1 # Indicate error
    print(f"Bootstrapper: Using FFmpeg from: {ffmpeg_path_resolved}")
    print(f"Bootstrapper: Using FFprobe from: {ffprobe_path_resolved}")


    # 3. Create Virtual Environment if it doesn't exist
    print(f"\nBootstrapper: Checking for virtual environment at: {venv_dir}")
    venv_python_executable = get_platform_specific_paths(project_root, VENV_DIR_NAME)

    if not os.path.exists(venv_python_executable):
        print("Bootstrapper: Virtual environment not found. Creating...")
        try:
            # Using subprocess to call 'python -m venv' for better cross-Python compatibility
            # and to ensure it uses the Python that's running *this* script.
            python_exe_for_venv = sys.executable # Use the same python that is running this script
            if not run_bootstrap_subprocess([python_exe_for_venv, "-m", "venv", venv_dir],
                                       desc="Create Virtual Environment"):
                print("Bootstrapper Error: Failed to create virtual environment.", file=sys.stderr)
                return 1
            print("Bootstrapper: Virtual environment created successfully.")
        except Exception as e:
            print(f"Bootstrapper Error creating virtual environment: {e}", file=sys.stderr)
            return 1
    else:
        print("Bootstrapper: Virtual environment already exists.")

    # 4. Install Dependencies (if any were needed, e.g., for FFmpeg download)
    # print("\nBootstrapper: Checking/installing Python dependencies (if any)...")
    # For this app, no external Python libs are needed by the UI app itself.

    # 5. Write the embedded UI application code to its .py file
    print(f"\nBootstrapper: Writing UI application script to: {app_script_target_path}")
    try:
        with open(app_script_target_path, "w", encoding="utf-8") as f:
            f.write(VIDEO_TOOL_APP_CODE)
        print("Bootstrapper: UI application script written successfully.")
    except IOError as e:
        print(f"Bootstrapper Error writing UI application script: {e}", file=sys.stderr)
        return 1

    # 6. Launch the UI application using the venv's Python
    print(f"\nBootstrapper: Launching UI application ({APP_SCRIPT_FILENAME})...")
    app_env = os.environ.copy()
    app_env['BOOTSTRAP_FFMPEG_PATH'] = ffmpeg_path_resolved
    app_env['BOOTSTRAP_FFPROBE_PATH'] = ffprobe_path_resolved
    # Add venv's scripts/bin to PATH for the app, in case it needs to find other venv tools
    # (though not strictly necessary if calling venv_python_executable directly)
    venv_scripts_or_bin = os.path.join(venv_dir, "Scripts" if platform.system() == "Windows" else "bin")
    app_env['PATH'] = venv_scripts_or_bin + os.pathsep + app_env.get('PATH', '')


    # Using subprocess.call to wait for the UI app to close
    # The UI app (Tkinter) will run its own mainloop.
    if not run_bootstrap_subprocess([venv_python_executable, app_script_target_path],
                               cwd=project_root, env_vars=app_env,
                               desc="Launch UI Application"):
        print("Bootstrapper: UI application did not launch or exited with an error.", file=sys.stderr)
        return 1
    
    print("\nBootstrapper: UI application finished.")
    print(f"You can find the project files at: {project_root}")
    print(f"To run the UI application again without this bootstrapper, activate the venv ({venv_dir}) "
          f"and run '{APP_SCRIPT_FILENAME}' from '{project_root}'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())