#!/usr/bin/env python3
"""
Demonstration script showing that agents properly engage in combat.
This addresses the issue where agents would circle without attacking.
"""

from src.models.creature import Creature, CreatureType
from src.models.stats import Stats, StatGrowth
from src.models.ability import create_ability
from src.systems.battle_spatial import SpatialBattle, BattleEventType
from src.models.spatial import Vector2D


def main():
    """Demonstrate combat engagement fix."""
    print("=" * 70)
    print("COMBAT ENGAGEMENT FIX DEMONSTRATION")
    print("=" * 70)
    print("\nThis demo shows that agents now properly engage in combat")
    print("instead of circling around each other indefinitely.\n")
    
    # Create two aggressive warriors
    warrior_type = CreatureType(
        name="Warrior",
        base_stats=Stats(max_hp=100, attack=20, defense=10, speed=15),
        stat_growth=StatGrowth(),
        type_tags=["fighter"]
    )
    
    warrior1 = Creature(name="RedWarrior", creature_type=warrior_type, level=5)
    warrior1.add_ability(create_ability('tackle'))
    
    warrior2 = Creature(name="BlueWarrior", creature_type=warrior_type, level=5)
    warrior2.add_ability(create_ability('tackle'))
    
    print(f"Created: {warrior1.name} (HP: {warrior1.stats.hp})")
    print(f"Created: {warrior2.name} (HP: {warrior2.stats.hp})\n")
    
    # Create small arena for close combat
    battle = SpatialBattle(
        [warrior1, warrior2],
        arena_width=40.0,
        arena_height=40.0,
        random_seed=42
    )
    
    # Track key events
    attack_count = 0
    damage_count = 0
    first_attack_time = None
    total_damage = {warrior1.name: 0, warrior2.name: 0}
    
    def event_callback(event):
        nonlocal attack_count, damage_count, first_attack_time
        
        if event.event_type == BattleEventType.ABILITY_USE:
            attack_count += 1
            if first_attack_time is None:
                first_attack_time = battle.current_time
            print(f"[{battle.current_time:.1f}s] {event.actor.creature.name} uses {event.ability.name}!")
        
        elif event.event_type == BattleEventType.DAMAGE_DEALT:
            damage_count += 1
            total_damage[event.target.creature.name] += event.value
            print(f"        → {event.target.creature.name} takes {event.value} damage! " +
                  f"(HP: {event.target.creature.stats.hp}/{event.target.creature.stats.max_hp})")
        
        elif event.event_type == BattleEventType.CREATURE_DEATH:
            print(f"\n[{battle.current_time:.1f}s] ⚔️  {event.target.creature.name} has been defeated!")
    
    battle.add_event_callback(event_callback)
    
    print("Starting battle simulation...")
    print("-" * 70 + "\n")
    
    # Get initial positions
    bc1 = battle.creatures[0]
    bc2 = battle.creatures[1]
    initial_distance = bc1.spatial.distance_to(bc2.spatial)
    print(f"Initial distance: {initial_distance:.1f} units\n")
    
    # Simulate battle
    battle.simulate(duration=15.0, time_step=0.1)
    
    # Print results
    print("\n" + "=" * 70)
    print("BATTLE RESULTS")
    print("=" * 70)
    
    final_distance = bc1.spatial.distance_to(bc2.spatial)
    
    print(f"\nBattle Duration: {battle.current_time:.1f}s")
    print(f"Initial Distance: {initial_distance:.1f} units")
    print(f"Final Distance: {final_distance:.1f} units")
    print(f"\nTotal Attacks: {attack_count}")
    print(f"Total Damage Events: {damage_count}")
    
    if first_attack_time is not None:
        print(f"First Attack Time: {first_attack_time:.1f}s")
    
    print(f"\nDamage Taken:")
    for name, damage in total_damage.items():
        creature = warrior1 if name == warrior1.name else warrior2
        print(f"  {name}: {damage} damage (HP: {creature.stats.hp}/{creature.stats.max_hp})")
    
    # Analyze results
    print("\n" + "=" * 70)
    print("ANALYSIS")
    print("=" * 70)
    
    if attack_count > 0:
        print("✅ SUCCESS: Agents engaged in combat!")
        print(f"   - {attack_count} attacks occurred")
        if first_attack_time and first_attack_time < 5.0:
            print(f"   - First attack within {first_attack_time:.1f}s (good responsiveness)")
        print(f"   - Agents closed distance from {initial_distance:.1f} to {final_distance:.1f} units")
    else:
        print("❌ ISSUE: No attacks occurred - agents may still be circling")
    
    print("\nKey Improvements:")
    print("  1. Combat engagement state prevents separation when fighting")
    print("  2. Melee attack range (4.0) > separation threshold (2.5)")
    print("  3. Reduced separation forces when attacking target")
    print("\nThese changes ensure agents commit to combat instead of circling.")
    print("=" * 70)


if __name__ == "__main__":
    main()
