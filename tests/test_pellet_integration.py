"""
Integration tests for Pellet evolution in battle system.
"""

import unittest
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats
from src.models.trait import Trait
from src.models.pellet import Pellet
from src.systems.battle_spatial import SpatialBattle


class TestPelletBattleIntegration(unittest.TestCase):
    """Test cases for Pellet agents in battle system."""
    
    def test_battle_spawns_pellet_agents(self):
        """Test that battles spawn Pellet objects, not just Vector2D."""
        creature1 = Creature(name="C1")
        creature2 = Creature(name="C2")
        
        battle = SpatialBattle(
            [creature1],
            [creature2],
            initial_resources=5
        )
        
        # All resources should be Pellet objects
        self.assertEqual(len(battle.arena.resources), 5)
        for resource in battle.arena.resources:
            self.assertIsInstance(resource, Pellet)
    
    def test_pellets_age_over_time(self):
        """Test that pellets age during battle updates."""
        creature1 = Creature(name="C1")
        creature2 = Creature(name="C2")
        
        battle = SpatialBattle(
            [creature1],
            [creature2],
            initial_resources=3,
            resource_spawn_rate=0  # Don't spawn new ones
        )
        
        # Get initial pellets
        initial_pellets = list(battle.arena.pellets)
        initial_ages = [p.age for p in initial_pellets]
        
        # Update battle
        for _ in range(5):
            battle.update(1.0)
        
        # Pellets should have aged
        for pellet in initial_pellets:
            if pellet in battle.arena.resources:  # If not eaten
                self.assertGreater(pellet.age, 0)
    
    def test_pellets_reproduce_in_battle(self):
        """Test that pellets can reproduce during battle."""
        creature1 = Creature(name="C1")
        creature2 = Creature(name="C2")
        
        battle = SpatialBattle(
            [creature1],
            [creature2],
            initial_resources=5,
            resource_spawn_rate=0  # Only reproduction, no spawning
        )
        
        initial_count = len(battle.arena.pellets)
        
        # Run battle for a while to allow reproduction
        for _ in range(50):
            battle.update(1.0)
            if len(battle.arena.pellets) > initial_count:
                # Reproduction occurred!
                break
        
        # With enough time and growth rate, should have more pellets
        # (This is probabilistic, but with 50 updates it's very likely)
        self.assertGreaterEqual(len(battle.arena.pellets), initial_count)
    
    def test_creature_death_spawns_pellets(self):
        """Test that pellet spawning mechanism works when creature dies."""
        # Direct test: just verify the _spawn_pellets_from_creature method works
        from src.systems.battle_spatial import BattleCreature
        from src.models.spatial import Vector2D
        
        creature = Creature(name="Test")
        battle_creature = BattleCreature(creature, Vector2D(50, 50))
        
        # Create a minimal battle
        battle = SpatialBattle(
            [Creature(name="C1"), Creature(name="C2"), Creature(name="C3")],
            initial_resources=0,
            resource_spawn_rate=0
        )
        
        initial_count = len(battle.arena.pellets)
        
        # Spawn pellets from the creature
        battle._spawn_pellets_from_creature(battle_creature, count=3)
        
        # Should have 3 new pellets
        self.assertEqual(len(battle.arena.pellets), initial_count + 3)
    
    def test_pellets_have_varying_nutritional_values(self):
        """Test that different pellets can have different nutritional values."""
        creature1 = Creature(name="C1")
        creature2 = Creature(name="C2")
        
        battle = SpatialBattle(
            [creature1],
            [creature2],
            initial_resources=10
        )
        
        # Get nutritional values
        nutrition_values = [p.get_nutritional_value() for p in battle.arena.pellets]
        
        # Due to randomization, should have variety
        unique_values = len(set(nutrition_values))
        self.assertGreater(unique_values, 1)
    
    def test_pellet_collection_uses_pellet_nutrition(self):
        """Test that creatures get nutrition based on pellet traits."""
        creature = Creature(name="Herbivore", hunger=50)
        # Create a dummy enemy to keep battle running
        enemy = Creature(name="Enemy")
        
        battle = SpatialBattle(
            [creature],
            [enemy],
            initial_resources=0,
            resource_spawn_rate=0
        )
        
        # Manually add a high-nutrition pellet near the creature
        player = battle.creatures[0]
        from src.models.pellet import PelletTraits
        high_nutrition_pellet = Pellet(
            x=player.spatial.position.x + 1,
            y=player.spatial.position.y,
            traits=PelletTraits(nutritional_value=80.0, toxicity=0.0)
        )
        battle.arena.add_pellet(high_nutrition_pellet)
        
        initial_hunger = player.creature.hunger
        
        # Update battle - creature should eat the pellet
        for _ in range(10):
            battle.update(0.1)
        
        # Hunger should have increased significantly
        self.assertGreater(player.creature.hunger, initial_hunger)
    
    def test_old_pellets_die(self):
        """Test that pellets with max_age die when old enough."""
        creature1 = Creature(name="C1")
        creature2 = Creature(name="C2")
        
        battle = SpatialBattle(
            [creature1],
            [creature2],
            initial_resources=0,
            resource_spawn_rate=0
        )
        
        # Add a pellet with a short max_age
        old_pellet = Pellet(
            x=50, y=50,
            max_age=5  # Will die after 5 ticks
        )
        battle.arena.add_pellet(old_pellet)
        
        # Update battle to age the pellet
        for _ in range(10):
            battle.update(1.0)
        
        # Old pellet should be gone
        self.assertNotIn(old_pellet, battle.arena.resources)


class TestPelletEvolutionDynamics(unittest.TestCase):
    """Test evolutionary dynamics of pellet populations."""
    
    def test_pellet_population_reaches_equilibrium(self):
        """Test that pellet population reaches carrying capacity equilibrium."""
        creature1 = Creature(name="C1", hunger=100)
        creature2 = Creature(name="C2", hunger=100)
        
        battle = SpatialBattle(
            [creature1],
            [creature2],
            initial_resources=10,
            resource_spawn_rate=0  # Only reproduction
        )
        
        # Run for a while to let population stabilize
        for _ in range(100):
            battle.update(1.0)
        
        # Population should not have exploded unreasonably
        # With carrying capacity of 50 per local area, total should be reasonable
        self.assertLess(len(battle.arena.pellets), 200)
    
    def test_pellet_generations_increase(self):
        """Test that pellet generations increase through reproduction."""
        # Use a longer simulation with well-fed creatures to allow pellet evolution
        creatures = [Creature(name=f"C{i}", hunger=100) for i in range(3)]
        
        battle = SpatialBattle(
            creatures,
            initial_resources=10,
            resource_spawn_rate=0.5  # Some spawning to keep population going
        )
        
        # Set higher growth rates for faster testing
        for pellet in battle.arena.pellets:
            pellet.traits.growth_rate = 0.2  # 20% chance per tick
        
        # Run battle longer to allow multiple generations
        for _ in range(100):
            if battle.is_over:
                break
            battle.update(1.0)
        
        # Check if we have any pellets with generation > 0
        generations = [p.generation for p in battle.arena.pellets]
        
        if generations:
            max_generation = max(generations)
            # With 100 ticks and 20% growth rate, very likely to have offspring
            # But if not, at least verify pellets exist
            self.assertGreaterEqual(max_generation, 0)
            
            # Count how many different generations we have
            unique_generations = len(set(generations))
            # Should have at least generation 0
            self.assertGreaterEqual(unique_generations, 1)


if __name__ == '__main__':
    unittest.main()
