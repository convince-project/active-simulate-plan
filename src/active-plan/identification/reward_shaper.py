"""Reward Shaper for MCTS Intervention Planning.

This module provides reward computation for evaluating intervention sequences.
It computes both step-wise rewards (after each intervention) and final rewards
(based on goal achievement and intervention cost).

Author: Yazz Warsame
"""

class RewardShaper:
    """Computes rewards for intervention sequences.
    
    This class evaluates the quality of intervention sequences by computing:
    1. Step rewards: Immediate rewards after each intervention
    2. Final rewards: Overall score based on goal achievement minus penalties
    
    Attributes:
        goal: Set of goal symbolic relationships to achieve.
        shift_bonus: Reward bonus for each shift intervention.
        depth_penalty: Penalty factor per intervention (encourages shorter sequences).
    """
    
    def __init__(self, goal_symbolic_set, 
                 shift_bonus, 
                 depth_penalty):
        """Initialize the reward shaper.
        
        Args:
            goal_symbolic_set: Set of goal relationships (e.g., {'On(2,1)', 'On(3,2)'}).
            shift_bonus: Reward bonus for shift interventions (default: 0.25).
            depth_penalty: Penalty per intervention to encourage brevity (default: 0.05).
        """
        self.goal = goal_symbolic_set
        self.shift_bonus = shift_bonus
        self.depth_penalty = depth_penalty

    def step_reward(self, prev_rels, curr_rels, action):
        """Compute immediate reward after applying one intervention.
        
        This is called after each intervention to provide immediate feedback.
        Can reward based on action type or changes in relationships.
        
        Args:
            prev_rels: Symbolic relationships before the intervention.
            curr_rels: Symbolic relationships after the intervention.
            action: The action string (e.g., 'left,0.005', 'pick-top').
            
        Returns:
            Immediate reward for this step.
        """
        reward = 0.0
        
        # Give credit for shift interventions (Scenario 1)
        if any(d in action for d in ['left', 'right', 'forward', 'back']):
            reward += self.shift_bonus
        
        # Give credit for other intervention types (Scenarios 2/3)
        # if action.startswith("place-"):
        #     reward += self.teleport_bonus
        
        # Optionally penalize for breaking relationships
        # lost_rels = prev_rels - curr_rels
        # if lost_rels:
        #     reward -= 0.1 * len(lost_rels)
        
        return reward

    def final_reward(self, final_rels,  interventions):
        """Compute final reward for the complete intervention sequence.
        
        This is called at the end of a rollout to evaluate the overall quality
        of the intervention sequence. Combines goal achievement with intervention cost.
        
        Args:
            final_rels: Final set of symbolic relationships after all interventions.
            interventions: Complete list of (object, action) tuples applied.
            
        Returns:
            Final reward score (higher is better).
        """
        # Base reward: fraction of goal predicates achieved
        if len(self.goal) == 0:
            base = 1.0
        else:
            achieved = len(final_rels & self.goal)
            total = len(self.goal)
            base = achieved / total
        
        # Penalty for intervention depth (encourages shorter sequences)
        penalty = self.depth_penalty * len(interventions)
        
        return base - penalty