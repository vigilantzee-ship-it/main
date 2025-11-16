"""
Unit tests for PelletLifeHistory system.
"""

import unittest
import time
from src.models.pellet_history import (
    PelletLifeHistory,
    PelletLifeEvent,
    PelletEventType,
    CreatureTargetingStats
)


class TestPelletLifeEvent(unittest.TestCase):
    """Test cases for PelletLifeEvent."""
    
    def test_event_creation(self):
        """Test creating a pellet life event."""
        event = PelletLifeEvent(
            timestamp=time.time(),
            event_type=PelletEventType.SPAWN,
            description="Pellet spawned",
            location=(10.0, 20.0)
        )
        
        self.assertEqual(event.event_type, PelletEventType.SPAWN)
        self.assertEqual(event.description, "Pellet spawned")
        self.assertEqual(event.location, (10.0, 20.0))
    
    def test_serialization(self):
        """Test event serialization."""
        event = PelletLifeEvent(
            timestamp=time.time(),
            event_type=PelletEventType.EATEN,
            description="Eaten by creature",
            creature_id="creature123",
            context={'nutritional_value': 25.0}
        )
        
        data = event.to_dict()
        restored = PelletLifeEvent.from_dict(data)
        
        self.assertEqual(restored.event_type, event.event_type)
        self.assertEqual(restored.creature_id, event.creature_id)
        self.assertEqual(restored.context, event.context)


class TestCreatureTargetingStats(unittest.TestCase):
    """Test cases for CreatureTargetingStats."""
    
    def test_stats_creation(self):
        """Test creating creature targeting stats."""
        stats = CreatureTargetingStats(creature_id="creature123")
        
        self.assertEqual(stats.creature_id, "creature123")
        self.assertEqual(stats.times_targeted, 0)
        self.assertEqual(stats.times_avoided, 0)
    
    def test_serialization(self):
        """Test stats serialization."""
        stats = CreatureTargetingStats(
            creature_id="creature123",
            times_targeted=5,
            times_avoided=2,
            distance_traveled=100.5
        )
        
        data = stats.to_dict()
        restored = CreatureTargetingStats.from_dict(data)
        
        self.assertEqual(restored.creature_id, stats.creature_id)
        self.assertEqual(restored.times_targeted, stats.times_targeted)


class TestPelletLifeHistory(unittest.TestCase):
    """Test cases for PelletLifeHistory."""
    
    def test_history_initialization(self):
        """Test creating a pellet life history."""
        history = PelletLifeHistory(pellet_id="pellet123")
        
        self.assertEqual(history.pellet_id, "pellet123")
        self.assertIsNone(history.death_time)
        self.assertTrue(history.is_alive())
        self.assertEqual(len(history.events), 0)
    
    def test_record_spawn(self):
        """Test recording spawn event."""
        history = PelletLifeHistory(pellet_id="pellet123")
        history.record_spawn(location=(10.0, 20.0))
        
        self.assertEqual(len(history.events), 1)
        self.assertEqual(history.events[0].event_type, PelletEventType.SPAWN)
        self.assertEqual(history.spawn_location, (10.0, 20.0))
    
    def test_record_spawn_with_parent(self):
        """Test recording spawn from parent."""
        history = PelletLifeHistory(pellet_id="pellet123")
        history.record_spawn(parent_id="parent456")
        
        self.assertEqual(history.parent_id, "parent456")
        spawn_events = history.get_events_by_type(PelletEventType.SPAWN)
        self.assertEqual(len(spawn_events), 1)
    
    def test_record_reproduction(self):
        """Test recording reproduction event."""
        history = PelletLifeHistory(pellet_id="pellet123")
        
        history.record_reproduction(
            offspring_id="offspring456",
            location=(15.0, 25.0)
        )
        
        self.assertEqual(len(history.offspring_ids), 1)
        self.assertEqual(history.offspring_ids[0], "offspring456")
        self.assertEqual(history.times_reproduced, 1)
        
        repro_events = history.get_events_by_type(PelletEventType.REPRODUCE)
        self.assertEqual(len(repro_events), 1)
    
    def test_record_mutation(self):
        """Test recording mutation event."""
        history = PelletLifeHistory(pellet_id="pellet123")
        
        mutation_details = {
            'trait': 'nutritional_value',
            'old_value': 25.0,
            'new_value': 30.0
        }
        history.record_mutation(mutation_details)
        
        self.assertEqual(history.mutation_count, 1)
        mutation_events = history.get_events_by_type(PelletEventType.MUTATE)
        self.assertEqual(len(mutation_events), 1)
        self.assertEqual(mutation_events[0].context, mutation_details)
    
    def test_record_targeted(self):
        """Test recording targeting by creature."""
        history = PelletLifeHistory(pellet_id="pellet123")
        
        history.record_targeted(
            creature_id="creature456",
            location=(10.0, 20.0),
            distance=5.0
        )
        
        self.assertEqual(history.total_times_targeted, 1)
        self.assertIn("creature456", history.creature_targeting)
        
        stats = history.creature_targeting["creature456"]
        self.assertEqual(stats.times_targeted, 1)
        self.assertEqual(stats.distance_traveled, 5.0)
    
    def test_record_avoided(self):
        """Test recording avoidance by creature."""
        history = PelletLifeHistory(pellet_id="pellet123")
        
        history.record_avoided(
            creature_id="creature456",
            reason="toxicity too high"
        )
        
        self.assertEqual(history.total_times_avoided, 1)
        self.assertIn("creature456", history.creature_targeting)
        
        stats = history.creature_targeting["creature456"]
        self.assertEqual(stats.times_avoided, 1)
    
    def test_record_eaten(self):
        """Test recording being eaten."""
        history = PelletLifeHistory(pellet_id="pellet123")
        
        history.record_eaten(
            creature_id="creature456",
            creature_name="Hungry Creature",
            location=(10.0, 20.0),
            nutritional_value=25.0
        )
        
        self.assertIsNotNone(history.death_time)
        self.assertEqual(history.cause_of_death, "eaten")
        self.assertEqual(history.eaten_by, "creature456")
        self.assertFalse(history.is_alive())
        
        eaten_events = history.get_events_by_type(PelletEventType.EATEN)
        self.assertEqual(len(eaten_events), 1)
    
    def test_record_death(self):
        """Test recording natural death."""
        history = PelletLifeHistory(pellet_id="pellet123")
        
        history.record_death(cause="old age", location=(10.0, 20.0))
        
        self.assertIsNotNone(history.death_time)
        self.assertEqual(history.cause_of_death, "old age")
        self.assertFalse(history.is_alive())
    
    def test_get_lifetime(self):
        """Test lifetime calculation."""
        spawn_time = time.time()
        history = PelletLifeHistory(pellet_id="pellet123", spawn_time=spawn_time)
        
        # Wait a tiny bit
        time.sleep(0.01)
        
        lifetime = history.get_lifetime()
        self.assertGreater(lifetime, 0)
    
    def test_targeting_rate(self):
        """Test targeting rate calculation."""
        history = PelletLifeHistory(pellet_id="pellet123")
        
        # 3 targeted, 1 avoided
        for i in range(3):
            history.record_targeted(
                creature_id=f"creature{i}",
                distance=5.0
            )
        
        history.record_avoided(creature_id="creature3")
        
        targeting_rate = history.get_targeting_rate()
        self.assertEqual(targeting_rate, 0.75)  # 3 out of 4
    
    def test_targeting_rate_no_interactions(self):
        """Test targeting rate with no interactions."""
        history = PelletLifeHistory(pellet_id="pellet123")
        
        self.assertEqual(history.get_targeting_rate(), 0.0)
    
    def test_most_interested_creature(self):
        """Test finding most interested creature."""
        history = PelletLifeHistory(pellet_id="pellet123")
        
        # Creature1 targets 5 times
        for i in range(5):
            history.record_targeted(creature_id="creature1", distance=1.0)
        
        # Creature2 targets 2 times
        for i in range(2):
            history.record_targeted(creature_id="creature2", distance=1.0)
        
        most_interested = history.get_most_interested_creature()
        self.assertIsNotNone(most_interested)
        self.assertEqual(most_interested.creature_id, "creature1")
        self.assertEqual(most_interested.times_targeted, 5)
    
    def test_lineage_tracking(self):
        """Test lineage depth and descendant count."""
        # Create parent
        parent = PelletLifeHistory(pellet_id="parent123")
        parent.generation = 0
        
        # Create child
        child = PelletLifeHistory(pellet_id="child456")
        child.parent_id = "parent123"
        child.generation = 1
        
        # Parent reproduces
        parent.record_reproduction(offspring_id="child456")
        
        self.assertEqual(parent.get_lineage_depth(), 0)
        self.assertEqual(child.get_lineage_depth(), 1)
        self.assertEqual(parent.get_descendant_count(), 1)
    
    def test_multiple_targeting_by_same_creature(self):
        """Test multiple targeting events from same creature."""
        history = PelletLifeHistory(pellet_id="pellet123")
        
        # Same creature targets 3 times
        for i in range(3):
            history.record_targeted(
                creature_id="creature456",
                distance=2.0
            )
        
        stats = history.creature_targeting["creature456"]
        self.assertEqual(stats.times_targeted, 3)
        self.assertEqual(stats.distance_traveled, 6.0)
        self.assertIsNotNone(stats.first_targeting)
        self.assertIsNotNone(stats.last_targeting)
    
    def test_recent_events(self):
        """Test getting recent events."""
        history = PelletLifeHistory(pellet_id="pellet123")
        
        # Add multiple events
        history.record_spawn()
        history.record_reproduction(offspring_id="child1")
        history.record_targeted(creature_id="creature1", distance=1.0)
        
        recent = history.get_recent_events(count=2)
        self.assertEqual(len(recent), 2)
        # Most recent should be the targeting event
        self.assertEqual(recent[0].event_type, PelletEventType.TARGETED)
    
    def test_serialization(self):
        """Test pellet history serialization."""
        history = PelletLifeHistory(pellet_id="pellet123")
        
        history.record_spawn(location=(10.0, 20.0))
        history.record_reproduction(offspring_id="child456")
        history.record_targeted(creature_id="creature789", distance=3.0)
        
        data = history.to_dict()
        restored = PelletLifeHistory.from_dict(data)
        
        self.assertEqual(restored.pellet_id, history.pellet_id)
        self.assertEqual(len(restored.events), len(history.events))
        self.assertEqual(len(restored.offspring_ids), len(history.offspring_ids))
        self.assertEqual(restored.total_times_targeted, history.total_times_targeted)


if __name__ == '__main__':
    unittest.main()
