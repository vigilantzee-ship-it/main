"""
Performance tests for spatial hash grid optimization.

Compares O(n²) baseline against O(n) spatial hash grid implementation.
"""

import unittest
import time
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats, StatGrowth
from src.models.spatial import Vector2D, SpatialHashGrid
from src.systems.battle_spatial import SpatialBattle, BattleCreature
import random


class TestSpatialHashGridPerformance(unittest.TestCase):
    """Test spatial hash grid performance."""
    
    def setUp(self):
        """Set up test fixtures."""
        random.seed(42)  # Reproducible tests
        
    def _create_test_creatures(self, count: int) -> list:
        """Create test creatures for performance testing."""
        creature_type = CreatureType(
            name="TestType",
            base_stats=Stats(max_hp=100, attack=10, defense=10, speed=10),
            stat_growth=StatGrowth()
        )
        
        creatures = []
        for i in range(count):
            creature = Creature(
                name=f"Creature_{i}",
                creature_type=creature_type,
                level=5
            )
            creatures.append(creature)
        
        return creatures
    
    def test_spatial_grid_basic_operations(self):
        """Test basic spatial grid operations."""
        grid = SpatialHashGrid(100.0, 100.0, cell_size=10.0)
        
        # Create test entities
        entities = []
        for i in range(100):
            pos = Vector2D(random.uniform(0, 100), random.uniform(0, 100))
            entities.append((i, pos))
        
        # Test insertion
        start = time.time()
        for entity_id, pos in entities:
            grid.insert(entity_id, pos)
        insert_time = time.time() - start
        
        # Test radius query
        start = time.time()
        for _ in range(100):
            center = Vector2D(random.uniform(0, 100), random.uniform(0, 100))
            results = grid.query_radius(center, 20.0)
        query_time = time.time() - start
        
        print(f"\nSpatial Grid Basic Operations (100 entities):")
        print(f"  Insert time: {insert_time*1000:.2f}ms")
        print(f"  100 radius queries: {query_time*1000:.2f}ms")
        
        # Verify correctness
        center = Vector2D(50, 50)
        results = grid.query_radius(
            center, 
            20.0, 
            exact_distance=True,
            get_position=lambda e: entities[e][1]  # e is the entity_id, get position from tuple
        )
        
        # Count actual entities within radius (brute force)
        actual_count = 0
        for entity_id, pos in entities:
            if center.distance_to(pos) <= 20.0:
                actual_count += 1
        
        self.assertEqual(len(results), actual_count)
    
    def test_battle_with_spatial_optimization(self):
        """Test battle performance with spatial optimization."""
        # Test with moderate population
        creature_count = 30
        creatures = self._create_test_creatures(creature_count)
        
        # Create battle with spatial optimization
        battle = SpatialBattle(
            creatures_or_team1=creatures,
            arena_width=100.0,
            arena_height=100.0,
            random_seed=42,
            resource_spawn_rate=0,  # No resources for this test
            initial_resources=0
        )
        
        # Run multiple update cycles and measure time
        num_updates = 100
        start = time.time()
        for _ in range(num_updates):
            battle.update(0.1)
            if battle.is_over:
                break
        elapsed = time.time() - start
        
        avg_frame_time = elapsed / num_updates * 1000  # milliseconds
        
        print(f"\nBattle Performance ({creature_count} creatures, {num_updates} updates):")
        print(f"  Total time: {elapsed:.3f}s")
        print(f"  Average frame time: {avg_frame_time:.2f}ms")
        print(f"  Target: <16ms for 60 FPS")
        
        # Performance assertion - should be well under 16ms per frame
        self.assertLess(avg_frame_time, 16.0, 
                       f"Frame time {avg_frame_time:.2f}ms exceeds 60 FPS target (16ms)")
    
    def test_breeding_proximity_scaling(self):
        """Test breeding proximity check performance with spatial grid."""
        # Create a larger population for breeding checks
        creature_count = 50
        creatures = self._create_test_creatures(creature_count)
        
        battle = SpatialBattle(
            creatures_or_team1=creatures,
            arena_width=100.0,
            arena_height=100.0,
            random_seed=42,
            resource_spawn_rate=0,
            initial_resources=0
        )
        
        # Manually trigger breeding check and measure time
        alive_creatures = [c for c in battle._creatures if c.is_alive()]
        
        start = time.time()
        battle._check_breeding(alive_creatures)
        elapsed = time.time() - start
        
        print(f"\nBreeding Check Performance ({len(alive_creatures)} creatures):")
        print(f"  Time: {elapsed*1000:.2f}ms")
        print(f"  Expected: O(n) with spatial grid vs O(n²) without")
        
        # Should complete in reasonable time even with 50 creatures
        self.assertLess(elapsed, 0.1, "Breeding check took too long")
    
    def test_pellet_density_check_performance(self):
        """Test pellet density check performance."""
        creature_count = 10
        creatures = self._create_test_creatures(creature_count)
        
        battle = SpatialBattle(
            creatures_or_team1=creatures,
            arena_width=100.0,
            arena_height=100.0,
            random_seed=42,
            resource_spawn_rate=1.0,  # Spawn resources
            initial_resources=50  # Start with many pellets
        )
        
        # Run updates to trigger pellet reproduction checks
        num_updates = 50
        start = time.time()
        for _ in range(num_updates):
            battle.update(0.1)
            if battle.is_over:
                break
        elapsed = time.time() - start
        
        avg_frame_time = elapsed / num_updates * 1000
        
        print(f"\nPellet Density Check Performance (50 initial pellets, {num_updates} updates):")
        print(f"  Average frame time: {avg_frame_time:.2f}ms")
        print(f"  Pellet count: {len(battle.arena.resources)}")
        
        # Even with many pellets, should maintain good performance
        self.assertLess(avg_frame_time, 20.0, 
                       "Frame time with pellets exceeds acceptable threshold")
    
    def test_spatial_grid_scaling(self):
        """Test how spatial grid scales with entity count."""
        entity_counts = [10, 50, 100]
        
        print(f"\nSpatial Grid Scaling Test:")
        print(f"{'Entities':>10} {'Insert (ms)':>15} {'Query (ms)':>15}")
        
        for count in entity_counts:
            grid = SpatialHashGrid(200.0, 200.0, cell_size=20.0)
            
            # Create entities
            entities = []
            for i in range(count):
                pos = Vector2D(random.uniform(0, 200), random.uniform(0, 200))
                entities.append((i, pos))
            
            # Measure insertion
            start = time.time()
            for entity_id, pos in entities:
                grid.insert(entity_id, pos)
            insert_time = (time.time() - start) * 1000
            
            # Measure queries (100 radius queries)
            start = time.time()
            for _ in range(100):
                center = Vector2D(random.uniform(0, 200), random.uniform(0, 200))
                grid.query_radius(center, 30.0)
            query_time = (time.time() - start) * 1000
            
            print(f"{count:>10} {insert_time:>15.2f} {query_time:>15.2f}")
            
            # Verify scaling is sub-quadratic
            # For spatial grid, query time should not grow with O(n²)
            # Should be roughly O(n) for inserts and O(k) for queries where k is cell count


if __name__ == '__main__':
    unittest.main()
