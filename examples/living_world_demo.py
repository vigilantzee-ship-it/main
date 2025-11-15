"""
Living World Demo - Showcases creature histories, skills, personalities, and relationships.

This demo creates a battle simulation where creatures develop unique stories through:
- Individual life histories tracking every significant event
- Skills that improve through use
- Personalities that affect behavior
- Relationships that create rivalries and alliances
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.creature import Creature, CreatureType
from src.models.stats import Stats, StatGrowth
from src.models.ability import create_ability
from src.models.ecosystem_traits import AGGRESSIVE, CAUTIOUS, FORAGER
from src.systems.living_world import LivingWorldBattleEnhancer
import random


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def create_warrior(name: str, level: int = 5) -> Creature:
    """Create a warrior creature."""
    base_stats = Stats(
        max_hp=100 + level * 10,
        attack=15 + level * 2,
        defense=12 + level * 2,
        speed=10 + level
    )
    
    creature_type = CreatureType(
        name="Warrior",
        base_stats=base_stats,
        type_tags=["normal"],
        stat_growth=StatGrowth(hp_growth=10.0, attack_growth=2.0)
    )
    
    creature = Creature(
        name=name,
        creature_type=creature_type,
        level=level,
        traits=[AGGRESSIVE]
    )
    
    creature.add_ability(create_ability('tackle'))
    creature.add_ability(create_ability('slash'))
    
    return creature


def simulate_attack(attacker: Creature, defender: Creature, enhancer: LivingWorldBattleEnhancer):
    """Simulate a single attack."""
    # Calculate base damage
    ability = attacker.abilities[0]
    base_damage = ability.calculate_damage(attacker.stats.attack, defender.stats.defense)
    
    # Check for critical hit
    base_crit_chance = 6.25  # 6.25% base
    crit_modifier = enhancer.calculate_critical_chance_modifier(attacker)
    crit_chance = base_crit_chance + crit_modifier
    is_critical = random.random() * 100 < crit_chance
    
    if is_critical:
        base_damage *= 1.5
    
    # Apply all modifiers
    final_damage = enhancer.calculate_damage_modifier(
        attacker, defender, base_damage, is_critical
    )
    
    # Record the attack
    enhancer.on_attack_made(attacker, defender, final_damage, is_critical, hit=True)
    
    # Apply damage
    actual_damage = defender.stats.take_damage(final_damage)
    
    return actual_damage, is_critical


def simulate_battle(creature1: Creature, creature2: Creature, max_rounds: int = 20) -> Creature:
    """Simulate a simple 1v1 battle."""
    enhancer = LivingWorldBattleEnhancer(None)
    enhancer.on_battle_start([creature1, creature2])
    
    round_num = 0
    while creature1.is_alive() and creature2.is_alive() and round_num < max_rounds:
        round_num += 1
        
        # Determine who attacks first based on speed
        if creature1.stats.speed >= creature2.stats.speed:
            first, second = creature1, creature2
        else:
            first, second = creature2, creature1
        
        # First creature attacks
        if first.is_alive() and second.is_alive():
            damage, was_crit = simulate_attack(first, second, enhancer)
            crit_str = " (CRITICAL!)" if was_crit else ""
            print(f"Round {round_num}: {first.name} attacks {second.name} for {damage:.1f} damage{crit_str}")
            print(f"  -> {second.name} HP: {second.stats.hp:.1f}/{second.stats.max_hp}")
            
            if not second.is_alive():
                print(f"  -> {second.name} has been defeated!")
                enhancer.on_creature_killed(first, second)
                break
        
        # Second creature counter-attacks
        if second.is_alive() and first.is_alive():
            damage, was_crit = simulate_attack(second, first, enhancer)
            crit_str = " (CRITICAL!)" if was_crit else ""
            print(f"         {second.name} counter-attacks {first.name} for {damage:.1f} damage{crit_str}")
            print(f"  -> {first.name} HP: {first.stats.hp:.1f}/{first.stats.max_hp}")
            
            if not first.is_alive():
                print(f"  -> {first.name} has been defeated!")
                enhancer.on_creature_killed(second, first)
                break
    
    # Return winner
    if creature1.is_alive():
        enhancer.on_battle_end([creature1])
        return creature1
    elif creature2.is_alive():
        enhancer.on_battle_end([creature2])
        return creature2
    else:
        return None


def display_creature_info(creature: Creature):
    """Display detailed creature information."""
    print(f"\n{creature.name} - Level {creature.level}")
    print(f"{'─'*70}")
    
    # Stats
    print(f"HP: {creature.stats.hp:.0f}/{creature.stats.max_hp}")
    print(f"Attack: {creature.stats.attack}  Defense: {creature.stats.defense}  Speed: {creature.stats.speed}")
    
    # Personality
    print(f"\nPersonality: {creature.personality.get_description()}")
    print(f"Combat Style: {creature.personality.get_combat_style()}")
    
    # Skills
    print(f"\nTop Skills:")
    top_skills = creature.skills.get_highest_skills(3)
    if top_skills:
        for skill_type, level in top_skills:
            skill = creature.skills.get_skill(skill_type)
            print(f"  - {skill.config.name}: Level {level} ({skill.get_proficiency().value})")
    else:
        print("  - No skills developed yet")
    
    # Battle History
    history = creature.history
    print(f"\nBattle Record:")
    print(f"  Battles: {history.battles_fought} (Won: {history.battles_won}, Win Rate: {history.get_win_rate()*100:.1f}%)")
    print(f"  Kills: {len(history.kills)}")
    print(f"  Deaths: {history.deaths}")
    if history.deaths > 0:
        print(f"  K/D Ratio: {history.get_kill_death_ratio():.2f}")
    print(f"  Damage Dealt: {history.total_damage_dealt:.1f}")
    print(f"  Damage Taken: {history.total_damage_received:.1f}")
    
    # Achievements
    if history.achievements:
        print(f"\nAchievements:")
        for achievement in history.achievements:
            rarity_stars = "⭐" * int(achievement.rarity * 5)
            print(f"  {rarity_stars} {achievement.name}: {achievement.description}")
    
    # Titles
    if history.titles:
        print(f"\nTitles: {', '.join(history.titles)}")
    
    # Legendary Moments
    if history.legendary_moments:
        print(f"\nLegendary Moments:")
        for event in history.legendary_moments[:3]:  # Show top 3
            print(f"  - {event.description}")
    
    # Relationships
    allies = creature.relationships.get_allies()
    enemies = creature.relationships.get_enemies()
    revenge_targets = creature.relationships.get_revenge_targets()
    
    if allies or enemies or revenge_targets:
        print(f"\nRelationships:")
        if allies:
            print(f"  Allies: {len(allies)}")
        if enemies:
            print(f"  Rivals: {len(enemies)}")
        if revenge_targets:
            print(f"  Revenge Targets: {len(revenge_targets)}")


def main():
    """Run the living world demo."""
    print_section("Living World Demo - Creature Stories & Histories")
    
    print("Creating creatures with unique personalities and traits...")
    
    # Create some warriors
    hero = create_warrior("Aragorn", level=5)
    rival = create_warrior("Sauron", level=5)
    warrior = create_warrior("Gimli", level=4)
    
    print(f"\nCreated {hero.name}: {hero.personality.get_description()}")
    print(f"Created {rival.name}: {rival.personality.get_description()}")
    print(f"Created {warrior.name}: {warrior.personality.get_description()}")
    
    # Display initial info
    print_section("Battle 1: Hero vs Rival")
    print("Initial Status:")
    display_creature_info(hero)
    display_creature_info(rival)
    
    # Simulate first battle
    print("\n--- Battle Begins ---")
    winner1 = simulate_battle(hero, rival, max_rounds=20)
    
    if winner1:
        print(f"\n🏆 Winner: {winner1.name}")
        print_section("After Battle 1")
        display_creature_info(winner1)
        
        # Check if loser should want revenge
        loser1 = rival if winner1 == hero else hero
        if loser1.is_alive():  # In case they survived
            print(f"\n{loser1.name} has developed a rivalry with {winner1.name}!")
            loser1.relationships.record_lost_to(winner1.creature_id)
    
    # Create a new rivalry scenario
    print_section("Battle 2: Winner vs New Challenger")
    
    if winner1:
        winner1.stats.hp = winner1.stats.max_hp  # Restore HP
        
        print("Initial Status:")
        display_creature_info(winner1)
        display_creature_info(warrior)
        
        print("\n--- Battle Begins ---")
        winner2 = simulate_battle(winner1, warrior, max_rounds=20)
        
        if winner2:
            print(f"\n🏆 Winner: {winner2.name}")
            print_section("Final Champion Status")
            display_creature_info(winner2)
    
    # Show event timeline
    print_section("Event Timeline for Champion")
    if winner2:
        recent_events = winner2.history.get_recent_events(10)
        print(f"\nRecent events in {winner2.name}'s life:")
        for i, event in enumerate(recent_events, 1):
            print(f"{i}. {event.event_type.value}: {event.description}")
    
    # Summary
    print_section("Demo Summary")
    print("This demo showcased:")
    print("✓ Unique personalities affecting combat style")
    print("✓ Skills developing through combat experience")
    print("✓ Comprehensive battle history tracking")
    print("✓ Achievement system for exceptional moments")
    print("✓ Relationship formation (rivalries)")
    print("✓ Individual life event timelines")
    print("\nEach creature now has a unique story and legacy!")
    
    print(f"\n{'='*70}")
    print("Demo complete. Every creature's journey is unique.")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
