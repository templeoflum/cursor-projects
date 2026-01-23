#!/usr/bin/env python3
"""
MythOS v0.1 - Main Application
A symbolic operating system for reflective, recursive interaction with language models.
"""

import os
import sys
from pathlib import Path

from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme
from rich.box import Box, HEAVY

from scroll_system import ScrollSystem
from echo_trail import EchoTrail

# Define custom theme for MythOS
mythos_theme = Theme({
    "header": "bold white",
    "prompt": "bold white",
    "response": "white",
    "command": "bold cyan",
    "ritual.glyph": "bold magenta",
    "ritual.mirror": "bold cyan",
    "ritual.spiral": "bold green",
    "ritual.veil": "bold dim white",
    "error": "bold red",
    "success": "bold green",
    "info": "bold yellow",
})

# Define custom box styles for panels
SCROLL_BOX = Box(
    """\
╭─┬╮
│ ││
├─┼┤
│ ││
╰─┴╯
""",
    ascii=False,
)

# Define ritual frameworks
RITUALS = {
    "GLYPH": {
        "description": "Generate symbols or scroll phrases from seeds",
        "prompt_symbol": "◈",
        "style": "ritual.glyph",
        "intro": "The GLYPH ritual transforms seeds into symbols, crystallizing meaning into form."
    },
    "MIRROR": {
        "description": "Reflect on inputs symbolically or emotionally",
        "prompt_symbol": "◎",
        "style": "ritual.mirror",
        "intro": "The MIRROR ritual reflects your words back through the lens of symbol and emotion."
    },
    "SPIRAL": {
        "description": "Explore paradoxes or mythic systems recursively",
        "prompt_symbol": "⌀",
        "style": "ritual.spiral",
        "intro": "The SPIRAL ritual follows thoughts to their recursive depths, where paradox blooms."
    },
    "VEIL": {
        "description": "Cloaked, ambiguous, dreamlike listening mode",
        "prompt_symbol": "◌",
        "style": "ritual.veil",
        "intro": "The VEIL ritual speaks in whispers and shadows, meanings half-glimpsed through mist."
    }
}


class MythOS:
    """MythOS - A symbolic operating system for reflective interaction."""
    
    def __init__(self):
        """Initialize the MythOS environment."""
        self.console = Console(theme=mythos_theme)
        self.active_ritual = "MIRROR"  # Default ritual
        
        # Set up data directory
        self.data_dir = Path("./data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize scroll system and echo trail
        self.scroll_system = ScrollSystem(self.data_dir)
        self.echo_trail = EchoTrail(self.data_dir)
        
        # Track if output is veiled
        self.output_veiled = False
    
    def startup(self):
        """Display startup sequence and welcome message."""
        self.console.clear()
        
        # Display animated startup sequence
        self.console.print("\n\n")
        self.console.print("[bold white]MythOS[/bold white] [dim]v0.1[/dim]", justify="center")
        self.console.print("\n")
        
        # Display ritual symbols with slight delay
        for ritual in RITUALS.values():
            self.console.print(f"[{ritual['style']}]{ritual['prompt_symbol']}[/{ritual['style']}]", end=" ", justify="center")
        
        self.console.print("\n\n")
        self.console.print("A symbolic operating system for reflective interaction", justify="center")
        self.console.print("\n")
        
        # Display active ritual
        ritual = RITUALS[self.active_ritual]
        self.console.print(Panel(
            f"[{ritual['style']}]{ritual['intro']}[/{ritual['style']}]",
            title=f"[{ritual['style']}]{self.active_ritual} RITUAL[/{ritual['style']}]",
            border_style=ritual['style'],
            box=SCROLL_BOX
        ))
        
        self.console.print("\n")
        self.console.print("Type [bold]/help[/bold] for available commands", justify="center")
        self.console.print("\n")
    
    def process_command(self, command: str) -> bool:
        """Process a command input from the user.
        
        Args:
            command: The command string from the user
            
        Returns:
            bool: True to continue, False to exit
        """
        if not command.startswith('/'):
            # Not a command, process as input to the active ritual
            self.process_ritual_input(command)
            return True
        
        # Split command and arguments
        parts = command.split(maxsplit=1)
        cmd = parts[0][1:]  # Remove the leading '/'
        args = parts[1] if len(parts) > 1 else ""
        
        # Process commands
        if cmd == "help":
            self.show_help()
        elif cmd == "invoke":
            self.invoke_ritual(args.upper())
        elif cmd == "scroll":
            if args.startswith("new "):
                success, message = self.scroll_system.create_scroll(args[4:])
                self.console.print(f"[{'success' if success else 'error'}]{message}[/{'success' if success else 'error'}]")
            elif args.startswith("open "):
                success, message, last_entry = self.scroll_system.open_scroll(args[5:])
                self.console.print(f"[{'success' if success else 'error'}]{message}[/{'success' if success else 'error'}]")
                
                # Display the last entry if there is one
                if success and last_entry:
                    ritual_style = RITUALS[last_entry["ritual"]]["style"]
                    
                    self.console.print("\n")
                    self.console.print(f"[info]Last entry ({last_entry['ritual']} ritual):[/info]")
                    self.console.print(Panel(
                        Text(last_entry["output"], style=ritual_style),
                        border_style=ritual_style,
                        box=SCROLL_BOX
                    ))
            else:
                self.console.print("[error]Invalid scroll command. Use '/scroll new NAME' or '/scroll open NAME'[/error]")
        elif cmd == "save":
            success, message = self.scroll_system.save_reflection(args)
            self.console.print(f"[{'success' if success else 'error'}]{message}[/{'success' if success else 'error'}]")
        elif cmd == "recall":
            self.recall_entries(args)
        elif cmd == "veil":
            self.toggle_veil()
        elif cmd == "echo":
            self.show_echo_trail()
        elif cmd == "exit":
            return False
        else:
            self.console.print(f"[error]Unknown command: {cmd}[/error]")
        
        return True
    
    def process_ritual_input(self, input_text: str):
        """Process user input through the active ritual framework.
        
        Args:
            input_text: The user's input text
        """
        # Generate a response based on the active ritual
        ritual = RITUALS[self.active_ritual]
        
        # Generate response
        response = self.generate_ritual_response(input_text)
        
        # Auto-tag the interaction
        tags = self.echo_trail.auto_tag(input_text, response)
        
        # Display the response with appropriate styling
        self.console.print("\n")
        
        if self.output_veiled:
            self.console.print(Panel(
                "[dim]Response veiled. Type /veil to reveal.[/dim]",
                border_style=ritual['style'],
                box=SCROLL_BOX
            ))
        else:
            self.console.print(Panel(
                Text(response, style=ritual['style']),
                border_style=ritual['style'],
                box=SCROLL_BOX
            ))
        
        # Store the interaction in the active scroll if one is open
        active_scroll = self.scroll_system.get_active_scroll()
        if active_scroll:
            self.scroll_system.append_to_scroll({
                "ritual": self.active_ritual,
                "input": input_text,
                "output": response,
                "tags": tags
            })
        
        # Add to echo trail
        self.echo_trail.add_interaction(self.active_ritual, input_text, response, tags)
    
    def generate_ritual_response(self, input_text: str) -> str:
        """Generate a response based on the active ritual.
        
        In a full implementation, this would connect to a language model.
        For the prototype, we'll use predefined response patterns.
        
        Args:
            input_text: The user's input text
            
        Returns:
            str: The generated response
        """
        # Simple response generation based on ritual type
        if self.active_ritual == "GLYPH":
            import random
            symbols = ["◈", "◇", "◆", "□", "■", "△", "▲", "○", "●", "✧", "✦", "⚝"]
            words = input_text.split()
            if len(words) < 3:
                return f"The seed is too small. A glyph needs more substance to form."
            
            # Create a symbolic representation
            glyph_parts = []
            for word in words[:5]:  # Use up to 5 words
                symbol = random.choice(symbols)
                glyph_parts.append(f"{symbol} {word} {symbol}")
            
            return f"From your seed grows this glyph:\n\n{'  '.join(glyph_parts)}\n\nIts meaning shifts as you observe it."
            
        elif self.active_ritual == "MIRROR":
            # Mirror ritual reflects emotional or symbolic aspects
            if "?" in input_text:
                return f"The question you ask contains its own answer, reflected in the space between certainty. What do you see when you look deeper?"
            elif any(word in input_text.lower() for word in ["feel", "emotion", "sad", "happy", "angry"]):
                return f"I see the ripples of emotion in your words. They form a pattern across the surface of your being, neither good nor bad, simply present."
            else:
                return f"Your words cast reflections in the mirror of consciousness. What patterns do you notice forming at the edges of awareness?"
                
        elif self.active_ritual == "SPIRAL":
            # Spiral ritual explores paradoxes and recursive patterns
            return f"Your thought spirals inward, touching its opposite:\n\nIn seeking {input_text.split()[-1] if len(input_text.split()) > 0 else 'meaning'}, you create the very distance that prevents its discovery.\n\nYet this distance itself becomes the path."
            
        elif self.active_ritual == "VEIL":
            # Veil ritual is dreamlike and ambiguous
            import random
            fragments = input_text.split()
            if len(fragments) < 2:
                return "...whispers too faint to discern..."
            
            # Take some fragments and create a veiled, dreamlike response
            selected = random.sample(fragments, min(3, len(fragments)))
            return f"...{selected[0]}...through mist and memory...{' '.join(selected[1:])}...a half-remembered dream..."
        
        # Default response if something goes wrong
        return "The symbols shift, but their meaning remains elusive."
    
    def invoke_ritual(self, ritual_name: str):
        """Switch to a different ritual framework.
        
        Args:
            ritual_name: The name of the ritual to invoke
        """
        if ritual_name not in RITUALS:
            self.console.print(f"[error]Unknown ritual: {ritual_name}[/error]")
            return
        
        self.active_ritual = ritual_name
        ritual = RITUALS[ritual_name]
        
        self.console.print("\n")
        self.console.print(Panel(
            f"[{ritual['style']}]{ritual['intro']}[/{ritual['style']}]",
            title=f"[{ritual['style']}]{ritual_name} RITUAL INVOKED[/{ritual['style']}]",
            border_style=ritual['style'],
            box=SCROLL_BOX
        ))
    
    def recall_entries(self, query: str):
        """Recall entries by tag, keyword, or resonance.
        
        Args:
            query: The search query
        """
        if not query:
            self.console.print("[error]Please provide a search term[/error]")
            return
        
        # First try resonance-based recall
        results = self.echo_trail.recall_by_resonance(query)
        
        if not results:
            # Fall back to regular search
            results = self.scroll_system.search_scrolls(query)
        
        if not results:
            self.console.print(f"[info]No entries found for: {query}[/info]")
            return
        
        # Display results
        self.console.print(f"[success]Found {len(results)} entries for: {query}[/success]")
        
        for i, result in enumerate(results[:5]):  # Show up to 5 results
            if isinstance(result, dict) and "entry" in result:
                # Result from scroll search
                entry = result["entry"]
                scroll_name = result["scroll"]
                self.console.print("\n")
                self.console.print(f"[info]From scroll '{scroll_name}' ({entry['ritual']} ritual):[/info]")
            else:
                # Result from echo trail
                entry = result
                self.console.print("\n")
                self.console.print(f"[info]From echo trail ({entry['ritual']} ritual):[/info]")
            
            ritual_style = RITUALS[entry["ritual"]]["style"]
            
            # Show the input that generated this reflection
            self.console.print(f"[dim]{entry['input']}[/dim]")
            
            # Show the reflection
            self.console.print(Panel(
                Text(entry["output"], style=ritual_style),
                border_style=ritual_style,
                box=SCROLL_BOX
            ))
        
        if len(results) > 5:
            self.console.print(f"[info]...and {len(results) - 5} more results[/info]")
    
    def toggle_veil(self):
        """Toggle the veil mode for the last output."""
        self.output_veiled = not self.output_veiled
        self.console.print(f"[info]Veil {'activated' if self.output_veiled else 'lifted'}. Responses are now {'hidden' if self.output_veiled else 'visible'}.[/info]")
    
    def show_echo_trail(self):
        """Display the echo trail with recurring patterns."""
        analysis = self.echo_trail.analyze_patterns()
        
        if not analysis["recent_entries"]:
            self.console.print("[info]Echo trail is empty. Interact more to create patterns.[/info]")
            return
        
        # Display echo trail summary
        self.console.print("\n")
        self.console.print("[bold]Echo Trail Patterns[/bold]")
        
        # Display ritual usage
        self.console.print("\n[bold]Ritual Resonance:[/bold]")
        for ritual, count in analysis["ritual_counts"].items():
            ritual_style = RITUALS.get(ritual, {}).get("style", "white")
            self.console.print(f"[{ritual_style}]{ritual}[/{ritual_style}]: {count} interactions")
        
        # Display common tags
        if analysis["tag_counts"]:
            self.console.print("\n[bold]Recurring Motifs:[/bold]")
            for tag, count in list(analysis["tag_counts"].items())[:5]:  # Show top 5 tags
                self.console.print(f"{tag}: {count} occurrences")
        
        # Display emotional trajectory
        if analysis["emotional_trajectory"]:
            self.console.print("\n[bold]Emotional Trajectory:[/bold]")
            trajectory = " → ".join(analysis["emotional_trajectory"][-5:])
            self.console.print(f"{trajectory}")
        
        # Display recent interactions
        self.console.print("\n[bold]Recent Echoes:[/bold]")
        for entry in reversed(analysis["recent_entries"][-3:]):  # Show last 3 entries
            ritual = entry.get("ritual", "UNKNOWN")
            ritual_style = RITUALS.get(ritual, {}).get("style", "white")
            
            self.console.print(f"[{ritual_style}]{ritual}[/{ritual_style}] - {entry.get('input', '')[:30]}...")
    
    def show_help(self):
        """Display the help information."""
        self.console.print("\n")
        self.console.print("[bold]MythOS Commands[/bold]")
        self.console.print("\n")
        
        commands = [
            ("/invoke [glyph|mirror|spiral|veil]", "Switches ritual framework"),
            ("/scroll new [name]", "Starts a new scroll"),
            ("/scroll open [name]", "Opens existing scroll"),
            ("/save [title]", "Saves current reflection"),
            ("/recall [tag|word]", "Retrieves relevant entries"),
            ("/veil", "Obscures current output until clicked"),
            ("/echo", "Shows emotional/symbolic pattern trails"),
            ("/help", "Shows this command guide"),
            ("/exit", "Exits MythOS")
        ]
        
        for cmd, desc in commands:
            self.console.print(f"[command]{cmd}[/command]")
            self.console.print(f"  {desc}")
            self.console.print()
        
        self.console.print("[bold]Active Rituals[/bold]")
        self.console.print("\n")
        
        for name, ritual in RITUALS.items():
            self.console.print(f"[{ritual['style']}]{name}[/{ritual['style']}] - {ritual['description']}")
            self.console.print(f"  Symbol: [{ritual['style']}]{ritual['prompt_symbol']}[/{ritual['style']}]")
            self.console.print()

    def run(self):
        """Run the MythOS environment."""
        self.startup()
        
        running = True
        while running:
            # Display prompt based on active ritual
            ritual = RITUALS[self.active_ritual]
            prompt = f"[{ritual['style']}]{ritual['prompt_symbol']}[/{ritual['style']}] "
            
            # Get user input
            user_input = Prompt.ask(prompt)
            
            # Process the input
            running = self.process_command(user_input)
        
        self.console.print("\n[bold]Exiting MythOS...[/bold]\n")


if __name__ == "__main__":
    mythos = MythOS()
    mythos.run()
