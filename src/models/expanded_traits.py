"""
Expanded trait definitions for creatures and pellets.

This module defines a comprehensive trait library with:
- Behavioral traits (timidity, aggression, curiosity)
- Physical traits (defensive adaptations, camouflage, sensory abilities)
- Ecological roles (scavenger, pollinator, parasite)
- Cross-entity interaction effects
"""

from typing import Dict, Any
from .trait import Trait


# ============================================================================
# BEHAVIORAL TRAITS - Affect creature decision making and personality
# ============================================================================

TIMID_TRAIT = Trait(
    name="Timid",
    description="Avoids confrontation and flees earlier from threats",
    trait_type="behavioral",
    strength_modifier=0.9,
    speed_modifier=1.1,
    defense_modifier=1.0,
    rarity="common",
    dominance="recessive",
    interaction_effects={
        'flee_threshold': 0.6,  # Flee when HP < 60%
        'aggression_penalty': -0.3
    }
)

AGGRESSIVE_TRAIT = Trait(
    name="Aggressive",
    description="Seeks out combat and fights more fiercely",
    trait_type="behavioral",
    strength_modifier=1.2,
    speed_modifier=0.95,
    defense_modifier=0.9,
    rarity="common",
    dominance="dominant",
    interaction_effects={
        'attack_bonus': 0.15,
        'flee_threshold': 0.2,  # Only flee when HP < 20%
        'target_preference': 'strongest'
    }
)

CURIOUS_TRAIT = Trait(
    name="Curious",
    description="Explores more and discovers resources faster",
    trait_type="behavioral",
    strength_modifier=1.0,
    speed_modifier=1.05,
    defense_modifier=1.0,
    rarity="common",
    dominance="codominant",
    interaction_effects={
        'exploration_range': 1.3,
        'resource_detection': 1.25
    }
)

CAUTIOUS_TRAIT = Trait(
    name="Cautious",
    description="Careful and strategic, avoids unnecessary risks",
    trait_type="behavioral",
    strength_modifier=1.0,
    speed_modifier=1.0,
    defense_modifier=1.15,
    rarity="uncommon",
    dominance="recessive",
    interaction_effects={
        'retreat_early': True,
        'pellet_selectivity': 1.2  # More selective about food
    }
)

BOLD_TRAIT = Trait(
    name="Bold",
    description="Takes risks and fights to the end",
    trait_type="behavioral",
    strength_modifier=1.1,
    speed_modifier=1.05,
    defense_modifier=0.95,
    rarity="uncommon",
    dominance="dominant",
    interaction_effects={
        'no_retreat': True,
        'critical_hit_chance': 1.2
    }
)

SOCIAL_TRAIT = Trait(
    name="Social",
    description="Cooperates better with family and allies",
    trait_type="behavioral",
    strength_modifier=1.0,
    speed_modifier=1.0,
    defense_modifier=1.0,
    rarity="uncommon",
    dominance="codominant",
    interaction_effects={
        'group_bonus': 1.15,
        'sharing_willingness': 0.8
    }
)

SOLITARY_TRAIT = Trait(
    name="Solitary",
    description="Prefers to hunt and fight alone",
    trait_type="behavioral",
    strength_modifier=1.15,
    speed_modifier=1.0,
    defense_modifier=1.05,
    rarity="uncommon",
    dominance="recessive",
    interaction_effects={
        'group_penalty': 0.9,
        'solo_bonus': 1.2
    }
)

# ============================================================================
# PHYSICAL TRAITS - Affect stats and physical capabilities
# ============================================================================

ARMORED_TRAIT = Trait(
    name="Armored",
    description="Thick hide provides exceptional defense",
    trait_type="physical",
    strength_modifier=0.95,
    speed_modifier=0.85,
    defense_modifier=1.4,
    rarity="uncommon",
    dominance="dominant",
    interaction_effects={
        'damage_reduction': 0.25,
        'blunt_resistance': 1.5
    }
)

SWIFT_TRAIT = Trait(
    name="Swift",
    description="Incredible speed and agility",
    trait_type="physical",
    strength_modifier=0.9,
    speed_modifier=1.5,
    defense_modifier=0.95,
    rarity="uncommon",
    dominance="dominant",
    interaction_effects={
        'dodge_chance': 1.4,
        'first_strike': True
    }
)

REGENERATIVE_TRAIT = Trait(
    name="Regenerative",
    description="Slowly heals over time",
    trait_type="physical",
    strength_modifier=0.95,
    speed_modifier=0.95,
    defense_modifier=1.1,
    rarity="rare",
    dominance="recessive",
    interaction_effects={
        'hp_regen_rate': 0.02,  # 2% HP per tick
        'recovery_speed': 1.5
    }
)

VENOMOUS_TRAIT = Trait(
    name="Venomous",
    description="Attacks inflict poison damage over time",
    trait_type="physical",
    strength_modifier=1.1,
    speed_modifier=1.0,
    defense_modifier=0.95,
    rarity="rare",
    dominance="dominant",
    interaction_effects={
        'poison_on_hit': 0.3,  # 30% chance
        'poison_damage': 5
    }
)

CAMOUFLAGED_TRAIT = Trait(
    name="Camouflaged",
    description="Blends with environment, harder to detect",
    trait_type="physical",
    strength_modifier=1.0,
    speed_modifier=1.05,
    defense_modifier=1.1,
    rarity="uncommon",
    dominance="recessive",
    interaction_effects={
        'detection_range': 0.7,  # Harder to spot
        'ambush_bonus': 1.3
    }
)

KEEN_SENSES_TRAIT = Trait(
    name="Keen Senses",
    description="Enhanced vision and hearing detect threats and food",
    trait_type="physical",
    strength_modifier=1.0,
    speed_modifier=1.1,
    defense_modifier=1.0,
    rarity="common",
    dominance="codominant",
    interaction_effects={
        'threat_detection': 1.4,
        'food_detection': 1.5,
        'pellet_quality_sense': True
    }
)

POWERFUL_TRAIT = Trait(
    name="Powerful",
    description="Immense physical strength",
    trait_type="physical",
    strength_modifier=1.4,
    speed_modifier=0.9,
    defense_modifier=1.05,
    rarity="uncommon",
    dominance="dominant",
    interaction_effects={
        'critical_damage': 1.5,
        'knockback': True
    }
)

# ============================================================================
# ECOLOGICAL TRAITS - Affect interactions with environment and other entities
# ============================================================================

SCAVENGER_TRAIT = Trait(
    name="Scavenger",
    description="Prefers eating corpses, gains more nutrition from them",
    trait_type="ecological",
    strength_modifier=1.0,
    speed_modifier=1.0,
    defense_modifier=1.0,
    rarity="uncommon",
    dominance="recessive",
    interaction_effects={
        'corpse_nutrition_bonus': 1.5,
        'corpse_preference': True,
        'toxin_resistance': 1.3
    }
)

POLLINATOR_TRAIT = Trait(
    name="Pollinator",
    description="Helps pellets reproduce when feeding",
    trait_type="ecological",
    strength_modifier=0.95,
    speed_modifier=1.05,
    defense_modifier=1.0,
    rarity="rare",
    dominance="codominant",
    interaction_effects={
        'pellet_reproduction_boost': 1.4,
        'symbiotic_bonus': True,
        'plant_pellet_preference': True
    }
)

PARASITE_TRAIT = Trait(
    name="Parasitic",
    description="Drains life from opponents over time",
    trait_type="ecological",
    strength_modifier=0.95,
    speed_modifier=1.0,
    defense_modifier=0.9,
    rarity="rare",
    dominance="dominant",
    interaction_effects={
        'lifesteal': 0.15,  # Steal 15% of damage as HP
        'attach_on_hit': 0.2  # 20% chance to attach
    }
)

SYMBIOTIC_TRAIT = Trait(
    name="Symbiotic",
    description="Benefits from proximity to certain pellets",
    trait_type="ecological",
    strength_modifier=1.0,
    speed_modifier=1.0,
    defense_modifier=1.05,
    rarity="rare",
    dominance="codominant",
    interaction_effects={
        'pellet_aura_bonus': 1.2,
        'beneficial_pellets': True,
        'mutual_benefit': True
    }
)

PREDATOR_TRAIT = Trait(
    name="Predator",
    description="Hunts other creatures more effectively",
    trait_type="ecological",
    strength_modifier=1.2,
    speed_modifier=1.1,
    defense_modifier=0.95,
    rarity="uncommon",
    dominance="dominant",
    interaction_effects={
        'hunt_bonus': 1.3,
        'carnivore': True,
        'track_prey': True
    }
)

HERBIVORE_TRAIT = Trait(
    name="Herbivore",
    description="Specialized for plant consumption, cannot eat meat",
    trait_type="ecological",
    strength_modifier=0.95,
    speed_modifier=1.0,
    defense_modifier=1.1,
    rarity="common",
    dominance="recessive",
    interaction_effects={
        'plant_nutrition_bonus': 1.4,
        'cannot_eat_meat': True,
        'plant_pellet_detection': 1.5
    }
)

OMNIVORE_TRAIT = Trait(
    name="Omnivore",
    description="Can eat both plants and meat efficiently",
    trait_type="ecological",
    strength_modifier=1.05,
    speed_modifier=1.05,
    defense_modifier=1.0,
    rarity="common",
    dominance="codominant",
    interaction_effects={
        'varied_diet_bonus': 1.2,
        'nutrition_efficiency': 1.15
    }
)

TOXIN_RESISTANT_TRAIT = Trait(
    name="Toxin Resistant",
    description="Reduced damage from toxic food and poisons",
    trait_type="ecological",
    strength_modifier=1.0,
    speed_modifier=0.95,
    defense_modifier=1.15,
    rarity="uncommon",
    dominance="dominant",
    interaction_effects={
        'toxin_damage_reduction': 0.6,  # 40% less damage
        'can_eat_toxic': True
    }
)

# ============================================================================
# PELLET-SPECIFIC TRAITS - New traits for pellet evolution
# ============================================================================

class PelletTrait:
    """
    Trait specific to pellets (food sources).
    Similar to creature Trait but with pellet-specific effects.
    """
    def __init__(
        self,
        name: str,
        description: str,
        trait_type: str,
        nutritional_modifier: float = 1.0,
        growth_modifier: float = 1.0,
        toxicity_modifier: float = 1.0,
        palatability_modifier: float = 1.0,
        rarity: str = "common",
        dominance: str = "codominant",
        interaction_effects: Dict[str, Any] = None
    ):
        self.name = name
        self.description = description
        self.trait_type = trait_type
        self.nutritional_modifier = nutritional_modifier
        self.growth_modifier = growth_modifier
        self.toxicity_modifier = toxicity_modifier
        self.palatability_modifier = palatability_modifier
        self.rarity = rarity
        self.dominance = dominance
        self.interaction_effects = interaction_effects if interaction_effects else {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'name': self.name,
            'description': self.description,
            'trait_type': self.trait_type,
            'nutritional_modifier': self.nutritional_modifier,
            'growth_modifier': self.growth_modifier,
            'toxicity_modifier': self.toxicity_modifier,
            'palatability_modifier': self.palatability_modifier,
            'rarity': self.rarity,
            'dominance': self.dominance,
            'interaction_effects': self.interaction_effects
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'PelletTrait':
        """Deserialize from dictionary."""
        return PelletTrait(
            name=data.get('name', 'Basic Pellet Trait'),
            description=data.get('description', ''),
            trait_type=data.get('trait_type', 'neutral'),
            nutritional_modifier=data.get('nutritional_modifier', 1.0),
            growth_modifier=data.get('growth_modifier', 1.0),
            toxicity_modifier=data.get('toxicity_modifier', 1.0),
            palatability_modifier=data.get('palatability_modifier', 1.0),
            rarity=data.get('rarity', 'common'),
            dominance=data.get('dominance', 'codominant'),
            interaction_effects=data.get('interaction_effects', {})
        )


# Pellet trait definitions
NUTRITIOUS_PELLET_TRAIT = PelletTrait(
    name="Highly Nutritious",
    description="Provides exceptional energy to consumers",
    trait_type="beneficial",
    nutritional_modifier=1.5,
    palatability_modifier=1.2,
    rarity="uncommon",
    dominance="recessive"
)

TOXIC_DEFENSE_PELLET_TRAIT = PelletTrait(
    name="Toxic Defense",
    description="Contains toxins that harm creatures without resistance",
    trait_type="defensive",
    toxicity_modifier=2.0,
    palatability_modifier=0.5,
    rarity="uncommon",
    dominance="dominant",
    interaction_effects={
        'damage_on_consumption': 10,
        'discourages_predation': True
    }
)

FAST_GROWING_PELLET_TRAIT = PelletTrait(
    name="Fast Growing",
    description="Reproduces more quickly",
    trait_type="reproductive",
    growth_modifier=1.8,
    nutritional_modifier=0.9,
    rarity="common",
    dominance="dominant"
)

ATTRACTIVE_PELLET_TRAIT = PelletTrait(
    name="Attractive",
    description="Highly palatable and sought after by creatures",
    trait_type="beneficial",
    palatability_modifier=1.6,
    rarity="uncommon",
    dominance="codominant",
    interaction_effects={
        'attract_creatures': True,
        'preferred_food': True
    }
)

REPELLENT_PELLET_TRAIT = PelletTrait(
    name="Repellent",
    description="Emits chemicals that discourage consumption",
    trait_type="defensive",
    palatability_modifier=0.3,
    toxicity_modifier=1.2,
    rarity="uncommon",
    dominance="dominant",
    interaction_effects={
        'repel_creatures': True,
        'avoid_radius': 5.0
    }
)

MEDICINAL_PELLET_TRAIT = PelletTrait(
    name="Medicinal",
    description="Heals creatures that consume it",
    trait_type="beneficial",
    nutritional_modifier=1.1,
    palatability_modifier=0.8,
    rarity="rare",
    dominance="recessive",
    interaction_effects={
        'heal_on_consumption': 15,
        'cure_poison': True
    }
)

SYMBIOTIC_PELLET_TRAIT = PelletTrait(
    name="Symbiotic",
    description="Benefits from creature proximity, grows near them",
    trait_type="ecological",
    growth_modifier=1.3,
    rarity="rare",
    dominance="codominant",
    interaction_effects={
        'creature_proximity_bonus': 1.4,
        'mutual_benefit': True
    }
)

HARDY_PELLET_TRAIT = PelletTrait(
    name="Hardy",
    description="Survives longer and in harsh conditions",
    trait_type="survival",
    growth_modifier=0.9,
    nutritional_modifier=1.1,
    rarity="common",
    dominance="recessive",
    interaction_effects={
        'lifespan_multiplier': 2.0,
        'environmental_resistance': True
    }
)

# ============================================================================
# TRAIT COLLECTIONS
# ============================================================================

# All creature traits
ALL_CREATURE_TRAITS = [
    # Behavioral
    TIMID_TRAIT, AGGRESSIVE_TRAIT, CURIOUS_TRAIT, CAUTIOUS_TRAIT, BOLD_TRAIT,
    SOCIAL_TRAIT, SOLITARY_TRAIT,
    # Physical
    ARMORED_TRAIT, SWIFT_TRAIT, REGENERATIVE_TRAIT, VENOMOUS_TRAIT,
    CAMOUFLAGED_TRAIT, KEEN_SENSES_TRAIT, POWERFUL_TRAIT,
    # Ecological
    SCAVENGER_TRAIT, POLLINATOR_TRAIT, PARASITE_TRAIT, SYMBIOTIC_TRAIT,
    PREDATOR_TRAIT, HERBIVORE_TRAIT, OMNIVORE_TRAIT, TOXIN_RESISTANT_TRAIT
]

# All pellet traits
ALL_PELLET_TRAITS = [
    NUTRITIOUS_PELLET_TRAIT, TOXIC_DEFENSE_PELLET_TRAIT, FAST_GROWING_PELLET_TRAIT,
    ATTRACTIVE_PELLET_TRAIT, REPELLENT_PELLET_TRAIT, MEDICINAL_PELLET_TRAIT,
    SYMBIOTIC_PELLET_TRAIT, HARDY_PELLET_TRAIT
]

# Traits by category
BEHAVIORAL_TRAITS = [TIMID_TRAIT, AGGRESSIVE_TRAIT, CURIOUS_TRAIT, CAUTIOUS_TRAIT, BOLD_TRAIT, SOCIAL_TRAIT, SOLITARY_TRAIT]
PHYSICAL_TRAITS = [ARMORED_TRAIT, SWIFT_TRAIT, REGENERATIVE_TRAIT, VENOMOUS_TRAIT, CAMOUFLAGED_TRAIT, KEEN_SENSES_TRAIT, POWERFUL_TRAIT]
ECOLOGICAL_TRAITS = [SCAVENGER_TRAIT, POLLINATOR_TRAIT, PARASITE_TRAIT, SYMBIOTIC_TRAIT, PREDATOR_TRAIT, HERBIVORE_TRAIT, OMNIVORE_TRAIT, TOXIN_RESISTANT_TRAIT]

# Traits by dominance
DOMINANT_TRAITS = [t for t in ALL_CREATURE_TRAITS if t.dominance == "dominant"]
RECESSIVE_TRAITS = [t for t in ALL_CREATURE_TRAITS if t.dominance == "recessive"]
CODOMINANT_TRAITS = [t for t in ALL_CREATURE_TRAITS if t.dominance == "codominant"]
