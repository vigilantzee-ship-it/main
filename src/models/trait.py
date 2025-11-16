"""
Trait model - Represents inheritable characteristics and abilities.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
import time


@dataclass
class TraitProvenance:
    """
    Tracks the origin and history of a trait.
    
    Attributes:
        source_type: How the trait was acquired ('inherited', 'mutated', 'emergent')
        parent_traits: Names of parent traits if inherited
        generation: Generation number when trait appeared
        timestamp: When the trait was acquired
        mutation_count: Number of mutations this trait has undergone
    """
    source_type: str = "inherited"
    parent_traits: List[str] = field(default_factory=list)
    generation: int = 0
    timestamp: float = field(default_factory=time.time)
    mutation_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'source_type': self.source_type,
            'parent_traits': self.parent_traits,
            'generation': self.generation,
            'timestamp': self.timestamp,
            'mutation_count': self.mutation_count
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TraitProvenance':
        """Deserialize from dictionary."""
        return TraitProvenance(
            source_type=data.get('source_type', 'inherited'),
            parent_traits=data.get('parent_traits', []),
            generation=data.get('generation', 0),
            timestamp=data.get('timestamp', time.time()),
            mutation_count=data.get('mutation_count', 0)
        )


class Trait:
    """
    Represents a genetic trait that can be inherited by fighters.
    
    Traits modify fighter attributes or provide special abilities during
    battles. They can be passed down through breeding and may mutate or
    combine in offspring.
    
    Enhanced with:
    - Dominance system (dominant/recessive genes)
    - Expanded trait categories (behavioral, physical, ecological)
    - Trait provenance tracking
    - Cross-entity interaction effects
    
    Attributes:
        name (str): The trait's name
        description (str): What the trait does
        trait_type (str): Category of trait (behavioral, physical, ecological, offensive, defensive, utility)
        strength_modifier (float): Multiplier for strength stat
        speed_modifier (float): Multiplier for speed stat
        defense_modifier (float): Multiplier for defense stat
        rarity (str): How rare the trait is (common, uncommon, rare, legendary)
        dominance (str): Gene dominance ('dominant', 'recessive', 'codominant')
        provenance (TraitProvenance): Tracks origin and history
        interaction_effects (Dict): Effects on cross-entity interactions
    """
    
    def __init__(
        self,
        name="Basic Trait",
        description="A basic trait",
        trait_type="neutral",
        strength_modifier=1.0,
        speed_modifier=1.0,
        defense_modifier=1.0,
        rarity="common",
        dominance="codominant",
        provenance: Optional[TraitProvenance] = None,
        interaction_effects: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new Trait.
        
        Args:
            name (str): The trait's name
            description (str): Description of what the trait does
            trait_type (str): Category of the trait
            strength_modifier (float): Strength stat multiplier
            speed_modifier (float): Speed stat multiplier
            defense_modifier (float): Defense stat multiplier
            rarity (str): Rarity level of the trait
            dominance (str): Gene dominance type
            provenance (TraitProvenance): Trait origin tracking
            interaction_effects (Dict): Effects on cross-entity interactions
        """
        self.name = name
        self.description = description
        self.trait_type = trait_type
        self.strength_modifier = strength_modifier
        self.speed_modifier = speed_modifier
        self.defense_modifier = defense_modifier
        self.rarity = rarity
        self.dominance = dominance
        self.provenance = provenance if provenance else TraitProvenance()
        self.interaction_effects = interaction_effects if interaction_effects else {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'name': self.name,
            'description': self.description,
            'trait_type': self.trait_type,
            'strength_modifier': self.strength_modifier,
            'speed_modifier': self.speed_modifier,
            'defense_modifier': self.defense_modifier,
            'rarity': self.rarity,
            'dominance': self.dominance,
            'provenance': self.provenance.to_dict(),
            'interaction_effects': self.interaction_effects
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Trait':
        """Deserialize from dictionary."""
        provenance = None
        if 'provenance' in data:
            provenance = TraitProvenance.from_dict(data['provenance'])
        
        return Trait(
            name=data.get('name', 'Basic Trait'),
            description=data.get('description', 'A basic trait'),
            trait_type=data.get('trait_type', 'neutral'),
            strength_modifier=data.get('strength_modifier', 1.0),
            speed_modifier=data.get('speed_modifier', 1.0),
            defense_modifier=data.get('defense_modifier', 1.0),
            rarity=data.get('rarity', 'common'),
            dominance=data.get('dominance', 'codominant'),
            provenance=provenance,
            interaction_effects=data.get('interaction_effects', {})
        )
    
    def copy(self) -> 'Trait':
        """Create a copy of this trait."""
        return Trait(
            name=self.name,
            description=self.description,
            trait_type=self.trait_type,
            strength_modifier=self.strength_modifier,
            speed_modifier=self.speed_modifier,
            defense_modifier=self.defense_modifier,
            rarity=self.rarity,
            dominance=self.dominance,
            provenance=TraitProvenance(
                source_type=self.provenance.source_type,
                parent_traits=self.provenance.parent_traits.copy(),
                generation=self.provenance.generation,
                timestamp=self.provenance.timestamp,
                mutation_count=self.provenance.mutation_count
            ),
            interaction_effects=self.interaction_effects.copy()
        )
    
    def __repr__(self):
        """String representation of the Trait."""
        return f"Trait(name='{self.name}', type='{self.trait_type}', rarity='{self.rarity}', dominance='{self.dominance}')"
