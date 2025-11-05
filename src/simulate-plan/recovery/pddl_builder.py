"""PDDL Problem Generator.

This module generates PDDL problem files that bridge symbolic and geometric reasoning.
The "Target Trick" creates symbolic proxies for geometric misalignments identified by MCTS.

Author: Yazz Warsame
"""

import re


class PDDLBuilder:
    """Generates PDDL problem files with target predicates for precise placement.
    
    The Target Trick works by adding special predicates for geometrically misaligned
    blocks that MCTS identified. For each target object:
    - Initial state gets TargetOn(X, Y) to mark "needs precise placement"
    - Goal state requires AtTarget(X) to force use of stack-target action
    
    This creates a symbolic gap that forces the planner to correct geometric
    misalignments, even when symbolic relationships like On(X,Y) are satisfied.
    """
    
    def __init__(self):
        """Initialize the PDDL problem builder."""
        pass
    
    def normalize_name(self, name):
        """Normalize block names to single uppercase letters.
        
        Handles various naming conventions from JSON files:
        - 'Box A', 'Block B' -> 'A', 'B'
        - '0', '1', '2', '3', '4' -> 'A', 'B', 'C', 'D', 'TABLE'
        - 'Goal_*', 'Table_*' -> 'TABLE'
        
        Args:
            name: Raw name string from JSON.
            
        Returns:
            Normalized name (single uppercase letter or 'TABLE').
        """
        s = str(name).strip()
        
        # Direct block mappings
        block_map = {
            'Box A': 'A', 'Box B': 'B', 'Box C': 'C', 'Box D': 'D',
            'Block A': 'A', 'Block B': 'B', 'Block C': 'C', 'Block D': 'D',
            'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D'
        }
        
        if s in block_map:
            return block_map[s]
        
        # Numeric to letter mapping (common in JSON states)
        # Object 0 is typically the table/goal surface
        # Objects 1,2,3,4 map to blocks A,B,C,D
        numeric_map = {
            '0': 'TABLE',
            '1': 'A',
            '2': 'B',
            '3': 'C',
            '4': 'D'
        }
        if s in numeric_map:
            return numeric_map[s]
        
        # Handle single letters
        if re.fullmatch(r'[A-Z]', s):
            return s
        
        # Clean and retry
        s_clean = re.sub(r'[^A-Za-z0-9_]', '', s)
        if s_clean in block_map or s_clean in numeric_map:
            return block_map.get(s_clean, numeric_map.get(s_clean))
        
        if re.fullmatch(r'[A-Z]', s_clean):
            return s_clean
        
        # Table/goal surface
        if re.match(r'(?i)goal', s) or re.match(r'(?i)table', s):
            return 'TABLE'
        
        return s_clean.upper()
    
    def parse_relationships(self, state):
        """Parse symbolic relationships from state dictionary.
        
        Extracts On(X,Y), OnTable(X), and Clear(X) relationships.
        Automatically computes Clear predicates if not explicitly provided.
        
        Args:
            state: Dictionary with 'relationships' list (e.g., ["On(A,B)", "Clear(A)"]).
            
        Returns:
            Tuple of (on_pairs, ontable_set, clear_set):
                - on_pairs: List of (upper, lower) tuples for On(upper, lower)
                - ontable_set: Set of blocks on the table
                - clear_set: Set of clear blocks
        """
        rels = state.get('relationships', [])
        on_pairs = []
        ontable_set = set()
        clear_set = set()
        
        # Parse relationships
        for r in rels:
            # Match On(X, Y)
            m = re.match(r'\s*On\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)', r, flags=re.IGNORECASE)
            if m:
                upper_raw, lower_raw = m.group(1), m.group(2)
                upper = self.normalize_name(upper_raw)
                lower = self.normalize_name(lower_raw)
                
                if lower == 'TABLE':
                    ontable_set.add(upper)
                else:
                    on_pairs.append((upper, lower))
                continue
            
            # Match Clear(X)
            m = re.match(r'\s*Clear\s*\(\s*([^)]+)\)', r, flags=re.IGNORECASE)
            if m:
                clear_set.add(self.normalize_name(m.group(1)))
                continue
        
        # If Clear not provided, compute from stack structure
        if not clear_set:
            # Blocks that have something on top of them
            supporting = {lower for upper, lower in on_pairs}
            # All blocks mentioned in On relationships
            all_blocks = {upper for upper, lower in on_pairs} | supporting
            # Clear blocks are those not supporting anything
            clear_set = {b for b in all_blocks if b not in supporting}
            # Also include ontable blocks not supporting anything
            clear_set |= {b for b in ontable_set if b not in supporting}
        
        return on_pairs, ontable_set, clear_set
    
    def build_support_map(self, on_pairs, ontable_set):
        """Build a map of what each block is sitting on.
        
        Args:
            on_pairs: List of (upper, lower) tuples from On relationships.
            ontable_set: Set of blocks on the table.
            
        Returns:
            Dictionary mapping block -> what it sits on ('TABLE' or another block).
        """
        supports = {}
        
        for upper, lower in on_pairs:
            supports[upper] = lower
        
        for block in ontable_set:
            supports[block] = 'TABLE'
        
        return supports
    
    def generate_problem(self, current_state, goal_state, target_objects):
        """Generate complete PDDL problem with Target Trick for precise placement.
        
        This is where the magic happens: target objects identified by MCTS get
        special treatment in the PDDL problem to force geometric corrections.
        
        Args:
            current_state: Dictionary with current symbolic state and relationships.
            goal_state: List of goal symbolic predicates (e.g., ["On(A,B)", "On(B,C)"]).
            target_objects: List of object IDs that need precise placement (from MCTS).
            
        Returns:
            String containing complete PDDL problem definition.
        """
        # Normalize target objects
        targets = set(self.normalize_name(obj) for obj in target_objects)
        
        # Parse current state
        on_current, ontable_current, clear_current = self.parse_relationships(current_state)

        # Remove TABLE from sets (it's not a block object)
        ontable_current.discard('TABLE')
        clear_current.discard('TABLE')
        
        # Parse goal state (provided as list of strings)
        goal_dict = {'relationships': goal_state}
        on_goal, ontable_goal, _ = self.parse_relationships(goal_dict)
        
        # Build support map for goal state
        supports_goal = self.build_support_map(on_goal, ontable_goal)


        
        # Collect all blocks (exclude TABLE)
        all_blocks = set()
        for upper, lower in on_current:
            all_blocks.add(upper)
            if lower != 'TABLE':
                all_blocks.add(lower)
        for upper, lower in on_goal:
            all_blocks.add(upper)
            if lower != 'TABLE':
                all_blocks.add(lower)
        all_blocks |= ontable_current
        all_blocks |= ontable_goal
        all_blocks.discard('TABLE')  # Remove TABLE from blocks set

        blocks = sorted(all_blocks)
        
    
        
        # Build initial state predicates
        init_lines = []
        init_lines.append("(HandEmpty)")
        
        # Add On relationships
        for upper, lower in on_current:
            init_lines.append(f"(On {upper} {lower})")
        
        # Add OnTable predicates
        for block in sorted(ontable_current):
            init_lines.append(f"(OnTable {block})")
        
        # Add Clear predicates
        for block in sorted(clear_current):
            init_lines.append(f"(Clear {block})")
        
        # THE TARGET TRICK: Add TargetOn predicates for misaligned blocks
        # This marks that these blocks need precise placement
        for block in targets:
            if block in supports_goal:
                support = supports_goal[block]
                if support != 'TABLE':  # stack-target only works for block-on-block
                    init_lines.append(f"(TargetOn {block} {support})")
        
        # Build goal predicates
        goal_lines = []
        
        # THE TARGET TRICK: Require AtTarget for all target blocks
        # This forces the planner to use stack-target actions
        for block in targets:
            if block in supports_goal:
                support = supports_goal[block]
                if support != 'TABLE':
                    goal_lines.append(f"(AtTarget {block})")
        
        # Add all goal On relationships
        for upper, lower in on_goal:
            goal_lines.append(f"(On {upper} {lower})")
        
        # Add goal OnTable relationships (skip TABLE itself)
        for block in sorted(ontable_goal):
            if block != 'TABLE':  # Add this check
                goal_lines.append(f"(OnTable {block})")
                
        # Require hand to be empty at end
        goal_lines.append("(HandEmpty)")
        
        # Assemble PDDL problem
        pddl_lines = []
        pddl_lines.append("(define (problem recovery-problem)")
        pddl_lines.append("  (:domain recovery-blocks)")
        pddl_lines.append("  (:objects")
        
        # Declare blocks
        if blocks:
            pddl_lines.append(f"    {' '.join(blocks)} - block")
        else:
            pddl_lines.append("    - block")
        
        pddl_lines.append("  )")
        pddl_lines.append("  (:init")
        
        for line in init_lines:
            pddl_lines.append(f"    {line}")
        
        pddl_lines.append("  )")
        pddl_lines.append("  (:goal (and")
        
        for line in goal_lines:
            pddl_lines.append(f"    {line}")
        
        pddl_lines.append("  ))")
        pddl_lines.append(")")

        return "\n".join(pddl_lines)
