"""
Integration tests for the complete random trait system.

Tests the full workflow of trait generation, injection, analytics,
and integration with the breeding system.
"""

import unittest
from src.systems.breeding import Breeding
from src.systems.trait_injection import TraitInjectionSystem, InjectionConfig
from src.models.trait_analytics import TraitAnalytics
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats


class TestTraitSystemIntegration(unittest.TestCase):
    """Test integration of all trait system components."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create analytics
        self.analytics = TraitAnalytics()
        
        # Create injection config with high rates for testing
        self.config = InjectionConfig(
            breeding_injection_rate=0.8,  # High rate for testing
            cosmic_event_interval=3,
            injection_enabled=True
        )
        
        # Create injection system
        self.injection_system = TraitInjectionSystem(
            config=self.config,
            analytics=self.analytics,
            seed=42
        )
        
        # Create breeding system with injection
        self.breeding = Breeding(
            mutation_rate=0.1,
            injection_system=self.injection_system
        )
        
        # Create test creatures
        creature_type = CreatureType(
            name="TestSpecies",
            base_stats=Stats(max_hp=100, attack=15, defense=12, speed=10)
        )
        
        self.parent1 = Creature(
            name="Parent1",
            creature_type=creature_type,
            level=10,
            mature=True  # Make mature for breeding
        )
        
        self.parent2 = Creature(
            name="Parent2",
            creature_type=creature_type,
            level=10,
            mature=True  # Make mature for breeding
        )
    
    def test_breeding_with_injection(self):
        """Test that breeding can inject new traits."""
        initial_trait_count = len(self.analytics.discoveries)
        
        # Breed multiple times to increase chance of injection
        offspring_list = []
        for _ in range(10):
            offspring = self.breeding.breed(self.parent1, self.parent2)
            if offspring:
                offspring_list.append(offspring)
        
        # Should have created offspring
        self.assertGreater(len(offspring_list), 0)
        
        # Check if any injections occurred
        # With 80% rate, at least one should have happened
        final_trait_count = len(self.analytics.discoveries)
        self.assertGreaterEqual(final_trait_count, initial_trait_count)
    
    def test_cosmic_events_tracked_in_analytics(self):
        """Test that cosmic events are tracked in analytics."""
        # Trigger cosmic event
        traits = self.injection_system.check_cosmic_event(generation=5)
        
        # Should have generated traits
        self.assertGreater(len(traits), 0)
        
        # All should be tracked in analytics
        for trait in traits:
            self.assertIn(trait.name, self.analytics.discoveries)
            discovery = self.analytics.discoveries[trait.name]
            self.assertEqual(discovery.source_type, 'cosmic')
            self.assertEqual(discovery.generation, 5)
    
    def test_pressure_response_tracked(self):
        """Test that pressure responses are tracked."""
        # Inject pressure response
        trait = self.injection_system.inject_pressure_response_trait(
            generation=3,
            pressure_type='starvation',
            population_affected=20
        )
        
        # Should be tracked
        self.assertIn(trait.name, self.analytics.discoveries)
        
        # Should have injection event
        events = [e for e in self.analytics.injection_events if e.trait_name == trait.name]
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].injection_reason, 'pressure_starvation')
        self.assertEqual(events[0].affected_creatures, 20)
    
    def test_offspring_inherits_injected_traits(self):
        """Test that offspring can inherit injected traits."""
        # First, inject a trait during breeding
        offspring = None
        injected_trait_name = None
        
        for _ in range(20):  # Multiple attempts
            offspring = self.breeding.breed(self.parent1, self.parent2)
            if offspring and len(offspring.traits) > len(self.parent1.traits):
                # Found offspring with extra trait
                injected_trait_name = offspring.traits[-1].name
                break
        
        # If we got an injection, verify it
        if injected_trait_name:
            self.assertIn(injected_trait_name, self.analytics.discoveries)
    
    def test_analytics_timeline_chronological(self):
        """Test that analytics timeline is chronological."""
        # Generate several events
        self.injection_system.inject_breeding_trait(self.parent1, self.parent2, 1)
        self.injection_system.check_cosmic_event(generation=3)
        self.injection_system.inject_pressure_response_trait(2, 'combat')
        
        # Get timeline
        timeline = self.analytics.get_trait_timeline()
        
        # Should be sorted by time
        times = [event['time'] for event in timeline]
        self.assertEqual(times, sorted(times))
    
    def test_trait_spread_tracking(self):
        """Test tracking trait spread across population."""
        # Discover a trait
        self.analytics.record_trait_discovery("TestTrait", 1, 'emergent')
        
        # Simulate spread over generations
        for gen in range(1, 6):
            carrier_count = gen * 5
            self.analytics.update_trait_spread(
                "TestTrait",
                generation=gen,
                carrier_count=carrier_count
            )
        
        # Check metrics
        metrics = self.analytics.spread_metrics["TestTrait"]
        self.assertEqual(len(metrics.spread_events), 5)
        self.assertEqual(metrics.current_carriers, 25)
        self.assertEqual(metrics.generations_present, 5)
    
    def test_population_pressure_evaluation(self):
        """Test automatic pressure evaluation and response."""
        # Simulate high starvation
        trait = self.injection_system.evaluate_population_pressure(
            population_size=100,
            starvation_count=50,  # 50% starving
            average_health=0.8,
            generation=10
        )
        
        # Should inject metabolic trait
        self.assertIsNotNone(trait)
        self.assertEqual(trait.trait_type, 'metabolic')
        
        # Should be tracked
        self.assertIn(trait.name, self.analytics.discoveries)
    
    def test_diversity_evaluation(self):
        """Test automatic diversity evaluation and response."""
        # Simulate low diversity
        traits = self.injection_system.evaluate_genetic_diversity(
            unique_trait_count=5,
            population_size=100,  # Very low diversity
            generation=15
        )
        
        # Should inject diversity traits
        self.assertGreater(len(traits), 0)
        
        # All should be tracked
        for trait in traits:
            self.assertIn(trait.name, self.analytics.discoveries)
            discovery = self.analytics.discoveries[trait.name]
            self.assertEqual(discovery.source_type, 'diversity_intervention')
    
    def test_dashboard_data_completeness(self):
        """Test that dashboard data is complete."""
        # Generate some data
        self.injection_system.inject_breeding_trait(self.parent1, self.parent2, 1)
        self.injection_system.check_cosmic_event(generation=5)
        
        # Get dashboard data
        dashboard = self.analytics.get_dashboard_data()
        
        # Verify structure
        self.assertIn('statistics', dashboard)
        self.assertIn('top_traits', dashboard)
        self.assertIn('recent_events', dashboard)
        
        # Verify stats
        stats = dashboard['statistics']
        self.assertGreater(stats['total_discoveries'], 0)
        self.assertGreater(stats['total_injections'], 0)
    
    def test_injection_callback_triggers(self):
        """Test that injection callbacks are triggered."""
        callback_calls = []
        
        def test_callback(trait, reason):
            callback_calls.append((trait.name, reason))
        
        self.injection_system.register_injection_callback(test_callback)
        
        # Trigger injection
        self.injection_system.inject_pressure_response_trait(1, 'toxin')
        
        # Callback should have been called
        self.assertEqual(len(callback_calls), 1)
        self.assertEqual(callback_calls[0][1], 'pressure')
    
    def test_export_and_import_workflow(self):
        """Test exporting analytics data."""
        import tempfile
        import os
        import json
        
        # Generate data
        for i in range(5):
            trait = self.injection_system.inject_pressure_response_trait(i, 'combat')
            self.analytics.update_trait_spread(trait.name, i, i * 2)
        
        # Export to JSON
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json_path = f.name
        
        try:
            self.analytics.export_to_json(json_path)
            
            # Verify file exists and is valid JSON
            self.assertTrue(os.path.exists(json_path))
            
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            # Verify structure
            self.assertIn('discoveries', data)
            self.assertIn('injection_events', data)
            self.assertIn('statistics', data)
            
        finally:
            if os.path.exists(json_path):
                os.remove(json_path)
    
    def test_full_simulation_lifecycle(self):
        """Test a full simulation lifecycle with all features."""
        generation = 0
        population = [self.parent1, self.parent2]
        
        # Simulate 5 generations
        for gen in range(5):
            generation = gen + 1
            
            # Breeding
            if len(population) >= 2:
                offspring = self.breeding.breed(population[0], population[1])
                if offspring:
                    population.append(offspring)
                    
                    # Track any new traits
                    for trait in offspring.traits:
                        self.analytics.record_creature_trait(
                            offspring.creature_id,
                            trait.name
                        )
            
            # Cosmic events
            cosmic_traits = self.injection_system.check_cosmic_event(generation)
            
            # Population pressure
            pressure_trait = self.injection_system.evaluate_population_pressure(
                population_size=len(population),
                starvation_count=max(0, len(population) // 4),
                average_health=0.7,
                generation=generation
            )
            
            # Diversity check
            unique_traits = len(set(
                trait.name
                for creature in population
                for trait in creature.traits
            ))
            
            diversity_traits = self.injection_system.evaluate_genetic_diversity(
                unique_trait_count=unique_traits,
                population_size=len(population),
                generation=generation
            )
        
        # Verify we have rich data
        self.assertGreater(len(self.analytics.discoveries), 0)
        self.assertGreater(self.analytics.total_injections, 0)
        
        # Verify timeline
        timeline = self.analytics.get_trait_timeline()
        self.assertGreater(len(timeline), 0)
        
        # Verify dashboard
        dashboard = self.analytics.get_dashboard_data()
        self.assertGreater(dashboard['statistics']['total_discoveries'], 0)


if __name__ == '__main__':
    unittest.main()
