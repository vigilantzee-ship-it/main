"""
Living World Battle Integration - Integrates history, skills, personality, and relationships into battles.

This module enhances the battle system with deep simulation features that make every
creature unique and every battle memorable.
"""

from typing import List, Optional, Tuple
import random
from ..models.creature import Creature
from ..models.history import EventType
from ..models.skills import SkillType
from ..models.relationships import RelationshipType


class LivingWorldBattleEnhancer:
    """
    Enhances battle system with living world features.
    
    Provides hooks for integrating history, skills, personality, and relationships
    into combat calculations and decision making.
    """
    
    def __init__(self, battle_system):
        """
        Initialize the enhancer.
        
        Args:
            battle_system: The battle system to enhance
        """
        self.battle = battle_system
        self.combat_started = {}  # Track who started combat with whom
    
    def on_battle_start(self, creatures: List[Creature]):
        """
        Called when battle starts.
        
        Args:
            creatures: All creatures in the battle
        """
        for creature in creatures:
            # Record battle start in history
            other_ids = [c.creature_id for c in creatures if c.creature_id != creature.creature_id]
            creature.history.record_battle_start(other_ids)
    
    def enhance_target_selection(
        self,
        attacker: Creature,
        potential_targets: List[Creature]
    ) -> Optional[Creature]:
        """
        Use personality to influence target selection.
        
        Args:
            attacker: The attacking creature
            potential_targets: List of possible targets
            
        Returns:
            Preferred target, or None for random selection
        """
        if not potential_targets:
            return None
        
        # Check for revenge targets first
        revenge_targets = attacker.relationships.get_revenge_targets()
        if revenge_targets:
            for target in potential_targets:
                if any(rel.target_id == target.creature_id for rel in revenge_targets):
                    return target
        
        # Use personality to select target
        # Create simple target info for personality system
        target_info = []
        for t in potential_targets:
            target_info.append(type('obj', (object,), {
                'attack': t.stats.attack,
                'hp': t.stats.hp,
                'level': t.level
            })())
        
        pref_index = attacker.personality.get_target_preference(target_info)
        if pref_index is not None:
            return potential_targets[pref_index]
        
        return None
    
    def should_retreat(
        self,
        creature: Creature,
        enemy_count: int
    ) -> bool:
        """
        Determine if creature should retreat based on personality.
        
        Args:
            creature: The creature to check
            enemy_count: Number of enemies
            
        Returns:
            True if should retreat
        """
        hp_percent = creature.stats.hp / creature.stats.max_hp if creature.stats.max_hp > 0 else 0
        return creature.personality.should_retreat(hp_percent, enemy_count)
    
    def calculate_damage_modifier(
        self,
        attacker: Creature,
        defender: Creature,
        base_damage: float,
        is_critical: bool = False
    ) -> float:
        """
        Calculate final damage with all living world modifiers.
        
        Args:
            attacker: Attacking creature
            defender: Defending creature
            base_damage: Base damage before modifiers
            is_critical: Whether this is a critical hit
            
        Returns:
            Modified damage value
        """
        damage = base_damage
        
        # Skill modifier for attack
        attack_skill = attacker.skills.get_skill(SkillType.MELEE_ATTACK)
        skill_modifier = attack_skill.get_performance_modifier()
        damage *= skill_modifier
        
        # Personality modifiers
        # Check if fighting with allies (same strain)
        has_allies = False  # Would need to check battle state
        has_family = False  # Would need to check if any family members are allies
        team_bonus = attacker.personality.get_team_fight_bonus(has_allies, has_family)
        damage *= team_bonus
        
        # Check for revenge
        is_revenge = attacker.relationships.has_relationship(
            defender.creature_id,
            RelationshipType.REVENGE_TARGET
        )
        revenge_bonus = attacker.personality.get_revenge_bonus(is_revenge)
        damage *= revenge_bonus
        
        # Relationship modifier
        rel = attacker.relationships.get_relationship(defender.creature_id)
        if rel:
            rel_modifier = rel.get_combat_modifier(fighting_together=False)
            damage *= rel_modifier
        
        return damage
    
    def calculate_critical_chance_modifier(self, attacker: Creature) -> float:
        """
        Calculate critical hit chance modifier.
        
        Args:
            attacker: Attacking creature
            
        Returns:
            Percentage point modifier to crit chance
        """
        # Base critical skill bonus
        crit_skill = attacker.skills.get_skill(SkillType.CRITICAL_STRIKE)
        skill_bonus = crit_skill.get_success_chance_bonus()
        
        # Personality modifier
        personality_bonus = attacker.personality.get_critical_hit_chance_modifier()
        
        return skill_bonus + personality_bonus
    
    def calculate_dodge_chance_modifier(self, defender: Creature) -> float:
        """
        Calculate dodge chance modifier.
        
        Args:
            defender: Defending creature
            
        Returns:
            Percentage point modifier to dodge chance
        """
        # Dodge skill bonus
        dodge_skill = defender.skills.get_skill(SkillType.DODGE)
        skill_bonus = dodge_skill.get_success_chance_bonus()
        
        # Personality modifier
        personality_bonus = defender.personality.get_dodge_chance_modifier()
        
        return skill_bonus + personality_bonus
    
    def on_attack_made(
        self,
        attacker: Creature,
        defender: Creature,
        damage: float,
        was_critical: bool = False,
        hit: bool = True
    ):
        """
        Called when an attack is made.
        
        Args:
            attacker: Attacking creature
            defender: Defending creature
            damage: Damage dealt
            was_critical: Whether it was a critical hit
            hit: Whether the attack hit
        """
        if hit:
            # Record in history
            attacker.history.record_attack(defender.creature_id, damage, was_critical)
            defender.history.record_damage_taken(attacker.creature_id, damage)
            
            # Update skills
            # Attack difficulty based on defender's defense
            difficulty = defender.stats.defense / max(attacker.stats.attack, 1)
            attacker.skills.use_skill(SkillType.MELEE_ATTACK, difficulty, success=True)
            
            if was_critical:
                attacker.skills.use_skill(SkillType.CRITICAL_STRIKE, difficulty, success=True)
        else:
            # Miss - update dodge skill for defender
            difficulty = attacker.stats.attack / max(defender.stats.speed, 1)
            defender.skills.use_skill(SkillType.DODGE, difficulty, success=True)
    
    def on_creature_killed(
        self,
        killer: Creature,
        victim: Creature,
        location: Optional[Tuple[float, float]] = None
    ):
        """
        Called when a creature is killed.
        
        Args:
            killer: The creature that got the kill
            victim: The creature that died
            location: Location of the kill
        """
        # Calculate power differential for achievement tracking
        killer_power = killer.stats.attack + killer.stats.defense + killer.stats.speed
        victim_power = victim.stats.attack + victim.stats.defense + victim.stats.speed
        power_diff = victim_power / max(killer_power, 1)
        
        # Check if this is revenge
        is_revenge = killer.relationships.has_relationship(
            victim.creature_id,
            RelationshipType.REVENGE_TARGET
        )
        
        # Record kill in killer's history
        killer.history.record_kill(
            victim.creature_id,
            victim.name,
            power_differential=power_diff,
            location=location,
            was_revenge=is_revenge
        )
        
        # Record death in victim's history
        killer_name = killer.name if killer else "unknown"
        killer_id = killer.creature_id if killer else None
        victim.history.record_death(killer_id, f"Killed by {killer_name}", location)
        
        # Update relationships
        if is_revenge:
            killer.relationships.record_revenge_completed(victim.creature_id)
        else:
            killer.relationships.record_defeated(victim.creature_id)
        
        # Notify family members of the victim
        family = victim.relationships.get_family()
        for family_rel in family:
            # Each family member should now want revenge
            # Note: This would need to be called on the actual creature object, not the relationship
            # In a real implementation, we'd need to look up the creature by ID
            pass
    
    def on_breeding(
        self,
        parent1: Creature,
        parent2: Creature,
        offspring: Creature
    ):
        """
        Called when breeding occurs.
        
        Args:
            parent1: First parent
            parent2: Second parent
            offspring: The new offspring
        """
        # Record in parents' history
        parent1.history.record_offspring_born(offspring.creature_id, offspring.name)
        parent2.history.record_offspring_born(offspring.creature_id, offspring.name)
        
        # Set up family relationships
        offspring.relationships.add_relationship(
            parent1.creature_id,
            RelationshipType.PARENT,
            strength=1.0
        )
        offspring.relationships.add_relationship(
            parent2.creature_id,
            RelationshipType.PARENT,
            strength=1.0
        )
        
        parent1.relationships.add_relationship(
            offspring.creature_id,
            RelationshipType.CHILD,
            strength=1.0
        )
        parent2.relationships.add_relationship(
            offspring.creature_id,
            RelationshipType.CHILD,
            strength=1.0
        )
        
        # Inherit personality
        offspring.personality = type(parent1.personality).inherit(
            parent1.personality,
            parent2.personality,
            mutation_rate=0.15
        )
    
    def on_battle_end(self, survivors: List[Creature]):
        """
        Called when battle ends.
        
        Args:
            survivors: Creatures that survived
        """
        for creature in survivors:
            # Record battle victory
            creature.history.record_battle_victory()
            
            # Update skill decay for all skills
            creature.skills.update_decay()
            
            # Update relationship decay
            creature.relationships.update_decay()
