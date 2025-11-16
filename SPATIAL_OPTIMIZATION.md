# Spatial Hash Grid Optimization

## Overview

The spatial hash grid optimization provides O(n) collision detection and proximity queries for the battle system, replacing the previous O(n²) implementations. This enables stable 60 FPS performance with 80+ creatures and 100+ pellets.

## Key Components

### SpatialHashGrid (`src/models/spatial.py`)

A generic spatial partitioning data structure that divides 2D space into a grid of cells.

**Features:**
- **O(1) cell lookup**: Constant-time position-to-cell conversion
- **O(n) insertion**: Linear time to populate all entities
- **O(k) queries**: Proximity searches only check nearby cells (k << n)
- **Automatic management**: Entities track their cells and update efficiently

**Usage:**
```python
from src.models.spatial import SpatialHashGrid, Vector2D

# Create a grid for a 100x100 arena with 10-unit cells
grid = SpatialHashGrid(width=100.0, height=100.0, cell_size=10.0)

# Insert entities
entity1 = MyEntity()
grid.insert(entity1, Vector2D(25, 25))

# Update entity position when it moves
grid.update(entity1, Vector2D(30, 30))

# Find entities within radius
nearby = grid.query_radius(Vector2D(50, 50), radius=20.0)

# Find nearest entity
nearest, distance = grid.query_nearest(Vector2D(50, 50), max_distance=30.0)

# Remove entity
grid.remove(entity1)
```

### Arena Integration (`src/models/spatial.py`)

The `Arena` class automatically manages resources (pellets) in a spatial grid.

**Usage:**
```python
from src.models.spatial import Arena, Vector2D

arena = Arena(width=100.0, height=100.0)  # Auto-creates spatial grid

# Add resources - automatically inserted into spatial grid
arena.add_pellet(pellet)

# Query resources efficiently
nearby_resources = arena.query_resources_in_radius(position, radius=20.0)

# Get nearest resource using spatial optimization
nearest = arena.get_nearest_resource(position)
```

### Battle System (`src/systems/battle_spatial.py`)

The battle system uses two spatial grids:
1. **Creature Grid**: Tracks all battle creatures for targeting and proximity
2. **Resource Grid** (via Arena): Tracks pellets and food sources

**Optimized Operations:**

#### Targeting (O(n²) → O(k))
```python
# Old: Checked all creatures
for other in all_creatures:
    distance = creature.distance_to(other)
    # ...

# New: Only checks nearby creatures within search radius
nearby = self.creature_grid.query_radius(
    creature.position, 
    search_radius=50.0,
    exclude={creature}
)
```

#### Breeding (O(n²) → O(n))
```python
# Old: Nested loop over all pairs
for i, creature1 in enumerate(creatures):
    for creature2 in creatures[i+1:]:
        if distance(creature1, creature2) <= breeding_range:
            # ...

# New: Each creature queries grid once
for creature in creatures:
    nearby = self.creature_grid.query_radius(
        creature.position,
        breeding_range,
        exclude={creature}
    )
```

#### Pellet Density (O(n²) → O(k))
```python
# Old: Each pellet counted all other pellets
nearby_count = sum(
    1 for p in all_pellets
    if distance(pellet, p) <= radius
)

# New: Spatial grid query with exact distance
nearby = arena.spatial_grid.query_radius(
    pellet_pos,
    radius,
    exclude={pellet},
    exact_distance=True
)
nearby_count = len(nearby)
```

## Performance Characteristics

### Complexity Analysis

| Operation | Before | After | Improvement |
|-----------|--------|-------|-------------|
| Targeting | O(n²) | O(k) | ~100x for n=100 |
| Breeding | O(n²) | O(n) | ~100x for n=100 |
| Pellet Density | O(n²) | O(k) | ~50x for n=100 |
| Frame Time | 160ms+ | <10ms | 16x+ faster |

### Measured Performance

With spatial hash grid optimization:
- **20 creatures**: 4.07ms avg frame time (✓ 60+ FPS)
- **50 creatures**: 5.36ms avg frame time (✓ 60+ FPS)
- **80 creatures**: 9.47ms avg frame time (✓ 60+ FPS)
- **100+ pellets**: <4ms per frame (✓ 60+ FPS)

Target: <16.67ms for 60 FPS

## Configuration

### Cell Size Selection

The grid cell size affects performance and accuracy:
- **Smaller cells** (5-10): More precise, slightly slower queries
- **Larger cells** (20-30): Faster queries, less precise

**Default**: 10% of arena's smaller dimension, clamped to 5-20 units

```python
# Automatic (recommended)
arena = Arena(100.0, 100.0)  # Uses cell_size=10.0

# Manual
arena = Arena(100.0, 100.0, cell_size=15.0)
```

### Exact Distance Filtering

For operations requiring precise distance checks (e.g., pellet density):

```python
# Bounding box (faster, less precise)
nearby = grid.query_radius(position, radius=20.0)

# Exact distance (slower, more precise)
nearby = grid.query_radius(
    position, 
    radius=20.0,
    exact_distance=True,
    get_position=lambda e: e.position
)
```

## Best Practices

1. **Use bounding box queries for gameplay**: Combat targeting and movement don't need exact distances
2. **Use exact distance for game rules**: Breeding range and pellet density should be precise
3. **Update grid on movement**: Call `grid.update()` after moving entities
4. **Remove dead entities**: Clean up the grid when entities die
5. **Choose appropriate cell size**: Too small = overhead, too large = false positives

## Implementation Notes

### Hashable Entities

Entities must be hashable to use with the spatial grid. We've added hash support:

```python
class Pellet:
    def __hash__(self):
        return hash(self.pellet_id)
    
    def __eq__(self, other):
        if not isinstance(other, Pellet):
            return False
        return self.pellet_id == other.pellet_id
```

### Grid Management

The battle system automatically:
- Inserts creatures on spawn
- Updates creatures on movement
- Removes creatures on death
- Manages pellet grid through Arena

## Testing

Run performance tests:
```bash
python -m unittest tests.test_spatial_performance -v
```

Run the performance demo:
```bash
python examples/spatial_performance_demo.py
```

## Future Optimizations

Potential enhancements:
1. **Multi-grid optimization**: Separate grids for different entity types
2. **Dynamic cell sizing**: Adjust cell size based on entity density
3. **Spatial caching**: Cache frequently queried positions
4. **Parallel queries**: Multi-threaded proximity checks for very large populations
5. **Quadtree integration**: Hybrid approach for sparse/dense areas

## References

- Issue: #13 - Performance optimization for large populations
- Files: 
  - `src/models/spatial.py` - SpatialHashGrid implementation
  - `src/systems/battle_spatial.py` - Battle system integration
  - `tests/test_spatial_performance.py` - Performance tests
  - `examples/spatial_performance_demo.py` - Demo script
