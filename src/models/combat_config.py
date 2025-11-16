"""
Combat Configuration - Tunable parameters for combat behavior.

Centralizes all combat-related parameters for easy balancing and tuning.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class CombatConfig:
    """
    Configuration parameters for combat system.
    
    All combat behaviors can be tuned through these parameters.
    """
    
    # === Targeting Parameters ===
    max_chase_distance: float = 30.0
    """Maximum distance to chase a target before giving up"""
    
    close_combat_range: float = 10.0
    """Distance considered "close range" for combat decisions"""
    
    support_range: float = 20.0
    """Maximum distance to support allies"""
    
    min_target_switch_time: float = 2.0
    """Minimum seconds before switching to a new target"""
    
    target_retention_distance: float = 15.0
    """Keep current target if within this distance (hysteresis)"""
    
    # === Targeting Score Weights ===
    weight_distance: float = 0.3
    """How much distance affects target selection"""
    
    weight_threat: float = 0.25
    """How much threat level affects target selection"""
    
    weight_relationship: float = 0.25
    """How much relationships affect target selection"""
    
    weight_opportunity: float = 0.2
    """How much opportunity (injured, weak) affects target selection"""
    
    # === Combat Memory ===
    recent_memory_duration: float = 10.0
    """How long to remember recent attackers (seconds)"""
    
    revenge_memory_duration: float = 30.0
    """How long to prioritize revenge (seconds)"""
    
    significant_damage_threshold: int = 50
    """Damage threshold to trigger revenge priority"""
    
    # === Cooperative Behavior ===
    gang_up_threshold: int = 2
    """Minimum allies nearby to trigger gang-up behavior"""
    
    gang_up_damage_bonus: float = 0.15
    """Damage bonus per ally when ganging up (multiplicative)"""
    
    protect_ally_hp_threshold: float = 0.3
    """HP threshold below which allies trigger protective behavior"""
    
    ally_support_bonus: float = 0.1
    """Damage bonus when fighting near allies"""
    
    # === Flee Behavior ===
    flee_hp_threshold: float = 0.15
    """HP percentage below which creature considers fleeing"""
    
    flee_outnumber_threshold: int = 3
    """Number of enemies to trigger outnumbered flee"""
    
    flee_speed_multiplier: float = 1.3
    """Speed multiplier when fleeing"""
    
    # === Strain & Family ===
    same_strain_avoid_combat: bool = False
    """Whether same-strain creatures avoid combat (cooperation mode)"""
    
    family_protection_bonus: float = 0.2
    """Damage bonus when protecting family members"""
    
    family_detection_range: float = 25.0
    """Range to detect family members needing help"""
    
    # === Attack Parameters ===
    base_attack_range_melee: float = 3.0
    """Base range for melee attacks"""
    
    base_attack_range_ranged: float = 8.0
    """Base range for ranged/special attacks"""
    
    attack_cooldown: float = 1.0
    """Seconds between attacks"""
    
    # === Retargeting ===
    retarget_check_interval: float = 0.5
    """How often to check for retargeting (seconds)"""
    
    retarget_distance_threshold: float = 0.8
    """Distance ratio to trigger retarget (new target must be X% closer)"""
    
    # === Personality Influence ===
    personality_aggression_targeting_weight: float = 0.3
    """How much aggression affects target selection"""
    
    personality_caution_flee_modifier: float = 0.3
    """How much caution affects flee threshold"""
    
    personality_loyalty_ally_bonus: float = 0.2
    """How much loyalty increases ally support bonus"""
    
    # === Balance Tuning ===
    carnivore_prey_bonus: float = 0.4
    """Targeting bonus for carnivores vs herbivores"""
    
    revenge_damage_bonus: float = 0.3
    """Damage bonus when attacking revenge targets"""
    
    rival_damage_bonus: float = 0.15
    """Damage bonus when attacking rivals"""
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'max_chase_distance': self.max_chase_distance,
            'close_combat_range': self.close_combat_range,
            'support_range': self.support_range,
            'min_target_switch_time': self.min_target_switch_time,
            'target_retention_distance': self.target_retention_distance,
            'weight_distance': self.weight_distance,
            'weight_threat': self.weight_threat,
            'weight_relationship': self.weight_relationship,
            'weight_opportunity': self.weight_opportunity,
            'recent_memory_duration': self.recent_memory_duration,
            'revenge_memory_duration': self.revenge_memory_duration,
            'significant_damage_threshold': self.significant_damage_threshold,
            'gang_up_threshold': self.gang_up_threshold,
            'gang_up_damage_bonus': self.gang_up_damage_bonus,
            'protect_ally_hp_threshold': self.protect_ally_hp_threshold,
            'ally_support_bonus': self.ally_support_bonus,
            'flee_hp_threshold': self.flee_hp_threshold,
            'flee_outnumber_threshold': self.flee_outnumber_threshold,
            'flee_speed_multiplier': self.flee_speed_multiplier,
            'same_strain_avoid_combat': self.same_strain_avoid_combat,
            'family_protection_bonus': self.family_protection_bonus,
            'family_detection_range': self.family_detection_range,
            'base_attack_range_melee': self.base_attack_range_melee,
            'base_attack_range_ranged': self.base_attack_range_ranged,
            'attack_cooldown': self.attack_cooldown,
            'retarget_check_interval': self.retarget_check_interval,
            'retarget_distance_threshold': self.retarget_distance_threshold,
            'personality_aggression_targeting_weight': self.personality_aggression_targeting_weight,
            'personality_caution_flee_modifier': self.personality_caution_flee_modifier,
            'personality_loyalty_ally_bonus': self.personality_loyalty_ally_bonus,
            'carnivore_prey_bonus': self.carnivore_prey_bonus,
            'revenge_damage_bonus': self.revenge_damage_bonus,
            'rival_damage_bonus': self.rival_damage_bonus
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'CombatConfig':
        """Deserialize from dictionary."""
        return CombatConfig(**data)
    
    @staticmethod
    def create_aggressive_config() -> 'CombatConfig':
        """Create configuration for aggressive, fast-paced combat."""
        config = CombatConfig()
        config.max_chase_distance = 40.0  # Chase further
        config.min_target_switch_time = 1.0  # Switch faster
        config.attack_cooldown = 0.8  # Attack more frequently
        config.revenge_damage_bonus = 0.5  # Higher revenge bonus
        return config
    
    @staticmethod
    def create_tactical_config() -> 'CombatConfig':
        """Create configuration for tactical, positioning-focused combat."""
        config = CombatConfig()
        config.max_chase_distance = 20.0  # Don't chase far
        config.min_target_switch_time = 3.0  # Stick with targets longer
        config.weight_distance = 0.5  # Distance matters more
        config.gang_up_damage_bonus = 0.25  # Reward positioning
        return config
    
    @staticmethod
    def create_family_focused_config() -> 'CombatConfig':
        """Create configuration emphasizing family and strain loyalty."""
        config = CombatConfig()
        config.same_strain_avoid_combat = True  # Same strain cooperation
        config.family_protection_bonus = 0.4  # High family bonus
        config.weight_relationship = 0.4  # Relationships matter more
        config.ally_support_bonus = 0.2  # Better ally support
        return config
