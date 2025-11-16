"""
Test cases for self-targeting bug fix.

Ensures that creatures cannot target themselves in spatial battles.
"""

import unittest
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats, StatGrowth
from src.models.spatial import Vector2D
from src.systems.battle_spatial import SpatialBattle, BattleCreature


class TestSelfTargeting(unittest.TestCase):
    """Test cases to ensure creatures never target themselves."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create test creature type
        warrior_type = CreatureType(
            name="Warrior",
            base_stats=Stats(max_hp=100, attack=15, defense=10, speed=12),
            stat_growth=StatGrowth(),
            type_tags=["fighter"]
        )
        
        self.creature1 = Creature(
            name="Fighter1",
            creature_type=warrior_type,
            level=5
        )
        self.creature2 = Creature(
            name="Fighter2",
            creature_type=warrior_type,
            level=5
        )
    
    def test_battle_creature_hash_and_equality(self):
        """Test that BattleCreature hash and equality work correctly."""
        pos1 = Vector2D(10, 10)
        pos2 = Vector2D(20, 20)
        
        bc1 = BattleCreature(self.creature1, pos1)
        bc1_duplicate = BattleCreature(self.creature1, pos2)  # Same creature, different position
        bc2 = BattleCreature(self.creature2, pos1)
        
        # Same creature should be equal regardless of position
        self.assertEqual(bc1, bc1_duplicate)
        self.assertEqual(hash(bc1), hash(bc1_duplicate))
        
        # Different creatures should not be equal
        self.assertNotEqual(bc1, bc2)
        
        # A creature should equal itself
        self.assertEqual(bc1, bc1)
        
        # Set operations should work correctly
        creature_set = {bc1}
        self.assertIn(bc1, creature_set)
        self.assertIn(bc1_duplicate, creature_set)  # Should be found even though different object
        self.assertNotIn(bc2, creature_set)
    
    def test_exclude_self_from_set(self):
        """Test that exclude parameter properly excludes self from spatial queries."""
        pos1 = Vector2D(10, 10)
        pos2 = Vector2D(15, 15)  # Close to pos1
        
        bc1 = BattleCreature(self.creature1, pos1)
        bc2 = BattleCreature(self.creature2, pos2)
        
        # Create a simple test - creature should be excluded when in exclude set
        exclude_set = {bc1}
        
        # Test set membership
        self.assertIn(bc1, exclude_set)
        self.assertNotIn(bc2, exclude_set)
    
    def test_creature_cannot_be_own_target(self):
        """Test that a creature cannot have itself as a target."""
        battle = SpatialBattle(
            [self.creature1, self.creature2],
            arena_width=50.0,
            arena_height=50.0
        )
        
        # Run battle for a few steps
        for _ in range(100):
            battle.update(0.1)
            
            # Check that no creature targets itself
            for bc in battle.creatures:
                if bc.target is not None:
                    self.assertNotEqual(bc, bc.target, 
                        f"Creature {bc.creature.name} is targeting itself!")
    
    def test_spatial_grid_excludes_self(self):
        """Test that spatial grid query excludes the querying creature."""
        battle = SpatialBattle(
            [self.creature1, self.creature2],
            arena_width=50.0,
            arena_height=50.0
        )
        
        # Get battle creatures
        bc1 = battle.creatures[0]
        bc2 = battle.creatures[1]
        
        # Query nearby creatures with self-exclusion
        nearby = battle.creature_grid.query_radius(
            bc1.spatial.position,
            radius=100.0,  # Large radius to get all creatures
            exclude={bc1}
        )
        
        # bc1 should not be in the results
        self.assertNotIn(bc1, nearby)
        # bc2 should be in the results (if alive)
        if bc2.is_alive():
            self.assertIn(bc2, nearby)
    
    def test_attack_self_check(self):
        """Test that _attempt_attack prevents self-attacks."""
        battle = SpatialBattle(
            [self.creature1],
            arena_width=50.0,
            arena_height=50.0
        )
        
        bc = battle.creatures[0]
        
        # Try to make the creature attack itself (should be prevented)
        initial_hp = bc.creature.stats.hp
        battle._attempt_attack(bc, bc)
        
        # HP should not have changed
        self.assertEqual(bc.creature.stats.hp, initial_hp)
    
    def test_get_enemies_excludes_self(self):
        """Test that _get_enemies excludes the creature itself."""
        battle = SpatialBattle(
            [self.creature1, self.creature2],
            arena_width=50.0,
            arena_height=50.0
        )
        
        bc1 = battle.creatures[0]
        
        # Get all creatures
        all_creatures = battle.creatures
        
        # Get enemies (should exclude self)
        enemies = battle._get_enemies(bc1, all_creatures, max_distance=1000.0)
        
        # bc1 should not be in enemies list
        self.assertNotIn(bc1, enemies)
    
    def test_get_allies_excludes_self(self):
        """Test that _get_allies excludes the creature itself."""
        battle = SpatialBattle(
            [self.creature1, self.creature2],
            arena_width=50.0,
            arena_height=50.0
        )
        
        bc1 = battle.creatures[0]
        
        # Get all creatures
        all_creatures = battle.creatures
        
        # Get allies (should exclude self)
        allies = battle._get_allies(bc1, all_creatures, max_distance=1000.0)
        
        # bc1 should not be in allies list
        self.assertNotIn(bc1, allies)
    
    def test_long_battle_no_self_targeting(self):
        """Run a longer battle simulation and ensure no self-targeting occurs."""
        # Create multiple creatures for more complex interactions
        creatures = []
        for i in range(5):
            warrior_type = CreatureType(
                name=f"Warrior{i}",
                base_stats=Stats(max_hp=100, attack=15, defense=10, speed=12),
                stat_growth=StatGrowth(),
                type_tags=["fighter"]
            )
            creatures.append(Creature(
                name=f"Fighter{i}",
                creature_type=warrior_type,
                level=5
            ))
        
        battle = SpatialBattle(
            creatures,
            arena_width=100.0,
            arena_height=100.0
        )
        
        # Run for many iterations
        for _ in range(500):
            if battle.is_over:
                break
            battle.update(0.1)
            
            # Check no self-targeting at each step
            for bc in battle.creatures:
                if bc.is_alive() and bc.target is not None:
                    self.assertNotEqual(bc, bc.target,
                        f"Step {_}: Creature {bc.creature.name} is targeting itself!")


if __name__ == '__main__':
    unittest.main()
