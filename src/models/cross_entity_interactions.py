"""
Cross-entity interaction system.

Handles trait-driven interactions between creatures and pellets, including:
- Selective foraging based on traits
- Symbiotic relationships
- Pollination effects
- Toxin resistance
- Scavenger behavior
"""

from typing import List, Optional, Tuple
from .creature import Creature
from .pellet import Pellet
from .trait import Trait


class CrossEntityInteractions:
    """
    Manages interactions between creatures and pellets.
    
    This system enables emergent behaviors based on traits:
    - Creatures with Pollinator trait boost pellet reproduction
    - Creatures with Toxin Resistant can eat toxic pellets
    - Scavenger trait affects corpse pellet preference
    - Symbiotic traits create mutual benefits
    """
    
    @staticmethod
    def calculate_pellet_preference(creature: Creature, pellet: Pellet) -> float:
        """
        Calculate how much a creature prefers a specific pellet.
        
        Higher values mean the creature is more likely to eat this pellet.
        
        Args:
            creature: The creature evaluating the pellet
            pellet: The pellet being evaluated
            
        Returns:
            Preference score (0.0 to 2.0+, 1.0 = neutral)
        """
        base_preference = pellet.get_palatability_score()
        
        # Check creature traits
        traits = {t.name: t for t in creature.traits}
        
        # Picky Eater - strongly affected by palatability
        if "Picky Eater" in traits or "Cautious" in traits:
            if pellet.traits.palatability > 0.7:
                base_preference *= 1.4  # Strong preference for quality
            elif pellet.traits.palatability < 0.4:
                base_preference *= 0.3  # Avoid low quality
        
        # Indiscriminate Eater - doesn't care about quality
        if "Indiscriminate Eater" in traits:
            base_preference = 1.0  # Eats anything
        
        # Scavenger - prefers corpse pellets (high nutrition, low growth rate)
        if "Scavenger" in traits:
            if pellet.traits.growth_rate < 0.01:  # Likely a corpse
                scavenger_trait = traits["Scavenger"]
                bonus = scavenger_trait.interaction_effects.get('corpse_nutrition_bonus', 1.0)
                base_preference *= bonus
        
        # Herbivore - prefers plant pellets (normal growth rate, green color)
        if "Herbivore" in traits:
            # Check if pellet looks like a plant (greenish color)
            green_value = pellet.traits.color[1]  # G component
            if green_value > 150:
                herbivore_trait = traits["Herbivore"]
                bonus = herbivore_trait.interaction_effects.get('plant_nutrition_bonus', 1.0)
                base_preference *= bonus
        
        # Toxin Resistant - less affected by toxicity
        if "Toxin Resistant" in traits:
            # Can eat toxic pellets that others avoid
            if pellet.traits.toxicity > 0.3:
                base_preference *= 1.3  # Actually prefer toxic (less competition)
        else:
            # Normal creatures avoid toxic pellets
            if pellet.traits.toxicity > 0.2:
                base_preference *= (1.0 - pellet.traits.toxicity)
        
        # Keen Senses - can detect pellet quality better
        if "Keen Senses" in traits:
            # Amplify preferences (good becomes better, bad becomes worse)
            if base_preference > 1.0:
                base_preference *= 1.2
            elif base_preference < 0.7:
                base_preference *= 0.8
        
        # Curious - willing to try varied foods
        if "Curious" in traits:
            base_preference *= 1.1  # Small bonus to exploration
        
        return base_preference
    
    @staticmethod
    def apply_consumption_effects(
        creature: Creature,
        pellet: Pellet
    ) -> dict:
        """
        Apply effects when a creature consumes a pellet.
        
        Args:
            creature: The creature eating
            pellet: The pellet being eaten
            
        Returns:
            Dictionary of effects applied
        """
        effects = {
            'nutrition_gained': 0,
            'hp_change': 0,
            'status_effects': [],
            'special_effects': []
        }
        
        # Base nutrition
        base_nutrition = pellet.get_nutritional_value()
        nutrition_multiplier = 1.0
        
        # Check creature traits
        traits = {t.name: t for t in creature.traits}
        
        # Scavenger bonus for corpses
        if "Scavenger" in traits and pellet.traits.growth_rate < 0.01:
            scavenger_trait = traits["Scavenger"]
            bonus = scavenger_trait.interaction_effects.get('corpse_nutrition_bonus', 1.0)
            nutrition_multiplier *= bonus
            effects['special_effects'].append('scavenger_bonus')
        
        # Herbivore bonus for plants
        if "Herbivore" in traits and pellet.traits.color[1] > 150:
            herbivore_trait = traits["Herbivore"]
            bonus = herbivore_trait.interaction_effects.get('plant_nutrition_bonus', 1.0)
            nutrition_multiplier *= bonus
            effects['special_effects'].append('herbivore_bonus')
        
        # Omnivore bonus for varied diet
        if "Omnivore" in traits:
            omnivore_trait = traits["Omnivore"]
            bonus = omnivore_trait.interaction_effects.get('nutrition_efficiency', 1.0)
            nutrition_multiplier *= bonus
        
        # Apply nutrition
        effects['nutrition_gained'] = int(base_nutrition * nutrition_multiplier)
        
        # Toxin damage
        if pellet.traits.toxicity > 0:
            toxin_damage = pellet.traits.toxicity * 20  # Base damage
            
            # Toxin Resistant reduces damage
            if "Toxin Resistant" in traits:
                resistant_trait = traits["Toxin Resistant"]
                reduction = resistant_trait.interaction_effects.get('toxin_damage_reduction', 1.0)
                toxin_damage *= reduction
                effects['special_effects'].append('toxin_resistance')
            
            # Indiscriminate Eater also has some resistance
            if "Indiscriminate Eater" in traits:
                toxin_damage *= 0.5
            
            effects['hp_change'] -= int(toxin_damage)
        
        # Check for pellet medicinal properties (future enhancement)
        # This would check pellet traits for healing effects
        
        return effects
    
    @staticmethod
    def apply_pollination_effect(creature: Creature, pellet: Pellet) -> float:
        """
        Calculate pollination boost to pellet reproduction.
        
        Creatures with Pollinator trait boost nearby pellet reproduction.
        
        Args:
            creature: The creature near the pellet
            pellet: The pellet that might be pollinated
            
        Returns:
            Reproduction rate multiplier (1.0 = no effect)
        """
        traits = {t.name: t for t in creature.traits}
        
        if "Pollinator" in traits:
            pollinator_trait = traits["Pollinator"]
            boost = pollinator_trait.interaction_effects.get('pellet_reproduction_boost', 1.0)
            return boost
        
        return 1.0
    
    @staticmethod
    def calculate_symbiotic_benefit(
        creature: Creature,
        nearby_pellets: List[Pellet],
        proximity_range: float = 10.0
    ) -> dict:
        """
        Calculate benefits from symbiotic relationships with pellets.
        
        Args:
            creature: The creature to check
            nearby_pellets: Pellets within proximity
            proximity_range: Maximum distance for symbiosis
            
        Returns:
            Dictionary of symbiotic benefits
        """
        benefits = {
            'stat_boost': 1.0,
            'hp_regen': 0.0,
            'energy_regen': 0.0
        }
        
        traits = {t.name: t for t in creature.traits}
        
        if "Symbiotic" in traits and nearby_pellets:
            symbiotic_trait = traits["Symbiotic"]
            
            # Count nearby pellets
            pellet_count = len(nearby_pellets)
            
            # Get bonus from trait
            bonus = symbiotic_trait.interaction_effects.get('pellet_aura_bonus', 1.0)
            
            # Apply bonus (capped at 3 pellets for balance)
            effective_count = min(pellet_count, 3)
            benefits['stat_boost'] = 1.0 + (bonus - 1.0) * (effective_count / 3.0)
            benefits['hp_regen'] = effective_count * 0.5  # Small HP regen
        
        return benefits
    
    @staticmethod
    def check_pellet_avoidance(creature: Creature, pellet: Pellet) -> bool:
        """
        Check if creature should avoid a pellet due to repellent traits.
        
        Args:
            creature: The creature checking
            pellet: The pellet to check
            
        Returns:
            True if creature should avoid this pellet
        """
        # Very toxic pellets are avoided by non-resistant creatures
        if pellet.traits.toxicity > 0.4:
            traits = {t.name: t for t in creature.traits}
            if "Toxin Resistant" not in traits and "Indiscriminate Eater" not in traits:
                return True
        
        # Very unpalatable pellets are avoided
        if pellet.traits.palatability < 0.2:
            traits = {t.name: t for t in creature.traits}
            if "Indiscriminate Eater" not in traits:
                return True
        
        return False


class PelletCreatureInteraction:
    """
    Handles how pellets affect creatures that consume them.
    
    Future enhancements could include:
    - Pellets that boost creature stats temporarily
    - Pellets that provide special abilities
    - Pellets that affect creature behavior
    """
    
    @staticmethod
    def get_stat_modifiers(pellet: Pellet) -> dict:
        """
        Get temporary stat modifiers from consuming a pellet.
        
        Args:
            pellet: The pellet being consumed
            
        Returns:
            Dictionary of stat modifiers
        """
        modifiers = {
            'strength': 1.0,
            'speed': 1.0,
            'defense': 1.0
        }
        
        # High nutrition pellets provide temporary strength
        if pellet.traits.nutritional_value > 60:
            modifiers['strength'] = 1.1
        
        # Low toxicity, high palatability provides speed
        if pellet.traits.toxicity < 0.1 and pellet.traits.palatability > 0.8:
            modifiers['speed'] = 1.05
        
        return modifiers


def find_best_pellet_for_creature(
    creature: Creature,
    available_pellets: List[Pellet],
    max_distance: Optional[float] = None
) -> Optional[Pellet]:
    """
    Find the best pellet for a creature to eat based on traits and preferences.
    
    Args:
        creature: The creature looking for food
        available_pellets: List of available pellets
        max_distance: Maximum distance to consider (None = any distance)
        
    Returns:
        Best pellet to eat, or None if no suitable pellet
    """
    if not available_pellets:
        return None
    
    interactions = CrossEntityInteractions()
    best_pellet = None
    best_score = 0.0
    
    for pellet in available_pellets:
        # Check avoidance
        if interactions.check_pellet_avoidance(creature, pellet):
            continue
        
        # Calculate preference
        preference = interactions.calculate_pellet_preference(creature, pellet)
        
        # Apply distance penalty if specified
        if max_distance is not None:
            # Would need creature and pellet positions to calculate
            # For now, just use preference
            pass
        
        if preference > best_score:
            best_score = preference
            best_pellet = pellet
    
    return best_pellet
