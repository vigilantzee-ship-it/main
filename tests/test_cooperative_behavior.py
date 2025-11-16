"""
Tests for cooperative behavior system and relationship metrics.
"""

import unittest
from src.models.relationship_metrics import (
    RelationshipMetrics,
    AgentTraits,
    AgentSocialState,
    SharedHistory,
    DecisionContext,
    CooperativeBehaviorSystem,
    create_family_bond,
    create_sibling_bond,
    create_pack_bond,
    update_metrics_after_cooperation
)
from src.models.creature import Creature
from src.models.relationships import RelationshipType


class TestRelationshipMetrics(unittest.TestCase):
    """Test RelationshipMetrics data class."""
    
    def test_initialization(self):
        """Test creating relationship metrics."""
        metrics = RelationshipMetrics(
            affinity=0.8,
            trust=0.7,
            kinship=0.5,
            rank=0.2
        )
        self.assertEqual(metrics.affinity, 0.8)
        self.assertEqual(metrics.trust, 0.7)
        self.assertEqual(metrics.kinship, 0.5)
        self.assertEqual(metrics.rank, 0.2)
    
    def test_bounds_validation(self):
        """Test that metrics are bounded correctly."""
        metrics = RelationshipMetrics(
            affinity=1.5,  # Over 1.0
            trust=-0.5,    # Under 0.0
            kinship=0.5,
            rank=2.0       # Over 1.0
        )
        self.assertEqual(metrics.affinity, 1.0)
        self.assertEqual(metrics.trust, 0.0)
        self.assertEqual(metrics.rank, 1.0)
    
    def test_cooperation_score(self):
        """Test cooperation score calculation."""
        metrics = RelationshipMetrics(
            affinity=0.8,
            trust=0.6,
            kinship=1.0,  # Family
            rank=0.0
        )
        score = metrics.get_cooperation_score()
        # Should be high for family with good affinity and trust
        self.assertGreater(score, 0.6)
    
    def test_decay(self):
        """Test metric decay over time."""
        metrics = RelationshipMetrics(
            affinity=0.8,
            trust=0.7,
            kinship=1.0,
            rank=0.5
        )
        initial_affinity = metrics.affinity
        initial_kinship = metrics.kinship
        
        metrics.decay(0.1)
        
        # Affinity and trust should decay
        self.assertLess(metrics.affinity, initial_affinity)
        # Kinship should not decay
        self.assertEqual(metrics.kinship, initial_kinship)
    
    def test_serialization(self):
        """Test serialization and deserialization."""
        metrics = RelationshipMetrics(
            affinity=0.8,
            trust=0.7,
            kinship=0.5,
            rank=0.2
        )
        data = metrics.to_dict()
        restored = RelationshipMetrics.from_dict(data)
        
        self.assertEqual(restored.affinity, metrics.affinity)
        self.assertEqual(restored.trust, metrics.trust)
        self.assertEqual(restored.kinship, metrics.kinship)
        self.assertEqual(restored.rank, metrics.rank)


class TestAgentTraits(unittest.TestCase):
    """Test AgentTraits data class."""
    
    def test_initialization(self):
        """Test creating agent traits."""
        traits = AgentTraits(
            altruism=0.8,
            dominance=0.3,
            cooperation=0.7,
            protectiveness=0.9,
            independence=0.2
        )
        self.assertEqual(traits.altruism, 0.8)
        self.assertEqual(traits.dominance, 0.3)
    
    def test_random_generation(self):
        """Test random trait generation."""
        traits = AgentTraits.random()
        self.assertGreaterEqual(traits.altruism, 0.0)
        self.assertLessEqual(traits.altruism, 1.0)
        self.assertGreaterEqual(traits.dominance, 0.0)
        self.assertLessEqual(traits.dominance, 1.0)
    
    def test_inheritance(self):
        """Test trait inheritance from parents."""
        parent1 = AgentTraits(altruism=0.8, dominance=0.2, cooperation=0.7, protectiveness=0.8, independence=0.3)
        parent2 = AgentTraits(altruism=0.6, dominance=0.6, cooperation=0.5, protectiveness=0.6, independence=0.5)
        
        child = AgentTraits.inherit(parent1, parent2, mutation_rate=0.0)
        
        # Without mutation, should be average of parents
        expected_altruism = (0.8 + 0.6) / 2
        self.assertAlmostEqual(child.altruism, expected_altruism, delta=0.01)
    
    def test_description(self):
        """Test trait description generation."""
        traits = AgentTraits(
            altruism=0.9,  # High altruism
            dominance=0.2,  # Low dominance (submissive)
            cooperation=0.8,  # High cooperation
            protectiveness=0.9,  # High protectiveness
            independence=0.1  # Low independence
        )
        desc = traits.get_description()
        self.assertIn("altruistic", desc)
        self.assertIn("submissive", desc)
        self.assertIn("cooperative", desc)
        self.assertIn("protective", desc)


class TestCooperativeBehaviorSystem(unittest.TestCase):
    """Test CooperativeBehaviorSystem."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.system = CooperativeBehaviorSystem()
    
    def test_food_sharing_high_kinship(self):
        """Test food sharing with family (high kinship)."""
        # Create context with high kinship (family)
        actor_traits = AgentTraits(altruism=0.8, dominance=0.5, cooperation=0.7, protectiveness=0.8, independence=0.3)
        target_traits = AgentTraits(altruism=0.5, dominance=0.5, cooperation=0.5, protectiveness=0.5, independence=0.5)
        metrics = RelationshipMetrics(affinity=0.9, trust=0.9, kinship=1.0, rank=0.0)
        
        actor_state = AgentSocialState(hunger_level=0.8, health_level=0.9)
        target_state = AgentSocialState(hunger_level=0.2, health_level=0.5)  # Target is hungry
        
        context = DecisionContext(
            actor_id="actor",
            target_id="target",
            actor_traits=actor_traits,
            target_traits=target_traits,
            metrics=metrics,
            actor_state=actor_state,
            target_state=target_state
        )
        
        should_share, amount = self.system.evaluate_food_sharing(context, 100.0)
        
        # Should share with starving family member
        self.assertTrue(should_share)
        self.assertGreater(amount, 0)
    
    def test_food_sharing_selfish(self):
        """Test that selfish creatures don't share."""
        # Create context with low altruism and no kinship
        actor_traits = AgentTraits(altruism=0.1, dominance=0.5, cooperation=0.3, protectiveness=0.2, independence=0.8)
        target_traits = AgentTraits(altruism=0.5, dominance=0.5, cooperation=0.5, protectiveness=0.5, independence=0.5)
        metrics = RelationshipMetrics(affinity=0.3, trust=0.3, kinship=0.0, rank=0.0)
        
        actor_state = AgentSocialState(hunger_level=0.5, health_level=0.9)
        target_state = AgentSocialState(hunger_level=0.3, health_level=0.5)
        
        context = DecisionContext(
            actor_id="actor",
            target_id="target",
            actor_traits=actor_traits,
            target_traits=target_traits,
            metrics=metrics,
            actor_state=actor_state,
            target_state=target_state
        )
        
        should_share, amount = self.system.evaluate_food_sharing(context, 100.0)
        
        # Selfish creature should not share
        self.assertFalse(should_share)
    
    def test_join_fight_family(self):
        """Test joining fight for family member."""
        # High cooperation and family bond
        actor_traits = AgentTraits(altruism=0.7, dominance=0.5, cooperation=0.8, protectiveness=0.9, independence=0.2)
        target_traits = AgentTraits(altruism=0.5, dominance=0.5, cooperation=0.5, protectiveness=0.5, independence=0.5)
        metrics = RelationshipMetrics(affinity=0.9, trust=0.9, kinship=1.0, rank=0.0)
        
        actor_state = AgentSocialState(hunger_level=0.7, health_level=0.8)
        target_state = AgentSocialState(hunger_level=0.5, health_level=0.4, in_combat=True, threatened=True)
        
        context = DecisionContext(
            actor_id="actor",
            target_id="target",
            actor_traits=actor_traits,
            target_traits=target_traits,
            metrics=metrics,
            actor_state=actor_state,
            target_state=target_state
        )
        
        should_join, commitment = self.system.evaluate_join_fight(context, threat_level=0.5)
        
        # Should join fight for family
        self.assertTrue(should_join)
        self.assertGreater(commitment, 0.5)
    
    def test_join_fight_independent(self):
        """Test that independent creatures don't join fights."""
        # High independence, low cooperation
        actor_traits = AgentTraits(altruism=0.3, dominance=0.5, cooperation=0.2, protectiveness=0.3, independence=0.9)
        target_traits = AgentTraits(altruism=0.5, dominance=0.5, cooperation=0.5, protectiveness=0.5, independence=0.5)
        metrics = RelationshipMetrics(affinity=0.4, trust=0.4, kinship=0.0, rank=0.0)
        
        actor_state = AgentSocialState(hunger_level=0.7, health_level=0.8)
        target_state = AgentSocialState(hunger_level=0.5, health_level=0.4, in_combat=True)
        
        context = DecisionContext(
            actor_id="actor",
            target_id="target",
            actor_traits=actor_traits,
            target_traits=target_traits,
            metrics=metrics,
            actor_state=actor_state,
            target_state=target_state
        )
        
        should_join, commitment = self.system.evaluate_join_fight(context, threat_level=0.6)
        
        # Independent creature should not join
        self.assertFalse(should_join)
    
    def test_group_combat_bonus(self):
        """Test group combat bonus calculation."""
        # Cooperative creature with allies
        traits = AgentTraits(altruism=0.7, dominance=0.5, cooperation=0.9, protectiveness=0.7, independence=0.2)
        
        bonus = self.system.calculate_group_combat_bonus(traits, allies_present=3, family_present=1)
        
        # Should get bonus from cooperation, allies, and family
        self.assertGreater(bonus, 1.0)
        
        # Solo fighter should get no bonus
        solo_bonus = self.system.calculate_group_combat_bonus(traits, allies_present=0, family_present=0)
        self.assertEqual(solo_bonus, 1.0)


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""
    
    def test_create_family_bond(self):
        """Test creating family bond metrics."""
        metrics = create_family_bond("parent", "child")
        self.assertEqual(metrics.kinship, 1.0)
        self.assertGreater(metrics.affinity, 0.8)
        self.assertGreater(metrics.trust, 0.8)
    
    def test_create_sibling_bond(self):
        """Test creating sibling bond metrics."""
        metrics = create_sibling_bond("sibling1", "sibling2")
        self.assertEqual(metrics.kinship, 1.0)
        self.assertGreater(metrics.affinity, 0.7)
    
    def test_create_pack_bond(self):
        """Test creating pack bond metrics."""
        metrics = create_pack_bond("member1", "member2")
        self.assertEqual(metrics.kinship, 0.0)  # Not family
        self.assertGreater(metrics.affinity, 0.5)
    
    def test_update_metrics_after_cooperation(self):
        """Test updating metrics after cooperative behavior."""
        metrics = RelationshipMetrics(affinity=0.5, trust=0.5, kinship=0.0, rank=0.0)
        
        updated = update_metrics_after_cooperation(metrics, "food_shared")
        
        # Should increase trust and affinity
        self.assertGreater(updated.trust, 0.5)
        self.assertGreater(updated.affinity, 0.5)


class TestCreatureIntegration(unittest.TestCase):
    """Test integration with Creature model."""
    
    def test_creature_has_social_traits(self):
        """Test that creatures have social traits."""
        creature = Creature(name="Test Creature")
        self.assertIsNotNone(creature.social_traits)
        self.assertIsInstance(creature.social_traits, AgentTraits)
    
    def test_creature_has_social_state(self):
        """Test that creatures have social state."""
        creature = Creature(name="Test Creature")
        self.assertIsNotNone(creature.social_state)
        self.assertIsInstance(creature.social_state, AgentSocialState)
    
    def test_creature_serialization_with_social_traits(self):
        """Test that social traits are serialized."""
        creature = Creature(name="Test Creature")
        creature.social_traits.altruism = 0.9
        creature.social_traits.dominance = 0.3
        
        data = creature.to_dict()
        self.assertIn('social_traits', data)
        self.assertEqual(data['social_traits']['altruism'], 0.9)
        self.assertEqual(data['social_traits']['dominance'], 0.3)
    
    def test_creature_deserialization_with_social_traits(self):
        """Test that social traits are deserialized."""
        creature = Creature(name="Test Creature")
        creature.social_traits.altruism = 0.9
        
        data = creature.to_dict()
        restored = Creature.from_dict(data)
        
        self.assertAlmostEqual(restored.social_traits.altruism, 0.9, delta=0.01)


if __name__ == '__main__':
    unittest.main()
