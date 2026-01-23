
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
    """ Get absolute path to resource, works for dev and for PyInstaller """ # This line too
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
            error_msg = f"{operation_name} Error (Code {process.returncode}):\n{_raw_error_output!r}"
            print(error_msg)
            messagebox.showerror(f"{operation_name} Error", error_msg)
            app_status_update_func(f"{operation_name} failed.")
            return False, stderr or stdout
        app_status_update_func(f"{operation_name} successful.")
        return True, stdout
    except FileNotFoundError:
        error_msg = f"{operation_name} (e.g., {command_list[0]}) not found. Please ensure it's installed correctly."
        if IS_BUNDLED:
             error_msg += f"\nExpected at: {command_list[0]}"
        else:
            error_msg += "\nEnsure it's in your system PATH for development."
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
                safe_path = video_file.replace("\\", "/")
                tmp_f.write(f"file '{safe_path}'\n")

        cmd = [FFMPEG_PATH, "-f", "concat", "-safe", "0", "-i", temp_concat_list_file,
               "-c", "copy",   # Copy video codec (fast, preserves quality)
               "-an",          # No audio
               "-y", output_file] # Overwrite output without asking

        success, _ = run_command(cmd, status_update_func, "Concatenation")
        if success:
            messagebox.showinfo("Success", f"Videos concatenated successfully to:\n{output_file}")
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
                safe_path = processed_parts_paths[key].replace("\\", "/")
                tmp_f.write(f"file '{safe_path}'\n")
        
        final_concat_opts = ["-c:v", "libx264", "-preset", "medium", "-crf", "20",
                             "-an", "-movflags", "+faststart", "-y"]
        cmd_final_concat = [FFMPEG_PATH, "-f", "concat", "-safe", "0", "-i", temp_concat_list_file] + final_concat_opts + [output_file]

        print("Final concat command:", ' '.join(cmd_final_concat))
        success, _ = run_command(cmd_final_concat, status_update_func, "Final Loop Assembly")
        if success:
            messagebox.showinfo("Success", f"Seamless loop created successfully:\n{output_file}")
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
            error_msg = f"FFmpeg/FFprobe not found or not working.\nUsing paths:\nFFMPEG: {FFMPEG_PATH}\nFFPROBE: {FFPROBE_PATH}\nError: {e}"
            if isinstance(e, subprocess.CalledProcessError):
                error_msg += f"\nOutput:\n{e.stdout}\n{e.stderr}"
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
