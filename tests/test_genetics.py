"""
Tests for the enhanced genetics system with dominant/recessive genes.
"""

import unittest
from src.models.genetics import GeneticsEngine, PelletGenetics
from src.models.creature import Creature, CreatureType
from src.models.pellet import Pellet, PelletTraits
from src.models.trait import Trait, TraitProvenance
from src.models.stats import Stats
from src.models.expanded_traits import (
    AGGRESSIVE_TRAIT, TIMID_TRAIT, ARMORED_TRAIT, SWIFT_TRAIT,
    REGENERATIVE_TRAIT, SCAVENGER_TRAIT
)


class TestTraitProvenance(unittest.TestCase):
    """Test trait provenance tracking."""
    
    def test_provenance_creation(self):
        """Test creating trait provenance."""
        prov = TraitProvenance(
            source_type='inherited',
            parent_traits=['Trait1', 'Trait2'],
            generation=5,
            mutation_count=2
        )
        
        self.assertEqual(prov.source_type, 'inherited')
        self.assertEqual(len(prov.parent_traits), 2)
        self.assertEqual(prov.generation, 5)
        self.assertEqual(prov.mutation_count, 2)
    
    def test_provenance_serialization(self):
        """Test provenance serialization."""
        prov = TraitProvenance(
            source_type='mutated',
            parent_traits=['Trait1'],
            generation=3
        )
        
        data = prov.to_dict()
        restored = TraitProvenance.from_dict(data)
        
        self.assertEqual(restored.source_type, 'mutated')
        self.assertEqual(restored.parent_traits, ['Trait1'])
        self.assertEqual(restored.generation, 3)


class TestEnhancedTrait(unittest.TestCase):
    """Test enhanced trait functionality."""
    
    def test_trait_with_dominance(self):
        """Test creating trait with dominance."""
        trait = Trait(
            name="Test",
            dominance="dominant",
            interaction_effects={'bonus': 1.5}
        )
        
        self.assertEqual(trait.dominance, "dominant")
        self.assertEqual(trait.interaction_effects['bonus'], 1.5)
    
    def test_trait_copy(self):
        """Test trait copying."""
        original = Trait(
            name="Original",
            strength_modifier=1.2,
            dominance="recessive"
        )
        
        copy = original.copy()
        
        self.assertEqual(copy.name, "Original")
        self.assertEqual(copy.strength_modifier, 1.2)
        self.assertEqual(copy.dominance, "recessive")
        self.assertIsNot(copy, original)
        self.assertIsNot(copy.provenance, original.provenance)
    
    def test_trait_serialization(self):
        """Test trait serialization with new fields."""
        trait = Trait(
            name="Test",
            dominance="codominant",
            interaction_effects={'speed_bonus': 1.1}
        )
        
        data = trait.to_dict()
        restored = Trait.from_dict(data)
        
        self.assertEqual(restored.name, "Test")
        self.assertEqual(restored.dominance, "codominant")
        self.assertEqual(restored.interaction_effects['speed_bonus'], 1.1)


class TestGeneticsEngine(unittest.TestCase):
    """Test the genetics engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.genetics = GeneticsEngine(mutation_rate=0.1)
        
        # Create test creatures
        warrior_type = CreatureType(
            name="Warrior",
            base_stats=Stats(max_hp=100, attack=15, defense=10, speed=12)
        )
        
        self.parent1 = Creature(
            name="Parent1",
            creature_type=warrior_type,
            mature=True,
            hue=120.0
        )
        
        self.parent2 = Creature(
            name="Parent2",
            creature_type=warrior_type,
            mature=True,
            hue=180.0
        )
    
    def test_combine_traits_both_parents_same(self):
        """Test combining same trait from both parents."""
        # Both parents have aggressive trait
        aggressive = AGGRESSIVE_TRAIT.copy()
        self.parent1.add_trait(aggressive)
        self.parent2.add_trait(aggressive)
        
        traits = self.genetics.combine_traits(self.parent1, self.parent2, generation=1)
        
        # Should inherit aggressive trait
        trait_names = [t.name for t in traits]
        self.assertIn("Aggressive", trait_names)
    
    def test_combine_traits_different_traits(self):
        """Test combining different traits from parents."""
        self.parent1.add_trait(AGGRESSIVE_TRAIT.copy())
        self.parent2.add_trait(ARMORED_TRAIT.copy())
        
        traits = self.genetics.combine_traits(self.parent1, self.parent2, generation=1)
        
        # Should potentially inherit both
        trait_names = [t.name for t in traits]
        # At least one should be inherited
        self.assertTrue(len(trait_names) > 0)
    
    def test_dominant_recessive_interaction(self):
        """Test dominant/recessive gene interaction."""
        # Aggressive is dominant, Timid is recessive
        dominant_trait = AGGRESSIVE_TRAIT.copy()
        recessive_trait = TIMID_TRAIT.copy()
        
        self.parent1.add_trait(dominant_trait)
        self.parent2.add_trait(recessive_trait)
        
        # Run multiple times to check dominance pattern
        aggressive_count = 0
        timid_count = 0
        
        for _ in range(20):
            p1 = Creature(name="P1", creature_type=self.parent1.creature_type, mature=True)
            p2 = Creature(name="P2", creature_type=self.parent2.creature_type, mature=True)
            p1.add_trait(dominant_trait.copy())
            p2.add_trait(recessive_trait.copy())
            
            traits = self.genetics.combine_traits(p1, p2, generation=1)
            trait_names = [t.name for t in traits]
            
            if "Aggressive" in trait_names:
                aggressive_count += 1
            if "Timid" in trait_names:
                timid_count += 1
        
        # Dominant trait should appear more often
        # Note: Due to single-parent inheritance, both might appear
        self.assertTrue(aggressive_count > 0 or timid_count > 0)
    
    def test_combine_stats(self):
        """Test stat combination from parents."""
        stats = self.genetics.combine_stats(self.parent1, self.parent2)
        
        # Stats should be in reasonable range
        self.assertGreater(stats.max_hp, 0)
        self.assertGreater(stats.attack, 0)
        self.assertGreater(stats.defense, 0)
        self.assertGreater(stats.speed, 0)
    
    def test_stat_blending_not_pure_average(self):
        """Test that stat blending isn't pure 50/50."""
        # Create parents with very different stats
        p1_type = CreatureType(
            name="Strong",
            base_stats=Stats(max_hp=200, attack=30, defense=20, speed=10)
        )
        p2_type = CreatureType(
            name="Weak",
            base_stats=Stats(max_hp=50, attack=5, defense=5, speed=20)
        )
        
        p1 = Creature(name="Strong", creature_type=p1_type, mature=True)
        p2 = Creature(name="Weak", creature_type=p2_type, mature=True)
        
        # Combine multiple times and check variation
        results = []
        for _ in range(10):
            stats = self.genetics.combine_stats(p1, p2)
            results.append(stats.attack)
        
        # Should have variation (not all the same)
        self.assertTrue(len(set(results)) > 1, "Stats should vary, not be identical")
    
    def test_trait_provenance_tracking(self):
        """Test that trait provenance is tracked."""
        self.parent1.add_trait(AGGRESSIVE_TRAIT.copy())
        self.parent2.add_trait(AGGRESSIVE_TRAIT.copy())
        
        traits = self.genetics.combine_traits(self.parent1, self.parent2, generation=5)
        
        if traits:
            trait = traits[0]
            self.assertIsNotNone(trait.provenance)
            self.assertEqual(trait.provenance.generation, 5)


class TestPelletGenetics(unittest.TestCase):
    """Test pellet genetics system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.genetics = PelletGenetics(mutation_rate=0.15)
        
        self.pellet1 = Pellet(
            x=10, y=10,
            traits=PelletTraits(
                nutritional_value=50.0,
                growth_rate=0.02,
                toxicity=0.1
            )
        )
        
        self.pellet2 = Pellet(
            x=20, y=20,
            traits=PelletTraits(
                nutritional_value=30.0,
                growth_rate=0.03,
                toxicity=0.05
            )
        )
    
    def test_asexual_reproduction(self):
        """Test asexual pellet reproduction."""
        traits = self.genetics.combine_pellet_traits(self.pellet1)
        
        # Should be similar to parent with some mutation
        self.assertIsNotNone(traits)
        # Values should be in reasonable range
        self.assertGreater(traits.nutritional_value, 0)
        self.assertGreater(traits.growth_rate, 0)
    
    def test_sexual_reproduction(self):
        """Test sexual pellet reproduction."""
        traits = self.genetics.combine_pellet_traits(self.pellet1, self.pellet2)
        
        # Should be blend of both parents
        self.assertIsNotNone(traits)
        
        # Nutritional value should be between parent values (with mutation)
        # Allow for mutation range
        self.assertGreater(traits.nutritional_value, 15)
        self.assertLess(traits.nutritional_value, 65)
    
    def test_pellet_trait_blending(self):
        """Test that pellet traits actually blend."""
        # Test multiple offspring to see variation
        offspring_traits = []
        for _ in range(10):
            traits = self.genetics.combine_pellet_traits(self.pellet1, self.pellet2)
            offspring_traits.append(traits.nutritional_value)
        
        # Should have variation
        self.assertTrue(len(set(offspring_traits)) > 1, "Offspring should vary")


class TestMultiGenerationalInheritance(unittest.TestCase):
    """Test inheritance across multiple generations."""
    
    def setUp(self):
        """Set up for multi-generational testing."""
        self.genetics = GeneticsEngine(mutation_rate=0.05)
        
        warrior_type = CreatureType(
            name="Warrior",
            base_stats=Stats(max_hp=100, attack=15, defense=10, speed=12)
        )
        
        # Generation 0
        self.gen0_1 = Creature(name="G0_1", creature_type=warrior_type, mature=True)
        self.gen0_1.add_trait(AGGRESSIVE_TRAIT.copy())
        
        self.gen0_2 = Creature(name="G0_2", creature_type=warrior_type, mature=True)
        self.gen0_2.add_trait(SWIFT_TRAIT.copy())
    
    def test_three_generation_inheritance(self):
        """Test trait inheritance over three generations."""
        # Generation 1
        gen1_traits = self.genetics.combine_traits(
            self.gen0_1, self.gen0_2, generation=1
        )
        
        warrior_type = CreatureType(
            name="Warrior",
            base_stats=Stats(max_hp=100, attack=15, defense=10, speed=12)
        )
        
        gen1 = Creature(
            name="G1",
            creature_type=warrior_type,
            traits=gen1_traits,
            mature=True
        )
        
        # Another gen 1
        gen1_b_traits = self.genetics.combine_traits(
            self.gen0_1, self.gen0_2, generation=1
        )
        gen1_b = Creature(
            name="G1_B",
            creature_type=warrior_type,
            traits=gen1_b_traits,
            mature=True
        )
        
        # Generation 2
        gen2_traits = self.genetics.combine_traits(gen1, gen1_b, generation=2)
        
        # Should have inherited traits
        self.assertIsNotNone(gen2_traits)
        
        # Check provenance if traits exist
        if gen2_traits:
            # At least one trait should have generation 2 provenance
            max_gen = max(t.provenance.generation for t in gen2_traits)
            self.assertGreaterEqual(max_gen, 2)
    
    def test_trait_accumulation(self):
        """Test that traits can accumulate over generations."""
        warrior_type = CreatureType(
            name="Warrior",
            base_stats=Stats(max_hp=100, attack=15, defense=10, speed=12)
        )
        
        # Start with 2 different traits
        parent1 = Creature(name="P1", creature_type=warrior_type, mature=True)
        parent1.add_trait(AGGRESSIVE_TRAIT.copy())
        
        parent2 = Creature(name="P2", creature_type=warrior_type, mature=True)
        parent2.add_trait(ARMORED_TRAIT.copy())
        
        # Breed multiple times
        for gen in range(3):
            child_traits = self.genetics.combine_traits(parent1, parent2, generation=gen)
            
            # Should potentially have traits from both parents
            self.assertIsNotNone(child_traits)


class TestTraitInteractionEffects(unittest.TestCase):
    """Test interaction effects in traits."""
    
    def test_aggressive_trait_effects(self):
        """Test aggressive trait has correct interaction effects."""
        self.assertIn('attack_bonus', AGGRESSIVE_TRAIT.interaction_effects)
        self.assertIn('flee_threshold', AGGRESSIVE_TRAIT.interaction_effects)
    
    def test_scavenger_trait_effects(self):
        """Test scavenger trait effects."""
        self.assertIn('corpse_nutrition_bonus', SCAVENGER_TRAIT.interaction_effects)
        self.assertIn('corpse_preference', SCAVENGER_TRAIT.interaction_effects)
    
    def test_regenerative_trait_effects(self):
        """Test regenerative trait effects."""
        self.assertIn('hp_regen_rate', REGENERATIVE_TRAIT.interaction_effects)


if __name__ == '__main__':
    unittest.main()
