"""PDDL Recovery Planner for Block Stacking.

This module orchestrates the recovery planning process by generating PDDL problems
from MCTS results and running Fast Downward to produce action sequences.

Author: Yazz Warsame
"""

import json
import sys
import subprocess
from pathlib import Path
from pddl_builder import PDDLBuilder
from plan_parser import PlanParser


def load_scenario_data(scenario_name):
    """Load all necessary files for recovery planning.
    
    Args:
        scenario_name: Name of scenario (e.g., 'scenario1').
        
    Returns:
        Tuple of (current_state, goal_state, mcts_results):
            - current_state: Initial symbolic state dictionary
            - goal_state: Goal symbolic relationships list
            - mcts_results: MCTS results containing identified misalignments
            
    Raises:
        FileNotFoundError: If any required file is missing.
    """
    # Get paths relative to this file
    base_dir = Path(__file__).parent.parent.parent
    config_dir = base_dir / 'active-plan' / 'config'
    results_dir = base_dir / 'active-plan' / 'identification'
    
    # Load current state
    state_path = config_dir / 'symbolic_state.json'
    with open(state_path, 'r') as f:
        current_state = json.load(f)
    
    # Load scenario config to get goal
    scenario_path = config_dir / f'{scenario_name}.json'
    with open(scenario_path, 'r') as f:
        scenario_config = json.load(f)
    goal_state = scenario_config['symbolic_goal']
    
    # Load MCTS results to identify target objects
    results_path = results_dir / f'results_{scenario_name}.json'
    with open(results_path, 'r') as f:
        mcts_results = json.load(f)
    
    return current_state, goal_state, mcts_results


def extract_target_objects(mcts_results):
    """Extract object IDs that need geometric correction from MCTS results.
    
    MCTS identifies objects with geometric misalignments that are invisible
    to pure symbolic reasoning. These become "target" objects in PDDL.
    
    Args:
        mcts_results: Dictionary containing MCTS intervention results.
        
    Returns:
        List of object IDs (as strings) that need precise placement.
    """
    interventions = mcts_results.get('interventions', [])
    # Extract unique object IDs from intervention sequence
    target_objects = list(set(obj for obj, action in interventions))
    return target_objects


def run_fast_downward(domain_path, problem_path, work_dir):
    """Execute Fast Downward planner.
    
    Args:
        domain_path: Path to PDDL domain file.
        problem_path: Path to PDDL problem file.
        work_dir: Working directory where Fast Downward will write output.
        
    Returns:
        Path to the generated plan file (sas_plan).
        
    Raises:
        RuntimeError: If Fast Downward fails to find a plan.
    """
    work_dir = Path(work_dir).resolve()
    work_dir.mkdir(parents=True, exist_ok=True)
    
    # Locate fast-downward.py
    # First try: sibling to recovery directory (recovery/../downward)
    fd_script = Path(__file__).parent.parent / 'downward' / 'fast-downward.py'
    
    if not fd_script.exists():
        # Second try: in work_dir
        fd_script = work_dir / 'downward' / 'fast-downward.py'
    
    if not fd_script.exists():
        # Third try: in recovery subdirectory
        fd_script = Path(__file__).parent / 'downward' / 'fast-downward.py'
    
    if not fd_script.exists():
        raise FileNotFoundError(
            f"Fast Downward script not found. Searched in:\n"
            f"  {Path(__file__).parent.parent / 'downward'}\n"
            f"  {work_dir / 'downward'}\n"
            f"  {Path(__file__).parent / 'downward'}"
        )
    
    # Build command
    cmd = [
        sys.executable,
        str(fd_script),
        str(domain_path),
        str(problem_path),
        "--search", "astar(lmcut())"
    ]
    
    print(f"\n[planner] Running Fast Downward...")
    print(f"[planner] Working directory: {work_dir}")
    
    # Run planner
    result = subprocess.run(
        cmd,
        cwd=str(work_dir),
        capture_output=True,
        text=True
    )
    
    # Check for success
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        raise RuntimeError("Fast Downward failed to find a plan")
    
    # Find plan file (Fast Downward writes sas_plan or sas_plan.1, etc.)
    plan_file = work_dir / 'sas_plan'
    if not plan_file.exists():
        # Check for numbered plans
        numbered_plans = list(work_dir.glob('sas_plan.*'))
        if numbered_plans:
            # Use the highest numbered plan
            plan_file = max(numbered_plans, key=lambda p: int(p.suffix[1:]) if p.suffix[1:].isdigit() else 0)
        else:
            raise FileNotFoundError("Fast Downward did not produce a plan file")
    
    return plan_file


def main():
    """Main entry point for PDDL recovery planning.
    
    Prompts user for scenario selection, generates PDDL problem with target
    objects identified by MCTS, runs Fast Downward, and displays the plan.
    """
    print("=" * 60)
    print("PDDL Recovery Planner")
    print("=" * 60)
    
    # Scenario selection
    print("\nAvailable scenarios:")
    print("  1. Scenario 1")
    print("  2. Scenario 2")
    print("  3. Scenario 3")
    
    choice = input("\nSelect scenario (1-3, or press Enter for scenario1): ").strip()
    
    scenario_map = {
        '1': 'scenario1',
        '2': 'scenario2',
        '3': 'scenario3',
        '': 'scenario1'
    }
    
    scenario_name = scenario_map.get(choice, 'scenario1')
    print(f"\nLoading {scenario_name}...")
    
    # Load data
    try:
        current_state, goal_state, mcts_results = load_scenario_data(scenario_name)
        target_objects = extract_target_objects(mcts_results)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    
    print(f"[planner] Loaded MCTS results: {len(target_objects)} objects need correction")
    print(f"[planner] Target objects: {target_objects}")
    
    # Generate PDDL problem
    builder = PDDLBuilder()
    pddl_problem = builder.generate_problem(
        current_state=current_state,
        goal_state=goal_state,
        target_objects=target_objects
    )
    
    # Set up directories
    work_dir = Path(__file__).parent / 'fd_output'
    work_dir.mkdir(parents=True, exist_ok=True)
    
    # Write PDDL files
    problem_path = work_dir / 'problem.pddl'
    with open(problem_path, 'w') as f:
        f.write(pddl_problem)
    print(f"[planner] Wrote problem: {problem_path}")
    
    # Copy or locate domain file
    domain_path = Path(__file__).parent / 'domains' / 'domain_s1.pddl'
    if not domain_path.exists():
        print(f"Error: Domain file not found at {domain_path}")
        return
    
    # Run Fast Downward
    try:
        plan_file = run_fast_downward(domain_path, problem_path, work_dir)
        print(f"[planner] Plan generated: {plan_file}")
    except (RuntimeError, FileNotFoundError) as e:
        print(f"Error: {e}")
        return
    
    # Parse and display plan
    parser = PlanParser()
    actions = parser.parse_plan_file(plan_file)
    
    print("\n" + "=" * 60)
    print("RECOVERY PLAN")
    print("=" * 60)
    
    if not actions:
        print("\nNo actions needed (goal already satisfied)")
    else:
        print(f"\nAction sequence ({len(actions)} steps):")
        for i, (action_name, params) in enumerate(actions, 1):
            print(f"  {i}. {action_name} {' '.join(params)}")
    
    # Save plan to JSON
    plan_json_path = work_dir / f'plan_{scenario_name}.json'
    with open(plan_json_path, 'w') as f:
        json.dump(
            [{'action': name, 'args': params} for name, params in actions],
            f,
            indent=2
        )
    print(f"\nPlan saved to: {plan_json_path}")


if __name__ == '__main__':
    main()