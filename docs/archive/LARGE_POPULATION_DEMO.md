# Large Population Ecosystem Demo

## Overview

The ecosystem pygame demo now supports large founder populations (20-30 creatures) with immediate breeding capability, enabling realistic population dynamics and evolution simulation.

## Key Features

### 1. Large Founder Population
- **Default: 20 creatures** (configurable up to 30+)
- Each founder has:
  - 2 random traits from the trait pool
  - Random level between 3-6
  - Unique color (hue) for family identification
  - Full hunger and HP at start
  - **Mature status** - ready to breed immediately

### 2. Active Breeding System
- Creatures within **10 units** of each other can breed
- Both parents must be mature and healthy
- Breeding checks occur every **5 seconds**
- Offspring characteristics:
  - Inherit traits from both parents (with mutations)
  - Spawn near parents (averaged position)
  - Start as immature (need to grow up)
  - Blend of parent hues with variation

### 3. Population Dynamics
- **Births tracked** - displayed in green in top-right corner
- **Deaths tracked** - displayed in red in top-right corner
- Real-time population count shows total and alive
- Event log shows birth and death announcements
- Natural population fluctuations based on:
  - Food availability
  - Combat
  - Starvation
  - Breeding success

### 4. Family Lineages
- Each creature has a `strain_id` (genetic lineage identifier)
- Offspring inherit strain from parents (or create new strain on mutation)
- Left panel shows strain distribution with:
  - Strain colors (averaged hue)
  - Population counts per strain
  - Alive vs. dead members

## Usage

### Running the Demo

```bash
python -m examples.ecosystem_pygame_demo
```

### Customizing Population

Edit `examples/ecosystem_pygame_demo.py` and modify the `create_ecosystem_battle()` call:

```python
# Create with 30 founders in a larger arena
battle = create_ecosystem_battle(
    num_founders=30,           # Number of starting creatures
    arena_width=120.0,         # Arena width
    arena_height=120.0,        # Arena height
    resource_spawn_rate=0.2,   # Food items per second
    initial_resources=30       # Starting food
)
```

### Controls

- **SPACE** - Pause/Resume simulation
- **ESC** - Exit
- **R** - Restart with new population

## What to Watch For

1. **Early Breeding Phase** (0-10s)
   - Creatures meet and breed
   - First offspring appear near parents
   - Population grows

2. **Resource Competition** (10-30s)
   - Food becomes scarce
   - Combat increases
   - Some creatures starve
   - Population may decline

3. **Stabilization** (30s+)
   - Surviving strains dominate
   - Population reaches equilibrium
   - Successful traits become more common

## Statistics Displayed

- **Top Center**: Battle timer
- **Top Left**: Population count (alive/total)
- **Top Right**: 
  - Food count
  - Births (green)
  - Deaths (red)
- **Left Panel**: Strain distribution
- **Right Panel**: Individual creature stats
- **Bottom**: Event log with recent births/deaths

## Example Session

```
Initial: 20 founders (all mature)
  └─> 10s: 25 creatures (5 births, 0 deaths)
  └─> 20s: 28 creatures (8 births, 5 deaths)
  └─> 30s: 23 creatures (8 births, 13 deaths)
  └─> 60s: 18 creatures (8 births, 18 deaths) - stabilized
```

## Technical Details

### Breeding Conditions
- Both parents must be alive and `can_breed()` returns True
- Parents must be within 10 units distance
- Breeding cooldown: 5 seconds between checks
- Mutation rate: 10% chance per trait

### Offspring Properties
```python
offspring = Creature(
    name=f"{parent1.name[:4]}{parent2.name[:4]}",  # e.g., "FounFoun"
    level=1,                      # Start at level 1
    traits=[inherited_traits],    # 70-90% chance per parent trait
    hue=(parent1.hue + parent2.hue) / 2 + mutation,
    strain_id=inherited_or_new,
    mature=False,                 # Not mature yet
    parent_ids=[parent1.id, parent2.id]
)
```

### Population End Conditions
- Battle ends when population drops to 1 or 0
- Can be prevented by maintaining sufficient resources
- Larger arenas reduce combat, increase survival

## Tips for Best Results

1. **For Maximum Breeding**: Use 25-30 founders in 100x100 arena
2. **For Long Simulations**: Increase resource spawn rate to 0.2+
3. **For Evolution**: Run 100+ seconds to see trait selection
4. **For Combat Focus**: Reduce resources to 0.1 spawn rate

## Related Files

- `examples/ecosystem_pygame_demo.py` - Main demo file
- `src/systems/battle_spatial.py` - Battle and breeding logic
- `src/systems/breeding.py` - Breeding system implementation
- `src/rendering/ui_components.py` - UI display components
