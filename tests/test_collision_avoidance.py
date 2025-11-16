"""
Tests for collision avoidance and creature size reduction.

Verifies that:
- Creatures have reduced size (both visual and collision)
- Creatures don't overlap when in close proximity
- Collision avoidance works smoothly without jitter
- High density scenarios are handled properly
"""

import pytest
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats
from src.models.ability import create_ability
from src.models.spatial import Vector2D, SpatialEntity, Arena
from src.systems.battle_spatial import SpatialBattle, BattleCreature
from src.rendering.creature_renderer import CreatureRenderer


class TestCreatureSize:
    """Test that creature sizes have been reduced."""
    
    def test_rendering_radius_reduced(self):
        """Verify that creature rendering radius is smaller than before."""
        renderer = CreatureRenderer()
        # Should be 10 (reduced from 15)
        assert renderer.radius == 10, f"Expected radius 10, got {renderer.radius}"
    
    def test_collision_radius_reduced(self):
        """Verify that creature collision radius is smaller."""
        creature = self._create_test_creature()
        position = Vector2D(50, 50)
        battle_creature = BattleCreature(creature, position)
        
        # Should be 0.6 (reduced from 1.0)
        assert battle_creature.spatial.radius == 0.6, \
            f"Expected radius 0.6, got {battle_creature.spatial.radius}"
    
    def _create_test_creature(self):
        """Helper to create a test creature."""
        stats = Stats(max_hp=100, attack=10, defense=10, speed=10)
        creature_type = CreatureType(
            name="TestType",
            base_stats=stats,
            type_tags=["normal"]
        )
        creature = Creature(
            name="TestCreature",
            creature_type=creature_type,
            level=1
        )
        creature.add_ability(create_ability('tackle'))
        return creature


class TestCollisionAvoidance:
    """Test collision avoidance between creatures."""
    
    def test_separation_force_applied(self):
        """Test that separation force is applied when creatures are too close."""
        entity1 = SpatialEntity(position=Vector2D(50, 50), radius=0.6)
        entity2 = SpatialEntity(position=Vector2D(50.5, 50), radius=0.6)
        
        # Entities are overlapping (distance 0.5 < combined radius 1.2)
        assert entity1.is_colliding(entity2)
        
        # Apply separation force
        initial_velocity = entity1.velocity.magnitude()
        entity1.apply_separation_force(entity2, strength=1.5)
        
        # Velocity should have changed (separation force applied)
        assert entity1.velocity.magnitude() > initial_velocity
        
        # Velocity should point away from entity2
        direction = (entity1.position - entity2.position).normalized()
        velocity_dir = entity1.velocity.normalized()
        # Dot product should be positive (same general direction)
        dot_product = direction.x * velocity_dir.x + direction.y * velocity_dir.y
        assert dot_product > 0, "Separation force should push entities apart"
    
    def test_no_separation_when_not_overlapping(self):
        """Test that no separation is applied when creatures are far apart."""
        entity1 = SpatialEntity(position=Vector2D(50, 50), radius=0.6)
        entity2 = SpatialEntity(position=Vector2D(55, 50), radius=0.6)
        
        # Entities are not overlapping
        assert not entity1.is_colliding(entity2)
        
        # Apply separation force
        initial_velocity = entity1.velocity.magnitude()
        entity1.apply_separation_force(entity2, strength=1.5)
        
        # Velocity should not have changed (no separation needed)
        assert entity1.velocity.magnitude() == initial_velocity
    
    def test_boundary_repulsion(self):
        """Test that boundary repulsion keeps creatures away from walls."""
        arena = Arena(width=100, height=100)
        entity = SpatialEntity(position=Vector2D(1.0, 50), radius=0.6, max_speed=5.0)
        
        # Entity is close to left boundary
        arena.apply_boundary_repulsion(entity, margin=3.0, strength=1.2)
        
        # Should have positive x velocity (pushed away from left wall)
        assert entity.velocity.x > 0, "Should be pushed away from left boundary"
    
    def test_creatures_dont_overlap_in_battle(self):
        """Test that creatures in battle don't overlap after updates."""
        creatures = []
        for i in range(5):
            creature = self._create_test_creature(name=f"Creature{i}")
            creatures.append(creature)
        
        # Create battle with small arena to force proximity
        battle = SpatialBattle(
            creatures,
            arena_width=20.0,
            arena_height=20.0,
            resource_spawn_rate=0.0,  # No resources to avoid food-seeking behavior
            initial_resources=0
        )
        
        # Run several updates to allow creatures to move
        for _ in range(30):
            battle.update(delta_time=0.016)  # 60 FPS
        
        # Check that no creatures are overlapping
        alive_creatures = [c for c in battle.creatures if c.is_alive()]
        overlaps = 0
        
        for i, creature1 in enumerate(alive_creatures):
            for creature2 in alive_creatures[i+1:]:
                if creature1.spatial.is_colliding(creature2.spatial):
                    overlaps += 1
                    distance = creature1.spatial.distance_to(creature2.spatial)
                    min_distance = creature1.spatial.radius + creature2.spatial.radius
                    print(f"Overlap detected: {creature1.creature.name} and {creature2.creature.name}")
                    print(f"  Distance: {distance:.2f}, Min distance: {min_distance:.2f}")
        
        # Allow for very minimal overlap due to physics simulation
        # but it should be rare (< 20% of pairs)
        max_allowed_overlaps = len(alive_creatures) * (len(alive_creatures) - 1) // 10
        assert overlaps <= max_allowed_overlaps, \
            f"Too many overlaps: {overlaps} (allowed: {max_allowed_overlaps})"
    
    def test_high_density_scenario(self):
        """Test collision avoidance in high density scenario."""
        creatures = []
        for i in range(20):
            creature = self._create_test_creature(name=f"Creature{i}")
            creatures.append(creature)
        
        # Create battle with very small arena for high density
        battle = SpatialBattle(
            creatures,
            arena_width=30.0,
            arena_height=30.0,
            resource_spawn_rate=0.0,
            initial_resources=0
        )
        
        # Run updates
        for _ in range(50):
            battle.update(delta_time=0.016)
        
        # Most creatures should still be alive (not stuck or killed by overlap)
        alive_count = len([c for c in battle.creatures if c.is_alive()])
        assert alive_count >= 15, f"Too many deaths in high density: {alive_count}/20 alive"
        
        # Check average distance between creatures is reasonable
        alive_creatures = [c for c in battle.creatures if c.is_alive()]
        total_distance = 0
        pairs = 0
        
        for i, c1 in enumerate(alive_creatures):
            for c2 in alive_creatures[i+1:]:
                total_distance += c1.spatial.distance_to(c2.spatial)
                pairs += 1
        
        if pairs > 0:
            avg_distance = total_distance / pairs
            # Average distance should be at least the minimum separation
            min_separation = 1.2  # Combined radius
            assert avg_distance >= min_separation * 0.8, \
                f"Creatures too close on average: {avg_distance:.2f}"
    
    def test_movement_smoothness(self):
        """Test that collision avoidance doesn't cause jitter."""
        creatures = []
        for i in range(3):
            creature = self._create_test_creature(name=f"Creature{i}")
            creatures.append(creature)
        
        battle = SpatialBattle(
            creatures,
            arena_width=50.0,
            arena_height=50.0,
            resource_spawn_rate=0.0,
            initial_resources=0
        )
        
        # Track velocity changes for a creature
        test_creature = battle.creatures[0]
        velocity_changes = []
        
        for _ in range(30):
            old_velocity = test_creature.spatial.velocity.magnitude()
            battle.update(delta_time=0.016)
            new_velocity = test_creature.spatial.velocity.magnitude()
            velocity_changes.append(abs(new_velocity - old_velocity))
        
        # Calculate average velocity change
        avg_change = sum(velocity_changes) / len(velocity_changes)
        
        # Large velocity changes indicate jitter
        # Average change should be small (smooth movement)
        assert avg_change < 2.0, f"Movement too jerky: avg velocity change {avg_change:.2f}"
    
    def _create_test_creature(self, name="TestCreature"):
        """Helper to create a test creature."""
        stats = Stats(max_hp=100, attack=10, defense=10, speed=10)
        creature_type = CreatureType(
            name="TestType",
            base_stats=stats,
            type_tags=["normal"]
        )
        creature = Creature(
            name=name,
            creature_type=creature_type,
            level=1
        )
        creature.add_ability(create_ability('tackle'))
        return creature


class TestBoundaryHandling:
    """Test that creatures handle arena boundaries correctly."""
    
    def test_boundary_repulsion_prevents_sticking(self):
        """Test that creatures don't get stuck on boundaries."""
        creature = self._create_test_creature()
        
        battle = SpatialBattle(
            [creature],
            arena_width=50.0,
            arena_height=50.0,
            resource_spawn_rate=0.0,
            initial_resources=0
        )
        
        # Manually move creature close to a boundary and give it a target
        battle.creatures[0].spatial.position = Vector2D(1.5, 25.0)
        battle.creatures[0].spatial.velocity = Vector2D(-0.5, 0.0)  # Moving toward wall
        
        # Update several times with boundary repulsion
        for _ in range(30):
            # Manually apply boundary repulsion since creature isn't moving
            battle.arena.apply_boundary_repulsion(
                battle.creatures[0].spatial,
                margin=3.0,
                strength=1.2
            )
            battle.creatures[0].spatial.update(0.016)
        
        # Creature should have been pushed away from the boundary
        final_x = battle.creatures[0].spatial.position.x
        assert final_x > 1.5, f"Creature should have been pushed away from boundary, was at {final_x}"
    
    def _create_test_creature(self):
        """Helper to create a test creature."""
        stats = Stats(max_hp=100, attack=10, defense=10, speed=10)
        creature_type = CreatureType(
            name="TestType",
            base_stats=stats,
            type_tags=["normal"]
        )
        creature = Creature(
            name="TestCreature",
            creature_type=creature_type,
            level=1
        )
        creature.add_ability(create_ability('tackle'))
        return creature
