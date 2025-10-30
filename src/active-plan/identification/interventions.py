"""Intervention Applier for Causal MCTS.

This module handles parsing and applying interventions to the symbolic state.
For simulation-less operation, interventions are applied purely symbolically
using the StateManager to update positions and infer relationships.

Author: Yazz Warsame
"""

from state_manager import StateManager


class InterventionApplier:
    """Lightweight intervention applier for symbolic state updates.
    
    This class parses intervention actions and applies them to a StateManager.
    For Scenario 1, it focuses on directional shifts (left, right, forward, back).
    
    Attributes:
        state_manager: StateManager instance for tracking state changes.
        shift_reward: Reward bonus for successful shifts (currently unused).
    """
    
    def __init__(self, state_manager, shift_reward):
        """Initialize the intervention applier.
        
        Args:
            state_manager: StateManager instance to apply interventions to.
            shift_reward: Reward bonus for successful shifts (default: 0.0).
        """
        self.state_manager = state_manager
        self.shift_reward = shift_reward
    
    def parse_action(self, action):
        """Parse an action string into direction and magnitude.
        
        Args:
            action: Action string (e.g., 'left,0.005', 'right,0.01').
            
        Returns:
            Tuple of (direction, magnitude), or (None, None) if parsing fails.
            
        Examples:
            >>> parse_action('left,0.005')
            ('left', 0.005)
            >>> parse_action('forward,0.02')
            ('forward', 0.02)
        """
        try:
            parts = action.split(',')
            if len(parts) != 2:
                return None, None
            
            direction = parts[0].strip()
            magnitude = float(parts[1].strip())
            
            # Validate direction
            valid_directions = {'left', 'right', 'forward', 'back'}
            if direction not in valid_directions:
                return None, None
            
            return direction, magnitude
            
        except (ValueError, AttributeError):
            return None, None
    
    def apply(self, obj, action) :
        """Apply an intervention to an object.
        
        Parses the action and applies it to the object via the StateManager.
        
        Args:
            obj: Name of the object to intervene on (e.g., '1', '2', '3').
            action: Action string (e.g., 'left,0.005').
            
        Returns:
            Tuple of (success, reward_delta):
                - success: True if intervention was successfully applied
                - reward_delta: Immediate reward from this intervention
        """
        # Handle shift actions
        if ',' in action and any(d in action for d in ['left', 'right', 'forward', 'back']):
            return self._apply_shift(obj, action)
        
        # Handle swap actions (for future scenarios)
        if obj == "Swap" and ',' in action:
            return self._apply_swap(action)
        
        # Handle pick/place actions (for future scenarios)
        if 'pick' in action or 'place' in action:
            return self._apply_pick_place(obj, action)
        
        # Unknown action type
        print(f"[InterventionApplier] Unknown action type: {action}")
        return False, 0.0
    
    def _apply_shift(self, obj, action):
        """Apply a directional shift intervention.
        
        Args:
            obj: Name of the object to shift.
            action: Action string (e.g., 'left,0.005').
            
        Returns:
            Tuple of (success, reward_delta).
        """
        direction, magnitude = self.parse_action(action)
        
        if direction is None or magnitude is None:
            print(f"[InterventionApplier] Failed to parse action: {action}")
            return False, 0.0
        
        # Apply shift via StateManager
        success = self.state_manager.apply_shift(obj, direction, magnitude)
        
        if not success:
            return False, 0.0
        
        # For shifts, we can give a small reward if desired
        reward = self.shift_reward if success else 0.0
        
        return success, reward
    
    def _apply_swap(self, action):
        """Apply a swap intervention (placeholder for future scenarios).
        
        Args:
            action: Action string (e.g., '1, 2' to swap objects 1 and 2).
            
        Returns:
            Tuple of (success, reward_delta).
        """
        # TODO: Implement when needed for Scenario 2/3
        print("[InterventionApplier] Swap not yet implemented")
        return False, 0.0
    
    def _apply_pick_place(self, obj, action):
        """Apply pick/place intervention (placeholder for future scenarios).
        
        Args:
            obj: Name of the object.
            action: Action string (e.g., 'pick-top', 'place-top, 2').
            
        Returns:
            Tuple of (success, reward_delta).
        """
        # TODO: Implement when needed for Scenario 2/3
        print("[InterventionApplier] Pick/place not yet implemented")
        return False, 0.0


def create_intervention_applier(initial_state, shift_reward, alignment_threshold):
    """Factory function to create an InterventionApplier with a new StateManager.
    
    Args:
        initial_state: Initial symbolic state dictionary.
        shift_reward: Reward bonus for successful shifts.
        alignment_threshold: Distance threshold for alignment checks.
        
    Returns:
        Configured InterventionApplier instance.
    """
    state_manager = StateManager(initial_state, alignment_threshold)
    return InterventionApplier(state_manager, shift_reward)