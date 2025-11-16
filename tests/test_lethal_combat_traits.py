"""
Tests for the new lethal combat traits.
"""

import unittest
from src.models.expanded_traits import (
    BERSERKER_TRAIT, EXECUTIONER_TRAIT, BLOODTHIRSTY_TRAIT, BRUTAL_TRAIT,
    ASSASSIN_TRAIT, APEX_PREDATOR_TRAIT, RECKLESS_FURY_TRAIT, TOXIC_TRAIT,
    FRENZIED_TRAIT, VAMPIRIC_TRAIT, LETHAL_COMBAT_TRAITS, ALL_CREATURE_TRAITS
)
from src.models.trait import Trait


class TestLethalCombatTraits(unittest.TestCase):
    """Test the new lethal combat traits."""
    
    def test_all_lethal_traits_exist(self):
        """Test that all 10 lethal combat traits are defined."""
        self.assertEqual(len(LETHAL_COMBAT_TRAITS), 10)
        
    def test_lethal_traits_in_all_creature_traits(self):
        """Test that lethal combat traits are included in ALL_CREATURE_TRAITS."""
        for trait in LETHAL_COMBAT_TRAITS:
            self.assertIn(trait, ALL_CREATURE_TRAITS)
    
    def test_berserker_trait(self):
        """Test Berserker trait properties."""
        self.assertEqual(BERSERKER_TRAIT.name, "Berserker")
        self.assertEqual(BERSERKER_TRAIT.trait_type, "offensive")
        self.assertEqual(BERSERKER_TRAIT.rarity, "rare")
        self.assertEqual(BERSERKER_TRAIT.defense_modifier, 0.7)
        self.assertTrue('attack_bonus_below_30_hp' in BERSERKER_TRAIT.interaction_effects)
        self.assertTrue('cannot_retreat' in BERSERKER_TRAIT.interaction_effects)
        self.assertEqual(BERSERKER_TRAIT.interaction_effects['attack_bonus_below_30_hp'], 1.0)
        
    def test_executioner_trait(self):
        """Test Executioner trait properties."""
        self.assertEqual(EXECUTIONER_TRAIT.name, "Executioner")
        self.assertEqual(EXECUTIONER_TRAIT.trait_type, "offensive")
        self.assertTrue('execute_bonus' in EXECUTIONER_TRAIT.interaction_effects)
        self.assertTrue('immune_to_fear' in EXECUTIONER_TRAIT.interaction_effects)
        self.assertEqual(EXECUTIONER_TRAIT.interaction_effects['execute_bonus'], 1.5)
        self.assertEqual(EXECUTIONER_TRAIT.interaction_effects['execute_threshold'], 0.4)
        
    def test_bloodthirsty_trait(self):
        """Test Bloodthirsty trait properties."""
        self.assertEqual(BLOODTHIRSTY_TRAIT.name, "Bloodthirsty")
        self.assertEqual(BLOODTHIRSTY_TRAIT.trait_type, "offensive")
        self.assertTrue('damage_per_kill' in BLOODTHIRSTY_TRAIT.interaction_effects)
        self.assertTrue('max_kill_stacks' in BLOODTHIRSTY_TRAIT.interaction_effects)
        self.assertEqual(BLOODTHIRSTY_TRAIT.interaction_effects['damage_per_kill'], 0.15)
        self.assertEqual(BLOODTHIRSTY_TRAIT.interaction_effects['max_kill_stacks'], 5)
        
    def test_brutal_trait(self):
        """Test Brutal trait properties."""
        self.assertEqual(BRUTAL_TRAIT.name, "Brutal")
        self.assertEqual(BRUTAL_TRAIT.strength_modifier, 1.5)
        self.assertTrue('armor_penetration' in BRUTAL_TRAIT.interaction_effects)
        self.assertTrue('bleed_on_hit' in BRUTAL_TRAIT.interaction_effects)
        self.assertEqual(BRUTAL_TRAIT.interaction_effects['armor_penetration'], 0.5)
        
    def test_assassin_trait(self):
        """Test Assassin trait properties."""
        self.assertEqual(ASSASSIN_TRAIT.name, "Assassin")
        self.assertEqual(ASSASSIN_TRAIT.defense_modifier, 0.7)
        self.assertTrue('ambush_damage' in ASSASSIN_TRAIT.interaction_effects)
        self.assertTrue('counter_vulnerability' in ASSASSIN_TRAIT.interaction_effects)
        self.assertEqual(ASSASSIN_TRAIT.interaction_effects['ambush_damage'], 2.0)
        self.assertEqual(ASSASSIN_TRAIT.interaction_effects['counter_vulnerability'], 2.0)
        
    def test_apex_predator_trait(self):
        """Test Apex Predator trait properties."""
        self.assertEqual(APEX_PREDATOR_TRAIT.name, "Apex Predator")
        self.assertEqual(APEX_PREDATOR_TRAIT.rarity, "legendary")
        self.assertTrue('stats_per_unique_kill' in APEX_PREDATOR_TRAIT.interaction_effects)
        self.assertTrue('fear_aura' in APEX_PREDATOR_TRAIT.interaction_effects)
        self.assertEqual(APEX_PREDATOR_TRAIT.interaction_effects['stats_per_unique_kill'], 0.2)
        
    def test_reckless_fury_trait(self):
        """Test Reckless Fury trait properties."""
        self.assertEqual(RECKLESS_FURY_TRAIT.name, "Reckless Fury")
        self.assertEqual(RECKLESS_FURY_TRAIT.strength_modifier, 1.6)
        self.assertEqual(RECKLESS_FURY_TRAIT.defense_modifier, 0.5)
        self.assertTrue('self_damage_chance' in RECKLESS_FURY_TRAIT.interaction_effects)
        self.assertTrue('cannot_block' in RECKLESS_FURY_TRAIT.interaction_effects)
        self.assertEqual(RECKLESS_FURY_TRAIT.interaction_effects['self_damage_chance'], 0.2)
        
    def test_toxic_trait(self):
        """Test Toxic trait properties."""
        self.assertEqual(TOXIC_TRAIT.name, "Toxic")
        self.assertTrue('poison_on_hit' in TOXIC_TRAIT.interaction_effects)
        self.assertTrue('poison_damage' in TOXIC_TRAIT.interaction_effects)
        self.assertTrue('poison_stacks' in TOXIC_TRAIT.interaction_effects)
        self.assertEqual(TOXIC_TRAIT.interaction_effects['poison_on_hit'], 1.0)
        self.assertEqual(TOXIC_TRAIT.interaction_effects['poison_stacks'], 5)
        
    def test_frenzied_trait(self):
        """Test Frenzied trait properties."""
        self.assertEqual(FRENZIED_TRAIT.name, "Frenzied")
        self.assertEqual(FRENZIED_TRAIT.speed_modifier, 2.5)
        self.assertTrue('multi_strike' in FRENZIED_TRAIT.interaction_effects)
        self.assertTrue('attack_speed_multiplier' in FRENZIED_TRAIT.interaction_effects)
        self.assertEqual(FRENZIED_TRAIT.interaction_effects['multi_strike'], 3)
        self.assertEqual(FRENZIED_TRAIT.interaction_effects['attack_speed_multiplier'], 2.5)
        
    def test_vampiric_trait(self):
        """Test Vampiric trait properties."""
        self.assertEqual(VAMPIRIC_TRAIT.name, "Vampiric")
        self.assertTrue('lifesteal' in VAMPIRIC_TRAIT.interaction_effects)
        self.assertTrue('overheal_shield' in VAMPIRIC_TRAIT.interaction_effects)
        self.assertEqual(VAMPIRIC_TRAIT.interaction_effects['lifesteal'], 0.5)
        self.assertEqual(VAMPIRIC_TRAIT.interaction_effects['overheal_max'], 0.3)
        
    def test_all_traits_are_trait_instances(self):
        """Test that all lethal combat traits are proper Trait instances."""
        for trait in LETHAL_COMBAT_TRAITS:
            self.assertIsInstance(trait, Trait)
            self.assertIsNotNone(trait.name)
            self.assertIsNotNone(trait.description)
            self.assertIsNotNone(trait.trait_type)
            
    def test_all_traits_have_interaction_effects(self):
        """Test that all lethal combat traits have interaction effects."""
        for trait in LETHAL_COMBAT_TRAITS:
            self.assertIsInstance(trait.interaction_effects, dict)
            self.assertGreater(len(trait.interaction_effects), 0)
            
    def test_high_risk_high_reward_balance(self):
        """Test that glass cannon traits have reduced defense."""
        # Berserker, Assassin, Reckless Fury should have low defense
        glass_cannon_traits = [BERSERKER_TRAIT, ASSASSIN_TRAIT, RECKLESS_FURY_TRAIT]
        for trait in glass_cannon_traits:
            self.assertLess(trait.defense_modifier, 0.8, 
                          f"{trait.name} should have reduced defense for high-risk gameplay")
            
    def test_offensive_traits_have_high_strength(self):
        """Test that most lethal traits boost strength."""
        high_strength_count = 0
        for trait in LETHAL_COMBAT_TRAITS:
            if trait.strength_modifier >= 1.1:
                high_strength_count += 1
        # At least 7 out of 10 should have boosted strength
        self.assertGreaterEqual(high_strength_count, 7)
        
    def test_trait_serialization(self):
        """Test that lethal traits can be serialized and deserialized."""
        for trait in LETHAL_COMBAT_TRAITS:
            trait_dict = trait.to_dict()
            self.assertIsInstance(trait_dict, dict)
            self.assertEqual(trait_dict['name'], trait.name)
            self.assertEqual(trait_dict['trait_type'], trait.trait_type)
            
            # Deserialize and check equality
            restored_trait = Trait.from_dict(trait_dict)
            self.assertEqual(restored_trait.name, trait.name)
            self.assertEqual(restored_trait.trait_type, trait.trait_type)
            self.assertEqual(restored_trait.strength_modifier, trait.strength_modifier)


class TestLethalTraitsIntegration(unittest.TestCase):
    """Test integration of lethal traits with the trait system."""
    
    def test_trait_dominance_patterns(self):
        """Test that lethal traits have appropriate dominance."""
        for trait in LETHAL_COMBAT_TRAITS:
            self.assertIn(trait.dominance, ['dominant', 'recessive', 'codominant'])
            
    def test_rare_traits_are_rare(self):
        """Test that most lethal traits are rare or legendary."""
        rare_count = sum(1 for t in LETHAL_COMBAT_TRAITS if t.rarity in ['rare', 'legendary'])
        self.assertGreaterEqual(rare_count, 9, "Most lethal traits should be rare or legendary")
        
    def test_unique_trait_names(self):
        """Test that all lethal trait names are unique."""
        names = [t.name for t in LETHAL_COMBAT_TRAITS]
        self.assertEqual(len(names), len(set(names)))


if __name__ == '__main__':
    unittest.main()
