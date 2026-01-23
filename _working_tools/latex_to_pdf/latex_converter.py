import tkinter as tk
from tkinter import messagebox
import os
from latex import build_pdf

class LatexConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LaTeX to PDF Converter")
        
        # Create main frame
        self.main_frame = tk.Frame(self.root, padx=10, pady=10)
        self.main_frame.pack(expand=True, fill='both')
        
        # Create and pack widgets
        self.create_widgets()
        
    def create_widgets(self):
        # Instructions label
        instructions = "Paste your LaTeX code below:"
        tk.Label(self.main_frame, text=instructions).pack(pady=5)
        
        # Text input area
        self.text_input = tk.Text(self.main_frame, height=20, width=60)
        self.text_input.pack(pady=5)
        
        # Default LaTeX code
        default_text = r"""\documentclass{article}
\begin{document}
Your LaTeX code here...
\end{document}"""
        self.text_input.insert('1.0', default_text)
        
        # Convert button
        tk.Button(
            self.main_frame,
            text="Convert to PDF",
            command=self.convert_to_pdf
        ).pack(pady=10)
        
    def convert_to_pdf(self):
        try:
            # Get the LaTeX code from the text input
            latex_code = self.text_input.get('1.0', tk.END)
            
            # Generate PDF with more detailed error reporting
            try:
                pdf = build_pdf(latex_code)
            except RuntimeError as latex_error:
                messagebox.showerror(
                    "LaTeX Error",
                    "LaTeX compilation failed. Make sure you have LaTeX installed.\n"
                    "For Windows: Install MiKTeX\n"
                    "For macOS: Install MacTeX\n"
                    "For Linux: sudo apt-get install texlive-full\n\n"
                    f"Error details: {str(latex_error)}"
                )
                return
            
            # Save the PDF
            output_path = "output.pdf"
            with open(output_path, 'wb') as f:
                f.write(bytes(pdf))
            
            messagebox.showinfo(
                "Success",
                f"PDF has been created successfully!\nSaved as: {os.path.abspath(output_path)}"
            )
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"An error occurred while creating the PDF:\n{str(e)}"
            )

if __name__ == "__main__":
    root = tk.Tk()
    app = LatexConverterGUI(root)
    root.mainloop() 