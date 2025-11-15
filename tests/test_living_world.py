"""
Tests for the Living World systems - history, skills, personality, relationships.
"""

import unittest
import time
from src.models.history import CreatureHistory, LifeEvent, EventType, KillRecord, Achievement
from src.models.skills import Skill, SkillType, SkillManager, Proficiency
from src.models.personality import PersonalityProfile
from src.models.relationships import Relationship, RelationshipType, RelationshipManager


class TestCreatureHistory(unittest.TestCase):
    """Test the CreatureHistory class."""
    
    def test_initialization(self):
        """Test creating a creature history."""
        history = CreatureHistory("test-id", "TestCreature")
        self.assertEqual(history.creature_id, "test-id")
        self.assertEqual(history.creature_name, "TestCreature")
        self.assertEqual(history.battles_fought, 0)
        self.assertEqual(len(history.events), 0)
    
    def test_record_attack(self):
        """Test recording an attack."""
        history = CreatureHistory("test-id", "TestCreature")
        history.record_attack("enemy-1", 50.0, was_critical=False)
        
        self.assertEqual(len(history.events), 1)
        self.assertEqual(history.total_damage_dealt, 50.0)
        self.assertEqual(history.events[0].event_type, EventType.ATTACK)
    
    def test_record_critical_hit(self):
        """Test recording a critical hit."""
        history = CreatureHistory("test-id", "TestCreature")
        history.record_attack("enemy-1", 100.0, was_critical=True)
        
        self.assertEqual(history.events[0].event_type, EventType.CRITICAL_HIT)
        self.assertGreater(history.events[0].significance, 0.5)
    
    def test_record_kill(self):
        """Test recording a kill."""
        history = CreatureHistory("test-id", "TestCreature")
        history.record_kill("victim-1", "Victim", power_differential=1.0)
        
        self.assertEqual(len(history.kills), 1)
        self.assertEqual(history.kills[0].victim_name, "Victim")
        self.assertEqual(len(history.events), 2)  # Kill event + First Blood achievement
        self.assertEqual(len(history.achievements), 1)
    
    def test_giant_slayer_achievement(self):
        """Test giant slayer achievement for defeating stronger enemy."""
        history = CreatureHistory("test-id", "TestCreature")
        history.record_kill("victim-1", "Giant", power_differential=2.5)
        
        # Should have First Blood and Giant Slayer
        self.assertEqual(len(history.achievements), 2)
        achievement_names = [a.name for a in history.achievements]
        self.assertIn("Giant Slayer", achievement_names)
    
    def test_revenge_kill(self):
        """Test recording a revenge kill."""
        history = CreatureHistory("test-id", "TestCreature")
        history.record_kill("victim-1", "Victim", was_revenge=True)
        
        self.assertEqual(history.events[0].event_type, EventType.REVENGE_KILL)
        self.assertGreater(history.events[0].significance, 0.8)
    
    def test_win_rate_calculation(self):
        """Test win rate calculation."""
        history = CreatureHistory("test-id", "TestCreature")
        history.battles_fought = 10
        history.battles_won = 7
        
        self.assertAlmostEqual(history.get_win_rate(), 0.7)
    
    def test_serialization(self):
        """Test serializing and deserializing history."""
        history = CreatureHistory("test-id", "TestCreature")
        history.record_attack("enemy-1", 50.0)
        history.record_kill("victim-1", "Victim")
        
        # Serialize
        data = history.to_dict()
        
        # Deserialize
        restored = CreatureHistory.from_dict(data)
        
        self.assertEqual(restored.creature_id, history.creature_id)
        self.assertEqual(len(restored.events), len(history.events))
        self.assertEqual(len(restored.kills), len(history.kills))


class TestSkillSystem(unittest.TestCase):
    """Test the skill system."""
    
    def test_skill_initialization(self):
        """Test creating a skill."""
        skill = Skill(SkillType.MELEE_ATTACK)
        self.assertEqual(skill.level, 0)
        self.assertEqual(skill.experience, 0.0)
        self.assertEqual(skill.get_proficiency(), Proficiency.NOVICE)
    
    def test_skill_use_gains_experience(self):
        """Test that using a skill gains experience."""
        skill = Skill(SkillType.MELEE_ATTACK)
        initial_xp = skill.experience
        
        skill.use(difficulty=1.0, success=True)
        
        self.assertGreater(skill.experience, initial_xp)
    
    def test_skill_levels_up(self):
        """Test that skills level up with enough experience."""
        skill = Skill(SkillType.MELEE_ATTACK)
        
        # Use skill many times
        for _ in range(100):
            skill.use(difficulty=1.0, success=True)
        
        self.assertGreater(skill.level, 0)
    
    def test_skill_performance_modifier(self):
        """Test that skill level affects performance."""
        skill = Skill(SkillType.MELEE_ATTACK, level=50)
        modifier = skill.get_performance_modifier()
        
        # Should be better than baseline
        self.assertGreater(modifier, 1.0)
        self.assertAlmostEqual(modifier, 1.5)
    
    def test_skill_proficiency_levels(self):
        """Test proficiency levels."""
        skill = Skill(SkillType.MELEE_ATTACK, level=0)
        self.assertEqual(skill.get_proficiency(), Proficiency.NOVICE)
        
        skill.level = 25
        self.assertEqual(skill.get_proficiency(), Proficiency.COMPETENT)
        
        skill.level = 45
        self.assertEqual(skill.get_proficiency(), Proficiency.EXPERT)
        
        skill.level = 65
        self.assertEqual(skill.get_proficiency(), Proficiency.MASTER)
        
        skill.level = 85
        self.assertEqual(skill.get_proficiency(), Proficiency.LEGENDARY)
    
    def test_skill_manager(self):
        """Test the skill manager."""
        manager = SkillManager()
        
        # Use a skill
        modifier = manager.use_skill(SkillType.MELEE_ATTACK, difficulty=1.0)
        
        # Should have created the skill
        self.assertIn(SkillType.MELEE_ATTACK, manager.skills)
        self.assertGreaterEqual(modifier, 1.0)
    
    def test_skill_serialization(self):
        """Test serializing skills."""
        skill = Skill(SkillType.DODGE, level=30, experience=100.0)
        
        # Serialize
        data = skill.to_dict()
        
        # Deserialize
        restored = Skill.from_dict(data)
        
        self.assertEqual(restored.skill_type, skill.skill_type)
        self.assertEqual(restored.level, skill.level)


class TestPersonalitySystem(unittest.TestCase):
    """Test the personality system."""
    
    def test_personality_initialization(self):
        """Test creating a personality."""
        personality = PersonalityProfile(
            aggression=0.8,
            caution=0.3,
            loyalty=0.9
        )
        
        self.assertEqual(personality.aggression, 0.8)
        self.assertEqual(personality.caution, 0.3)
        self.assertEqual(personality.loyalty, 0.9)
    
    def test_personality_bounds(self):
        """Test that personality values are bounded 0-1."""
        personality = PersonalityProfile(
            aggression=1.5,  # Too high
            caution=-0.5     # Too low
        )
        
        self.assertEqual(personality.aggression, 1.0)
        self.assertEqual(personality.caution, 0.0)
    
    def test_random_personality(self):
        """Test generating random personalities."""
        p1 = PersonalityProfile.random()
        p2 = PersonalityProfile.random()
        
        # Should be different
        self.assertNotEqual(p1.aggression, p2.aggression)
    
    def test_personality_inheritance(self):
        """Test inheriting personality from parents."""
        parent1 = PersonalityProfile(aggression=0.8, caution=0.2)
        parent2 = PersonalityProfile(aggression=0.4, caution=0.6)
        
        child = PersonalityProfile.inherit(parent1, parent2, mutation_rate=0.0)
        
        # Child should have average
        self.assertAlmostEqual(child.aggression, 0.6, delta=0.05)
        self.assertAlmostEqual(child.caution, 0.4, delta=0.05)
    
    def test_retreat_decision(self):
        """Test personality affects retreat decision."""
        cautious = PersonalityProfile(caution=0.9)
        reckless = PersonalityProfile(caution=0.1)
        
        # At 30% HP with 2 enemies
        cautious_retreats = cautious.should_retreat(0.3, 2)
        reckless_retreats = reckless.should_retreat(0.3, 2)
        
        # Cautious should be more likely to retreat
        self.assertTrue(cautious_retreats or not reckless_retreats)
    
    def test_combat_modifiers(self):
        """Test personality-based combat modifiers."""
        loyal = PersonalityProfile(loyalty=1.0, pride=1.0)
        
        # Team fight bonus
        team_bonus = loyal.get_team_fight_bonus(has_allies=True, has_family=True)
        self.assertGreater(team_bonus, 1.0)
        
        # Revenge bonus
        revenge_bonus = loyal.get_revenge_bonus(is_revenge=True)
        self.assertGreater(revenge_bonus, 1.0)
    
    def test_serialization(self):
        """Test serializing personality."""
        personality = PersonalityProfile(
            aggression=0.7,
            caution=0.4,
            loyalty=0.9
        )
        
        # Serialize
        data = personality.to_dict()
        
        # Deserialize
        restored = PersonalityProfile.from_dict(data)
        
        self.assertEqual(restored.aggression, personality.aggression)
        self.assertEqual(restored.caution, personality.caution)
        self.assertEqual(restored.loyalty, personality.loyalty)


class TestRelationshipSystem(unittest.TestCase):
    """Test the relationship system."""
    
    def test_relationship_initialization(self):
        """Test creating a relationship."""
        rel = Relationship("creature-1", "creature-2", RelationshipType.ALLY, strength=0.7)
        
        self.assertEqual(rel.creature_id, "creature-1")
        self.assertEqual(rel.target_id, "creature-2")
        self.assertEqual(rel.relationship_type, RelationshipType.ALLY)
        self.assertEqual(rel.strength, 0.7)
    
    def test_relationship_strengthen_weaken(self):
        """Test strengthening and weakening relationships."""
        rel = Relationship("creature-1", "creature-2", RelationshipType.ALLY, strength=0.5)
        
        rel.strengthen(0.2)
        self.assertAlmostEqual(rel.strength, 0.7)
        
        rel.weaken(0.3)
        self.assertAlmostEqual(rel.strength, 0.4)
    
    def test_relationship_combat_modifier(self):
        """Test combat modifiers from relationships."""
        # Fighting together with ally
        ally = Relationship("c1", "c2", RelationshipType.ALLY, strength=1.0)
        ally_bonus = ally.get_combat_modifier(fighting_together=True)
        self.assertGreater(ally_bonus, 1.0)
        
        # Fighting against revenge target
        revenge = Relationship("c1", "c2", RelationshipType.REVENGE_TARGET, strength=1.0)
        revenge_bonus = revenge.get_combat_modifier(fighting_together=False)
        self.assertGreater(revenge_bonus, 1.0)
    
    def test_relationship_manager(self):
        """Test the relationship manager."""
        manager = RelationshipManager("creature-1")
        
        # Add relationships
        manager.add_relationship("creature-2", RelationshipType.ALLY, strength=0.8)
        manager.add_relationship("creature-3", RelationshipType.RIVAL, strength=0.6)
        
        self.assertEqual(len(manager.relationships), 2)
        self.assertTrue(manager.has_relationship("creature-2"))
        self.assertFalse(manager.has_relationship("creature-4"))
    
    def test_get_family(self):
        """Test getting family members."""
        manager = RelationshipManager("creature-1")
        
        manager.add_relationship("parent-1", RelationshipType.PARENT)
        manager.add_relationship("child-1", RelationshipType.CHILD)
        manager.add_relationship("sibling-1", RelationshipType.SIBLING)
        manager.add_relationship("ally-1", RelationshipType.ALLY)
        
        family = manager.get_family()
        self.assertEqual(len(family), 3)
    
    def test_record_fought_together(self):
        """Test recording fighting together."""
        manager = RelationshipManager("creature-1")
        
        manager.record_fought_together("ally-1")
        
        self.assertTrue(manager.has_relationship("ally-1", RelationshipType.ALLY))
    
    def test_revenge_target_tracking(self):
        """Test tracking revenge targets."""
        manager = RelationshipManager("creature-1")
        
        manager.record_family_killed("killer-1", "Parent")
        
        revenge_targets = manager.get_revenge_targets()
        self.assertEqual(len(revenge_targets), 1)
        self.assertEqual(revenge_targets[0].target_id, "killer-1")
    
    def test_serialization(self):
        """Test serializing relationships."""
        manager = RelationshipManager("creature-1")
        manager.add_relationship("creature-2", RelationshipType.ALLY, strength=0.8)
        
        # Serialize
        data = manager.to_dict()
        
        # Deserialize
        restored = RelationshipManager.from_dict(data)
        
        self.assertEqual(restored.creature_id, manager.creature_id)
        self.assertEqual(len(restored.relationships), len(manager.relationships))


if __name__ == '__main__':
    unittest.main()
