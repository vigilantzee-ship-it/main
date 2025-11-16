# Genetics, Breeding, and Evolution System Architecture

## Overview

This document clarifies the responsibilities and boundaries between the genetics, breeding, and evolution systems in the Evolution Battle game.

## System Boundaries

### 1. GeneticsEngine (`src/models/genetics.py`)

**Primary Responsibility:** Core genetic inheritance logic with advanced Mendelian genetics

**Features:**
- Dominant/recessive/codominant gene expression
- Trait blending with proper genetic rules
- Stat combination with weighted averaging and genetic variation
- Mutation with provenance tracking
- Multi-generational trait history

**Key Methods:**
- `combine_traits(parent1, parent2, generation)` - Combines traits using Mendelian genetics
- `combine_stats(parent1, parent2)` - Combines stats with weighted averaging and variation
- `_mutate_trait(trait)` - Applies mutations to existing traits
- `_generate_mutation(generation)` - Creates new emergent traits

**Use When:** You need the core genetics logic for trait/stat inheritance

**Used By:** Breeding system

---

### 2. PelletGenetics (`src/models/genetics.py`)

**Primary Responsibility:** Genetics for pellet (food) reproduction

**Features:**
- Asexual reproduction (single parent cloning with mutations)
- Sexual reproduction (two parent trait blending)
- Pellet-specific trait inheritance (nutrition, growth rate, toxicity, etc.)
- Higher mutation rates than creatures

**Key Methods:**
- `combine_pellet_traits(parent1, parent2)` - Combines pellet traits
- `_asexual_inheritance(parent)` - Handles cloning
- `_sexual_inheritance(parent1, parent2)` - Handles sexual reproduction

**Use When:** Pellets reproduce (not creatures)

**Used By:** Pellet.reproduce() method

---

### 3. Breeding System (`src/systems/breeding.py`)

**Primary Responsibility:** High-level breeding orchestration and creature lifecycle

**Features:**
- Breeding eligibility checks (maturity, health, hunger)
- Integration with lineage tracking (parent IDs, generations)
- Hue/color inheritance
- Strain ID management
- Birth time and age tracking

**Key Methods:**
- `breed(parent1, parent2, birth_time)` - Main breeding method
- Legacy wrapper methods (deprecated, delegate to GeneticsEngine):
  - `calculate_inherited_traits()` 
  - `_inherit_stats()`
  - `apply_mutation()`
  - `generate_new_trait()`

**Use When:** You need to breed creatures in the game (high-level API)

**Used By:** SpatialBattle and other game systems

**Note:** This is the primary API for breeding in the game. It wraps GeneticsEngine for convenience.

---

### 4. EvolutionSystem (`src/models/evolution.py`)

**Primary Responsibility:** Creature type transformation (evolving to new forms)

**Features:**
- Evolution path management (defining what creatures can evolve into)
- Evolution condition checking (level, traits, etc.)
- Creature type transformation
- Stat recalculation for evolved forms
- Full heal on evolution

**Key Classes:**
- `EvolutionPath` - Defines a possible evolution (Newborn → Warrior @ Level 10)
- `EvolutionSystem` - Manages all evolution paths and executes evolutions

**Key Methods:**
- `add_evolution_path(path)` - Registers an evolution possibility
- `can_evolve(creature)` - Checks if creature can evolve
- `evolve(creature, path)` - Transforms creature to evolved form

**Use When:** Creatures level up and reach evolution thresholds (like Pokémon evolution)

**NOT Used For:** Breeding/reproduction (separate concern)

---

### 5. GeneticsSystem (`src/models/evolution.py`) [DEPRECATED]

**Status:** DEPRECATED - Maintained only for backward compatibility

**Why Deprecated:** 
- Simple 50/50 trait inheritance (no Mendelian genetics)
- Basic stat averaging (no weighted variation)
- Duplicates functionality of GeneticsEngine
- Less sophisticated than GeneticsEngine

**Migration Path:** Use `Breeding` system instead, which wraps `GeneticsEngine`

**Note:** This class is now a thin wrapper around GeneticsEngine to maintain API compatibility.

---

## System Interactions

```
High-Level Game Systems
         ↓
   Breeding System ←────────┐
         ↓                  │
   GeneticsEngine           │
    (Trait/Stat Logic)      │
                            │
                    Creature.reproduce()
                            ↓
                      New Offspring
                            
                            
Pellets
   ↓
Pellet.reproduce()
   ↓
PelletGenetics
   ↓
New Pellet Offspring


Leveling/Experience
   ↓
EvolutionSystem.can_evolve()
   ↓
EvolutionSystem.evolve()
   ↓
Transformed Creature
```

## Code Duplication Resolution

### Before Refactoring

**Problem:** Three different systems handled similar logic:

1. `GeneticsEngine.combine_traits()` - Advanced Mendelian genetics
2. `GeneticsSystem._inherit_traits()` - Simple 50/50 inheritance
3. `Breeding.calculate_inherited_traits()` - Custom 70-90% inheritance

**Result:** Inconsistent behavior, maintenance burden, confusion about which to use

### After Refactoring

**Solution:**

1. **GeneticsEngine** = Single source of truth for genetics logic
2. **Breeding** = High-level API that delegates to GeneticsEngine
3. **GeneticsSystem** = Deprecated wrapper for backward compatibility
4. **EvolutionSystem** = Separate concern (type transformation, not breeding)

**Benefits:**
- Single implementation of genetics logic (DRY principle)
- Clear separation of concerns
- Easier to test and maintain
- Backward compatible

---

## Usage Examples

### Breeding Creatures

```python
from src.systems.breeding import Breeding

breeding_system = Breeding(mutation_rate=0.1)

# Check if creatures can breed
if parent1.can_breed() and parent2.can_breed():
    offspring = breeding_system.breed(parent1, parent2)
    print(f"Born: {offspring.name}")
```

### Pellet Reproduction

```python
# Asexual reproduction (cloning)
offspring = pellet.reproduce(mutation_rate=0.15)

# Sexual reproduction
offspring = pellet.reproduce(mutation_rate=0.15, partner=other_pellet)
```

### Evolution

```python
from src.models.evolution import EvolutionSystem, EvolutionPath

evolution_system = EvolutionSystem()

# Define evolution path
path = EvolutionPath(
    from_type="Newborn",
    to_type="Warrior",
    min_level=10
)
evolution_system.add_evolution_path(path)

# Check and evolve
if evolution_system.can_evolve(creature):
    success, message = evolution_system.evolve(creature)
    print(message)  # "Evolved from Newborn to Warrior!"
```

### Advanced Genetics (Direct Use - Rare)

```python
from src.models.genetics import GeneticsEngine

# Only use directly if you need fine-grained control
genetics = GeneticsEngine(mutation_rate=0.1)
traits = genetics.combine_traits(parent1, parent2, generation=5)
stats = genetics.combine_stats(parent1, parent2)
```

---

## Design Principles

### Single Responsibility Principle

Each system has ONE clear responsibility:

- **GeneticsEngine**: Genetic inheritance algorithms
- **PelletGenetics**: Pellet-specific genetics
- **Breeding**: High-level breeding orchestration
- **EvolutionSystem**: Type transformation
- **GeneticsSystem**: Deprecated backward compatibility

### Don't Repeat Yourself (DRY)

All trait/stat inheritance logic is now in **one place** (GeneticsEngine), eliminating the previous duplication across three different implementations.

### Open/Closed Principle

Systems are open for extension (e.g., new evolution paths) but closed for modification (core genetics logic is stable).

---

## Testing Strategy

### Unit Tests

- `test_genetics.py` - Tests GeneticsEngine and PelletGenetics
- `test_breeding.py` - Tests Breeding system
- `test_evolution.py` - Tests EvolutionSystem and deprecated GeneticsSystem

### Integration Tests

- `test_ecosystem_breeding.py` - Tests breeding in spatial battles
- `test_pellet.py` - Tests pellet reproduction

### Key Test Coverage

✅ Mendelian genetics (dominant/recessive/codominant)
✅ Trait blending and inheritance
✅ Stat combination with variation
✅ Mutation tracking and provenance
✅ Breeding eligibility checks
✅ Evolution path conditions
✅ Pellet asexual/sexual reproduction
✅ Backward compatibility with GeneticsSystem

---

## Migration Guide

### If You're Using GeneticsSystem (Deprecated)

**Old Code:**
```python
from src.models.evolution import GeneticsSystem

genetics = GeneticsSystem(mutation_rate=0.1)
offspring = genetics.breed(parent1, parent2, "Baby")
```

**New Code:**
```python
from src.systems.breeding import Breeding

breeding = Breeding(mutation_rate=0.1)
offspring = breeding.breed(parent1, parent2)
```

### If You're Implementing Custom Breeding Logic

**Before:**
```python
# Custom trait inheritance
def my_custom_breed(p1, p2):
    traits = []
    for trait in p1.traits + p2.traits:
        if random.random() < 0.5:
            traits.append(trait)
    # ... more custom logic
```

**After (Use GeneticsEngine):**
```python
from src.models.genetics import GeneticsEngine

def my_custom_breed(p1, p2):
    genetics = GeneticsEngine(mutation_rate=0.1)
    # Use the advanced genetics logic
    traits = genetics.combine_traits(p1, p2, generation=0)
    stats = genetics.combine_stats(p1, p2)
    # ... your custom wrapper logic
```

---

## Future Enhancements

### Potential Additions

1. **Hybrid Evolution** - Breeding between different creature types
2. **Genetic Markers** - Track specific genes through lineages
3. **Epigenetics** - Environmental influences on gene expression
4. **Genetic Diseases** - Recessive harmful traits
5. **Selective Breeding** - Player-directed trait selection

### Extensibility Points

- **Custom Dominance Rules** - Override `_combine_same_trait()` in GeneticsEngine
- **New Trait Types** - Add to `expanded_traits.py`
- **Custom Evolution Conditions** - Add to `EvolutionPath.conditions`
- **Pellet Traits** - Add new pellet trait types in `PelletTraits`

---

## Troubleshooting

### Issue: "ImportError: cannot import name 'GeneticsSystem'"

**Solution:** Make sure you're importing from the correct module:
```python
from src.models.evolution import GeneticsSystem  # Deprecated but exists
```

### Issue: "Offspring doesn't inherit expected traits"

**Check:** 
1. Trait dominance settings (dominant/recessive/codominant)
2. Mutation rate (high rate = more variation)
3. Random seed (genetics uses randomness)

### Issue: "Breeding not working in battle"

**Check:**
1. Creatures are mature (`creature.mature == True`)
2. Creatures have enough health (`hp > 50% max_hp`)
3. Creatures have enough hunger (`hunger > 70`)
4. Creatures are within breeding range

---

## Conclusion

The refactored architecture provides:

✅ **Clear boundaries** between systems
✅ **No code duplication** in genetics logic  
✅ **Single source of truth** (GeneticsEngine)
✅ **Backward compatibility** (GeneticsSystem wrapper)
✅ **Separation of concerns** (Breeding ≠ Evolution)
✅ **Comprehensive documentation**
✅ **Full test coverage**

This architecture supports maintainable, extensible genetics and breeding systems for the Evolution Battle game.
