"""
Trait Analytics - Tracks and analyzes trait emergence and spread.

This module provides comprehensive tracking of:
- Trait discovery and first appearance
- Spread across populations and generations
- Impact metrics (creatures affected, survival rates)
- Timeline visualization data
- Export capabilities for analysis
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import time
import json
import csv
from collections import defaultdict


@dataclass
class TraitDiscovery:
    """
    Records when and how a trait first appeared.
    
    Attributes:
        trait_name: Name of the trait
        discovery_time: Unix timestamp of discovery
        generation: Generation number when discovered
        source_type: How it was discovered (emergent, mutated, inherited)
        discoverer_id: ID of first creature with this trait
        initial_rarity: Rarity at discovery
        category: Trait category
    """
    trait_name: str
    discovery_time: float
    generation: int
    source_type: str
    discoverer_id: Optional[str] = None
    initial_rarity: str = 'common'
    category: str = 'neutral'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'trait_name': self.trait_name,
            'discovery_time': self.discovery_time,
            'generation': self.generation,
            'source_type': self.source_type,
            'discoverer_id': self.discoverer_id,
            'initial_rarity': self.initial_rarity,
            'category': self.category
        }


@dataclass
class TraitSpreadMetrics:
    """
    Tracks how a trait spreads through the population.
    
    Attributes:
        trait_name: Name of the trait
        total_creatures: Total creatures that have had this trait
        current_carriers: Current living creatures with this trait
        generations_present: Number of generations with this trait
        survival_rate: Survival rate of creatures with this trait
        spread_events: List of (generation, count) tuples
    """
    trait_name: str
    total_creatures: int = 0
    current_carriers: int = 0
    generations_present: int = 0
    survival_rate: float = 0.0
    spread_events: List[Tuple[int, int]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'trait_name': self.trait_name,
            'total_creatures': self.total_creatures,
            'current_carriers': self.current_carriers,
            'generations_present': self.generations_present,
            'survival_rate': self.survival_rate,
            'spread_events': self.spread_events
        }


@dataclass
class InjectionEvent:
    """
    Records a trait injection event.
    
    Attributes:
        trait_name: Name of injected trait
        injection_time: Unix timestamp
        generation: Generation number
        injection_reason: Why trait was injected
        affected_creatures: Number of creatures affected
        event_data: Additional event data
    """
    trait_name: str
    injection_time: float
    generation: int
    injection_reason: str
    affected_creatures: int = 1
    event_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'trait_name': self.trait_name,
            'injection_time': self.injection_time,
            'generation': self.generation,
            'injection_reason': self.injection_reason,
            'affected_creatures': self.affected_creatures,
            'event_data': self.event_data
        }


class TraitAnalytics:
    """
    Comprehensive analytics system for trait tracking and visualization.
    
    Tracks:
    - When traits are discovered/injected
    - How they spread through populations
    - Impact on survival and evolution
    - Timeline of all trait-related events
    """
    
    def __init__(self):
        """Initialize the analytics system."""
        self.discoveries: Dict[str, TraitDiscovery] = {}
        self.spread_metrics: Dict[str, TraitSpreadMetrics] = {}
        self.injection_events: List[InjectionEvent] = []
        self.timeline: List[Dict[str, Any]] = []
        
        # Tracking data
        self.generation_trait_counts: Dict[int, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.creature_trait_history: Dict[str, List[str]] = defaultdict(list)
        
        # Statistics
        self.total_injections = 0
        self.total_discoveries = 0
        self.active_trait_count = 0
    
    def record_trait_discovery(
        self,
        trait_name: str,
        generation: int,
        source_type: str,
        discoverer_id: Optional[str] = None,
        rarity: str = 'common',
        category: str = 'neutral'
    ):
        """
        Record the discovery of a new trait.
        
        Args:
            trait_name: Name of the trait
            generation: Generation number
            source_type: How it was discovered
            discoverer_id: ID of first creature with trait
            rarity: Initial rarity
            category: Trait category
        """
        if trait_name not in self.discoveries:
            discovery = TraitDiscovery(
                trait_name=trait_name,
                discovery_time=time.time(),
                generation=generation,
                source_type=source_type,
                discoverer_id=discoverer_id,
                initial_rarity=rarity,
                category=category
            )
            
            self.discoveries[trait_name] = discovery
            self.total_discoveries += 1
            
            # Add to timeline
            self.timeline.append({
                'event_type': 'discovery',
                'trait_name': trait_name,
                'time': discovery.discovery_time,
                'generation': generation,
                'source_type': source_type
            })
            
            # Initialize spread metrics
            self.spread_metrics[trait_name] = TraitSpreadMetrics(trait_name=trait_name)
    
    def record_injection_event(
        self,
        trait_name: str,
        generation: int,
        injection_reason: str,
        affected_creatures: int = 1,
        event_data: Optional[Dict[str, Any]] = None
    ):
        """
        Record a trait injection event.
        
        Args:
            trait_name: Name of injected trait
            generation: Generation number
            injection_reason: Reason for injection
            affected_creatures: Number of creatures affected
            event_data: Additional event data
        """
        event = InjectionEvent(
            trait_name=trait_name,
            injection_time=time.time(),
            generation=generation,
            injection_reason=injection_reason,
            affected_creatures=affected_creatures,
            event_data=event_data or {}
        )
        
        self.injection_events.append(event)
        self.total_injections += 1
        
        # Add to timeline
        self.timeline.append({
            'event_type': 'injection',
            'trait_name': trait_name,
            'time': event.injection_time,
            'generation': generation,
            'reason': injection_reason,
            'affected': affected_creatures
        })
    
    def update_trait_spread(
        self,
        trait_name: str,
        generation: int,
        carrier_count: int,
        total_ever: Optional[int] = None
    ):
        """
        Update spread metrics for a trait.
        
        Args:
            trait_name: Name of the trait
            generation: Current generation
            carrier_count: Current number of carriers
            total_ever: Total creatures that have ever had this trait
        """
        if trait_name not in self.spread_metrics:
            self.spread_metrics[trait_name] = TraitSpreadMetrics(trait_name=trait_name)
        
        metrics = self.spread_metrics[trait_name]
        metrics.current_carriers = carrier_count
        
        if total_ever is not None:
            metrics.total_creatures = total_ever
        
        # Record spread event
        metrics.spread_events.append((generation, carrier_count))
        
        # Update generation tracking
        self.generation_trait_counts[generation][trait_name] = carrier_count
        
        # Update generations present
        unique_gens = set(gen for gen, _ in metrics.spread_events)
        metrics.generations_present = len(unique_gens)
    
    def record_creature_trait(self, creature_id: str, trait_name: str):
        """
        Record that a creature has a specific trait.
        
        Args:
            creature_id: Creature identifier
            trait_name: Trait name
        """
        if trait_name not in self.creature_trait_history[creature_id]:
            self.creature_trait_history[creature_id].append(trait_name)
            
            # Update total creatures count
            if trait_name in self.spread_metrics:
                self.spread_metrics[trait_name].total_creatures += 1
    
    def calculate_trait_survival_rate(
        self,
        trait_name: str,
        total_deaths: int,
        deaths_with_trait: int
    ):
        """
        Calculate survival rate for creatures with a specific trait.
        
        Args:
            trait_name: Trait name
            total_deaths: Total creature deaths
            deaths_with_trait: Deaths of creatures with this trait
        """
        if trait_name not in self.spread_metrics:
            return
        
        if total_deaths > 0:
            death_rate_with_trait = deaths_with_trait / total_deaths
            survival_rate = 1.0 - death_rate_with_trait
            self.spread_metrics[trait_name].survival_rate = survival_rate
    
    def get_trait_timeline(
        self,
        trait_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get timeline of trait events.
        
        Args:
            trait_name: Filter by specific trait (None for all)
            
        Returns:
            List of timeline events
        """
        if trait_name is None:
            return sorted(self.timeline, key=lambda x: x['time'])
        
        return sorted(
            [e for e in self.timeline if e['trait_name'] == trait_name],
            key=lambda x: x['time']
        )
    
    def get_generation_summary(self, generation: int) -> Dict[str, Any]:
        """
        Get summary of traits in a specific generation.
        
        Args:
            generation: Generation number
            
        Returns:
            Summary dictionary
        """
        trait_counts = self.generation_trait_counts.get(generation, {})
        
        return {
            'generation': generation,
            'unique_traits': len(trait_counts),
            'trait_counts': dict(trait_counts),
            'total_carriers': sum(trait_counts.values())
        }
    
    def get_most_successful_traits(self, limit: int = 10) -> List[Tuple[str, TraitSpreadMetrics]]:
        """
        Get most successful traits by spread and survival.
        
        Args:
            limit: Maximum number of traits to return
            
        Returns:
            List of (trait_name, metrics) tuples
        """
        scored_traits = []
        
        for trait_name, metrics in self.spread_metrics.items():
            # Score based on spread and survival
            score = (
                metrics.current_carriers * 2 +
                metrics.total_creatures * 1 +
                metrics.generations_present * 3 +
                metrics.survival_rate * 50
            )
            scored_traits.append((score, trait_name, metrics))
        
        # Sort by score descending
        scored_traits.sort(reverse=True, key=lambda x: x[0])
        
        return [(name, metrics) for _, name, metrics in scored_traits[:limit]]
    
    def get_recent_injections(self, limit: int = 10) -> List[InjectionEvent]:
        """
        Get most recent injection events.
        
        Args:
            limit: Maximum number of events
            
        Returns:
            List of recent injection events
        """
        return sorted(
            self.injection_events,
            key=lambda x: x.injection_time,
            reverse=True
        )[:limit]
    
    def export_to_json(self, filepath: str):
        """
        Export analytics data to JSON file.
        
        Args:
            filepath: Output file path
        """
        data = {
            'discoveries': {
                name: discovery.to_dict()
                for name, discovery in self.discoveries.items()
            },
            'spread_metrics': {
                name: metrics.to_dict()
                for name, metrics in self.spread_metrics.items()
            },
            'injection_events': [
                event.to_dict() for event in self.injection_events
            ],
            'timeline': self.timeline,
            'statistics': {
                'total_injections': self.total_injections,
                'total_discoveries': self.total_discoveries,
                'active_trait_count': len(self.spread_metrics)
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def export_to_csv(self, filepath: str):
        """
        Export spread metrics to CSV file.
        
        Args:
            filepath: Output file path
        """
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'Trait Name', 'Category', 'Rarity', 'Source Type',
                'Generation Discovered', 'Total Creatures', 'Current Carriers',
                'Generations Present', 'Survival Rate'
            ])
            
            # Data rows
            for trait_name, metrics in self.spread_metrics.items():
                discovery = self.discoveries.get(trait_name)
                
                writer.writerow([
                    trait_name,
                    discovery.category if discovery else 'unknown',
                    discovery.initial_rarity if discovery else 'common',
                    discovery.source_type if discovery else 'unknown',
                    discovery.generation if discovery else 0,
                    metrics.total_creatures,
                    metrics.current_carriers,
                    metrics.generations_present,
                    f"{metrics.survival_rate:.2%}"
                ])
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get data formatted for dashboard display.
        
        Returns:
            Dashboard data dictionary
        """
        return {
            'statistics': {
                'total_discoveries': self.total_discoveries,
                'total_injections': self.total_injections,
                'active_traits': len(self.spread_metrics),
                'unique_traits_ever': len(self.discoveries)
            },
            'top_traits': [
                {
                    'name': name,
                    'carriers': metrics.current_carriers,
                    'total_ever': metrics.total_creatures,
                    'generations': metrics.generations_present,
                    'survival_rate': f"{metrics.survival_rate:.1%}"
                }
                for name, metrics in self.get_most_successful_traits(10)
            ],
            'recent_events': [
                {
                    'type': event['event_type'],
                    'trait': event['trait_name'],
                    'generation': event['generation'],
                    'time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(event['time']))
                }
                for event in sorted(self.timeline, key=lambda x: x['time'], reverse=True)[:15]
            ]
        }
