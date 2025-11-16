"""
Trait Injection System - Manages procedural trait injection into gene pool.

This system decides when and how to introduce random traits based on:
- Breeding events (low chance of novel traits)
- Environmental pressure (population stress, starvation, toxins)
- Cosmic events (periodic random injection)
- Genetic diversity metrics (low diversity triggers new traits)
"""

from typing import Optional, List, Dict, Any, Callable
import random
import time
from dataclasses import dataclass, field

from ..models.trait import Trait
from ..models.trait_generator import TraitGenerator
from ..models.trait_analytics import TraitAnalytics
from ..models.creature import Creature


@dataclass
class InjectionConfig:
    """
    Configuration for trait injection system.
    
    Attributes:
        breeding_injection_rate: Chance of new trait during breeding (0.0-1.0)
        cosmic_event_interval: Generations between cosmic events
        cosmic_event_trait_count: Traits injected per cosmic event
        pressure_threshold: Population stress threshold for pressure events
        diversity_threshold: Genetic diversity threshold for intervention
        allow_negative_traits: Whether to allow potentially harmful traits
        injection_enabled: Master switch for trait injection
    """
    breeding_injection_rate: float = 0.02
    cosmic_event_interval: int = 10
    cosmic_event_trait_count: int = 3
    pressure_threshold: float = 0.3
    diversity_threshold: float = 0.4
    allow_negative_traits: bool = True
    injection_enabled: bool = True


class TraitInjectionSystem:
    """
    Manages injection of procedurally generated traits into the gene pool.
    
    Integrates with:
    - Breeding system (hook for breeding events)
    - Population system (track stress and diversity)
    - Analytics system (log all injections)
    - Genetics engine (ensure compatibility)
    """
    
    def __init__(
        self,
        config: Optional[InjectionConfig] = None,
        analytics: Optional[TraitAnalytics] = None,
        seed: Optional[int] = None
    ):
        """
        Initialize the trait injection system.
        
        Args:
            config: Injection configuration
            analytics: Analytics system for tracking
            seed: Random seed for reproducibility
        """
        self.config = config or InjectionConfig()
        self.analytics = analytics or TraitAnalytics()
        self.generator = TraitGenerator(seed=seed)
        
        # State tracking
        self.current_generation = 0
        self.last_cosmic_event = 0
        self.injection_history: List[Dict[str, Any]] = []
        
        # Event callbacks
        self.on_trait_injected: List[Callable[[Trait, str], None]] = []
    
    def should_inject_on_breeding(self) -> bool:
        """
        Determine if a new trait should be injected during breeding.
        
        Returns:
            True if injection should occur
        """
        if not self.config.injection_enabled:
            return False
        
        return random.random() < self.config.breeding_injection_rate
    
    def inject_breeding_trait(
        self,
        parent1: Creature,
        parent2: Creature,
        generation: int
    ) -> Optional[Trait]:
        """
        Inject a new trait during breeding event.
        
        Args:
            parent1: First parent
            parent2: Second parent
            generation: Current generation
            
        Returns:
            Newly injected trait or None
        """
        if not self.should_inject_on_breeding():
            return None
        
        # Generate creature trait
        trait = self.generator.generate_creature_trait(
            generation=generation,
            source_type='emergent'
        )
        
        # Record in analytics
        self.analytics.record_trait_discovery(
            trait_name=trait.name,
            generation=generation,
            source_type='emergent',
            rarity=trait.rarity,
            category=trait.trait_type
        )
        
        self.analytics.record_injection_event(
            trait_name=trait.name,
            generation=generation,
            injection_reason='breeding_mutation',
            affected_creatures=1,
            event_data={
                'parent1_id': parent1.name,
                'parent2_id': parent2.name
            }
        )
        
        # Log injection
        self._log_injection(trait, 'breeding', generation)
        
        # Trigger callbacks
        self._trigger_callbacks(trait, 'breeding')
        
        return trait
    
    def check_cosmic_event(self, generation: int) -> List[Trait]:
        """
        Check if a cosmic event should occur and inject traits.
        
        Args:
            generation: Current generation
            
        Returns:
            List of injected traits (empty if no event)
        """
        if not self.config.injection_enabled:
            return []
        
        # Check if interval has passed
        if generation - self.last_cosmic_event < self.config.cosmic_event_interval:
            return []
        
        # Cosmic event occurs!
        self.last_cosmic_event = generation
        injected_traits = []
        
        for _ in range(self.config.cosmic_event_trait_count):
            trait = self.generator.generate_creature_trait(
                generation=generation,
                source_type='cosmic'
            )
            
            injected_traits.append(trait)
            
            # Record in analytics
            self.analytics.record_trait_discovery(
                trait_name=trait.name,
                generation=generation,
                source_type='cosmic',
                rarity=trait.rarity,
                category=trait.trait_type
            )
            
            self.analytics.record_injection_event(
                trait_name=trait.name,
                generation=generation,
                injection_reason='cosmic_event',
                affected_creatures=0,  # Available to pool, not yet in creatures
                event_data={'event_generation': generation}
            )
            
            # Log injection
            self._log_injection(trait, 'cosmic', generation)
            
            # Trigger callbacks
            self._trigger_callbacks(trait, 'cosmic')
        
        return injected_traits
    
    def inject_pressure_response_trait(
        self,
        generation: int,
        pressure_type: str,
        population_affected: int = 1
    ) -> Optional[Trait]:
        """
        Inject a trait in response to environmental pressure.
        
        Args:
            generation: Current generation
            pressure_type: Type of pressure ('starvation', 'toxin', 'combat', 'overcrowding')
            population_affected: Number of creatures affected
            
        Returns:
            Adaptive trait or None
        """
        if not self.config.injection_enabled:
            return None
        
        # Generate trait appropriate to pressure type
        category = self._pressure_to_category(pressure_type)
        
        trait = self.generator.generate_trait(
            category=category,
            generation=generation,
            source_type='adaptive'
        )
        
        # Record in analytics
        self.analytics.record_trait_discovery(
            trait_name=trait.name,
            generation=generation,
            source_type='adaptive',
            rarity=trait.rarity,
            category=trait.trait_type
        )
        
        self.analytics.record_injection_event(
            trait_name=trait.name,
            generation=generation,
            injection_reason=f'pressure_{pressure_type}',
            affected_creatures=population_affected,
            event_data={
                'pressure_type': pressure_type,
                'severity': 'high'
            }
        )
        
        # Log injection
        self._log_injection(trait, f'pressure_{pressure_type}', generation)
        
        # Trigger callbacks
        self._trigger_callbacks(trait, 'pressure')
        
        return trait
    
    def inject_diversity_boost_traits(
        self,
        generation: int,
        trait_count: int = 2
    ) -> List[Trait]:
        """
        Inject traits to boost genetic diversity.
        
        Args:
            generation: Current generation
            trait_count: Number of traits to inject
            
        Returns:
            List of injected traits
        """
        if not self.config.injection_enabled:
            return []
        
        injected_traits = []
        
        for _ in range(trait_count):
            trait = self.generator.generate_creature_trait(
                generation=generation,
                source_type='diversity_intervention'
            )
            
            injected_traits.append(trait)
            
            # Record in analytics
            self.analytics.record_trait_discovery(
                trait_name=trait.name,
                generation=generation,
                source_type='diversity_intervention',
                rarity=trait.rarity,
                category=trait.trait_type
            )
            
            self.analytics.record_injection_event(
                trait_name=trait.name,
                generation=generation,
                injection_reason='low_diversity',
                affected_creatures=0,
                event_data={'diversity_boost': True}
            )
            
            # Log injection
            self._log_injection(trait, 'diversity', generation)
            
            # Trigger callbacks
            self._trigger_callbacks(trait, 'diversity')
        
        return injected_traits
    
    def evaluate_population_pressure(
        self,
        population_size: int,
        starvation_count: int,
        average_health: float,
        generation: int
    ) -> Optional[Trait]:
        """
        Evaluate population metrics and potentially inject adaptive trait.
        
        Args:
            population_size: Current population size
            starvation_count: Number of starving creatures
            average_health: Average health percentage
            generation: Current generation
            
        Returns:
            Adaptive trait if pressure is high, None otherwise
        """
        if population_size == 0:
            return None
        
        # Calculate pressure metrics
        starvation_rate = starvation_count / population_size
        
        # Check if pressure threshold met
        pressure_detected = False
        pressure_type = None
        
        if starvation_rate > self.config.pressure_threshold:
            pressure_detected = True
            pressure_type = 'starvation'
        elif average_health < self.config.pressure_threshold:
            pressure_detected = True
            pressure_type = 'combat'
        
        if pressure_detected and pressure_type:
            return self.inject_pressure_response_trait(
                generation=generation,
                pressure_type=pressure_type,
                population_affected=population_size
            )
        
        return None
    
    def evaluate_genetic_diversity(
        self,
        unique_trait_count: int,
        population_size: int,
        generation: int
    ) -> List[Trait]:
        """
        Evaluate genetic diversity and inject traits if needed.
        
        Args:
            unique_trait_count: Number of unique traits in population
            population_size: Current population size
            generation: Current generation
            
        Returns:
            List of diversity-boosting traits (empty if not needed)
        """
        if population_size == 0:
            return []
        
        # Calculate diversity metric
        diversity_ratio = unique_trait_count / max(population_size, 1)
        
        # If diversity too low, inject new traits
        if diversity_ratio < self.config.diversity_threshold:
            return self.inject_diversity_boost_traits(
                generation=generation,
                trait_count=2
            )
        
        return []
    
    def register_injection_callback(self, callback: Callable[[Trait, str], None]):
        """
        Register a callback for when traits are injected.
        
        Args:
            callback: Function to call with (trait, injection_reason)
        """
        self.on_trait_injected.append(callback)
    
    def _pressure_to_category(self, pressure_type: str) -> str:
        """
        Map pressure type to appropriate trait category.
        
        Args:
            pressure_type: Type of environmental pressure
            
        Returns:
            Trait category
        """
        mapping = {
            'starvation': 'metabolic',
            'toxin': 'ecological',
            'combat': 'defensive',
            'overcrowding': 'behavioral'
        }
        
        return mapping.get(pressure_type, 'ecological')
    
    def _log_injection(self, trait: Trait, reason: str, generation: int):
        """
        Log an injection event.
        
        Args:
            trait: Injected trait
            reason: Reason for injection
            generation: Generation number
        """
        log_entry = {
            'trait_name': trait.name,
            'trait_type': trait.trait_type,
            'rarity': trait.rarity,
            'reason': reason,
            'generation': generation,
            'timestamp': time.time()
        }
        
        self.injection_history.append(log_entry)
    
    def _trigger_callbacks(self, trait: Trait, reason: str):
        """
        Trigger registered callbacks.
        
        Args:
            trait: Injected trait
            reason: Injection reason
        """
        for callback in self.on_trait_injected:
            try:
                callback(trait, reason)
            except Exception as e:
                # Don't let callback errors break injection
                print(f"Warning: Injection callback failed: {e}")
    
    def get_injection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about trait injections.
        
        Returns:
            Statistics dictionary
        """
        reason_counts = {}
        category_counts = {}
        rarity_counts = {}
        
        for entry in self.injection_history:
            reason = entry['reason']
            category = entry['trait_type']
            rarity = entry['rarity']
            
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
            category_counts[category] = category_counts.get(category, 0) + 1
            rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1
        
        return {
            'total_injections': len(self.injection_history),
            'by_reason': reason_counts,
            'by_category': category_counts,
            'by_rarity': rarity_counts,
            'last_cosmic_event': self.last_cosmic_event,
            'unique_traits_generated': len(self.generator.trait_name_history)
        }
    
    def get_available_traits_pool(self) -> List[Trait]:
        """
        Get pool of all generated traits available for injection.
        
        Returns:
            List of available traits
        """
        return self.generator.get_generated_traits()
