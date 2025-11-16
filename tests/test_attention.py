"""
Test the attention/focus system for agents.

Validates that agents properly prioritize stimuli and maintain focus.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.attention import (
    AttentionManager,
    StimulusType,
    create_attention_manager_from_traits
)
from src.models.trait import Trait


def test_basic_attention_switching():
    """Test that attention manager switches focus based on priorities."""
    print("\n=== Test: Basic Attention Switching ===")
    
    manager = AttentionManager()
    current_time = 0.0
    
    # Start with exploring
    stimuli = {
        StimulusType.EXPLORING: 30.0
    }
    focus = manager.evaluate_and_update_focus(stimuli, current_time)
    assert focus == StimulusType.EXPLORING, f"Expected EXPLORING, got {focus}"
    print(f"✓ Initial focus: {focus.value}")
    
    # Try to switch to combat (higher priority)
    current_time = 0.5  # Before commitment time
    stimuli = {
        StimulusType.EXPLORING: 30.0,
        StimulusType.COMBAT: 70.0
    }
    focus = manager.evaluate_and_update_focus(stimuli, current_time)
    # Should switch because combat is much higher priority
    print(f"✓ At 0.5s with combat stimulus, focus: {focus.value}")
    
    # After commitment time, higher priority should definitely switch
    current_time = 4.0
    focus = manager.evaluate_and_update_focus(stimuli, current_time)
    assert focus == StimulusType.COMBAT, f"Expected COMBAT after commitment, got {focus}"
    print(f"✓ At 4.0s, switched to combat: {focus.value}")
    
    print("✓ Basic attention switching works!")


def test_commitment_time():
    """Test that agents stay committed to their current focus."""
    print("\n=== Test: Commitment Time ===")
    
    manager = AttentionManager()
    current_time = 0.0
    
    # Start foraging
    stimuli = {StimulusType.FORAGING: 60.0}
    focus = manager.evaluate_and_update_focus(stimuli, current_time)
    assert focus == StimulusType.FORAGING
    print(f"✓ Started foraging at time 0.0")
    
    # Try to switch to combat immediately (should resist)
    current_time = 0.5
    stimuli = {
        StimulusType.FORAGING: 60.0,
        StimulusType.COMBAT: 65.0  # Only slightly higher
    }
    focus = manager.evaluate_and_update_focus(stimuli, current_time)
    is_committed = manager.is_committed(current_time)
    print(f"✓ At 0.5s: committed={is_committed}, focus={focus.value}")
    
    # After commitment time, should be willing to switch
    current_time = 3.0
    focus = manager.evaluate_and_update_focus(stimuli, current_time)
    is_committed = manager.is_committed(current_time)
    print(f"✓ At 3.0s: committed={is_committed}, focus={focus.value}")
    
    print("✓ Commitment time works!")


def test_trait_modifiers():
    """Test that traits affect attention behavior."""
    print("\n=== Test: Trait Modifiers ===")
    
    # Create persistent trait
    persistent_trait = Trait(
        name="Persistent",
        description="Sticks with tasks longer",
        trait_type="personality"
    )
    
    # Create distractible trait
    distractible_trait = Trait(
        name="Distractible",
        description="Easily distracted",
        trait_type="personality"
    )
    
    # Test persistent creature
    persistent_manager = create_attention_manager_from_traits([persistent_trait])
    persistent_commitment = persistent_manager.priorities[StimulusType.FORAGING].min_commitment_time
    print(f"✓ Persistent creature foraging commitment: {persistent_commitment:.2f}s")
    
    # Test distractible creature
    distractible_manager = create_attention_manager_from_traits([distractible_trait])
    distractible_threshold = distractible_manager.priorities[StimulusType.FORAGING].distraction_threshold
    print(f"✓ Distractible creature foraging threshold: {distractible_threshold:.2f}")
    
    # Test normal creature
    normal_manager = AttentionManager()
    normal_commitment = normal_manager.priorities[StimulusType.FORAGING].min_commitment_time
    normal_threshold = normal_manager.priorities[StimulusType.FORAGING].distraction_threshold
    print(f"✓ Normal creature foraging commitment: {normal_commitment:.2f}s, threshold: {normal_threshold:.2f}")
    
    # Verify persistent has higher commitment time
    assert persistent_commitment > normal_commitment, "Persistent should have longer commitment"
    print("✓ Trait modifiers work!")


def test_priority_calculation():
    """Test that priorities are calculated correctly with urgency."""
    print("\n=== Test: Priority Calculation ===")
    
    manager = AttentionManager()
    
    # Normal foraging priority
    normal_priority = manager.calculate_effective_priority(
        StimulusType.FORAGING,
        urgency_modifier=1.0
    )
    print(f"✓ Normal foraging priority: {normal_priority}")
    
    # Critical hunger urgency
    critical_priority = manager.calculate_effective_priority(
        StimulusType.FORAGING,
        urgency_modifier=3.0
    )
    print(f"✓ Critical foraging priority: {critical_priority}")
    
    # Verify urgency multiplies priority
    assert critical_priority == normal_priority * 3.0, "Urgency should multiply priority"
    
    # Fleeing always has higher base priority than foraging
    flee_priority = manager.calculate_effective_priority(StimulusType.FLEEING)
    forage_priority = manager.calculate_effective_priority(StimulusType.FORAGING)
    assert flee_priority > forage_priority, "Fleeing should have higher base priority"
    print(f"✓ Fleeing priority ({flee_priority}) > Foraging priority ({forage_priority})")
    
    print("✓ Priority calculation works!")


def test_debug_info():
    """Test that debug info is provided."""
    print("\n=== Test: Debug Info ===")
    
    manager = AttentionManager()
    current_time = 0.0
    
    # Set a focus
    manager.set_focus(StimulusType.COMBAT, current_time)
    
    # Get debug info
    debug = manager.get_debug_info(current_time)
    
    assert 'current_focus' in debug
    assert 'focus_duration' in debug
    assert 'is_committed' in debug
    assert debug['current_focus'] == StimulusType.COMBAT.value
    
    print(f"✓ Debug info: {debug}")
    print("✓ Debug info works!")


def run_all_tests():
    """Run all attention system tests."""
    print("=" * 60)
    print("Testing Attention/Focus System")
    print("=" * 60)
    
    try:
        test_basic_attention_switching()
        test_commitment_time()
        test_trait_modifiers()
        test_priority_calculation()
        test_debug_info()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        return True
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
