#!/usr/bin/env python3
"""
Visual demonstration of the jitter fix.

This script simulates two creatures approaching each other and shows
how they stop at an appropriate distance instead of jittering.

Before the fix: Creatures would oscillate back and forth when close
After the fix: Creatures smoothly approach and stop at stopping distance
"""

from src.models.spatial import Vector2D, SpatialEntity


def test_approach_with_stopping_distance():
    """Test two creatures approaching each other with stopping distance."""
    print("=" * 70)
    print("CREATURE JITTER FIX DEMONSTRATION")
    print("=" * 70)
    print()
    print("Simulating two creatures approaching each other...")
    print()
    
    # Create two entities at opposite ends
    creature1 = SpatialEntity(
        position=Vector2D(0, 0),
        radius=0.6,
        max_speed=2.0,
        acceleration=5.0
    )
    
    creature2 = SpatialEntity(
        position=Vector2D(10, 0),
        radius=0.6,
        max_speed=2.0,
        acceleration=5.0
    )
    
    # Calculate stopping distance (like in battle system)
    stopping_distance = creature1.radius + creature2.radius + 0.5
    
    print(f"Initial setup:")
    print(f"  Creature 1: position = {creature1.position.to_tuple()}")
    print(f"  Creature 2: position = {creature2.position.to_tuple()}")
    print(f"  Starting distance: {creature1.position.distance_to(creature2.position):.2f} units")
    print(f"  Stopping distance: {stopping_distance:.2f} units")
    print(f"  Melee attack range: 4.0 units (for reference)")
    print()
    print("Approaching...")
    print()
    
    # Track key moments
    entered_decel_zone = False
    reached_stopping = False
    
    # Simulate movement
    for step in range(500):
        distance = creature1.position.distance_to(creature2.position)
        
        # Move towards each other with stopping distance
        creature1.move_towards(
            creature2.position,
            delta_time=0.016,
            stopping_distance=stopping_distance
        )
        creature2.move_towards(
            creature1.position,
            delta_time=0.016,
            stopping_distance=stopping_distance
        )
        
        # Update positions
        creature1.update(0.016)
        creature2.update(0.016)
        
        new_distance = creature1.position.distance_to(creature2.position)
        
        # Report key moments
        decel_zone = stopping_distance + max(3.0, creature1.max_speed * 2.0)
        
        if not entered_decel_zone and new_distance < decel_zone:
            entered_decel_zone = True
            print(f"Step {step:3d}: Entering deceleration zone")
            print(f"           Distance = {new_distance:.3f}, Velocity = {creature1.velocity.magnitude():.3f}")
            print()
        
        if not reached_stopping and new_distance <= stopping_distance * 1.1:
            reached_stopping = True
            print(f"Step {step:3d}: Reached stopping distance")
            print(f"           Distance = {new_distance:.3f}, Velocity = {creature1.velocity.magnitude():.3f}")
            print()
        
        # Check for equilibrium
        total_velocity = creature1.velocity.magnitude() + creature2.velocity.magnitude()
        if total_velocity < 0.02 and step > 100:
            print(f"Step {step:3d}: Equilibrium reached!")
            print(f"           Final distance = {new_distance:.3f}")
            print(f"           Combined velocity = {total_velocity:.4f}")
            break
        
        # Periodic status updates during deceleration
        if entered_decel_zone and step % 50 == 0:
            print(f"Step {step:3d}: Distance = {new_distance:.3f}, Velocity = {creature1.velocity.magnitude():.3f}")
    
    # Final report
    final_distance = creature1.position.distance_to(creature2.position)
    print()
    print("=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    print(f"Final distance between creatures: {final_distance:.3f} units")
    print(f"Target stopping distance: {stopping_distance:.2f} units")
    print(f"Difference from target: {abs(final_distance - stopping_distance):.3f} units")
    print()
    
    # Check if within attack range
    melee_range = 4.0
    can_attack = final_distance <= melee_range
    
    print("Combat readiness:")
    print(f"  Can perform melee attack? {'✓ YES' if can_attack else '✗ NO'}")
    print(f"  Distance to attack range limit: {melee_range - final_distance:.2f} units")
    print()
    
    # Success check
    if abs(final_distance - stopping_distance) < 0.3:
        print("✓ SUCCESS: Creatures stopped at appropriate distance without jittering!")
    else:
        print("✗ WARNING: Creatures did not reach target distance")
    print()
    
    return final_distance, stopping_distance


def test_jitter_prevention():
    """Test that creatures don't jitter when at stopping distance."""
    print("=" * 70)
    print("JITTER PREVENTION TEST")
    print("=" * 70)
    print()
    print("Testing stability when creatures are at stopping distance...")
    print()
    
    # Create entities already at stopping distance
    stopping_distance = 1.7
    
    creature1 = SpatialEntity(
        position=Vector2D(0, 0),
        radius=0.6,
        max_speed=2.0,
        acceleration=5.0
    )
    
    creature2 = SpatialEntity(
        position=Vector2D(stopping_distance, 0),
        radius=0.6,
        max_speed=2.0,
        acceleration=5.0
    )
    
    initial_distance = creature1.position.distance_to(creature2.position)
    print(f"Initial distance: {initial_distance:.3f} units (at stopping distance)")
    print()
    
    # Track position changes
    positions = []
    
    # Simulate 100 frames
    for step in range(100):
        # Both try to move towards each other (simulating continuous targeting)
        creature1.move_towards(
            creature2.position,
            delta_time=0.016,
            stopping_distance=stopping_distance
        )
        creature2.move_towards(
            creature1.position,
            delta_time=0.016,
            stopping_distance=stopping_distance
        )
        
        creature1.update(0.016)
        creature2.update(0.016)
        
        distance = creature1.position.distance_to(creature2.position)
        positions.append(distance)
    
    # Analyze stability
    min_dist = min(positions)
    max_dist = max(positions)
    variation = max_dist - min_dist
    
    print(f"After 100 frames:")
    print(f"  Minimum distance: {min_dist:.3f}")
    print(f"  Maximum distance: {max_dist:.3f}")
    print(f"  Variation: {variation:.3f} units")
    print()
    
    if variation < 0.5:
        print("✓ SUCCESS: Creatures remain stable without jittering!")
        print(f"  (Variation of {variation:.3f} units is within acceptable bounds)")
    else:
        print("✗ WARNING: Excessive movement detected")
        print(f"  (Variation of {variation:.3f} units may indicate jittering)")
    print()


if __name__ == "__main__":
    # Run both tests
    test_approach_with_stopping_distance()
    print("\n")
    test_jitter_prevention()
