# Combat System Tuning Guide

## Quick Start

The enhanced combat system is highly configurable. This guide helps you tune it for different gameplay styles.

## Common Tuning Scenarios

### Problem: Creatures chase too far

```python
config = CombatConfig(
    max_chase_distance=20.0,  # Reduce from default 30.0
    target_retention_distance=12.0  # Reduce from default 15.0
)
```

### Problem: Too much target switching

```python
config = CombatConfig(
    min_target_switch_time=3.0,  # Increase from default 2.0
    retarget_check_interval=1.0   # Increase from default 0.5
)
```

### Problem: Not enough cooperation

```python
config = CombatConfig(
    gang_up_damage_bonus=0.25,      # Increase from default 0.15
    ally_support_bonus=0.15,        # Increase from default 0.1
    gang_up_threshold=1,            # Reduce from default 2
    same_strain_avoid_combat=True  # Enable strain cooperation
)
```

### Problem: Creatures flee too early

```python
config = CombatConfig(
    flee_hp_threshold=0.1,          # Reduce from default 0.15
    flee_outnumber_threshold=4,     # Increase from default 3
)
```

### Problem: Creatures never flee

```python
config = CombatConfig(
    flee_hp_threshold=0.25,         # Increase from default 0.15
    flee_outnumber_threshold=2,     # Reduce from default 3
)
```

### Problem: Revenge not impactful enough

```python
config = CombatConfig(
    revenge_damage_bonus=0.5,       # Increase from default 0.3
    weight_relationship=0.35,       # Increase from default 0.25
)
```

### Problem: Family protection too weak

```python
config = CombatConfig(
    family_protection_bonus=0.3,    # Increase from default 0.2
    protect_ally_hp_threshold=0.4,  # Increase from default 0.3
)
```

## Preset Configurations

### Aggressive Fast-Paced Combat
```python
config = CombatConfig.create_aggressive_config()
# Features:
# - Longer chase distances (40.0)
# - Faster retargeting (1.0s)
# - Faster attacks (0.8s cooldown)
# - Higher revenge bonus (0.5)
```

### Tactical Positioning Combat
```python
config = CombatConfig.create_tactical_config()
# Features:
# - Shorter chase distances (20.0)
# - Longer target commitment (3.0s)
# - Distance matters more (0.5 weight)
# - Better gang-up rewards (0.25)
```

### Family-Focused Cooperation
```python
config = CombatConfig.create_family_focused_config()
# Features:
# - Strain cooperation enabled
# - High family protection (0.4)
# - Relationships matter more (0.4 weight)
# - Better ally support (0.2)
```

## Parameter Reference

### Targeting Parameters

| Parameter | Default | Description | Impact |
|-----------|---------|-------------|--------|
| `max_chase_distance` | 30.0 | Max distance to pursue targets | Lower = less chasing |
| `close_combat_range` | 10.0 | Distance considered "close" | Affects threat assessment |
| `support_range` | 20.0 | Range for ally detection | Larger = more cooperation |
| `min_target_switch_time` | 2.0 | Min seconds before retargeting | Higher = less switching |
| `target_retention_distance` | 15.0 | Keep target if within range | Hysteresis for targeting |
| `retarget_check_interval` | 0.5 | How often to check retarget | Lower = more responsive |

### Damage Modifiers

| Parameter | Default | Description | Impact |
|-----------|---------|-------------|--------|
| `revenge_damage_bonus` | 0.3 | Bonus vs revenge targets | +30% damage |
| `rival_damage_bonus` | 0.15 | Bonus vs rivals | +15% damage |
| `gang_up_damage_bonus` | 0.15 | Bonus per ally in gang-up | +15% per ally |
| `ally_support_bonus` | 0.1 | Bonus when near allies | +10% damage |
| `family_protection_bonus` | 0.2 | Bonus protecting family | +20% damage |

### Targeting Weights

| Parameter | Default | Description | Range |
|-----------|---------|-------------|-------|
| `weight_distance` | 0.3 | Importance of proximity | 0-1 |
| `weight_threat` | 0.25 | Importance of threat level | 0-1 |
| `weight_relationship` | 0.25 | Importance of relationships | 0-1 |
| `weight_opportunity` | 0.2 | Importance of opportunity | 0-1 |

**Note:** Weights don't need to sum to 1.0. Higher relative weight = more important.

### Flee Behavior

| Parameter | Default | Description | Impact |
|-----------|---------|-------------|--------|
| `flee_hp_threshold` | 0.15 | HP % to trigger flee | Lower = fight longer |
| `flee_outnumber_threshold` | 3 | Enemies to trigger flee | Lower = flee easier |
| `flee_speed_multiplier` | 1.3 | Speed boost when fleeing | Higher = faster escapes |

### Cooperation Settings

| Parameter | Default | Description | Impact |
|-----------|---------|-------------|--------|
| `same_strain_avoid_combat` | False | Same strain = allies | Enable for strain battles |
| `gang_up_threshold` | 2 | Min allies for gang-up | Lower = easier gang-ups |
| `protect_ally_hp_threshold` | 0.3 | HP to trigger protection | Higher = more protective |

## Tuning Workflow

### 1. Identify the Problem
- Watch a battle and note specific issues
- Too much chasing? Target switching? No cooperation?

### 2. Adjust Related Parameters
- Start with one parameter
- Make small changes (10-20% adjustments)
- Test and observe

### 3. Iterate
- Combine multiple parameter changes
- Test edge cases (outnumbered, low HP, etc.)
- Document what works

### 4. Create Custom Preset
```python
def create_my_config():
    config = CombatConfig()
    config.max_chase_distance = 25.0
    config.revenge_damage_bonus = 0.4
    config.gang_up_damage_bonus = 0.2
    return config
```

## Balancing Guidelines

### For Faster Combat
- Reduce `attack_cooldown`
- Increase `max_chase_distance`
- Reduce `min_target_switch_time`

### For More Strategic Combat
- Increase targeting weights (especially `weight_distance`)
- Increase `min_target_switch_time`
- Increase gang-up and cooperation bonuses

### For Story-Driven Combat
- Increase `weight_relationship`
- Increase revenge and family bonuses
- Enable `same_strain_avoid_combat`

### For Chaotic Battles
- Reduce `min_target_switch_time`
- Reduce targeting weights
- Reduce cooperation bonuses

## Testing Your Configuration

```python
# Test with logging
battle = SpatialBattle(creatures, combat_config=config)
battle.simulate(duration=30.0)

# Check logs for behavior
for log in battle.battle_log:
    print(log)

# Check combat memory
for creature in battle.creatures:
    if creature.is_alive():
        print(f"{creature.creature.name}:")
        print(f"  Encounters: {len(creature.creature.combat_memory.encounters)}")
        print(f"  Recent attackers: {creature.creature.combat_memory.recent_attackers}")
```

## Common Mistakes

❌ **Setting all weights to 1.0**: Doesn't add variety
✅ **Vary weights**: Make some factors more important

❌ **Extreme values**: Setting chase distance to 5.0 or 500.0
✅ **Reasonable ranges**: 15.0-50.0 for most arenas

❌ **Ignoring personality**: Parameters override personality
✅ **Work with personality**: Let personality influence, tune parameters for balance

❌ **Too many gang-up bonuses**: Makes fights one-sided
✅ **Moderate bonuses**: 15-25% keeps it balanced

## Monitoring Combat Quality

Good combat should have:
- ✅ Creatures engage enemies within reasonable distance
- ✅ Target switching occurs but not constantly
- ✅ Cooperation visible (gang-ups, protection)
- ✅ Personalities affect behavior (cautious flee, aggressive attack)
- ✅ Revenge arcs create narrative tension
- ✅ Fleeing occurs when appropriate

Bad combat indicators:
- ❌ Creatures chasing across entire arena
- ❌ Target switching every frame
- ❌ No visible cooperation
- ❌ All creatures behave identically
- ❌ No one ever flees or everyone flees
- ❌ Revenge never triggers

## Advanced Tuning

### Situational Configs
Create different configs for different scenarios:

```python
# Small arena - tighter engagement
small_arena_config = CombatConfig(max_chase_distance=15.0)

# Large arena - allow more pursuit
large_arena_config = CombatConfig(max_chase_distance=40.0)

# Family battle - high cooperation
family_config = CombatConfig.create_family_focused_config()

# Free-for-all - individualistic
ffa_config = CombatConfig(
    same_strain_avoid_combat=False,
    gang_up_damage_bonus=0.1,
    weight_relationship=0.1
)
```

### Dynamic Tuning
Adjust config during battle:

```python
# Start aggressive
battle.combat_config.max_chase_distance = 40.0

# Later, make it more tactical
if battle.current_time > 20.0:
    battle.combat_config.max_chase_distance = 25.0
    battle.combat_config.gang_up_damage_bonus = 0.25
```

## Performance Considerations

Most parameters don't affect performance, but:

- `max_chase_distance`: Affects query radius (lower = faster)
- `support_range`: Affects ally/enemy queries (lower = faster)
- `retarget_check_interval`: Higher = fewer checks = faster

For 100+ creatures:
```python
config = CombatConfig(
    max_chase_distance=25.0,  # Smaller queries
    support_range=15.0,       # Smaller queries  
    retarget_check_interval=1.0  # Less frequent checks
)
```

## Getting Help

If combat doesn't feel right:

1. Enable battle logging and review decisions
2. Check combat memory to see what creatures remember
3. Try a preset config first (aggressive/tactical/family)
4. Adjust one parameter at a time
5. Document what changes helped

The system is designed to be flexible - experiment and find what works for your game!
