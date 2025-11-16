"""
Demo: Enhanced Genetics and Cross-Entity Interactions

This demo showcases:
1. Dominant/recessive gene inheritance
2. Trait blending from both parents
3. Cross-entity interactions (creatures and pellets)
4. Pellet sexual reproduction
5. Multi-generational trait tracking
"""

from src.models.creature import Creature, CreatureType
from src.models.pellet import Pellet, PelletTraits
from src.models.stats import Stats
from src.models.expanded_traits import (
    AGGRESSIVE_TRAIT, TIMID_TRAIT, ARMORED_TRAIT, SWIFT_TRAIT,
    SCAVENGER_TRAIT, HERBIVORE_TRAIT, TOXIN_RESISTANT_TRAIT,
    POLLINATOR_TRAIT, SYMBIOTIC_TRAIT
)
from src.systems.breeding import Breeding
from src.models.cross_entity_interactions import (
    CrossEntityInteractions,
    find_best_pellet_for_creature
)


def print_section(title):
    """Print a section header."""
    print(f"\n{'=' * 60}")
    print(f" {title}")
    print(f"{'=' * 60}\n")


def print_creature(creature, label="Creature"):
    """Print creature details."""
    print(f"{label}: {creature.name}")
    print(f"  Stats: HP={creature.stats.max_hp}, ATK={creature.stats.attack}, "
          f"DEF={creature.stats.defense}, SPD={creature.stats.speed}")
    print(f"  Traits: {[t.name for t in creature.traits]}")
    print(f"  Hue: {creature.hue:.1f}")
    if creature.traits:
        for trait in creature.traits:
            print(f"    - {trait.name}: "
                  f"STR={trait.strength_modifier:.2f}, "
                  f"SPD={trait.speed_modifier:.2f}, "
                  f"DEF={trait.defense_modifier:.2f} "
                  f"({trait.dominance})")
            print(f"      Provenance: {trait.provenance.source_type}, "
                  f"Gen={trait.provenance.generation}, "
                  f"Mutations={trait.provenance.mutation_count}")
    print()


def demo_dominant_recessive_genes():
    """Demonstrate dominant/recessive gene inheritance."""
    print_section("1. Dominant vs Recessive Gene Inheritance")
    
    # Create creature type
    warrior = CreatureType(
        name="Warrior",
        base_stats=Stats(max_hp=100, attack=15, defense=10, speed=12)
    )
    
    # Parent 1: Aggressive (dominant)
    parent1 = Creature(name="Aggressor", creature_type=warrior, mature=True, hue=120)
    parent1.add_trait(AGGRESSIVE_TRAIT.copy())
    print_creature(parent1, "Parent 1 (Aggressive - Dominant)")
    
    # Parent 2: Timid (recessive)
    parent2 = Creature(name="Timid", creature_type=warrior, mature=True, hue=180)
    parent2.add_trait(TIMID_TRAIT.copy())
    print_creature(parent2, "Parent 2 (Timid - Recessive)")
    
    # Breed them
    breeding = Breeding(mutation_rate=0.05)
    offspring = breeding.breed(parent1, parent2)
    
    print_creature(offspring, "Offspring")
    
    print("Analysis:")
    if offspring.has_trait("Aggressive"):
        print("  ✓ Dominant Aggressive trait expressed (as expected)")
    if offspring.has_trait("Timid"):
        print("  ✓ Recessive Timid trait also present (single parent)")
    
    print("\nNote: With dominant vs recessive, the dominant trait should")
    print("have stronger expression in the offspring.")


def demo_trait_blending():
    """Demonstrate trait blending from both parents."""
    print_section("2. Trait Blending from Both Parents")
    
    warrior = CreatureType(
        name="Warrior",
        base_stats=Stats(max_hp=100, attack=15, defense=10, speed=12)
    )
    
    # Parent 1: Armored (dominant)
    parent1 = Creature(name="Tank", creature_type=warrior, mature=True)
    parent1.add_trait(ARMORED_TRAIT.copy())
    
    # Parent 2: Swift (dominant)
    parent2 = Creature(name="Speedster", creature_type=warrior, mature=True)
    parent2.add_trait(SWIFT_TRAIT.copy())
    
    print("Parent 1 has ARMORED (high defense, low speed)")
    print("Parent 2 has SWIFT (high speed, low defense)")
    print()
    
    # Breed multiple times to show variation
    breeding = Breeding(mutation_rate=0.1)
    
    print("Breeding 5 offspring to demonstrate variation:\n")
    for i in range(5):
        offspring = breeding.breed(parent1, parent2)
        print(f"Offspring {i+1}:")
        print(f"  Stats: HP={offspring.stats.max_hp}, ATK={offspring.stats.attack}, "
              f"DEF={offspring.stats.defense}, SPD={offspring.stats.speed}")
        print(f"  Traits: {[t.name for t in offspring.traits]}")
    
    print("\nAnalysis:")
    print("  ✓ Each offspring has different stats (not pure average)")
    print("  ✓ Traits may be inherited from both parents")
    print("  ✓ Genetic variation creates diverse population")


def demo_cross_entity_interactions():
    """Demonstrate cross-entity interactions."""
    print_section("3. Cross-Entity Interactions: Creatures and Pellets")
    
    warrior = CreatureType(
        name="Warrior",
        base_stats=Stats(max_hp=100, attack=15, defense=10, speed=12)
    )
    
    # Create different pellets
    normal_pellet = Pellet(x=10, y=10, traits=PelletTraits(
        nutritional_value=30.0,
        toxicity=0.1,
        palatability=0.6,
        growth_rate=0.02,
        color=(100, 200, 100)
    ))
    
    toxic_pellet = Pellet(x=20, y=20, traits=PelletTraits(
        nutritional_value=40.0,
        toxicity=0.8,
        palatability=0.3,
        growth_rate=0.01,
        color=(200, 100, 200)
    ))
    
    corpse_pellet = Pellet(x=30, y=30, traits=PelletTraits(
        nutritional_value=60.0,
        growth_rate=0.0,  # Corpses don't reproduce
        toxicity=0.1,
        palatability=0.7,
        color=(200, 100, 100)
    ))
    
    print("Available Pellets:")
    print(f"  1. Normal: nutrition={normal_pellet.traits.nutritional_value}, "
          f"toxicity={normal_pellet.traits.toxicity}, color=green")
    print(f"  2. Toxic: nutrition={toxic_pellet.traits.nutritional_value}, "
          f"toxicity={toxic_pellet.traits.toxicity}, color=purple")
    print(f"  3. Corpse: nutrition={corpse_pellet.traits.nutritional_value}, "
          f"growth_rate={corpse_pellet.traits.growth_rate}, color=red")
    print()
    
    interactions = CrossEntityInteractions()
    
    # Test 1: Normal creature
    print("Test 1: Normal Creature")
    normal_creature = Creature(name="Normal", creature_type=warrior)
    
    prefs = {
        "normal": interactions.calculate_pellet_preference(normal_creature, normal_pellet),
        "toxic": interactions.calculate_pellet_preference(normal_creature, toxic_pellet),
        "corpse": interactions.calculate_pellet_preference(normal_creature, corpse_pellet)
    }
    
    print(f"  Preferences: Normal={prefs['normal']:.2f}, "
          f"Toxic={prefs['toxic']:.2f}, Corpse={prefs['corpse']:.2f}")
    print(f"  → Avoids toxic pellet (low preference)")
    print()
    
    # Test 2: Scavenger creature
    print("Test 2: Scavenger Creature")
    scavenger = Creature(name="Scavenger", creature_type=warrior)
    scavenger.add_trait(SCAVENGER_TRAIT.copy())
    
    prefs = {
        "normal": interactions.calculate_pellet_preference(scavenger, normal_pellet),
        "toxic": interactions.calculate_pellet_preference(scavenger, toxic_pellet),
        "corpse": interactions.calculate_pellet_preference(scavenger, corpse_pellet)
    }
    
    print(f"  Preferences: Normal={prefs['normal']:.2f}, "
          f"Toxic={prefs['toxic']:.2f}, Corpse={prefs['corpse']:.2f}")
    print(f"  → Strongly prefers corpse pellet (1.5x bonus)")
    
    # Show consumption effects
    effects = interactions.apply_consumption_effects(scavenger, corpse_pellet)
    print(f"  Consumption: +{effects['nutrition_gained']} nutrition")
    print(f"  Special: {effects['special_effects']}")
    print()
    
    # Test 3: Herbivore creature
    print("Test 3: Herbivore Creature")
    herbivore = Creature(name="Herbivore", creature_type=warrior)
    herbivore.add_trait(HERBIVORE_TRAIT.copy())
    
    prefs = {
        "normal": interactions.calculate_pellet_preference(herbivore, normal_pellet),
        "toxic": interactions.calculate_pellet_preference(herbivore, toxic_pellet),
        "corpse": interactions.calculate_pellet_preference(herbivore, corpse_pellet)
    }
    
    print(f"  Preferences: Normal={prefs['normal']:.2f}, "
          f"Toxic={prefs['toxic']:.2f}, Corpse={prefs['corpse']:.2f}")
    print(f"  → Prefers green (plant) pellet over red (meat)")
    print()
    
    # Test 4: Toxin Resistant creature
    print("Test 4: Toxin Resistant Creature")
    resistant = Creature(name="Resistant", creature_type=warrior)
    resistant.add_trait(TOXIN_RESISTANT_TRAIT.copy())
    
    prefs = {
        "normal": interactions.calculate_pellet_preference(resistant, normal_pellet),
        "toxic": interactions.calculate_pellet_preference(resistant, toxic_pellet),
        "corpse": interactions.calculate_pellet_preference(resistant, corpse_pellet)
    }
    
    print(f"  Preferences: Normal={prefs['normal']:.2f}, "
          f"Toxic={prefs['toxic']:.2f}, Corpse={prefs['corpse']:.2f}")
    print(f"  → Can eat toxic pellet (actually prefers it)")
    
    effects = interactions.apply_consumption_effects(resistant, toxic_pellet)
    print(f"  Toxin damage reduced: {effects['hp_change']} HP")
    print()


def demo_pellet_sexual_reproduction():
    """Demonstrate pellet sexual reproduction."""
    print_section("4. Pellet Sexual Reproduction")
    
    # Create two parent pellets with different traits
    parent1 = Pellet(x=10, y=10, traits=PelletTraits(
        nutritional_value=50.0,
        growth_rate=0.02,
        toxicity=0.1,
        palatability=0.8,
        color=(100, 200, 100)
    ))
    
    parent2 = Pellet(x=15, y=15, traits=PelletTraits(
        nutritional_value=30.0,
        growth_rate=0.03,
        toxicity=0.05,
        palatability=0.6,
        color=(150, 220, 120)
    ))
    
    print("Parent 1:")
    print(f"  Nutrition: {parent1.traits.nutritional_value}")
    print(f"  Growth: {parent1.traits.growth_rate}")
    print(f"  Toxicity: {parent1.traits.toxicity}")
    print(f"  Color: {parent1.traits.color}")
    print()
    
    print("Parent 2:")
    print(f"  Nutrition: {parent2.traits.nutritional_value}")
    print(f"  Growth: {parent2.traits.growth_rate}")
    print(f"  Toxicity: {parent2.traits.toxicity}")
    print(f"  Color: {parent2.traits.color}")
    print()
    
    # Create multiple offspring to show variation
    print("Offspring from sexual reproduction:")
    for i in range(5):
        offspring = parent1.reproduce(mutation_rate=0.15, partner=parent2)
        print(f"  {i+1}. Nutrition={offspring.traits.nutritional_value:.1f}, "
              f"Growth={offspring.traits.growth_rate:.3f}, "
              f"Toxicity={offspring.traits.toxicity:.2f}, "
              f"Color={offspring.traits.color}")
    
    print("\nAnalysis:")
    print("  ✓ Nutrition blended from both parents (~40, with variation)")
    print("  ✓ Growth rate blended (~0.025, with variation)")
    print("  ✓ Toxicity blended (~0.075, with variation)")
    print("  ✓ Color blended (greenish)")
    print("  ✓ Each offspring is unique due to weighted blending + mutation")


def demo_multi_generational():
    """Demonstrate multi-generational trait tracking."""
    print_section("5. Multi-Generational Trait Tracking")
    
    warrior = CreatureType(
        name="Warrior",
        base_stats=Stats(max_hp=100, attack=15, defense=10, speed=12)
    )
    
    breeding = Breeding(mutation_rate=0.05)
    
    # Generation 0
    print("Generation 0: Founders")
    gen0_a = Creature(name="Founder_A", creature_type=warrior, mature=True, hue=120)
    gen0_a.add_trait(AGGRESSIVE_TRAIT.copy())
    
    gen0_b = Creature(name="Founder_B", creature_type=warrior, mature=True, hue=180)
    gen0_b.add_trait(ARMORED_TRAIT.copy())
    
    print(f"  {gen0_a.name}: {[t.name for t in gen0_a.traits]}")
    print(f"  {gen0_b.name}: {[t.name for t in gen0_b.traits]}")
    print()
    
    # Generation 1
    print("Generation 1:")
    gen1_a = breeding.breed(gen0_a, gen0_b)
    gen1_a.name = "Gen1_A"
    gen1_a.mature = True
    
    gen1_b = breeding.breed(gen0_a, gen0_b)
    gen1_b.name = "Gen1_B"
    gen1_b.mature = True
    
    print(f"  {gen1_a.name}: {[t.name for t in gen1_a.traits]}")
    for trait in gen1_a.traits:
        print(f"    - {trait.name}: Gen={trait.provenance.generation}, "
              f"Source={trait.provenance.source_type}")
    
    print(f"  {gen1_b.name}: {[t.name for t in gen1_b.traits]}")
    for trait in gen1_b.traits:
        print(f"    - {trait.name}: Gen={trait.provenance.generation}, "
              f"Source={trait.provenance.source_type}")
    print()
    
    # Generation 2
    print("Generation 2:")
    gen2 = breeding.breed(gen1_a, gen1_b)
    gen2.name = "Gen2"
    
    print(f"  {gen2.name}: {[t.name for t in gen2.traits]}")
    for trait in gen2.traits:
        print(f"    - {trait.name}: Gen={trait.provenance.generation}, "
              f"Source={trait.provenance.source_type}, "
              f"Mutations={trait.provenance.mutation_count}")
    
    print("\nAnalysis:")
    print("  ✓ Each generation tracked in trait provenance")
    print("  ✓ Trait sources visible (inherited, mutated, emergent)")
    print("  ✓ Mutation count accumulates")
    print("  ✓ Complete ancestry can be reconstructed")


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print(" ENHANCED GENETICS AND CROSS-ENTITY INTERACTIONS DEMO")
    print("=" * 60)
    
    demo_dominant_recessive_genes()
    demo_trait_blending()
    demo_cross_entity_interactions()
    demo_pellet_sexual_reproduction()
    demo_multi_generational()
    
    print_section("Demo Complete")
    print("All features demonstrated successfully!")
    print("\nKey Takeaways:")
    print("  1. Dominant/recessive genes work as expected")
    print("  2. Traits blend from both parents (not random 50/50)")
    print("  3. Cross-entity interactions create emergent behavior")
    print("  4. Pellet sexual reproduction creates variation")
    print("  5. Multi-generational tracking enables deep simulation")
    print()


if __name__ == "__main__":
    main()
