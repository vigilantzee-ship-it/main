"""
Performance tests for rendering optimizations.

Tests the various caching and optimization features to ensure they work correctly
and provide performance improvements.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rendering import (
    ArenaRenderer,
    CreatureRenderer,
    UIComponents,
    EventAnimator,
    GameWindow
)
from src.systems.battle_spatial import SpatialBattle, BattleEvent, BattleEventType
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats
from src.models.ability import create_ability
from src.models.spatial import Vector2D


def test_grid_caching():
    """Test that grid caching works correctly."""
    print("Testing grid caching...")
    
    import pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    # Create arena renderer with grid enabled
    renderer = ArenaRenderer(show_grid=True)
    
    # Create a simple battle
    creature_type = CreatureType(
        name="TestCreature",
        base_stats=Stats(max_hp=100, attack=10, defense=10, speed=10)
    )
    c1 = Creature(name="Test1", creature_type=creature_type, level=5)
    c1.add_ability(create_ability('tackle'))
    
    battle = SpatialBattle([c1], arena_width=50, arena_height=30)
    
    # Render once to create the cache
    renderer.render(screen, battle)
    assert renderer._cached_grid_surface is not None, "Grid cache should be created"
    assert renderer._cached_grid_bounds is not None, "Grid bounds should be cached"
    
    # Store reference to cached surface
    first_surface = renderer._cached_grid_surface
    
    # Render again - should reuse cache
    renderer.render(screen, battle)
    assert renderer._cached_grid_surface is first_surface, "Grid cache should be reused"
    
    print("✅ Grid caching working correctly")
    pygame.quit()
    return True


def test_text_caching():
    """Test that text caching works correctly."""
    print("Testing text caching...")
    
    import pygame
    pygame.init()
    
    # Test CreatureRenderer text caching
    renderer = CreatureRenderer()
    
    # Get same text multiple times
    text1 = renderer._get_cached_text("Test HP: 100/100", renderer.stat_font, (255, 255, 255))
    text2 = renderer._get_cached_text("Test HP: 100/100", renderer.stat_font, (255, 255, 255))
    
    # Should return same surface object from cache
    assert text1 is text2, "Text cache should return same surface for identical text"
    assert len(renderer._text_cache) > 0, "Text cache should have entries"
    
    # Test UIComponents text caching
    ui = UIComponents()
    
    ui_text1 = ui._get_cached_text("Battle Feed", ui.text_font, (200, 200, 255))
    ui_text2 = ui._get_cached_text("Battle Feed", ui.text_font, (200, 200, 255))
    
    assert ui_text1 is ui_text2, "UI text cache should return same surface for identical text"
    assert len(ui._text_cache) > 0, "UI text cache should have entries"
    
    # Test cache limit
    for i in range(250):
        renderer._get_cached_text(f"Unique text {i}", renderer.stat_font, (255, 255, 255))
    
    # Cache should be limited (may be slightly over 200 due to the clearing threshold)
    assert len(renderer._text_cache) <= 210, f"Text cache should be limited to prevent memory issues, got {len(renderer._text_cache)}"
    
    print("✅ Text caching working correctly")
    pygame.quit()
    return True


def test_effect_pooling():
    """Test that effect object pooling works correctly."""
    print("Testing effect pooling...")
    
    import pygame
    pygame.init()
    
    animator = EventAnimator()
    
    # Create some effects
    effect1 = animator._get_effect_from_pool(
        position=(100, 100),
        text="Test",
        color=(255, 255, 255),
        lifetime=1.0,
        velocity=(0, -30)
    )
    
    assert effect1 is not None, "Should create effect"
    assert len(animator._effect_pool) == 0, "Pool should be empty after getting effect"
    
    # Return effect to pool
    animator._return_effect_to_pool(effect1)
    assert len(animator._effect_pool) == 1, "Pool should have one effect after return"
    
    # Get effect again - should reuse from pool
    effect2 = animator._get_effect_from_pool(
        position=(200, 200),
        text="Test2",
        color=(100, 100, 100),
        lifetime=2.0,
        velocity=(10, -20)
    )
    
    assert effect2 is effect1, "Should reuse effect from pool"
    assert len(animator._effect_pool) == 0, "Pool should be empty after reuse"
    assert effect2.text == "Test2", "Effect should be reset with new values"
    assert effect2.position == [200, 200], "Effect position should be reset"
    
    # Test pool size limit
    for i in range(60):
        effect = animator._get_effect_from_pool((0, 0), f"Test{i}", (255, 255, 255), 1.0, (0, 0))
        animator._return_effect_to_pool(effect)
    
    assert len(animator._effect_pool) <= animator._max_pool_size, "Pool should be limited"
    
    print("✅ Effect pooling working correctly")
    pygame.quit()
    return True


def test_fps_configuration():
    """Test FPS configuration and display."""
    print("Testing FPS configuration...")
    
    import pygame
    pygame.init()
    
    window = GameWindow(width=800, height=600, fps=30)
    
    # Test default FPS
    assert window.fps == 30, "Default FPS should be 30"
    
    # Test FPS adjustment
    window.set_fps(60)
    assert window.fps == 60, "FPS should be adjustable"
    
    # Test FPS clamping
    window.set_fps(200)
    assert window.fps == 120, "FPS should be clamped to maximum"
    
    window.set_fps(5)
    assert window.fps == 10, "FPS should be clamped to minimum"
    
    # Test FPS display toggle
    initial_state = window.show_fps
    window.toggle_fps_display()
    assert window.show_fps != initial_state, "FPS display should toggle"
    
    print("✅ FPS configuration working correctly")
    pygame.quit()
    return True


def test_grid_toggle():
    """Test that grid can be toggled on/off."""
    print("Testing grid toggle...")
    
    import pygame
    pygame.init()
    
    # Test default (should be off for performance)
    renderer1 = ArenaRenderer()
    assert renderer1.show_grid == False, "Grid should be off by default for performance"
    
    # Test explicit enable
    renderer2 = ArenaRenderer(show_grid=True)
    assert renderer2.show_grid == True, "Grid should be enabled when specified"
    
    print("✅ Grid toggle working correctly")
    pygame.quit()
    return True


def test_performance_with_large_battle():
    """Test rendering performance with a large battle."""
    print("Testing performance with large battle...")
    
    import pygame
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    
    # Create a large battle with many creatures
    creature_type = CreatureType(
        name="TestCreature",
        base_stats=Stats(max_hp=100, attack=10, defense=10, speed=10)
    )
    
    creatures = []
    for i in range(20):  # 20 creatures
        creature = Creature(name=f"Creature{i}", creature_type=creature_type, level=5)
        creature.add_ability(create_ability('tackle'))
        creatures.append(creature)
    
    battle = SpatialBattle(creatures, arena_width=100, arena_height=60)
    
    # Create renderers with optimizations
    arena_renderer = ArenaRenderer(show_grid=False)  # Grid off for performance
    creature_renderer = CreatureRenderer()
    ui_components = UIComponents()
    event_animator = EventAnimator()
    
    # Simulate several frames
    import time
    start_time = time.time()
    
    for _ in range(30):  # Render 30 frames
        battle.update(0.016)  # ~60 FPS update rate
        
        screen.fill((20, 20, 30))
        arena_renderer.render(screen, battle)
        creature_renderer.render(screen, battle)
        ui_components.render(screen, battle, False)
        event_animator.update(0.016)
        event_animator.render(screen)
    
    elapsed = time.time() - start_time
    avg_frame_time = elapsed / 30
    
    print(f"   Rendered 30 frames in {elapsed:.2f}s")
    print(f"   Average frame time: {avg_frame_time*1000:.2f}ms")
    print(f"   Estimated FPS: {1/avg_frame_time:.1f}")
    
    # Check caches are being used
    assert len(creature_renderer._text_cache) > 0, "Creature renderer should have cached text"
    assert len(ui_components._text_cache) > 0, "UI components should have cached text"
    
    print("✅ Large battle performance test passed")
    pygame.quit()
    return True


def main():
    """Run all performance tests."""
    print("=" * 70)
    print("Rendering Performance Tests")
    print("=" * 70)
    print()
    
    results = []
    
    # Run tests
    results.append(("Grid Caching", test_grid_caching()))
    results.append(("Text Caching", test_text_caching()))
    results.append(("Effect Pooling", test_effect_pooling()))
    results.append(("FPS Configuration", test_fps_configuration()))
    results.append(("Grid Toggle", test_grid_toggle()))
    results.append(("Large Battle Performance", test_performance_with_large_battle()))
    
    # Summary
    print()
    print("=" * 70)
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
        print("\n🎉 All performance tests passed!")
        print("\nPerformance optimizations are working correctly:")
        print("  - Grid caching reduces redraw overhead")
        print("  - Text caching reduces font rendering calls")
        print("  - Effect pooling reduces object allocation")
        print("  - FPS is configurable at runtime")
        print("  - Default settings optimized for performance")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
