"""
Combat Memory System - Track combat encounters and past interactions.

Creatures remember who attacked them, who they've fought, and use this
information to make smarter targeting decisions.
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
import time


@dataclass
class CombatEncounter:
    """
    Records a single combat encounter between two creatures.
    
    Attributes:
        target_id: ID of the creature we fought
        timestamp: When the encounter occurred
        damage_dealt: Total damage we dealt to them
        damage_received: Total damage they dealt to us
        was_killed: Whether we killed them
        killed_us: Whether they killed us (for tracking revenge after respawn)
        times_fought: Number of times we've fought this creature
    """
    target_id: str
    timestamp: float
    damage_dealt: int = 0
    damage_received: int = 0
    was_killed: bool = False
    killed_us: bool = False
    times_fought: int = 1
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'target_id': self.target_id,
            'timestamp': self.timestamp,
            'damage_dealt': self.damage_dealt,
            'damage_received': self.damage_received,
            'was_killed': self.was_killed,
            'killed_us': self.killed_us,
            'times_fought': self.times_fought
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'CombatEncounter':
        """Deserialize from dictionary."""
        return CombatEncounter(**data)


class CombatMemory:
    """
    Manages a creature's combat memory and targeting preferences.
    
    Tracks who attacked us recently, who we've fought before, and uses
    this to make smarter targeting decisions (revenge, threat assessment, etc.)
    """
    
    def __init__(self, creature_id: str):
        """
        Initialize combat memory.
        
        Args:
            creature_id: ID of the creature who owns this memory
        """
        self.creature_id = creature_id
        
        # Recent attackers (for revenge/threat assessment)
        self.recent_attackers: List[str] = []  # IDs of creatures who attacked us recently
        self.attacker_damage: Dict[str, int] = {}  # Total damage received from each attacker
        
        # Combat encounters (full history)
        self.encounters: Dict[str, CombatEncounter] = {}
        
        # Threat assessment
        self.threat_level: Dict[str, float] = {}  # Assessed threat (0-1) of each creature
        
        # Last target (to prevent rapid switching)
        self.last_target_id: Optional[str] = None
        self.last_target_time: float = 0.0
        
        # Allies we've fought alongside
        self.fought_alongside: Set[str] = set()
    
    def record_attacked_by(self, attacker_id: str, damage: int):
        """
        Record being attacked by another creature.
        
        Args:
            attacker_id: ID of the attacker
            damage: Damage received
        """
        current_time = time.time()
        
        # Add to recent attackers if not already there
        if attacker_id not in self.recent_attackers:
            self.recent_attackers.append(attacker_id)
        
        # Update damage tracking
        self.attacker_damage[attacker_id] = self.attacker_damage.get(attacker_id, 0) + damage
        
        # Update or create encounter
        if attacker_id in self.encounters:
            encounter = self.encounters[attacker_id]
            encounter.damage_received += damage
            encounter.timestamp = current_time
        else:
            encounter = CombatEncounter(
                target_id=attacker_id,
                timestamp=current_time,
                damage_received=damage
            )
            self.encounters[attacker_id] = encounter
        
        # Update threat assessment (recent attackers are high threat)
        self._update_threat_level(attacker_id, damage)
    
    def record_attacked(self, target_id: str, damage: int, killed: bool = False):
        """
        Record attacking another creature.
        
        Args:
            target_id: ID of the target
            damage: Damage dealt
            killed: Whether we killed them
        """
        current_time = time.time()
        
        # Update or create encounter
        if target_id in self.encounters:
            encounter = self.encounters[target_id]
            encounter.damage_dealt += damage
            encounter.timestamp = current_time
            if killed:
                encounter.was_killed = True
        else:
            encounter = CombatEncounter(
                target_id=target_id,
                timestamp=current_time,
                damage_dealt=damage,
                was_killed=killed
            )
            self.encounters[target_id] = encounter
        
        # Track as last target
        self.last_target_id = target_id
        self.last_target_time = current_time
    
    def record_killed_by(self, killer_id: str):
        """
        Record being killed by another creature.
        
        Args:
            killer_id: ID of the killer
        """
        if killer_id in self.encounters:
            self.encounters[killer_id].killed_us = True
        else:
            self.encounters[killer_id] = CombatEncounter(
                target_id=killer_id,
                timestamp=time.time(),
                killed_us=True
            )
        
        # Maximum threat
        self.threat_level[killer_id] = 1.0
    
    def record_fought_alongside(self, ally_id: str):
        """
        Record fighting alongside another creature.
        
        Args:
            ally_id: ID of the ally
        """
        self.fought_alongside.add(ally_id)
    
    def _update_threat_level(self, creature_id: str, recent_damage: int):
        """
        Update threat assessment for a creature.
        
        Args:
            creature_id: ID of the creature
            recent_damage: Recent damage received from them
        """
        # Base threat on damage dealt
        total_damage = self.attacker_damage.get(creature_id, 0)
        
        # Normalize to 0-1 (assuming 100 damage = high threat)
        damage_threat = min(1.0, total_damage / 100.0)
        
        # Recent attackers are higher threat
        recency_bonus = 0.3 if creature_id in self.recent_attackers[:3] else 0.0
        
        self.threat_level[creature_id] = min(1.0, damage_threat + recency_bonus)
    
    def get_threat_level(self, creature_id: str) -> float:
        """
        Get assessed threat level of a creature.
        
        Args:
            creature_id: ID of the creature
            
        Returns:
            Threat level (0-1, higher = more threatening)
        """
        return self.threat_level.get(creature_id, 0.0)
    
    def get_most_threatening(self, candidate_ids: List[str]) -> Optional[str]:
        """
        Get the most threatening creature from a list.
        
        Args:
            candidate_ids: List of creature IDs to choose from
            
        Returns:
            ID of most threatening creature, or None if list is empty
        """
        if not candidate_ids:
            return None
        
        return max(candidate_ids, key=lambda cid: self.get_threat_level(cid))
    
    def get_recent_attackers(self, max_age: float = 10.0) -> List[str]:
        """
        Get creatures who attacked us recently.
        
        Args:
            max_age: Maximum age in seconds to consider "recent"
            
        Returns:
            List of creature IDs who attacked us recently
        """
        current_time = time.time()
        recent = []
        
        for attacker_id in self.recent_attackers:
            if attacker_id in self.encounters:
                encounter = self.encounters[attacker_id]
                if current_time - encounter.timestamp <= max_age:
                    recent.append(attacker_id)
        
        return recent
    
    def should_prioritize_revenge(self, target_id: str) -> bool:
        """
        Check if we should prioritize revenge against a target.
        
        Args:
            target_id: ID of potential target
            
        Returns:
            True if this is a priority revenge target
        """
        if target_id not in self.encounters:
            return False
        
        encounter = self.encounters[target_id]
        
        # Prioritize if they killed us or dealt significant damage recently
        if encounter.killed_us:
            return True
        
        if encounter.damage_received > 50:  # Significant damage threshold
            current_time = time.time()
            if current_time - encounter.timestamp < 30.0:  # Within last 30 seconds
                return True
        
        return False
    
    def should_stick_with_target(self, target_id: str, min_duration: float = 2.0) -> bool:
        """
        Check if we should stick with current target to prevent rapid switching.
        
        Args:
            target_id: ID of current target
            min_duration: Minimum time to stick with target
            
        Returns:
            True if we should keep this target
        """
        if self.last_target_id != target_id:
            return False
        
        current_time = time.time()
        time_on_target = current_time - self.last_target_time
        
        return time_on_target < min_duration
    
    def clear_recent_memory(self):
        """Clear recent attacker memory (for periodic cleanup)."""
        self.recent_attackers.clear()
        self.attacker_damage.clear()
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'creature_id': self.creature_id,
            'recent_attackers': self.recent_attackers,
            'attacker_damage': self.attacker_damage,
            'encounters': {
                target_id: enc.to_dict()
                for target_id, enc in self.encounters.items()
            },
            'threat_level': self.threat_level,
            'last_target_id': self.last_target_id,
            'last_target_time': self.last_target_time,
            'fought_alongside': list(self.fought_alongside)
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'CombatMemory':
        """Deserialize from dictionary."""
        memory = CombatMemory(data['creature_id'])
        memory.recent_attackers = data.get('recent_attackers', [])
        memory.attacker_damage = data.get('attacker_damage', {})
        memory.threat_level = data.get('threat_level', {})
        memory.last_target_id = data.get('last_target_id')
        memory.last_target_time = data.get('last_target_time', 0.0)
        memory.fought_alongside = set(data.get('fought_alongside', []))
        
        # Restore encounters
        for target_id, enc_data in data.get('encounters', {}).items():
            memory.encounters[target_id] = CombatEncounter.from_dict(enc_data)
        
        return memory
