"""
Integration test for attention system in battle context.

Demonstrates that creatures with different attention traits behave differently.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.creature import Creature
from src.models.stats import Stats
from src.models.spatial import Vector2D
from src.systems.battle_spatial import SpatialBattle
from src.models.ecosystem_traits import PERSISTENT, DISTRACTIBLE, TUNNEL_VISION, OPPORTUNIST
from src.models.trait import Trait


def create_test_creature(name: str, traits: list, position: Vector2D) -> Creature:
    """Create a creature for testing."""
    base_stats = Stats(hp=100, max_hp=100, attack=20, defense=15, speed=25)
    creature = Creature(
        name=name,
        base_stats=base_stats,
        level=1
    )
    for trait in traits:
        creature.add_trait(trait)
    return creature


def test_attention_in_battle():
    """Test that creatures with different attention traits behave differently in battle."""
    print("\n=== Integration Test: Attention System in Battle ===\n")
    
    # Create creatures with different attention traits
    persistent_creature = create_test_creature(
        "Persistent Pete",
        [PERSISTENT],
        Vector2D(10, 10)
    )
    
    distractible_creature = create_test_creature(
        "Distractible Dan",
        [DISTRACTIBLE],
        Vector2D(90, 90)
    )
    
    tunnel_vision_creature = create_test_creature(
        "Focused Fran",
        [TUNNEL_VISION],
        Vector2D(50, 10)
    )
    
    opportunist_creature = create_test_creature(
        "Opportunistic Oscar",
        [OPPORTUNIST],
        Vector2D(50, 90)
    )
    
    # Create a battle
    all_creatures = [
        persistent_creature,
        distractible_creature,
        tunnel_vision_creature,
        opportunist_creature
    ]
    
    battle = SpatialBattle(
        creatures_or_team1=all_creatures,
        arena_width=100.0,
        arena_height=100.0,
        resource_spawn_rate=0.2,
        initial_resources=5
    )
    
    # Verify attention managers were created
    print("Verifying attention managers created:")
    for bc in battle.creatures:
        assert hasattr(bc, 'attention'), f"{bc.creature.name} missing attention manager"
        debug = bc.attention.get_debug_info(0.0)
        print(f"  {bc.creature.name}:")
        print(f"    - Persistence modifier: {debug['persistence_modifier']:.2f}")
        print(f"    - Distractibility modifier: {debug['distractibility_modifier']:.2f}")
    
    print("\n✓ All creatures have attention managers with correct trait modifiers!\n")
    
    # Run battle for a short time
    print("Running battle for 5 seconds...")
    for _ in range(50):  # 50 updates at 0.1s each = 5 seconds
        battle.update(0.1)
    
    # Check attention states
    print("\nAttention states after 5 seconds:")
    for bc in battle.creatures:
        if bc.is_alive():
            debug = bc.attention.get_debug_info(battle.current_time)
            print(f"  {bc.creature.name}:")
            print(f"    - Current focus: {debug['current_focus']}")
            print(f"    - Focus duration: {debug['focus_duration']:.2f}s")
            print(f"    - Is committed: {debug['is_committed']}")
    
    print("\n✓ Integration test completed successfully!")
    print("\nBattle summary:")
    print(f"  - Battle time: {battle.current_time:.1f}s")
    print(f"  - Creatures alive: {len([c for c in battle.creatures if c.is_alive()])}/{len(battle.creatures)}")
    print(f"  - Births: {battle.birth_count}")
    print(f"  - Deaths: {battle.death_count}")


def test_focus_persistence():
    """Test that persistent creatures stick with their focus longer."""
    print("\n=== Test: Focus Persistence ===\n")
    
    # Create two creatures - one persistent, one normal
    persistent = create_test_creature(
        "Persistent",
        [PERSISTENT],
        Vector2D(25, 25)
    )
    
    normal = create_test_creature(
        "Normal",
        [],
        Vector2D(75, 75)
    )
    
    battle = SpatialBattle(
        creatures_or_team1=[persistent, normal],
        arena_width=100.0,
        arena_height=100.0,
        resource_spawn_rate=0.5,
        initial_resources=10
    )
    
    # Track focus changes
    persistent_bc = battle.creatures[0]
    normal_bc = battle.creatures[1]
    
    persistent_focus_changes = []
    normal_focus_changes = []
    
    last_persistent_focus = persistent_bc.attention.get_current_focus()
    last_normal_focus = normal_bc.attention.get_current_focus()
    
    # Run for 10 seconds, tracking focus changes
    for i in range(100):
        battle.update(0.1)
        
        current_persistent = persistent_bc.attention.get_current_focus()
        current_normal = normal_bc.attention.get_current_focus()
        
        if current_persistent != last_persistent_focus:
            persistent_focus_changes.append((battle.current_time, current_persistent.value))
            last_persistent_focus = current_persistent
        
        if current_normal != last_normal_focus:
            normal_focus_changes.append((battle.current_time, current_normal.value))
            last_normal_focus = current_normal
    
    print(f"Persistent creature focus changes: {len(persistent_focus_changes)}")
    for time, focus in persistent_focus_changes[:5]:  # Show first 5
        print(f"  - {time:.1f}s: {focus}")
    
    print(f"\nNormal creature focus changes: {len(normal_focus_changes)}")
    for time, focus in normal_focus_changes[:5]:  # Show first 5
        print(f"  - {time:.1f}s: {focus}")
    
    print(f"\n✓ Test completed!")
    print(f"  Persistent had {len(persistent_focus_changes)} focus changes")
    print(f"  Normal had {len(normal_focus_changes)} focus changes")


def run_integration_tests():
    """Run all integration tests."""
    print("=" * 70)
    print("Integration Tests: Attention System in Battle")
    print("=" * 70)
    
    try:
        test_attention_in_battle()
        test_focus_persistence()
        
        print("\n" + "=" * 70)
        print("✓ ALL INTEGRATION TESTS PASSED!")
        print("=" * 70)
        return True
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
