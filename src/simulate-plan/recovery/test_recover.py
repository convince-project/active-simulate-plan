"""Integration tests for PDDL recovery planning.

This module provides basic tests to verify that PDDL problem generation,
plan parsing, and the overall recovery pipeline work correctly.

Author: Yazz Warsame
"""

from pddl_builder import PDDLBuilder
from plan_parser import PlanParser


def test_normalize_names():
    """Test block name normalization."""
    print("\nTest: Block name normalization")
    print("-" * 40)
    
    builder = PDDLBuilder()
    
    test_cases = [
        ('1', 'A'),
        ('2', 'B'),
        ('3', 'C'),
        ('4', 'D'),
        ('0', 'TABLE'),
        ('Box A', 'A'),
        ('Block B', 'B'),
        ('Goal_1', 'TABLE'),
        ('Table_0', 'TABLE'),
        ('A', 'A'),
    ]
    
    passed = 0
    for input_name, expected in test_cases:
        result = builder.normalize_name(input_name)
        status = "PASS" if result == expected else "FAIL"
        print(f"  {status} '{input_name}' -> '{result}' (expected '{expected}')")
        if result == expected:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(test_cases)}")
    return passed == len(test_cases)


def test_parse_relationships():
    """Test parsing of symbolic relationships."""
    print("\nTest: Relationship parsing")
    print("-" * 40)
    
    builder = PDDLBuilder()
    
    # Test case: simple stack
    state = {
        'relationships': [
            'On(2,1)',
            'On(1,0)',
            'Clear(2)'
        ]
    }
    
    on_pairs, ontable, clear = builder.parse_relationships(state)
    
    print(f"  Input relationships: {state['relationships']}")
    print(f"  Parsed On pairs: {on_pairs}")
    print(f"  Parsed OnTable: {ontable}")
    print(f"  Parsed Clear: {clear}")
    
    # Verify results
    expected_on = [('B', 'A'), ('A', 'TABLE')]  # After normalization
    expected_ontable = {'A'}  # A is on table (0 -> TABLE)
    expected_clear = {'B'}
    
    on_match = set(on_pairs) == set(expected_on[:-1])  # Exclude TABLE entries
    ontable_match = ontable == expected_ontable
    clear_match = clear == expected_clear
    
    success = ontable_match and clear_match
    
    print(f"\n  Status: {'PASS' if success else 'FAIL'}")
    return success


def test_target_trick():
    """Test PDDL generation with Target Trick."""
    print("\nTest: Target Trick in PDDL generation")
    print("-" * 40)
    
    builder = PDDLBuilder()
    
    # Current state: B on A, A on table, B is misaligned
    current_state = {
        'relationships': [
            'On(2,1)',  # B on A (using numeric IDs)
            'On(1,0)',  # A on table
            'Clear(2)'
        ]
    }
    
    # Goal: Same structure but B needs precise placement
    goal_state = [
        'On(2,1)',  # B on A
        'On(1,0)'   # A on table
    ]
    
    # MCTS identified object 2 (B) as misaligned
    target_objects = ['2']
    
    pddl = builder.generate_problem(current_state, goal_state, target_objects)
    
    print("  Generated PDDL problem:")
    print()
    # Print first 15 lines
    lines = pddl.split('\n')
    for line in lines[:15]:
        print(f"    {line}")
    if len(lines) > 15:
        print(f"    ... ({len(lines)-15} more lines)")
    
    # Verify Target Trick predicates are present
    has_target_on = '(TargetOn B A)' in pddl
    has_at_target = '(AtTarget B)' in pddl
    
    print(f"\n  Contains (TargetOn B A): {has_target_on}")
    print(f"  Contains (AtTarget B) in goal: {has_at_target}")
    
    success = has_target_on and has_at_target
    print(f"\n  Status: {'PASS' if success else 'FAIL'}")
    return success


def test_plan_parsing():
    """Test parsing of Fast Downward plan output."""
    print("\nTest: Plan file parsing")
    print("-" * 40)
    
    parser = PlanParser()
    
    # Create a mock plan file
    plan_content = """; cost = 4 (unit cost)
(unstack b a)
(putdown-to-table b)
(pickup-from-table a)
(stack-target a b)
; Plan length: 4 steps
"""
    
    # Write temporary plan file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.plan', delete=False) as f:
        f.write(plan_content)
        temp_path = f.name
    
    try:
        # Parse the plan
        actions = parser.parse_plan_file(temp_path)
        
        print(f"  Parsed {len(actions)} actions:")
        for action_name, params in actions:
            print(f"    {action_name}({', '.join(params)})")
        
        # Verify
        expected_count = 4
        has_stack_target = any(name == 'stack-target' for name, _ in actions)
        
        success = len(actions) == expected_count and has_stack_target
        
        print(f"\n  Correct action count: {len(actions) == expected_count}")
        print(f"  Contains stack-target: {has_stack_target}")
        print(f"\n  Status: {'PASS' if success else 'FAIL'}")
        
        return success
    finally:
        # Clean up
        import os
        os.unlink(temp_path)


def test_plan_validation():
    """Test plan validation."""
    print("\nTest: Plan validation")
    print("-" * 40)
    
    parser = PlanParser()
    
    # Valid plan
    valid_plan = [
        ('unstack', ['A', 'B']),
        ('stack-target', ['A', 'B'])
    ]
    
    is_valid, error = parser.validate_plan(valid_plan)
    print(f"  Valid plan: {'PASS' if is_valid else 'FAIL'}")
    if error:
        print(f"    Error: {error}")
    
    # Invalid plan (wrong parameter count)
    invalid_plan = [
        ('unstack', ['A']),  # Should have 2 parameters
    ]
    
    is_valid, error = parser.validate_plan(invalid_plan)
    print(f"  Invalid plan detection: {'PASS' if not is_valid else 'FAIL'}")
    if error:
        print(f"    Expected error: {error}")
    
    return True


def run_all_tests():
    """Run all integration tests."""
    print("=" * 60)
    print("PDDL Recovery Integration Tests")
    print("=" * 60)
    
    tests = [
        test_normalize_names,
        test_parse_relationships,
        test_target_trick,
        test_plan_parsing,
        test_plan_validation,
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append((test_func.__name__, result))
        except Exception as e:
            print(f"\n  EXCEPTION: {e}")
            results.append((test_func.__name__, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else " FAIL"
        print(f"  {status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return passed == total


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)