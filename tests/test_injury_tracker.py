"""
Unit tests for InjuryTracker system.
"""

import unittest
import time
from src.models.injury_tracker import (
    InjuryTracker,
    InjuryRecord,
    AttackerStats,
    DamageType
)


class TestInjuryRecord(unittest.TestCase):
    """Test cases for InjuryRecord."""
    
    def test_injury_record_creation(self):
        """Test creating an injury record."""
        injury = InjuryRecord(
            timestamp=time.time(),
            attacker_id="attacker123",
            attacker_name="Evil Creature",
            damage_type=DamageType.PHYSICAL,
            damage_amount=25.0,
            health_before=100.0,
            health_after=75.0,
            was_critical=False
        )
        
        self.assertEqual(injury.attacker_id, "attacker123")
        self.assertEqual(injury.damage_amount, 25.0)
        self.assertFalse(injury.was_critical)
    
    def test_health_percentages(self):
        """Test health percentage calculations."""
        injury = InjuryRecord(
            timestamp=time.time(),
            attacker_id="attacker123",
            attacker_name="Test",
            damage_type=DamageType.PHYSICAL,
            damage_amount=50.0,
            health_before=100.0,
            health_after=50.0
        )
        
        self.assertEqual(injury.health_percentage_before(100.0), 100.0)
        self.assertEqual(injury.health_percentage_after(100.0), 50.0)
    
    def test_near_death_detection(self):
        """Test near-death experience detection."""
        injury = InjuryRecord(
            timestamp=time.time(),
            attacker_id="attacker123",
            attacker_name="Test",
            damage_type=DamageType.PHYSICAL,
            damage_amount=95.0,
            health_before=100.0,
            health_after=5.0
        )
        
        self.assertTrue(injury.was_near_death(100.0, 0.1))
        self.assertFalse(injury.was_near_death(100.0, 0.01))
    
    def test_serialization(self):
        """Test injury record serialization."""
        injury = InjuryRecord(
            timestamp=time.time(),
            attacker_id="attacker123",
            attacker_name="Test",
            damage_type=DamageType.PHYSICAL,
            damage_amount=25.0,
            health_before=100.0,
            health_after=75.0
        )
        
        data = injury.to_dict()
        restored = InjuryRecord.from_dict(data)
        
        self.assertEqual(restored.attacker_id, injury.attacker_id)
        self.assertEqual(restored.damage_amount, injury.damage_amount)
        self.assertEqual(restored.damage_type, injury.damage_type)


class TestAttackerStats(unittest.TestCase):
    """Test cases for AttackerStats."""
    
    def test_attacker_stats_creation(self):
        """Test creating attacker stats."""
        stats = AttackerStats(
            attacker_id="attacker123",
            attacker_name="Evil Creature"
        )
        
        self.assertEqual(stats.attacker_id, "attacker123")
        self.assertEqual(stats.total_damage, 0.0)
        self.assertEqual(stats.hit_count, 0)
    
    def test_average_damage_calculation(self):
        """Test average damage calculation."""
        stats = AttackerStats(
            attacker_id="attacker123",
            attacker_name="Test",
            total_damage=100.0,
            hit_count=4
        )
        
        self.assertEqual(stats.average_damage(), 25.0)
    
    def test_average_damage_no_hits(self):
        """Test average damage with no hits."""
        stats = AttackerStats(
            attacker_id="attacker123",
            attacker_name="Test"
        )
        
        self.assertEqual(stats.average_damage(), 0.0)


class TestInjuryTracker(unittest.TestCase):
    """Test cases for InjuryTracker."""
    
    def test_tracker_initialization(self):
        """Test creating an injury tracker."""
        tracker = InjuryTracker(creature_id="creature123", max_hp=100.0)
        
        self.assertEqual(tracker.creature_id, "creature123")
        self.assertEqual(tracker.max_hp, 100.0)
        self.assertEqual(len(tracker.injuries), 0)
        self.assertEqual(tracker.near_death_count, 0)
    
    def test_record_injury(self):
        """Test recording an injury."""
        tracker = InjuryTracker(creature_id="creature123", max_hp=100.0)
        
        tracker.record_injury(
            attacker_id="attacker123",
            attacker_name="Evil Creature",
            damage_type=DamageType.PHYSICAL,
            damage_amount=25.0,
            health_before=100.0,
            health_after=75.0,
            was_critical=False
        )
        
        self.assertEqual(len(tracker.injuries), 1)
        self.assertEqual(tracker.get_total_damage_received(), 25.0)
        self.assertEqual(tracker.damage_by_type[DamageType.PHYSICAL], 25.0)
    
    def test_critical_hit_tracking(self):
        """Test critical hit tracking."""
        tracker = InjuryTracker(creature_id="creature123", max_hp=100.0)
        
        tracker.record_injury(
            attacker_id="attacker123",
            attacker_name="Critical Hitter",
            damage_type=DamageType.PHYSICAL,
            damage_amount=50.0,
            health_before=100.0,
            health_after=50.0,
            was_critical=True
        )
        
        self.assertEqual(tracker.critical_hits_received, 1)
        criticals = tracker.get_critical_hits()
        self.assertEqual(len(criticals), 1)
        self.assertTrue(criticals[0].was_critical)
    
    def test_near_death_tracking(self):
        """Test near-death experience tracking."""
        tracker = InjuryTracker(creature_id="creature123", max_hp=100.0)
        
        tracker.record_injury(
            attacker_id="attacker123",
            attacker_name="Deadly Attacker",
            damage_type=DamageType.PHYSICAL,
            damage_amount=95.0,
            health_before=100.0,
            health_after=5.0
        )
        
        self.assertEqual(tracker.near_death_count, 1)
        near_deaths = tracker.get_near_death_injuries()
        self.assertEqual(len(near_deaths), 1)
    
    def test_attacker_stats_tracking(self):
        """Test attacker statistics tracking."""
        tracker = InjuryTracker(creature_id="creature123", max_hp=100.0)
        
        # Record multiple injuries from same attacker
        for i in range(3):
            tracker.record_injury(
                attacker_id="attacker123",
                attacker_name="Persistent Foe",
                damage_type=DamageType.PHYSICAL,
                damage_amount=10.0,
                health_before=100.0 - (i * 10.0),
                health_after=90.0 - (i * 10.0)
            )
        
        self.assertIn("attacker123", tracker.attacker_stats)
        stats = tracker.attacker_stats["attacker123"]
        self.assertEqual(stats.hit_count, 3)
        self.assertEqual(stats.total_damage, 30.0)
        self.assertEqual(stats.average_damage(), 10.0)
    
    def test_most_dangerous_attacker(self):
        """Test finding most dangerous attacker."""
        tracker = InjuryTracker(creature_id="creature123", max_hp=100.0)
        
        tracker.record_injury(
            attacker_id="attacker1",
            attacker_name="Weak",
            damage_type=DamageType.PHYSICAL,
            damage_amount=10.0,
            health_before=100.0,
            health_after=90.0
        )
        
        tracker.record_injury(
            attacker_id="attacker2",
            attacker_name="Strong",
            damage_type=DamageType.PHYSICAL,
            damage_amount=50.0,
            health_before=90.0,
            health_after=40.0
        )
        
        most_dangerous = tracker.get_most_dangerous_attacker()
        self.assertIsNotNone(most_dangerous)
        self.assertEqual(most_dangerous.attacker_id, "attacker2")
        self.assertEqual(most_dangerous.total_damage, 50.0)
    
    def test_starvation_tracking(self):
        """Test starvation damage tracking."""
        tracker = InjuryTracker(creature_id="creature123", max_hp=100.0)
        
        tracker.record_injury(
            attacker_id=None,
            attacker_name="Starvation",
            damage_type=DamageType.STARVATION,
            damage_amount=15.0,
            health_before=100.0,
            health_after=85.0
        )
        
        self.assertEqual(tracker.starvation_damage, 15.0)
        self.assertEqual(tracker.times_starved, 1)
        self.assertEqual(tracker.damage_by_type[DamageType.STARVATION], 15.0)
    
    def test_damage_breakdown(self):
        """Test damage breakdown by type."""
        tracker = InjuryTracker(creature_id="creature123", max_hp=100.0)
        
        tracker.record_injury(
            attacker_id="attacker1",
            attacker_name="Physical",
            damage_type=DamageType.PHYSICAL,
            damage_amount=50.0,
            health_before=100.0,
            health_after=50.0
        )
        
        tracker.record_injury(
            attacker_id="attacker2",
            attacker_name="Special",
            damage_type=DamageType.SPECIAL,
            damage_amount=30.0,
            health_before=50.0,
            health_after=20.0
        )
        
        breakdown = tracker.get_damage_breakdown()
        self.assertAlmostEqual(breakdown[DamageType.PHYSICAL.value], 62.5, places=1)  # 50/80
        self.assertAlmostEqual(breakdown[DamageType.SPECIAL.value], 37.5, places=1)  # 30/80
    
    def test_serialization(self):
        """Test injury tracker serialization."""
        tracker = InjuryTracker(creature_id="creature123", max_hp=100.0)
        
        tracker.record_injury(
            attacker_id="attacker123",
            attacker_name="Test",
            damage_type=DamageType.PHYSICAL,
            damage_amount=25.0,
            health_before=100.0,
            health_after=75.0
        )
        
        data = tracker.to_dict()
        restored = InjuryTracker.from_dict(data)
        
        self.assertEqual(restored.creature_id, tracker.creature_id)
        self.assertEqual(restored.max_hp, tracker.max_hp)
        self.assertEqual(len(restored.injuries), len(tracker.injuries))
        self.assertEqual(restored.get_total_damage_received(), tracker.get_total_damage_received())


if __name__ == '__main__':
    unittest.main()
