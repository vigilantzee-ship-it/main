"""
Demonstration of the Attention/Focus System.

Shows how creatures with different attention traits behave differently
and how they prioritize stimuli (combat, foraging, fleeing, exploring).
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.creature import Creature
from src.models.stats import Stats
from src.models.spatial import Vector2D
from src.systems.battle_spatial import SpatialBattle, BattleEventType
from src.models.ecosystem_traits import (
    PERSISTENT, DISTRACTIBLE, TUNNEL_VISION, OPPORTUNIST,
    FOCUSED, FICKLE, AGGRESSIVE, CAUTIOUS
)


def create_creature(name: str, traits: list, x: float, y: float) -> Creature:
    """Create a test creature."""
    base_stats = Stats(hp=100, max_hp=100, attack=20, defense=15, speed=25)
    creature = Creature(name=name, base_stats=base_stats, level=1)
    for trait in traits:
        creature.add_trait(trait)
    return creature


def main():
    """Run the attention system demonstration."""
    print("=" * 80)
    print("ATTENTION/FOCUS SYSTEM DEMONSTRATION")
    print("=" * 80)
    print()
    print("This demo shows how creatures with different attention traits behave:")
    print("  • Persistent Pete - Sticks with tasks longer")
    print("  • Distractible Dan - Easily switches focus")
    print("  • Focused Fran - Resistant to distractions (Tunnel Vision)")
    print("  • Opportunistic Oscar - Quick to adapt to new opportunities")
    print("  • Aggressive Alan - Prioritizes combat")
    print("  • Cautious Carol - Avoids danger, prioritizes safety")
    print()
    
    # Create creatures with different traits
    creatures = [
        create_creature("Persistent Pete", [PERSISTENT], 20, 20),
        create_creature("Distractible Dan", [DISTRACTIBLE], 80, 20),
        create_creature("Focused Fran", [TUNNEL_VISION], 20, 80),
        create_creature("Opportunistic Oscar", [OPPORTUNIST], 80, 80),
        create_creature("Aggressive Alan", [AGGRESSIVE], 50, 20),
        create_creature("Cautious Carol", [CAUTIOUS], 50, 80),
    ]
    
    # Create battle with many resources to give choices
    battle = SpatialBattle(
        creatures_or_team1=creatures,
        arena_width=100.0,
        arena_height=100.0,
        resource_spawn_rate=0.3,
        initial_resources=15
    )
    
    # Track attention changes
    attention_changes = []
    
    def on_event(event):
        """Track attention change events."""
        if event.event_type == BattleEventType.ATTENTION_CHANGE:
            attention_changes.append({
                'time': battle.current_time,
                'creature': event.actor.creature.name,
                'from': event.data['previous_focus'],
                'to': event.data['new_focus']
            })
    
    battle.add_event_callback(on_event)
    
    # Display initial attention states
    print("Initial Attention States:")
    print("-" * 80)
    for bc in battle.creatures:
        debug = bc.get_attention_debug_info(battle.current_time)
        print(f"{bc.creature.name:25s} Focus: {debug['current_focus']:15s} "
              f"Persist: {debug['persistence_modifier']:.2f}  "
              f"Distract: {debug['distractibility_modifier']:.2f}")
    print()
    
    # Run simulation
    print("Running simulation for 20 seconds...")
    print("-" * 80)
    
    updates = 0
    while battle.current_time < 20.0 and not battle.is_over:
        battle.update(0.1)
        updates += 1
        
        # Print status every 5 seconds
        if updates % 50 == 0:
            print(f"\n⏱ Time: {battle.current_time:.1f}s")
            for bc in battle.creatures:
                if bc.is_alive():
                    debug = bc.get_attention_debug_info(battle.current_time)
                    committed = "✓" if debug['is_committed'] else " "
                    print(f"  [{committed}] {bc.creature.name:25s} → {debug['current_focus']:15s} "
                          f"(duration: {debug['focus_duration']:.1f}s, "
                          f"hunger: {bc.creature.hunger}/{bc.creature.max_hunger})")
    
    # Summary
    print("\n" + "=" * 80)
    print("SIMULATION SUMMARY")
    print("=" * 80)
    print(f"Total simulation time: {battle.current_time:.1f}s")
    print(f"Creatures alive: {len([c for c in battle.creatures if c.is_alive()])}/{len(battle.creatures)}")
    print(f"Total attention changes: {len(attention_changes)}")
    print()
    
    # Count focus changes per creature
    focus_changes_per_creature = {}
    for change in attention_changes:
        name = change['creature']
        if name not in focus_changes_per_creature:
            focus_changes_per_creature[name] = 0
        focus_changes_per_creature[name] += 1
    
    print("Attention Changes per Creature:")
    print("-" * 80)
    for name in sorted(focus_changes_per_creature.keys()):
        count = focus_changes_per_creature[name]
        print(f"  {name:25s} {count:3d} changes")
    print()
    
    # Show some example attention changes
    print("Sample Attention Changes:")
    print("-" * 80)
    for change in attention_changes[:10]:
        print(f"  {change['time']:5.1f}s - {change['creature']:25s} "
              f"{change['from']:12s} → {change['to']:12s}")
    if len(attention_changes) > 10:
        print(f"  ... and {len(attention_changes) - 10} more")
    print()
    
    # Final attention states
    print("Final Attention States:")
    print("-" * 80)
    for bc in battle.creatures:
        if bc.is_alive():
            debug = bc.get_attention_debug_info(battle.current_time)
            committed = "✓" if debug['is_committed'] else " "
            print(f"[{committed}] {bc.creature.name:25s} Focus: {debug['current_focus']:15s} "
                  f"Duration: {debug['focus_duration']:.1f}s  "
                  f"HP: {bc.creature.stats.hp}/{bc.creature.stats.max_hp}  "
                  f"Hunger: {bc.creature.hunger}/{bc.creature.max_hunger}")
    
    print("\n" + "=" * 80)
    print("Key Observations:")
    print("  • Persistent creatures change focus less frequently")
    print("  • Distractible creatures are more responsive to new stimuli")
    print("  • Tunnel vision creatures commit deeply to their current task")
    print("  • Opportunists adapt quickly to changing conditions")
    print("=" * 80)


if __name__ == "__main__":
    main()
