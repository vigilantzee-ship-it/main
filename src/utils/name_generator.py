"""
Simple random name generator for creatures.

Generates memorable creature names by combining syllables and patterns.
"""

import random


class NameGenerator:
    """Generate random but memorable names for creatures."""
    
    # Simple syllable components for creature names
    PREFIXES = [
        "Al", "Bel", "Cro", "Dar", "El", "Fal", "Gar", "Hal", "Ix", "Jor",
        "Kal", "Lor", "Mal", "Nor", "Or", "Pax", "Quin", "Ral", "Sal", "Tor",
        "Ul", "Val", "Wil", "Xan", "Yor", "Zel", "Bro", "Dex", "Fin", "Grim"
    ]
    
    MIDDLES = [
        "a", "e", "i", "o", "u", "an", "en", "in", "on", "ar", "er", "ir",
        "or", "ax", "ex", "ix", "ox"
    ]
    
    SUFFIXES = [
        "n", "x", "s", "th", "k", "r", "d", "m", "l", "p",
        "nar", "dor", "kin", "win", "ton", "rak", "vas", "zor", "mir", "tex"
    ]
    
    def __init__(self, seed=None):
        """
        Initialize the name generator.
        
        Args:
            seed: Optional random seed for reproducibility
        """
        self.rng = random.Random(seed)
    
    def generate(self, min_syllables=2, max_syllables=3):
        """
        Generate a random creature name.
        
        Args:
            min_syllables: Minimum number of syllables (default: 2)
            max_syllables: Maximum number of syllables (default: 3)
            
        Returns:
            str: A randomly generated name
        """
        num_syllables = self.rng.randint(min_syllables, max_syllables)
        
        if num_syllables == 2:
            # Simple two-part name
            name = self.rng.choice(self.PREFIXES) + self.rng.choice(self.SUFFIXES)
        else:
            # Three-part name with middle
            name = (
                self.rng.choice(self.PREFIXES) +
                self.rng.choice(self.MIDDLES) +
                self.rng.choice(self.SUFFIXES)
            )
        
        # Capitalize first letter
        return name.capitalize()
    
    def generate_batch(self, count, unique=True):
        """
        Generate a batch of names.
        
        Args:
            count: Number of names to generate
            unique: If True, ensure all names are unique (default: True)
            
        Returns:
            list: List of generated names
        """
        if unique:
            names = set()
            attempts = 0
            max_attempts = count * 100
            
            while len(names) < count and attempts < max_attempts:
                names.add(self.generate())
                attempts += 1
            
            return list(names)
        else:
            return [self.generate() for _ in range(count)]


# Module-level convenience function
_default_generator = None


def generate_name(seed=None):
    """
    Generate a random creature name using the default generator.
    
    Args:
        seed: Optional random seed for reproducibility
        
    Returns:
        str: A randomly generated name
    """
    global _default_generator
    
    if seed is not None or _default_generator is None:
        _default_generator = NameGenerator(seed)
    
    return _default_generator.generate()
