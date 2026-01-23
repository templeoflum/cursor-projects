import tkinter as tk
from tkinter import font as tkfont
from funnel_data import FunnelData

class HorizontalFunnelView:
    def __init__(self, root, funnel_data):
        self.root = root
        self.root.title(f"Horizontal View - {funnel_data.title}")
        self.funnel_data = funnel_data
        
        # Make window open maximized
        self.root.state('zoomed')
        self.root.minsize(1200, 800)

        self.setup_ui()

    def setup_ui(self):
        # Create canvas
        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bind resize event
        self.canvas.bind("<Configure>", lambda e: self.draw_funnel())

    def draw_funnel(self):
        self.canvas.delete("all")  # Clear canvas
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width < 100 or height < 100:
            return

        # Draw title
        title_font = tkfont.Font(family="Arial", size=24, weight="bold")
        self.canvas.create_text(
            width / 2,
            height * 0.1,
            text=self.funnel_data.title,
            font=title_font
        )

        # Calculate funnel dimensions
        num_stages = len(self.funnel_data.stages)
        funnel_width = width * 0.8
        funnel_height = height * 0.6
        start_x = width * 0.1
        start_y = height * 0.2

        # Calculate stage dimensions
        stage_width = funnel_width / num_stages
        stage_spacing = stage_width * 0.1

        for i, stage in enumerate(self.funnel_data.stages):
            # Calculate trapezoid coordinates for horizontal funnel
            x1 = start_x + (i * stage_width)
            x2 = x1 + stage_width - stage_spacing
            
            # Make each stage slightly smaller than the previous
            height_reduction = (i / num_stages) * (funnel_height * 0.4)
            y1 = start_y + height_reduction
            y2 = start_y + funnel_height - height_reduction

            # Draw trapezoid
            self.canvas.create_polygon(
                x1, y1,
                x2, y1,
                x2, y2,
                x1, y2,
                fill=stage["color"],
                outline="black"
            )

            # Draw stage name
            name_font = tkfont.Font(family="Arial", size=12, weight="bold")
            self.canvas.create_text(
                (x1 + x2) / 2,
                y1 - 20,
                text=stage["name"],
                font=name_font,
                anchor="s"
            )

            # Draw items
            items_font = tkfont.Font(family="Arial", size=10)
            items_text = "\n".join(stage["items"])
            self.canvas.create_text(
                (x1 + x2) / 2,
                (y1 + y2) / 2,
                text=items_text,
                font=items_font,
                justify=tk.CENTER
            )

            # Draw stage description
            if stage["name"] in self.funnel_data.descriptions:
                desc_font = tkfont.Font(family="Arial", size=9)
                self.canvas.create_text(
                    (x1 + x2) / 2,
                    y2 + 20,
                    text=self.funnel_data.descriptions[stage["name"]]["short"],
                    font=desc_font,
                    anchor="n",
                    width=stage_width - stage_spacing
                )

        # Draw arrows between stages
        arrow_y = start_y + funnel_height / 2
        for i in range(num_stages - 1):
            x1 = start_x + ((i + 1) * stage_width) - (stage_spacing / 2)
            self.canvas.create_line(
                x1, arrow_y,
                x1 + stage_spacing, arrow_y,
                arrow="last",
                width=2
            ) 