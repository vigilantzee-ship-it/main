"""
Unit tests for status effect system.
"""

import unittest
from src.models.status_effect import (
    StatusEffect,
    StatusEffectType,
    create_status_effect,
    PREDEFINED_STATUS_EFFECTS
)


class TestStatusEffect(unittest.TestCase):
    """Test cases for StatusEffect class."""
    
    def test_status_effect_initialization(self):
        """Test creating a status effect."""
        effect = StatusEffect(
            name="Test Poison",
            effect_type=StatusEffectType.POISON,
            duration=5,
            potency=10
        )
        
        self.assertEqual(effect.name, "Test Poison")
        self.assertEqual(effect.effect_type, StatusEffectType.POISON)
        self.assertEqual(effect.duration, 5)
        self.assertEqual(effect.potency, 10)
        self.assertTrue(effect.is_active())
    
    def test_status_effect_tick(self):
        """Test status effect duration decreases."""
        effect = StatusEffect(
            name="Burn",
            effect_type=StatusEffectType.BURN,
            duration=3,
            potency=5
        )
        
        self.assertEqual(effect.current_duration, 3)
        
        # Tick once
        still_active = effect.tick()
        self.assertTrue(still_active)
        self.assertEqual(effect.current_duration, 2)
        
        # Tick twice more
        effect.tick()
        still_active = effect.tick()
        self.assertFalse(still_active)
        self.assertEqual(effect.current_duration, 0)
        self.assertFalse(effect.is_active())
    
    def test_damage_over_time(self):
        """Test damage-over-time effects."""
        poison = StatusEffect(
            name="Poison",
            effect_type=StatusEffectType.POISON,
            duration=3,
            potency=8
        )
        
        self.assertEqual(poison.get_damage(), 8)
        self.assertEqual(poison.get_healing(), 0)
        
        burn = StatusEffect(
            name="Burn",
            effect_type=StatusEffectType.BURN,
            duration=3,
            potency=10
        )
        
        self.assertEqual(burn.get_damage(), 10)
    
    def test_healing_over_time(self):
        """Test healing-over-time effects."""
        regen = StatusEffect(
            name="Regeneration",
            effect_type=StatusEffectType.REGEN,
            duration=5,
            potency=12
        )
        
        self.assertEqual(regen.get_healing(), 12)
        self.assertEqual(regen.get_damage(), 0)
    
    def test_prevents_action(self):
        """Test effects that prevent actions."""
        sleep = StatusEffect(
            name="Sleep",
            effect_type=StatusEffectType.SLEEP,
            duration=3
        )
        
        self.assertTrue(sleep.prevents_creature_action())
        
        freeze = StatusEffect(
            name="Freeze",
            effect_type=StatusEffectType.FREEZE,
            duration=2
        )
        
        self.assertTrue(freeze.prevents_creature_action())
        
        poison = StatusEffect(
            name="Poison",
            effect_type=StatusEffectType.POISON,
            duration=3
        )
        
        self.assertFalse(poison.prevents_creature_action())
    
    def test_status_effect_serialization(self):
        """Test serialization and deserialization."""
        effect = StatusEffect(
            name="Test Effect",
            effect_type=StatusEffectType.PARALYSIS,
            duration=4,
            potency=5,
            prevents_action=True,
            applied_turn=10
        )
        
        # Tick once to modify duration
        effect.tick()
        
        # Serialize
        data = effect.to_dict()
        
        self.assertEqual(data['name'], "Test Effect")
        self.assertEqual(data['effect_type'], "paralysis")
        self.assertEqual(data['duration'], 4)
        self.assertEqual(data['current_duration'], 3)
        
        # Deserialize
        restored = StatusEffect.from_dict(data)
        
        self.assertEqual(restored.name, effect.name)
        self.assertEqual(restored.effect_type, effect.effect_type)
        self.assertEqual(restored.current_duration, 3)


class TestPredefinedStatusEffects(unittest.TestCase):
    """Test cases for predefined status effects."""
    
    def test_predefined_effects_exist(self):
        """Test that predefined status effects are available."""
        self.assertIn('poison', PREDEFINED_STATUS_EFFECTS)
        self.assertIn('burn', PREDEFINED_STATUS_EFFECTS)
        self.assertIn('sleep', PREDEFINED_STATUS_EFFECTS)
        self.assertIn('paralysis', PREDEFINED_STATUS_EFFECTS)
        self.assertIn('regen', PREDEFINED_STATUS_EFFECTS)
    
    def test_create_status_effect(self):
        """Test creating status effect from template."""
        poison = create_status_effect('poison')
        
        self.assertIsNotNone(poison)
        self.assertEqual(poison.name, "Poison")
        self.assertEqual(poison.effect_type, StatusEffectType.POISON)
        self.assertGreater(poison.duration, 0)
        self.assertGreater(poison.potency, 0)
    
    def test_create_invalid_status_effect(self):
        """Test creating status effect with invalid name."""
        effect = create_status_effect('nonexistent')
        self.assertIsNone(effect)
    
    def test_templates_are_independent(self):
        """Test that created effects are independent instances."""
        effect1 = create_status_effect('burn')
        effect2 = create_status_effect('burn')
        
        self.assertIsNot(effect1, effect2)
        
        # Modify one
        effect1.tick()
        
        # Other should be unaffected
        self.assertNotEqual(effect1.current_duration, effect2.current_duration)


if __name__ == '__main__':
    unittest.main()
