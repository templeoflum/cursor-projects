#!/usr/bin/env python3
"""
MythOS v0.1 - A symbolic operating system for reflective, recursive interaction with language models.
"""

import json
import os
import datetime
import random
from pathlib import Path
from typing import Dict, List, Optional, Any

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.theme import Theme
from rich.style import Style
from rich.box import Box, HEAVY

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
        self.active_scroll = None
        self.data_dir = Path("./scrolls")
        self.data_dir.mkdir(exist_ok=True)
        
        # Ensure scrolls directory exists
        self.scrolls_dir = self.data_dir / "scrolls"
        self.scrolls_dir.mkdir(exist_ok=True)
        
        # Initialize echo trail storage
        self.echo_trail_file = self.data_dir / "echo_trail.json"
        if not self.echo_trail_file.exists():
            with open(self.echo_trail_file, 'w') as f:
                json.dump([], f)
    
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
                self.create_scroll(args[4:])
            elif args.startswith("open "):
                self.open_scroll(args[5:])
            else:
                self.console.print("[error]Invalid scroll command. Use '/scroll new NAME' or '/scroll open NAME'[/error]")
        elif cmd == "save":
            self.save_reflection(args)
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
        
        # In a full implementation, this would connect to a language model
        # For the prototype, we'll use predefined responses based on the ritual
        response = self.generate_ritual_response(input_text)
        
        # Display the response with appropriate styling
        self.console.print("\n")
        self.console.print(Panel(
            Text(response, style=ritual['style']),
            border_style=ritual['style'],
            box=SCROLL_BOX
        ))
        
        # Store the interaction in the active scroll if one is open
        if self.active_scroll:
            self.append_to_scroll({
                "timestamp": datetime.datetime.now().isoformat(),
                "ritual": self.active_ritual,
                "input": input_text,
                "output": response,
                "tags": self.auto_tag(input_text, response)
            })
        
        # Add to echo trail
        self.add_to_echo_trail(input_text, response)
    
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
    
    def create_scroll(self, name: str):
        """Create a new scroll with the given name.
        
        Args:
            name: The name for the new scroll
        """
        if not name:
            self.console.print("[error]Scroll name cannot be empty[/error]")
            return
        
        # Sanitize name for filename
        safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in name)
        filename = f"{safe_name.lower().replace(' ', '_')}.json"
        scroll_path = self.scrolls_dir / filename
        
        if scroll_path.exists():
            self.console.print(f"[error]A scroll named '{name}' already exists[/error]")
            return
        
        # Create new scroll file
        scroll_data = {
            "scroll": name,
            "created": datetime.datetime.now().isoformat(),
            "entries": []
        }
        
        with open(scroll_path, 'w') as f:
            json.dump(scroll_data, f, indent=2)
        
        self.active_scroll = {
            "name": name,
            "path": scroll_path,
            "data": scroll_data
        }
        
        self.console.print(f"[success]Created new scroll: {name}[/success]")
    
    def open_scroll(self, name: str):
        """Open an existing scroll.
        
        Args:
            name: The name of the scroll to open
        """
        if not name:
            self.console.print("[error]Scroll name cannot be empty[/error]")
            return
        
        # Try to find the scroll file
        for scroll_file in self.scrolls_dir.glob("*.json"):
            try:
                with open(scroll_file, 'r') as f:
                    scroll_data = json.load(f)
                
                if scroll_data.get("scroll", "").lower() == name.lower():
                    self.active_scroll = {
                        "name": scroll_data["scroll"],
                        "path": scroll_file,
                        "data": scroll_data
                    }
                    
                    self.console.print(f"[success]Opened scroll: {scroll_data['scroll']}[/success]")
                    
                    # Display the last entry if there are any
                    if scroll_data["entries"]:
                        last_entry = scroll_data["entries"][-1]
                        ritual_style = RITUALS[last_entry["ritual"]]["style"]
                        
                        self.console.print("\n")
                        self.console.print(f"[info]Last entry ({last_entry['ritual']} ritual):[/info]")
                        self.console.print(Panel(
                            Text(last_entry["output"], style=ritual_style),
                            border_style=ritual_style,
                            box=SCROLL_BOX
                        ))
                    
                    return
            except (json.JSONDecodeError, KeyError):
                continue
        
        self.console.print(f"[error]Could not find scroll: {name}[/error]")
    
    def append_to_scroll(self, entry: Dict[str, Any]):
        """Append an entry to the active scroll.
        
        Args:
            entry: The entry data to append
        """
        if not self.active_scroll:
            return
        
        self.active_scroll["data"]["entries"].append(entry)
        
        with open(self.active_scroll["path"], 'w') as f:
            json.dump(self.active_scroll["data"], f, indent=2)
    
    def save_reflection(self, title: str):
        """Save the current reflection with an optional title.
        
        Args:
            title: Optional title for the saved reflection
        """
        if not self.active_scroll:
            self.console.print("[error]No active scroll. Create or open a scroll first.[/error]")
            return
        
        if not self.active_scroll["data"]["entries"]:
            self.console.print("[error]No reflections to save in the current scroll.[/error]")
            return
        
        # The last entry is already saved in the scroll, just add a title if provided
        if title:
            last_entry = self.active_scroll["data"]["entries"][-1]
            last_entry["title"] = title
            
            with open(self.active_scroll["path"], 'w') as f:
                json.dump(self.active_scroll["data"], f, indent=2)
            
            self.console.print(f"[success]Saved reflection as: {title}[/success]")
        else:
            self.console.print("[success]Reflection saved to scroll[/success]")
    
    def recall_entries(self, query: str):
        """Recall entries by tag, keyword, or resonance.
        
        Args:
            query: The search query
        """
        if not query:
            self.console.print("[error]Please provide a search term[/error]")
            return
        
        results = []
        
        # Search through all scrolls
        for scroll_file in self.scrolls_dir.glob("*.json"):
            try:
                with open(scroll_file, 'r') as f:
                    scroll_data = json.load(f)
                
                for entry in scroll_data.get("entries", []):
                    # Check if query matches tags, input, or output
                    if (query.lower() in [tag.lower() for tag in entry.get("tags", [])] or
                        query.lower() in entry.get("input", "").lower() or
                        query.lower() in entry.get("output", "").lower()):
                        
                        results.append({
                            "scroll": scroll_data["scroll"],
                            "entry": entry
                        })
            except (json.JSONDecodeError, KeyError):
                continue
        
        if not results:
            self.console.print(f"[info]No entries found for: {query}[/info]")
            return
        
        # Display results
        self.console.print(f"[success]Found {len(results)} entries for: {query}[/success]")
        
        for i, result in enumerate(results[:5]):  # Show up to 5 results
            entry = result["entry"]
            ritual_style = RITUALS[entry["ritual"]]["style"]
            
            self.console.print("\n")
            self.console.print(f"[info]From scroll '{result['scroll']}' ({entry['ritual']} ritual):[/info]")
            
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
        # In a full implementation, this would hide/show the last output
        # For the prototype, we'll just acknowledge the command
        self.console.print("[info]Veil toggled. The last reflection shifts between seen and unseen.[/info]")
    
    def add_to_echo_trail(self, input_text: str, response: str):
        """Add an interaction to the echo trail.
        
        Args:
            input_text: The user's input text
            response: The system's response
        """
        try:
            with open(self.echo_trail_file, 'r') as f:
                echo_trail = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            echo_trail = []
        
        # Add new entry
        echo_trail.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "ritual": self.active_ritual,
            "input": input_text,
            "output": response,
            "tags": self.auto_tag(input_text, response)
        })
        
        # Keep only the last 100 entries
        if len(echo_trail) > 100:
            echo_trail = echo_trail[-100:]
        
        with open(self.echo_trail_file, 'w') as f:
            json.dump(echo_trail, f, indent=2)
    
    def show_echo_trail(self):
        """Display the echo trail with recurring patterns."""
        try:
            with open(self.echo_trail_file, 'r') as f:
                echo_trail = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            echo_trail = []
        
        if not echo_trail:
            self.console.print("[info]Echo trail is empty. Interact more to create patterns.[/info]")
            return
        
        # In a full implementation, this would analyze patterns
        # For the prototype, we'll show recent interactions and simple patterns
        
        # Count ritual usage
        ritual_counts = {}
        for entry in echo_trail:
            ritual = entry.get("ritual", "UNKNOWN")
            ritual_counts[ritual] = ritual_counts.get(ritual, 0) + 1
        
        # Collect all tags
        all_tags = []
        for entry in echo_trail:
            all_tags.extend(entry.get("tags", []))
        
        # Count tag frequency
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Sort tags by frequency
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Display echo trail summary
        self.console.print("\n")
        self.console.print("[bold]Echo Trail Patterns[/bold]")
        
        # Display ritual usage
        self.console.print("\n[bold]Ritual Resonance:[/bold]")
        for ritual, count in ritual_counts.items():
            ritual_style = RITUALS.get(ritual, {}).get("style", "white")
            self.console.print(f"[{ritual_style}]{ritual}[/{ritual_style}]: {count} interactions")
        
        # Display common tags
        if sorted_tags:
            self.console.print("\n[bold]Recurring Motifs:[/bold]")
            for tag, count in sorted_tags[:5]:  # Show top 5 tags
                self.console.print(f"{tag}: {count} occurrences")
        
        # Display recent interactions
        self.console.print("\n[bold]Recent Echoes:[/bold]")
        for entry in reversed(echo_trail[-3:]):  # Show last 3 entries
            ritual = entry.get("ritual", "UNKNOWN")
            ritual_style = RITUALS.get(ritual, {}).get("style", "white")
            
            self.console.print(f"[{ritual_style}]{ritual}[/{ritual_style}] - {entry.get('input', '')[:30]}...")
    
    def auto_tag(self, input_text: str, response: str) -> List[str]:
        """Automatically generate tags for an interaction.
        
        Args:
            input_text: The user's input text
            response: The system's response
            
        Returns:
            List[str]: Generated tags
        """
        # In a full implementation, this would use NLP or a language model
        # For the prototype, we'll use simple keyword extraction
        
        # Combine input and response for analysis
        combined_text = f"{input_text} {response}".lower()
        
        # Define some emotion/theme keywords to look for
        emotions = {
            "longing": ["miss", "wish", "hope", "dream", "longing", "desire"],
            "wonder": ["awe", "wonder", "amaze", "curious", "mystery"],
            "reflection": ["think", "reflect", "consider", "ponder", "contemplate"],
            "transformation": ["change", "transform", "become", "evolve", "shift"],
            "connection": ["connect", "relation", "bond", "together", "shared"],
            "uncertainty": ["perhaps", "maybe", "uncertain", "unclear", "doubt"],
            "resonance": ["echo", "resonate", "vibrate", "harmony", "chord"]
        }
        
        # Check for emotion keywords
        tags = []
        for emotion, keywords in emotions.items():
            if any(keyword in combined_text for keyword in keywords):
                tags.append(emotion)
        
        # Add ritual as a tag
        tags.append(self.active_ritual.lower())
        
        # Extract potential noun phrases (very simplified)
        words = combined_text.split()
        for word in words:
            # Only consider words of sufficient length that aren't already emotions
            if (len(word) > 5 and 
                word.isalpha() and 
                word not in [tag.lower() for tag in tags] and
                not any(word in keywords for keywords in emotions.values())):
                tags.append(word)
        
        # Limit to 5 tags maximum
        return tags[:5]
    
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
