"""
Test cases for combat engagement fix - ensuring agents don't circle without attacking.
"""

import unittest
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats, StatGrowth
from src.models.ability import create_ability
from src.systems.battle_spatial import SpatialBattle, BattleCreature, BattleEventType
from src.models.spatial import Vector2D


class TestCombatEngagement(unittest.TestCase):
    """Test that creatures properly engage in combat when close."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create aggressive creature type
        warrior_type = CreatureType(
            name="Warrior",
            base_stats=Stats(max_hp=100, attack=20, defense=10, speed=12),
            stat_growth=StatGrowth(),
            type_tags=["fighter"]
        )
        
        # Create two warriors
        self.warrior1 = Creature(
            name="Warrior1",
            creature_type=warrior_type,
            level=5
        )
        self.warrior1.add_ability(create_ability('tackle'))
        
        self.warrior2 = Creature(
            name="Warrior2",
            creature_type=warrior_type,
            level=5
        )
        self.warrior2.add_ability(create_ability('tackle'))
    
    def test_creatures_attack_when_in_range(self):
        """Test that creatures attack when they get close enough."""
        # Create battle with two creatures placed close together
        battle = SpatialBattle(
            [self.warrior1, self.warrior2],
            arena_width=50.0,
            arena_height=50.0,
            random_seed=42
        )
        
        # Track attack events
        attack_events = []
        damage_events = []
        
        def event_callback(event):
            if event.event_type == BattleEventType.ABILITY_USE:
                attack_events.append(event)
            elif event.event_type == BattleEventType.DAMAGE_DEALT:
                damage_events.append(event)
        
        battle.add_event_callback(event_callback)
        
        # Simulate for a short time
        battle.simulate(duration=10.0, time_step=0.1)
        
        # Verify that attacks occurred
        self.assertGreater(len(attack_events), 0, 
                          "Creatures should have attacked each other")
        self.assertGreater(len(damage_events), 0,
                          "Damage should have been dealt")
    
    def test_combat_engagement_flag_set_when_close(self):
        """Test that combat_engaged flag is set when creatures are close."""
        # Create battle with creatures placed at specific positions
        battle = SpatialBattle(
            [self.warrior1, self.warrior2],
            arena_width=50.0,
            arena_height=50.0,
            random_seed=42
        )
        
        # Get battle creatures
        bc1 = battle.creatures[0]
        bc2 = battle.creatures[1]
        
        # Manually position them close to each other (within engagement range)
        bc1.spatial.position = Vector2D(25.0, 25.0)
        bc2.spatial.position = Vector2D(29.0, 25.0)  # 4 units apart
        
        # Set targets
        bc1.target = bc2
        bc2.target = bc1
        
        # Update once to trigger combat engagement check
        battle.update(0.1)
        
        # Check that combat engagement is set
        self.assertTrue(bc1.combat_engaged, 
                       "Creature should be combat engaged when close to target")
        self.assertTrue(bc2.combat_engaged,
                       "Creature should be combat engaged when close to target")
    
    def test_creatures_dont_separate_when_combat_engaged(self):
        """Test that separation forces are reduced during combat engagement."""
        # Create battle with creatures placed very close
        battle = SpatialBattle(
            [self.warrior1, self.warrior2],
            arena_width=50.0,
            arena_height=50.0,
            random_seed=42
        )
        
        bc1 = battle.creatures[0]
        bc2 = battle.creatures[1]
        
        # Position them close (within both engagement and separation range)
        bc1.spatial.position = Vector2D(25.0, 25.0)
        bc2.spatial.position = Vector2D(27.0, 25.0)  # 2 units apart
        
        # Set targets to trigger combat engagement
        bc1.target = bc2
        bc2.target = bc1
        
        # Record initial distance
        initial_distance = bc1.spatial.distance_to(bc2.spatial)
        
        # Update several times
        for _ in range(5):
            battle.update(0.1)
        
        # Check final distance - should not have increased significantly
        # (some variation is expected due to movement)
        final_distance = bc1.spatial.distance_to(bc2.spatial)
        
        # Distance shouldn't have increased much (allowing for attack movement)
        self.assertLess(final_distance, initial_distance + 2.0,
                       "Creatures shouldn't separate significantly when combat engaged")
    
    def test_melee_range_larger_than_separation_threshold(self):
        """Test that melee attack range is larger than separation force threshold."""
        from src.models.combat_config import CombatConfig
        
        config = CombatConfig()
        
        # Melee range should be larger than the separation force radius (2.5)
        # to allow attacks to trigger before separation pushes them apart
        self.assertGreater(config.base_attack_range_melee, 2.5,
                          "Melee attack range should be larger than separation threshold")
    
    def test_attacks_occur_within_timeout(self):
        """Test that attacks occur within a reasonable timeframe."""
        # Create battle with creatures close together
        battle = SpatialBattle(
            [self.warrior1, self.warrior2],
            arena_width=30.0,
            arena_height=30.0,
            random_seed=42
        )
        
        attack_count = 0
        first_attack_time = None
        
        def event_callback(event):
            nonlocal attack_count, first_attack_time
            if event.event_type == BattleEventType.ABILITY_USE:
                attack_count += 1
                if first_attack_time is None:
                    first_attack_time = battle.current_time
        
        battle.add_event_callback(event_callback)
        
        # Simulate battle
        battle.simulate(duration=5.0, time_step=0.1)
        
        # Attacks should occur within 5 seconds
        self.assertIsNotNone(first_attack_time, 
                            "First attack should occur within 5 seconds")
        self.assertLess(first_attack_time, 5.0,
                       "First attack should occur quickly")
        self.assertGreater(attack_count, 0,
                          "Multiple attacks should occur")
    
    def test_creatures_approach_and_attack(self):
        """Test full scenario: creatures approach each other and attack."""
        # Create battle with creatures at opposite ends
        battle = SpatialBattle(
            [self.warrior1, self.warrior2],
            arena_width=50.0,
            arena_height=50.0,
            random_seed=42
        )
        
        bc1 = battle.creatures[0]
        bc2 = battle.creatures[1]
        
        # Position them apart
        bc1.spatial.position = Vector2D(10.0, 25.0)
        bc2.spatial.position = Vector2D(40.0, 25.0)  # 30 units apart
        
        # Track events
        movement_occurred = False
        attacks_occurred = False
        
        def event_callback(event):
            nonlocal movement_occurred, attacks_occurred
            if event.event_type == BattleEventType.CREATURE_MOVE:
                movement_occurred = True
            elif event.event_type == BattleEventType.ABILITY_USE:
                attacks_occurred = True
        
        battle.add_event_callback(event_callback)
        
        # Simulate until creatures attack
        battle.simulate(duration=20.0, time_step=0.1)
        
        # Verify both movement and attacks occurred
        self.assertTrue(movement_occurred, "Creatures should move towards each other")
        self.assertTrue(attacks_occurred, "Creatures should attack after approaching")
        
        # Final distance should be within attack range
        final_distance = bc1.spatial.distance_to(bc2.spatial)
        from src.models.combat_config import CombatConfig
        config = CombatConfig()
        
        # Should be close (not necessarily within melee, but should have engaged)
        self.assertLess(final_distance, config.max_chase_distance,
                       "Creatures should have closed distance significantly")


if __name__ == '__main__':
    unittest.main()
