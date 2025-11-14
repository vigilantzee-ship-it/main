"""
Status effect model - Represents temporary battle conditions.
"""

from typing import Dict, Optional
from enum import Enum


class StatusEffectType(Enum):
    """Types of status effects that can affect creatures."""
    POISON = "poison"
    BURN = "burn"
    PARALYSIS = "paralysis"
    SLEEP = "sleep"
    FREEZE = "freeze"
    CONFUSION = "confusion"
    STUN = "stun"
    REGEN = "regen"
    SHIELD = "shield"


class StatusEffect:
    """
    Represents a status effect applied to a creature during battle.
    
    Status effects can deal damage over time, prevent actions, modify stats,
    or provide other battle effects. They have durations and can stack or
    replace existing effects.
    
    Attributes:
        name (str): Name of the status effect
        effect_type (StatusEffectType): Type of status effect
        duration (int): Number of turns the effect lasts
        potency (int): Strength of the effect (damage per turn, etc.)
        prevents_action (bool): Whether this effect prevents the creature from acting
        applied_turn (int): The turn number when effect was applied
    """
    
    def __init__(
        self,
        name: str,
        effect_type: StatusEffectType,
        duration: int = 3,
        potency: int = 0,
        prevents_action: bool = False,
        applied_turn: int = 0
    ):
        """
        Initialize a status effect.
        
        Args:
            name: Name of the effect
            effect_type: Type of status effect
            duration: How many turns it lasts
            potency: Strength of the effect
            prevents_action: If True, creature cannot act
            applied_turn: Turn when effect was applied
        """
        self.name = name
        self.effect_type = effect_type
        self.duration = duration
        self.potency = potency
        self.prevents_action = prevents_action
        self.applied_turn = applied_turn
        self.current_duration = duration
    
    def tick(self) -> bool:
        """
        Process one turn of the status effect.
        
        Returns:
            True if effect is still active, False if expired
        """
        self.current_duration -= 1
        return self.current_duration > 0
    
    def is_active(self) -> bool:
        """Check if the effect is still active."""
        return self.current_duration > 0
    
    def get_damage(self) -> int:
        """
        Get damage dealt this turn (for damage-over-time effects).
        
        Returns:
            Damage amount, or 0 if not a damaging effect
        """
        if self.effect_type in [StatusEffectType.POISON, StatusEffectType.BURN]:
            return self.potency
        return 0
    
    def get_healing(self) -> int:
        """
        Get healing provided this turn (for regeneration effects).
        
        Returns:
            Healing amount, or 0 if not a healing effect
        """
        if self.effect_type == StatusEffectType.REGEN:
            return self.potency
        return 0
    
    def prevents_creature_action(self) -> bool:
        """Check if this effect prevents the creature from acting."""
        return self.prevents_action or self.effect_type in [
            StatusEffectType.SLEEP,
            StatusEffectType.FREEZE,
            StatusEffectType.STUN
        ]
    
    def to_dict(self) -> Dict:
        """Serialize status effect to dictionary."""
        return {
            'name': self.name,
            'effect_type': self.effect_type.value,
            'duration': self.duration,
            'potency': self.potency,
            'prevents_action': self.prevents_action,
            'applied_turn': self.applied_turn,
            'current_duration': self.current_duration
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'StatusEffect':
        """Deserialize status effect from dictionary."""
        effect = StatusEffect(
            name=data['name'],
            effect_type=StatusEffectType(data['effect_type']),
            duration=data['duration'],
            potency=data.get('potency', 0),
            prevents_action=data.get('prevents_action', False),
            applied_turn=data.get('applied_turn', 0)
        )
        effect.current_duration = data.get('current_duration', effect.duration)
        return effect
    
    def __repr__(self):
        """String representation of StatusEffect."""
        return f"StatusEffect(name='{self.name}', type={self.effect_type.value}, duration={self.current_duration})"


# Predefined status effects for easy creation
PREDEFINED_STATUS_EFFECTS = {
    'poison': lambda: StatusEffect(
        name="Poison",
        effect_type=StatusEffectType.POISON,
        duration=5,
        potency=5
    ),
    'burn': lambda: StatusEffect(
        name="Burn",
        effect_type=StatusEffectType.BURN,
        duration=4,
        potency=8
    ),
    'paralysis': lambda: StatusEffect(
        name="Paralysis",
        effect_type=StatusEffectType.PARALYSIS,
        duration=3,
        prevents_action=False
    ),
    'sleep': lambda: StatusEffect(
        name="Sleep",
        effect_type=StatusEffectType.SLEEP,
        duration=3,
        prevents_action=True
    ),
    'freeze': lambda: StatusEffect(
        name="Freeze",
        effect_type=StatusEffectType.FREEZE,
        duration=2,
        prevents_action=True
    ),
    'confusion': lambda: StatusEffect(
        name="Confusion",
        effect_type=StatusEffectType.CONFUSION,
        duration=4,
        prevents_action=False
    ),
    'stun': lambda: StatusEffect(
        name="Stun",
        effect_type=StatusEffectType.STUN,
        duration=1,
        prevents_action=True
    ),
    'regen': lambda: StatusEffect(
        name="Regeneration",
        effect_type=StatusEffectType.REGEN,
        duration=5,
        potency=10
    ),
    'shield': lambda: StatusEffect(
        name="Shield",
        effect_type=StatusEffectType.SHIELD,
        duration=3,
        potency=5
    )
}


def create_status_effect(effect_name: str) -> Optional[StatusEffect]:
    """
    Create a status effect from a predefined template.
    
    Args:
        effect_name: Name of the status effect template
        
    Returns:
        A new StatusEffect instance, or None if not found
    """
    creator = PREDEFINED_STATUS_EFFECTS.get(effect_name.lower())
    return creator() if creator else None
