"""
Random Trait System Demo - Demonstrates the trait generation and analytics features.

This example shows how to:
1. Generate random traits
2. Integrate with breeding
3. Track trait spread
4. Export analytics
"""

from src.models.trait_generator import TraitGenerator
from src.models.trait_analytics import TraitAnalytics
from src.systems.trait_injection import TraitInjectionSystem, InjectionConfig
from src.systems.breeding import Breeding
from src.models.creature import Creature, CreatureType
from src.models.stats import Stats


def main():
    print("=" * 70)
    print("Random Trait Generation & Analytics System Demo")
    print("=" * 70)
    print()
    
    # 1. Create systems
    print("1. Setting up trait systems...")
    analytics = TraitAnalytics()
    
    config = InjectionConfig(
        breeding_injection_rate=0.3,  # Higher rate for demo
        cosmic_event_interval=3,
        injection_enabled=True
    )
    
    injection_system = TraitInjectionSystem(
        config=config,
        analytics=analytics,
        seed=42
    )
    
    breeding = Breeding(injection_system=injection_system)
    print("   ✓ Systems initialized")
    print()
    
    # 2. Generate some random traits
    print("2. Generating random traits...")
    generator = TraitGenerator(seed=42)
    
    for i in range(5):
        trait = generator.generate_creature_trait(generation=0)
        print(f"   • {trait.name} ({trait.rarity}) - {trait.trait_type}")
        print(f"     {trait.description[:60]}...")
    print()
    
    # 3. Create population and breed
    print("3. Creating initial population...")
    creature_type = CreatureType(
        name="Evolvon",
        base_stats=Stats(max_hp=100, attack=15, defense=12, speed=10)
    )
    
    population = []
    for i in range(4):
        creature = Creature(
            name=f"Gen0-{i+1}",
            creature_type=creature_type,
            level=5,
            mature=True
        )
        population.append(creature)
        
    print(f"   ✓ Created {len(population)} creatures")
    print()
    
    # 4. Simulate evolution over generations
    print("4. Simulating evolution (10 generations)...")
    for generation in range(1, 11):
        print(f"\n   Generation {generation}:")
        
        # Breeding
        new_offspring = []
        for i in range(0, len(population) - 1, 2):
            if i + 1 < len(population):
                offspring = breeding.breed(population[i], population[i + 1])
                if offspring:
                    offspring.name = f"Gen{generation}-{len(new_offspring) + 1}"
                    new_offspring.append(offspring)
                    
                    # Track traits
                    for trait in offspring.traits:
                        analytics.record_creature_trait(offspring.creature_id, trait.name)
        
        print(f"      Births: {len(new_offspring)}")
        
        # Cosmic events
        cosmic_traits = injection_system.check_cosmic_event(generation)
        if cosmic_traits:
            print(f"      🌟 Cosmic Event! {len(cosmic_traits)} new traits:")
            for trait in cosmic_traits:
                print(f"         • {trait.name}")
        
        # Population pressure
        pressure_trait = injection_system.evaluate_population_pressure(
            population_size=len(population),
            starvation_count=max(1, len(population) // 5),
            average_health=0.7,
            generation=generation
        )
        if pressure_trait:
            print(f"      🛡️ Pressure Response: {pressure_trait.name}")
        
        # Add offspring to population
        population.extend(new_offspring)
        
        # Limit population size
        if len(population) > 20:
            population = population[-20:]
    
    print()
    print("   ✓ Simulation complete")
    print()
    
    # 5. Display analytics
    print("5. Analytics Summary:")
    print("=" * 70)
    
    dashboard = analytics.get_dashboard_data()
    stats = dashboard['statistics']
    
    print(f"\n   Overall Statistics:")
    print(f"      Total Discoveries: {stats['total_discoveries']}")
    print(f"      Total Injections: {stats['total_injections']}")
    print(f"      Active Traits: {stats['active_traits']}")
    print(f"      Unique Traits Ever: {stats['unique_traits_ever']}")
    
    print(f"\n   Top 5 Most Successful Traits:")
    for i, trait_data in enumerate(dashboard['top_traits'][:5], 1):
        print(f"      {i}. {trait_data['name']}")
        print(f"         Carriers: {trait_data['carriers']} | " +
              f"Total: {trait_data['total_ever']} | " +
              f"Generations: {trait_data['generations']}")
    
    print(f"\n   Recent Trait Events:")
    for event in dashboard['recent_events'][:5]:
        icon = "🔍" if event['type'] == 'discovery' else "💉"
        print(f"      {icon} {event['type'].title()}: {event['trait']} (Gen {event['generation']})")
    
    # 6. Injection statistics
    print()
    print("6. Injection Statistics:")
    print("=" * 70)
    
    injection_stats = injection_system.get_injection_stats()
    print(f"\n   Total Injections: {injection_stats['total_injections']}")
    
    print(f"\n   By Reason:")
    for reason, count in injection_stats['by_reason'].items():
        print(f"      • {reason}: {count}")
    
    print(f"\n   By Category:")
    for category, count in injection_stats['by_category'].items():
        print(f"      • {category}: {count}")
    
    print(f"\n   By Rarity:")
    for rarity, count in injection_stats['by_rarity'].items():
        print(f"      • {rarity}: {count}")
    
    # 7. Export data
    print()
    print("7. Exporting data...")
    
    try:
        analytics.export_to_json('/tmp/trait_analytics.json')
        print("   ✓ Exported to /tmp/trait_analytics.json")
        
        analytics.export_to_csv('/tmp/trait_metrics.csv')
        print("   ✓ Exported to /tmp/trait_metrics.csv")
    except Exception as e:
        print(f"   ⚠ Export failed: {e}")
    
    print()
    print("=" * 70)
    print("Demo Complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()
