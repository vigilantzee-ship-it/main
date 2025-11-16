"""
Grass Growth Enhancement System

Implements interesting simulation-based grass (pellet) growth mechanics:
1. Pollination: Creatures spread pellet seeds as they move through grass
2. Nutrient zones: Areas where creatures died have higher growth rates
3. Growth pulses: Periodic environmental events boost growth (rain/sunshine)
4. Symbiotic bonus: Pellets near herbivore creatures grow faster

This system integrates with the existing pellet reproduction system to create
a more dynamic and interesting ecosystem without overpopulating the arena.
"""

from typing import List, Dict, Tuple, Optional, TYPE_CHECKING
import random
import time
import math

if TYPE_CHECKING:
    from ..models.pellet import Pellet
    from ..models.spatial import Vector2D
    from .battle_spatial import BattleCreature

from ..models.pellet import create_random_pellet


class NutrientZone:
    """Represents a nutrient-rich area where creatures have died."""
    
    def __init__(self, x: float, y: float, strength: float = 1.5, radius: float = 15.0):
        """
        Create a nutrient zone.
        
        Args:
            x: X position of zone center
            y: Y position of zone center
            strength: Growth rate multiplier (1.5 = 50% faster growth)
            radius: Effective radius of the zone
        """
        self.x = x
        self.y = y
        self.strength = strength
        self.radius = radius
        self.created_time = time.time()
        self.duration = 60.0  # Lasts 60 seconds
    
    def is_expired(self) -> bool:
        """Check if this zone has expired."""
        return (time.time() - self.created_time) > self.duration
    
    def get_growth_multiplier(self, pellet_x: float, pellet_y: float) -> float:
        """
        Get growth rate multiplier for a pellet at given position.
        
        Args:
            pellet_x: Pellet X position
            pellet_y: Pellet Y position
            
        Returns:
            Multiplier for growth rate (1.0 = no effect, >1.0 = faster growth)
        """
        dist_sq = (pellet_x - self.x) ** 2 + (pellet_y - self.y) ** 2
        radius_sq = self.radius ** 2
        
        if dist_sq > radius_sq:
            return 1.0
        
        # Linear falloff from center to edge
        dist = math.sqrt(dist_sq)
        falloff = 1.0 - (dist / self.radius)
        return 1.0 + (self.strength - 1.0) * falloff


class GrassGrowthSystem:
    """
    Manages enhanced grass (pellet) growth mechanics.
    
    Features:
    - Pollination: Creatures moving through grass spread seeds
    - Nutrient zones: Enhanced growth where creatures died
    - Growth pulses: Periodic environmental boosts
    - Symbiotic bonuses: Herbivores boost nearby grass growth
    """
    
    def __init__(
        self,
        arena_width: float,
        arena_height: float,
        enable_pollination: bool = True,
        enable_nutrient_zones: bool = True,
        enable_growth_pulses: bool = True,
        enable_symbiotic_bonus: bool = True
    ):
        """
        Initialize the grass growth system.
        
        Args:
            arena_width: Width of the arena
            arena_height: Height of the arena
            enable_pollination: Enable pollination mechanic
            enable_nutrient_zones: Enable nutrient zone mechanic
            enable_growth_pulses: Enable growth pulse events
            enable_symbiotic_bonus: Enable symbiotic growth bonuses
        """
        self.arena_width = arena_width
        self.arena_height = arena_height
        
        # Feature toggles
        self.enable_pollination = enable_pollination
        self.enable_nutrient_zones = enable_nutrient_zones
        self.enable_growth_pulses = enable_growth_pulses
        self.enable_symbiotic_bonus = enable_symbiotic_bonus
        
        # Nutrient zones from creature deaths
        self.nutrient_zones: List[NutrientZone] = []
        
        # Growth pulse state
        self.growth_pulse_active = False
        self.growth_pulse_end_time = 0.0
        self.growth_pulse_multiplier = 1.3  # 30% boost during pulse
        self.last_growth_pulse = time.time()
        self.growth_pulse_interval = 45.0  # Every 45 seconds
        self.growth_pulse_duration = 10.0  # Lasts 10 seconds
        
        # Pollination tracking - tracks which pellets creatures have visited
        # Key: creature_id, Value: set of pellet_ids
        self.creature_visited_pellets: Dict[str, set] = {}
        self.pollination_cooldown = 5.0  # Can pollinate once per 5 seconds per creature
        self.last_pollination: Dict[str, float] = {}
    
    def on_creature_death(
        self,
        x: float,
        y: float,
        creature_size: float = 1.0
    ) -> None:
        """
        Called when a creature dies. Creates a nutrient-rich zone.
        
        Args:
            x: X position where creature died
            y: Y position where creature died
            creature_size: Size of the creature (affects zone strength)
        """
        if not self.enable_nutrient_zones:
            return
        
        # Create nutrient zone
        strength = 1.3 + min(0.5, creature_size * 0.2)  # 1.3x to 1.8x boost
        radius = 12.0 + min(8.0, creature_size * 5.0)  # 12-20 unit radius
        
        zone = NutrientZone(x, y, strength=strength, radius=radius)
        self.nutrient_zones.append(zone)
    
    def update(self, delta_time: float) -> None:
        """
        Update growth system state.
        
        Args:
            delta_time: Time elapsed since last update
        """
        # Update growth pulse
        if self.enable_growth_pulses:
            current_time = time.time()
            
            # Check if pulse should end
            if self.growth_pulse_active and current_time > self.growth_pulse_end_time:
                self.growth_pulse_active = False
            
            # Check if new pulse should start
            if not self.growth_pulse_active:
                time_since_last = current_time - self.last_growth_pulse
                if time_since_last >= self.growth_pulse_interval:
                    self.growth_pulse_active = True
                    self.growth_pulse_end_time = current_time + self.growth_pulse_duration
                    self.last_growth_pulse = current_time
        
        # Clean up expired nutrient zones
        if self.enable_nutrient_zones:
            self.nutrient_zones = [z for z in self.nutrient_zones if not z.is_expired()]
    
    def get_growth_rate_multiplier(
        self,
        pellet: 'Pellet',
        nearby_creatures: Optional[List['BattleCreature']] = None
    ) -> float:
        """
        Calculate total growth rate multiplier for a pellet.
        
        Combines effects from:
        - Nutrient zones
        - Growth pulses
        - Symbiotic creatures nearby
        
        Args:
            pellet: The pellet to calculate multiplier for
            nearby_creatures: Creatures near the pellet (for symbiotic bonus)
            
        Returns:
            Multiplier for growth rate (1.0 = baseline, >1.0 = faster growth)
        """
        multiplier = 1.0
        
        # Nutrient zone effect
        if self.enable_nutrient_zones:
            for zone in self.nutrient_zones:
                zone_mult = zone.get_growth_multiplier(pellet.x, pellet.y)
                if zone_mult > multiplier:
                    multiplier = zone_mult
        
        # Growth pulse effect (stacks with nutrient zones)
        if self.enable_growth_pulses and self.growth_pulse_active:
            multiplier *= self.growth_pulse_multiplier
        
        # Symbiotic bonus (herbivores boost nearby grass)
        if self.enable_symbiotic_bonus and nearby_creatures:
            herbivore_count = 0
            for creature in nearby_creatures:
                # Check if creature is herbivore (has Forager trait or diet includes plants)
                if hasattr(creature.creature, 'traits'):
                    for trait in creature.creature.traits:
                        if 'Forager' in trait.name or 'Herbivore' in trait.name:
                            herbivore_count += 1
                            break
            
            if herbivore_count > 0:
                # Small bonus per nearby herbivore (max 20% boost from 2+ herbivores)
                bonus = min(0.2, herbivore_count * 0.12)
                multiplier *= (1.0 + bonus)
        
        return multiplier
    
    def try_pollination(
        self,
        creature: 'BattleCreature',
        pellet: 'Pellet',
        current_time: float
    ) -> Optional['Pellet']:
        """
        Attempt pollination - creature spreads seeds from pellet.
        
        When a creature moves near a pellet, it may carry pollen to create
        a new pellet nearby (simulating seed dispersal).
        
        Args:
            creature: The creature potentially pollinating
            pellet: The pellet being visited
            current_time: Current simulation time
            
        Returns:
            New pellet if pollination occurred, None otherwise
        """
        if not self.enable_pollination:
            return None
        
        creature_id = creature.creature.creature_id
        
        # Check cooldown
        last_poll = self.last_pollination.get(creature_id, 0.0)
        if current_time - last_poll < self.pollination_cooldown:
            return None
        
        # Track visited pellets
        if creature_id not in self.creature_visited_pellets:
            self.creature_visited_pellets[creature_id] = set()
        
        pellet_id = pellet.pellet_id
        
        # If creature has visited this pellet before, it might spread seeds
        if pellet_id in self.creature_visited_pellets[creature_id]:
            # 5% chance to pollinate when revisiting
            if random.random() < 0.05:
                # Create new pellet nearby (within creature's movement range)
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(5.0, 15.0)
                new_x = pellet.x + distance * math.cos(angle)
                new_y = pellet.y + distance * math.sin(angle)
                
                # Clamp to arena bounds
                new_x = max(0, min(self.arena_width, new_x))
                new_y = max(0, min(self.arena_height, new_y))
                
                # Create new pellet with similar traits to parent
                offspring = pellet.reproduce(mutation_rate=0.1)
                offspring.x = new_x
                offspring.y = new_y
                
                self.last_pollination[creature_id] = current_time
                return offspring
        else:
            # Mark this pellet as visited
            self.creature_visited_pellets[creature_id].add(pellet_id)
        
        return None
    
    def is_growth_pulse_active(self) -> bool:
        """Check if a growth pulse is currently active."""
        return self.growth_pulse_active
    
    def get_nutrient_zone_count(self) -> int:
        """Get the number of active nutrient zones."""
        return len(self.nutrient_zones)
