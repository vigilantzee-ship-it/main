"""
Enhanced Interaction System - Track detailed social interactions between creatures.

This module provides comprehensive tracking of food competition, mating attempts,
territorial displays, flee/chase behaviors, and social observations.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time


class InteractionType(Enum):
    """Types of social interactions."""
    FOOD_COMPETITION = "food_competition"
    MATING_ATTEMPT = "mating_attempt"
    MATING_SUCCESS = "mating_success"
    TERRITORIAL_DISPLAY = "territorial_display"
    FLEE = "flee"
    CHASE = "chase"
    SOCIAL_OBSERVATION = "social_observation"
    ALLIANCE_FORMED = "alliance_formed"
    COOPERATION = "cooperation"


@dataclass
class InteractionRecord:
    """
    Records a single social interaction.
    
    Attributes:
        timestamp: When the interaction occurred
        interaction_type: Type of interaction
        initiator_id: ID of the creature that initiated the interaction
        target_id: ID of the target creature (or pellet)
        target_name: Name of the target
        success: Whether the interaction was successful
        location: Optional (x, y) coordinates where interaction occurred
        context: Additional interaction-specific data
    """
    timestamp: float
    interaction_type: InteractionType
    initiator_id: str
    target_id: str
    target_name: str
    success: bool
    location: Optional[Tuple[float, float]] = None
    context: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'timestamp': self.timestamp,
            'interaction_type': self.interaction_type.value,
            'initiator_id': self.initiator_id,
            'target_id': self.target_id,
            'target_name': self.target_name,
            'success': self.success,
            'location': self.location,
            'context': self.context
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'InteractionRecord':
        """Deserialize from dictionary."""
        data_copy = data.copy()
        data_copy['interaction_type'] = InteractionType(data_copy['interaction_type'])
        return InteractionRecord(**data_copy)


@dataclass
class FoodCompetitionRecord:
    """
    Records a food competition event.
    
    Attributes:
        timestamp: When the competition occurred
        pellet_id: ID of the contested pellet
        competitors: List of creature IDs competing for the pellet
        winner_id: ID of the creature that got the pellet
        location: Where the competition occurred
    """
    timestamp: float
    pellet_id: str
    competitors: List[str]
    winner_id: str
    location: Optional[Tuple[float, float]] = None
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'timestamp': self.timestamp,
            'pellet_id': self.pellet_id,
            'competitors': self.competitors,
            'winner_id': self.winner_id,
            'location': self.location
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'FoodCompetitionRecord':
        """Deserialize from dictionary."""
        return FoodCompetitionRecord(**data)


@dataclass
class MatingRecord:
    """
    Records a mating event.
    
    Attributes:
        timestamp: When the mating occurred
        partner_id: ID of the mating partner
        partner_name: Name of the partner
        success: Whether mating was successful
        offspring_id: ID of offspring if successful
        offspring_name: Name of offspring if successful
        location: Where mating occurred
    """
    timestamp: float
    partner_id: str
    partner_name: str
    success: bool
    offspring_id: Optional[str] = None
    offspring_name: Optional[str] = None
    location: Optional[Tuple[float, float]] = None
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'timestamp': self.timestamp,
            'partner_id': self.partner_id,
            'partner_name': self.partner_name,
            'success': self.success,
            'offspring_id': self.offspring_id,
            'offspring_name': self.offspring_name,
            'location': self.location
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'MatingRecord':
        """Deserialize from dictionary."""
        return MatingRecord(**data)


@dataclass
class PartnerStats:
    """
    Statistics for interactions with a specific partner.
    
    Attributes:
        partner_id: ID of the partner
        partner_name: Name of the partner
        mating_attempts: Number of mating attempts
        successful_matings: Number of successful matings
        offspring_count: Number of offspring produced together
        food_competitions: Number of food competitions
        competitions_won: Number of competitions won against this partner
        first_interaction: Timestamp of first interaction
        last_interaction: Timestamp of most recent interaction
    """
    partner_id: str
    partner_name: str
    mating_attempts: int = 0
    successful_matings: int = 0
    offspring_count: int = 0
    food_competitions: int = 0
    competitions_won: int = 0
    first_interaction: Optional[float] = None
    last_interaction: Optional[float] = None
    
    def mating_success_rate(self) -> float:
        """Calculate mating success rate."""
        if self.mating_attempts == 0:
            return 0.0
        return self.successful_matings / self.mating_attempts
    
    def competition_win_rate(self) -> float:
        """Calculate food competition win rate against this partner."""
        if self.food_competitions == 0:
            return 0.0
        return self.competitions_won / self.food_competitions
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'partner_id': self.partner_id,
            'partner_name': self.partner_name,
            'mating_attempts': self.mating_attempts,
            'successful_matings': self.successful_matings,
            'offspring_count': self.offspring_count,
            'food_competitions': self.food_competitions,
            'competitions_won': self.competitions_won,
            'first_interaction': self.first_interaction,
            'last_interaction': self.last_interaction
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'PartnerStats':
        """Deserialize from dictionary."""
        return PartnerStats(**data)


class InteractionTracker:
    """
    Comprehensive interaction tracking system for a creature.
    
    Tracks all social interactions including food competition, mating,
    territorial behaviors, and provides detailed statistics.
    """
    
    def __init__(self, creature_id: str, creature_name: str):
        """
        Initialize interaction tracker.
        
        Args:
            creature_id: Unique identifier for the creature
            creature_name: Name of the creature
        """
        self.creature_id = creature_id
        self.creature_name = creature_name
        
        # All interaction records
        self.interactions: List[InteractionRecord] = []
        
        # Specific interaction types
        self.food_competitions: List[FoodCompetitionRecord] = []
        self.mating_records: List[MatingRecord] = []
        
        # Statistics by partner
        self.partner_stats: Dict[str, PartnerStats] = {}
        
        # Interaction counters
        self.total_food_competitions: int = 0
        self.food_competitions_won: int = 0
        self.total_mating_attempts: int = 0
        self.successful_matings: int = 0
        self.territorial_displays: int = 0
        self.times_fled: int = 0
        self.times_chased: int = 0
        self.social_observations: int = 0
    
    def record_interaction(
        self,
        interaction_type: InteractionType,
        target_id: str,
        target_name: str,
        success: bool,
        location: Optional[Tuple[float, float]] = None,
        context: Optional[Dict] = None
    ):
        """
        Record a general interaction.
        
        Args:
            interaction_type: Type of interaction
            target_id: ID of the target
            target_name: Name of the target
            success: Whether interaction was successful
            location: Where the interaction occurred
            context: Additional context data
        """
        interaction = InteractionRecord(
            timestamp=time.time(),
            interaction_type=interaction_type,
            initiator_id=self.creature_id,
            target_id=target_id,
            target_name=target_name,
            success=success,
            location=location,
            context=context or {}
        )
        self.interactions.append(interaction)
        
        # Update counters
        if interaction_type == InteractionType.TERRITORIAL_DISPLAY:
            self.territorial_displays += 1
        elif interaction_type == InteractionType.FLEE:
            self.times_fled += 1
        elif interaction_type == InteractionType.CHASE:
            self.times_chased += 1
        elif interaction_type == InteractionType.SOCIAL_OBSERVATION:
            self.social_observations += 1
    
    def record_food_competition(
        self,
        pellet_id: str,
        competitors: List[str],
        winner_id: str,
        location: Optional[Tuple[float, float]] = None
    ):
        """
        Record a food competition event.
        
        Args:
            pellet_id: ID of the contested pellet
            competitors: List of creature IDs competing
            winner_id: ID of the winner
            location: Where the competition occurred
        """
        competition = FoodCompetitionRecord(
            timestamp=time.time(),
            pellet_id=pellet_id,
            competitors=competitors,
            winner_id=winner_id,
            location=location
        )
        self.food_competitions.append(competition)
        self.total_food_competitions += 1
        
        # Track if this creature won
        if winner_id == self.creature_id:
            self.food_competitions_won += 1
        
        # Update partner stats for each competitor
        for competitor_id in competitors:
            if competitor_id != self.creature_id:
                if competitor_id not in self.partner_stats:
                    self.partner_stats[competitor_id] = PartnerStats(
                        partner_id=competitor_id,
                        partner_name=f"Creature {competitor_id[:8]}"
                    )
                
                stats = self.partner_stats[competitor_id]
                stats.food_competitions += 1
                if winner_id == self.creature_id:
                    stats.competitions_won += 1
                if stats.first_interaction is None:
                    stats.first_interaction = competition.timestamp
                stats.last_interaction = competition.timestamp
    
    def record_mating_attempt(
        self,
        partner_id: str,
        partner_name: str,
        success: bool,
        offspring_id: Optional[str] = None,
        offspring_name: Optional[str] = None,
        location: Optional[Tuple[float, float]] = None
    ):
        """
        Record a mating attempt.
        
        Args:
            partner_id: ID of the mating partner
            partner_name: Name of the partner
            success: Whether mating was successful
            offspring_id: ID of offspring if successful
            offspring_name: Name of offspring if successful
            location: Where mating occurred
        """
        mating = MatingRecord(
            timestamp=time.time(),
            partner_id=partner_id,
            partner_name=partner_name,
            success=success,
            offspring_id=offspring_id,
            offspring_name=offspring_name,
            location=location
        )
        self.mating_records.append(mating)
        self.total_mating_attempts += 1
        
        if success:
            self.successful_matings += 1
        
        # Record as general interaction
        interaction_type = InteractionType.MATING_SUCCESS if success else InteractionType.MATING_ATTEMPT
        context = {
            'offspring_id': offspring_id,
            'offspring_name': offspring_name
        } if success else {}
        
        self.record_interaction(
            interaction_type=interaction_type,
            target_id=partner_id,
            target_name=partner_name,
            success=success,
            location=location,
            context=context
        )
        
        # Update partner stats
        if partner_id not in self.partner_stats:
            self.partner_stats[partner_id] = PartnerStats(
                partner_id=partner_id,
                partner_name=partner_name
            )
        
        stats = self.partner_stats[partner_id]
        stats.mating_attempts += 1
        if success:
            stats.successful_matings += 1
            stats.offspring_count += 1
        if stats.first_interaction is None:
            stats.first_interaction = mating.timestamp
        stats.last_interaction = mating.timestamp
    
    def get_food_competition_win_rate(self) -> float:
        """Calculate overall food competition win rate."""
        if self.total_food_competitions == 0:
            return 0.0
        return self.food_competitions_won / self.total_food_competitions
    
    def get_mating_success_rate(self) -> float:
        """Calculate overall mating success rate."""
        if self.total_mating_attempts == 0:
            return 0.0
        return self.successful_matings / self.total_mating_attempts
    
    def get_most_frequent_partner(self) -> Optional[PartnerStats]:
        """Get the partner with the most interactions."""
        if not self.partner_stats:
            return None
        return max(
            self.partner_stats.values(),
            key=lambda s: s.mating_attempts + s.food_competitions
        )
    
    def get_best_mating_partner(self) -> Optional[PartnerStats]:
        """Get the partner with the most successful matings."""
        if not self.partner_stats:
            return None
        partners_with_matings = [
            s for s in self.partner_stats.values() if s.successful_matings > 0
        ]
        if not partners_with_matings:
            return None
        return max(partners_with_matings, key=lambda s: s.successful_matings)
    
    def get_biggest_rival(self) -> Optional[PartnerStats]:
        """Get the partner with the most food competitions."""
        if not self.partner_stats:
            return None
        partners_with_competitions = [
            s for s in self.partner_stats.values() if s.food_competitions > 0
        ]
        if not partners_with_competitions:
            return None
        return max(partners_with_competitions, key=lambda s: s.food_competitions)
    
    def get_recent_interactions(self, count: int = 10) -> List[InteractionRecord]:
        """Get the most recent interactions."""
        return sorted(self.interactions, key=lambda i: i.timestamp, reverse=True)[:count]
    
    def get_interactions_by_type(self, interaction_type: InteractionType) -> List[InteractionRecord]:
        """Get all interactions of a specific type."""
        return [i for i in self.interactions if i.interaction_type == interaction_type]
    
    def get_interaction_summary(self) -> Dict[str, int]:
        """
        Get a summary of all interaction counts.
        
        Returns:
            Dictionary mapping interaction types to counts
        """
        return {
            'total_interactions': len(self.interactions),
            'food_competitions': self.total_food_competitions,
            'food_competitions_won': self.food_competitions_won,
            'mating_attempts': self.total_mating_attempts,
            'successful_matings': self.successful_matings,
            'territorial_displays': self.territorial_displays,
            'times_fled': self.times_fled,
            'times_chased': self.times_chased,
            'social_observations': self.social_observations
        }
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            'creature_id': self.creature_id,
            'creature_name': self.creature_name,
            'interactions': [i.to_dict() for i in self.interactions],
            'food_competitions': [fc.to_dict() for fc in self.food_competitions],
            'mating_records': [mr.to_dict() for mr in self.mating_records],
            'partner_stats': {
                partner_id: stats.to_dict()
                for partner_id, stats in self.partner_stats.items()
            },
            'total_food_competitions': self.total_food_competitions,
            'food_competitions_won': self.food_competitions_won,
            'total_mating_attempts': self.total_mating_attempts,
            'successful_matings': self.successful_matings,
            'territorial_displays': self.territorial_displays,
            'times_fled': self.times_fled,
            'times_chased': self.times_chased,
            'social_observations': self.social_observations
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'InteractionTracker':
        """Deserialize from dictionary."""
        tracker = InteractionTracker(data['creature_id'], data['creature_name'])
        tracker.interactions = [InteractionRecord.from_dict(i) for i in data['interactions']]
        tracker.food_competitions = [FoodCompetitionRecord.from_dict(fc) for fc in data['food_competitions']]
        tracker.mating_records = [MatingRecord.from_dict(mr) for mr in data['mating_records']]
        tracker.partner_stats = {
            partner_id: PartnerStats.from_dict(stats)
            for partner_id, stats in data['partner_stats'].items()
        }
        tracker.total_food_competitions = data['total_food_competitions']
        tracker.food_competitions_won = data['food_competitions_won']
        tracker.total_mating_attempts = data['total_mating_attempts']
        tracker.successful_matings = data['successful_matings']
        tracker.territorial_displays = data['territorial_displays']
        tracker.times_fled = data['times_fled']
        tracker.times_chased = data['times_chased']
        tracker.social_observations = data['social_observations']
        return tracker
