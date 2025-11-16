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
from ..models.relationship_metrics import (
    CooperativeBehaviorSystem,
    DecisionContext,
    AgentSocialState
)


class LivingWorldBattleEnhancer:
    """
    Enhances battle system with living world features.
    
    Provides hooks for integrating history, skills, personality, and relationships
    into combat calculations and decision making. Now includes cooperative behaviors.
    """
    
    def __init__(self, battle_system):
        """
        Initialize the enhancer.
        
        Args:
            battle_system: The battle system to enhance
        """
        self.battle = battle_system
        self.combat_started = {}  # Track who started combat with whom
        self.cooperative_system = CooperativeBehaviorSystem()
    
    def update_social_states(self, creatures: List[Creature]):
        """
        Update social state for all creatures based on current battle context.
        
        Args:
            creatures: All creatures in the battle
        """
        for creature in creatures:
            # Update hunger level (normalized 0-1)
            creature.social_state.hunger_level = creature.hunger / creature.max_hunger
            
            # Update health level (normalized 0-1)
            creature.social_state.health_level = creature.stats.hp / creature.stats.max_hp if creature.stats.max_hp > 0 else 0
            
            # Update combat status
            creature.social_state.in_combat = True
            
            # Determine pack members (same strain fighting together)
            creature.social_state.current_pack = [
                c.creature_id for c in creatures
                if c.strain_id == creature.strain_id and c.creature_id != creature.creature_id and c.stats.hp > 0
            ]
    
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
        
        # Update social states for all creatures
        self.update_social_states(creatures)
    
    def evaluate_food_sharing(
        self,
        giver: Creature,
        receiver: Creature,
        food_amount: float
    ) -> Tuple[bool, float]:
        """
        Evaluate whether a creature should share food.
        
        Args:
            giver: Creature that has food
            receiver: Creature that might receive food
            food_amount: Amount of food giver has
            
        Returns:
            (should_share, amount_to_share)
        """
        # Get or create relationship
        rel = giver.relationships.get_relationship(receiver.creature_id)
        if not rel:
            return False, 0.0
        
        # Create decision context
        context = DecisionContext(
            actor_id=giver.creature_id,
            target_id=receiver.creature_id,
            actor_traits=giver.social_traits,
            target_traits=receiver.social_traits,
            metrics=rel.metrics,
            actor_state=giver.social_state,
            target_state=receiver.social_state
        )
        
        # Evaluate sharing decision
        should_share, amount = self.cooperative_system.evaluate_food_sharing(context, food_amount)
        
        if should_share:
            # Record the cooperative behavior
            rel.record_cooperative_behavior("food_shared")
            giver.history.add_custom_event(
                "food_shared",
                f"Shared food with {receiver.name}"
            )
            self.cooperative_system.record_behavior(giver.creature_id, "food_shared")
        
        return should_share, amount
    
    def evaluate_join_fight(
        self,
        potential_ally: Creature,
        creature_in_fight: Creature,
        threat_level: float
    ) -> Tuple[bool, float]:
        """
        Evaluate whether a creature should join an ally's fight.
        
        Args:
            potential_ally: Creature considering joining
            creature_in_fight: Ally who is fighting
            threat_level: How dangerous the fight is (0-1)
            
        Returns:
            (should_join, commitment_level)
        """
        # Get or create relationship
        rel = potential_ally.relationships.get_relationship(creature_in_fight.creature_id)
        if not rel:
            # No relationship, unlikely to help unless pack member
            if creature_in_fight.creature_id not in potential_ally.social_state.current_pack:
                return False, 0.0
            # Create pack relationship
            from ..models.relationship_metrics import create_pack_bond
            metrics = create_pack_bond(potential_ally.creature_id, creature_in_fight.creature_id)
            rel = potential_ally.relationships.add_relationship(
                creature_in_fight.creature_id,
                RelationshipType.ALLY,
                strength=0.6
            )
            rel.metrics = metrics
        
        # Create decision context
        context = DecisionContext(
            actor_id=potential_ally.creature_id,
            target_id=creature_in_fight.creature_id,
            actor_traits=potential_ally.social_traits,
            target_traits=creature_in_fight.social_traits,
            metrics=rel.metrics,
            actor_state=potential_ally.social_state,
            target_state=creature_in_fight.social_state
        )
        
        # Evaluate join decision
        should_join, commitment = self.cooperative_system.evaluate_join_fight(context, threat_level)
        
        if should_join:
            # Record the cooperative behavior
            rel.record_cooperative_behavior("fought_together")
            potential_ally.relationships.record_fought_together(creature_in_fight.creature_id)
            self.cooperative_system.record_behavior(potential_ally.creature_id, "joined_fight")
        
        return should_join, commitment
    
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
        is_critical: bool = False,
        allies_present: Optional[List[Creature]] = None
    ) -> float:
        """
        Calculate final damage with all living world modifiers.
        
        Args:
            attacker: Attacking creature
            defender: Defending creature
            base_damage: Base damage before modifiers
            is_critical: Whether this is a critical hit
            allies_present: List of allies fighting alongside attacker
            
        Returns:
            Modified damage value
        """
        damage = base_damage
        
        # Skill modifier for attack
        attack_skill = attacker.skills.get_skill(SkillType.MELEE_ATTACK)
        skill_modifier = attack_skill.get_performance_modifier()
        damage *= skill_modifier
        
        # Count allies and family members
        allies_count = 0
        family_count = 0
        if allies_present:
            for ally in allies_present:
                if ally.creature_id != attacker.creature_id and ally.stats.hp > 0:
                    allies_count += 1
                    # Check if family member
                    rel = attacker.relationships.get_relationship(ally.creature_id)
                    if rel and rel.relationship_type in [
                        RelationshipType.PARENT,
                        RelationshipType.CHILD,
                        RelationshipType.SIBLING
                    ]:
                        family_count += 1
        
        # Group combat bonus from cooperative behavior system
        group_bonus = self.cooperative_system.calculate_group_combat_bonus(
            attacker.social_traits,
            allies_count,
            family_count
        )
        damage *= group_bonus
        
        # Personality modifiers
        has_allies = allies_count > 0
        has_family = family_count > 0
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
        hit: bool = True,
        location: Optional[Tuple[float, float]] = None
    ):
        """
        Called when an attack is made.
        
        Args:
            attacker: Attacking creature
            defender: Defending creature
            damage: Damage dealt
            was_critical: Whether it was a critical hit
            hit: Whether the attack hit
            location: Where the attack occurred
        """
        if hit:
            # Record in history
            attacker.history.record_attack(defender.creature_id, damage, was_critical)
            defender.history.record_damage_taken(attacker.creature_id, damage)
            
            # Record injury in tracker
            self.on_damage_dealt(
                attacker=attacker,
                defender=defender,
                damage=damage,
                damage_type="physical",
                was_critical=was_critical,
                location=location
            )
            
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
    
    def on_damage_dealt(
        self,
        attacker: Creature,
        defender: Creature,
        damage: float,
        damage_type: str = "physical",
        was_critical: bool = False,
        location: Optional[Tuple[float, float]] = None
    ):
        """
        Called when damage is dealt to track injuries.
        
        Args:
            attacker: Creature dealing damage
            defender: Creature receiving damage
            damage: Amount of damage dealt
            damage_type: Type of damage (physical, special, starvation, etc.)
            was_critical: Whether this was a critical hit
            location: Where the damage occurred
        """
        from ..models.injury_tracker import DamageType
        
        # Map string to DamageType enum
        damage_type_map = {
            'physical': DamageType.PHYSICAL,
            'special': DamageType.SPECIAL,
            'starvation': DamageType.STARVATION,
            'poison': DamageType.POISON,
            'burning': DamageType.BURNING,
            'environmental': DamageType.ENVIRONMENTAL
        }
        dt = damage_type_map.get(damage_type.lower(), DamageType.PHYSICAL)
        
        # Record injury in defender's tracker
        health_before = defender.stats.hp + damage  # HP before damage was applied
        health_after = defender.stats.hp
        
        defender.injury_tracker.record_injury(
            attacker_id=attacker.creature_id,
            attacker_name=attacker.name,
            damage_type=dt,
            damage_amount=damage,
            health_before=health_before,
            health_after=health_after,
            was_critical=was_critical,
            location=location
        )
    
    def on_food_competition(
        self,
        pellet_id: str,
        competitors: List[Creature],
        winner: Creature,
        location: Optional[Tuple[float, float]] = None
    ):
        """
        Called when multiple creatures compete for the same food.
        
        Args:
            pellet_id: ID of the contested pellet
            competitors: List of creatures competing
            winner: Creature that won the competition
            location: Where the competition occurred
        """
        competitor_ids = [c.creature_id for c in competitors]
        
        # Record in each competitor's interaction tracker
        for creature in competitors:
            creature.interaction_tracker.record_food_competition(
                pellet_id=pellet_id,
                competitors=competitor_ids,
                winner_id=winner.creature_id,
                location=location
            )
    
    def on_pellet_targeted(
        self,
        pellet,
        creature: Creature,
        distance: float = 0.0,
        location: Optional[Tuple[float, float]] = None
    ):
        """
        Called when a creature targets a pellet.
        
        Args:
            pellet: The pellet being targeted
            creature: Creature targeting the pellet
            distance: Distance traveled to target
            location: Where targeting occurred
        """
        if hasattr(pellet, 'history') and pellet.history:
            pellet.history.record_targeted(
                creature_id=creature.creature_id,
                location=location,
                distance=distance
            )
    
    def on_pellet_avoided(
        self,
        pellet,
        creature: Creature,
        reason: str = "low palatability",
        location: Optional[Tuple[float, float]] = None
    ):
        """
        Called when a creature avoids a pellet.
        
        Args:
            pellet: The pellet being avoided
            creature: Creature avoiding the pellet
            reason: Why the pellet was avoided
            location: Where avoidance occurred
        """
        if hasattr(pellet, 'history') and pellet.history:
            pellet.history.record_avoided(
                creature_id=creature.creature_id,
                location=location,
                reason=reason
            )
    
    def on_pellet_eaten(
        self,
        pellet,
        creature: Creature,
        location: Optional[Tuple[float, float]] = None
    ):
        """
        Called when a creature eats a pellet.
        
        Args:
            pellet: The pellet being eaten
            creature: Creature eating the pellet
            location: Where consumption occurred
        """
        if hasattr(pellet, 'history') and pellet.history:
            nutritional_value = pellet.get_nutritional_value()
            pellet.history.record_eaten(
                creature_id=creature.creature_id,
                creature_name=creature.name,
                location=location,
                nutritional_value=nutritional_value
            )
