"""
Tests for the trait injection system.
"""

import unittest
from src.systems.trait_injection import (
    TraitInjectionSystem,
    InjectionConfig
)
from src.models.trait_analytics import TraitAnalytics
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats


class TestInjectionConfig(unittest.TestCase):
    """Test injection configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = InjectionConfig()
        
        self.assertEqual(config.breeding_injection_rate, 0.02)
        self.assertEqual(config.cosmic_event_interval, 10)
        self.assertTrue(config.injection_enabled)
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = InjectionConfig(
            breeding_injection_rate=0.05,
            cosmic_event_interval=5,
            allow_negative_traits=False
        )
        
        self.assertEqual(config.breeding_injection_rate, 0.05)
        self.assertEqual(config.cosmic_event_interval, 5)
        self.assertFalse(config.allow_negative_traits)


class TestTraitInjectionSystem(unittest.TestCase):
    """Test trait injection system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = InjectionConfig(
            breeding_injection_rate=0.5,  # High rate for testing
            cosmic_event_interval=5
        )
        self.analytics = TraitAnalytics()
        self.system = TraitInjectionSystem(
            config=self.config,
            analytics=self.analytics,
            seed=42
        )
        
        # Create test creatures
        creature_type = CreatureType(
            name="TestType",
            base_stats=Stats(max_hp=100, attack=10, defense=10, speed=10)
        )
        
        self.parent1 = Creature(
            name="Parent1",
            creature_type=creature_type,
            level=5
        )
        
        self.parent2 = Creature(
            name="Parent2",
            creature_type=creature_type,
            level=5
        )
    
    def test_system_initialization(self):
        """Test system initializes correctly."""
        self.assertIsNotNone(self.system)
        self.assertEqual(self.system.current_generation, 0)
        self.assertEqual(len(self.system.injection_history), 0)
    
    def test_should_inject_on_breeding(self):
        """Test breeding injection decision."""
        # With high injection rate, should often return True
        results = [self.system.should_inject_on_breeding() for _ in range(100)]
        true_count = sum(results)
        
        # Should inject in roughly 50% of cases
        self.assertGreater(true_count, 30)
        self.assertLess(true_count, 70)
    
    def test_inject_breeding_trait(self):
        """Test injecting trait during breeding."""
        trait = self.system.inject_breeding_trait(
            self.parent1,
            self.parent2,
            generation=5
        )
        
        if trait is not None:
            self.assertIsNotNone(trait.name)
            self.assertEqual(trait.provenance.generation, 5)
            self.assertEqual(trait.provenance.source_type, 'emergent')
            
            # Should be recorded in analytics
            self.assertIn(trait.name, self.analytics.discoveries)
    
    def test_cosmic_event_timing(self):
        """Test cosmic event timing."""
        # No event should occur initially
        traits1 = self.system.check_cosmic_event(generation=3)
        self.assertEqual(len(traits1), 0)
        
        # Event should occur after interval
        traits2 = self.system.check_cosmic_event(generation=5)
        self.assertEqual(len(traits2), self.config.cosmic_event_trait_count)
        
        # Should not occur again immediately
        traits3 = self.system.check_cosmic_event(generation=6)
        self.assertEqual(len(traits3), 0)
    
    def test_cosmic_event_injection(self):
        """Test cosmic event trait injection."""
        traits = self.system.check_cosmic_event(generation=10)
        
        self.assertEqual(len(traits), self.config.cosmic_event_trait_count)
        
        for trait in traits:
            self.assertEqual(trait.provenance.source_type, 'cosmic')
            self.assertIn(trait.name, self.analytics.discoveries)
    
    def test_pressure_response_injection(self):
        """Test pressure response trait injection."""
        trait = self.system.inject_pressure_response_trait(
            generation=5,
            pressure_type='starvation',
            population_affected=10
        )
        
        self.assertIsNotNone(trait)
        self.assertEqual(trait.provenance.source_type, 'adaptive')
        
        # Should be metabolic category for starvation
        self.assertEqual(trait.trait_type, 'metabolic')
    
    def test_pressure_type_mapping(self):
        """Test that pressure types map to correct categories."""
        # Starvation -> metabolic
        trait1 = self.system.inject_pressure_response_trait(
            generation=1,
            pressure_type='starvation'
        )
        self.assertEqual(trait1.trait_type, 'metabolic')
        
        # Toxin -> ecological
        trait2 = self.system.inject_pressure_response_trait(
            generation=1,
            pressure_type='toxin'
        )
        self.assertEqual(trait2.trait_type, 'ecological')
        
        # Combat -> defensive
        trait3 = self.system.inject_pressure_response_trait(
            generation=1,
            pressure_type='combat'
        )
        self.assertEqual(trait3.trait_type, 'defensive')
    
    def test_diversity_boost_injection(self):
        """Test diversity boost trait injection."""
        traits = self.system.inject_diversity_boost_traits(
            generation=8,
            trait_count=3
        )
        
        self.assertEqual(len(traits), 3)
        
        for trait in traits:
            self.assertEqual(trait.provenance.source_type, 'diversity_intervention')
            self.assertIn(trait.name, self.analytics.discoveries)
    
    def test_evaluate_population_pressure_starvation(self):
        """Test evaluation of starvation pressure."""
        # High starvation rate should trigger injection
        trait = self.system.evaluate_population_pressure(
            population_size=100,
            starvation_count=40,  # 40% starving
            average_health=0.8,
            generation=5
        )
        
        self.assertIsNotNone(trait)
        self.assertEqual(trait.trait_type, 'metabolic')
    
    def test_evaluate_population_pressure_combat(self):
        """Test evaluation of combat pressure."""
        # Low health should trigger injection
        trait = self.system.evaluate_population_pressure(
            population_size=100,
            starvation_count=5,
            average_health=0.2,  # Very low health
            generation=5
        )
        
        self.assertIsNotNone(trait)
        self.assertEqual(trait.trait_type, 'defensive')
    
    def test_evaluate_population_pressure_no_trigger(self):
        """Test no injection when pressure is low."""
        # Normal conditions shouldn't trigger
        trait = self.system.evaluate_population_pressure(
            population_size=100,
            starvation_count=5,
            average_health=0.8,
            generation=5
        )
        
        self.assertIsNone(trait)
    
    def test_evaluate_genetic_diversity_low(self):
        """Test diversity evaluation with low diversity."""
        # Low diversity should trigger injection
        traits = self.system.evaluate_genetic_diversity(
            unique_trait_count=10,
            population_size=100,  # Only 0.1 traits per creature
            generation=5
        )
        
        self.assertGreater(len(traits), 0)
    
    def test_evaluate_genetic_diversity_adequate(self):
        """Test diversity evaluation with adequate diversity."""
        # Adequate diversity shouldn't trigger
        traits = self.system.evaluate_genetic_diversity(
            unique_trait_count=50,
            population_size=100,
            generation=5
        )
        
        self.assertEqual(len(traits), 0)
    
    def test_injection_callback_registration(self):
        """Test registering injection callbacks."""
        callback_called = []
        
        def test_callback(trait, reason):
            callback_called.append((trait.name, reason))
        
        self.system.register_injection_callback(test_callback)
        
        # Trigger an injection
        trait = self.system.inject_pressure_response_trait(
            generation=1,
            pressure_type='starvation'
        )
        
        # Callback should have been called
        self.assertEqual(len(callback_called), 1)
        self.assertEqual(callback_called[0][0], trait.name)
        self.assertEqual(callback_called[0][1], 'pressure')
    
    def test_injection_disabled(self):
        """Test that injection can be disabled."""
        config = InjectionConfig(injection_enabled=False)
        system = TraitInjectionSystem(config=config)
        
        # No injections should occur
        self.assertFalse(system.should_inject_on_breeding())
        
        trait = system.inject_breeding_trait(
            self.parent1,
            self.parent2,
            generation=1
        )
        self.assertIsNone(trait)
        
        traits = system.check_cosmic_event(generation=10)
        self.assertEqual(len(traits), 0)
    
    def test_get_injection_stats(self):
        """Test getting injection statistics."""
        # Perform various injections
        self.system.inject_breeding_trait(self.parent1, self.parent2, 1)
        self.system.inject_pressure_response_trait(1, 'starvation')
        self.system.check_cosmic_event(generation=10)
        
        stats = self.system.get_injection_stats()
        
        self.assertIn('total_injections', stats)
        self.assertIn('by_reason', stats)
        self.assertIn('by_category', stats)
        self.assertIn('by_rarity', stats)
        
        # Should have multiple injections
        self.assertGreater(stats['total_injections'], 0)
    
    def test_get_available_traits_pool(self):
        """Test getting available traits pool."""
        # Generate some traits
        self.system.check_cosmic_event(generation=10)
        
        pool = self.system.get_available_traits_pool()
        
        self.assertIsInstance(pool, list)
        self.assertGreater(len(pool), 0)
    
    def test_injection_history_logging(self):
        """Test that injections are logged to history."""
        initial_count = len(self.system.injection_history)
        
        self.system.inject_pressure_response_trait(1, 'combat')
        
        self.assertEqual(len(self.system.injection_history), initial_count + 1)
        
        log_entry = self.system.injection_history[-1]
        self.assertIn('trait_name', log_entry)
        self.assertIn('reason', log_entry)
        self.assertIn('generation', log_entry)
    
    def test_analytics_integration(self):
        """Test that analytics are properly updated."""
        # Perform injection
        trait = self.system.inject_breeding_trait(
            self.parent1,
            self.parent2,
            generation=5
        )
        
        if trait:
            # Should be in discoveries
            self.assertIn(trait.name, self.analytics.discoveries)
            
            # Should have injection event
            self.assertGreater(len(self.analytics.injection_events), 0)
            
            # Should be in timeline
            timeline = self.analytics.get_trait_timeline()
            self.assertGreater(len(timeline), 0)


class TestInjectionSystemIntegration(unittest.TestCase):
    """Test integration scenarios."""
    
    def test_full_lifecycle(self):
        """Test full trait injection lifecycle."""
        analytics = TraitAnalytics()
        config = InjectionConfig(
            breeding_injection_rate=1.0,  # Always inject for testing
            cosmic_event_interval=5
        )
        system = TraitInjectionSystem(
            config=config,
            analytics=analytics,
            seed=123
        )
        
        creature_type = CreatureType(
            name="Test",
            base_stats=Stats(max_hp=100, attack=10, defense=10, speed=10)
        )
        parent1 = Creature(name="P1", creature_type=creature_type, level=5)
        parent2 = Creature(name="P2", creature_type=creature_type, level=5)
        
        # Breeding injection
        breeding_trait = system.inject_breeding_trait(parent1, parent2, 1)
        self.assertIsNotNone(breeding_trait)
        
        # Cosmic event
        cosmic_traits = system.check_cosmic_event(generation=5)
        self.assertGreater(len(cosmic_traits), 0)
        
        # Pressure response
        pressure_trait = system.inject_pressure_response_trait(5, 'starvation')
        self.assertIsNotNone(pressure_trait)
        
        # Check analytics
        self.assertGreater(analytics.total_discoveries, 0)
        self.assertGreater(analytics.total_injections, 0)
        
        # Check dashboard
        dashboard = analytics.get_dashboard_data()
        self.assertGreater(dashboard['statistics']['total_discoveries'], 0)


if __name__ == '__main__':
    unittest.main()
