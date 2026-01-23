import os
import glob
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from functools import partial

class FileSelectorGUI:
    def __init__(self, master):
        self.master = master
        master.title("File Selector for Steps 01-06 with Substeps")
        master.geometry("800x600")
        master.resizable(True, True)

        self.base_dir = "."
        self.node_dir = "node"
        self.steps = [
            "01_Potential",
            "02_Symmetry",
            "03_Flow",
            "04_Connectivity",
            "05_Emergence",
            "06_Recursion"
        ]
        self.file_types = {
            "01_Potential": {
                "Seed/Law": ["fn.xx.law"],
                "Energy/Dynamics": ["fn.xx.dyn"]
            },
            "02_Symmetry": {
                "Constraints/Resonance": ["im.xx.pol", "ap.xx.reso"],
                "Tuning/Harmony": ["im.xx.vib", "ap.xx.tun"]
            },
            "03_Flow": {
                "Expansion/Logic": ["im.xx.flw", "im.xx.rhy"],
                "Transformation/Rule": ["im.xx.convert", "im.xx.update"]
            },
            "04_Connectivity": {
                "Bridging/Rule": ["im.xx.bridge", "im.xx.rule"],
                "Style/Mapping": ["im.xx.atm", "im.xx.cha"]
            },
            "05_Emergence": {
                "Synthesis/Design": ["ex.xx.syn", "ds.xx.sheet"],
                "Insights/Utility": ["ex.xx.utl", "ex.xx.per"]
            },
            "06_Recursion": {
                "Feedback": ["ex.xx.feedback", "ap.xx.reso"],
                "Control": ["im.xx.clk", "im.xx.rnd", "ex.xx.size"]
            }
        }
        self.selected_files = {step: {substep: None for substep in self.file_types[step]} for step in self.steps}

        # Ensure directories exist
        self.ensure_directories()

        # Create UI elements
        self.create_widgets()

        # Initialize default selections to 'init' files if they exist
        self.initialize_defaults()
    def ensure_directories(self):
        """Ensure that all step directories exist."""
        for step in self.steps:
            step_dir = os.path.join(self.base_dir, self.node_dir, step)
            os.makedirs(step_dir, exist_ok=True)

    def create_widgets(self):
        # Create a main frame to hold everything
        main_frame = tk.Frame(self.master, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create a canvas and scrollbar for the scrollable frame
        canvas = tk.Canvas(main_frame, bg="#f0f0f0")
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

         # Styling configurations with reduced font sizes
        label_font = ("Helvetica", 10, "bold")          # Reduced from 12
        substep_label_font = ("Helvetica", 9, "bold")   # Reduced from 11
        entry_font = ("Helvetica", 8)                    # Reduced from 10
        button_font = ("Helvetica", 9, "bold")          # Reduced from 10
        submit_button_font = ("Helvetica", 12, "bold")  # Reduced from 14

        # Initialize row counter for scrollable_frame
        current_row = 0


        # Create labels and buttons for each step and its substeps
        self.file_vars = {}  # To keep references to StringVar for each substep
        for step in self.steps:
            # Step Label
            step_label = tk.Label(scrollable_frame, text=step, anchor="w", bg="#cccccc",
                                  relief="groove", font=label_font)
            step_label.grid(row=current_row, column=0, sticky="w", padx=5, pady=(8, 3), columnspan=3, ipadx=3)
            current_row += 1

            # Substeps
            for substep in self.file_types[step]:
                # Substep Label
                substep_label = tk.Label(scrollable_frame, text=substep, anchor="w", bg="#e6e6e6",
                                         relief="ridge", font=substep_label_font)
                substep_label.grid(row=current_row, column=0, sticky="w", padx=15, pady=2)

                # File Entry
                file_var = tk.StringVar()
                self.file_vars[(step, substep)] = file_var
                file_entry = tk.Entry(scrollable_frame, textvariable=file_var, width=50, state='readonly',
                                      font=entry_font, bg="#f2f2f2")
                file_entry.grid(row=current_row, column=1, padx=5, pady=2)

                # Browse Button
                browse_button = tk.Button(
                    scrollable_frame,
                    text="Browse",
                    command=partial(self.browse_file, step, substep, file_var),
                    font=button_font,
                    bg="#4CAF50",
                    fg="white",
                    activebackground="#45a049",
                    padx=8,
                    pady=2
                )
                browse_button.grid(row=current_row, column=2, padx=5, pady=2)
                current_row += 1


        # Create a control frame for the "Synergize" button
        control_frame = tk.Frame(main_frame, bg="#f0f0f0")
        control_frame.pack(fill=tk.X, pady=(5, 0))


        # Create a submit button with customized appearance
        submit_button = tk.Button(
            control_frame,
            text="Synergize",
            command=self.show_selections_window, # Modified command to call new window
            bg="#808080",  # Grey background
            fg="white",
            font=submit_button_font,  # Reduced from 14
            activebackground="#696969",
            activeforeground="white",
            padx=15,  # Adjusted padding
            pady=5    # Adjusted padding
        )
        submit_button.pack(pady=5)

    def browse_file(self, step, substep, file_var):
      step_dir = os.path.join(self.base_dir, self.node_dir, step)
      if not os.path.exists(step_dir):
            messagebox.showerror("Error", f"Directory does not exist: {step_dir}")
            return

      # Get allowed file types for the substep
      allowed_extensions = self.file_types[step][substep]
        # Create filetype tuples for filedialog
      filetype_tuples = [("Allowed files", f"*{ext}") for ext in allowed_extensions]
      filetype_tuples.append(("All files", "*.*"))  # Allow all files as fallback

      # Open file dialog restricted to the step's directory and allowed file types
      file_path = filedialog.askopenfilename(
            initialdir=step_dir,
            title=f"Select a file for {step} - {substep}",
            filetypes=filetype_tuples
       )

      if file_path:
            self.selected_files[step][substep] = file_path
            file_var.set(file_path)


    def initialize_defaults(self):
        """Automatically select 'init' files if they exist in each substep's directory."""
        for step in self.steps:
            for substep in self.file_types[step]:
                step_dir = os.path.join(self.base_dir, self.node_dir, step)
                # Assuming 'init' files follow the pattern 'init.*'
                init_file_pattern = os.path.join(step_dir, "init*")
                init_files = glob.glob(init_file_pattern)

                if init_files:
                    # If multiple 'init' files exist, select the first one
                    init_file = init_files[0]
                    # Update selected_files and entry
                    self.selected_files[step][substep] = init_file
                    self.file_vars[(step, substep)].set(init_file)
                    print(f"Defaulted '{step}' - '{substep}' to '{init_file}'")
                else:
                    print(f"No 'init' file found for '{step}' - '{substep}'")


    def show_selections_window(self):
        """Creates a new window to display selected files."""

        # Check if at least one file is selected
        if not any(
           file_path
            for step in self.steps
            for file_path in self.selected_files[step].values()
        ):
            messagebox.showwarning("No Selections", "Please select at least one file before synergizing.")
            return

        # Collect the selected files
        selections = ""
        for step in self.steps:
            selections += f"--- {step} ---\n"
            for substep in self.file_types[step]:
                file_path = self.selected_files[step][substep]
                selections += f"  {substep} : {file_path if file_path else 'None'}\n"
            selections += "\n"

        # Create new Toplevel window
        selection_window = tk.Toplevel(self.master)
        selection_window.title("Selected Files")

        # Add scrolled text to display selected files
        text_area = scrolledtext.ScrolledText(selection_window, wrap=tk.WORD, width=80, height=20)
        text_area.insert(tk.INSERT, selections)
        text_area.config(state=tk.DISABLED)  # Make it read-only
        text_area.pack(padx=10, pady=10)


        # Add a button to copy the text area to the clipboard
        copy_button = tk.Button(selection_window, text="Copy to Clipboard", command=lambda: self.copy_text_to_clipboard(text_area))
        copy_button.pack(pady=5)


    def copy_text_to_clipboard(self, text_area):
      """Copies text from a ScrolledText area to the clipboard."""
      self.master.clipboard_clear()
      self.master.clipboard_append(text_area.get("1.0", tk.END))
      messagebox.showinfo("Clipboard", "Selected files copied to clipboard")




def main():
    root = tk.Tk()
    app = FileSelectorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()