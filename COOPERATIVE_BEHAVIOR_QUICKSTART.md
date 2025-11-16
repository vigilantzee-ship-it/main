# Cooperative Behavior System - Quick Start Guide

## What Is This?

The Cooperative Behavior System adds social personality traits and emergent cooperative behaviors to EvoBattle creatures. Creatures can now:

- 🤝 Share food with family and allies
- ⚔️ Join allies' fights based on loyalty
- 👥 Gain combat bonuses when fighting in groups
- 👑 Follow dominant leaders
- 💚 Provide parental care to offspring

## Quick Examples

### Food Sharing
```python
from src.systems.living_world import LivingWorldBattleEnhancer

enhancer = LivingWorldBattleEnhancer(battle_system)

# Evaluate if creature should share food
should_share, amount = enhancer.evaluate_food_sharing(
    giver=parent_creature,
    receiver=child_creature,
    food_amount=100.0
)

if should_share:
    child_creature.eat(amount)
    parent_creature.hunger -= amount
```

### Group Combat Bonuses
```python
# Get all allies in battle
allies = [c for c in all_creatures if c.strain_id == attacker.strain_id]

# Calculate damage with group bonuses
damage = enhancer.calculate_damage_modifier(
    attacker=creature,
    defender=enemy,
    base_damage=50.0,
    allies_present=allies  # NEW parameter
)
# Cooperative creatures get up to +44% bonus!
```

### Check Social Traits
```python
# Every creature now has social traits
creature = Creature(name="Fighter")

print(creature.social_traits.get_description())
# Output: "altruistic, cooperative, protective"

# Individual traits (all 0-1)
creature.social_traits.altruism       # Willingness to help/share
creature.social_traits.dominance      # Leadership tendencies
creature.social_traits.cooperation    # Team fighting
creature.social_traits.protectiveness # Defend family
creature.social_traits.independence   # Solo preference
```

### Check Relationship Metrics
```python
rel = creature.relationships.get_relationship(ally_id)

# New metrics on every relationship
cooperation = rel.metrics.get_cooperation_score()  # 0-1
affinity = rel.metrics.affinity     # Emotional bond (0-1)
trust = rel.metrics.trust           # Reliability (0-1)
kinship = rel.metrics.kinship       # Genetic (0-1, 1.0 for family)
rank = rel.metrics.rank             # Dominance (-1 to 1)
```

## How Social Traits Work

### Trait Combinations Create Personalities

**Protective Family Fighter:**
```python
creature.social_traits.altruism = 0.9
creature.social_traits.protectiveness = 0.9
creature.social_traits.cooperation = 0.8
# → Shares food, defends family, strong in groups
```

**Selfish Loner:**
```python
creature.social_traits.altruism = 0.2
creature.social_traits.independence = 0.9
creature.social_traits.cooperation = 0.2
# → Hoards resources, fights alone, weak bonuses
```

**Pack Leader:**
```python
creature.social_traits.dominance = 0.9
creature.social_traits.cooperation = 0.8
creature.social_traits.protectiveness = 0.7
# → Leads groups, coordinates well, defends pack
```

### Traits Are Inherited

Social traits are automatically inherited from parents:

```python
from src.models.relationship_metrics import AgentTraits

# During breeding (this is automatic in the system)
child_traits = AgentTraits.inherit(
    parent1.social_traits,
    parent2.social_traits,
    mutation_rate=0.1
)
```

## Integration Points

### In Battle System
```python
# At battle start
enhancer.update_social_states(all_creatures)

# During creature AI decisions
target = enhancer.enhance_target_selection(attacker, targets)
should_flee = enhancer.should_retreat(creature, enemy_count)

# When calculating damage
damage = enhancer.calculate_damage_modifier(
    attacker, defender, base_damage,
    allies_present=nearby_allies
)

# When creature takes food
should_share, amount = enhancer.evaluate_food_sharing(
    creature, nearby_hungry_ally, food_amount
)
```

### In UI
```python
# Creature inspector automatically shows:
# - Social trait description
# - Cooperation scores for relationships
# - Relationship metrics (affinity, trust)

# Access for custom UI:
traits_desc = creature.social_traits.get_description()
coop_score = relationship.metrics.get_cooperation_score()
```

### In Breeding System
```python
# Social traits are automatically inherited
# No additional code needed - happens in Creature.from_dict()

# But you can manually set if needed:
child.social_traits = AgentTraits.inherit(
    parent1.social_traits,
    parent2.social_traits,
    mutation_rate=0.1
)
```

## Demo Application

Run the interactive demo to see all features:

```bash
python -m examples.cooperative_behavior_demo
```

This demonstrates:
- Food sharing (family vs strangers)
- Fight joining (protective vs independent)
- Group combat bonuses (cooperative vs solo)

## Common Patterns

### Create Altruistic Healer
```python
healer = Creature(name="Healer")
healer.social_traits.altruism = 0.95
healer.social_traits.protectiveness = 0.9
healer.social_traits.cooperation = 0.8
```

### Create Aggressive Loner
```python
loner = Creature(name="Lone Wolf")
loner.social_traits.independence = 0.95
loner.social_traits.altruism = 0.2
loner.social_traits.dominance = 0.8
```

### Create Team Fighter
```python
team_fighter = Creature(name="Team Player")
team_fighter.social_traits.cooperation = 0.95
team_fighter.social_traits.altruism = 0.7
team_fighter.social_traits.dominance = 0.4  # Follows leaders
```

## Performance Notes

- Social trait checks are O(1)
- Behavior evaluations are <0.5ms
- Group bonus calculation is O(n) where n = allies (typically <10)
- No FPS impact in normal gameplay

## Testing

All cooperative behaviors have comprehensive tests:

```bash
python -m unittest tests.test_cooperative_behavior -v
```

22 tests covering:
- Trait mechanics
- Relationship metrics
- All 5 cooperative behaviors
- Creature integration
- Serialization

## Documentation

Full documentation available in:
- `LIVING_WORLD_DOCUMENTATION.md` - API reference and usage
- `COOPERATIVE_BEHAVIOR_IMPLEMENTATION.md` - Implementation details
- Code docstrings in `src/models/relationship_metrics.py`

## Troubleshooting

**Q: Creatures not sharing food?**
A: Check altruism trait and relationship metrics. Low altruism (<0.4) or weak relationships won't share.

**Q: No group bonus?**
A: Check cooperation trait. Independent creatures (independence >0.7) get reduced bonuses.

**Q: How do I make creatures cooperate more?**
A: Increase altruism, cooperation, and protectiveness traits. Decrease independence.

**Q: Can I disable cooperative behaviors?**
A: Yes, just don't call the evaluate_* methods. The system is opt-in.

## Future Enhancements

The system is ready for these features (implementation needed):
- Pack movement following alpha
- Food sharing in ecosystem pellet system
- Spawning allies to join fights
- Parental teaching of skills
- Cooperative hunting strategies

## Support

For questions or issues:
1. Check `LIVING_WORLD_DOCUMENTATION.md` for API details
2. Run `examples/cooperative_behavior_demo.py` to see it in action
3. Review tests in `tests/test_cooperative_behavior.py`
4. Check inline docstrings in `src/models/relationship_metrics.py`

---

**Made with ❤️ for creating emergent social dynamics in EvoBattle!**
