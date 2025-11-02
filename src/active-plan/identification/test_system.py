#!/usr/bin/env python3
"""Quick test script for the refactored MCTS system.

This script tests the basic functionality of the StateManager, InterventionApplier,
and MCTS integration.

Author: Yazz Warsame
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from state_manager import StateManager
from interventions import InterventionApplier
from reward_shaper import RewardShaper


def test_state_manager():
    """Test StateManager basic functionality."""
    print("=" * 60)
    print("Testing StateManager")
    print("=" * 60)
    
    # Load initial state
    config_dir = Path(__file__).parent.parent / 'config'
    state_path = config_dir / 'symbolic_state.json'
    
    with open(state_path, 'r') as f:
        initial_state = json.load(f)
    
    # Create state manager
    state_mgr = StateManager(initial_state, alignment_threshold=0.05)
    
    print(f"\n{state_mgr}")
    print(f"Initial relationships: {len(state_mgr.relationships)}")
    print(f"Objects: {list(state_mgr.objects.keys())[:10]}...")
    
    # Check initial misalignment
    print("\nInitial alignment check:")
    for obj in ['1', '2', '3', '4']:
        misaligned = state_mgr.check_misalignment(obj, '0')
        print(f"  Object {obj}: {'MISALIGNED' if misaligned else 'aligned'}")
    
    # Test a shift
    print("\nTesting shift: Object '1' left by 0.01m")
    success = state_mgr.apply_shift('1', 'left', 0.01)
    print(f"  Success: {success}")
    
    # Check alignment after shift
    misaligned_after = state_mgr.check_misalignment('1', '0')
    print(f"  Object 1 after shift: {'MISALIGNED' if misaligned_after else 'aligned'}")
    
    print("\n✓ StateManager test passed!")
    return state_mgr


def test_intervention_applier(state_mgr):
    """Test InterventionApplier functionality."""
    print("\n" + "=" * 60)
    print("Testing InterventionApplier")
    print("=" * 60)
    
    applier = InterventionApplier(state_mgr, shift_reward=0.0)
    
    # Test parsing
    direction, magnitude = applier.parse_action("left,0.005")
    print(f"\nParsing 'left,0.005': direction={direction}, magnitude={magnitude}")
    
    # Test applying an intervention
    print("\nApplying intervention: Object '2', action 'right,0.01'")
    success, reward = applier.apply('2', 'right,0.01')
    print(f"  Success: {success}, Reward: {reward}")
    
    # Check new alignment
    misaligned = state_mgr.check_misalignment('2', '0')
    print(f"  Object 2 alignment: {'MISALIGNED' if misaligned else 'aligned'}")
    
    print("\n✓ InterventionApplier test passed!")
    return applier


def test_reward_shaper():
    """Test RewardShaper functionality."""
    print("\n" + "=" * 60)
    print("Testing RewardShaper")
    print("=" * 60)
    
    goal = {'On(2,1)', 'On(3,2)', 'On(4,3)'}
    shaper = RewardShaper(goal, shift_bonus=0.0, depth_penalty=0.0)
    
    # Test step reward
    prev_rels = {'On(1,0)', 'On(2,1)', 'On(3,2)'}
    curr_rels = {'On(1,0)', 'On(2,1)', 'On(3,2)'}
    
    step_rew = shaper.step_reward(prev_rels, curr_rels, 'left,0.005')
    print(f"\nStep reward for 'left,0.005': {step_rew}")
    
    # Test final reward
    interventions = [('1', 'left,0.005'), ('2', 'right,0.01')]
    final_rew = shaper.final_reward(curr_rels, interventions)
    print(f"Final reward (2 interventions, 2/3 goals): {final_rew:.3f}")
    
    print("\n✓ RewardShaper test passed!")
    return shaper


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("MCTS System Integration Test")
    print("=" * 60)
    
    try:
        # Test components
        state_mgr = test_state_manager()
        applier = test_intervention_applier(state_mgr)
        shaper = test_reward_shaper()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nYou can now run the full MCTS with:")
        print("  python mcts_new.py")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())