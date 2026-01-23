import tkinter as tk
from tkinter import colorchooser, ttk, filedialog
from tkinter import font as tkfont
from PIL import Image, ImageGrab, ImageDraw, ImageFont
import os
from datetime import datetime
from reportlab.pdfgen import canvas as rlcanvas
from reportlab.graphics import renderPM
from reportlab.lib import colors
from io import BytesIO
from reportlab.graphics.shapes import Drawing, Polygon, String
import yaml  # Add to imports at top

class MarketingFunnelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Marketing Funnel Builder")
        
        # Make window open maximized
        self.root.state('zoomed')  # For Windows
        # self.root.attributes('-zoomed', True)  # For Linux
        # self.root.state('zoomed')  # For macOS
        
        self.root.minsize(1200, 800)  # Keep minimum size requirements

        # Add title property with default
        self.funnel_title = "Marketing Funnel"

        # Default funnel data with items ordered by length (longest to shortest)
        self.stages = [
            {"name": "Awareness", "items": ["Social Media", "Google Ads", "Meta Ads"], "color": "#FF9999"},
            {"name": "Engagement", "items": ["Lead Magnets", "Blog Content", "Emails"], "color": "#FFCC99"},
            {"name": "Consideration", "items": ["Retargeting Ads", "Testimonials", "Webinar"], "color": "#FFFF99"},
            {"name": "Conversion", "items": ["Consultation", "Sign-Ups", "Offers"], "color": "#CCFF99"},
            {"name": "Retention", "items": ["Community", "Check-ins", "Referrals"], "color": "#99FF99"}
        ]

        # Update stage descriptions to include both long (control panel) and short (funnel display) versions
        self.stage_descriptions = {
            "Awareness": {
                "long": "Top of funnel - where potential customers first discover your brand through various marketing channels.",
                "short": "Potential customers discover\nyour brand and offerings"
            },
            "Engagement": {
                "long": "Users begin interacting with your content and showing interest in your offerings.",
                "short": "Users interact with content\nand show initial interest"
            },
            "Consideration": {
                "long": "Prospects actively evaluate your solution against alternatives.",
                "short": "Prospects evaluate options\nand consider solutions"
            },
            "Conversion": {
                "long": "Users take desired actions, becoming customers through purchases or sign-ups.",
                "short": "Leads convert into\npaying customers"
            },
            "Retention": {
                "long": "Maintaining customer relationships and encouraging repeat business and referrals.",
                "short": "Keep customers engaged\nand encourage referrals"
            }
        }

        self.setup_ui()

    def setup_ui(self):
        # Create main frames
        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.control_frame = tk.Frame(self.root, width=300)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Add controls header
        tk.Label(self.control_frame, text="Funnel Controls", font=("Arial", 16)).pack(pady=10)

        # Add title input at the top
        title_frame = tk.Frame(self.control_frame)
        title_frame.pack(pady=(0, 10), padx=10, fill=tk.X)
        
        tk.Label(title_frame, text="Title:", font=("Arial", 10)).pack(side=tk.LEFT)
        self.title_entry = tk.Entry(title_frame)
        self.title_entry.insert(0, self.funnel_title)
        self.title_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5,0))
        self.title_entry.bind("<FocusOut>", self.update_title)
        self.title_entry.bind("<KeyRelease>", self.update_title)  # Add real-time update

        # Add separator after title
        ttk.Separator(self.control_frame, orient='horizontal').pack(fill=tk.X, pady=10, padx=10)

        # Add export button
        export_frame = tk.Frame(self.control_frame)
        export_frame.pack(pady=(0, 10), padx=10, fill=tk.X)
        
        button_frame = tk.Frame(export_frame)
        button_frame.pack(fill=tk.X)
        
        export_btn = tk.Button(button_frame, 
                             text="Export as Image",
                             command=self.export_image,
                             font=("Arial", 10))
        export_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        save_btn = tk.Button(button_frame,
                           text="Save Funnel",
                           command=self.save_funnel,
                           font=("Arial", 10))
        save_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))

        load_btn = tk.Button(button_frame,
                           text="Load Funnel",
                           command=self.load_funnel,
                           font=("Arial", 10))
        load_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        # Create controls for each stage
        self.name_entries = []
        self.items_texts = []
        
        for idx, stage in enumerate(self.stages):
            # Create frame for each stage's controls
            stage_frame = tk.Frame(self.control_frame)
            stage_frame.pack(pady=10, padx=10, fill=tk.X)
            
            # Stage header with color button and description
            header_frame = tk.Frame(stage_frame)
            header_frame.pack(fill=tk.X)
            
            # Left side: Stage number and color
            left_frame = tk.Frame(header_frame)
            left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            stage_label = tk.Label(left_frame, 
                                 text=f"Stage {idx + 1}",
                                 font=("Arial", 12, "bold"))
            stage_label.pack(side=tk.LEFT)
            
            color_btn = tk.Button(left_frame, 
                                text="Change Color",
                                command=lambda idx=idx: self.change_color(idx))
            color_btn.pack(side=tk.RIGHT)

            # Add description below header
            desc_frame = tk.Frame(stage_frame)
            desc_frame.pack(fill=tk.X, pady=(5, 10))
            
            desc_text = tk.Text(desc_frame, 
                              height=2, 
                              wrap=tk.WORD, 
                              font=("Arial", 9),
                              bg='#f0f0f0',  # Light gray background
                              relief=tk.FLAT)
            desc_text.insert('1.0', self.stage_descriptions[stage['name']]['long'])
            desc_text.config(state=tk.DISABLED)  # Make read-only
            desc_text.pack(fill=tk.X, padx=5)

            # Rest of the stage controls (name and items)
            name_frame = tk.Frame(stage_frame)
            name_frame.pack(fill=tk.X, pady=(5,0))
            
            tk.Label(name_frame, text="Name:", font=("Arial", 10)).pack(side=tk.LEFT)
            name_entry = tk.Entry(name_frame)
            name_entry.insert(0, stage['name'])
            name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5,0))
            name_entry.bind("<FocusOut>", lambda e, idx=idx, entry=name_entry: self.update_stage_name(idx, entry.get()))
            name_entry.bind("<KeyRelease>", lambda e, idx=idx, entry=name_entry: self.update_stage_name(idx, entry.get()))
            self.name_entries.append(name_entry)

            # Stage items entry - using Text widget instead of Entry
            items_frame = tk.Frame(stage_frame)
            items_frame.pack(fill=tk.X, pady=(5,0))
            
            tk.Label(items_frame, text="Items:", font=("Arial", 10)).pack(side=tk.LEFT, anchor='n')
            items_text = tk.Text(items_frame, height=2, width=38)  # Increased width from 30 to 38 (25% more)
            items_str = ", ".join(stage['items'])
            items_text.insert('1.0', items_str)
            items_text.pack(side=tk.LEFT, padx=(5,0))
            items_text.bind("<FocusOut>", lambda e, idx=idx, text=items_text: self.update_stage_items(idx, text.get('1.0', 'end-1c')))
            items_text.bind("<KeyRelease>", lambda e, idx=idx, text=items_text: self.update_stage_items(idx, text.get('1.0', 'end-1c')))
            self.items_texts.append(items_text)

            # Add separator with more padding
            if idx < len(self.stages) - 1:
                ttk.Separator(self.control_frame, orient='horizontal').pack(fill=tk.X, pady=10, padx=10)

        # Bind the resize event to redraw the funnel dynamically
        self.canvas.bind("<Configure>", lambda event: self.draw_funnel())

        # Ensure the window is rendered before drawing
        self.root.update_idletasks()
        self.draw_funnel()

    def draw_funnel(self):
        self.canvas.delete("all")  # Clear previous drawings
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width < 100 or height < 100:
            return

        # Draw title at the top
        title_font = tkfont.Font(family="Arial", size=24, weight="bold")
        self.canvas.create_text(
            width / 2,
            height * 0.05,  # Position at 5% from top
            text=self.funnel_title,
            font=title_font
        )

        # Adjust funnel position and size
        num_stages = len(self.stages)
        funnel_height = height * 0.7  # Keep this the same
        funnel_width = width * 0.6    # Increased from 0.5 to 0.6 for wider funnel

        # Set a minimum funnel width
        min_funnel_width = 600        # Increased from 500 to 600
        if funnel_width < min_funnel_width:
            funnel_width = min_funnel_width

        start_x = (width - funnel_width) / 2
        start_y = (height - funnel_height) / 2
        stage_height = funnel_height / num_stages

        # Calculate the width of the bottom stage to use as reference
        bottom_stage_width = funnel_width * (1 - (num_stages - 1) / num_stages)

        for i, stage in enumerate(self.stages):
            # Calculate coordinates for each trapezoid
            top_width = funnel_width * (1 - i / num_stages)
            bottom_width = funnel_width * (1 - (i + 1) / num_stages)
            top_x = (width - top_width) / 2
            bottom_x = (width - bottom_width) / 2
            y1 = start_y + i * stage_height
            y2 = y1 + stage_height

            # Draw the trapezoid
            self.canvas.create_polygon(
                top_x, y1,
                top_x + top_width, y1,
                bottom_x + bottom_width, y2,
                bottom_x, y2,
                fill=stage["color"],
                outline="black"
            )

            # Calculate the average width of this stage
            current_stage_width = (top_width + bottom_width) / 2
            
            # Calculate the scale factor based on the ratio of current width to bottom stage width
            scale_factor = current_stage_width / bottom_stage_width

            # Adjust base font sizes and scaling for better proportions
            base_name_font_size = 20
            base_items_font_size = 16

            # Adjust font sizes for specific stages
            if i == len(self.stages) - 1:  # Retention stage
                scale_factor = scale_factor * 0.7
                base_items_font_size = 8
                items_font_size = min(max(int(base_items_font_size * scale_factor), 8), 16)
            elif i == len(self.stages) - 2:  # Conversion stage
                base_items_font_size = 20  # Increase base size for conversion items
                items_font_size = min(max(int(base_items_font_size * scale_factor), 14), 36)
            else:
                items_font_size = min(max(int(base_items_font_size * scale_factor), 12), 32)

            # Calculate available height for text with minimal top padding
            available_height = stage_height - (stage_height * 0.02)

            # Try font sizes until text fits
            name_font_size = min(max(int(base_name_font_size * scale_factor), 14), 36)

            while True:
                # Create test fonts
                test_name_font = tkfont.Font(family="Arial", size=name_font_size, weight="bold")
                test_items_font = tkfont.Font(family="Arial", size=items_font_size)

                # Calculate heights
                name_height = test_name_font.metrics("linespace")
                items_height = test_items_font.metrics("linespace") * len(stage["items"])
                
                total_height = name_height + items_height + stage_height * 0.02  # Reduced padding between elements

                # Test width constraints
                name_text = stage["name"]
                items_text = "\n".join(stage["items"])
                
                # Calculate the minimum width needed for the text
                name_width = test_name_font.measure(name_text)
                max_item_width = max(test_items_font.measure(item) for item in stage["items"])
                
                # Use bottom_width as the constraint since it's narrower
                max_allowed_width = bottom_width * 0.9  # 90% of the bottom width
                
                # Check if text fits both vertically and horizontally
                if (total_height <= available_height and 
                    name_width <= max_allowed_width and 
                    max_item_width <= max_allowed_width):
                    break

                # Reduce font sizes if text doesn't fit
                if name_font_size > 14 and items_font_size > 12:  # Updated minimum thresholds
                    name_font_size -= 1
                    items_font_size -= 1
                else:
                    break

            # Use the final calculated font sizes
            name_font = tkfont.Font(family="Arial", size=name_font_size, weight="bold")
            items_font = tkfont.Font(family="Arial", size=items_font_size)

            # Rest of the drawing logic
            name_text = stage["name"]
            items_text = "\n".join(stage["items"])

            # Calculate heights
            name_height = name_font.metrics("linespace")
            items_height = items_font.metrics("linespace") * len(stage["items"])

            # Position text at the top of the stage with minimal padding
            top_padding = stage_height * 0.02
            
            # Add extra padding between name and items for conversion stage
            name_items_padding = stage_height * 0.02
            if i == len(self.stages) - 2:  # Conversion stage
                name_items_padding = stage_height * 0.08  # Increase padding for conversion stage
            
            name_y = y1 + top_padding + name_height / 2
            items_y = name_y + name_height / 2 + name_items_padding + items_height / 2

            self.canvas.create_text(
                width / 2, name_y,
                text=name_text,
                font=name_font
            )

            # Use bottom width for text wrapping to ensure text stays within bounds
            text_wrap_width = bottom_width * 0.9

            self.canvas.create_text(
                width / 2, items_y,
                text=items_text,
                font=items_font,
                justify=tk.CENTER,
                width=text_wrap_width
            )

            # Add stage number indicator on the left side
            stage_number = f"Stage {i + 1}"
            number_font = tkfont.Font(family="Arial", size=12)
            self.canvas.create_text(
                top_x - 20,  # Position to the left of the funnel
                y1 + stage_height/2,
                text=stage_number,
                font=number_font,
                anchor='e'  # Right-align
            )

            # Add stage description on the right side
            description_font = tkfont.Font(family="Arial", size=10)
            self.canvas.create_text(
                top_x + top_width + 30,  # Position further to the right of the funnel
                y1 + stage_height/2,
                text=self.stage_descriptions[stage['name']]['short'],
                font=description_font,
                anchor='w',  # Left-align
                justify=tk.LEFT
            )

    def change_color(self, stage_index):
        # Open color chooser dialog
        color_code = colorchooser.askcolor(title=f"Choose color for {self.stages[stage_index]['name']}")
        if color_code and color_code[1]:
            self.stages[stage_index]['color'] = color_code[1]
            self.draw_funnel()

    def update_stage_name(self, stage_index, new_name):
        if new_name.strip():
            self.stages[stage_index]['name'] = new_name.strip()
            self.draw_funnel()

    def update_stage_items(self, stage_index, new_items):
        # Split the input by commas and strip whitespace
        items = [item.strip() for item in new_items.split(",") if item.strip()]
        if items:
            self.stages[stage_index]['items'] = items
            self.draw_funnel()

    def update_title(self, event=None):  # Make event optional
        new_title = self.title_entry.get().strip()
        if new_title:
            self.funnel_title = new_title
            self.draw_funnel()

    def export_image(self):
        # Get current directory and timestamp
        current_dir = os.path.dirname(os.path.abspath(__file__))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(current_dir, f"funnel_{timestamp}.png")

        # Get canvas dimensions
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        # Create a new image with white background
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)

        # Draw title
        title_size = 36
        try:
            title_font = ImageFont.truetype("arial.ttf", title_size)
        except:
            title_font = ImageFont.load_default()

        title_width = draw.textlength(self.funnel_title, font=title_font)
        title_x = width/2 - title_width/2
        title_y = height * 0.05
        draw.text((title_x, title_y), self.funnel_title, fill='black', font=title_font)

        # Calculate funnel dimensions
        num_stages = len(self.stages)
        funnel_height = height * 0.7  # Match the display version
        funnel_width = width * 0.6    # Match the display version (increased from 0.5)
        min_funnel_width = 600        # Match the display version (increased from 500)
        
        start_y = (height - funnel_height) / 2
        stage_height = funnel_height / num_stages
        bottom_stage_width = funnel_width * (1 - (num_stages - 1) / num_stages)

        for i, stage in enumerate(self.stages):
            # Calculate trapezoid coordinates
            top_width = funnel_width * (1 - i / num_stages)
            bottom_width = funnel_width * (1 - (i + 1) / num_stages)
            top_x = (width - top_width) / 2
            bottom_x = (width - bottom_width) / 2
            y1 = start_y + i * stage_height
            y2 = y1 + stage_height

            # Draw trapezoid
            color = stage["color"]
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            draw.polygon([
                (top_x, y1),
                (top_x + top_width, y1),
                (bottom_x + bottom_width, y2),
                (bottom_x, y2)
            ], fill=(r, g, b), outline='black')

            # Calculate font sizes
            current_stage_width = (top_width + bottom_width) / 2
            scale_factor = current_stage_width / bottom_stage_width

            if i == len(self.stages) - 1:  # Retention stage
                name_size = int(24 * scale_factor)
                item_size = int(20 * scale_factor)
            elif i == len(self.stages) - 2:  # Conversion stage
                name_size = int(18 * scale_factor)
                item_size = int(14 * scale_factor)
            else:
                name_size = int(22 * scale_factor)
                item_size = int(16 * scale_factor)

            # Limit maximum sizes
            name_size = min(name_size, 32)
            item_size = min(item_size, 24)

            try:
                name_font = ImageFont.truetype("arial.ttf", name_size)
                item_font = ImageFont.truetype("arial.ttf", item_size)
            except:
                name_font = ImageFont.load_default()
                item_font = ImageFont.load_default()

            # Draw stage name
            text = stage["name"]
            text_width = draw.textlength(text, font=name_font)
            text_x = width/2 - text_width/2
            text_y = y1 + stage_height * 0.02
            draw.text((text_x, text_y), text, fill='black', font=name_font)

            # Draw items with proper spacing
            padding = stage_height * (0.08 if i == len(self.stages) - 2 else 0.02)
            items_y = text_y + name_size + padding
            
            # Handle items text - special handling for conversion stage
            if i == len(self.stages) - 2:  # Conversion stage
                # Calculate total height needed for items
                total_items = len(stage["items"])
                available_height = y2 - (text_y + name_size + padding)
                spacing = available_height / (total_items + 1)  # +1 for extra spacing
                
                for item in stage["items"]:
                    item_width = draw.textlength(item, font=item_font)
                    item_x = width/2 - item_width/2
                    draw.text((item_x, items_y), item, fill='black', font=item_font)
                    items_y += spacing  # Evenly space items
            else:
                # Normal handling for other stages
                for item in stage["items"]:
                    item_width = draw.textlength(item, font=item_font)
                    item_x = width/2 - item_width/2
                    draw.text((item_x, items_y), item, fill='black', font=item_font)
                    items_y += item_size * 1.2

            # Draw stage number on the left side
            stage_number = f"Stage {i + 1}"
            try:
                number_font = ImageFont.truetype("arial.ttf", 12)
            except:
                number_font = ImageFont.load_default()
            
            number_width = draw.textlength(stage_number, font=number_font)
            number_x = top_x - 20 - number_width  # Position to the left of the funnel
            number_y = y1 + stage_height/2 - 6  # Adjust for vertical centering
            draw.text((number_x, number_y), stage_number, fill='black', font=number_font)

            # Draw stage description on the right side
            try:
                desc_font = ImageFont.truetype("arial.ttf", 10)
            except:
                desc_font = ImageFont.load_default()
            
            description = self.stage_descriptions[stage['name']]['short']
            desc_x = top_x + top_width + 30  # Position to the right of the funnel
            desc_y = y1 + stage_height/2 - 10  # Adjust for vertical centering
            
            # Draw each line of the description
            for line in description.split('\n'):
                draw.text((desc_x, desc_y), line, fill='black', font=desc_font)
                desc_y += 15  # Move down for next line

        # Save the image
        image.save(file_path, 'PNG')

    def save_funnel(self):
        """Save the funnel configuration to a YAML file in the funnels directory"""
        # Create the data structure to save
        funnel_data = {
            'title': self.funnel_title,
            'stages': self.stages
        }

        # Get current directory and ensure funnels directory exists
        current_dir = os.path.dirname(os.path.abspath(__file__))
        funnels_dir = os.path.join(current_dir, "funnels")
        os.makedirs(funnels_dir, exist_ok=True)

        # Create filename from title and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in self.funnel_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_title}_{timestamp}.yaml"
        file_path = os.path.join(funnels_dir, filename)

        try:
            with open(file_path, 'w') as f:
                yaml.safe_dump(funnel_data, f, default_flow_style=False)
            tk.messagebox.showinfo("Success", f"Funnel saved to:\n{file_path}")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to save funnel: {str(e)}")

    def load_funnel(self):
        """Load a funnel configuration from a YAML file"""
        # Get funnels directory path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        funnels_dir = os.path.join(current_dir, "funnels")
        
        # Create directory if it doesn't exist
        os.makedirs(funnels_dir, exist_ok=True)

        file_path = filedialog.askopenfilename(
            initialdir=funnels_dir,
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, 'r') as f:
                    funnel_data = yaml.safe_load(f)

                # Validate the loaded data
                if not isinstance(funnel_data, dict):
                    raise ValueError("Invalid file format")
                if 'title' not in funnel_data or 'stages' not in funnel_data:
                    raise ValueError("Missing required fields")
                if not isinstance(funnel_data['stages'], list):
                    raise ValueError("Invalid stages format")

                # Update the funnel data
                self.funnel_title = funnel_data['title']
                self.stages = funnel_data['stages']

                # Update UI elements
                self.title_entry.delete(0, tk.END)
                self.title_entry.insert(0, self.funnel_title)

                for i, stage in enumerate(self.stages):
                    if i < len(self.name_entries):
                        self.name_entries[i].delete(0, tk.END)
                        self.name_entries[i].insert(0, stage['name'])
                        
                        self.items_texts[i].delete('1.0', tk.END)
                        self.items_texts[i].insert('1.0', ', '.join(stage['items']))

                # Redraw the funnel
                self.draw_funnel()
                tk.messagebox.showinfo("Success", "Funnel configuration loaded successfully!")
            except Exception as e:
                tk.messagebox.showerror("Error", f"Failed to load funnel: {str(e)}")

def main():
    root = tk.Tk()
    app = MarketingFunnelApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
