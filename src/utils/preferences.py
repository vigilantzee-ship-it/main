"""
User Preferences System - Persistent settings storage.

Manages user preferences like panel positions, UI settings, and other
configuration options that should persist between sessions.
"""

import json
import os
from typing import Any, Optional
from pathlib import Path


class Preferences:
    """
    Manages user preferences with file persistence.
    
    Stores preferences in a JSON file in the user's home directory
    or a configurable location.
    
    Attributes:
        preferences_path: Path to the preferences file
        _data: Dictionary containing all preference values
    """
    
    def __init__(self, filename: str = ".evobattle_prefs.json"):
        """
        Initialize preferences system.
        
        Args:
            filename: Name of the preferences file (stored in user's home directory)
        """
        # Store in user's home directory
        home_dir = Path.home()
        self.preferences_path = home_dir / filename
        self._data = {}
        self.load()
    
    def load(self):
        """Load preferences from file."""
        if self.preferences_path.exists():
            try:
                with open(self.preferences_path, 'r') as f:
                    self._data = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load preferences: {e}")
                self._data = {}
        else:
            self._data = {}
    
    def save(self):
        """Save preferences to file."""
        try:
            # Ensure parent directory exists
            self.preferences_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.preferences_path, 'w') as f:
                json.dump(self._data, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save preferences: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a preference value.
        
        Args:
            key: Preference key (can use dot notation for nested keys)
            default: Default value if key doesn't exist
            
        Returns:
            The preference value or default
        """
        # Support dot notation for nested keys
        keys = key.split('.')
        value = self._data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any, auto_save: bool = True):
        """
        Set a preference value.
        
        Args:
            key: Preference key (can use dot notation for nested keys)
            value: Value to set
            auto_save: Whether to automatically save after setting
        """
        # Support dot notation for nested keys
        keys = key.split('.')
        data = self._data
        
        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]
        
        data[keys[-1]] = value
        
        if auto_save:
            self.save()
    
    def clear(self, auto_save: bool = True):
        """
        Clear all preferences.
        
        Args:
            auto_save: Whether to automatically save after clearing
        """
        self._data = {}
        if auto_save:
            self.save()
    
    def has(self, key: str) -> bool:
        """
        Check if a preference key exists.
        
        Args:
            key: Preference key to check
            
        Returns:
            True if key exists, False otherwise
        """
        return self.get(key) is not None


# Global preferences instance
_global_prefs = None


def get_preferences() -> Preferences:
    """
    Get the global preferences instance.
    
    Returns:
        The global Preferences instance
    """
    global _global_prefs
    if _global_prefs is None:
        _global_prefs = Preferences()
    return _global_prefs
