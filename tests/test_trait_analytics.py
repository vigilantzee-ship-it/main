"""
Tests for the trait analytics system.
"""

import unittest
import tempfile
import os
import json
from src.models.trait_analytics import (
    TraitAnalytics,
    TraitDiscovery,
    TraitSpreadMetrics,
    InjectionEvent
)


class TestTraitDiscovery(unittest.TestCase):
    """Test TraitDiscovery data structure."""
    
    def test_discovery_creation(self):
        """Test creating a trait discovery."""
        discovery = TraitDiscovery(
            trait_name="Test Trait",
            discovery_time=1000.0,
            generation=5,
            source_type='emergent',
            initial_rarity='rare',
            category='physical'
        )
        
        self.assertEqual(discovery.trait_name, "Test Trait")
        self.assertEqual(discovery.generation, 5)
        self.assertEqual(discovery.source_type, 'emergent')
        self.assertEqual(discovery.initial_rarity, 'rare')
    
    def test_discovery_to_dict(self):
        """Test serialization of discovery."""
        discovery = TraitDiscovery(
            trait_name="Test",
            discovery_time=1000.0,
            generation=1,
            source_type='cosmic'
        )
        
        data = discovery.to_dict()
        
        self.assertIn('trait_name', data)
        self.assertIn('generation', data)
        self.assertEqual(data['trait_name'], "Test")


class TestTraitSpreadMetrics(unittest.TestCase):
    """Test TraitSpreadMetrics data structure."""
    
    def test_metrics_creation(self):
        """Test creating spread metrics."""
        metrics = TraitSpreadMetrics(trait_name="Test")
        
        self.assertEqual(metrics.trait_name, "Test")
        self.assertEqual(metrics.total_creatures, 0)
        self.assertEqual(metrics.current_carriers, 0)
    
    def test_metrics_to_dict(self):
        """Test serialization of metrics."""
        metrics = TraitSpreadMetrics(
            trait_name="Test",
            total_creatures=10,
            current_carriers=5
        )
        
        data = metrics.to_dict()
        
        self.assertEqual(data['total_creatures'], 10)
        self.assertEqual(data['current_carriers'], 5)


class TestTraitAnalytics(unittest.TestCase):
    """Test TraitAnalytics system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analytics = TraitAnalytics()
    
    def test_analytics_initialization(self):
        """Test analytics initializes correctly."""
        self.assertIsNotNone(self.analytics)
        self.assertEqual(len(self.analytics.discoveries), 0)
        self.assertEqual(len(self.analytics.injection_events), 0)
        self.assertEqual(self.analytics.total_injections, 0)
    
    def test_record_trait_discovery(self):
        """Test recording trait discoveries."""
        self.analytics.record_trait_discovery(
            trait_name="Swift",
            generation=1,
            source_type='emergent',
            rarity='uncommon',
            category='physical'
        )
        
        self.assertEqual(len(self.analytics.discoveries), 1)
        self.assertIn("Swift", self.analytics.discoveries)
        self.assertEqual(self.analytics.total_discoveries, 1)
        
        discovery = self.analytics.discoveries["Swift"]
        self.assertEqual(discovery.generation, 1)
        self.assertEqual(discovery.source_type, 'emergent')
    
    def test_record_injection_event(self):
        """Test recording injection events."""
        self.analytics.record_injection_event(
            trait_name="Adaptive",
            generation=5,
            injection_reason='breeding_mutation',
            affected_creatures=1
        )
        
        self.assertEqual(len(self.analytics.injection_events), 1)
        self.assertEqual(self.analytics.total_injections, 1)
        
        event = self.analytics.injection_events[0]
        self.assertEqual(event.trait_name, "Adaptive")
        self.assertEqual(event.injection_reason, 'breeding_mutation')
    
    def test_update_trait_spread(self):
        """Test updating trait spread metrics."""
        # First discover the trait
        self.analytics.record_trait_discovery(
            trait_name="Hardy",
            generation=1,
            source_type='emergent'
        )
        
        # Update spread
        self.analytics.update_trait_spread(
            trait_name="Hardy",
            generation=1,
            carrier_count=5,
            total_ever=5
        )
        
        metrics = self.analytics.spread_metrics["Hardy"]
        self.assertEqual(metrics.current_carriers, 5)
        self.assertEqual(metrics.total_creatures, 5)
        self.assertEqual(len(metrics.spread_events), 1)
    
    def test_record_creature_trait(self):
        """Test recording creature-trait associations."""
        self.analytics.record_trait_discovery(
            trait_name="Fast",
            generation=1,
            source_type='emergent'
        )
        
        self.analytics.record_creature_trait("creature_1", "Fast")
        self.analytics.record_creature_trait("creature_2", "Fast")
        
        # Same creature, same trait (shouldn't double count)
        self.analytics.record_creature_trait("creature_1", "Fast")
        
        metrics = self.analytics.spread_metrics["Fast"]
        self.assertEqual(metrics.total_creatures, 2)
    
    def test_calculate_trait_survival_rate(self):
        """Test calculating survival rates."""
        self.analytics.record_trait_discovery(
            trait_name="Survivor",
            generation=1,
            source_type='emergent'
        )
        
        # 100 total deaths, 30 had the trait
        self.analytics.calculate_trait_survival_rate(
            trait_name="Survivor",
            total_deaths=100,
            deaths_with_trait=30
        )
        
        metrics = self.analytics.spread_metrics["Survivor"]
        self.assertAlmostEqual(metrics.survival_rate, 0.7, places=2)
    
    def test_get_trait_timeline(self):
        """Test getting trait timeline."""
        self.analytics.record_trait_discovery(
            trait_name="Alpha",
            generation=1,
            source_type='emergent'
        )
        
        self.analytics.record_injection_event(
            trait_name="Beta",
            generation=2,
            injection_reason='cosmic'
        )
        
        timeline = self.analytics.get_trait_timeline()
        self.assertEqual(len(timeline), 2)
        
        # Should be sorted by time
        self.assertLessEqual(timeline[0]['time'], timeline[1]['time'])
    
    def test_get_trait_timeline_filtered(self):
        """Test getting timeline for specific trait."""
        self.analytics.record_trait_discovery(
            trait_name="Alpha",
            generation=1,
            source_type='emergent'
        )
        
        self.analytics.record_trait_discovery(
            trait_name="Beta",
            generation=2,
            source_type='cosmic'
        )
        
        timeline = self.analytics.get_trait_timeline(trait_name="Alpha")
        self.assertEqual(len(timeline), 1)
        self.assertEqual(timeline[0]['trait_name'], "Alpha")
    
    def test_get_generation_summary(self):
        """Test getting generation summary."""
        self.analytics.record_trait_discovery("Trait1", 5, 'emergent')
        self.analytics.record_trait_discovery("Trait2", 5, 'emergent')
        
        self.analytics.update_trait_spread("Trait1", 5, 10)
        self.analytics.update_trait_spread("Trait2", 5, 15)
        
        summary = self.analytics.get_generation_summary(5)
        
        self.assertEqual(summary['generation'], 5)
        self.assertEqual(summary['unique_traits'], 2)
        self.assertEqual(summary['total_carriers'], 25)
    
    def test_get_most_successful_traits(self):
        """Test getting most successful traits."""
        # Create multiple traits with different metrics
        for i in range(5):
            trait_name = f"Trait{i}"
            self.analytics.record_trait_discovery(trait_name, 1, 'emergent')
            self.analytics.update_trait_spread(
                trait_name,
                generation=1,
                carrier_count=i * 10,
                total_ever=i * 15
            )
        
        successful = self.analytics.get_most_successful_traits(limit=3)
        
        self.assertEqual(len(successful), 3)
        # Should be sorted by success
        self.assertGreaterEqual(
            successful[0][1].current_carriers,
            successful[1][1].current_carriers
        )
    
    def test_get_recent_injections(self):
        """Test getting recent injections."""
        for i in range(10):
            self.analytics.record_injection_event(
                trait_name=f"Trait{i}",
                generation=i,
                injection_reason='breeding'
            )
        
        recent = self.analytics.get_recent_injections(limit=5)
        
        self.assertEqual(len(recent), 5)
        # Should be most recent first
        self.assertGreaterEqual(
            recent[0].injection_time,
            recent[1].injection_time
        )
    
    def test_export_to_json(self):
        """Test exporting to JSON."""
        self.analytics.record_trait_discovery("Test", 1, 'emergent')
        self.analytics.record_injection_event("Test", 1, 'breeding')
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name
        
        try:
            self.analytics.export_to_json(filepath)
            
            # Verify file was created and contains valid JSON
            self.assertTrue(os.path.exists(filepath))
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.assertIn('discoveries', data)
            self.assertIn('injection_events', data)
            self.assertIn('statistics', data)
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)
    
    def test_export_to_csv(self):
        """Test exporting to CSV."""
        self.analytics.record_trait_discovery("Test1", 1, 'emergent', rarity='rare')
        self.analytics.record_trait_discovery("Test2", 2, 'cosmic', rarity='common')
        self.analytics.update_trait_spread("Test1", 1, 10, 15)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            filepath = f.name
        
        try:
            self.analytics.export_to_csv(filepath)
            
            # Verify file was created
            self.assertTrue(os.path.exists(filepath))
            
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Check for header
            self.assertIn('Trait Name', content)
            self.assertIn('Category', content)
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)
    
    def test_get_dashboard_data(self):
        """Test getting dashboard data."""
        self.analytics.record_trait_discovery("Alpha", 1, 'emergent')
        self.analytics.record_injection_event("Alpha", 1, 'breeding')
        self.analytics.update_trait_spread("Alpha", 1, 5, 10)
        
        dashboard = self.analytics.get_dashboard_data()
        
        self.assertIn('statistics', dashboard)
        self.assertIn('top_traits', dashboard)
        self.assertIn('recent_events', dashboard)
        
        stats = dashboard['statistics']
        self.assertEqual(stats['total_discoveries'], 1)
        self.assertEqual(stats['total_injections'], 1)
    
    def test_multiple_spread_updates(self):
        """Test tracking spread over multiple generations."""
        self.analytics.record_trait_discovery("Growing", 1, 'emergent')
        
        # Simulate growth over generations
        for gen in range(1, 6):
            self.analytics.update_trait_spread(
                "Growing",
                generation=gen,
                carrier_count=gen * 5
            )
        
        metrics = self.analytics.spread_metrics["Growing"]
        self.assertEqual(len(metrics.spread_events), 5)
        self.assertEqual(metrics.generations_present, 5)
        
        # Last event should have highest count
        last_gen, last_count = metrics.spread_events[-1]
        self.assertEqual(last_count, 25)


if __name__ == '__main__':
    unittest.main()
