#!/usr/bin/env python3
"""
MythOS Echo Trail - Memory and pattern recognition system for MythOS.
"""

import json
import os
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import random


class EchoTrail:
    """Manages the echo trail and memory recall features of MythOS."""
    
    def __init__(self, data_dir: Path):
        """Initialize the echo trail system.
        
        Args:
            data_dir: Base directory for data storage
        """
        self.data_dir = data_dir
        self.echo_trail_file = data_dir / "echo_trail.json"
        
        # Initialize echo trail storage if it doesn't exist
        if not self.echo_trail_file.exists():
            with open(self.echo_trail_file, 'w') as f:
                json.dump([], f)
    
    def add_interaction(self, ritual: str, input_text: str, response: str, tags: List[str]) -> bool:
        """Add an interaction to the echo trail.
        
        Args:
            ritual: The ritual framework used
            input_text: The user's input text
            response: The system's response
            tags: Associated tags
            
        Returns:
            bool: Success status
        """
        try:
            with open(self.echo_trail_file, 'r') as f:
                echo_trail = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            echo_trail = []
        
        # Add new entry
        echo_trail.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "ritual": ritual,
            "input": input_text,
            "output": response,
            "tags": tags
        })
        
        # Keep only the last 100 entries
        if len(echo_trail) > 100:
            echo_trail = echo_trail[-100:]
        
        with open(self.echo_trail_file, 'w') as f:
            json.dump(echo_trail, f, indent=2)
        
        return True
    
    def get_echo_trail(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get the echo trail entries.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List[Dict[str, Any]]: Echo trail entries
        """
        try:
            with open(self.echo_trail_file, 'r') as f:
                echo_trail = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            echo_trail = []
        
        return echo_trail[-limit:]
    
    def analyze_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in the echo trail.
        
        Returns:
            Dict[str, Any]: Analysis results
        """
        try:
            with open(self.echo_trail_file, 'r') as f:
                echo_trail = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            echo_trail = []
        
        if not echo_trail:
            return {
                "ritual_counts": {},
                "tag_counts": {},
                "common_words": {},
                "emotional_trajectory": [],
                "recent_entries": []
            }
        
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
        
        # Extract common words (simplified)
        common_words = {}
        for entry in echo_trail:
            words = " ".join([entry.get("input", ""), entry.get("output", "")]).lower().split()
            for word in words:
                if len(word) > 5 and word.isalpha():
                    common_words[word] = common_words.get(word, 0) + 1
        
        # Sort common words by frequency and take top 10
        common_words = dict(sorted(common_words.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Create a simplified emotional trajectory
        # In a full implementation, this would use sentiment analysis
        emotional_trajectory = []
        emotions = ["reflection", "wonder", "longing", "uncertainty", "connection", "transformation"]
        
        for entry in echo_trail[-10:]:  # Last 10 entries
            tags = entry.get("tags", [])
            matching_emotions = [tag for tag in tags if tag in emotions]
            
            if matching_emotions:
                emotional_trajectory.append(matching_emotions[0])
            else:
                # If no emotion tag, assign a random one (this is a simplification)
                emotional_trajectory.append(random.choice(emotions))
        
        # Get recent entries
        recent_entries = echo_trail[-5:]
        
        return {
            "ritual_counts": ritual_counts,
            "tag_counts": dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            "common_words": common_words,
            "emotional_trajectory": emotional_trajectory,
            "recent_entries": recent_entries
        }
    
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
    
    def recall_by_resonance(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Recall entries by emotional or thematic resonance.
        
        Args:
            query: The resonance query
            limit: Maximum number of entries to return
            
        Returns:
            List[Dict[str, Any]]: Matching entries
        """
        try:
            with open(self.echo_trail_file, 'r') as f:
                echo_trail = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            echo_trail = []
        
        if not echo_trail:
            return []
        
        # Define emotional/thematic categories
        resonance_categories = {
            "longing": ["miss", "wish", "hope", "dream", "longing", "desire", "yearn"],
            "wonder": ["awe", "wonder", "amaze", "curious", "mystery", "marvel"],
            "reflection": ["think", "reflect", "consider", "ponder", "contemplate", "introspect"],
            "transformation": ["change", "transform", "become", "evolve", "shift", "metamorphosis"],
            "connection": ["connect", "relation", "bond", "together", "shared", "unity"],
            "uncertainty": ["perhaps", "maybe", "uncertain", "unclear", "doubt", "ambiguous"],
            "resonance": ["echo", "resonate", "vibrate", "harmony", "chord", "synchrony"]
        }
        
        # Check if query matches a resonance category
        matching_category = None
        for category, keywords in resonance_categories.items():
            if query.lower() in keywords or query.lower() == category:
                matching_category = category
                break
        
        results = []
        
        if matching_category:
            # Find entries with matching resonance
            for entry in echo_trail:
                # Check tags first
                if matching_category in [tag.lower() for tag in entry.get("tags", [])]:
                    results.append(entry)
                    continue
                
                # Check content for keywords
                combined_text = f"{entry.get('input', '')} {entry.get('output', '')}".lower()
                if any(keyword in combined_text for keyword in resonance_categories[matching_category]):
                    results.append(entry)
        else:
            # Treat as regular keyword search
            for entry in echo_trail:
                combined_text = f"{entry.get('input', '')} {entry.get('output', '')}".lower()
                if query.lower() in combined_text:
                    results.append(entry)
        
        # Sort by recency (newest first) and limit results
        results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return results[:limit]
