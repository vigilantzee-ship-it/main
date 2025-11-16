"""
Cooperative Behavior Demo - Shows social traits and cooperative behaviors in action.

This demo creates creatures with different social traits and demonstrates:
- Food sharing between family and allies
- Joining allies in fights
- Group combat bonuses
- Relationship metric tracking
"""

from src.models.creature import Creature
from src.models.relationships import RelationshipType
from src.models.relationship_metrics import (
    CooperativeBehaviorSystem,
    DecisionContext,
    AgentTraits,
    create_family_bond,
    create_pack_bond
)
from src.systems.living_world import LivingWorldBattleEnhancer


def create_creature_with_traits(name: str, altruism: float, dominance: float, cooperation: float):
    """Create a creature with specific social traits."""
    creature = Creature(name=name)
    creature.social_traits.altruism = altruism
    creature.social_traits.dominance = dominance
    creature.social_traits.cooperation = cooperation
    creature.social_traits.protectiveness = 0.7
    creature.social_traits.independence = 0.3
    creature.hunger = 80
    creature.social_state.hunger_level = 0.8
    creature.social_state.health_level = 0.9
    return creature


def demonstrate_food_sharing():
    """Demonstrate food sharing behavior."""
    print("=" * 60)
    print("FOOD SHARING DEMONSTRATION")
    print("=" * 60)
    
    # Create altruistic parent and hungry child
    parent = create_creature_with_traits("Caring Parent", altruism=0.9, dominance=0.6, cooperation=0.8)
    child = create_creature_with_traits("Hungry Child", altruism=0.5, dominance=0.3, cooperation=0.6)
    child.hunger = 20
    child.social_state.hunger_level = 0.2
    
    # Create family bond
    parent_rel = parent.relationships.add_relationship(
        child.creature_id,
        RelationshipType.CHILD,
        strength=1.0
    )
    parent_rel.metrics = create_family_bond(parent.creature_id, child.creature_id)
    
    # Also create selfish stranger
    stranger = create_creature_with_traits("Selfish Stranger", altruism=0.2, dominance=0.5, cooperation=0.3)
    stranger.hunger = 20
    stranger.social_state.hunger_level = 0.2
    
    # Create weak relationship with stranger
    stranger_rel = parent.relationships.add_relationship(
        stranger.creature_id,
        RelationshipType.ALLY,
        strength=0.3
    )
    stranger_rel.metrics = create_pack_bond(parent.creature_id, stranger.creature_id)
    
    # Test food sharing
    coop_system = CooperativeBehaviorSystem()
    
    print(f"\n{parent.name} has {parent.hunger} hunger")
    print(f"{child.name} has {child.hunger} hunger (STARVING)")
    print(f"{stranger.name} has {stranger.hunger} hunger (STARVING)")
    
    # Try sharing with child (family)
    print(f"\n{parent.name}'s social traits: {parent.social_traits.get_description()}")
    context_child = DecisionContext(
        actor_id=parent.creature_id,
        target_id=child.creature_id,
        actor_traits=parent.social_traits,
        target_traits=child.social_traits,
        metrics=parent_rel.metrics,
        actor_state=parent.social_state,
        target_state=child.social_state
    )
    
    should_share_child, amount_child = coop_system.evaluate_food_sharing(context_child, parent.hunger)
    print(f"\nShould share with {child.name} (family)? {should_share_child}")
    if should_share_child:
        print(f"  → Will share {amount_child:.1f} food")
        print(f"  → Cooperation score: {parent_rel.metrics.get_cooperation_score():.2f}")
    
    # Try sharing with stranger
    context_stranger = DecisionContext(
        actor_id=parent.creature_id,
        target_id=stranger.creature_id,
        actor_traits=parent.social_traits,
        target_traits=stranger.social_traits,
        metrics=stranger_rel.metrics,
        actor_state=parent.social_state,
        target_state=stranger.social_state
    )
    
    should_share_stranger, amount_stranger = coop_system.evaluate_food_sharing(context_stranger, parent.hunger)
    print(f"\nShould share with {stranger.name} (stranger)? {should_share_stranger}")
    if should_share_stranger:
        print(f"  → Will share {amount_stranger:.1f} food")
    else:
        print(f"  → Not sharing (low cooperation score: {stranger_rel.metrics.get_cooperation_score():.2f})")


def demonstrate_fight_joining():
    """Demonstrate joining allies in fights."""
    print("\n\n" + "=" * 60)
    print("FIGHT JOINING DEMONSTRATION")
    print("=" * 60)
    
    # Create protective family member
    protector = create_creature_with_traits("Protective Sibling", altruism=0.7, dominance=0.7, cooperation=0.9)
    protector.social_traits.protectiveness = 0.9
    
    # Create sibling in danger
    sibling = create_creature_with_traits("Sibling in Danger", altruism=0.5, dominance=0.4, cooperation=0.6)
    sibling.social_state.in_combat = True
    sibling.social_state.threatened = True
    sibling.social_state.health_level = 0.4
    
    # Create family bond
    sibling_rel = protector.relationships.add_relationship(
        sibling.creature_id,
        RelationshipType.SIBLING,
        strength=1.0
    )
    sibling_rel.metrics = create_family_bond(protector.creature_id, sibling.creature_id)
    
    # Also create independent creature
    loner = create_creature_with_traits("Independent Loner", altruism=0.3, dominance=0.6, cooperation=0.2)
    loner.social_traits.independence = 0.9
    
    loner_rel = loner.relationships.add_relationship(
        sibling.creature_id,
        RelationshipType.ALLY,
        strength=0.5
    )
    loner_rel.metrics = create_pack_bond(loner.creature_id, sibling.creature_id)
    
    # Test fight joining
    coop_system = CooperativeBehaviorSystem()
    
    print(f"\n{sibling.name} is in a dangerous fight!")
    print(f"  Health: {sibling.social_state.health_level * 100:.0f}%")
    
    # Protector evaluates joining
    print(f"\n{protector.name}'s traits: {protector.social_traits.get_description()}")
    context_protector = DecisionContext(
        actor_id=protector.creature_id,
        target_id=sibling.creature_id,
        actor_traits=protector.social_traits,
        target_traits=sibling.social_traits,
        metrics=sibling_rel.metrics,
        actor_state=protector.social_state,
        target_state=sibling.social_state
    )
    
    should_join_p, commitment_p = coop_system.evaluate_join_fight(context_protector, threat_level=0.6)
    print(f"\nWill {protector.name} join the fight? {should_join_p}")
    if should_join_p:
        print(f"  → Commitment level: {commitment_p:.2f} (HIGH)")
        print(f"  → Reason: High protectiveness + family bond")
    
    # Loner evaluates joining
    print(f"\n{loner.name}'s traits: {loner.social_traits.get_description()}")
    context_loner = DecisionContext(
        actor_id=loner.creature_id,
        target_id=sibling.creature_id,
        actor_traits=loner.social_traits,
        target_traits=sibling.social_traits,
        metrics=loner_rel.metrics,
        actor_state=loner.social_state,
        target_state=sibling.social_state
    )
    
    should_join_l, commitment_l = coop_system.evaluate_join_fight(context_loner, threat_level=0.6)
    print(f"\nWill {loner.name} join the fight? {should_join_l}")
    if not should_join_l:
        print(f"  → Refused: High independence ({loner.social_traits.independence:.1f}) + weak bond")


def demonstrate_group_combat():
    """Demonstrate group combat bonuses."""
    print("\n\n" + "=" * 60)
    print("GROUP COMBAT BONUS DEMONSTRATION")
    print("=" * 60)
    
    # Create cooperative fighter
    team_fighter = create_creature_with_traits("Team Fighter", altruism=0.7, dominance=0.5, cooperation=0.9)
    
    # Create solo fighter
    solo_fighter = create_creature_with_traits("Solo Fighter", altruism=0.3, dominance=0.7, cooperation=0.2)
    solo_fighter.social_traits.independence = 0.9
    
    coop_system = CooperativeBehaviorSystem()
    
    print(f"\n{team_fighter.name} traits: {team_fighter.social_traits.get_description()}")
    print(f"  Cooperation: {team_fighter.social_traits.cooperation:.2f}")
    
    print(f"\n{solo_fighter.name} traits: {solo_fighter.social_traits.get_description()}")
    print(f"  Cooperation: {solo_fighter.social_traits.cooperation:.2f}")
    print(f"  Independence: {solo_fighter.social_traits.independence:.2f}")
    
    # Test with different group sizes
    scenarios = [
        (0, 0, "Fighting alone"),
        (2, 0, "With 2 allies"),
        (3, 1, "With 3 allies (1 family)"),
        (5, 2, "With 5 allies (2 family)")
    ]
    
    print(f"\n{team_fighter.name}'s bonuses:")
    for allies, family, desc in scenarios:
        bonus = coop_system.calculate_group_combat_bonus(
            team_fighter.social_traits,
            allies,
            family
        )
        print(f"  {desc}: {bonus:.2%} damage ({(bonus - 1) * 100:+.1f}%)")
    
    print(f"\n{solo_fighter.name}'s bonuses:")
    for allies, family, desc in scenarios:
        bonus = coop_system.calculate_group_combat_bonus(
            solo_fighter.social_traits,
            allies,
            family
        )
        print(f"  {desc}: {bonus:.2%} damage ({(bonus - 1) * 100:+.1f}%)")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 60)
    print("COOPERATIVE BEHAVIOR SYSTEM DEMONSTRATION")
    print("=" * 60)
    print("\nThis demo shows how social traits drive cooperative behaviors:")
    print("  - Food sharing based on altruism, kinship, and need")
    print("  - Fight joining based on protectiveness and relationships")
    print("  - Group combat bonuses for cooperative fighters")
    
    demonstrate_food_sharing()
    demonstrate_fight_joining()
    demonstrate_group_combat()
    
    print("\n\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("\nKey Takeaways:")
    print("  ✓ Altruistic creatures share food with family and hungry allies")
    print("  ✓ Protective creatures join family fights despite danger")
    print("  ✓ Cooperative creatures get stronger in groups")
    print("  ✓ Independent/selfish creatures prioritize themselves")
    print("  ✓ Relationship metrics (affinity, trust, kinship) drive decisions")
    print("\nThese behaviors emerge naturally from trait combinations!")
    print("=" * 60)


if __name__ == "__main__":
    main()
