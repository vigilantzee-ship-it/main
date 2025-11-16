"""
Injury Record System - Track detailed creature injuries and damage.

This module provides comprehensive tracking of every damage event, health history,
near-death experiences, and critical hits to create detailed injury narratives.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time


class DamageType(Enum):
    """Types of damage that can be inflicted."""
    PHYSICAL = "physical"
    SPECIAL = "special"
    STARVATION = "starvation"
    POISON = "poison"
    BURNING = "burning"
    ENVIRONMENTAL = "environmental"


@dataclass
class InjuryRecord:
    """
    Records a single injury/damage event.
    
    Attributes:
        timestamp: When the injury occurred
        attacker_id: ID of the attacker (None for environmental damage)
        attacker_name: Name of the attacker
        damage_type: Type of damage inflicted
        damage_amount: Amount of damage taken
        health_before: HP before damage
        health_after: HP after damage
        was_critical: Whether this was a critical hit
        location: Optional (x, y) coordinates where injury occurred
    """
    timestamp: float
    attacker_id: Optional[str]
    attacker_name: str
    damage_type: DamageType
    damage_amount: float
    health_before: float
    health_after: float
    was_critical: bool = False
    location: Optional[Tuple[float, float]] = None
    
    def health_percentage_before(self, max_hp: float) -> float:
        """Get health percentage before damage."""
        return (self.health_before / max_hp * 100) if max_hp > 0 else 0.0
    
    def health_percentage_after(self, max_hp: float) -> float:
        """Get health percentage after damage."""
        return (self.health_after / max_hp * 100) if max_hp > 0 else 0.0
    
    def was_near_death(self, max_hp: float, threshold: float = 0.1) -> bool:
        """Check if this injury brought creature near death."""
        return self.health_percentage_after(max_hp) <= threshold * 100
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'timestamp': self.timestamp,
            'attacker_id': self.attacker_id,
            'attacker_name': self.attacker_name,
            'damage_type': self.damage_type.value,
            'damage_amount': self.damage_amount,
            'health_before': self.health_before,
            'health_after': self.health_after,
            'was_critical': self.was_critical,
            'location': self.location
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'InjuryRecord':
        """Deserialize from dictionary."""
        data_copy = data.copy()
        data_copy['damage_type'] = DamageType(data_copy['damage_type'])
        return InjuryRecord(**data_copy)


@dataclass
class AttackerStats:
    """
    Statistics for damage received from a specific attacker.
    
    Attributes:
        attacker_id: ID of the attacker
        attacker_name: Name of the attacker
        total_damage: Total damage received from this attacker
        hit_count: Number of times hit by this attacker
        critical_hits: Number of critical hits received
        near_death_hits: Number of hits that brought creature near death
        first_encounter: Timestamp of first damage from this attacker
        last_encounter: Timestamp of most recent damage
    """
    attacker_id: str
    attacker_name: str
    total_damage: float = 0.0
    hit_count: int = 0
    critical_hits: int = 0
    near_death_hits: int = 0
    first_encounter: Optional[float] = None
    last_encounter: Optional[float] = None
    
    def average_damage(self) -> float:
        """Calculate average damage per hit."""
        return self.total_damage / self.hit_count if self.hit_count > 0 else 0.0
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'attacker_id': self.attacker_id,
            'attacker_name': self.attacker_name,
            'total_damage': self.total_damage,
            'hit_count': self.hit_count,
            'critical_hits': self.critical_hits,
            'near_death_hits': self.near_death_hits,
            'first_encounter': self.first_encounter,
            'last_encounter': self.last_encounter
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'AttackerStats':
        """Deserialize from dictionary."""
        return AttackerStats(**data)


class InjuryTracker:
    """
    Comprehensive injury tracking system for a creature.
    
    Tracks all damage events, health history, near-death experiences,
    and provides detailed statistics about injuries sustained.
    """
    
    def __init__(self, creature_id: str, max_hp: float):
        """
        Initialize injury tracker.
        
        Args:
            creature_id: Unique identifier for the creature
            max_hp: Maximum HP of the creature
        """
        self.creature_id = creature_id
        self.max_hp = max_hp
        
        # All injury records
        self.injuries: List[InjuryRecord] = []
        
        # Statistics by attacker
        self.attacker_stats: Dict[str, AttackerStats] = {}
        
        # Statistics by damage type
        self.damage_by_type: Dict[DamageType, float] = {dt: 0.0 for dt in DamageType}
        
        # Near-death tracking
        self.near_death_count: int = 0
        self.near_death_threshold: float = 0.1  # 10% HP
        
        # Critical hit tracking
        self.critical_hits_received: int = 0
        
        # Starvation tracking
        self.starvation_damage: float = 0.0
        self.times_starved: int = 0
    
    def record_injury(
        self,
        attacker_id: Optional[str],
        attacker_name: str,
        damage_type: DamageType,
        damage_amount: float,
        health_before: float,
        health_after: float,
        was_critical: bool = False,
        location: Optional[Tuple[float, float]] = None
    ):
        """
        Record a new injury.
        
        Args:
            attacker_id: ID of the attacker (None for environmental)
            attacker_name: Name of the attacker
            damage_type: Type of damage
            damage_amount: Amount of damage taken
            health_before: HP before damage
            health_after: HP after damage
            was_critical: Whether this was a critical hit
            location: Where the injury occurred
        """
        # Create injury record
        injury = InjuryRecord(
            timestamp=time.time(),
            attacker_id=attacker_id,
            attacker_name=attacker_name,
            damage_type=damage_type,
            damage_amount=damage_amount,
            health_before=health_before,
            health_after=health_after,
            was_critical=was_critical,
            location=location
        )
        self.injuries.append(injury)
        
        # Update damage by type
        self.damage_by_type[damage_type] += damage_amount
        
        # Update starvation tracking
        if damage_type == DamageType.STARVATION:
            self.starvation_damage += damage_amount
            # Count distinct starvation events (when damage occurs)
            if damage_amount > 0:
                self.times_starved += 1
        
        # Update critical hit count
        if was_critical:
            self.critical_hits_received += 1
        
        # Check for near-death experience
        if injury.was_near_death(self.max_hp, self.near_death_threshold):
            self.near_death_count += 1
        
        # Update attacker statistics if applicable
        if attacker_id:
            if attacker_id not in self.attacker_stats:
                self.attacker_stats[attacker_id] = AttackerStats(
                    attacker_id=attacker_id,
                    attacker_name=attacker_name
                )
            
            stats = self.attacker_stats[attacker_id]
            stats.total_damage += damage_amount
            stats.hit_count += 1
            if was_critical:
                stats.critical_hits += 1
            if injury.was_near_death(self.max_hp, self.near_death_threshold):
                stats.near_death_hits += 1
            if stats.first_encounter is None:
                stats.first_encounter = injury.timestamp
            stats.last_encounter = injury.timestamp
    
    def get_total_damage_received(self) -> float:
        """Get total damage received from all sources."""
        return sum(injury.damage_amount for injury in self.injuries)
    
    def get_damage_by_attacker(self, attacker_id: str) -> float:
        """Get total damage received from a specific attacker."""
        if attacker_id in self.attacker_stats:
            return self.attacker_stats[attacker_id].total_damage
        return 0.0
    
    def get_most_dangerous_attacker(self) -> Optional[AttackerStats]:
        """Get the attacker who dealt the most damage."""
        if not self.attacker_stats:
            return None
        return max(self.attacker_stats.values(), key=lambda s: s.total_damage)
    
    def get_recent_injuries(self, count: int = 10) -> List[InjuryRecord]:
        """Get the most recent injuries."""
        return sorted(self.injuries, key=lambda i: i.timestamp, reverse=True)[:count]
    
    def get_injuries_by_type(self, damage_type: DamageType) -> List[InjuryRecord]:
        """Get all injuries of a specific damage type."""
        return [i for i in self.injuries if i.damage_type == damage_type]
    
    def get_critical_hits(self) -> List[InjuryRecord]:
        """Get all critical hits received."""
        return [i for i in self.injuries if i.was_critical]
    
    def get_near_death_injuries(self) -> List[InjuryRecord]:
        """Get all injuries that brought creature near death."""
        return [i for i in self.injuries if i.was_near_death(self.max_hp, self.near_death_threshold)]
    
    def get_survival_rate(self) -> float:
        """
        Calculate survival rate as percentage of time spent above near-death threshold.
        
        Returns:
            Percentage (0-100) representing overall health throughout encounters
        """
        if not self.injuries:
            return 100.0
        
        # Calculate average health percentage after each injury
        total_health_pct = sum(
            injury.health_percentage_after(self.max_hp) 
            for injury in self.injuries
        )
        return total_health_pct / len(self.injuries) if self.injuries else 100.0
    
    def get_damage_breakdown(self) -> Dict[str, float]:
        """
        Get damage breakdown by type as percentages.
        
        Returns:
            Dictionary mapping damage type names to percentage of total damage
        """
        total_damage = self.get_total_damage_received()
        if total_damage == 0:
            return {dt.value: 0.0 for dt in DamageType}
        
        return {
            dt.value: (self.damage_by_type[dt] / total_damage * 100)
            for dt in DamageType
        }
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'creature_id': self.creature_id,
            'max_hp': self.max_hp,
            'injuries': [i.to_dict() for i in self.injuries],
            'attacker_stats': {
                attacker_id: stats.to_dict() 
                for attacker_id, stats in self.attacker_stats.items()
            },
            'damage_by_type': {dt.value: dmg for dt, dmg in self.damage_by_type.items()},
            'near_death_count': self.near_death_count,
            'near_death_threshold': self.near_death_threshold,
            'critical_hits_received': self.critical_hits_received,
            'starvation_damage': self.starvation_damage,
            'times_starved': self.times_starved
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'InjuryTracker':
        """Deserialize from dictionary."""
        tracker = InjuryTracker(data['creature_id'], data['max_hp'])
        tracker.injuries = [InjuryRecord.from_dict(i) for i in data['injuries']]
        tracker.attacker_stats = {
            attacker_id: AttackerStats.from_dict(stats)
            for attacker_id, stats in data['attacker_stats'].items()
        }
        tracker.damage_by_type = {
            DamageType(dt): dmg for dt, dmg in data['damage_by_type'].items()
        }
        tracker.near_death_count = data['near_death_count']
        tracker.near_death_threshold = data['near_death_threshold']
        tracker.critical_hits_received = data['critical_hits_received']
        tracker.starvation_damage = data['starvation_damage']
        tracker.times_starved = data['times_starved']
        return tracker
