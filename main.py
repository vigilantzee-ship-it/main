"""
EvoBattle - Evolution-based Battle Game
Main entry point for running the unified game with all features.

Combines:
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
from src.models.ecosystem_traits import (
    AGGRESSIVE, CAUTIOUS, FORAGER, EFFICIENT_METABOLISM,
    CURIOUS, GLUTTON, VORACIOUS, WANDERER
)
from src.systems.battle_spatial import SpatialBattle
from src.systems.living_world import LivingWorldBattleEnhancer
from src.rendering import (
    GameWindow, ArenaRenderer, CreatureRenderer, PelletRenderer,
    UIComponents, EventAnimator, CreatureInspector, PauseMenu,
    PauseMenuAction, PostGameSummary
)
from src.utils.name_generator import NameGenerator


# Game modes
MODE_LIVING_WORLD = "living_world"
MODE_PELLET_EVOLUTION = "pellet_evolution"
MODE_ECOSYSTEM_SURVIVAL = "ecosystem_survival"


def create_warrior(name: str, level: int = 5, traits: list = None) -> Creature:
    """Create a warrior creature for living world mode."""
    if traits is None:
        traits = [random.choice([AGGRESSIVE, CAUTIOUS])]
    
    base_stats = Stats(
        max_hp=80 + level * 10,
        attack=12 + level * 2,
        defense=10 + level * 2,
        speed=15 + level
    )
    
    creature_type = CreatureType(
        name="Warrior",
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
    
    creature.add_ability(create_ability('tackle'))
    ability = create_ability('quick_strike')
    if ability:
        creature.add_ability(ability)
    
    return creature


def create_ecosystem_creature(name: str, traits: list, level: int = 5) -> Creature:
    """Create a creature for ecosystem simulation."""
    base_stats = Stats(
        max_hp=80 + (level - 1) * 10,
        attack=12 + (level - 1) * 2,
        defense=10 + (level - 1) * 2,
        speed=15 + (level - 1)
    )
    
    creature_type = CreatureType(
        name=f"{name} Type",
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
    
    creature.add_ability(create_ability('tackle'))
    
    return creature


def show_main_menu(window):
    """
    Show the main menu and return selected mode.
    
    Returns:
        str: Selected mode or None to quit
    """
    font_title = pygame.font.Font(None, 64)
    font_option = pygame.font.Font(None, 36)
    font_desc = pygame.font.Font(None, 24)
    
    title = "EvoBattle"
    subtitle = "Evolution-Based Living World Simulator"
    
    options = [
        (MODE_LIVING_WORLD, "Living World Battle", 
         "Creatures with personalities, skills, and rivalries"),
        (MODE_PELLET_EVOLUTION, "Pellet Evolution", 
         "Watch pellets evolve through reproduction and mutation"),
        (MODE_ECOSYSTEM_SURVIVAL, "Ecosystem Survival", 
         "Population dynamics with hunger and breeding"),
    ]
    
    selected = 0
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return options[selected][0]
        
        # Render menu
        window.screen.fill((20, 20, 30))
        
        # Title
        title_surface = font_title.render(title, True, (255, 215, 100))
        title_rect = title_surface.get_rect(center=(window.width // 2, 100))
        window.screen.blit(title_surface, title_rect)
        
        # Subtitle
        subtitle_surface = font_desc.render(subtitle, True, (180, 180, 180))
        subtitle_rect = subtitle_surface.get_rect(center=(window.width // 2, 160))
        window.screen.blit(subtitle_surface, subtitle_rect)
        
        # Options
        y_offset = 250
        for i, (mode, name, desc) in enumerate(options):
            color = (255, 255, 100) if i == selected else (200, 200, 200)
            
            # Option name
            option_surface = font_option.render(name, True, color)
            option_rect = option_surface.get_rect(center=(window.width // 2, y_offset))
            
            # Highlight selected
            if i == selected:
                highlight_rect = option_rect.inflate(40, 20)
                pygame.draw.rect(window.screen, (60, 60, 80), highlight_rect, border_radius=10)
            
            window.screen.blit(option_surface, option_rect)
            
            # Description
            desc_surface = font_desc.render(desc, True, (150, 150, 150))
            desc_rect = desc_surface.get_rect(center=(window.width // 2, y_offset + 35))
            window.screen.blit(desc_surface, desc_rect)
            
            y_offset += 100
        
        # Instructions
        instructions = "Use ↑↓ to navigate, ENTER to select, ESC to quit"
        inst_surface = font_desc.render(instructions, True, (120, 120, 120))
        inst_rect = inst_surface.get_rect(center=(window.width // 2, window.height - 50))
        window.screen.blit(inst_surface, inst_rect)
        
        pygame.display.flip()
        clock.tick(60)


def run_living_world_mode(window):
    """Run the living world battle mode with creature inspector."""
    print("\n=== Living World Battle Mode ===")
    
    # Generate creature names
    name_gen = NameGenerator()
    warrior_names = name_gen.generate_batch(8)
    
    # Create warriors with personalities
    warriors = []
    for i, name in enumerate(warrior_names):
        level = random.randint(3, 6)
        trait = random.choice([AGGRESSIVE, CAUTIOUS])
        warrior = create_warrior(name, level=level, traits=[trait])
        warriors.append(warrior)
    
    print(f"\nCreated {len(warriors)} warriors:")
    for w in warriors:
        print(f"  {w.name}: {w.personality.get_description()} (lvl {w.level})")
    
    # Create battle
    battle = SpatialBattle(
        warriors,
        arena_width=120.0,
        arena_height=90.0,
        resource_spawn_rate=0.0
    )
    
    # Add living world enhancer
    enhancer = LivingWorldBattleEnhancer(battle)
    battle.enhancer = enhancer
    enhancer.on_battle_start(warriors)
    
    # Create renderers
    arena_renderer = ArenaRenderer(show_grid=True)
    creature_renderer = CreatureRenderer()
    ui_components = UIComponents(max_log_entries=10)
    event_animator = EventAnimator()
    creature_inspector = CreatureInspector()
    pause_menu = PauseMenu()
    post_game_summary = PostGameSummary()
    
    # Subscribe to events
    battle.add_event_callback(ui_components.add_event_to_log)
    battle.add_event_callback(event_animator.on_battle_event)
    
    # Run battle loop
    return run_battle_loop(
        window, battle, arena_renderer, creature_renderer,
        ui_components, event_animator, creature_inspector,
        pause_menu, post_game_summary,
        show_inspector=True
    )


def run_pellet_evolution_mode(window):
    """Run the pellet evolution visualization mode."""
    print("\n=== Pellet Evolution Mode ===")
    
    # Generate creature names
    name_gen = NameGenerator()
    creature_names = name_gen.generate_batch(6)
    
    creatures = []
    # Create herbivores
    for i in range(4):
        from src.models.trait import Trait
        creature = Creature(
            name=creature_names[i],
            hunger=100,
            traits=[Trait(name="Herbivore")]
        )
        creatures.append(creature)
    
    # Create omnivores
    for i in range(4, 6):
        creature = Creature(
            name=creature_names[i],
            hunger=100,
            traits=[]
        )
        creatures.append(creature)
    
    print(f"\nCreated {len(creatures)} creatures:")
    for c in creatures:
        trait_names = [t.name for t in c.traits] if c.traits else ["Omnivore"]
        print(f"  {c.name}: {', '.join(trait_names)}")
    
    # Create battle
    battle = SpatialBattle(
        creatures,
        arena_width=120.0,
        arena_height=120.0,
        resource_spawn_rate=0.2,
        initial_resources=15
    )
    
    # Create renderers with pellet focus
    arena_renderer = ArenaRenderer(show_grid=True)
    pellet_renderer = PelletRenderer(base_radius=6, show_generation=True)
    creature_renderer = CreatureRenderer(radius=15)
    ui_components = UIComponents(show_pellet_stats=True)
    event_animator = EventAnimator()
    pause_menu = PauseMenu()
    post_game_summary = PostGameSummary()
    
    # Connect pellet renderer
    arena_renderer.pellet_renderer = pellet_renderer
    
    # Subscribe to events
    battle.add_event_callback(ui_components.add_event_to_log)
    battle.add_event_callback(event_animator.on_battle_event)
    
    # Run battle loop
    return run_battle_loop(
        window, battle, arena_renderer, creature_renderer,
        ui_components, event_animator, None,
        pause_menu, post_game_summary,
        pellet_renderer=pellet_renderer
    )


def run_ecosystem_survival_mode(window):
    """Run the ecosystem survival mode with hunger and breeding."""
    print("\n=== Ecosystem Survival Mode ===")
    
    # Generate creature names
    name_gen = NameGenerator()
    num_founders = 20
    creature_names = name_gen.generate_batch(num_founders)
    
    trait_pool = [FORAGER, EFFICIENT_METABOLISM, CURIOUS, GLUTTON, 
                  VORACIOUS, AGGRESSIVE, CAUTIOUS, WANDERER]
    
    founders = []
    for i, name in enumerate(creature_names):
        traits = random.sample(trait_pool, k=2)
        level = random.randint(3, 6)
        creature = create_ecosystem_creature(name, traits, level=level)
        
        # Mark as mature
        if hasattr(creature, "mature"):
            creature.mature = True
        
        # Initialize hunger
        if hasattr(creature, "hunger"):
            creature.hunger = getattr(creature, "max_hunger", 100)
        
        # Full HP
        if hasattr(creature, "stats"):
            creature.stats.hp = getattr(creature.stats, "max_hp", creature.stats.hp)
        
        # Random hue
        if hasattr(creature, "hue"):
            creature.hue = random.uniform(0, 360)
        
        founders.append(creature)
    
    print(f"\nCreated {num_founders} founders (sample):")
    for c in founders[:5]:
        trait_names = [t.name for t in c.traits]
        print(f"  {c.name}: {', '.join(trait_names)} (lvl {c.level})")
    print(f"  ... and {num_founders - 5} more")
    
    # Create battle
    battle = SpatialBattle(
        founders,
        arena_width=100.0,
        arena_height=100.0,
        resource_spawn_rate=0.15,
        initial_resources=20
    )
    
    # Create renderers
    arena_renderer = ArenaRenderer(show_grid=True)
    creature_renderer = CreatureRenderer(radius=15)
    ui_components = UIComponents()
    event_animator = EventAnimator()
    pause_menu = PauseMenu()
    post_game_summary = PostGameSummary()
    
    # Subscribe to events
    battle.add_event_callback(event_animator.on_battle_event)
    
    # Run battle loop
    return run_battle_loop(
        window, battle, arena_renderer, creature_renderer,
        ui_components, event_animator, None,
        pause_menu, post_game_summary,
        show_population_stats=True
    )


def run_battle_loop(
    window, battle, arena_renderer, creature_renderer,
    ui_components, event_animator, creature_inspector,
    pause_menu, post_game_summary,
    pellet_renderer=None, show_inspector=False, show_population_stats=False
):
    """
    Run the main battle game loop.
    
    Args:
        window: Game window
        battle: Spatial battle instance
        arena_renderer: Arena renderer
        creature_renderer: Creature renderer
        ui_components: UI components
        event_animator: Event animator
        creature_inspector: Creature inspector (or None)
        pause_menu: Pause menu
        post_game_summary: Post-game summary
        pellet_renderer: Optional pellet renderer
        show_inspector: Whether inspector is available
        show_population_stats: Whether to show population stats
        
    Returns:
        bool: True to return to menu, False to quit
    """
    clock = pygame.time.Clock()
    running = True
    paused = False
    selected_battle_creature = None
    show_summary = False
    
    print("\n=== Battle Started ===")
    print("Controls:")
    if show_inspector:
        print("  Click on creatures to inspect")
        print("  I: Toggle inspector")
    print("  SPACE: Pause/Resume")
    print("  ESC: Pause Menu")
    print("  R: Restart (in pause menu)")
    
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
                    return True  # Return to menu
                elif action == PauseMenuAction.QUIT:
                    return False
                continue
            
            # Post-game summary handling
            if show_summary:
                action = post_game_summary.handle_input(event)
                if action == 'menu':
                    return True
                elif action == 'replay':
                    return True
                elif action == 'export':
                    filepath = post_game_summary.export_stats()
                    print(f"Stats exported to: {filepath}")
                continue
            
            # Inspector handling
            if show_inspector and creature_inspector:
                if creature_inspector.handle_mouse_event(event, window.screen):
                    continue
            
            # Regular input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if show_inspector and creature_inspector and creature_inspector.visible and not creature_inspector.is_pinned:
                        creature_inspector.hide()
                    else:
                        pause_menu.show()
                        paused = True
                elif event.key == pygame.K_SPACE:
                    if not pause_menu.visible:
                        paused = not paused
                elif event.key == pygame.K_i and show_inspector and creature_inspector:
                    creature_inspector.toggle_visibility()
            
            elif event.type == pygame.MOUSEBUTTONDOWN and show_inspector and creature_inspector:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    clicked_creature = get_creature_at_position(
                        mouse_pos, battle, arena_renderer, window
                    )
                    if clicked_creature:
                        selected_battle_creature = clicked_creature
                        creature_inspector.select_creature(clicked_creature.creature)
            
            elif event.type == pygame.MOUSEWHEEL and show_inspector and creature_inspector:
                creature_inspector.handle_scroll(-event.y)
        
        # Update battle
        if not paused and not battle.is_over:
            battle.update(dt)
        
        # Update animations
        if show_inspector and creature_inspector:
            creature_inspector.update(dt)
        event_animator.update(dt)
        event_animator.process_events(window.screen, battle)
        
        # Render
        window.screen.fill((20, 20, 30))
        
        # Render arena
        arena_renderer.render(window.screen, battle)
        
        # Render pellets if applicable
        if pellet_renderer:
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
        
        # Render animations
        event_animator.render(window.screen)
        
        # Render UI
        ui_components.render(window.screen, battle, paused)
        
        # Population stats if requested
        if show_population_stats:
            alive_creatures = [c for c in battle.creatures if c.is_alive()]
            font = pygame.font.Font(None, 24)
            
            # Food count
            resource_text = f"Food: {len(battle.arena.resources)}"
            text_surface = font.render(resource_text, True, (120, 255, 100))
            window.screen.blit(text_surface, (window.width - 150, 30))
            
            # Births/Deaths
            births_text = f"Births: {battle.birth_count}"
            births_surface = font.render(births_text, True, (100, 255, 150))
            window.screen.blit(births_surface, (window.width - 150, 60))
            
            deaths_text = f"Deaths: {battle.death_count}"
            deaths_surface = font.render(deaths_text, True, (255, 100, 100))
            window.screen.blit(deaths_surface, (window.width - 150, 90))
        
        # Render inspector
        if show_inspector and creature_inspector:
            creature_inspector.render(window.screen)
        
        # Render pause menu
        pause_menu.render(window.screen)
        
        # Render post-game summary
        if show_summary:
            post_game_summary.render(window.screen)
        
        # Instructions overlay
        if not pause_menu.visible and not show_summary:
            if show_inspector and creature_inspector and not creature_inspector.visible:
                font = pygame.font.Font(None, 24)
                instruction_text = font.render(
                    "Click creatures to inspect! Press I, ESC for menu, SPACE to pause",
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
        
        # Battle result
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
    """Main entry point for EvoBattle."""
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
    print("\nStarting main menu...")
    
    # Main menu loop
    while True:
        mode = show_main_menu(window)
        
        if mode is None:
            break
        
        print(f"\nStarting mode: {mode}")
        
        # Run selected mode
        if mode == MODE_LIVING_WORLD:
            continue_to_menu = run_living_world_mode(window)
        elif mode == MODE_PELLET_EVOLUTION:
            continue_to_menu = run_pellet_evolution_mode(window)
        elif mode == MODE_ECOSYSTEM_SURVIVAL:
            continue_to_menu = run_ecosystem_survival_mode(window)
        else:
            print(f"Unknown mode: {mode}")
            continue_to_menu = True
        
        if not continue_to_menu:
            break
    
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
