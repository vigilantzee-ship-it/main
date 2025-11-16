"""
Environmental Simulation Demo

Demonstrates the environmental system with weather, terrain, day/night cycles,
and hazards affecting creature behavior and survival.
"""

from src.models.creature import Creature, CreatureType
from src.models.stats import Stats
from src.models.environment import Environment, WeatherType, TimeOfDay, EnvironmentalHazard, HazardType
from src.models.spatial import Vector2D
from src.models.trait import Trait
from src.systems.battle_spatial import SpatialBattle
import time


def create_creature_with_traits(name: str, traits_list: list) -> Creature:
    """Create a creature with specific environmental traits."""
    creature_type = CreatureType(
        name="Survivor",
        base_stats=Stats(max_hp=100, attack=12, defense=10, speed=15)
    )
    creature = Creature(name=name, creature_type=creature_type, level=1)
    for trait in traits_list:
        creature.traits.append(trait)
    return creature


def main():
    """Run environmental simulation demo."""
    print("=" * 70)
    print("EVOLUTION BATTLE GAME - ENVIRONMENTAL SIMULATION DEMO")
    print("=" * 70)
    print()
    
    # Create creatures with different environmental adaptations
    print("Creating creatures with environmental adaptations...")
    creatures = [
        create_creature_with_traits("Aqua", [
            Trait(name="Aquatic", description="Fast in water", trait_type="environmental")
        ]),
        create_creature_with_traits("Rocky", [
            Trait(name="Rock Climber", description="Expert at rocky terrain", trait_type="environmental")
        ]),
        create_creature_with_traits("Nocturnus", [
            Trait(name="Nocturnal", description="Active at night", trait_type="environmental")
        ]),
        create_creature_with_traits("Blazewalker", [
            Trait(name="Fire Proof", description="Immune to fire", trait_type="environmental"),
            Trait(name="Heat Resistant", description="Thrives in heat", trait_type="environmental")
        ]),
        create_creature_with_traits("Survivor", [
            Trait(name="All Terrain", description="Versatile movement", trait_type="environmental"),
            Trait(name="Warm Blooded", description="Temperature stable", trait_type="environmental")
        ]),
        create_creature_with_traits("Nighthawk", [
            Trait(name="Nocturnal", description="Active at night", trait_type="environmental"),
            Trait(name="Tracker", description="Reads environment", trait_type="environmental")
        ]),
        create_creature_with_traits("Tundra", [
            Trait(name="Thick Fur", description="Insulated", trait_type="environmental"),
            Trait(name="Storm Walker", description="Unaffected by storms", trait_type="environmental")
        ]),
        create_creature_with_traits("Desert Fox", [
            Trait(name="Desert Adapted", description="Thrives in desert", trait_type="environmental"),
            Trait(name="Drought Survivor", description="Efficient water usage", trait_type="environmental")
        ]),
    ]
    
    print(f"✓ Created {len(creatures)} creatures with unique adaptations")
    for c in creatures:
        trait_names = [t.name for t in c.traits]
        print(f"  - {c.name}: {', '.join(trait_names)}")
    print()
    
    # Create custom environment
    print("Setting up environment...")
    env = Environment(
        width=100.0,
        height=100.0,
        cell_size=10.0,
        enable_weather=True,
        enable_day_night=True,
        day_night_cycle_duration=60.0  # 1 minute = 24 hours
    )
    
    # Set specific weather
    env.weather.weather_type = WeatherType.RAINY
    env.weather.temperature = 15.0
    env.weather.humidity = 0.8
    env.weather.precipitation = 0.5
    
    print(f"✓ Environment created:")
    print(f"  - Arena: {env.width}x{env.height}")
    print(f"  - Weather: {env.weather.weather_type.value}")
    print(f"  - Temperature: {env.weather.temperature}°C")
    print(f"  - Humidity: {env.weather.humidity * 100:.0f}%")
    print(f"  - Time: {env.day_night.get_time_of_day().value}")
    print()
    
    # Add some environmental hazards
    print("Adding environmental hazards...")
    hazards = [
        EnvironmentalHazard(
            hazard_type=HazardType.FIRE,
            position=Vector2D(75, 75),
            radius=15.0,
            damage=5.0,
            duration=-1  # Permanent
        ),
        EnvironmentalHazard(
            hazard_type=HazardType.POISON_CLOUD,
            position=Vector2D(25, 25),
            radius=10.0,
            damage=3.0,
            duration=-1
        ),
    ]
    for hazard in hazards:
        env.add_hazard(hazard)
    print(f"✓ Added {len(hazards)} environmental hazards")
    for h in hazards:
        print(f"  - {h.hazard_type.value} at ({h.position.x:.0f}, {h.position.y:.0f}), radius {h.radius:.0f}")
    print()
    
    # Create battle with environment
    print("Initializing battle with environmental simulation...")
    battle = SpatialBattle(
        creatures,
        arena_width=100.0,
        arena_height=100.0,
        environment=env,
        resource_spawn_rate=0.5,
        initial_resources=15
    )
    print(f"✓ Battle initialized with {len(battle.creatures)} creatures")
    print()
    
    # Run simulation
    print("=" * 70)
    print("SIMULATION RUNNING")
    print("=" * 70)
    print()
    
    total_time = 0.0
    update_interval = 2.0  # Update every 2 seconds
    report_interval = 10.0  # Report every 10 seconds
    last_report = 0.0
    
    print("Simulating environmental effects on creatures...")
    print()
    
    while not battle.is_over and total_time < 30.0:  # Run for 30 seconds
        battle.update(update_interval)
        total_time += update_interval
        
        # Report status periodically
        if total_time - last_report >= report_interval:
            alive = [c for c in battle.creatures if c.is_alive()]
            
            print(f"[T+{total_time:.0f}s] Status Report:")
            print(f"  Environment:")
            print(f"    - Weather: {env.weather.weather_type.value}, {env.weather.temperature:.1f}°C")
            print(f"    - Time: {env.day_night.get_time_of_day().value} ({env.day_night.get_current_hour():.1f}h)")
            print(f"    - Visibility: {env.get_combined_visibility(Vector2D(50, 50)):.0%}")
            print(f"  Population: {len(alive)}/{len(battle.creatures)} alive")
            
            # Show creature status
            for c in alive[:3]:  # Show first 3 alive creatures
                pos = c.spatial.position
                terrain = env.get_terrain_at(pos)
                terrain_name = terrain.terrain_type.value if terrain else "unknown"
                hazard_dmg = env.get_total_hazard_damage(pos)
                
                print(f"    - {c.creature.name}:")
                print(f"        HP: {c.creature.stats.hp:.0f}/{c.creature.stats.max_hp:.0f}, "
                      f"Hunger: {c.creature.hunger:.0f}/100")
                print(f"        Position: ({pos.x:.1f}, {pos.y:.1f}) - {terrain_name} terrain")
                if hazard_dmg > 0:
                    print(f"        ⚠️  In hazard zone! {hazard_dmg:.1f} damage/sec")
            
            print()
            last_report = total_time
    
    # Final report
    print("=" * 70)
    print("SIMULATION COMPLETE")
    print("=" * 70)
    print()
    
    alive = [c for c in battle.creatures if c.is_alive()]
    print(f"Final Status:")
    print(f"  Duration: {total_time:.0f} seconds")
    print(f"  Survivors: {len(alive)}/{len(battle.creatures)}")
    print()
    
    print("Survivor Details:")
    for c in alive:
        pos = c.spatial.position
        terrain = env.get_terrain_at(pos)
        terrain_name = terrain.terrain_type.value if terrain else "unknown"
        
        print(f"  {c.creature.name}:")
        print(f"    HP: {c.creature.stats.hp:.0f}/{c.creature.stats.max_hp:.0f}")
        print(f"    Hunger: {c.creature.hunger:.0f}/100")
        print(f"    Age: {c.creature.age:.1f}s")
        print(f"    Position: ({pos.x:.1f}, {pos.y:.1f}) - {terrain_name}")
        trait_names = [t.name for t in c.creature.traits]
        print(f"    Traits: {', '.join(trait_names)}")
        print()
    
    if len(alive) < len(battle.creatures):
        print(f"Casualties: {len(battle.creatures) - len(alive)}")
        for c in battle.creatures:
            if not c.is_alive():
                print(f"  - {c.creature.name} (died)")
        print()
    
    # Environmental summary
    print("Environmental Impact:")
    print(f"  Weather effects:")
    print(f"    - Movement modifier: {env.weather.get_movement_modifier():.2f}x")
    print(f"    - Hunger modifier: {env.weather.get_hunger_modifier():.2f}x")
    print(f"    - Resource quality: {env.weather.get_resource_quality_modifier():.2f}x")
    print()
    print(f"  Time effects:")
    print(f"    - Current time: {env.day_night.get_time_of_day().value}")
    print(f"    - Visibility modifier: {env.day_night.get_visibility_modifier():.2f}x")
    print(f"    - Activity modifier: {env.day_night.get_activity_modifier():.2f}x")
    print()
    print(f"  Active hazards: {len(env.hazards)}")
    print()
    
    print("=" * 70)
    print("Demo complete! Environmental simulation affects:")
    print("  ✓ Creature movement speed (terrain + weather)")
    print("  ✓ Hunger depletion rate (weather)")
    print("  ✓ Resource quality and quantity (terrain + weather)")
    print("  ✓ Visibility and combat effectiveness (time of day + terrain)")
    print("  ✓ Environmental hazard damage (with trait resistances)")
    print("  ✓ Creature survival strategies based on traits")
    print("=" * 70)


if __name__ == "__main__":
    main()
