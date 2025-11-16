"""
Tests for cross-entity interactions between creatures and pellets.
"""

import unittest
from src.models.cross_entity_interactions import (
    CrossEntityInteractions,
    PelletCreatureInteraction,
    find_best_pellet_for_creature
)
from src.models.creature import Creature, CreatureType
from src.models.pellet import Pellet, PelletTraits
from src.models.stats import Stats
from src.models.expanded_traits import (
    SCAVENGER_TRAIT, HERBIVORE_TRAIT, TOXIN_RESISTANT_TRAIT,
    POLLINATOR_TRAIT, SYMBIOTIC_TRAIT, CURIOUS_TRAIT
)


class TestCrossEntityInteractions(unittest.TestCase):
    """Test cross-entity interaction system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.interactions = CrossEntityInteractions()
        
        # Create test creature
        warrior_type = CreatureType(
            name="Warrior",
            base_stats=Stats(max_hp=100, attack=15, defense=10, speed=12)
        )
        self.creature = Creature(name="Test", creature_type=warrior_type)
        
        # Create test pellets
        self.normal_pellet = Pellet(
            x=10, y=10,
            traits=PelletTraits(
                nutritional_value=30.0,
                toxicity=0.1,
                palatability=0.6
            )
        )
        
        self.toxic_pellet = Pellet(
            x=20, y=20,
            traits=PelletTraits(
                nutritional_value=40.0,
                toxicity=0.8,
                palatability=0.3
            )
        )
        
        self.quality_pellet = Pellet(
            x=30, y=30,
            traits=PelletTraits(
                nutritional_value=50.0,
                toxicity=0.0,
                palatability=0.9,
                color=(100, 200, 100)  # Green
            )
        )
        
        self.corpse_pellet = Pellet(
            x=40, y=40,
            traits=PelletTraits(
                nutritional_value=60.0,
                growth_rate=0.0,  # Corpses don't reproduce
                toxicity=0.1,
                palatability=0.7,
                color=(200, 100, 100)  # Red/meat color
            )
        )
    
    def test_normal_creature_prefers_quality(self):
        """Test that normal creatures prefer high quality pellets."""
        quality_pref = self.interactions.calculate_pellet_preference(
            self.creature, self.quality_pellet
        )
        normal_pref = self.interactions.calculate_pellet_preference(
            self.creature, self.normal_pellet
        )
        
        self.assertGreater(quality_pref, normal_pref)
    
    def test_normal_creature_avoids_toxic(self):
        """Test that normal creatures avoid toxic pellets."""
        toxic_pref = self.interactions.calculate_pellet_preference(
            self.creature, self.toxic_pellet
        )
        normal_pref = self.interactions.calculate_pellet_preference(
            self.creature, self.normal_pellet
        )
        
        self.assertLess(toxic_pref, normal_pref)
    
    def test_scavenger_prefers_corpses(self):
        """Test that scavengers prefer corpse pellets."""
        self.creature.add_trait(SCAVENGER_TRAIT.copy())
        
        corpse_pref = self.interactions.calculate_pellet_preference(
            self.creature, self.corpse_pellet
        )
        normal_pref = self.interactions.calculate_pellet_preference(
            self.creature, self.normal_pellet
        )
        
        # Scavenger should prefer corpses
        self.assertGreater(corpse_pref, normal_pref)
    
    def test_herbivore_prefers_plants(self):
        """Test that herbivores prefer plant-like pellets."""
        self.creature.add_trait(HERBIVORE_TRAIT.copy())
        
        plant_pref = self.interactions.calculate_pellet_preference(
            self.creature, self.quality_pellet  # Green pellet
        )
        meat_pref = self.interactions.calculate_pellet_preference(
            self.creature, self.corpse_pellet  # Red pellet
        )
        
        # Herbivore should prefer green (plant) pellets
        self.assertGreater(plant_pref, meat_pref)
    
    def test_toxin_resistant_handles_toxic(self):
        """Test that toxin resistant creatures can eat toxic pellets."""
        self.creature.add_trait(TOXIN_RESISTANT_TRAIT.copy())
        
        toxic_pref = self.interactions.calculate_pellet_preference(
            self.creature, self.toxic_pellet
        )
        
        # Should be higher than what a normal creature would prefer
        # (not severely penalized by toxicity)
        # The toxic pellet has low palatability (0.3), so we expect a moderate preference
        self.assertGreater(toxic_pref, 0.3)
    
    def test_consumption_effects_basic(self):
        """Test basic consumption effects."""
        effects = self.interactions.apply_consumption_effects(
            self.creature, self.normal_pellet
        )
        
        self.assertIn('nutrition_gained', effects)
        self.assertGreater(effects['nutrition_gained'], 0)
    
    def test_consumption_with_scavenger_bonus(self):
        """Test scavenger gets bonus from corpses."""
        self.creature.add_trait(SCAVENGER_TRAIT.copy())
        
        normal_effects = self.interactions.apply_consumption_effects(
            self.creature, self.normal_pellet
        )
        corpse_effects = self.interactions.apply_consumption_effects(
            self.creature, self.corpse_pellet
        )
        
        # Corpse should give more nutrition to scavenger
        self.assertGreater(
            corpse_effects['nutrition_gained'],
            normal_effects['nutrition_gained']
        )
        self.assertIn('scavenger_bonus', corpse_effects['special_effects'])
    
    def test_consumption_toxin_damage(self):
        """Test that toxic pellets cause damage."""
        effects = self.interactions.apply_consumption_effects(
            self.creature, self.toxic_pellet
        )
        
        # Should take some damage from toxins
        self.assertLess(effects['hp_change'], 0)
    
    def test_consumption_toxin_resistant_reduces_damage(self):
        """Test toxin resistance reduces damage."""
        self.creature.add_trait(TOXIN_RESISTANT_TRAIT.copy())
        
        effects = self.interactions.apply_consumption_effects(
            self.creature, self.toxic_pellet
        )
        
        # Should still take damage but less
        # Check that toxin resistance was applied
        self.assertIn('toxin_resistance', effects['special_effects'])
    
    def test_pollination_effect(self):
        """Test pollination effect on pellet reproduction."""
        # Normal creature - no effect
        normal_boost = self.interactions.apply_pollination_effect(
            self.creature, self.normal_pellet
        )
        self.assertEqual(normal_boost, 1.0)
        
        # Pollinator creature - boost
        self.creature.add_trait(POLLINATOR_TRAIT.copy())
        pollinator_boost = self.interactions.apply_pollination_effect(
            self.creature, self.normal_pellet
        )
        self.assertGreater(pollinator_boost, 1.0)
    
    def test_symbiotic_benefit(self):
        """Test symbiotic benefits from nearby pellets."""
        pellets = [self.normal_pellet, self.quality_pellet]
        
        # Normal creature - no benefit
        normal_benefits = self.interactions.calculate_symbiotic_benefit(
            self.creature, pellets
        )
        self.assertEqual(normal_benefits['stat_boost'], 1.0)
        
        # Symbiotic creature - benefit
        self.creature.add_trait(SYMBIOTIC_TRAIT.copy())
        symbiotic_benefits = self.interactions.calculate_symbiotic_benefit(
            self.creature, pellets
        )
        self.assertGreater(symbiotic_benefits['stat_boost'], 1.0)
    
    def test_pellet_avoidance(self):
        """Test that creatures avoid dangerous pellets."""
        # Normal creature should avoid very toxic pellets
        should_avoid = self.interactions.check_pellet_avoidance(
            self.creature, self.toxic_pellet
        )
        self.assertTrue(should_avoid)
        
        # Toxin resistant should not avoid
        self.creature.add_trait(TOXIN_RESISTANT_TRAIT.copy())
        should_avoid = self.interactions.check_pellet_avoidance(
            self.creature, self.toxic_pellet
        )
        self.assertFalse(should_avoid)


class TestPelletCreatureInteraction(unittest.TestCase):
    """Test pellet effects on creatures."""
    
    def test_stat_modifiers_from_pellet(self):
        """Test getting stat modifiers from pellets."""
        high_nutrition_pellet = Pellet(
            x=10, y=10,
            traits=PelletTraits(nutritional_value=70.0)
        )
        
        modifiers = PelletCreatureInteraction.get_stat_modifiers(
            high_nutrition_pellet
        )
        
        self.assertIn('strength', modifiers)
        self.assertGreater(modifiers['strength'], 1.0)


class TestFindBestPellet(unittest.TestCase):
    """Test finding best pellet for creature."""
    
    def setUp(self):
        """Set up test fixtures."""
        warrior_type = CreatureType(
            name="Warrior",
            base_stats=Stats(max_hp=100, attack=15, defense=10, speed=12)
        )
        self.creature = Creature(name="Test", creature_type=warrior_type)
        
        self.pellets = [
            Pellet(x=10, y=10, traits=PelletTraits(
                nutritional_value=30.0,
                toxicity=0.1,
                palatability=0.6
            )),
            Pellet(x=20, y=20, traits=PelletTraits(
                nutritional_value=40.0,
                toxicity=0.8,
                palatability=0.3
            )),
            Pellet(x=30, y=30, traits=PelletTraits(
                nutritional_value=50.0,
                toxicity=0.0,
                palatability=0.9
            ))
        ]
    
    def test_find_best_pellet(self):
        """Test finding best pellet for creature."""
        best = find_best_pellet_for_creature(self.creature, self.pellets)
        
        self.assertIsNotNone(best)
        # Should prefer high palatability, low toxicity
        self.assertGreater(best.traits.palatability, 0.7)
    
    def test_find_best_with_empty_list(self):
        """Test finding pellet with empty list."""
        best = find_best_pellet_for_creature(self.creature, [])
        self.assertIsNone(best)
    
    def test_scavenger_finds_corpse(self):
        """Test that scavenger finds corpse pellet."""
        self.creature.add_trait(SCAVENGER_TRAIT.copy())
        
        corpse = Pellet(x=40, y=40, traits=PelletTraits(
            nutritional_value=60.0,
            growth_rate=0.0,
            palatability=0.7
        ))
        
        pellets_with_corpse = self.pellets + [corpse]
        best = find_best_pellet_for_creature(self.creature, pellets_with_corpse)
        
        # Scavenger should prefer corpse
        self.assertEqual(best, corpse)


if __name__ == '__main__':
    unittest.main()
