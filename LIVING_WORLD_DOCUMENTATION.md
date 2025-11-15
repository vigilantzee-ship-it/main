# Living World System Documentation

## Overview

The Living World System transforms EvoBattle from a simple battle simulator into a rich, emergent narrative experience where every creature has a unique story. This system tracks individual histories, develops skills through experience, creates personalities that affect behavior, and forms relationships that drive emergent gameplay.

## Core Components

### 1. History System (`src/models/history.py`)

Tracks every significant event in a creature's lifetime, creating a rich narrative history.

#### CreatureHistory

Comprehensive tracking of:
- **Lifecycle**: Birth time, death time, cause of death
- **Battle Statistics**: Battles fought/won, damage dealt/received, kills, deaths
- **Survival**: Food consumed, starvation events, near-death experiences
- **Social**: Offspring count, breeding attempts
- **Events**: Timeline of all significant moments
- **Achievements**: Special accomplishments
- **Titles**: Earned honorifics

#### Event Types

```python
EventType.BIRTH              # Creature born
EventType.DEATH              # Creature died
EventType.BATTLE_START       # Entered combat
EventType.BATTLE_WIN         # Won battle
EventType.ATTACK             # Made an attack
EventType.CRITICAL_HIT       # Landed critical hit
EventType.KILL               # Killed an opponent
EventType.REVENGE_KILL       # Avenged family member
EventType.OFFSPRING_BORN     # Had offspring
EventType.FIRST_KILL         # First kill achievement
EventType.LEGENDARY_MOMENT   # Exceptional achievement
```

#### Usage Example

```python
from src.models.history import CreatureHistory

# Create history
history = CreatureHistory(creature.creature_id, creature.name)

# Record events
history.record_battle_start(enemy_ids)
history.record_attack(target_id, damage=50.0, was_critical=True)
history.record_kill(victim_id, "Enemy", power_differential=2.0)

# Query history
win_rate = history.get_win_rate()
recent = history.get_recent_events(10)
legendary = history.legendary_moments
```

### 2. Skill System (`src/models/skills.py`)

Skills develop through use, creating unique combat styles and emergent specialization.

#### Skill Types

**Combat Skills:**
- `MELEE_ATTACK` - Close-range attack proficiency
- `RANGED_ATTACK` - Long-range attack accuracy
- `CRITICAL_STRIKE` - Chance to land devastating hits
- `DODGE` - Ability to evade attacks
- `BLOCK` - Reduce incoming damage

**Survival Skills:**
- `FORAGING` - Efficiency at finding food
- `METABOLISM` - Food energy efficiency
- `STAMINA` - Sustained activity endurance

**Social Skills:**
- `LEADERSHIP` - Inspire and coordinate allies
- `TEAMWORK` - Fight effectively with allies
- `INTIMIDATION` - Frighten and demoralize enemies

#### Proficiency Levels

- **Novice** (0-19): Just learning
- **Competent** (20-39): Basic proficiency
- **Expert** (40-59): Advanced skill
- **Master** (60-79): Expert mastery
- **Legendary** (80-100): Unmatched excellence

#### Usage Example

```python
from src.models.skills import SkillManager, SkillType

# Use skills
manager = SkillManager()
modifier = manager.use_skill(SkillType.MELEE_ATTACK, difficulty=1.5, success=True)

# Query skills
top_skills = manager.get_highest_skills(3)
for skill_type, level in top_skills:
    skill = manager.get_skill(skill_type)
    print(f"{skill.config.name}: Level {level} ({skill.get_proficiency().value})")
```

### 3. Personality System (`src/models/personality.py`)

Seven core personality traits drive unique behaviors and decision-making.

#### Personality Traits

- **Aggression** (0-1): Passive to very aggressive
  - High: Attacks more, targets strong enemies
  - Low: Defensive, strategic approach
  
- **Caution** (0-1): Reckless to very cautious
  - High: Retreats early, plays safe
  - Low: Fights to the death, takes risks
  
- **Loyalty** (0-1): Selfish to very loyal
  - High: Protects allies, fights for family
  - Low: Self-preservation focus
  
- **Ambition** (0-1): Passive to very ambitious
  - High: Seeks challenges, gains more XP
  - Low: Avoids risk
  
- **Curiosity** (0-1): Routine to very curious
  - High: Explores more, tries new tactics
  - Low: Sticks to patterns
  
- **Pride** (0-1): Humble to very proud
  - High: Refuses to retreat, seeks glory
  - Low: Pragmatic survival
  
- **Compassion** (0-1): Ruthless to very compassionate
  - High: Helps wounded allies
  - Low: Fights independently

#### Personality Effects

```python
from src.models.personality import PersonalityProfile

# Create personality
personality = PersonalityProfile.random()

# Query behavior
should_retreat = personality.should_retreat(hp_percent=0.3, enemy_count=2)
target_index = personality.get_target_preference(enemies)
team_bonus = personality.get_team_fight_bonus(has_allies=True, has_family=True)
revenge_bonus = personality.get_revenge_bonus(is_revenge=True)

# Inheritance
child = PersonalityProfile.inherit(parent1.personality, parent2.personality)
```

### 4. Relationship System (`src/models/relationships.py`)

Tracks social bonds between creatures, affecting behavior and creating narrative arcs.

#### Relationship Types

- `PARENT` / `CHILD` - Family bonds (never decay)
- `SIBLING` - Brotherhood/sisterhood (never decay)
- `ALLY` - Fought together, mutual support
- `RIVAL` - Repeated confrontations
- `RESPECT` - Admiration for skill
- `FEAR` - Intimidated by opponent
- `REVENGE_TARGET` - Killed family member (seek vengeance)

#### Relationship Effects

**Combat Modifiers:**
- Fighting with allies/family: Up to +20% damage
- Fighting revenge target: Up to +30% damage
- Fighting rival: Up to +15% damage
- Fighting feared opponent: Up to -20% damage

#### Usage Example

```python
from src.models.relationships import RelationshipManager, RelationshipType

# Create relationships
manager = RelationshipManager(creature.creature_id)
manager.add_relationship(ally_id, RelationshipType.ALLY, strength=0.8)

# Record events
manager.record_fought_together(ally_id)
manager.record_family_killed(killer_id, "Parent")

# Query relationships
allies = manager.get_allies()
revenge_targets = manager.get_revenge_targets()
family = manager.get_family()
```

## Battle Integration

The `LivingWorldBattleEnhancer` (`src/systems/living_world.py`) seamlessly integrates all systems into combat.

### Features

1. **Automatic History Tracking**
   - All attacks, kills, deaths logged
   - Battle outcomes recorded
   - Achievements detected

2. **Personality-Driven AI**
   - Target selection based on aggression/caution
   - Retreat decisions based on pride/caution
   - Combat modifiers from personality

3. **Skill-Based Combat**
   - Performance modifiers from skill level
   - Critical hit chance from Critical Strike skill
   - Dodge chance from Dodge skill
   - Experience gained for successful actions

4. **Relationship Modifiers**
   - Revenge bonus against family killers
   - Team bonuses with allies/family
   - Rivalry bonuses
   - Fear penalties

### Usage Example

```python
from src.systems.living_world import LivingWorldBattleEnhancer

# Create enhancer
enhancer = LivingWorldBattleEnhancer(battle_system)

# Start battle
enhancer.on_battle_start(creatures)

# During combat
target = enhancer.enhance_target_selection(attacker, potential_targets)
should_flee = enhancer.should_retreat(creature, enemy_count)
final_damage = enhancer.calculate_damage_modifier(attacker, defender, base_damage)

# After combat
enhancer.on_creature_killed(killer, victim, location)
enhancer.on_battle_end(survivors)
```

## Creature Inspector UI

Interactive Pygame panel for viewing detailed creature information (`src/rendering/creature_inspector.py`).

### Features

- **Stats & Status**: HP, energy, hunger, current state
- **Personality**: Full personality profile and combat style
- **Skills**: Top skills with proficiency levels
- **Battle Record**: Win/loss record, K/D ratio, damage stats
- **Achievements**: Unlocked achievements with rarity
- **Titles**: Earned honorifics
- **Relationships**: Family, allies, rivals, revenge targets
- **Event Timeline**: Recent life events

### Usage Example

```python
from src.rendering.creature_inspector import CreatureInspector

# Create inspector
inspector = CreatureInspector()

# Select creature (e.g., on click)
inspector.select_creature(creature)

# Handle scrolling
inspector.handle_scroll(direction=-1)  # Scroll up

# Render
inspector.render(screen)
```

## Examples

### 1. Text-Based Demo (`examples/living_world_demo.py`)

Simple command-line demo showing:
- Creature creation with personalities
- Battle simulation with history tracking
- Skill progression
- Achievement unlocking
- Relationship formation

Run with:
```bash
python3 -m examples.living_world_demo
```

### 2. Interactive Visual Demo (`examples/interactive_living_world_demo.py`)

Full Pygame demo featuring:
- Real-time battle visualization
- Click creatures to inspect
- Watch skills develop
- See personalities affect behavior
- Track relationships forming

Run with:
```bash
python3 -m examples.interactive_living_world_demo
```

**Controls:**
- **Left Click**: Select creature for inspection
- **SPACE**: Pause/Resume battle
- **I**: Toggle inspector visibility
- **Mouse Wheel**: Scroll inspector
- **ESC**: Exit

## Integration with Existing Systems

### Creature Model Extension

The `Creature` class automatically includes:
```python
creature.history        # CreatureHistory instance
creature.skills         # SkillManager instance
creature.personality    # PersonalityProfile instance
creature.relationships  # RelationshipManager instance
```

### Breeding Integration

Personality inheritance:
```python
offspring.personality = PersonalityProfile.inherit(
    parent1.personality,
    parent2.personality,
    mutation_rate=0.15
)
```

### Serialization Support

All systems support full serialization:
```python
# Save
data = {
    'history': creature.history.to_dict(),
    'skills': creature.skills.to_dict(),
    'personality': creature.personality.to_dict(),
    'relationships': creature.relationships.to_dict()
}

# Load
creature.history = CreatureHistory.from_dict(data['history'])
creature.skills = SkillManager.from_dict(data['skills'])
creature.personality = PersonalityProfile.from_dict(data['personality'])
creature.relationships = RelationshipManager.from_dict(data['relationships'])
```

## Performance Considerations

- **Event Logging**: ~0.1ms per event
- **Skill Calculations**: <0.5ms per skill check
- **History Queries**: <100ms for most queries
- **UI Rendering**: <50ms to populate inspector
- **No Impact**: Battle frame rate maintained at 60 FPS

## Future Enhancements

Potential additions:
- Hall of Fame for legendary creatures
- Persistent database for cross-battle histories
- Family tree visualization
- Achievement notification system
- Injury/scar system
- More sophisticated AI behaviors
- Narrative generation from events

## Testing

Comprehensive test suite in `tests/test_living_world.py`:
- 30+ tests covering all systems
- History tracking validation
- Skill progression verification
- Personality effects testing
- Relationship mechanics testing
- Serialization validation

Run tests:
```bash
python3 -m unittest tests.test_living_world -v
```

## Conclusion

The Living World System creates emergent narratives and memorable moments through:
- ✅ Every creature has a unique story
- ✅ Skills create diverse combat styles
- ✅ Personalities drive interesting behaviors
- ✅ Relationships create dramatic arcs
- ✅ History preserves legacy
- ✅ Achievements celebrate greatness

Players form attachments to individual creatures and remember legendary moments long after battles end. Every life matters, every battle is memorable, and every death is meaningful.
