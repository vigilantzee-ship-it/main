# Enhanced Combat System Documentation

## Overview

The enhanced combat system introduces sophisticated, relationship-aware targeting and combat behaviors that create dynamic, realistic battles. Creatures now make intelligent decisions based on:

- **Spatial Context**: Distance, proximity to allies/enemies
- **Relationships**: Family bonds, alliances, rivalries, revenge
- **Combat Memory**: Past encounters, recent attackers, threat assessment
- **Personality**: Aggression, caution, loyalty, pride
- **Tactical Awareness**: Outnumbered situations, injured allies, gang-up opportunities

## Key Features

### 1. Intelligent Targeting System

Creatures no longer blindly chase targets across the map. Target selection uses a comprehensive scoring system:

```python
Target Score = 
    Distance Score × 0.3 +
    Threat Score × 0.25 +
    Relationship Score × 0.25 +
    Opportunity Score × 0.2 +
    Personality Score × 0.1
```

**Distance Score:**
- Prevents long-distance chasing (default max: 30 units)
- Closer targets score higher
- Targets beyond max distance are excluded

**Threat Score:**
- Based on combat memory (damage received, recent attacks)
- Revenge targets get significant boost
- Creatures who killed you get maximum threat

**Relationship Score:**
- Revenge targets: +1.0
- Rivals: +0.7
- Feared enemies: -0.5
- Allies/Family: -2.0 (avoid friendly fire)

**Opportunity Score:**
- Injured targets: Higher score
- Weaker targets: Bonus points
- Carnivore vs Herbivore: +0.4 bonus

**Personality Score:**
- Aggressive: Prefer strong enemies
- Cautious: Prefer weak enemies
- Loyal: Protect injured allies
- Proud: Accept challenges from stronger enemies

### 2. Ally & Enemy Recognition

Creatures identify allies through multiple systems:

**Family Bonds:**
- Parent/Child relationships
- Sibling relationships
- Never attack family members

**Explicit Alliances:**
- Ally relationships
- Fought together bonds

**Strain Cooperation** (configurable):
- Same strain_id creatures can be allies
- Enables strain vs strain battles

### 3. Combat Memory System

Each creature remembers:

**Recent Attackers:**
- Who attacked in last 10 seconds
- Total damage received from each
- Threat level assessment

**Combat Encounters:**
- Full history of fights
- Damage dealt/received
- Times fought
- Whether they killed you

**Target Stickiness:**
- Minimum time on target (2 seconds default)
- Prevents rapid target switching
- Maintains combat focus

### 4. Relationship-Aware Combat

**Revenge Mechanics:**
- When family member is killed, create REVENGE_TARGET relationship
- Revenge targets prioritized in targeting
- +30% damage bonus against revenge targets
- Creatures seek out their family's killers

**Rivalry:**
- Develops through repeated combat
- +15% damage bonus against rivals
- Moderate targeting priority

**Protective Behavior:**
- Defend injured family members
- +20% damage when protecting injured family
- Prioritize enemies attacking allies

**Gang-Up Tactics:**
- Multiple allies near target
- +15% damage per nearby ally (configurable)
- Rewards cooperative positioning

### 5. Flee Behavior

Creatures intelligently flee based on:

**HP Threshold:**
- Default: 15% HP triggers flee consideration
- Modified by personality (cautious flee earlier)

**Outnumbered:**
- 3+ enemies nearby triggers flee
- Even at higher HP if badly outnumbered

**Personality:**
- Caution trait lowers flee threshold
- Pride trait raises flee threshold
- Reckless creatures never flee

**Flee Direction:**
- Away from center of enemy positions
- Maintains safe distance
- Re-engages when healed/enemies reduce

## Configuration

All combat parameters are tunable via `CombatConfig`:

```python
from src.models.combat_config import CombatConfig

# Default balanced configuration
config = CombatConfig()

# Aggressive fast-paced combat
config = CombatConfig.create_aggressive_config()

# Tactical positioning-focused
config = CombatConfig.create_tactical_config()

# Family-focused cooperation
config = CombatConfig.create_family_focused_config()

# Custom configuration
config = CombatConfig(
    max_chase_distance=40.0,        # Chase further
    revenge_damage_bonus=0.5,       # Higher revenge bonus
    gang_up_damage_bonus=0.25,      # Better gang-up rewards
    same_strain_avoid_combat=True   # Strain cooperation
)

# Use in battle
battle = SpatialBattle(
    creatures,
    combat_config=config
)
```

### Key Parameters

**Targeting:**
- `max_chase_distance`: Max distance to pursue (default: 30.0)
- `min_target_switch_time`: Min seconds before retargeting (default: 2.0)
- `target_retention_distance`: Keep target if within this distance (default: 15.0)

**Damage Modifiers:**
- `revenge_damage_bonus`: Bonus vs revenge targets (default: 0.3 = +30%)
- `rival_damage_bonus`: Bonus vs rivals (default: 0.15 = +15%)
- `gang_up_damage_bonus`: Bonus per ally (default: 0.15 = +15%)
- `ally_support_bonus`: Bonus when near allies (default: 0.1 = +10%)
- `family_protection_bonus`: Bonus protecting injured family (default: 0.2 = +20%)

**Flee Behavior:**
- `flee_hp_threshold`: HP % to trigger flee (default: 0.15 = 15%)
- `flee_outnumber_threshold`: Enemies to trigger flee (default: 3)
- `flee_speed_multiplier`: Speed boost when fleeing (default: 1.3 = +30%)

**Cooperation:**
- `same_strain_avoid_combat`: Whether same strain = allies (default: False)
- `gang_up_threshold`: Min allies for gang-up bonus (default: 2)
- `protect_ally_hp_threshold`: HP to trigger protection (default: 0.3 = 30%)

## Usage Examples

### Basic Enhanced Combat

```python
from src.systems.battle_spatial import SpatialBattle
from src.models.creature import Creature, CreatureType
from src.models.combat_config import CombatConfig

# Create creatures with relationships
dragon = Creature(name="Blaze", ...)
serpent = Creature(name="Aqua", ...)

# Add family relationship
dragon.relationships.add_relationship(
    serpent.creature_id,
    RelationshipType.SIBLING,
    strength=0.9
)

# Create battle with default config
battle = SpatialBattle([dragon, serpent, ...])

# Or with custom config
config = CombatConfig(max_chase_distance=40.0)
battle = SpatialBattle([dragon, serpent, ...], combat_config=config)
```

### Strain vs Strain Combat

```python
# Enable strain cooperation
config = CombatConfig(same_strain_avoid_combat=True)

# Create two strains
strain_a = [create_creature(strain_id="alpha") for _ in range(5)]
strain_b = [create_creature(strain_id="beta") for _ in range(5)]

# They'll cooperate within strain, fight between strains
battle = SpatialBattle(
    strain_a + strain_b,
    combat_config=config
)
```

### Revenge-Focused Combat

```python
# High revenge bonuses
config = CombatConfig(
    revenge_damage_bonus=0.5,      # +50% vs revenge targets
    weight_relationship=0.4,        # Relationships matter more
    family_protection_bonus=0.3     # +30% protecting family
)

battle = SpatialBattle(creatures, combat_config=config)
```

### Tactical Positioning Combat

```python
# Reward positioning and cooperation
config = CombatConfig(
    max_chase_distance=20.0,        # Don't chase far
    gang_up_damage_bonus=0.25,      # Better gang-up
    weight_distance=0.5,            # Distance matters more
    ally_support_bonus=0.15         # Better ally support
)

battle = SpatialBattle(creatures, combat_config=config)
```

## Combat Memory API

Creatures automatically track combat encounters:

```python
# Access combat memory
memory = creature.combat_memory

# Recent attackers (last 10 seconds)
recent = memory.get_recent_attackers(max_age=10.0)

# Threat assessment
threat = memory.get_threat_level(enemy_id)  # 0-1

# Most threatening enemy
most_dangerous = memory.get_most_threatening(enemy_ids)

# Should prioritize revenge?
should_revenge = memory.should_prioritize_revenge(target_id)

# Manually record events
memory.record_attacked_by(attacker_id, damage=50)
memory.record_attacked(target_id, damage=30, killed=True)
memory.record_killed_by(killer_id)
```

## Personality Integration

The system automatically integrates personality traits:

**Aggression:**
- High aggression → target stronger enemies
- Low aggression → defensive positioning

**Caution:**
- High caution → target weak enemies, flee earlier
- Low caution → reckless, fight to death

**Loyalty:**
- High loyalty → protect allies, fight better with team
- Low loyalty → self-preservation

**Pride:**
- High pride → accept challenges, never flee
- Low pride → pragmatic retreats

**Compassion:**
- High compassion → protect wounded allies
- Low compassion → ruthless opportunism

## Targeting Strategy Breakdown

The system uses these strategies automatically:

1. **REVENGE**: Prioritize revenge targets (family killers)
2. **PROTECT_ALLIES**: Target enemies attacking allies
3. **OPPORTUNISTIC**: Target injured + close enemies
4. **FAMILY_DEFENDER**: Defend injured family members
5. **NEAREST**: Fall back to closest enemy
6. **WEAKEST**: Cautious creatures prefer weak targets
7. **STRONGEST**: Aggressive creatures prefer strong targets

## Performance Considerations

The enhanced system uses spatial hashing for efficiency:

- O(1) ally/enemy lookups within range
- Efficient nearest-neighbor queries
- Minimal overhead for targeting decisions
- Scales well to 100+ creatures

## Migration from Old System

The new system is backward compatible:

```python
# Old API still works
battle = SpatialBattle(team1, team2)

# New API recommended
battle = SpatialBattle(all_creatures)

# With configuration
battle = SpatialBattle(all_creatures, combat_config=config)
```

Existing code will use default configuration with enhanced behaviors automatically.

## Debugging & Tuning

Enable combat logging to see decisions:

```python
# Battle logs show targeting decisions
for log_entry in battle.battle_log:
    print(log_entry)

# Combat memory debugging
print(f"Recent attackers: {creature.combat_memory.recent_attackers}")
print(f"Threat levels: {creature.combat_memory.threat_level}")
print(f"Encounters: {len(creature.combat_memory.encounters)}")
```

Tune parameters based on desired gameplay:

- **Too much chasing?** Reduce `max_chase_distance`
- **Too defensive?** Reduce `flee_hp_threshold`
- **Not enough cooperation?** Increase gang-up and ally bonuses
- **Too many target switches?** Increase `min_target_switch_time`

## Future Extensions

The system is designed for easy extension:

- **Team Formations**: Leader/follower behaviors
- **Tactical Retreats**: Retreat to specific positions
- **Coordinated Attacks**: Synchronized multi-creature attacks
- **Advanced Memory**: Long-term grudges, alliances
- **Skill-Based Targeting**: Target based on enemy abilities
- **Environmental Tactics**: Use terrain for advantage

## Summary

The enhanced combat system transforms simple proximity-based fighting into sophisticated, emergent tactical battles. Creatures now:

- ✅ Don't chase targets across the entire arena
- ✅ Remember who attacked them and seek revenge
- ✅ Protect family members and allies
- ✅ Gang up on isolated enemies
- ✅ Flee when outnumbered or critically injured
- ✅ Make personality-driven targeting decisions
- ✅ Benefit from cooperative positioning
- ✅ Create dynamic rivalries and revenge arcs

This creates engaging, varied combat with emergent narratives driven by relationships, memory, and personality.
