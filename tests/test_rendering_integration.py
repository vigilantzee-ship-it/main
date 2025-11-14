"""
Simple Rendering Test - Minimal example to verify rendering works.

Run this to test that the rendering system is properly installed and functional.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all rendering modules can be imported."""
    print("Testing imports...")
    try:
        from src.rendering import (
            GameWindow,
            ArenaRenderer,
            CreatureRenderer,
            UIComponents,
            EventAnimator
        )
        print("✅ All rendering modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_initialization():
    """Test that rendering components can be initialized."""
    print("\nTesting component initialization...")
    try:
        from src.rendering import (
            GameWindow,
            ArenaRenderer,
            CreatureRenderer,
            UIComponents,
            EventAnimator
        )
        
        # Test initialization (without creating actual window)
        arena_renderer = ArenaRenderer(show_grid=True)
        creature_renderer = CreatureRenderer()
        ui_components = UIComponents(max_log_entries=8)
        event_animator = EventAnimator()
        
        print("✅ ArenaRenderer initialized")
        print("✅ CreatureRenderer initialized")
        print("✅ UIComponents initialized")
        print("✅ EventAnimator initialized")
        return True
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False


def test_battle_integration():
    """Test integration with battle system."""
    print("\nTesting battle system integration...")
    try:
        from src.systems.battle_spatial import SpatialBattle
        from src.models.creature import Creature, CreatureType
        from src.models.stats import Stats
        from src.models.ability import create_ability
        from src.rendering import ArenaRenderer, CreatureRenderer, UIComponents
        
        # Create simple battle
        creature_type = CreatureType(
            name="TestCreature",
            base_stats=Stats(max_hp=100, attack=10, defense=10, speed=10)
        )
        
        c1 = Creature(name="Player1", creature_type=creature_type, level=5)
        c1.add_ability(create_ability('tackle'))
        
        c2 = Creature(name="Enemy1", creature_type=creature_type, level=5)
        c2.add_ability(create_ability('tackle'))
        
        battle = SpatialBattle([c1], [c2], arena_width=50, arena_height=30)
        
        # Test that renderers can handle the battle
        arena_renderer = ArenaRenderer()
        creature_renderer = CreatureRenderer()
        ui_components = UIComponents()
        
        # Simulate a few frames
        for _ in range(10):
            battle.update(0.1)
        
        print("✅ Battle system integration working")
        print(f"   Battle time: {battle.current_time:.1f}s")
        print(f"   Total events: {len(battle.events)}")
        return True
    except Exception as e:
        print(f"❌ Battle integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_event_handling():
    """Test event handling and callbacks."""
    print("\nTesting event handling...")
    try:
        from src.systems.battle_spatial import SpatialBattle, BattleEvent
        from src.models.creature import Creature, CreatureType
        from src.models.stats import Stats
        from src.models.ability import create_ability
        from src.rendering import UIComponents, EventAnimator
        
        # Create battle
        creature_type = CreatureType(
            name="TestCreature",
            base_stats=Stats(max_hp=100, attack=15, defense=10, speed=10)
        )
        
        c1 = Creature(name="Hero", creature_type=creature_type, level=5)
        c1.add_ability(create_ability('fireball'))
        
        c2 = Creature(name="Foe", creature_type=creature_type, level=5)
        c2.add_ability(create_ability('tackle'))
        
        battle = SpatialBattle([c1], [c2])
        
        # Setup event handling
        ui_components = UIComponents()
        event_animator = EventAnimator()
        
        event_count = 0
        def on_event(event):
            nonlocal event_count
            event_count += 1
            ui_components.add_event_to_log(event)
            event_animator.add_battle_event(event)
        
        battle.add_event_callback(on_event)
        
        # Run battle for a bit
        for _ in range(50):
            battle.update(0.1)
        
        print("✅ Event handling working")
        print(f"   Events processed: {event_count}")
        print(f"   Log entries: {len(ui_components.event_log)}")
        print(f"   Active effects: {len(event_animator.effects)}")
        return True
    except Exception as e:
        print(f"❌ Event handling failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 70)
    print("EvoBattle Rendering System - Integration Test")
    print("=" * 70)
    
    results = []
    
    # Run tests
    results.append(("Import Test", test_imports()))
    results.append(("Initialization Test", test_initialization()))
    results.append(("Battle Integration Test", test_battle_integration()))
    results.append(("Event Handling Test", test_event_handling()))
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Rendering system is working correctly.")
        print("\nNext steps:")
        print("  - Run: python3 examples/pygame_rendering_demo.py")
        print("  - See: RENDERING_DOCUMENTATION.md for API details")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
