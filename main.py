"""
EvoBattle - Evolution-based Battle Game
Main entry point for running the unified game with all features.

Combines in one cohesive experience:
- Living World with creature inspector, personalities, skills, and histories
- Pellet Evolution with visual traits and generation tracking
- Ecosystem Survival with hunger, foraging, and population dynamics
"""

import pygame
import random
import sys
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats, StatGrowth
from src.models.ability import create_ability
from src.models.trait import Trait
from src.models.ecosystem_traits import (
    AGGRESSIVE, CAUTIOUS, FORAGER, EFFICIENT_METABOLISM,
    CURIOUS, GLUTTON, VORACIOUS, WANDERER, PICKY_EATER, INDISCRIMINATE_EATER
)
from src.systems.battle_spatial import SpatialBattle
from src.systems.living_world import LivingWorldBattleEnhancer
from src.rendering import (
    GameWindow, ArenaRenderer, CreatureRenderer, PelletRenderer,
    UIComponents, EventAnimator, CreatureInspector, PauseMenu,
    PauseMenuAction, PostGameSummary
)
from src.utils.name_generator import NameGenerator


def create_creature(name: str, level: int = 5, traits: list = None) -> Creature:
    """
    Create a creature with full ecosystem, living world, and pellet features.
    
    This unified creature supports:
    - Living world: personalities, skills, history, relationships
    - Ecosystem: hunger, foraging, breeding
    - Combat: stats, abilities, tactics
    """
    if traits is None:
        # Mix of combat and ecosystem traits
        trait_pool = [AGGRESSIVE, CAUTIOUS, FORAGER, EFFICIENT_METABOLISM, 
                      CURIOUS, WANDERER]
        traits = random.sample(trait_pool, k=2)
    
    base_stats = Stats(
        max_hp=80 + level * 10,
        attack=12 + level * 2,
        defense=10 + level * 2,
        speed=15 + level
    )
    
    creature_type = CreatureType(
        name="Creature",
        base_stats=base_stats,
        type_tags=["normal"],
        stat_growth=StatGrowth(hp_growth=10.0, attack_growth=2.0)
    )
    
    creature = Creature(
        name=name,
        creature_type=creature_type,
        level=level,
        traits=traits
    )
    
    # Add abilities
    creature.add_ability(create_ability('tackle'))
    ability = create_ability('quick_strike')
    if ability:
        creature.add_ability(ability)
    
    # Initialize ecosystem features
    if hasattr(creature, "mature"):
        creature.mature = True  # Ready to breed
    
    if hasattr(creature, "hunger"):
        creature.hunger = getattr(creature, "max_hunger", 100)
    
    if hasattr(creature, "stats"):
        creature.stats.hp = getattr(creature.stats, "max_hp", creature.stats.hp)
    
    if hasattr(creature, "hue"):
        creature.hue = random.uniform(0, 360)  # For family colors
    
    return creature


def create_unified_battle():
    """
    Create a unified battle with all features enabled:
    - Living world (personalities, skills, history)
    - Pellet evolution (trait-based pellets that reproduce)
    - Ecosystem survival (hunger, foraging, breeding)
    """
    print("\n=== Creating Unified EvoBattle World ===")
    
    # Generate unique creature names
    name_gen = NameGenerator()
    num_creatures = 15
    creature_names = name_gen.generate_batch(num_creatures)
    
    creatures = []
    for i, name in enumerate(creature_names):
        level = random.randint(3, 6)
        creature = create_creature(name, level=level)
        creatures.append(creature)
    
    print(f"\nCreated {len(creatures)} creatures (sample):")
    for c in creatures[:5]:
        trait_names = [t.name for t in c.traits]
        print(f"  {c.name}: {', '.join(trait_names)} (lvl {c.level})")
        print(f"    Personality: {c.personality.get_description()}")
    if len(creatures) > 5:
        print(f"  ... and {len(creatures) - 5} more")
    
    # Create battle with balanced settings for all features
    battle = SpatialBattle(
        creatures,
        arena_width=120.0,
        arena_height=100.0,
        resource_spawn_rate=0.06,  # Reduced from 0.15 to 0.06 for better balance
        initial_resources=20  # Starting pellets
    )
    
    # Enable living world features
    enhancer = LivingWorldBattleEnhancer(battle)
    battle.enhancer = enhancer
    enhancer.on_battle_start(creatures)
    
    print("\n=== All Features Enabled ===")
    print("  ✓ Living World: Personalities, skills, history, relationships")
    print("  ✓ Pellet Evolution: Visual traits, generation tracking, reproduction")
    print("  ✓ Ecosystem: Hunger, foraging, breeding, population dynamics")
    print("  ✓ Combat: Spatial battles with abilities and tactics")
    
    return battle


def run_battle_loop(window, battle):
    """
    Run the main unified battle game loop with all features.
    
    Features include:
    - Living world: Creature inspector, personalities, skills, history
    - Pellet evolution: Visual trait rendering, generation tracking
    - Ecosystem: Hunger bars, population stats, breeding
    - Combat: Spatial battles, abilities, event animations
    
    Args:
        window: Game window
        battle: Spatial battle instance with all features enabled
    """
    # Create all renderers
    arena_renderer = ArenaRenderer(show_grid=True)
    creature_renderer = CreatureRenderer()
    pellet_renderer = PelletRenderer(base_radius=6, show_generation=True)
    ui_components = UIComponents(max_log_entries=10, show_pellet_stats=True)
    event_animator = EventAnimator()
    creature_inspector = CreatureInspector()
    pause_menu = PauseMenu()
    post_game_summary = PostGameSummary()
    
    # Connect pellet renderer to arena renderer
    arena_renderer.pellet_renderer = pellet_renderer
    
    # Subscribe to battle events
    battle.add_event_callback(ui_components.add_event_to_log)
    battle.add_event_callback(event_animator.on_battle_event)
    
    # Game state
    clock = pygame.time.Clock()
    running = True
    paused = False
    selected_battle_creature = None
    show_summary = False
    
    print("\n=== Battle Started ===")
    print("Controls:")
    print("  Click on creatures to inspect their history and stats")
    print("  I: Toggle creature inspector")
    print("  SPACE: Pause/Resume")
    print("  ESC: Pause Menu")
    print("  R: Restart (from pause menu)")
    print("\nWatch creatures develop skills, pellets evolve, and populations grow!")
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Pause menu handling
            if pause_menu.visible:
                action = pause_menu.handle_input(event)
                if action == PauseMenuAction.RESUME:
                    paused = False
                elif action == PauseMenuAction.RESTART:
                    return True  # Restart
                elif action == PauseMenuAction.QUIT:
                    return False
                continue
            
            # Post-game summary handling
            if show_summary:
                action = post_game_summary.handle_input(event)
                if action == 'menu' or action == 'replay':
                    return True  # Restart
                elif action == 'export':
                    filepath = post_game_summary.export_stats()
                    print(f"Stats exported to: {filepath}")
                continue
            
            # Inspector handling
            if creature_inspector.handle_mouse_event(event, window.screen):
                continue
            
            # Regular input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if creature_inspector.visible and not creature_inspector.is_pinned:
                        creature_inspector.hide()
                    else:
                        pause_menu.show()
                        paused = True
                elif event.key == pygame.K_SPACE:
                    if not pause_menu.visible:
                        paused = not paused
                elif event.key == pygame.K_i:
                    creature_inspector.toggle_visibility()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    clicked_creature = get_creature_at_position(
                        mouse_pos, battle, arena_renderer, window
                    )
                    if clicked_creature:
                        selected_battle_creature = clicked_creature
                        creature_inspector.select_creature(clicked_creature.creature)
                        print(f"\nSelected: {clicked_creature.creature.name}")
            
            elif event.type == pygame.MOUSEWHEEL:
                creature_inspector.handle_scroll(-event.y)
        
        # Update battle
        if not paused and not battle.is_over:
            battle.update(dt)
        
        # Update animations
        creature_inspector.update(dt)
        event_animator.update(dt)
        event_animator.process_events(window.screen, battle)
        
        # Render
        window.screen.fill((20, 20, 30))
        
        # Render arena
        arena_renderer.render(window.screen, battle)
        
        # Render pellets with evolution tracking
        pellet_renderer.render(window.screen, battle)
        
        # Render creatures
        creature_renderer.render(window.screen, battle)
        
        # Highlight selected creature
        if selected_battle_creature and selected_battle_creature.is_alive():
            screen_pos = arena_renderer.world_to_screen(
                selected_battle_creature.spatial.position,
                window.screen,
                battle.arena
            )
            pygame.draw.circle(
                window.screen,
                (255, 255, 0),
                (int(screen_pos[0]), int(screen_pos[1])),
                30,
                3
            )
        
        # Render event animations
        event_animator.render(window.screen)
        
        # Render main UI (includes battle timer, population, pellet stats, event log)
        ui_components.render(window.screen, battle, paused)
        
        # Render additional ecosystem stats
        alive_creatures = [c for c in battle.creatures if c.is_alive()]
        font = pygame.font.Font(None, 24)
        
        # Food/resource count
        resource_text = f"Food: {len(battle.arena.resources)}"
        text_surface = font.render(resource_text, True, (120, 255, 100))
        window.screen.blit(text_surface, (window.width - 150, 30))
        
        # Birth and death counts
        births_text = f"Births: {battle.birth_count}"
        births_surface = font.render(births_text, True, (100, 255, 150))
        window.screen.blit(births_surface, (window.width - 150, 60))
        
        deaths_text = f"Deaths: {battle.death_count}"
        deaths_surface = font.render(deaths_text, True, (255, 100, 100))
        window.screen.blit(deaths_surface, (window.width - 150, 90))
        
        # Render creature inspector
        creature_inspector.render(window.screen)
        
        # Render pause menu
        pause_menu.render(window.screen)
        
        # Render post-game summary
        if show_summary:
            post_game_summary.render(window.screen)
        
        # Instructions overlay
        if not pause_menu.visible and not show_summary and not creature_inspector.visible:
            instruction_text = font.render(
                "Click creatures to inspect! | I: Inspector | SPACE: Pause | ESC: Menu",
                True,
                (255, 255, 100)
            )
            text_rect = instruction_text.get_rect(center=(window.width // 2, 50))
            
            bg_rect = text_rect.inflate(20, 10)
            bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 180))
            window.screen.blit(bg_surface, bg_rect.topleft)
            window.screen.blit(instruction_text, text_rect)
        
        # Pause indicator
        if paused and not pause_menu.visible:
            pause_font = pygame.font.Font(None, 48)
            pause_text = pause_font.render("PAUSED", True, (255, 255, 100))
            text_rect = pause_text.get_rect(center=(window.width // 2, window.height // 2))
            
            s = pygame.Surface((text_rect.width + 40, text_rect.height + 20))
            s.set_alpha(200)
            s.fill((30, 30, 40))
            window.screen.blit(s, (text_rect.x - 20, text_rect.y - 10))
            window.screen.blit(pause_text, text_rect)
        
        # Show post-game summary when battle ends
        if battle.is_over and not show_summary and not pause_menu.visible:
            post_game_summary.show(battle)
            show_summary = True
        
        pygame.display.flip()
    
    return False


def get_creature_at_position(mouse_pos, battle, arena_renderer, window):
    """Find creature at mouse position."""
    click_radius = 25
    
    for bc in battle.creatures:
        if not bc.is_alive():
            continue
        
        screen_pos = arena_renderer.world_to_screen(
            bc.spatial.position,
            window.screen,
            battle.arena
        )
        dx = mouse_pos[0] - screen_pos[0]
        dy = mouse_pos[1] - screen_pos[1]
        distance = (dx * dx + dy * dy) ** 0.5
        
        if distance <= click_radius:
            return bc
    
    return None


def main():
    """Main entry point for EvoBattle - Unified living world simulator."""
    print("=" * 70)
    print("EvoBattle - Evolution-Based Living World Simulator")
    print("=" * 70)
    print("\nInitializing game systems...")
    
    # Initialize Pygame
    pygame.init()
    
    # Create window
    window = GameWindow(
        width=1400,
        height=900,
        title="EvoBattle - Living World Simulator"
    )
    
    print("✓ All systems ready!")
    
    # Main game loop - restart on request
    while True:
        # Create unified battle with all features
        battle = create_unified_battle()
        
        # Run the game
        restart = run_battle_loop(window, battle)
        
        if not restart:
            break
        
        print("\n" + "=" * 70)
        print("Restarting simulation...")
        print("=" * 70)
    
    # Cleanup
    pygame.quit()
    print("\n" + "=" * 70)
    print("Thank you for playing EvoBattle!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGame interrupted by user.")
        pygame.quit()
        sys.exit(0)
