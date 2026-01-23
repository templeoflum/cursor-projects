import tkinter as tk
from tkinter import filedialog, messagebox
import traceback

class LightweightDevEnvUI(tk.Tk):
    """
    Minimal environment for editing and testing small Tkinter UI scripts,
    with a live debug console.
    """
    def __init__(self):
        super().__init__()
        self.title("Lightweight UI Dev Environment (With Debug Console)")

        # Child window reference (preview)
        self.child_window = None

        # Debug console references
        self.debug_window = None
        self.debug_text = None

        # Build interface
        self._build_menu()
        self._build_main_layout()

        # Insert a basic hello world script into the editor
        sample_code = """import tkinter as tk

def build_ui(root, params):
    # A minimal "Hello World" UI to test quickly
    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)

    label = tk.Label(frame, text="Hello World!", bg="lightblue")
    label.pack(pady=10)

    return frame
"""
        self.editor.insert("1.0", sample_code)

    def _build_menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="New", command=self.new_script)
        file_menu.add_command(label="Open...", command=self.open_script)
        file_menu.add_command(label="Save...", command=self.save_script)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        script_menu = tk.Menu(menubar, tearoff=False)
        script_menu.add_command(label="Run", command=self.run_script)
        script_menu.add_command(label="Close Preview", command=self.close_preview)
        script_menu.add_command(label="Show Debug Console", command=self.show_debug_window)
        menubar.add_cascade(label="Script", menu=script_menu)

        help_menu = tk.Menu(menubar, tearoff=False)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menubar)

    def _build_main_layout(self):
        container = tk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True)

        # Side panel for parameters
        self.side_panel = tk.Frame(container, bg="#fafafa", width=180)
        self.side_panel.pack(side=tk.LEFT, fill=tk.Y)

        # Example sliders (optional for "Hello World")
        self.param_vars = {
            "slider1": tk.DoubleVar(value=0.5),
            "slider2": tk.DoubleVar(value=0.2),
        }

        tk.Label(self.side_panel, text="Parameters:", bg="#fafafa").pack(pady=(10,5))
        for name, var in self.param_vars.items():
            tk.Label(self.side_panel, text=name, bg="#fafafa").pack(anchor="w", padx=5)
            scale = tk.Scale(
                self.side_panel, from_=0.0, to=1.0, resolution=0.01,
                orient=tk.HORIZONTAL, variable=var
            )
            scale.pack(fill=tk.X, padx=5, pady=(0,10))

        # Editor area
        editor_frame = tk.Frame(container)
        editor_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(editor_frame, text="Code Editor:").pack(anchor="w", padx=5, pady=5)
        self.editor = tk.Text(editor_frame, wrap="none", height=20)
        self.editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0,5))

    # ---------------------------
    # Menu / Button Callbacks
    # ---------------------------
    def new_script(self):
        self.editor.delete("1.0", tk.END)

    def open_script(self):
        fname = filedialog.askopenfilename(
            title="Open Python Script",
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        if fname:
            with open(fname, "r", encoding="utf-8") as f:
                contents = f.read()
            self.editor.delete("1.0", tk.END)
            self.editor.insert("1.0", contents)

    def save_script(self):
        fname = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        if fname:
            code = self.editor.get("1.0", tk.END)
            with open(fname, "w", encoding="utf-8") as f:
                f.write(code)

    def run_script(self):
        """
        Run the code from the editor in a new (or re-used) Toplevel preview.
        Looks for a 'build_ui' function that receives (root, params).
        """
        self.close_preview()  # Close old preview if open
        self.show_debug_window()  # Ensure debug window is available

        code = self.editor.get("1.0", tk.END)
        local_ns = {}

        # Log a message to debug console
        self.log_debug("Running script...\n")

        try:
            exec(code, {}, local_ns)
            if "build_ui" in local_ns:
                self.child_window = tk.Toplevel(self)
                self.child_window.title("Preview")
                params = {k: v.get() for k, v in self.param_vars.items()}
                local_ns["build_ui"](self.child_window, params)
                self.log_debug("Script ran successfully.\n")
            else:
                msg = "No build_ui function found.\n"
                self.log_debug(msg)
        except Exception:
            err_msg = traceback.format_exc()
            self.log_debug(f"Error:\n{err_msg}\n")

    def close_preview(self):
        if self.child_window is not None:
            self.child_window.destroy()
            self.child_window = None

    def show_debug_window(self):
        """
        Creates or raises the debug console window so we can see logs and errors.
        """
        if self.debug_window is None or not tk.Toplevel.winfo_exists(self.debug_window):
            self._create_debug_window()
        else:
            self.debug_window.deiconify()
            self.debug_window.lift()

    def _create_debug_window(self):
        """
        Actually instantiate the debug console window.
        """
        self.debug_window = tk.Toplevel(self)
        self.debug_window.title("Debug Console")

        # We'll add a text widget for the debug log
        text_frame = tk.Frame(self.debug_window)
        text_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.debug_text = tk.Text(text_frame, wrap="none", yscrollcommand=scrollbar.set)
        self.debug_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.debug_text.yview)

        # Optional: a button to clear the debug console
        clear_btn = tk.Button(self.debug_window, text="Clear", command=self._clear_debug)
        clear_btn.pack(side=tk.BOTTOM, pady=5)

    def _clear_debug(self):
        if self.debug_text:
            self.debug_text.delete("1.0", tk.END)

    def log_debug(self, message):
        """
        Append a message to the debug console text widget.
        If the console doesn't exist yet, create it.
        """
        if not self.debug_window or not tk.Toplevel.winfo_exists(self.debug_window):
            self._create_debug_window()
        self.debug_text.insert(tk.END, message)
        self.debug_text.see(tk.END)  # auto-scroll to bottom

    def show_about(self):
        messagebox.showinfo(
            "About",
            "Lightweight UI Dev Environment (With Debug Console)\n\n"
            "Granular control at high speed.\n"
            "Small decisions, big creativity."
        )

if __name__ == "__main__":
    app = LightweightDevEnvUI()
    app.mainloop()
