"""
Demo script showcasing the new lethal combat traits.

This script demonstrates:
- All 10 new lethal combat traits
- Their stats and interaction effects
- Trait generation with lethal effects
- Integration with the trait system
"""

from src.models.expanded_traits import (
    LETHAL_COMBAT_TRAITS,
    BERSERKER_TRAIT,
    EXECUTIONER_TRAIT,
    BLOODTHIRSTY_TRAIT,
    BRUTAL_TRAIT,
    ASSASSIN_TRAIT,
    APEX_PREDATOR_TRAIT,
    RECKLESS_FURY_TRAIT,
    TOXIC_TRAIT,
    FRENZIED_TRAIT,
    VAMPIRIC_TRAIT
)
from src.models.trait_generator import TraitGenerator


def print_separator(char='=', length=80):
    """Print a separator line."""
    print(char * length)


def print_trait_details(trait):
    """Print detailed information about a trait."""
    print(f"\n🗡️  {trait.name}")
    print(f"   {trait.description}")
    print(f"   Category: {trait.trait_type.upper()} | Rarity: {trait.rarity.upper()} | Dominance: {trait.dominance}")
    print(f"   Stats: STR {trait.strength_modifier:.2f}x | SPD {trait.speed_modifier:.2f}x | DEF {trait.defense_modifier:.2f}x")
    
    if trait.interaction_effects:
        print(f"   Special Effects:")
        for key, value in trait.interaction_effects.items():
            print(f"      • {key}: {value}")


def demo_all_lethal_traits():
    """Demonstrate all lethal combat traits."""
    print_separator()
    print("LETHAL COMBAT TRAITS SHOWCASE")
    print_separator()
    print(f"\nTotal Lethal Traits: {len(LETHAL_COMBAT_TRAITS)}")
    print("These high-risk, high-reward traits enable dramatic kills and apex predators.\n")
    
    for trait in LETHAL_COMBAT_TRAITS:
        print_trait_details(trait)
    
    print_separator()


def demo_trait_generation():
    """Demonstrate generating random offensive traits with lethal effects."""
    print("\nGENERATING RANDOM LETHAL TRAITS")
    print_separator()
    
    generator = TraitGenerator(seed=42)
    
    print("\nGenerating 5 random offensive traits with lethal effects:\n")
    
    for i in range(5):
        trait = generator.generate_trait(category='offensive', rarity='rare')
        print(f"{i+1}. {trait.name}")
        print(f"   {trait.description}")
        print(f"   STR {trait.strength_modifier:.2f}x | SPD {trait.speed_modifier:.2f}x | DEF {trait.defense_modifier:.2f}x")
        
        # Highlight lethal effects
        lethal_effects = ['lifesteal', 'poison_on_hit', 'bleed_on_hit', 'execute_bonus', 
                         'multi_strike', 'armor_penetration']
        effects_found = [k for k in trait.interaction_effects.keys() if k in lethal_effects]
        
        if effects_found:
            print(f"   💀 Lethal Effects: {', '.join(effects_found)}")
        print()
    
    print_separator()


def demo_archetype_builds():
    """Show example trait combinations for different archetypes."""
    print("\nLETHAL ARCHETYPE BUILDS")
    print_separator()
    
    archetypes = [
        {
            'name': 'Glass Cannon Assassin',
            'traits': [ASSASSIN_TRAIT, RECKLESS_FURY_TRAIT],
            'description': 'Extreme offense, one-shot potential, extremely vulnerable'
        },
        {
            'name': 'Apex Predator Hunter',
            'traits': [APEX_PREDATOR_TRAIT, BLOODTHIRSTY_TRAIT],
            'description': 'Scales infinitely with kills, becomes unstoppable'
        },
        {
            'name': 'Toxic Attrition Fighter',
            'traits': [TOXIC_TRAIT, BRUTAL_TRAIT],
            'description': 'Poison + bleed stacking, wears down any opponent'
        },
        {
            'name': 'Vampiric Berserker',
            'traits': [VAMPIRIC_TRAIT, BERSERKER_TRAIT],
            'description': 'Sustain fighter that gets deadly when low HP'
        },
        {
            'name': 'Execution Squad',
            'traits': [EXECUTIONER_TRAIT, FRENZIED_TRAIT],
            'description': 'Rapid multi-strikes that finish wounded targets'
        }
    ]
    
    for archetype in archetypes:
        print(f"\n⚔️  {archetype['name']}")
        print(f"   {archetype['description']}\n")
        
        total_str = 1.0
        total_spd = 1.0
        total_def = 1.0
        
        print("   Traits:")
        for trait in archetype['traits']:
            print(f"      • {trait.name} ({trait.rarity})")
            total_str *= trait.strength_modifier
            total_spd *= trait.speed_modifier
            total_def *= trait.defense_modifier
        
        print(f"\n   Combined Multipliers:")
        print(f"      STR: {total_str:.2f}x | SPD: {total_spd:.2f}x | DEF: {total_def:.2f}x")
    
    print_separator()


def demo_trait_statistics():
    """Show statistics about the lethal traits."""
    print("\nLETHAL TRAITS STATISTICS")
    print_separator()
    
    # Rarity distribution
    rarity_count = {}
    for trait in LETHAL_COMBAT_TRAITS:
        rarity_count[trait.rarity] = rarity_count.get(trait.rarity, 0) + 1
    
    print("\nRarity Distribution:")
    for rarity, count in sorted(rarity_count.items()):
        percentage = (count / len(LETHAL_COMBAT_TRAITS)) * 100
        print(f"   {rarity.capitalize():12s}: {count:2d} ({percentage:5.1f}%)")
    
    # Dominance distribution
    dominance_count = {}
    for trait in LETHAL_COMBAT_TRAITS:
        dominance_count[trait.dominance] = dominance_count.get(trait.dominance, 0) + 1
    
    print("\nDominance Distribution:")
    for dominance, count in sorted(dominance_count.items()):
        percentage = (count / len(LETHAL_COMBAT_TRAITS)) * 100
        print(f"   {dominance.capitalize():12s}: {count:2d} ({percentage:5.1f}%)")
    
    # Average stat modifiers
    avg_str = sum(t.strength_modifier for t in LETHAL_COMBAT_TRAITS) / len(LETHAL_COMBAT_TRAITS)
    avg_spd = sum(t.speed_modifier for t in LETHAL_COMBAT_TRAITS) / len(LETHAL_COMBAT_TRAITS)
    avg_def = sum(t.defense_modifier for t in LETHAL_COMBAT_TRAITS) / len(LETHAL_COMBAT_TRAITS)
    
    print("\nAverage Stat Modifiers:")
    print(f"   Strength: {avg_str:.2f}x (offensive focus)")
    print(f"   Speed:    {avg_spd:.2f}x")
    print(f"   Defense:  {avg_def:.2f}x (glass cannon design)")
    
    # Glass cannon traits
    glass_cannons = [t for t in LETHAL_COMBAT_TRAITS if t.defense_modifier < 0.8]
    print(f"\nGlass Cannon Traits (Defense < 0.8x): {len(glass_cannons)}")
    for trait in glass_cannons:
        print(f"   • {trait.name}: {trait.defense_modifier:.2f}x defense")
    
    # High power traits
    high_power = [t for t in LETHAL_COMBAT_TRAITS if t.strength_modifier >= 1.5]
    print(f"\nHigh Power Traits (Strength ≥ 1.5x): {len(high_power)}")
    for trait in high_power:
        print(f"   • {trait.name}: {trait.strength_modifier:.2f}x strength")
    
    print_separator()


def main():
    """Run all demonstrations."""
    print("\n" + "="*80)
    print(" "*20 + "LETHAL COMBAT TRAITS DEMO")
    print("="*80)
    
    # Show all traits
    demo_all_lethal_traits()
    
    # Generate random traits
    demo_trait_generation()
    
    # Show archetype builds
    demo_archetype_builds()
    
    # Show statistics
    demo_trait_statistics()
    
    print("\n" + "="*80)
    print("Demo complete! Check LETHAL_COMBAT_TRAITS_DOCUMENTATION.md for full details.")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
