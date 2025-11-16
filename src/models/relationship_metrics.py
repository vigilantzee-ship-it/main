"""
Relationship Metrics and Cooperative Behavior System.

Implements comprehensive social dynamics including:
- Relationship metrics (affinity, trust, kinship, rank)
- Agent traits (altruistic, dominant, follower, etc.)
- Cooperative behaviors (food sharing, coordinated fighting, following alpha, etc.)
- Emergent pack/family/coalition dynamics
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time
import random


class SocialTrait(Enum):
    """Social personality traits that affect cooperative behavior."""
    ALTRUISTIC = "altruistic"  # Willing to share and help others
    SELFISH = "selfish"  # Prioritizes own needs
    DOMINANT = "dominant"  # Seeks leadership, alpha behavior
    SUBMISSIVE = "submissive"  # Defers to others, follows
    COOPERATIVE = "cooperative"  # Works well in groups
    INDEPENDENT = "independent"  # Prefers solo action
    PROTECTIVE = "protective"  # Guards family/pack
    AGGRESSIVE = "aggressive"  # Quick to fight, less cooperative


@dataclass
class RelationshipMetrics:
    """
    Quantitative metrics for a relationship between two agents.
    
    Attributes:
        affinity: Emotional bond strength (0-1), affects cooperation willingness
        trust: Reliability and dependability (0-1), affects food sharing
        kinship: Genetic relatedness (0-1), 1.0 for parent/child/sibling
        rank: Relative social dominance (-1 to 1), positive if this creature is dominant
    """
    affinity: float = 0.5  # Emotional bond
    trust: float = 0.5  # Reliability
    kinship: float = 0.0  # Genetic relatedness
    rank: float = 0.0  # Relative dominance
    
    def __post_init__(self):
        """Validate metrics are in valid ranges."""
        self.affinity = max(0.0, min(1.0, self.affinity))
        self.trust = max(0.0, min(1.0, self.trust))
        self.kinship = max(0.0, min(1.0, self.kinship))
        self.rank = max(-1.0, min(1.0, self.rank))
    
    def get_cooperation_score(self) -> float:
        """
        Calculate overall cooperation likelihood.
        
        Returns:
            Score 0-1 indicating how likely cooperation is
        """
        # Kinship has strongest effect, followed by affinity and trust
        return (self.kinship * 0.5 + self.affinity * 0.3 + self.trust * 0.2)
    
    def decay(self, amount: float = 0.01):
        """
        Decay non-kinship metrics over time without interaction.
        
        Args:
            amount: Amount to decay (default 0.01)
        """
        # Kinship never decays (genetic relationship is permanent)
        self.affinity = max(0.0, self.affinity - amount)
        self.trust = max(0.0, self.trust - amount)
        # Rank drifts toward neutral
        if self.rank > 0:
            self.rank = max(0.0, self.rank - amount)
        elif self.rank < 0:
            self.rank = min(0.0, self.rank + amount)
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'affinity': self.affinity,
            'trust': self.trust,
            'kinship': self.kinship,
            'rank': self.rank
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'RelationshipMetrics':
        """Deserialize from dictionary."""
        return RelationshipMetrics(**data)


@dataclass
class AgentTraits:
    """
    Social personality traits for an agent/creature.
    
    Attributes:
        altruism: Willingness to help others (0-1)
        dominance: Leadership and alpha tendencies (0-1)
        cooperation: Teamwork preference (0-1)
        protectiveness: Family/pack protection drive (0-1)
        independence: Preference for solo vs group action (0-1, high=solo)
    """
    altruism: float = 0.5
    dominance: float = 0.5
    cooperation: float = 0.5
    protectiveness: float = 0.5
    independence: float = 0.5
    
    def __post_init__(self):
        """Validate traits are in valid ranges."""
        self.altruism = max(0.0, min(1.0, self.altruism))
        self.dominance = max(0.0, min(1.0, self.dominance))
        self.cooperation = max(0.0, min(1.0, self.cooperation))
        self.protectiveness = max(0.0, min(1.0, self.protectiveness))
        self.independence = max(0.0, min(1.0, self.independence))
    
    @staticmethod
    def random() -> 'AgentTraits':
        """Generate random traits."""
        return AgentTraits(
            altruism=random.uniform(0.2, 0.8),
            dominance=random.uniform(0.2, 0.8),
            cooperation=random.uniform(0.2, 0.8),
            protectiveness=random.uniform(0.2, 0.8),
            independence=random.uniform(0.2, 0.8)
        )
    
    @staticmethod
    def inherit(parent1: 'AgentTraits', parent2: 'AgentTraits', mutation_rate: float = 0.1) -> 'AgentTraits':
        """
        Inherit traits from two parents with mutation.
        
        Args:
            parent1: First parent's traits
            parent2: Second parent's traits
            mutation_rate: Chance of mutation (0-1)
            
        Returns:
            New traits inherited from parents
        """
        def inherit_trait(t1: float, t2: float) -> float:
            # Average parents with some random variation
            base = (t1 + t2) / 2
            if random.random() < mutation_rate:
                base += random.uniform(-0.2, 0.2)
            return max(0.0, min(1.0, base))
        
        return AgentTraits(
            altruism=inherit_trait(parent1.altruism, parent2.altruism),
            dominance=inherit_trait(parent1.dominance, parent2.dominance),
            cooperation=inherit_trait(parent1.cooperation, parent2.cooperation),
            protectiveness=inherit_trait(parent1.protectiveness, parent2.protectiveness),
            independence=inherit_trait(parent1.independence, parent2.independence)
        )
    
    def get_description(self) -> str:
        """Get human-readable description of traits."""
        desc = []
        if self.altruism > 0.7:
            desc.append("altruistic")
        elif self.altruism < 0.3:
            desc.append("selfish")
        
        if self.dominance > 0.7:
            desc.append("dominant")
        elif self.dominance < 0.3:
            desc.append("submissive")
        
        if self.cooperation > 0.7:
            desc.append("cooperative")
        elif self.independence > 0.7:
            desc.append("independent")
        
        if self.protectiveness > 0.7:
            desc.append("protective")
        
        return ", ".join(desc) if desc else "balanced"
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'altruism': self.altruism,
            'dominance': self.dominance,
            'cooperation': self.cooperation,
            'protectiveness': self.protectiveness,
            'independence': self.independence
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'AgentTraits':
        """Deserialize from dictionary."""
        return AgentTraits(**data)


@dataclass
class SharedHistory:
    """
    Records history of interactions between two agents.
    
    Attributes:
        interactions: List of interaction timestamps and types
        cooperative_acts: Count of cooperative behaviors
        conflicts: Count of conflicts or betrayals
        food_shared: Times food was shared
        fought_together: Times fought as allies
    """
    interactions: List[Tuple[float, str]] = field(default_factory=list)
    cooperative_acts: int = 0
    conflicts: int = 0
    food_shared: int = 0
    fought_together: int = 0
    
    def record_interaction(self, interaction_type: str):
        """
        Record an interaction.
        
        Args:
            interaction_type: Type of interaction (e.g., "food_shared", "fought_together")
        """
        self.interactions.append((time.time(), interaction_type))
        
        # Update specific counters
        if interaction_type == "food_shared":
            self.food_shared += 1
            self.cooperative_acts += 1
        elif interaction_type == "fought_together":
            self.fought_together += 1
            self.cooperative_acts += 1
        elif interaction_type == "conflict":
            self.conflicts += 1
    
    def get_recent_interactions(self, since: float) -> List[Tuple[float, str]]:
        """
        Get interactions since a given time.
        
        Args:
            since: Timestamp to get interactions after
            
        Returns:
            List of recent interactions
        """
        return [(t, itype) for t, itype in self.interactions if t >= since]
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'interactions': self.interactions,
            'cooperative_acts': self.cooperative_acts,
            'conflicts': self.conflicts,
            'food_shared': self.food_shared,
            'fought_together': self.fought_together
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'SharedHistory':
        """Deserialize from dictionary."""
        return SharedHistory(**data)


@dataclass
class AgentSocialState:
    """
    Current social state and context for an agent.
    
    Attributes:
        current_pack: IDs of creatures in current pack/group
        current_alpha: ID of current pack leader (if any)
        hunger_level: Current hunger (0-1, 0=starving)
        health_level: Current health (0-1, 0=dead)
        in_combat: Whether currently fighting
        threatened: Whether feeling threatened
    """
    current_pack: List[str] = field(default_factory=list)
    current_alpha: Optional[str] = None
    hunger_level: float = 1.0
    health_level: float = 1.0
    in_combat: bool = False
    threatened: bool = False
    
    def __post_init__(self):
        """Validate state values."""
        self.hunger_level = max(0.0, min(1.0, self.hunger_level))
        self.health_level = max(0.0, min(1.0, self.health_level))


@dataclass
class DecisionContext:
    """
    Context for making cooperative behavior decisions.
    
    Attributes:
        actor_id: ID of creature making decision
        target_id: ID of creature decision involves
        actor_traits: Social traits of actor
        target_traits: Social traits of target
        metrics: Relationship metrics between actor and target
        actor_state: Current state of actor
        target_state: Current state of target
    """
    actor_id: str
    target_id: str
    actor_traits: AgentTraits
    target_traits: AgentTraits
    metrics: RelationshipMetrics
    actor_state: AgentSocialState
    target_state: AgentSocialState


class CooperativeBehaviorSystem:
    """
    System for evaluating and executing cooperative behaviors.
    
    Handles:
    - Food sharing decisions
    - Fight coordination
    - Alpha following
    - Group hunting/defense
    - Parental care
    """
    
    def __init__(self):
        """Initialize cooperative behavior system."""
        self.behavior_history: Dict[str, List[str]] = {}  # Track behaviors per agent
    
    def evaluate_food_sharing(
        self,
        context: DecisionContext,
        food_amount: float
    ) -> Tuple[bool, float]:
        """
        Evaluate whether to share food and how much.
        
        Args:
            context: Decision context
            food_amount: Amount of food actor has
            
        Returns:
            (should_share, amount_to_share)
        """
        # Don't share if starving
        if context.actor_state.hunger_level < 0.3:
            return False, 0.0
        
        # Calculate base willingness from traits and metrics
        willingness = (
            context.actor_traits.altruism * 0.4 +
            context.metrics.kinship * 0.4 +
            context.metrics.affinity * 0.2
        )
        
        # Boost for family (kinship)
        if context.metrics.kinship > 0.8:
            willingness += 0.2
        
        # Reduce if target is well-fed
        if context.target_state.hunger_level > 0.7:
            willingness *= 0.5
        
        # Increase if target is starving
        if context.target_state.hunger_level < 0.3:
            willingness *= 1.5
        
        # Decide based on willingness threshold
        should_share = willingness > 0.6
        
        if should_share:
            # Amount depends on own hunger and relationship
            max_share = min(food_amount * 0.5, food_amount - 30)  # Keep some for self
            share_ratio = willingness * context.actor_traits.altruism
            amount = max_share * share_ratio
            return True, max(0.0, amount)
        
        return False, 0.0
    
    def evaluate_join_fight(
        self,
        context: DecisionContext,
        threat_level: float
    ) -> Tuple[bool, float]:
        """
        Evaluate whether to join an ally's fight.
        
        Args:
            context: Decision context
            threat_level: How dangerous the fight is (0-1)
            
        Returns:
            (should_join, commitment_level)
        """
        # Don't join if too weak
        if context.actor_state.health_level < 0.3:
            return False, 0.0
        
        # Calculate willingness based on relationship and traits
        willingness = (
            context.actor_traits.cooperation * 0.3 +
            context.actor_traits.protectiveness * 0.3 +
            context.metrics.affinity * 0.2 +
            context.metrics.kinship * 0.2
        )
        
        # Strong boost for family
        if context.metrics.kinship > 0.8:
            willingness += 0.3
        
        # Boost for pack members
        if context.target_id in context.actor_state.current_pack:
            willingness += 0.2
        
        # Reduce based on threat level and independence
        willingness *= (1.0 - threat_level * 0.3)
        willingness *= (1.0 - context.actor_traits.independence * 0.3)
        
        should_join = willingness > 0.5
        commitment = min(1.0, willingness) if should_join else 0.0
        
        return should_join, commitment
    
    def evaluate_follow_alpha(
        self,
        context: DecisionContext
    ) -> Tuple[bool, float]:
        """
        Evaluate whether to follow an alpha/leader.
        
        Args:
            context: Decision context
            
        Returns:
            (should_follow, loyalty_level)
        """
        # Check if target is dominant enough to be alpha
        if context.target_traits.dominance < 0.6:
            return False, 0.0
        
        # Calculate following tendency
        follow_tendency = (
            (1.0 - context.actor_traits.dominance) * 0.4 +  # Submissive creatures follow more
            context.actor_traits.cooperation * 0.3 +
            context.metrics.affinity * 0.2 +
            (1.0 - context.actor_traits.independence) * 0.1
        )
        
        # Boost if there's rank difference (target is dominant)
        if context.metrics.rank < -0.3:  # Target is more dominant
            follow_tendency += 0.2
        
        # Family members might follow despite being dominant themselves
        if context.metrics.kinship > 0.8:
            follow_tendency += 0.15
        
        should_follow = follow_tendency > 0.5
        loyalty = min(1.0, follow_tendency) if should_follow else 0.0
        
        return should_follow, loyalty
    
    def evaluate_group_hunting(
        self,
        actor_traits: AgentTraits,
        pack_members: List[str],
        pack_size: int
    ) -> Tuple[bool, float]:
        """
        Evaluate participation in group hunting.
        
        Args:
            actor_traits: Actor's social traits
            pack_members: IDs of pack members
            pack_size: Size of hunting pack
            
        Returns:
            (should_participate, coordination_bonus)
        """
        # Independent creatures prefer solo hunting
        if actor_traits.independence > 0.7:
            return False, 0.0
        
        # Calculate participation willingness
        participation = (
            actor_traits.cooperation * 0.5 +
            (1.0 - actor_traits.independence) * 0.3 +
            actor_traits.dominance * 0.2  # Dominant creatures like leading hunts
        )
        
        # Larger packs are more appealing
        pack_bonus = min(0.3, pack_size * 0.05)
        participation += pack_bonus
        
        should_participate = participation > 0.5
        
        # Coordination bonus based on cooperation trait
        coordination_bonus = actor_traits.cooperation * 0.3 if should_participate else 0.0
        
        return should_participate, coordination_bonus
    
    def evaluate_parental_care(
        self,
        context: DecisionContext,
        offspring_need: float
    ) -> Tuple[bool, float]:
        """
        Evaluate parental care behavior.
        
        Args:
            context: Decision context (parent->offspring)
            offspring_need: How much the offspring needs care (0-1)
            
        Returns:
            (should_care, care_intensity)
        """
        # Only provide care to offspring (high kinship)
        if context.metrics.kinship < 0.8:
            return False, 0.0
        
        # Calculate care intensity
        care_intensity = (
            context.actor_traits.protectiveness * 0.5 +
            context.actor_traits.altruism * 0.3 +
            offspring_need * 0.2
        )
        
        # Reduce if parent is weak
        if context.actor_state.health_level < 0.3:
            care_intensity *= 0.5
        
        # Reduce if parent is starving (can't care if dying)
        if context.actor_state.hunger_level < 0.2:
            care_intensity *= 0.3
        
        should_care = care_intensity > 0.4
        
        return should_care, min(1.0, care_intensity)
    
    def calculate_group_combat_bonus(
        self,
        actor_traits: AgentTraits,
        allies_present: int,
        family_present: int
    ) -> float:
        """
        Calculate combat bonus from group fighting.
        
        Args:
            actor_traits: Actor's social traits
            allies_present: Number of allies fighting alongside
            family_present: Number of family members present
            
        Returns:
            Damage multiplier (1.0 = no bonus)
        """
        if allies_present == 0 and family_present == 0:
            return 1.0
        
        # Base bonus from cooperation trait
        base_bonus = actor_traits.cooperation * 0.15
        
        # Additional bonus for each ally
        ally_bonus = min(0.15, allies_present * 0.05)
        
        # Extra bonus for family
        family_bonus = min(0.20, family_present * 0.08)
        
        total_bonus = base_bonus + ally_bonus + family_bonus
        
        return 1.0 + total_bonus
    
    def record_behavior(self, actor_id: str, behavior_type: str):
        """
        Record that a cooperative behavior occurred.
        
        Args:
            actor_id: ID of actor performing behavior
            behavior_type: Type of behavior (e.g., "food_shared", "joined_fight")
        """
        if actor_id not in self.behavior_history:
            self.behavior_history[actor_id] = []
        self.behavior_history[actor_id].append(behavior_type)


# Utility functions for creating and managing relationships

def create_family_bond(parent_id: str, child_id: str) -> RelationshipMetrics:
    """
    Create relationship metrics for parent-child bond.
    
    Args:
        parent_id: ID of parent
        child_id: ID of child
        
    Returns:
        RelationshipMetrics with high kinship
    """
    return RelationshipMetrics(
        affinity=0.9,
        trust=0.9,
        kinship=1.0,  # Direct family
        rank=0.0  # No dominance in family (at creation)
    )


def create_sibling_bond(sibling1_id: str, sibling2_id: str) -> RelationshipMetrics:
    """
    Create relationship metrics for sibling bond.
    
    Args:
        sibling1_id: ID of first sibling
        sibling2_id: ID of second sibling
        
    Returns:
        RelationshipMetrics with high kinship
    """
    return RelationshipMetrics(
        affinity=0.8,
        trust=0.8,
        kinship=1.0,  # Siblings share parents
        rank=0.0
    )


def create_pack_bond(member1_id: str, member2_id: str) -> RelationshipMetrics:
    """
    Create relationship metrics for pack members.
    
    Args:
        member1_id: ID of first pack member
        member2_id: ID of second pack member
        
    Returns:
        RelationshipMetrics for pack allies
    """
    return RelationshipMetrics(
        affinity=0.6,
        trust=0.6,
        kinship=0.0,  # Not family
        rank=0.0  # Equal rank initially
    )


def update_metrics_after_cooperation(
    metrics: RelationshipMetrics,
    behavior_type: str
) -> RelationshipMetrics:
    """
    Update relationship metrics after cooperative behavior.
    
    Args:
        metrics: Current metrics
        behavior_type: Type of cooperative behavior
        
    Returns:
        Updated metrics
    """
    if behavior_type == "food_shared":
        metrics.trust += 0.05
        metrics.affinity += 0.03
    elif behavior_type == "fought_together":
        metrics.affinity += 0.05
        metrics.trust += 0.02
    elif behavior_type == "protected":
        metrics.affinity += 0.08
        metrics.trust += 0.05
    
    # Ensure bounds
    metrics.affinity = min(1.0, metrics.affinity)
    metrics.trust = min(1.0, metrics.trust)
    
    return metrics


def generate_social_traits() -> AgentTraits:
    """
    Generate random social traits for a new agent.
    
    Returns:
        Random AgentTraits
    """
    return AgentTraits.random()
