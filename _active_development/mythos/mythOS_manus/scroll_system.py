#!/usr/bin/env python3
"""
MythOS Scroll System - Data storage and management for MythOS scrolls.
"""

import json
import os
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple


class ScrollSystem:
    """Manages the creation, storage, and retrieval of MythOS scrolls."""
    
    def __init__(self, data_dir: Path):
        """Initialize the scroll system.
        
        Args:
            data_dir: Base directory for data storage
        """
        self.data_dir = data_dir
        self.scrolls_dir = data_dir / "scrolls"
        self.scrolls_dir.mkdir(exist_ok=True, parents=True)
        self.active_scroll = None
    
    def create_scroll(self, name: str) -> Tuple[bool, str]:
        """Create a new scroll with the given name.
        
        Args:
            name: The name for the new scroll
            
        Returns:
            Tuple[bool, str]: Success status and message
        """
        if not name:
            return False, "Scroll name cannot be empty"
        
        # Sanitize name for filename
        safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in name)
        filename = f"{safe_name.lower().replace(' ', '_')}.json"
        scroll_path = self.scrolls_dir / filename
        
        if scroll_path.exists():
            return False, f"A scroll named '{name}' already exists"
        
        # Create new scroll file
        scroll_data = {
            "scroll": name,
            "created": datetime.datetime.now().isoformat(),
            "last_modified": datetime.datetime.now().isoformat(),
            "entries": []
        }
        
        with open(scroll_path, 'w') as f:
            json.dump(scroll_data, f, indent=2)
        
        self.active_scroll = {
            "name": name,
            "path": scroll_path,
            "data": scroll_data
        }
        
        return True, f"Created new scroll: {name}"
    
    def open_scroll(self, name: str) -> Tuple[bool, str, Optional[Dict]]:
        """Open an existing scroll.
        
        Args:
            name: The name of the scroll to open
            
        Returns:
            Tuple[bool, str, Optional[Dict]]: Success status, message, and last entry if available
        """
        if not name:
            return False, "Scroll name cannot be empty", None
        
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
                    
                    # Return the last entry if there are any
                    last_entry = None
                    if scroll_data["entries"]:
                        last_entry = scroll_data["entries"][-1]
                    
                    return True, f"Opened scroll: {scroll_data['scroll']}", last_entry
            except (json.JSONDecodeError, KeyError):
                continue
        
        return False, f"Could not find scroll: {name}", None
    
    def append_to_scroll(self, entry: Dict[str, Any]) -> bool:
        """Append an entry to the active scroll.
        
        Args:
            entry: The entry data to append
            
        Returns:
            bool: Success status
        """
        if not self.active_scroll:
            return False
        
        self.active_scroll["data"]["entries"].append(entry)
        self.active_scroll["data"]["last_modified"] = datetime.datetime.now().isoformat()
        
        with open(self.active_scroll["path"], 'w') as f:
            json.dump(self.active_scroll["data"], f, indent=2)
        
        return True
    
    def save_reflection(self, title: str) -> Tuple[bool, str]:
        """Save the current reflection with an optional title.
        
        Args:
            title: Optional title for the saved reflection
            
        Returns:
            Tuple[bool, str]: Success status and message
        """
        if not self.active_scroll:
            return False, "No active scroll. Create or open a scroll first."
        
        if not self.active_scroll["data"]["entries"]:
            return False, "No reflections to save in the current scroll."
        
        # The last entry is already saved in the scroll, just add a title if provided
        if title:
            last_entry = self.active_scroll["data"]["entries"][-1]
            last_entry["title"] = title
            
            with open(self.active_scroll["path"], 'w') as f:
                json.dump(self.active_scroll["data"], f, indent=2)
            
            return True, f"Saved reflection as: {title}"
        else:
            return True, "Reflection saved to scroll"
    
    def list_scrolls(self) -> List[Dict[str, Any]]:
        """List all available scrolls.
        
        Returns:
            List[Dict[str, Any]]: List of scroll metadata
        """
        scrolls = []
        
        for scroll_file in self.scrolls_dir.glob("*.json"):
            try:
                with open(scroll_file, 'r') as f:
                    scroll_data = json.load(f)
                
                scrolls.append({
                    "name": scroll_data.get("scroll", "Unknown"),
                    "created": scroll_data.get("created", "Unknown"),
                    "last_modified": scroll_data.get("last_modified", scroll_data.get("created", "Unknown")),
                    "entries": len(scroll_data.get("entries", [])),
                    "path": str(scroll_file)
                })
            except (json.JSONDecodeError, KeyError):
                continue
        
        return scrolls
    
    def get_active_scroll(self) -> Optional[Dict[str, Any]]:
        """Get the currently active scroll.
        
        Returns:
            Optional[Dict[str, Any]]: Active scroll data or None
        """
        return self.active_scroll
    
    def search_scrolls(self, query: str) -> List[Dict[str, Any]]:
        """Search all scrolls for entries matching the query.
        
        Args:
            query: The search query
            
        Returns:
            List[Dict[str, Any]]: Matching entries with scroll context
        """
        if not query:
            return []
        
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
        
        return results
    
    def export_scroll(self, name: str, format: str = "json") -> Tuple[bool, str, Optional[str]]:
        """Export a scroll to the specified format.
        
        Args:
            name: The name of the scroll to export
            format: The export format (json, txt, md)
            
        Returns:
            Tuple[bool, str, Optional[str]]: Success status, message, and export path if successful
        """
        # Find the scroll
        scroll_data = None
        scroll_path = None
        
        for scroll_file in self.scrolls_dir.glob("*.json"):
            try:
                with open(scroll_file, 'r') as f:
                    data = json.load(f)
                
                if data.get("scroll", "").lower() == name.lower():
                    scroll_data = data
                    scroll_path = scroll_file
                    break
            except (json.JSONDecodeError, KeyError):
                continue
        
        if not scroll_data:
            return False, f"Could not find scroll: {name}", None
        
        # Export based on format
        if format == "json":
            # Already in JSON format, just copy to export directory
            export_dir = self.data_dir / "exports"
            export_dir.mkdir(exist_ok=True)
            
            export_path = export_dir / f"{scroll_path.stem}_export.json"
            
            with open(export_path, 'w') as f:
                json.dump(scroll_data, f, indent=2)
            
            return True, f"Exported scroll to {export_path}", str(export_path)
        
        elif format == "txt":
            # Export as plain text
            export_dir = self.data_dir / "exports"
            export_dir.mkdir(exist_ok=True)
            
            export_path = export_dir / f"{scroll_path.stem}_export.txt"
            
            with open(export_path, 'w') as f:
                f.write(f"SCROLL: {scroll_data['scroll']}\n")
                f.write(f"Created: {scroll_data['created']}\n")
                f.write(f"Last Modified: {scroll_data.get('last_modified', scroll_data['created'])}\n")
                f.write("\n" + "="*50 + "\n\n")
                
                for i, entry in enumerate(scroll_data.get("entries", []), 1):
                    f.write(f"ENTRY {i} - {entry.get('ritual', 'UNKNOWN')} RITUAL\n")
                    f.write(f"Timestamp: {entry.get('timestamp', 'Unknown')}\n")
                    if "title" in entry:
                        f.write(f"Title: {entry['title']}\n")
                    f.write("\nInput:\n")
                    f.write(entry.get("input", "") + "\n\n")
                    f.write("Response:\n")
                    f.write(entry.get("output", "") + "\n\n")
                    if "tags" in entry and entry["tags"]:
                        f.write(f"Tags: {', '.join(entry['tags'])}\n")
                    f.write("\n" + "-"*50 + "\n\n")
            
            return True, f"Exported scroll to {export_path}", str(export_path)
        
        elif format == "md":
            # Export as Markdown
            export_dir = self.data_dir / "exports"
            export_dir.mkdir(exist_ok=True)
            
            export_path = export_dir / f"{scroll_path.stem}_export.md"
            
            with open(export_path, 'w') as f:
                f.write(f"# {scroll_data['scroll']}\n\n")
                f.write(f"*Created: {scroll_data['created']}*\n\n")
                f.write(f"*Last Modified: {scroll_data.get('last_modified', scroll_data['created'])}*\n\n")
                f.write("---\n\n")
                
                for i, entry in enumerate(scroll_data.get("entries", []), 1):
                    f.write(f"## Entry {i}: {entry.get('ritual', 'UNKNOWN')} Ritual\n\n")
                    if "title" in entry:
                        f.write(f"### {entry['title']}\n\n")
                    f.write(f"*{entry.get('timestamp', 'Unknown')}*\n\n")
                    f.write("**Input:**\n\n")
                    f.write(entry.get("input", "") + "\n\n")
                    f.write("**Response:**\n\n")
                    f.write(entry.get("output", "") + "\n\n")
                    if "tags" in entry and entry["tags"]:
                        f.write(f"*Tags: {', '.join(entry['tags'])}*\n\n")
                    f.write("---\n\n")
            
            return True, f"Exported scroll to {export_path}", str(export_path)
        
        else:
            return False, f"Unsupported export format: {format}", None
