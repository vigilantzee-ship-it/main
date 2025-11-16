"""
Unit tests for InteractionTracker system.
"""

import unittest
import time
from src.models.interactions import (
    InteractionTracker,
    InteractionRecord,
    InteractionType,
    FoodCompetitionRecord,
    MatingRecord,
    PartnerStats
)


class TestInteractionRecord(unittest.TestCase):
    """Test cases for InteractionRecord."""
    
    def test_interaction_record_creation(self):
        """Test creating an interaction record."""
        interaction = InteractionRecord(
            timestamp=time.time(),
            interaction_type=InteractionType.FOOD_COMPETITION,
            initiator_id="creature123",
            target_id="pellet456",
            target_name="Food Pellet",
            success=True
        )
        
        self.assertEqual(interaction.initiator_id, "creature123")
        self.assertEqual(interaction.target_id, "pellet456")
        self.assertTrue(interaction.success)
        self.assertEqual(interaction.interaction_type, InteractionType.FOOD_COMPETITION)
    
    def test_serialization(self):
        """Test interaction record serialization."""
        interaction = InteractionRecord(
            timestamp=time.time(),
            interaction_type=InteractionType.MATING_SUCCESS,
            initiator_id="creature123",
            target_id="creature456",
            target_name="Partner",
            success=True,
            context={'offspring_id': 'offspring789'}
        )
        
        data = interaction.to_dict()
        restored = InteractionRecord.from_dict(data)
        
        self.assertEqual(restored.initiator_id, interaction.initiator_id)
        self.assertEqual(restored.interaction_type, interaction.interaction_type)
        self.assertEqual(restored.context, interaction.context)


class TestFoodCompetitionRecord(unittest.TestCase):
    """Test cases for FoodCompetitionRecord."""
    
    def test_food_competition_creation(self):
        """Test creating a food competition record."""
        competition = FoodCompetitionRecord(
            timestamp=time.time(),
            pellet_id="pellet123",
            competitors=["creature1", "creature2", "creature3"],
            winner_id="creature1"
        )
        
        self.assertEqual(competition.pellet_id, "pellet123")
        self.assertEqual(len(competition.competitors), 3)
        self.assertEqual(competition.winner_id, "creature1")
    
    def test_serialization(self):
        """Test food competition serialization."""
        competition = FoodCompetitionRecord(
            timestamp=time.time(),
            pellet_id="pellet123",
            competitors=["creature1", "creature2"],
            winner_id="creature1"
        )
        
        data = competition.to_dict()
        restored = FoodCompetitionRecord.from_dict(data)
        
        self.assertEqual(restored.pellet_id, competition.pellet_id)
        self.assertEqual(restored.competitors, competition.competitors)


class TestMatingRecord(unittest.TestCase):
    """Test cases for MatingRecord."""
    
    def test_mating_record_creation(self):
        """Test creating a mating record."""
        mating = MatingRecord(
            timestamp=time.time(),
            partner_id="partner123",
            partner_name="Mate",
            success=True,
            offspring_id="offspring456",
            offspring_name="Baby"
        )
        
        self.assertEqual(mating.partner_id, "partner123")
        self.assertTrue(mating.success)
        self.assertEqual(mating.offspring_id, "offspring456")
    
    def test_failed_mating(self):
        """Test recording a failed mating attempt."""
        mating = MatingRecord(
            timestamp=time.time(),
            partner_id="partner123",
            partner_name="Mate",
            success=False
        )
        
        self.assertFalse(mating.success)
        self.assertIsNone(mating.offspring_id)


class TestPartnerStats(unittest.TestCase):
    """Test cases for PartnerStats."""
    
    def test_partner_stats_creation(self):
        """Test creating partner stats."""
        stats = PartnerStats(
            partner_id="partner123",
            partner_name="Test Partner"
        )
        
        self.assertEqual(stats.partner_id, "partner123")
        self.assertEqual(stats.mating_attempts, 0)
        self.assertEqual(stats.food_competitions, 0)
    
    def test_mating_success_rate(self):
        """Test mating success rate calculation."""
        stats = PartnerStats(
            partner_id="partner123",
            partner_name="Test",
            mating_attempts=10,
            successful_matings=7
        )
        
        self.assertEqual(stats.mating_success_rate(), 0.7)
    
    def test_mating_success_rate_no_attempts(self):
        """Test mating success rate with no attempts."""
        stats = PartnerStats(
            partner_id="partner123",
            partner_name="Test"
        )
        
        self.assertEqual(stats.mating_success_rate(), 0.0)
    
    def test_competition_win_rate(self):
        """Test food competition win rate."""
        stats = PartnerStats(
            partner_id="partner123",
            partner_name="Test",
            food_competitions=8,
            competitions_won=5
        )
        
        self.assertEqual(stats.competition_win_rate(), 0.625)


class TestInteractionTracker(unittest.TestCase):
    """Test cases for InteractionTracker."""
    
    def test_tracker_initialization(self):
        """Test creating an interaction tracker."""
        tracker = InteractionTracker(
            creature_id="creature123",
            creature_name="Test Creature"
        )
        
        self.assertEqual(tracker.creature_id, "creature123")
        self.assertEqual(tracker.creature_name, "Test Creature")
        self.assertEqual(len(tracker.interactions), 0)
        self.assertEqual(tracker.total_food_competitions, 0)
    
    def test_record_general_interaction(self):
        """Test recording a general interaction."""
        tracker = InteractionTracker(
            creature_id="creature123",
            creature_name="Test"
        )
        
        tracker.record_interaction(
            interaction_type=InteractionType.FLEE,
            target_id="threat456",
            target_name="Dangerous Creature",
            success=True
        )
        
        self.assertEqual(len(tracker.interactions), 1)
        self.assertEqual(tracker.times_fled, 1)
    
    def test_record_food_competition(self):
        """Test recording food competition."""
        tracker = InteractionTracker(
            creature_id="creature123",
            creature_name="Test"
        )
        
        tracker.record_food_competition(
            pellet_id="pellet456",
            competitors=["creature123", "creature789"],
            winner_id="creature123"
        )
        
        self.assertEqual(len(tracker.food_competitions), 1)
        self.assertEqual(tracker.total_food_competitions, 1)
        self.assertEqual(tracker.food_competitions_won, 1)
    
    def test_record_food_competition_loss(self):
        """Test recording a lost food competition."""
        tracker = InteractionTracker(
            creature_id="creature123",
            creature_name="Test"
        )
        
        tracker.record_food_competition(
            pellet_id="pellet456",
            competitors=["creature123", "creature789"],
            winner_id="creature789"
        )
        
        self.assertEqual(tracker.total_food_competitions, 1)
        self.assertEqual(tracker.food_competitions_won, 0)
    
    def test_record_mating_success(self):
        """Test recording successful mating."""
        tracker = InteractionTracker(
            creature_id="creature123",
            creature_name="Test"
        )
        
        tracker.record_mating_attempt(
            partner_id="partner456",
            partner_name="Mate",
            success=True,
            offspring_id="offspring789",
            offspring_name="Baby"
        )
        
        self.assertEqual(len(tracker.mating_records), 1)
        self.assertEqual(tracker.total_mating_attempts, 1)
        self.assertEqual(tracker.successful_matings, 1)
    
    def test_record_mating_failure(self):
        """Test recording failed mating."""
        tracker = InteractionTracker(
            creature_id="creature123",
            creature_name="Test"
        )
        
        tracker.record_mating_attempt(
            partner_id="partner456",
            partner_name="Mate",
            success=False
        )
        
        self.assertEqual(tracker.total_mating_attempts, 1)
        self.assertEqual(tracker.successful_matings, 0)
    
    def test_partner_stats_tracking(self):
        """Test partner statistics tracking."""
        tracker = InteractionTracker(
            creature_id="creature123",
            creature_name="Test"
        )
        
        # Record multiple interactions with same partner
        for i in range(3):
            tracker.record_mating_attempt(
                partner_id="partner456",
                partner_name="Favorite Mate",
                success=(i % 2 == 0),  # Success on even iterations
                offspring_id=f"offspring{i}" if i % 2 == 0 else None,
                offspring_name=f"Baby{i}" if i % 2 == 0 else None
            )
        
        self.assertIn("partner456", tracker.partner_stats)
        stats = tracker.partner_stats["partner456"]
        self.assertEqual(stats.mating_attempts, 3)
        self.assertEqual(stats.successful_matings, 2)  # 0 and 2 succeeded
        self.assertEqual(stats.offspring_count, 2)
    
    def test_food_competition_win_rate(self):
        """Test food competition win rate calculation."""
        tracker = InteractionTracker(
            creature_id="creature123",
            creature_name="Test"
        )
        
        # Win 3 out of 5 competitions
        for i in range(5):
            tracker.record_food_competition(
                pellet_id=f"pellet{i}",
                competitors=["creature123", "creature789"],
                winner_id="creature123" if i < 3 else "creature789"
            )
        
        self.assertEqual(tracker.get_food_competition_win_rate(), 0.6)
    
    def test_mating_success_rate(self):
        """Test mating success rate calculation."""
        tracker = InteractionTracker(
            creature_id="creature123",
            creature_name="Test"
        )
        
        # 2 successes out of 5 attempts
        for i in range(5):
            tracker.record_mating_attempt(
                partner_id=f"partner{i}",
                partner_name=f"Mate{i}",
                success=(i < 2)
            )
        
        self.assertEqual(tracker.get_mating_success_rate(), 0.4)
    
    def test_most_frequent_partner(self):
        """Test finding most frequent partner."""
        tracker = InteractionTracker(
            creature_id="creature123",
            creature_name="Test"
        )
        
        # Partner 1: 2 matings
        for i in range(2):
            tracker.record_mating_attempt(
                partner_id="partner1",
                partner_name="First",
                success=True
            )
        
        # Partner 2: 5 competitions
        for i in range(5):
            tracker.record_food_competition(
                pellet_id=f"pellet{i}",
                competitors=["creature123", "partner2"],
                winner_id="creature123"
            )
        
        most_frequent = tracker.get_most_frequent_partner()
        self.assertIsNotNone(most_frequent)
        self.assertEqual(most_frequent.partner_id, "partner2")
    
    def test_get_interaction_summary(self):
        """Test getting interaction summary."""
        tracker = InteractionTracker(
            creature_id="creature123",
            creature_name="Test"
        )
        
        tracker.record_food_competition(
            pellet_id="pellet1",
            competitors=["creature123", "other"],
            winner_id="creature123"
        )
        
        tracker.record_mating_attempt(
            partner_id="partner1",
            partner_name="Mate",
            success=True
        )
        
        tracker.record_interaction(
            interaction_type=InteractionType.FLEE,
            target_id="threat",
            target_name="Danger",
            success=True
        )
        
        summary = tracker.get_interaction_summary()
        self.assertEqual(summary['food_competitions'], 1)
        self.assertEqual(summary['mating_attempts'], 1)
        self.assertEqual(summary['times_fled'], 1)
    
    def test_serialization(self):
        """Test interaction tracker serialization."""
        tracker = InteractionTracker(
            creature_id="creature123",
            creature_name="Test"
        )
        
        tracker.record_food_competition(
            pellet_id="pellet1",
            competitors=["creature123", "other"],
            winner_id="creature123"
        )
        
        data = tracker.to_dict()
        restored = InteractionTracker.from_dict(data)
        
        self.assertEqual(restored.creature_id, tracker.creature_id)
        self.assertEqual(restored.total_food_competitions, tracker.total_food_competitions)
        self.assertEqual(len(restored.food_competitions), len(tracker.food_competitions))


if __name__ == '__main__':
    unittest.main()
