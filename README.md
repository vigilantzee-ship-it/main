# Evolution Battle Game

## Project Description
This is an evolution-based battle game where players can engage in battles, breed their fighters, and place bets. Every creature has a unique story, personality, and history that makes them memorable.

## Features

### AI-Powered Battle Stories ✓ NEW!
Transform battles into shareable narratives with AI-generated story summaries:
- **Automatic Story Generation**: AI creates engaging battle reports every 5 minutes (configurable)
- **Multiple Tones**: Choose from dramatic, heroic, comedic, serious, or documentary styles
- **Story Viewer UI**: Dedicated panel with scrollable text, tone selection, and export options
- **Export & Share**: Save stories as TXT or Markdown files
- **Key Moments**: Highlights MVPs, turning points, alliances, betrayals, and dramatic events
- **Works Offline**: Fallback mode generates structured summaries without AI API

See [Battle Story Mode Documentation](BATTLE_STORY_MODE_DOCUMENTATION.md) for details.

### Living World System ✓
Transform battles into emergent narratives where every creature matters:
- **Individual Histories**: Track every attack, kill, achievement, and life event
- **Skill Progression**: Skills improve through use (Melee Attack, Dodge, Critical Strike, etc.)
- **Unique Personalities**: 7 personality traits affect behavior (aggression, caution, loyalty, pride, etc.)
- **Dynamic Relationships**: Family bonds, rivalries, alliances, and revenge arcs
- **Achievement System**: Celebrate exceptional moments (Giant Slayer, First Blood, etc.)
- **Creature Inspector UI**: Click creatures to see their full history and stats
- **Emergent Stories**: Watch legendary creatures rise and dramatic rivalries form

See [Living World Documentation](LIVING_WORLD_DOCUMENTATION.md) for details.

### Battle System ✓
A comprehensive turn-based combat engine featuring:
- Speed-based turn order with random tiebreaking
- Complex damage calculation with type effectiveness
- Status effects (poison, burn, sleep, paralysis, etc.)
- Buff/debuff system for strategic gameplay
- Multiple ability types (physical, special, healing, buff, debuff)
- Complete battle logging for analysis and replay

See [Battle System Documentation](BATTLE_SYSTEM_DOCUMENTATION.md) for details.

### Creature System ✓
Full creature management including:
- Stats and stat modifiers
- Level and experience system
- Ability learning and cooldowns
- Trait system for genetic characteristics
- Evolution paths and breeding mechanics

See [Core Models Documentation](MODELS_DOCUMENTATION.md) for details.

### Ecosystem Survival System ✓
A complete survival ecosystem simulation featuring:
- Hunger system with metabolic traits
- Resource gathering and foraging behavior
- Trait-driven wandering and exploration
- Starvation mechanics
- Dynamic behavior based on hunger levels
- 15+ predefined ecosystem traits (Forager, Efficient Metabolism, Curious, etc.)

See [Ecosystem Documentation](ECOSYSTEM_DOCUMENTATION.md) for details.

### Grass Growth Enhancement System ✓ NEW!
Dynamic pellet (food) growth using simulation-based mechanics:
- **Nutrient Zones**: Pellets grow faster where creatures died (1.05-1.15x boost, lasts 30s)
- **Pollination**: Creatures spread seeds as they move (3% chance on revisit)
- **Growth Pulses**: Periodic environmental boosts (10% boost every 60s for 8s)
- **Symbiotic Bonus**: Herbivores enhance nearby grass growth (up to 8% boost)
- **Spatial Patterns**: Pellets cluster around death sites and herbivore paths
- **Balanced Growth**: 100% increase over 30s with zones vs 40% baseline

See [Grass Growth System Documentation](GRASS_GROWTH_SYSTEM.md) for details.

### Lethal Combat Traits ✓ NEW!
High-risk, high-reward combat traits that enable dramatic kills and apex predators:
- **10 New Offensive Traits**: Berserker, Executioner, Bloodthirsty, Brutal, Assassin, Apex Predator, Reckless Fury, Toxic, Frenzied, Vampiric
- **Advanced Mechanics**: Bleed, poison, lifesteal, execute, multi-strike, armor penetration
- **Glass Cannon Builds**: High offense with defensive trade-offs
- **Scaling Effects**: Kill streaks, rage mode, fear auras
- **Strategic Depth**: Counter-play and archetype diversity

See [Lethal Combat Traits Documentation](LETHAL_COMBAT_TRAITS_DOCUMENTATION.md) for details.

### Genetic Lineage System ✓
An evolutionary ecosystem where creatures form dynamic genetic families:
- Strain-based families instead of fixed teams
- Color-coded genetic similarity (hue represents lineage)
- Trait inheritance with mutations (add/remove/modify traits)
- Natural selection and strain extinction
- Population analytics tracking dominant/extinct strains
- Visual evolution through color spectrum changes

See [Lineage System Documentation](LINEAGE_SYSTEM_DOCUMENTATION.md) for details.

## Quick Start

```python
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats
from src.models.ability import create_ability
from src.systems.battle import Battle

# Create creatures
warrior_type = CreatureType(
    name="Warrior",
    base_stats=Stats(max_hp=120, attack=15, defense=12, speed=10)
)

player = Creature(name="Hero", creature_type=warrior_type, level=5)
player.add_ability(create_ability('tackle'))

enemy = Creature(name="Foe", creature_type=warrior_type, level=5)
enemy.add_ability(create_ability('tackle'))

# Run battle
battle = Battle([player], [enemy])
winner = battle.simulate()

print(f"Winner: {winner.name}")
for log in battle.get_battle_log():
    print(log)
```

## For Developers

### Agent Coordination
This project is developed by three specialist agents working in coordination:
- **Core Gameplay Engineer** - Implements game mechanics, physics, and player interaction ([Issue #11](https://github.com/dbmelville2-jpg/evobattle/issues/11))
- **Graphics & Rendering Agent** - Handles visual systems, animations, and UI ([Issue #12](https://github.com/dbmelville2-jpg/evobattle/issues/12))
- **Data & Systems Agent** - Manages game state, persistence, and support systems ([Issue #13](https://github.com/dbmelville2-jpg/evobattle/issues/13))

**Important Documentation:**
- [**Battle Story Mode Documentation**](BATTLE_STORY_MODE_DOCUMENTATION.md) - **NEW!** AI-powered battle narratives
- [**Living World Documentation**](LIVING_WORLD_DOCUMENTATION.md) - Creature histories, skills, personalities, relationships
- [Battle System Documentation](BATTLE_SYSTEM_DOCUMENTATION.md) - Complete battle system guide
- [Core Models Documentation](MODELS_DOCUMENTATION.md) - Creature, stats, and ability systems
- [Ecosystem Documentation](ECOSYSTEM_DOCUMENTATION.md) - Hunger, foraging, and survival mechanics
- [Lineage System Documentation](LINEAGE_SYSTEM_DOCUMENTATION.md) - Genetic strains and evolution
- [Rendering Documentation](RENDERING_DOCUMENTATION.md) - Visual rendering and animation systems
- [Agent Coordination Guide](AGENT_COORDINATION.md) - Team standards, interface contracts, and integration goals
- [Integration Checklist](INTEGRATION_CHECKLIST.md) - Track implementation progress and integration milestones
- [Project Architect Vision](https://github.com/dbmelville2-jpg/evobattle/issues/2) - Overall project leadership and vision

### Running Examples

All examples should be run from the project root directory using Python's module syntax:

```bash
# Battle Story Mode demo (NEW!)
python3 -m examples.battle_story_mode_demo  # AI-powered battle narratives

# Living World demos
python3 -m examples.living_world_demo              # Text-based: See histories and skills
python3 -m examples.interactive_living_world_demo  # Visual: Click creatures to inspect

# Battle system examples
python3 -m examples.battle_system_example

# Core models examples
python3 -m examples.core_models_example

# Spatial battle examples
python3 -m examples.spatial_battle_example

# Ecosystem survival simulation (text-based)
python3 -m examples.ecosystem_survival_demo

# Ecosystem survival with Pygame visualization
python3 -m examples.ecosystem_pygame_demo

# Genetic strain evolution demo (shows lineage system)
python3 -m examples.genetic_strain_demo

# Real-time battle example
python3 -m examples.realtime_battle_example

# Pygame rendering demo
python3 -m examples.pygame_rendering_demo
```

### Pygame Rendering Demo

Watch battles in real-time with full visual rendering:

```bash
# Run the Pygame visualization demo
python3 -m examples.pygame_rendering_demo
```

**Features:**
- Real-time 2D arena visualization
- Creature movement and combat animations
- HP/energy bars and status indicators
- Event log showing battle actions
- Interactive controls (SPACE to pause, ESC to exit)

### Ecosystem Survival Demo

Experience the complete survival ecosystem with hunger and foraging:

```bash
# Run the Ecosystem Survival Pygame demo
python3 -m examples.ecosystem_pygame_demo
```

**Features:**
- Hunger bars showing creature survival status
- Food resources scattered in arena
- Creatures seeking food when hungry
- Diverse metabolic traits affecting behavior
- Real-time survival simulation
- Interactive controls (SPACE to pause, R to restart, ESC to exit)

**Controls:**
- `SPACE` - Pause/Resume battle
- `ESC` - Exit

The rendering system uses an event-driven architecture that subscribes to battle events and creates corresponding visual effects. All rendering components are modular and can be customized or extended.

### Running Tests

```bash
# Run all tests
python3 -m unittest discover tests -v

# Run specific test suites
python3 -m unittest tests.test_battle -v
python3 -m unittest tests.test_status_effect -v
python3 -m unittest tests.test_creature -v
```

## Rendering & Visualization ✓
Real-time Pygame-based visualization system featuring:
- 2D spatial arena with grid and resource locations
- Creature rendering with HP/hunger bars and strain-based colors
- Interactive UI with population panels and battle feed
- Event-driven animations (damage numbers, effects)
- Pause/resume and input handling
- Battle state visualization and survivor display

See the [Pygame Rendering Demo](#pygame-rendering-demo) below for a live visualization example.

![EvoBattle Rendering Screenshot](https://github.com/user-attachments/assets/e876d6cc-186d-4e7c-bdf3-6d89972b03e8)

## Setup Instructions
1. Clone the repository: `git clone https://github.com/dbmelville2-jpg/evobattle`
2. Navigate into the project directory: `cd evobattle`
3. Install dependencies: `pip install -r requirements.txt`
   - Includes: Flask, Python-dotenv, Pygame