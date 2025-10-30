"""Monte Carlo Tree Search for Causal Intervention Planning.

This module implements a canonical MCTS algorithm (Select, Expand, Rollout, Backpropagate)
for finding minimal causal interventions that transform a current symbolic state into a goal state.
The algorithm operates purely on symbolic representations without requiring simulation.

Author: Yazz Warsame
"""


from state_manager import StateManager
from interventions import InterventionApplier
from reward_shaper import RewardShaper
import math
import random
import json
from pathlib import Path
from typing import List, Tuple, Dict, Set, Optional


class MCTSNode:
    """Represents a node in the MCTS tree.
    
    Each node corresponds to a state reached by applying a sequence of interventions
    from the root state.
    
    Attributes:
        interventions: Sequence of (object, action) tuples leading to this state.
        parent: Parent node in the tree, or None for root.
        children: List of child nodes.
        visits: Number of times this node has been visited.
        total_reward: Cumulative reward from all rollouts through this node.
        untried_actions: List of legal actions not yet expanded from this node.
        local_violations: Set of actions that led to violations (used for pruning).
    """
    
    def __init__(self, interventions = None, parent = None):
        """Initialize a new MCTS node.
        
        Args:
            interventions: List of (object, action) tuples applied to reach this state.
            parent: Parent node in the tree, or None if this is the root.
        """
        self.interventions = interventions or []
        self.parent = parent
        self.children = []
        self.visits = 0
        self.total_reward = 0.0
        self.untried_actions = None
        self.local_violations = set()


class CausalMCTS:
    """MCTS-based planner for causal intervention planning.
    
    This class implements a complete MCTS loop for finding sequences of causal interventions
    that transform an initial symbolic state into a goal state. The planner operates on
    symbolic state representations loaded from JSON files.
    
    Attributes:
        initial_state: Dictionary containing the initial symbolic state.
        goal_state: Set of symbolic relationships defining the goal.
        scenario: Dictionary containing scenario configuration.
        reward_shaper: RewardShaper instance for computing rewards.
        intervention_space: Dictionary mapping objects to available interventions.
        max_rollout_depth: Maximum depth for random rollouts.
        termination_threshold: Reward threshold for early termination.
        exploration_constant: UCT exploration parameter (default: 0.5).
        reward_history: List of rewards from completed rollouts.
    """
    
    def __init__(
        self,
        initial_state,
        goal_state,
        scenario,
        reward_shaper,
        intervention_space,
        max_rollout_depth,
        termination_threshold,
        exploration_constant
    ):
        """Initialize the Causal MCTS planner.
        
        Args:
            initial_state: Dictionary with initial symbolic state (from JSON).
            goal_state: Set of symbolic goal predicates (e.g., {'On(2,1)', 'On(3,2)'}).
            scenario: Complete scenario configuration dictionary.
            reward_shaper: Instance of RewardShaper for reward computation.
            intervention_space: Dict mapping object names to available intervention actions.
            max_rollout_depth: Maximum number of interventions in a rollout.
            termination_threshold: Reward value that indicates success.
            exploration_constant: UCT exploration constant (higher = more exploration).
        """
        self.initial_state = initial_state
        self.goal_state = goal_state
        self.scenario = scenario
        self.reward_shaper = reward_shaper
        self.intervention_space = intervention_space
        self.max_rollout_depth = max_rollout_depth
        self.termination_threshold = termination_threshold
        self.exploration_constant = exploration_constant
        
        self.reward_history = []
        self.intervention_trace = []
        
        # Track if we've found a solution
        self.solution_found = False
        
        # Current symbolic state (will be updated during rollouts)
        self.current_relationships = set(initial_state.get('relationships', []))

    def search_resolution(self, iterations: int = 300):
        """Execute MCTS search for a fixed number of iterations.
        
        This is the main entry point for running the MCTS algorithm. It performs
        the complete MCTS loop: selection, expansion, rollout, and backpropagation.
        
        Args:
            iterations: Number of MCTS iterations to perform.
            
        Returns:
            A tuple containing:
                - Best sequence of interventions found (list of (object, action) tuples)
                - Number of iterations completed before termination
        """
        root = MCTSNode()
        
        # Initialize root with all legal actions
        base_actions = self.get_legal_actions([], root)
        root.untried_actions = base_actions
        
        print(f"Starting MCTS with {len(base_actions)} possible root actions")
        print(f"Goal: {self.goal_state}")
        print(f"Termination threshold: {self.termination_threshold}\n")
        
        for i in range(iterations):
            print(f"--- Iteration {i} ---")
            
            # MCTS phases
            node = self.select(root)
            child = self.expand(node)
            
            # Skip if root is exhausted
            if child.interventions == []:
                continue
            
            # Check if another process found a solution (for future parallel version)
            if self.solution_found:
                print(f"Solution found at iteration {i}")
                if self.reward_history:
                    return self.reward_history[-1]['interventions'], i
                return child.interventions, i
            
            # Perform rollout
            reward = self.rollout(child)
            
            print(f"[ITER {i}] reward={reward:.3f}, depth={len(child.interventions)}, "
                  f"interventions={child.interventions}")
            
            # Backpropagate reward
            self.backpropagate(child, reward)
            
            # Check for early termination
            if reward >= self.termination_threshold:
                print(f"\n Success! Found solution at iteration {i}")
                print(f"Final interventions: {child.interventions}")
                self.solution_found = True
                return child.interventions, i
        
        # Return best solution found
        if root.children:
            best = max(root.children, 
                      key=lambda c: c.total_reward / c.visits if c.visits else 0.0)
            print(f"\nCompleted {iterations} iterations.")
            print(f"Best solution: {best.interventions}")
            print(f"Best reward: {best.total_reward / best.visits if best.visits else 0.0:.3f}")
            return best.interventions, iterations
        else:
            print("\nNo solution found.")
            return [], iterations

    def select(self, node: MCTSNode):
        """Select a node to expand using UCT policy.
        
        Traverses the tree from the given node using Upper Confidence Bound for Trees (UCT)
        until reaching a node that can be expanded.
        
        Args:
            node: Root node from which to start selection.
            
        Returns:
            Node selected for expansion.
        """
        while True:
            # Can we expand this node?
            if node.untried_actions:
                return node
            
            # If node has children, descend using UCT
            if node.children:
                node = self._best_child(node)
                
                # Initialize untried actions for this node if needed
                if node.untried_actions is None:
                    node.untried_actions = self.get_legal_actions(node.interventions, node)
                continue
            
            # Leaf node with no untried actions
            return node

    def _best_child(self, node: MCTSNode):
        """Select child with highest UCT score.
        
        Uses the Upper Confidence Bound for Trees formula:
        UCT = exploitation + exploration
            = (total_reward / visits) + c * sqrt(ln(parent_visits) / visits)
        
        Args:
            node: Parent node.
            
        Returns:
            Child node with maximum UCT score.
        """
        best_child = None
        best_score = -float('inf')
        
        for child in node.children:
            # Exploitation term
            exploit = child.total_reward / child.visits if child.visits > 0 else 0.0
            
            # Exploration term
            if child.visits > 0 and node.visits > 0:
                explore = self.exploration_constant * math.sqrt(
                    math.log(node.visits) / child.visits
                )
            else:
                explore = float('inf')  # Prioritize unvisited children
            
            score = exploit + explore
            
            if score > best_score:
                best_child = child
                best_score = score
        
        return best_child

    def expand(self, node: MCTSNode):
        """Expand a node by trying an untried action.
        
        Creates a new child node by applying one of the untried actions from the given node.
        
        Args:
            node: Node to expand.
            
        Returns:
            Newly created child node, or the input node if no actions available.
        """

        if node.untried_actions is None:
            node.untried_actions = self.get_legal_actions(node.interventions, node)
        
        if not node.untried_actions:
            return node
        
        # Select and remove an untried action
        action = node.untried_actions.pop(0)
        
        # Create new child with this action
        new_interventions = node.interventions + [action]
        child = MCTSNode(interventions=new_interventions, parent=node)
        node.children.append(child)
        
        return child

    def get_legal_actions(self, interventions, node):
        """Generate list of legal actions for a given state.
        
        Determines which interventions are valid to apply next, based on the current
        sequence of interventions and any known violations.
        
        Args:
            interventions: Current sequence of (object, action) tuples.
            node: Current MCTS node (used for pruning based on violations).
            
        Returns:
            List of legal (object, action) tuples that can be applied next.
        """
        legal_actions = []
        
        # Get all possible actions from intervention space
        for obj, actions in self.intervention_space.items():
            for action in actions:
                candidate = (obj, action)
                
                # Skip if this action has been marked as a violation
                if candidate in node.local_violations:
                    continue
                
                # Skip if object was already intervened on (optional - can be relaxed)
                intervened_objects = {intv[0] for intv in interventions}
                if obj in intervened_objects and obj != "Swap":
                    continue
                
                legal_actions.append(candidate)
        
        return legal_actions

    def rollout(self, node: MCTSNode) -> float:
        """Perform a random rollout from the given node.
        
        Simulates applying the interventions in the node, then continues with random
        actions until max depth is reached or goal is achieved. Computes cumulative reward.
        
        Args:
            node: Node from which to start the rollout.
            
        Returns:
            Total reward accumulated during the rollout.
        """
    
        
        # Create a fresh state manager for this rollout
        # Using stricter threshold (5mm) for Scenario 1 misalignments of 10-25mm
        state_mgr = StateManager(self.initial_state, alignment_threshold=0.005)
        applier = InterventionApplier(state_mgr, shift_reward=0.0)
        
        # Track relationships
        prev_rels = set(self.initial_state.get('relationships', []))
        
        shaped_reward = 0.0
        
        # 1) Apply the prefix interventions (deterministic part)
        for obj, action in node.interventions:
            # Apply intervention to state
            success, step_reward = applier.apply(obj, action)
            
            # Get updated relationships
            current_rels = state_mgr.get_relationships()
            
            # Compute step reward
            shaped_reward += self.reward_shaper.step_reward(prev_rels, current_rels, action)
            prev_rels = current_rels.copy()
            
            # Add immediate reward from intervention (if any)
            shaped_reward += step_reward
        
        # Get current relationships after prefix
        current_rels = state_mgr.get_relationships()
        
        # Add final reward for the prefix
        shaped_reward += self.reward_shaper.final_reward(current_rels, node.interventions)
        
        # Check for misalignment bonus (Scenario 1 specific)
        # ALL objects should align with Object 0 (the reference)
        misalignment_bonus = 0.0
        
        # DEBUG: Print alignment details
        if len(node.interventions) <= 1:  # Only debug first few
            print(f"\n  [DEBUG] Alignment check after {len(node.interventions)} interventions:")
            for obj in ['1', '2', '3', '4']:
                obj_pos = state_mgr.get_position(obj)
                ref_pos = state_mgr.get_position('0')
                if obj_pos and ref_pos:
                    x_diff = abs(obj_pos[0] - ref_pos[0])
                    y_diff = abs(obj_pos[1] - ref_pos[1])
                    is_aligned = not state_mgr.check_misalignment(obj, reference='0')
                    print(f"    Obj {obj} vs 0: pos={obj_pos[:2]}, ref={ref_pos[:2]}, "
                          f"x_diff={x_diff:.4f}, y_diff={y_diff:.4f}, "
                          f"aligned={is_aligned}, threshold={state_mgr.alignment_threshold}")
                    if is_aligned:
                        misalignment_bonus += 0.25
        else:
            # Normal operation without debug prints
            for obj in ['1', '2', '3', '4']:
                if not state_mgr.check_misalignment(obj, reference='0'):
                    misalignment_bonus += 0.25  # Aligned with Object 0!
        
        shaped_reward += misalignment_bonus
        
        # 2) Early exit if we've hit the termination threshold
        if shaped_reward >= self.termination_threshold:
            self.reward_history.append({
                "interventions": node.interventions.copy(),
                "reward": shaped_reward,
            })
            return shaped_reward
        
        # 3) Random rollout suffix (if allowed)
        rollout_history = node.interventions.copy()
        prefix_len = len(node.interventions)
        suffix_budget = max(0, self.max_rollout_depth - prefix_len)
        
        for _ in range(suffix_budget):
            valid_actions = self.get_legal_actions(rollout_history, node)
            
            if not valid_actions:
                break
            
            # Choose random action for rollout
            obj, action = random.choice(valid_actions)
            rollout_history.append((obj, action))
            
            # Apply intervention
            success, step_reward = applier.apply(obj, action)
            current_rels = state_mgr.get_relationships()
            
            # Compute step reward
            shaped_reward += self.reward_shaper.step_reward(prev_rels, current_rels, action)
            shaped_reward += step_reward
            prev_rels = current_rels.copy()
        
        # Compute final reward
        current_rels = state_mgr.get_relationships()
        shaped_reward += self.reward_shaper.final_reward(current_rels, rollout_history)
        
        # Record this rollout
        self.reward_history.append({
            "interventions": rollout_history.copy(),
            "reward": shaped_reward,
        })
       
        return shaped_reward

    def checkMisalignment(self, obj, state_manager):
        """Check if an object is misaligned relative to a reference.
        
        Determines whether an object's position deviates significantly from an expected
        alignment (useful for detecting geometric violations).
        
        Args:
            obj: Name of the object to check.
            state_manager: Optional StateManager to use for checking. If None, uses initial state.
            
        Returns:
            True if object is misaligned, False otherwise.
        """
        # If state_manager provided, use it
        if state_manager is not None:
            return state_manager.check_misalignment(obj, reference='0')
        
        # Otherwise check against initial state
        if 'objects' not in self.initial_state:
            return False
        
        objects = self.initial_state['objects']
        
        if obj not in objects or '0' not in objects:
            return False
        
        obj_pos = objects[obj]
        ref_pos = objects['0']
        
        # Check alignment on X and Y axes (threshold: 0.05m)
        threshold = 0.05
        x_aligned = abs(obj_pos[0] - ref_pos[0]) < threshold
        y_aligned = abs(obj_pos[1] - ref_pos[1]) < threshold
        
        # Return True if misaligned (i.e., NOT aligned)
        return not (x_aligned and y_aligned)

    def backpropagate(self, node, reward):
        """Backpropagate reward up the tree.
        
        Updates visit counts and total rewards for all nodes from the given node
        back to the root.
        
        Args:
            node: Node where rollout ended.
            reward: Reward value to propagate.
        """
        while node is not None:
            node.visits += 1
            node.total_reward += reward
            
            # Propagate violations up to parent
            if node.parent:
                node.parent.local_violations.update(node.local_violations)
            
            # Record trace for debugging
            avg_reward = node.total_reward / node.visits
            self.intervention_trace.append({
                'interventions': node.interventions.copy(),
                'visits': node.visits,
                'avg_reward': avg_reward,
                'reward': reward
            })
            
            node = node.parent


def load_scenario(scenario_name):
    """Load scenario configuration and initial state from JSON files.
    
    Args:
        scenario_name: Name of the scenario (e.g., 'scenario1', 'scenario2').
        
    Returns:
        Tuple containing:
            - scenario_config: Scenario configuration dictionary
            - initial_state: Initial symbolic state dictionary  
            - symbolic_state: Copy of initial state for reference
    """
    config_dir = Path(__file__).parent.parent / 'config'
    
    # Load scenario configuration
    scenario_path = config_dir / f'{scenario_name}.json'
    with open(scenario_path, 'r') as f:
        scenario_config = json.load(f)
    
    # Load initial symbolic state
    state_path = config_dir / 'symbolic_state.json'
    with open(state_path, 'r') as f:
        initial_state = json.load(f)
    
    return scenario_config, initial_state, initial_state.copy()


def main():
    """Main entry point for running MCTS intervention planning.
    
    Allows user to select a scenario and runs the MCTS planner to find
    a sequence of interventions that achieves the goal.
    """
    print("=" * 60)
    print("Causal MCTS Intervention Planner")
    print("=" * 60)
    
    # Let user select scenario
    print("\nAvailable scenarios:")
    print("  1. Scenario 1")
    print("  2. Scenario 2")
    print("  3. Scenario 3")
    
    choice = input("\nSelect scenario (1-3, or press Enter for scenario1): ").strip()
    
    scenario_map = {
        '1': 'scenario1',
        '2': 'scenario2',
        '3': 'scenario3',
        '': 'scenario1'  # Default
    }
    
    scenario_name = scenario_map.get(choice, 'scenario1')
    print(f"\nLoading {scenario_name}...")
    
    # Load configuration and state
    try:
        scenario_config, initial_state, _ = load_scenario(scenario_name)
    except FileNotFoundError as e:
        print(f"Error: Could not find configuration files: {e}")
        return
    
  
    
    # Build RewardShaper from config
    reward_shaper = RewardShaper(
        goal_symbolic_set=set(scenario_config["symbolic_goal"]),
        shift_bonus=scenario_config["reward_shaping"]["shift_bonus"],
        depth_penalty=scenario_config["reward_shaping"]["depth_penalty"]
    )
    
    # Initialize MCTS planner
    planner = CausalMCTS(
        initial_state=initial_state,
        goal_state=set(scenario_config["symbolic_goal"]),
        scenario=scenario_config,
        reward_shaper=reward_shaper,
        intervention_space=scenario_config["intv_space"],
        max_rollout_depth=scenario_config["max_rollout_depth"],
        termination_threshold=scenario_config["termination_threshold"],
        exploration_constant=0.0
    )
    
    # Run MCTS search
    print("\nStarting MCTS search...")
    print(f"Max rollout depth: {scenario_config['max_rollout_depth']}")
    print(f"Termination threshold: {scenario_config['termination_threshold']}")
    
    # DEBUG: Check initial alignment state
    print("\n[DEBUG] Initial alignment state (all vs Object 0):")

    debug_mgr = StateManager(initial_state, alignment_threshold=0.005)  # Match rollout threshold
    
    for obj in ['1', '2', '3', '4']:
        obj_pos = debug_mgr.get_position(obj)
        ref_pos = debug_mgr.get_position('0')
        if obj_pos and ref_pos:
            x_diff = abs(obj_pos[0] - ref_pos[0])
            y_diff = abs(obj_pos[1] - ref_pos[1])
            is_aligned = not debug_mgr.check_misalignment(obj, reference='0')
            print(f"  Obj {obj} vs 0: x_diff={x_diff:.4f}, y_diff={y_diff:.4f}, "
                  f"aligned={is_aligned} (threshold={debug_mgr.alignment_threshold}m)")
    print()
    
    iterations = 30000  # Can make this configurable
    result_interventions, final_iter = planner.search_resolution(iterations=iterations)
    
    # Display results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    if result_interventions:
        print(f"\nFinal intervention sequence ({len(result_interventions)} steps):")
        for i, (obj, action) in enumerate(result_interventions, 1):
            print(f"  {i}. Object '{obj}': {action}")
    else:
        print("\nNo solution found within iteration limit.")
    
    print(f"\nTotal iterations: {final_iter}")
    print(f"Total rollouts evaluated: {len(planner.reward_history)}")
    
    # Save results to file
    output_file = f"results_{scenario_name}.json"
    results = {
        'scenario': scenario_name,
        'interventions': result_interventions,
        'iterations': final_iter,
        'total_rollouts': len(planner.reward_history),
        'goal_achieved': planner.solution_found
    }
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")


if __name__ == '__main__':
    main()