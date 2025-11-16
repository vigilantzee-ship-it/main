"""
Demo script to visualize collision avoidance and creature size reduction.

This script runs a visual simulation showing:
- Reduced creature sizes
- Creatures avoiding overlaps through separation forces
- Smooth pathfinding around clusters
- Boundary repulsion preventing wall-sticking

Press ESC to exit.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats
from src.models.ability import create_ability
from src.systems.battle_spatial import SpatialBattle
from src.rendering import (
    GameWindow,
    ArenaRenderer,
    CreatureRenderer,
    UIComponents
)


def create_test_creature(name: str, level: int = 5) -> Creature:
    """Create a test creature."""
    base_stats = Stats(
        max_hp=100,
        attack=15,
        defense=10,
        speed=20 + level
    )
    
    creature_type = CreatureType(
        name=f"{name} Type",
        base_stats=base_stats,
        type_tags=["normal"]
    )
    
    creature = Creature(
        name=name,
        creature_type=creature_type,
        level=level
    )
    
    creature.add_ability(create_ability('tackle'))
    return creature


def main():
    """Run the collision avoidance demo."""
    # Initialize pygame
    pygame.init()
    
    # Create window
    window = GameWindow(width=1400, height=900, title="Collision Avoidance Demo")
    
    # Create creatures with variety in levels/speeds
    creatures = []
    for i in range(25):
        level = 3 + (i % 5)
        creature = create_test_creature(f"Creature{i+1}", level=level)
        creatures.append(creature)
    
    # Create battle with moderate arena size for density
    battle = SpatialBattle(
        creatures,
        arena_width=80.0,
        arena_height=60.0,
        resource_spawn_rate=0.2,
        initial_resources=15
    )
    
    # Create renderers
    arena_renderer = ArenaRenderer()
    creature_renderer = CreatureRenderer()  # Now with reduced radius
    ui_components = UIComponents()
    
    # Game loop
    clock = pygame.time.Clock()
    running = True
    paused = False
    
    print("\n" + "="*60)
    print("COLLISION AVOIDANCE DEMO")
    print("="*60)
    print("\nFeatures demonstrated:")
    print("  • Creatures are smaller (radius: 10px rendering, 0.6 world units)")
    print("  • Separation forces prevent overlapping")
    print("  • Boundary repulsion prevents wall-sticking")
    print("  • Smooth pathfinding around clusters")
    print("\nControls:")
    print("  • SPACE: Pause/Resume")
    print("  • ESC: Exit")
    print("="*60 + "\n")
    
    frame_count = 0
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
        
        # Update battle (if not paused)
        if not paused:
            battle.update(delta_time=1/60.0)
        
        # Render
        window.screen.fill((20, 20, 30))  # Dark background
        
        # Draw arena
        arena_renderer.render(window.screen, battle)
        
        # Draw creatures
        creature_renderer.render(window.screen, battle)
        
        # Draw UI
        ui_components.render(window.screen, battle, paused)
        
        # Draw info text
        font = pygame.font.Font(None, 24)
        
        # Count overlaps
        overlaps = 0
        alive_creatures = [c for c in battle.creatures if c.is_alive()]
        for i, c1 in enumerate(alive_creatures):
            for c2 in alive_creatures[i+1:]:
                if c1.spatial.is_colliding(c2.spatial):
                    overlaps += 1
        
        info_lines = [
            f"Frame: {frame_count}",
            f"Alive: {len(alive_creatures)}/{len(battle.creatures)}",
            f"Overlaps: {overlaps}",
            f"Radius: {creature_renderer.radius}px (render), {battle.creatures[0].spatial.radius} (physics)",
            "SPACE: Pause  ESC: Exit"
        ]
        
        y_offset = 10
        for line in info_lines:
            text = font.render(line, True, (255, 255, 255))
            window.screen.blit(text, (10, y_offset))
            y_offset += 25
        
        # Update display
        pygame.display.flip()
        clock.tick(60)  # 60 FPS
        
        frame_count += 1
        
        # Auto-exit after a while for automated testing
        if frame_count > 600:  # 10 seconds at 60 FPS
            print(f"\nDemo completed successfully!")
            print(f"Final stats: {len(alive_creatures)} alive, {overlaps} overlaps")
            running = False
    
    pygame.quit()


if __name__ == "__main__":
    main()
