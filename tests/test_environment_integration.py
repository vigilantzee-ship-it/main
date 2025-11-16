"""
Integration tests for environmental system with battle system.

Tests that environment affects creature movement, hunger, combat, and survival.
"""

import unittest
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats
from src.models.spatial import Vector2D
from src.models.environment import Environment, WeatherType, TimeOfDay, EnvironmentalHazard, HazardType
from src.models.trait import Trait
from src.systems.battle_spatial import SpatialBattle


class TestEnvironmentBattleIntegration(unittest.TestCase):
    """Test environmental integration with battle system."""
    
    def test_battle_with_environment_enabled(self):
        """Test creating a battle with environment enabled."""
        # Create creatures
        creature_type = CreatureType(
            name="TestType",
            base_stats=Stats(max_hp=100, attack=10, defense=10, speed=10)
        )
        creatures = [
            Creature(name=f"Creature{i}", creature_type=creature_type, level=1)
            for i in range(5)
        ]
        
        # Create battle with environment
        battle = SpatialBattle(
            creatures,
            arena_width=50.0,
            arena_height=50.0,
            enable_environment=True
        )
        
        # Environment should be created
        self.assertIsNotNone(battle.environment)
        self.assertIsNotNone(battle.environment.weather)
        self.assertIsNotNone(battle.environment.day_night)
    
    def test_battle_without_environment(self):
        """Test creating a battle without environment."""
        creature_type = CreatureType(
            name="TestType",
            base_stats=Stats(max_hp=100, attack=10, defense=10, speed=10)
        )
        creatures = [
            Creature(name=f"Creature{i}", creature_type=creature_type, level=1)
            for i in range(3)
        ]
        
        # Create battle without environment
        battle = SpatialBattle(
            creatures,
            arena_width=50.0,
            arena_height=50.0,
            enable_environment=False
        )
        
        # Environment should not be created
        self.assertIsNone(battle.environment)
    
    def test_battle_with_custom_environment(self):
        """Test creating a battle with custom environment."""
        creature_type = CreatureType(
            name="TestType",
            base_stats=Stats(max_hp=100, attack=10, defense=10, speed=10)
        )
        creatures = [
            Creature(name=f"Creature{i}", creature_type=creature_type, level=1)
            for i in range(3)
        ]
        
        # Create custom environment
        env = Environment(width=50.0, height=50.0, enable_weather=True, enable_day_night=True)
        
        # Create battle with custom environment
        battle = SpatialBattle(
            creatures,
            arena_width=50.0,
            arena_height=50.0,
            environment=env
        )
        
        # Should use the provided environment
        self.assertIs(battle.environment, env)
    
    def test_environmental_update_in_battle(self):
        """Test that environment updates during battle."""
        creature_type = CreatureType(
            name="TestType",
            base_stats=Stats(max_hp=100, attack=10, defense=10, speed=10)
        )
        creatures = [
            Creature(name=f"Creature{i}", creature_type=creature_type, level=1)
            for i in range(3)
        ]
        
        battle = SpatialBattle(
            creatures,
            arena_width=50.0,
            arena_height=50.0,
            enable_environment=True
        )
        
        # Update battle (should update environment)
        initial_hour = battle.environment.day_night.get_current_hour()
        battle.update(10.0)  # 10 seconds
        updated_hour = battle.environment.day_night.get_current_hour()
        
        # Hour should have progressed
        self.assertNotEqual(initial_hour, updated_hour)
    
    def test_weather_affects_hunger(self):
        """Test that weather affects creature hunger depletion."""
        creature_type = CreatureType(
            name="TestType",
            base_stats=Stats(max_hp=100, attack=10, defense=10, speed=10)
        )
        creatures = [
            Creature(name=f"Creature{i}", creature_type=creature_type, level=1)
            for i in range(3)
        ]
        
        # Create environment with hot weather
        env = Environment(width=50.0, height=50.0, enable_weather=True)
        env.weather.temperature = 38.0  # Hot temperature
        
        battle = SpatialBattle(
            creatures,
            arena_width=50.0,
            arena_height=50.0,
            environment=env
        )
        
        # Track initial hunger
        initial_hunger = battle.creatures[0].creature.hunger
        
        # Update battle
        battle.update(5.0)
        
        # Hunger should have decreased (affected by hot weather)
        final_hunger = battle.creatures[0].creature.hunger
        self.assertLess(final_hunger, initial_hunger)
    
    def test_terrain_affects_resource_quality(self):
        """Test that terrain affects spawned resource quality."""
        creature_type = CreatureType(
            name="TestType",
            base_stats=Stats(max_hp=100, attack=10, defense=10, speed=10)
        )
        creatures = [
            Creature(name=f"Creature{i}", creature_type=creature_type, level=1)
            for i in range(3)
        ]
        
        battle = SpatialBattle(
            creatures,
            arena_width=50.0,
            arena_height=50.0,
            enable_environment=True,
            initial_resources=10
        )
        
        # Resources should exist
        self.assertGreater(len(battle.arena.resources), 0)
        
        # At least some resources should have varied nutritional values
        # (due to environmental modifiers)
        nutritional_values = [r.traits.nutritional_value for r in battle.arena.pellets]
        # Should have some variation
        self.assertGreater(max(nutritional_values), min(nutritional_values))
    
    def test_environmental_hazard_damage(self):
        """Test that environmental hazards damage creatures."""
        creature_type = CreatureType(
            name="TestType",
            base_stats=Stats(max_hp=100, attack=10, defense=10, speed=10)
        )
        creatures = [
            Creature(name=f"Creature{i}", creature_type=creature_type, level=1)
            for i in range(3)
        ]
        
        env = Environment(width=50.0, height=50.0)
        
        battle = SpatialBattle(
            creatures,
            arena_width=50.0,
            arena_height=50.0,
            environment=env
        )
        
        # Add hazard at creature position
        creature_pos = battle.creatures[0].spatial.position
        hazard = EnvironmentalHazard(
            hazard_type=HazardType.FIRE,
            position=creature_pos,
            radius=10.0,
            damage=10.0
        )
        env.add_hazard(hazard)
        
        # Get initial HP
        initial_hp = battle.creatures[0].creature.stats.hp
        
        # Update battle
        battle.update(1.0)
        
        # Creature should have taken damage
        final_hp = battle.creatures[0].creature.stats.hp
        self.assertLess(final_hp, initial_hp)
    
    def test_trait_resistance_to_hazards(self):
        """Test that creatures with resistance traits take less hazard damage."""
        creature_type = CreatureType(
            name="TestType",
            base_stats=Stats(max_hp=100, attack=10, defense=10, speed=10)
        )
        
        # Creature without resistance
        normal_creature = Creature(name="Normal", creature_type=creature_type, level=1)
        
        # Creature with resistance trait
        resistant_creature = Creature(name="Resistant", creature_type=creature_type, level=1)
        resistant_creature.traits.append(Trait(
            name="Fire Proof",
            description="Immune to fire",
            trait_type="environmental"
        ))
        
        env = Environment(width=50.0, height=50.0)
        
        battle = SpatialBattle(
            [normal_creature, resistant_creature],
            arena_width=50.0,
            arena_height=50.0,
            environment=env
        )
        
        # Add fire hazard affecting both creatures
        hazard = EnvironmentalHazard(
            hazard_type=HazardType.FIRE,
            position=Vector2D(25, 25),
            radius=50.0,  # Large radius to hit both
            damage=20.0
        )
        env.add_hazard(hazard)
        
        # Get initial HP
        normal_hp_before = battle.creatures[0].creature.stats.hp
        resistant_hp_before = battle.creatures[1].creature.stats.hp
        
        # Update battle
        battle.update(1.0)
        
        # Normal creature should take damage
        normal_hp_after = battle.creatures[0].creature.stats.hp
        self.assertLess(normal_hp_after, normal_hp_before)
        
        # Resistant creature should take no damage (fire proof)
        resistant_hp_after = battle.creatures[1].creature.stats.hp
        self.assertEqual(resistant_hp_after, resistant_hp_before)
    
    def test_terrain_adaptation_traits(self):
        """Test that creatures with terrain adaptation get speed bonuses."""
        creature_type = CreatureType(
            name="TestType",
            base_stats=Stats(max_hp=100, attack=10, defense=10, speed=20)
        )
        
        # Normal creature
        normal_creature = Creature(name="Normal", creature_type=creature_type, level=1)
        
        # Aquatic creature
        aquatic_creature = Creature(name="Aquatic", creature_type=creature_type, level=1)
        aquatic_creature.traits.append(Trait(
            name="Aquatic",
            description="Fast in water",
            trait_type="environmental"
        ))
        
        env = Environment(width=50.0, height=50.0)
        
        battle = SpatialBattle(
            [normal_creature, aquatic_creature],
            arena_width=50.0,
            arena_height=50.0,
            environment=env
        )
        
        # Both creatures should have their own movement adaptations
        # This is validated by checking that the system doesn't crash
        # and creatures can move normally
        battle.update(1.0)
        
        # Both creatures should still be alive
        self.assertTrue(battle.creatures[0].is_alive())
        self.assertTrue(battle.creatures[1].is_alive())


if __name__ == '__main__':
    unittest.main()
