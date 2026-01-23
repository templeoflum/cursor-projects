import tkinter as tk
from tkinter import font as tkfont
from funnel_data import FunnelData
import math

class AnimatedFunnelView:
    def __init__(self, root, funnel_data):
        self.root = root
        self.root.title(f"Animated View - {funnel_data.title}")
        self.funnel_data = funnel_data
        
        # Make window open maximized
        self.root.state('zoomed')
        self.root.minsize(1200, 800)

        # Animation properties
        self.animation_speed = 10
        self.current_stage = -1
        self.fade_progress = 0.0
        self.text_fade_progress = 0.0
        self.animation_running = True
        self.pyramid_complete = False
        self.text_stage = -1  # New: track which text stage is fading in
        self.stage_delay = 1000

        self.setup_ui()
        self.start_animation()

    def setup_ui(self):
        # Create canvas
        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Add animation control buttons
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill=tk.X, pady=5)

        tk.Button(control_frame, text="Restart Animation", 
                 command=self.restart_animation).pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_frame, text="Pause/Resume", 
                 command=self.toggle_animation).pack(side=tk.LEFT, padx=5)

        # Bind resize event
        self.canvas.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        self.draw_funnel()

    def get_stage_coords(self, stage_index):
        """Calculate coordinates for a specific stage"""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        num_stages = len(self.funnel_data.stages)
        
        funnel_height = height * 0.7
        funnel_width = width * 0.6
        start_x = (width - funnel_width) / 2
        start_y = height * 0.15

        top_width = funnel_width * (1 - stage_index / num_stages)
        bottom_width = funnel_width * (1 - (stage_index + 1) / num_stages)
        top_x = (width - top_width) / 2
        bottom_x = (width - bottom_width) / 2
        y1 = start_y + stage_index * (funnel_height / num_stages)
        y2 = y1 + (funnel_height / num_stages)

        return (top_x, y1, top_x + top_width, y1,
                bottom_x + bottom_width, y2, bottom_x, y2)

    def draw_funnel(self):
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width < 100 or height < 100:
            return

        # Draw title
        title_font = tkfont.Font(family="Arial", size=24, weight="bold")
        title_opacity = min(1.0, self.fade_progress) if self.current_stage == -1 else 1.0
        self.canvas.create_text(
            width / 2, height * 0.05,
            text=self.funnel_data.title,
            font=title_font,
            fill=self.get_fade_color("black", title_opacity)
        )

        # Draw all stages of the pyramid
        for i, stage in enumerate(self.funnel_data.stages):
            if i > self.current_stage:
                continue

            opacity = 1.0
            if i == self.current_stage:
                opacity = self.fade_progress

            coords = self.get_stage_coords(i)
            
            # Draw trapezoid with fade
            color = stage["color"]
            fade_color = self.get_fade_color(color, opacity)
            self.canvas.create_polygon(
                coords,
                fill=fade_color,
                outline=self.get_fade_color("black", opacity)
            )

            # Draw stage name and items (inside pyramid)
            if opacity > 0.3:
                name_font = tkfont.Font(family="Arial", size=12, weight="bold")
                items_font = tkfont.Font(family="Arial", size=10)
                text_color = self.get_fade_color("black", opacity)
                
                center_x = width / 2
                center_y = (coords[1] + coords[5]) / 2

                # Draw stage name
                self.canvas.create_text(
                    center_x, center_y - 20,
                    text=stage["name"],
                    font=name_font,
                    fill=text_color
                )

                # Draw items
                self.canvas.create_text(
                    center_x, center_y + 10,
                    text="\n".join(stage["items"]),
                    font=items_font,
                    justify=tk.CENTER,
                    fill=text_color
                )

        # Draw external text elements after pyramid is complete
        if self.pyramid_complete:
            for i, stage in enumerate(self.funnel_data.stages):
                if i > self.text_stage:
                    continue

                coords = self.get_stage_coords(i)
                center_y = (coords[1] + coords[5]) / 2
                
                # Calculate opacity for this stage's text
                text_opacity = 1.0
                if i == self.text_stage:
                    text_opacity = self.text_fade_progress
                
                text_color = self.get_fade_color("black", text_opacity)

                # Draw stage number on the left
                stage_number = f"Stage {i + 1}"
                number_font = tkfont.Font(family="Arial", size=12)
                self.canvas.create_text(
                    coords[0] - 20,
                    center_y,
                    text=stage_number,
                    font=number_font,
                    fill=text_color,
                    anchor='e'
                )

                # Draw description on the right
                if stage["name"] in self.funnel_data.descriptions:
                    desc_font = tkfont.Font(family="Arial", size=10)
                    self.canvas.create_text(
                        coords[2] + 30,
                        center_y,
                        text=self.funnel_data.descriptions[stage["name"]]["short"],
                        font=desc_font,
                        fill=text_color,
                        anchor='w',
                        width=200
                    )

    def get_fade_color(self, color, opacity):
        """Convert color to hex with opacity"""
        if color.startswith('#'):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
        else:
            return color  # Return original color for named colors when opacity = 1

        bg_r, bg_g, bg_b = 255, 255, 255  # White background
        r = int(bg_r + (r - bg_r) * opacity)
        g = int(bg_g + (g - bg_g) * opacity)
        b = int(bg_b + (b - bg_b) * opacity)
        
        return f'#{r:02x}{g:02x}{b:02x}'

    def animate(self):
        """Main animation loop"""
        if not self.animation_running:
            return

        if not self.pyramid_complete:
            # Build the pyramid first
            self.fade_progress += 0.15
            if self.fade_progress >= 1.0:
                self.fade_progress = 0.0
                self.current_stage += 1
                if self.current_stage >= len(self.funnel_data.stages):
                    self.pyramid_complete = True
                    self.text_stage = -1
                    self.text_fade_progress = 0.0
        else:
            # Fade in text elements one stage at a time
            self.text_fade_progress += 0.1
            if self.text_fade_progress >= 1.0:
                self.text_fade_progress = 0.0
                self.text_stage += 1
                if self.text_stage >= len(self.funnel_data.stages):
                    self.animation_running = False

        self.draw_funnel()
        self.root.after(self.animation_speed, self.animate)

    def start_animation(self):
        """Start the animation"""
        self.current_stage = -1
        self.text_stage = -1
        self.fade_progress = 0.0
        self.text_fade_progress = 0.0
        self.pyramid_complete = False
        self.animation_running = True
        self.animate()

    def restart_animation(self):
        """Restart the animation from the beginning"""
        self.start_animation()

    def toggle_animation(self):
        """Pause or resume the animation"""
        self.animation_running = not self.animation_running
        if self.animation_running:
            self.animate() 