"""
Unit tests for Pellet system - evolving food agents with traits and lifecycle.
"""

import unittest
from src.models.pellet import Pellet, PelletTraits, create_random_pellet, create_pellet_from_creature
from src.models.spatial import Vector2D, Arena


class TestPelletTraits(unittest.TestCase):
    """Test cases for PelletTraits."""
    
    def test_default_traits(self):
        """Test that default traits are created properly."""
        traits = PelletTraits()
        self.assertEqual(traits.nutritional_value, 25.0)  # Updated from 40.0 to 25.0
        self.assertEqual(traits.growth_rate, 0.01)
        self.assertEqual(traits.spread_radius, 5)
        self.assertEqual(traits.size, 1.0)
        self.assertEqual(traits.toxicity, 0.0)
        self.assertEqual(traits.palatability, 0.5)
    
    def test_custom_traits(self):
        """Test creating traits with custom values."""
        traits = PelletTraits(
            nutritional_value=80.0,
            growth_rate=0.05,
            spread_radius=10,
            size=1.5,
            color=(255, 0, 0),
            toxicity=0.2,
            palatability=0.9
        )
        self.assertEqual(traits.nutritional_value, 80.0)
        self.assertEqual(traits.growth_rate, 0.05)
        self.assertEqual(traits.spread_radius, 10)
        self.assertEqual(traits.size, 1.5)
        self.assertEqual(traits.color, (255, 0, 0))
        self.assertEqual(traits.toxicity, 0.2)
        self.assertEqual(traits.palatability, 0.9)
    
    def test_trait_mutation(self):
        """Test that trait mutation creates variation."""
        original = PelletTraits(nutritional_value=50.0, growth_rate=0.02)
        
        # Mutate with high mutation rate to ensure changes
        mutated = original.mutate(mutation_rate=1.0)
        
        # Should be different objects
        self.assertIsNot(mutated, original)
        
        # Values should potentially differ (with mutation_rate=1.0, they likely will)
        # At minimum, it should create a valid PelletTraits object
        self.assertIsInstance(mutated, PelletTraits)
        self.assertGreaterEqual(mutated.nutritional_value, 10.0)
        self.assertLessEqual(mutated.nutritional_value, 100.0)
    
    def test_trait_mutation_preserves_bounds(self):
        """Test that mutation keeps values within valid ranges."""
        traits = PelletTraits(
            nutritional_value=10.0,  # At minimum
            growth_rate=0.1,  # At maximum
            toxicity=0.5  # At maximum
        )
        
        for _ in range(10):
            mutated = traits.mutate(mutation_rate=0.5)
            
            # Check all values are within bounds
            self.assertGreaterEqual(mutated.nutritional_value, 10.0)
            self.assertLessEqual(mutated.nutritional_value, 100.0)
            self.assertGreaterEqual(mutated.growth_rate, 0.001)
            self.assertLessEqual(mutated.growth_rate, 0.1)
            self.assertGreaterEqual(mutated.toxicity, 0.0)
            self.assertLessEqual(mutated.toxicity, 0.5)
    
    def test_trait_serialization(self):
        """Test trait serialization and deserialization."""
        original = PelletTraits(
            nutritional_value=75.0,
            growth_rate=0.03,
            color=(200, 150, 100)
        )
        
        data = original.to_dict()
        restored = PelletTraits.from_dict(data)
        
        self.assertEqual(restored.nutritional_value, 75.0)
        self.assertEqual(restored.growth_rate, 0.03)
        self.assertEqual(restored.color, (200, 150, 100))


class TestPellet(unittest.TestCase):
    """Test cases for Pellet agent."""
    
    def test_pellet_creation(self):
        """Test creating a basic pellet."""
        pellet = Pellet(x=10.0, y=20.0)
        
        self.assertEqual(pellet.x, 10.0)
        self.assertEqual(pellet.y, 20.0)
        self.assertEqual(pellet.age, 0)
        self.assertEqual(pellet.generation, 0)
        self.assertIsNotNone(pellet.pellet_id)
        self.assertIsInstance(pellet.traits, PelletTraits)
    
    def test_pellet_tick(self):
        """Test that pellet ages when ticked."""
        pellet = Pellet()
        self.assertEqual(pellet.age, 0)
        
        pellet.tick()
        self.assertEqual(pellet.age, 1)
        
        pellet.tick()
        self.assertEqual(pellet.age, 2)
    
    def test_pellet_reproduction(self):
        """Test pellet reproduction creates offspring."""
        parent = Pellet(x=50.0, y=50.0, traits=PelletTraits(spread_radius=10))
        
        offspring = parent.reproduce()
        
        # Offspring should exist
        self.assertIsNotNone(offspring)
        self.assertIsInstance(offspring, Pellet)
        
        # Should be a different pellet
        self.assertNotEqual(offspring.pellet_id, parent.pellet_id)
        
        # Should be near parent (within spread radius)
        distance = ((offspring.x - parent.x)**2 + (offspring.y - parent.y)**2)**0.5
        self.assertLessEqual(distance, parent.traits.spread_radius)
        
        # Should have parent_id set
        self.assertEqual(offspring.parent_id, parent.pellet_id)
        
        # Should be next generation
        self.assertEqual(offspring.generation, parent.generation + 1)
    
    def test_pellet_can_reproduce_with_low_density(self):
        """Test that pellets can reproduce when density is low."""
        pellet = Pellet(traits=PelletTraits(growth_rate=0.5))  # High growth rate
        
        # With very low density, should often be able to reproduce
        can_reproduce_count = sum(
            1 for _ in range(100) 
            if pellet.can_reproduce(local_pellet_count=1, carrying_capacity=100)
        )
        
        # With 50% growth rate and low density, should reproduce roughly 50% of the time
        self.assertGreater(can_reproduce_count, 30)  # At least 30%
        self.assertLess(can_reproduce_count, 70)  # At most 70%
    
    def test_pellet_cannot_reproduce_at_capacity(self):
        """Test that pellets cannot reproduce at carrying capacity."""
        pellet = Pellet(traits=PelletTraits(growth_rate=1.0))  # 100% growth rate
        
        # At carrying capacity, should never reproduce
        for _ in range(20):
            self.assertFalse(
                pellet.can_reproduce(local_pellet_count=100, carrying_capacity=100)
            )
    
    def test_pellet_death_from_age(self):
        """Test that pellets die when reaching max_age."""
        pellet = Pellet(max_age=10)
        
        self.assertFalse(pellet.is_dead())
        
        for _ in range(9):
            pellet.tick()
            self.assertFalse(pellet.is_dead())
        
        pellet.tick()  # Age 10
        self.assertTrue(pellet.is_dead())
    
    def test_pellet_immortal_without_max_age(self):
        """Test that pellets without max_age don't die naturally."""
        pellet = Pellet(max_age=None)
        
        for _ in range(1000):
            pellet.tick()
            self.assertFalse(pellet.is_dead())
    
    def test_pellet_nutritional_value(self):
        """Test that nutritional value accounts for toxicity."""
        # Non-toxic pellet
        pellet1 = Pellet(traits=PelletTraits(nutritional_value=100.0, toxicity=0.0))
        self.assertEqual(pellet1.get_nutritional_value(), 100.0)
        
        # 50% toxic pellet
        pellet2 = Pellet(traits=PelletTraits(nutritional_value=100.0, toxicity=0.5))
        self.assertEqual(pellet2.get_nutritional_value(), 50.0)
        
        # Fully toxic pellet
        pellet3 = Pellet(traits=PelletTraits(nutritional_value=100.0, toxicity=1.0))
        self.assertEqual(pellet3.get_nutritional_value(), 0.0)
    
    def test_pellet_palatability(self):
        """Test palatability score retrieval."""
        pellet = Pellet(traits=PelletTraits(palatability=0.8))
        self.assertEqual(pellet.get_palatability_score(), 0.8)
    
    def test_pellet_display_properties(self):
        """Test display properties for rendering."""
        traits = PelletTraits(color=(255, 128, 64), size=1.5)
        pellet = Pellet(traits=traits)
        
        self.assertEqual(pellet.get_display_color(), (255, 128, 64))
        self.assertEqual(pellet.get_display_size(), 1.5)
    
    def test_pellet_serialization(self):
        """Test pellet serialization and deserialization."""
        original = Pellet(
            x=25.0,
            y=35.0,
            traits=PelletTraits(nutritional_value=60.0),
            age=5,
            generation=2
        )
        
        data = original.to_dict()
        restored = Pellet.from_dict(data)
        
        self.assertEqual(restored.x, 25.0)
        self.assertEqual(restored.y, 35.0)
        self.assertEqual(restored.age, 5)
        self.assertEqual(restored.generation, 2)
        self.assertEqual(restored.traits.nutritional_value, 60.0)


class TestPelletCreation(unittest.TestCase):
    """Test cases for pellet factory functions."""
    
    def test_create_random_pellet(self):
        """Test creating random pellets."""
        pellet = create_random_pellet(x=10.0, y=20.0, generation=3)
        
        self.assertEqual(pellet.x, 10.0)
        self.assertEqual(pellet.y, 20.0)
        self.assertEqual(pellet.generation, 3)
        
        # Check traits are within expected ranges (updated to 15-35)
        self.assertGreaterEqual(pellet.traits.nutritional_value, 15.0)
        self.assertLessEqual(pellet.traits.nutritional_value, 35.0)
    
    def test_create_pellet_from_creature(self):
        """Test creating pellets from dead creatures."""
        pellet = create_pellet_from_creature(x=50.0, y=60.0, creature_nutritional_value=75.0)
        
        self.assertEqual(pellet.x, 50.0)
        self.assertEqual(pellet.y, 60.0)
        
        # Creature pellets should have high nutrition
        self.assertEqual(pellet.traits.nutritional_value, 75.0)
        
        # Should not reproduce (corpses don't reproduce)
        self.assertEqual(pellet.traits.growth_rate, 0.0)
        
        # Should have a max_age (corpses decay)
        self.assertIsNotNone(pellet.max_age)
        
        # Color should be reddish (meat color)
        self.assertEqual(pellet.traits.color, (200, 100, 100))


class TestPelletArenaIntegration(unittest.TestCase):
    """Test cases for Pellet integration with Arena."""
    
    def test_arena_supports_pellets(self):
        """Test that Arena can store Pellet objects."""
        arena = Arena(100, 100)
        pellet = Pellet(x=50, y=50)
        
        arena.add_pellet(pellet)
        
        self.assertEqual(len(arena.resources), 1)
        self.assertIn(pellet, arena.resources)
    
    def test_arena_pellets_property(self):
        """Test that Arena.pellets returns only Pellet objects."""
        arena = Arena(100, 100)
        
        # Add a Pellet
        pellet1 = Pellet(x=10, y=10)
        arena.add_pellet(pellet1)
        
        # Add a Vector2D (legacy resource)
        arena.add_resource(Vector2D(20, 20))
        
        # Add another Pellet
        pellet2 = Pellet(x=30, y=30)
        arena.add_pellet(pellet2)
        
        # Should have 3 total resources
        self.assertEqual(len(arena.resources), 3)
        
        # But only 2 pellets
        pellets = arena.pellets
        self.assertEqual(len(pellets), 2)
        self.assertIn(pellet1, pellets)
        self.assertIn(pellet2, pellets)
    
    def test_arena_get_resource_position(self):
        """Test getting position from both Vector2D and Pellet resources."""
        arena = Arena(100, 100)
        
        # Add Vector2D resource
        vec_resource = Vector2D(10, 20)
        arena.add_resource(vec_resource)
        
        # Add Pellet resource
        pellet_resource = Pellet(x=30, y=40)
        arena.add_pellet(pellet_resource)
        
        # Should be able to get position from both
        vec_pos = arena.get_resource_position(vec_resource)
        self.assertEqual(vec_pos.x, 10)
        self.assertEqual(vec_pos.y, 20)
        
        pellet_pos = arena.get_resource_position(pellet_resource)
        self.assertEqual(pellet_pos.x, 30)
        self.assertEqual(pellet_pos.y, 40)
    
    def test_arena_remove_resource(self):
        """Test removing resources from arena."""
        arena = Arena(100, 100)
        
        pellet = Pellet(x=50, y=50)
        arena.add_pellet(pellet)
        
        self.assertEqual(len(arena.resources), 1)
        
        removed = arena.remove_resource(pellet)
        self.assertTrue(removed)
        self.assertEqual(len(arena.resources), 0)
    
    def test_arena_get_nearest_resource_with_pellets(self):
        """Test finding nearest resource when using Pellets."""
        arena = Arena(100, 100)
        
        # Add pellets at different positions
        pellet1 = Pellet(x=10, y=10)
        pellet2 = Pellet(x=50, y=50)
        pellet3 = Pellet(x=90, y=90)
        
        arena.add_pellet(pellet1)
        arena.add_pellet(pellet2)
        arena.add_pellet(pellet3)
        
        # Find nearest to position (15, 15)
        query_pos = Vector2D(15, 15)
        nearest, distance = arena.get_nearest_resource(query_pos)
        
        # Should find pellet1 as nearest
        self.assertEqual(nearest, pellet1)
        self.assertAlmostEqual(distance, ((15-10)**2 + (15-10)**2)**0.5, places=2)


class TestPelletEvolution(unittest.TestCase):
    """Test cases for pellet evolution over generations."""
    
    def test_multi_generation_inheritance(self):
        """Test that traits are inherited across multiple generations."""
        # Create initial pellet with specific traits
        gen0 = Pellet(
            x=50, y=50,
            traits=PelletTraits(
                nutritional_value=50.0,
                growth_rate=0.05,
                palatability=0.6
            )
        )
        
        # Create several generations
        gen1 = gen0.reproduce(mutation_rate=0.1)
        gen2 = gen1.reproduce(mutation_rate=0.1)
        gen3 = gen2.reproduce(mutation_rate=0.1)
        
        # Check generation numbers
        self.assertEqual(gen0.generation, 0)
        self.assertEqual(gen1.generation, 1)
        self.assertEqual(gen2.generation, 2)
        self.assertEqual(gen3.generation, 3)
        
        # Traits should be similar but potentially mutated
        # With low mutation rate, values should still be in reasonable range
        for pellet in [gen1, gen2, gen3]:
            self.assertGreaterEqual(pellet.traits.nutritional_value, 10.0)
            self.assertLessEqual(pellet.traits.nutritional_value, 100.0)
    
    def test_density_based_population_control(self):
        """Test that carrying capacity limits population growth."""
        pellets = []
        
        # Create initial population
        for i in range(10):
            pellets.append(Pellet(
                x=i*10, y=i*10,
                traits=PelletTraits(growth_rate=0.5)
            ))
        
        carrying_capacity = 20
        
        # Simulate reproduction attempts
        for _ in range(5):
            new_pellets = []
            for pellet in pellets:
                if pellet.can_reproduce(len(pellets), carrying_capacity):
                    new_pellets.append(pellet.reproduce())
            pellets.extend(new_pellets)
        
        # Population should not exceed carrying capacity by much
        # (some overshoot is expected due to simultaneous reproduction)
        self.assertLessEqual(len(pellets), carrying_capacity * 1.5)


if __name__ == '__main__':
    unittest.main()
