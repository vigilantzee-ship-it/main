"""
Pellet Life History System - Track pellet lifecycle, targeting, and lineage.

This module provides comprehensive tracking of pellet lifecycle events, targeting
statistics, offspring lineage, and survival data.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time


class PelletEventType(Enum):
    """Types of pellet lifecycle events."""
    SPAWN = "spawn"
    REPRODUCE = "reproduce"
    MUTATE = "mutate"
    TARGETED = "targeted"
    AVOIDED = "avoided"
    EATEN = "eaten"
    DIED = "died"  # Natural death (old age)


@dataclass
class PelletLifeEvent:
    """
    Records a single pellet lifecycle event.
    
    Attributes:
        timestamp: When the event occurred
        event_type: Type of event
        description: Human-readable description
        creature_id: ID of creature involved (if any)
        location: Optional (x, y) coordinates where event occurred
        context: Additional event-specific data
    """
    timestamp: float
    event_type: PelletEventType
    description: str
    creature_id: Optional[str] = None
    location: Optional[Tuple[float, float]] = None
    context: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'timestamp': self.timestamp,
            'event_type': self.event_type.value,
            'description': self.description,
            'creature_id': self.creature_id,
            'location': self.location,
            'context': self.context
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'PelletLifeEvent':
        """Deserialize from dictionary."""
        data_copy = data.copy()
        data_copy['event_type'] = PelletEventType(data_copy['event_type'])
        return PelletLifeEvent(**data_copy)


@dataclass
class CreatureTargetingStats:
    """
    Statistics for a creature's interactions with this pellet.
    
    Attributes:
        creature_id: ID of the creature
        times_targeted: Number of times creature targeted this pellet
        times_avoided: Number of times creature avoided this pellet
        distance_traveled: Total distance creature traveled to target this pellet
        first_targeting: Timestamp of first targeting
        last_targeting: Timestamp of last targeting
    """
    creature_id: str
    times_targeted: int = 0
    times_avoided: int = 0
    distance_traveled: float = 0.0
    first_targeting: Optional[float] = None
    last_targeting: Optional[float] = None
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'creature_id': self.creature_id,
            'times_targeted': self.times_targeted,
            'times_avoided': self.times_avoided,
            'distance_traveled': self.distance_traveled,
            'first_targeting': self.first_targeting,
            'last_targeting': self.last_targeting
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'CreatureTargetingStats':
        """Deserialize from dictionary."""
        return CreatureTargetingStats(**data)


class PelletLifeHistory:
    """
    Comprehensive lifecycle tracking for a pellet.
    
    Tracks spawn, reproduction, mutations, targeting by creatures,
    and eventual consumption or death.
    """
    
    def __init__(self, pellet_id: str, spawn_time: Optional[float] = None):
        """
        Initialize pellet life history.
        
        Args:
            pellet_id: Unique identifier for the pellet
            spawn_time: When the pellet was spawned (defaults to current time)
        """
        self.pellet_id = pellet_id
        
        # Lifecycle
        self.spawn_time: float = spawn_time if spawn_time is not None else time.time()
        self.death_time: Optional[float] = None
        self.cause_of_death: Optional[str] = None  # "eaten" or "natural"
        self.eaten_by: Optional[str] = None  # Creature ID if eaten
        
        # Lineage
        self.parent_id: Optional[str] = None
        self.offspring_ids: List[str] = []
        self.generation: int = 0
        
        # Event log
        self.events: List[PelletLifeEvent] = []
        
        # Targeting statistics
        self.creature_targeting: Dict[str, CreatureTargetingStats] = {}
        self.total_times_targeted: int = 0
        self.total_times_avoided: int = 0
        
        # Reproduction
        self.times_reproduced: int = 0
        self.mutation_count: int = 0
        
        # Location tracking
        self.spawn_location: Optional[Tuple[float, float]] = None
        self.death_location: Optional[Tuple[float, float]] = None
    
    def record_spawn(self, location: Optional[Tuple[float, float]] = None, parent_id: Optional[str] = None):
        """
        Record pellet spawn event.
        
        Args:
            location: Where the pellet spawned
            parent_id: ID of parent pellet if reproduced
        """
        self.spawn_location = location
        self.parent_id = parent_id
        
        event = PelletLifeEvent(
            timestamp=self.spawn_time,
            event_type=PelletEventType.SPAWN,
            description=f"Pellet spawned" + (f" from parent {parent_id[:8]}" if parent_id else ""),
            location=location,
            context={'parent_id': parent_id} if parent_id else {}
        )
        self.events.append(event)
    
    def record_reproduction(self, offspring_id: str, location: Optional[Tuple[float, float]] = None):
        """
        Record reproduction event.
        
        Args:
            offspring_id: ID of the new offspring pellet
            location: Where reproduction occurred
        """
        self.offspring_ids.append(offspring_id)
        self.times_reproduced += 1
        
        event = PelletLifeEvent(
            timestamp=time.time(),
            event_type=PelletEventType.REPRODUCE,
            description=f"Pellet reproduced (offspring: {offspring_id[:8]})",
            location=location,
            context={'offspring_id': offspring_id}
        )
        self.events.append(event)
    
    def record_mutation(self, mutation_details: Dict):
        """
        Record mutation event.
        
        Args:
            mutation_details: Dictionary describing what mutated
        """
        self.mutation_count += 1
        
        event = PelletLifeEvent(
            timestamp=time.time(),
            event_type=PelletEventType.MUTATE,
            description="Pellet mutated",
            context=mutation_details
        )
        self.events.append(event)
    
    def record_targeted(
        self,
        creature_id: str,
        location: Optional[Tuple[float, float]] = None,
        distance: float = 0.0
    ):
        """
        Record being targeted by a creature.
        
        Args:
            creature_id: ID of the targeting creature
            location: Where targeting occurred
            distance: Distance creature traveled to target
        """
        self.total_times_targeted += 1
        
        # Update creature targeting stats
        if creature_id not in self.creature_targeting:
            self.creature_targeting[creature_id] = CreatureTargetingStats(
                creature_id=creature_id
            )
        
        stats = self.creature_targeting[creature_id]
        stats.times_targeted += 1
        stats.distance_traveled += distance
        if stats.first_targeting is None:
            stats.first_targeting = time.time()
        stats.last_targeting = time.time()
        
        event = PelletLifeEvent(
            timestamp=time.time(),
            event_type=PelletEventType.TARGETED,
            description=f"Targeted by creature {creature_id[:8]}",
            creature_id=creature_id,
            location=location,
            context={'distance': distance}
        )
        self.events.append(event)
    
    def record_avoided(
        self,
        creature_id: str,
        location: Optional[Tuple[float, float]] = None,
        reason: str = "low palatability"
    ):
        """
        Record being avoided by a creature.
        
        Args:
            creature_id: ID of the avoiding creature
            location: Where avoidance occurred
            reason: Why the creature avoided this pellet
        """
        self.total_times_avoided += 1
        
        # Update creature targeting stats
        if creature_id not in self.creature_targeting:
            self.creature_targeting[creature_id] = CreatureTargetingStats(
                creature_id=creature_id
            )
        
        stats = self.creature_targeting[creature_id]
        stats.times_avoided += 1
        
        event = PelletLifeEvent(
            timestamp=time.time(),
            event_type=PelletEventType.AVOIDED,
            description=f"Avoided by creature {creature_id[:8]} ({reason})",
            creature_id=creature_id,
            location=location,
            context={'reason': reason}
        )
        self.events.append(event)
    
    def record_eaten(
        self,
        creature_id: str,
        creature_name: str,
        location: Optional[Tuple[float, float]] = None,
        nutritional_value: float = 0.0
    ):
        """
        Record being eaten by a creature.
        
        Args:
            creature_id: ID of the creature that ate this pellet
            creature_name: Name of the creature
            location: Where the pellet was eaten
            nutritional_value: How much nutrition was provided
        """
        self.death_time = time.time()
        self.cause_of_death = "eaten"
        self.eaten_by = creature_id
        self.death_location = location
        
        event = PelletLifeEvent(
            timestamp=self.death_time,
            event_type=PelletEventType.EATEN,
            description=f"Eaten by {creature_name}",
            creature_id=creature_id,
            location=location,
            context={
                'creature_name': creature_name,
                'nutritional_value': nutritional_value
            }
        )
        self.events.append(event)
    
    def record_death(
        self,
        cause: str = "old age",
        location: Optional[Tuple[float, float]] = None
    ):
        """
        Record natural death.
        
        Args:
            cause: Cause of death
            location: Where the pellet died
        """
        self.death_time = time.time()
        self.cause_of_death = cause
        self.death_location = location
        
        event = PelletLifeEvent(
            timestamp=self.death_time,
            event_type=PelletEventType.DIED,
            description=f"Died: {cause}",
            location=location,
            context={'cause': cause}
        )
        self.events.append(event)
    
    def get_lifetime(self) -> float:
        """
        Get pellet's lifetime in seconds.
        
        Returns:
            Lifetime duration, or current age if still alive
        """
        end_time = self.death_time if self.death_time else time.time()
        return end_time - self.spawn_time
    
    def is_alive(self) -> bool:
        """Check if pellet is still alive."""
        return self.death_time is None
    
    def get_targeting_rate(self) -> float:
        """
        Calculate how often pellet is targeted vs avoided.
        
        Returns:
            Ratio of targeted to total interactions (0-1)
        """
        total = self.total_times_targeted + self.total_times_avoided
        if total == 0:
            return 0.0
        return self.total_times_targeted / total
    
    def get_most_interested_creature(self) -> Optional[CreatureTargetingStats]:
        """Get the creature that targeted this pellet the most."""
        if not self.creature_targeting:
            return None
        return max(self.creature_targeting.values(), key=lambda s: s.times_targeted)
    
    def get_lineage_depth(self) -> int:
        """
        Get the depth of this pellet's lineage.
        
        Returns:
            Generation number (0 for original, 1+ for descendants)
        """
        return self.generation
    
    def get_descendant_count(self) -> int:
        """
        Get total number of direct descendants.
        
        Returns:
            Number of offspring produced
        """
        return len(self.offspring_ids)
    
    def get_recent_events(self, count: int = 10) -> List[PelletLifeEvent]:
        """Get the most recent events."""
        return sorted(self.events, key=lambda e: e.timestamp, reverse=True)[:count]
    
    def get_events_by_type(self, event_type: PelletEventType) -> List[PelletLifeEvent]:
        """Get all events of a specific type."""
        return [e for e in self.events if e.event_type == event_type]
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'pellet_id': self.pellet_id,
            'spawn_time': self.spawn_time,
            'death_time': self.death_time,
            'cause_of_death': self.cause_of_death,
            'eaten_by': self.eaten_by,
            'parent_id': self.parent_id,
            'offspring_ids': self.offspring_ids,
            'generation': self.generation,
            'events': [e.to_dict() for e in self.events],
            'creature_targeting': {
                creature_id: stats.to_dict()
                for creature_id, stats in self.creature_targeting.items()
            },
            'total_times_targeted': self.total_times_targeted,
            'total_times_avoided': self.total_times_avoided,
            'times_reproduced': self.times_reproduced,
            'mutation_count': self.mutation_count,
            'spawn_location': self.spawn_location,
            'death_location': self.death_location
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'PelletLifeHistory':
        """Deserialize from dictionary."""
        history = PelletLifeHistory(data['pellet_id'], data['spawn_time'])
        history.death_time = data.get('death_time')
        history.cause_of_death = data.get('cause_of_death')
        history.eaten_by = data.get('eaten_by')
        history.parent_id = data.get('parent_id')
        history.offspring_ids = data['offspring_ids']
        history.generation = data['generation']
        history.events = [PelletLifeEvent.from_dict(e) for e in data['events']]
        history.creature_targeting = {
            creature_id: CreatureTargetingStats.from_dict(stats)
            for creature_id, stats in data['creature_targeting'].items()
        }
        history.total_times_targeted = data['total_times_targeted']
        history.total_times_avoided = data['total_times_avoided']
        history.times_reproduced = data['times_reproduced']
        history.mutation_count = data['mutation_count']
        history.spawn_location = data.get('spawn_location')
        history.death_location = data.get('death_location')
        return history
