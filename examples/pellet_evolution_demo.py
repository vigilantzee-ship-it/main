"""
Pellet Evolution Demo - Showcase evolving food ecosystem

This demo shows how pellets evolve over time through reproduction and mutation,
creating a dynamic food ecosystem for creatures.
"""

import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats
from src.models.trait import Trait
from src.systems.battle_spatial import SpatialBattle


def print_pellet_stats(battle):
    """Print statistics about the pellet population."""
    pellets = battle.arena.pellets
    
    if not pellets:
        print("  No pellets in arena")
        return
    
    print(f"  Total pellets: {len(pellets)}")
    
    # Nutrition stats
    nutrition_values = [p.get_nutritional_value() for p in pellets]
    avg_nutrition = sum(nutrition_values) / len(nutrition_values)
    min_nutrition = min(nutrition_values)
    max_nutrition = max(nutrition_values)
    
    print(f"  Nutrition - Avg: {avg_nutrition:.1f}, Min: {min_nutrition:.1f}, Max: {max_nutrition:.1f}")
    
    # Growth rate stats
    growth_rates = [p.traits.growth_rate for p in pellets]
    avg_growth = sum(growth_rates) / len(growth_rates)
    
    print(f"  Avg Growth Rate: {avg_growth:.3f}")
    
    # Generation stats
    generations = [p.generation for p in pellets]
    max_gen = max(generations)
    avg_gen = sum(generations) / len(generations)
    
    print(f"  Generations - Max: {max_gen}, Avg: {avg_gen:.1f}")
    
    # Age stats
    ages = [p.age for p in pellets]
    max_age = max(ages)
    avg_age = sum(ages) / len(ages)
    
    print(f"  Age - Max: {max_age}, Avg: {avg_age:.1f}")
    
    # Toxicity stats
    toxicity_values = [p.traits.toxicity for p in pellets]
    avg_toxicity = sum(toxicity_values) / len(toxicity_values)
    
    print(f"  Avg Toxicity: {avg_toxicity:.2f}")


def print_creature_stats(battle):
    """Print statistics about creatures."""
    alive = [c for c in battle.creatures if c.is_alive()]
    
    print(f"  Alive creatures: {len(alive)}/{len(battle.creatures)}")
    
    if alive:
        avg_hunger = sum(c.creature.hunger for c in alive) / len(alive)
        print(f"  Avg Hunger: {avg_hunger:.1f}")
        
        avg_hp = sum(c.creature.stats.hp for c in alive) / len(alive)
        max_hp = sum(c.creature.stats.max_hp for c in alive) / len(alive)
        print(f"  Avg HP: {avg_hp:.1f}/{max_hp:.1f}")


def run_pellet_evolution_demo():
    """
    Run a demo showing pellet evolution over time.
    """
    print("=" * 60)
    print("PELLET EVOLUTION DEMO")
    print("=" * 60)
    print()
    print("This demo shows how pellets evolve through reproduction and mutation.")
    print("Watch as the pellet population changes over time!")
    print()
    
    # Create creatures with specific traits for interesting dynamics
    print("Creating ecosystem with 6 creatures...")
    creatures = []
    
    # Mix of herbivores and omnivores
    for i in range(4):
        c = Creature(
            name=f"Herbivore-{i+1}",
            hunger=100,
            traits=[Trait(name="Herbivore")]  # Can only eat plants
        )
        creatures.append(c)
    
    for i in range(2):
        c = Creature(
            name=f"Omnivore-{i+1}",
            hunger=100
            # Omnivores can eat both plants and creatures
        )
        creatures.append(c)
    
    # Create battle with initial pellet population
    print("Initializing battle arena with 15 initial pellets...")
    battle = SpatialBattle(
        creatures,
        initial_resources=15,
        resource_spawn_rate=0.2,  # Spawn 0.2 pellets per second
        arena_width=120.0,
        arena_height=120.0
    )
    
    print()
    print("=" * 60)
    print("SIMULATION START")
    print("=" * 60)
    print()
    
    # Run simulation
    TOTAL_TIME = 60  # seconds (reduced for quick demo)
    UPDATE_INTERVAL = 15  # Print stats every 15 seconds
    
    for sim_time in range(0, TOTAL_TIME, UPDATE_INTERVAL):
        # Update battle
        for _ in range(UPDATE_INTERVAL * 2):  # 2 updates per second
            if battle.is_over:
                print("Battle ended (population collapse)")
                break
            battle.update(0.5)
        
        if battle.is_over:
            break
        
        # Print statistics
        print(f"--- Time: {sim_time}s ---")
        print()
        
        print("Creature Status:")
        print_creature_stats(battle)
        print()
        
        print("Pellet Population:")
        print_pellet_stats(battle)
        print()
        
        # Show some interesting pellets
        pellets = battle.arena.pellets
        if pellets:
            # Find most evolved pellet
            max_gen_pellet = max(pellets, key=lambda p: p.generation)
            if max_gen_pellet.generation > 0:
                print(f"  Most Evolved: Gen {max_gen_pellet.generation}, "
                      f"Nutrition: {max_gen_pellet.get_nutritional_value():.1f}, "
                      f"Age: {max_gen_pellet.age}")
            
            # Find best nutrition pellet
            best_nutrition = max(pellets, key=lambda p: p.get_nutritional_value())
            print(f"  Most Nutritious: {best_nutrition.get_nutritional_value():.1f}, "
                  f"Gen: {best_nutrition.generation}, "
                  f"Growth Rate: {best_nutrition.traits.growth_rate:.3f}")
        
        print()
    
    print("=" * 60)
    print("SIMULATION COMPLETE")
    print("=" * 60)
    print()
    
    # Final summary
    print("Final Statistics:")
    print()
    print("Pellet Evolution:")
    print_pellet_stats(battle)
    print()
    
    print("Creature Status:")
    print_creature_stats(battle)
    print()
    
    print(f"Total births: {battle.birth_count}")
    print(f"Total deaths: {battle.death_count}")
    print()
    
    # Analyze evolution
    pellets = battle.arena.pellets
    if pellets:
        print("Evolution Analysis:")
        
        # Compare to initial generation
        gen0_pellets = [p for p in pellets if p.generation == 0]
        evolved_pellets = [p for p in pellets if p.generation > 0]
        
        print(f"  Generation 0 remaining: {len(gen0_pellets)}")
        print(f"  Evolved pellets: {len(evolved_pellets)}")
        
        if evolved_pellets:
            avg_evolved_nutrition = sum(p.get_nutritional_value() for p in evolved_pellets) / len(evolved_pellets)
            print(f"  Avg evolved nutrition: {avg_evolved_nutrition:.1f}")
            
            avg_evolved_growth = sum(p.traits.growth_rate for p in evolved_pellets) / len(evolved_pellets)
            print(f"  Avg evolved growth rate: {avg_evolved_growth:.3f}")
            
            max_generation = max(p.generation for p in pellets)
            print(f"  Maximum generation reached: {max_generation}")
    
    print()
    print("=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print()
    print("Key Observations:")
    print("- Pellets reproduce and mutate, creating genetic diversity")
    print("- Population is limited by carrying capacity")
    print("- Creatures consume pellets, creating selection pressure")
    print("- Dead creatures spawn new pellets, completing the cycle")
    print("- Over time, pellet traits evolve based on survival")


if __name__ == "__main__":
    run_pellet_evolution_demo()
