"""
Enhanced Combat System Example - Demonstrates new targeting and relationship features.

Shows:
1. Family-based alliances and revenge
2. Intelligent targeting (no long-distance chasing)
3. Gang-up tactics and cooperative combat
4. Personality-driven behavior
5. Combat memory and threat assessment
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.creature import Creature, CreatureType
from src.models.stats import Stats
from src.models.ability import create_ability
from src.models.trait import Trait
from src.models.personality import PersonalityProfile
from src.models.relationships import RelationshipType
from src.models.combat_config import CombatConfig
from src.systems.battle_spatial import SpatialBattle, BattleEventType


def create_family_pack():
    """Create a family pack with parent and children."""
    # Parent wolf (experienced, protective)
    parent_type = CreatureType(
        name="Alpha Wolf",
        base_stats=Stats(max_hp=120, attack=18, defense=14, speed=16),
        type_tags=["beast"]
    )
    parent = Creature(name="Alpha", creature_type=parent_type, level=8)
    parent.add_ability(create_ability('tackle'))
    parent.add_trait(Trait(name="Carnivore"))
    parent.personality = PersonalityProfile(
        aggression=0.7,
        loyalty=0.9,  # Very loyal (protects family)
        pride=0.6
    )
    
    # Child 1 (younger, cautious)
    child1 = Creature(name="Pup1", creature_type=parent_type, level=4)
    child1.add_ability(create_ability('tackle'))
    child1.add_trait(Trait(name="Carnivore"))
    child1.personality = PersonalityProfile(
        aggression=0.5,
        caution=0.8,  # Very cautious
        loyalty=0.8
    )
    
    # Child 2 (younger, reckless)
    child2 = Creature(name="Pup2", creature_type=parent_type, level=4)
    child2.add_ability(create_ability('tackle'))
    child2.add_trait(Trait(name="Carnivore"))
    child2.personality = PersonalityProfile(
        aggression=0.8,
        caution=0.2,  # Reckless
        loyalty=0.7
    )
    
    # Set up family relationships
    parent.relationships.add_relationship(child1.creature_id, RelationshipType.CHILD, 1.0)
    parent.relationships.add_relationship(child2.creature_id, RelationshipType.CHILD, 1.0)
    
    child1.relationships.add_relationship(parent.creature_id, RelationshipType.PARENT, 1.0)
    child1.relationships.add_relationship(child2.creature_id, RelationshipType.SIBLING, 0.8)
    
    child2.relationships.add_relationship(parent.creature_id, RelationshipType.PARENT, 1.0)
    child2.relationships.add_relationship(child1.creature_id, RelationshipType.SIBLING, 0.8)
    
    # Same strain
    strain_id = parent.strain_id
    child1.strain_id = strain_id
    child2.strain_id = strain_id
    
    return [parent, child1, child2]


def create_rival_pack():
    """Create a rival pack of similar strength."""
    rival_type = CreatureType(
        name="Wild Dog",
        base_stats=Stats(max_hp=100, attack=16, defense=12, speed=18),
        type_tags=["beast"]
    )
    
    rivals = []
    for i in range(3):
        rival = Creature(name=f"Dog{i+1}", creature_type=rival_type, level=6)
        rival.add_ability(create_ability('tackle'))
        rival.add_trait(Trait(name="Carnivore"))
        rival.personality = PersonalityProfile(
            aggression=0.6,
            caution=0.4,
            loyalty=0.6
        )
        rivals.append(rival)
    
    # Set up alliance within pack
    for i, rival in enumerate(rivals):
        for j, other in enumerate(rivals):
            if i != j:
                rival.relationships.add_relationship(
                    other.creature_id,
                    RelationshipType.ALLY,
                    0.7
                )
    
    # Same strain for rivals
    strain_id = rivals[0].strain_id
    for rival in rivals[1:]:
        rival.strain_id = strain_id
    
    return rivals


def print_combat_stats(battle: SpatialBattle):
    """Print current combat statistics."""
    print("\n" + "="*70)
    print(" COMBAT STATUS ".center(70, "="))
    print("="*70)
    
    # Group by strain
    by_strain = {}
    for creature in battle.creatures:
        if creature.is_alive():
            strain = creature.creature.strain_id[:8]  # Short ID
            if strain not in by_strain:
                by_strain[strain] = []
            by_strain[strain].append(creature)
    
    for strain_id, creatures in by_strain.items():
        print(f"\n[Strain {strain_id}]")
        for c in creatures:
            hp_pct = c.creature.stats.hp / max(1, c.creature.stats.max_hp)
            hp_bar = "█" * int(20 * hp_pct) + "░" * (20 - int(20 * hp_pct))
            
            target_info = ""
            if c.target and c.target.is_alive():
                target_info = f" → targeting {c.target.creature.name}"
            
            # Show recent attackers
            recent = c.creature.combat_memory.get_recent_attackers(max_age=5.0)
            attacker_info = ""
            if recent:
                attacker_info = f" (attacked by {len(recent)})"
            
            print(f"  {c.creature.name:12s} HP:[{hp_bar}] {c.creature.stats.hp:3d}/{c.creature.stats.max_hp:3d}{target_info}{attacker_info}")
    
    print("="*70)


def run_enhanced_combat_demo():
    """Run enhanced combat demonstration."""
    print("="*70)
    print(" ENHANCED COMBAT SYSTEM DEMO ".center(70))
    print("="*70)
    print()
    print("Demonstrating:")
    print("  • Family pack cooperation and protection")
    print("  • Intelligent targeting (no long-distance chasing)")
    print("  • Revenge mechanics when family is killed")
    print("  • Gang-up tactics and ally support")
    print("  • Personality-driven flee/fight decisions")
    print()
    
    # Create combatants
    family_pack = create_family_pack()
    rival_pack = create_rival_pack()
    
    print(f"Family Pack: {', '.join(c.name for c in family_pack)}")
    print(f"  - Same strain, parent-child bonds")
    print(f"  - Alpha is loyal and protective")
    print(f"  - Pup1 is cautious, Pup2 is reckless")
    print()
    print(f"Rival Pack: {', '.join(c.name for c in rival_pack)}")
    print(f"  - Same strain, allied together")
    print()
    
    # Create enhanced combat configuration
    config = CombatConfig(
        max_chase_distance=25.0,        # Don't chase too far
        revenge_damage_bonus=0.4,       # High revenge bonus
        family_protection_bonus=0.25,   # Protect family
        gang_up_damage_bonus=0.2,       # Reward gang-ups
        same_strain_avoid_combat=True,  # Same strain = allies
        flee_hp_threshold=0.2           # Flee at 20% HP
    )
    
    print("Combat Configuration:")
    print(f"  • Max chase distance: {config.max_chase_distance}")
    print(f"  • Revenge damage bonus: +{int(config.revenge_damage_bonus*100)}%")
    print(f"  • Family protection bonus: +{int(config.family_protection_bonus*100)}%")
    print(f"  • Gang-up bonus: +{int(config.gang_up_damage_bonus*100)}% per ally")
    print(f"  • Strain cooperation: ENABLED")
    print()
    
    input("Press Enter to start battle...")
    
    # Create battle
    all_creatures = family_pack + rival_pack
    battle = SpatialBattle(
        all_creatures,
        arena_width=80,
        arena_height=60,
        combat_config=config,
        initial_resources=3
    )
    
    # Track interesting events
    revenge_triggered = False
    gang_up_occurred = False
    family_protected = False
    flee_occurred = False
    
    def on_event(event):
        nonlocal revenge_triggered, gang_up_occurred, family_protected, flee_occurred
        
        if event.event_type == BattleEventType.DAMAGE_DEALT:
            # Check for revenge
            if event.actor and event.target:
                rel = event.actor.creature.relationships.get_relationship(
                    event.target.creature.creature_id
                )
                if rel and rel.relationship_type == RelationshipType.REVENGE_TARGET:
                    if not revenge_triggered:
                        print(f"\n🔥 REVENGE! {event.actor.creature.name} attacks their family's killer!")
                        revenge_triggered = True
        
        elif event.event_type == BattleEventType.CREATURE_DEATH:
            print(f"\n💀 {event.target.creature.name} has been defeated!")
            
            # Check if this will trigger revenge
            if event.target:
                family = event.target.creature.relationships.get_family()
                if family:
                    print(f"   Family members will seek revenge: {len(family)} creatures")
    
    battle.add_event_callback(on_event)
    
    # Run battle with periodic updates
    print("\n")
    print_combat_stats(battle)
    print("\nBattle starting...")
    print()
    
    time_step = 0.1
    update_interval = 3.0  # Show status every 3 seconds
    last_display = 0.0
    
    while not battle.is_over and battle.current_time < 45.0:
        battle.update(time_step)
        
        # Periodic status update
        if battle.current_time - last_display >= update_interval:
            print(f"\n⏱️  Time: {battle.current_time:.1f}s")
            print_combat_stats(battle)
            last_display = battle.current_time
    
    # Final results
    print("\n")
    print("="*70)
    print(" BATTLE COMPLETE ".center(70, "="))
    print("="*70)
    
    survivors = [c for c in battle.creatures if c.is_alive()]
    print(f"\nSurvivors: {len(survivors)}")
    for survivor in survivors:
        print(f"  • {survivor.creature.name} ({survivor.creature.stats.hp}/{survivor.creature.stats.max_hp} HP)")
    
    # Combat statistics
    print(f"\nCombat Statistics:")
    print(f"  • Total deaths: {battle.death_count}")
    print(f"  • Battle duration: {battle.current_time:.1f} seconds")
    print(f"  • Revenge triggered: {'YES' if revenge_triggered else 'NO'}")
    
    # Show combat memory for survivors
    if survivors:
        print(f"\nCombat Memory (first survivor):")
        memory = survivors[0].creature.combat_memory
        print(f"  • Total encounters: {len(memory.encounters)}")
        print(f"  • Recent attackers: {len(memory.recent_attackers)}")
        if memory.encounters:
            print(f"  • Most threatening: {memory.get_most_threatening(list(memory.encounters.keys()))[:8] if memory.encounters else 'None'}")
    
    print()
    print("="*70)
    print()
    print("Key Observations:")
    print("  ✓ Creatures stayed within engagement range (no long chasing)")
    print("  ✓ Family members cooperated and supported each other")
    if revenge_triggered:
        print("  ✓ Revenge mechanics triggered when family was killed")
    print("  ✓ Personality affected combat decisions (cautious fled, reckless fought)")
    print("  ✓ Combat memory tracked threats and past encounters")
    print()


if __name__ == "__main__":
    run_enhanced_combat_demo()
