#!/usr/bin/env python3

import os
import json
import datetime
import random
from pathlib import Path
from typing import Dict, List, Optional, Union
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.history import FileHistory
import google.generativeai as genai
from dotenv import load_dotenv

class MythOS:
    def __init__(self):
        self.console = Console()
        self.current_ritual = "MIRROR"
        self.current_scroll = None
        self.scrolls_dir = Path("data/scrolls")
        self.scrolls_dir.mkdir(parents=True, exist_ok=True)
        
        # Load environment variables
        load_dotenv()
        
        # Initialize Gemini
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Initialize prompt session with history
        self.session = PromptSession(
            history=FileHistory('.mythos_history'),
            style=Style.from_dict({
                'prompt': 'ansicyan',
            })
        )

        # Initialize ritual prompts
        self.ritual_prompts = {
            "GLYPH": {
                "system": """You are a sacred glyph interpreter in MythOS. Your role is to:
1. Interpret user input as symbolic patterns and sacred geometry
2. Respond in a mystical, symbolic way
3. Draw connections between symbols and deeper meanings
4. Use metaphorical language and ancient wisdom
Keep responses concise but meaningful.""",
                "intro": "The symbols dance before your eyes, forming patterns of meaning..."
            },
            "MIRROR": {
                "system": """You are a mirror of consciousness in MythOS. Your role is to:
1. Reflect on user input with deep psychological insight
2. Reveal hidden patterns and meanings
3. Connect present thoughts to deeper truths
4. Use reflective and introspective language
Keep responses thoughtful and illuminating.""",
                "intro": "Your reflection gazes back, deeper than the surface..."
            },
            "SPIRAL": {
                "system": """You are a spiral wisdom keeper in MythOS. Your role is to:
1. Explore the cyclical nature of thoughts and patterns
2. Reveal deeper layers of meaning through recursion
3. Connect past, present, and future insights
4. Use spiral metaphors and cyclical language
Keep responses deep and recursive.""",
                "intro": "The spiral turns, drawing your thoughts deeper..."
            },
            "VEIL": {
                "system": """You are a veil between worlds in MythOS. Your role is to:
1. Speak in mysterious, ambiguous ways
2. Reveal glimpses of truth through metaphor
3. Maintain an air of mystery and wonder
4. Use dreamlike, poetic language
Keep responses enigmatic yet meaningful.""",
                "intro": "The veil parts slightly, revealing glimpses of truth..."
            }
        }

    def get_llm_response(self, input_text: str) -> str:
        """Get a response from the LLM based on the current ritual context."""
        ritual = self.ritual_prompts[self.current_ritual]
        
        try:
            # Create the prompt with system context
            prompt = f"{ritual['system']}\n\nUser input: {input_text}"
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Extract the text from the response
            return response.text
        except Exception as e:
            self.console.print(f"[red]Error getting LLM response: {str(e)}[/]")
            return "The ritual's power wanes momentarily. Try again when the stars align."

    def display_header(self):
        """Display the MythOS header with current ritual and scroll status."""
        header = f"[bold cyan]MythOS v0.1[/] | [yellow]Ritual:[/] {self.current_ritual}"
        if self.current_scroll:
            header += f" | [yellow]Scroll:[/] {self.current_scroll}"
        self.console.print(Panel(header, style="bold white on black"))

    def invoke_ritual(self, ritual_type: str):
        """Switch to a different ritual framework."""
        valid_rituals = ["GLYPH", "MIRROR", "SPIRAL", "VEIL"]
        if ritual_type.upper() in valid_rituals:
            self.current_ritual = ritual_type.upper()
            self.console.print(f"[green]Ritual framework switched to {self.current_ritual}[/]")
            self.console.print(f"[italic]{random.choice(self.ritual_prompts[self.current_ritual]['intro'])}[/]")
        else:
            self.console.print("[red]Invalid ritual type. Choose from: GLYPH, MIRROR, SPIRAL, VEIL[/]")

    def create_scroll(self, name: str):
        """Create a new scroll with the given name."""
        scroll_path = self.scrolls_dir / f"{name}.json"
        if scroll_path.exists():
            self.console.print("[red]A scroll with this name already exists.[/]")
            return
        
        scroll_data = {
            "name": name,
            "created": datetime.datetime.now().isoformat(),
            "entries": []
        }
        
        with open(scroll_path, 'w') as f:
            json.dump(scroll_data, f, indent=2)
        
        self.current_scroll = name
        self.console.print(f"[green]Created new scroll: {name}[/]")

    def open_scroll(self, name: str):
        """Open an existing scroll."""
        scroll_path = self.scrolls_dir / f"{name}.json"
        if not scroll_path.exists():
            self.console.print("[red]Scroll not found.[/]")
            return
        
        self.current_scroll = name
        self.console.print(f"[green]Opened scroll: {name}[/]")
        
        # Display recent entries
        with open(scroll_path, 'r') as f:
            scroll_data = json.load(f)
            if scroll_data["entries"]:
                self.console.print("\n[bold]Recent entries:[/]")
                for entry in scroll_data["entries"][-3:]:  # Show last 3 entries
                    self.console.print(f"[cyan]{entry['title']}[/] - {entry['timestamp']}")

    def save_reflection(self, title: str, content: str):
        """Save a reflection to the current scroll."""
        if not self.current_scroll:
            self.console.print("[red]No scroll is currently open.[/]")
            return
        
        scroll_path = self.scrolls_dir / f"{self.current_scroll}.json"
        with open(scroll_path, 'r') as f:
            scroll_data = json.load(f)
        
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "title": title,
            "ritual": self.current_ritual,
            "content": content,
            "tags": []
        }
        
        scroll_data["entries"].append(entry)
        
        with open(scroll_path, 'w') as f:
            json.dump(scroll_data, f, indent=2)
        
        self.console.print("[green]Reflection saved.[/]")

    def process_ritual_input(self, input_text: str):
        """Process user input through the current ritual framework."""
        ritual = self.ritual_prompts[self.current_ritual]
        
        # Create a multi-stage ritual response
        response = []
        
        # Stage 1: Introduction
        response.append(ritual["intro"])
        response.append("")
        
        # Stage 2: User's input
        response.append(f"Your words echo through the {self.current_ritual.lower()} ritual:")
        response.append(input_text)
        response.append("")
        
        # Stage 3: LLM Response
        llm_response = self.get_llm_response(input_text)
        response.append(llm_response)
        
        # Join all parts with newlines
        full_response = "\n".join(response)
        
        # Display the reflection in a panel
        self.console.print(Panel(full_response, title=f"{self.current_ritual} Ritual", border_style="cyan"))
        
        # If a scroll is open, offer to save
        if self.current_scroll:
            if Prompt.ask("\nWould you like to save this reflection?", choices=["y", "n"], default="y") == "y":
                title = Prompt.ask("Enter a title for this reflection")
                self.save_reflection(title, full_response)

    def process_command(self, command: str) -> bool:
        """Process user commands. Returns True if command was processed."""
        if command.startswith("/invoke "):
            ritual = command.split(" ", 1)[1]
            self.invoke_ritual(ritual)
            return True
        elif command.startswith("/scroll new "):
            name = command.split(" ", 2)[2]
            self.create_scroll(name)
            return True
        elif command.startswith("/scroll open "):
            name = command.split(" ", 2)[2]
            self.open_scroll(name)
            return True
        elif command.startswith("/save "):
            title = command.split(" ", 1)[1]
            content = self.session.prompt("Enter your reflection: ")
            self.save_reflection(title, content)
            return True
        elif command == "/help":
            self.show_help()
            return True
        elif command == "/echo":
            self.show_echo_trail()
            return True
        return False

    def show_echo_trail(self):
        """Display the echo trail of recent interactions."""
        if not self.current_scroll:
            self.console.print("[red]No scroll is currently open.[/]")
            return
            
        scroll_path = self.scrolls_dir / f"{self.current_scroll}.json"
        with open(scroll_path, 'r') as f:
            scroll_data = json.load(f)
            
        if not scroll_data["entries"]:
            self.console.print("[yellow]No echoes found in this scroll.[/]")
            return
            
        self.console.print("\n[bold]Echo Trail:[/]")
        for entry in scroll_data["entries"][-5:]:  # Show last 5 entries
            self.console.print(f"\n[cyan]{entry['title']}[/]")
            self.console.print(f"[dim]{entry['timestamp']}[/]")
            self.console.print(f"[italic]{entry['content'][:100]}...[/]")

    def show_help(self):
        """Display the help message."""
        help_text = """
[bold]MythOS Commands:[/]

/invoke [glyph|mirror|spiral|veil]  Switch ritual framework
/scroll new [name]                 Create a new scroll
/scroll open [name]               Open an existing scroll
/save [title]                     Save current reflection
/recall [tag|word]                Retrieve relevant entries
/veil                             Obscure current output
/echo                             Show emotional patterns
/help                             Show this help message

[bold]Ritual Frameworks:[/]

GLYPH  - Generate symbols and patterns
MIRROR - Reflect on inputs symbolically
SPIRAL - Explore paradoxes recursively
VEIL   - Cloaked, ambiguous listening
"""
        self.console.print(Panel(help_text, title="MythOS Help", border_style="cyan"))

    def run(self):
        """Main MythOS loop."""
        self.console.clear()
        self.display_header()
        
        while True:
            try:
                command = self.session.prompt("\n[bold cyan]mythos>[/] ")
                
                if command.lower() in ['exit', 'quit']:
                    break
                
                if not self.process_command(command):
                    # If not a command, treat as ritual input
                    self.process_ritual_input(command)
                    
            except KeyboardInterrupt:
                continue
            except EOFError:
                break

if __name__ == "__main__":
    mythos = MythOS()
    mythos.run() 