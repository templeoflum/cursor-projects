import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from funnel_data import FunnelData
from horizontal_funnel import HorizontalFunnelView
from animated_funnel import AnimatedFunnelView

class FunnelLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Funnel Visualization Launcher")
        self.root.geometry("800x600")
        
        # Current funnel data
        self.funnel_data = self.load_most_recent_funnel()
        
        self.setup_ui()

    def setup_ui(self):
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(main_frame, 
                              text="Marketing Funnel Visualizer", 
                              font=("Arial", 24, "bold"))
        title_label.pack(pady=20)

        # Data Management Frame
        data_frame = ttk.LabelFrame(main_frame, text="Funnel Data", padding="10")
        data_frame.pack(fill=tk.X, pady=10)

        data_buttons = ttk.Frame(data_frame)
        data_buttons.pack(fill=tk.X, pady=5)

        ttk.Button(data_buttons, 
                  text="New Funnel", 
                  command=self.create_new_funnel).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(data_buttons, 
                  text="Load Funnel", 
                  command=self.load_funnel).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(data_buttons, 
                  text="Save Funnel", 
                  command=self.save_funnel).pack(side=tk.LEFT, padx=5)

        # Status label
        status_text = "No funnel loaded" if not self.funnel_data else f"Loaded: {self.funnel_data.title}"
        self.status_label = ttk.Label(data_frame, text=status_text, font=("Arial", 10))
        self.status_label.pack(pady=5)

        # Visualization Frame
        viz_frame = ttk.LabelFrame(main_frame, text="Visualizations", padding="10")
        viz_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Visualization buttons
        ttk.Button(viz_frame, 
                  text="Classic Vertical Funnel", 
                  command=self.launch_classic_funnel).pack(fill=tk.X, pady=5)
        
        ttk.Button(viz_frame, 
                  text="Horizontal Funnel", 
                  command=self.launch_horizontal_funnel).pack(fill=tk.X, pady=5)
        
        ttk.Button(viz_frame, 
                  text="Animated Funnel", 
                  command=self.launch_animated_funnel).pack(fill=tk.X, pady=5)
        
        ttk.Button(viz_frame, 
                  text="Web Funnel", 
                  command=self.launch_web_funnel).pack(fill=tk.X, pady=5)

    def create_new_funnel(self):
        self.funnel_data = FunnelData()
        self.status_label.config(text=f"New funnel created: {self.funnel_data.title}")

    def load_funnel(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")]
        )
        if file_path:
            try:
                self.funnel_data = FunnelData.load(file_path)
                self.status_label.config(text=f"Loaded: {self.funnel_data.title}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load funnel: {str(e)}")

    def save_funnel(self):
        if not self.funnel_data:
            messagebox.showwarning("Warning", "No funnel data to save!")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")]
        )
        if file_path:
            try:
                self.funnel_data.save(file_path)
                messagebox.showinfo("Success", "Funnel saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save funnel: {str(e)}")

    def launch_classic_funnel(self):
        if not self.funnel_data:
            messagebox.showwarning("Warning", "Please create or load a funnel first!")
            return
        
        window = tk.Toplevel(self.root)
        from funnel import MarketingFunnelApp
        app = MarketingFunnelApp(window)

    def launch_horizontal_funnel(self):
        if not self.funnel_data:
            messagebox.showwarning("Warning", "Please create or load a funnel first!")
            return
        
        window = tk.Toplevel(self.root)
        HorizontalFunnelView(window, self.funnel_data)

    def launch_animated_funnel(self):
        if not self.funnel_data:
            messagebox.showwarning("Warning", "Please create or load a funnel first!")
            return
        
        window = tk.Toplevel(self.root)
        AnimatedFunnelView(window, self.funnel_data)

    def launch_web_funnel(self):
        if not self.funnel_data:
            messagebox.showwarning("Warning", "Please create or load a funnel first!")
            return
        
        try:
            import webbrowser
            # Save temporary funnel data
            temp_file = self.funnel_data.save("temp_funnel.yaml")
            # Launch Flask app (you'll need to implement this part)
            webbrowser.open('http://localhost:5000')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch web view: {str(e)}")

    def load_most_recent_funnel(self):
        """Load the most recent funnel from the funnels directory"""
        try:
            # Get funnels directory path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            funnels_dir = os.path.join(current_dir, "funnels")
            
            # Create directory if it doesn't exist
            os.makedirs(funnels_dir, exist_ok=True)
            
            # Get list of YAML files in the funnels directory
            funnel_files = [f for f in os.listdir(funnels_dir) if f.endswith('.yaml')]
            
            if funnel_files:
                # Sort by modification time, most recent first
                latest_funnel = max(
                    funnel_files,
                    key=lambda f: os.path.getmtime(os.path.join(funnels_dir, f))
                )
                return FunnelData.load(os.path.join(funnels_dir, latest_funnel))
            
            # If no files found, create new funnel
            funnel = FunnelData()
            # Save it to the funnels directory
            funnel.save(os.path.join(funnels_dir, "default_funnel.yaml"))
            return funnel
            
        except Exception as e:
            print(f"Error loading recent funnel: {str(e)}")
            # Return a new funnel if loading fails
            return FunnelData()

def main():
    root = tk.Tk()
    app = FunnelLauncher(root)
    root.mainloop()

if __name__ == "__main__":
    main() 