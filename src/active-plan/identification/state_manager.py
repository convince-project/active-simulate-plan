"""State Manager for Symbolic State Tracking and Updates.

This module manages the symbolic state of the world, including object positions and
relationships. It handles applying interventions (like shifts) and inferring symbolic
relationships from geometric configurations.

Author: Yazz Warsame
"""

import copy
import math


class StateManager:
    """Manages symbolic state and geometric positions for intervention planning.
    
    This class tracks the current state of all objects, including their positions
    and symbolic relationships. It provides methods to apply interventions and
    check whether relationships are maintained.
    
    Attributes:
        objects: Dictionary mapping object names to [x, y, z] positions.
        relationships: Set of current symbolic relationships (e.g., 'On(2,1)').
        alignment_threshold: Distance threshold for considering objects aligned (meters).
        initial_objects: Copy of initial object positions for reference.
    """
    
    def __init__(self, initial_state, alignment_threshold):
        """Initialize the state manager with an initial state.
        
        Args:
            initial_state: Dictionary containing 'objects' and 'relationships' keys.
            alignment_threshold: Maximum distance (in meters) between objects to
                                maintain alignment. Default: 0.05m (5cm).
        """
        self.objects = copy.deepcopy(initial_state.get('objects', {}))
        self.initial_objects = copy.deepcopy(self.objects)
        self.relationships = set(initial_state.get('relationships', []))
        self.alignment_threshold = alignment_threshold
        
        # Track which objects have been intervened on
        self.intervened_objects = set()
    
    def apply_shift(self, obj, direction, magnitude) :
        """Apply a directional shift to an object's position.
        
        Updates the object's position by moving it in the specified direction
        by the given magnitude. Directions are in the world frame.
        
        Args:
            obj: Name of the object to shift (e.g., '1', '2', '3').
            direction: Direction to shift ('left', 'right', 'forward', 'back').
            magnitude: Distance to shift in meters.
            
        Returns:
            True if shift was successfully applied, False if object not found.
        """
        if obj not in self.objects:
            print(f"[StateManager] Warning: Object '{obj}' not found in state")
            return False
        
        # Direction vectors (x, y, z)
        direction_vectors = {
            'left': (-magnitude, 0, 0),
            'right': (magnitude, 0, 0),
            'forward': (0, magnitude, 0),
            'back': (0, -magnitude, 0)
        }
        
        if direction not in direction_vectors:
            print(f"[StateManager] Warning: Unknown direction '{direction}'")
            return False
        
        # Get current position
        current_pos = self.objects[obj]
        dx, dy, dz = direction_vectors[direction]
        
        # Update position
        self.objects[obj] = [
            current_pos[0] + dx,
            current_pos[1] + dy,
            current_pos[2] + dz
        ]
        
        # Mark as intervened
        self.intervened_objects.add(obj)
        
        return True
    
    def get_relationships(self):
        """Infer current symbolic relationships from geometric positions.
        
        Determines which 'On(A,B)' relationships hold based on current object
        positions. Two objects maintain an 'On' relationship if they are
        geometrically aligned (within threshold).
        
        Returns:
            Set of symbolic relationship strings (e.g., {'On(2,1)', 'On(3,2)'}).
        """
        current_relationships = set()
        
        # Check each original relationship to see if it still holds
        for rel in self.relationships:
            if self._check_relationship_holds(rel):
                current_relationships.add(rel)
        
        return current_relationships
    
    def _check_relationship_holds(self, relationship):
        """Check if a symbolic relationship still holds geometrically.
        
        For 'On(A,B)' relationships, checks if object A is still aligned with
        object B in the x-y plane.
        
        Args:
            relationship: Relationship string (e.g., 'On(2,1)').
            
        Returns:
            True if the relationship still holds, False otherwise.
        """
        # Parse relationship string: 'On(2,1)' -> ('On', '2', '1')
        if not relationship.startswith('On('):
            # Handle non-On relationships (e.g., 'On(X, Table)', 'Obstruct')
            return True  # Assume they hold for now
        
        # Extract objects from 'On(A,B)'
        parts = relationship[3:-1].split(',')  # Remove 'On(' and ')', split by ','
        if len(parts) != 2:
            return True  # Can't parse, assume it holds
        
        obj_a = parts[0].strip()
        obj_b = parts[1].strip()
        
        # Check if both objects exist
        if obj_a not in self.objects or obj_b not in self.objects:
            # If one is missing (like Goal), assume relationship holds
            return True
        
        # Check alignment in x-y plane
        return self.check_alignment(obj_a, obj_b)
    
    def check_alignment(self, obj_a, obj_b):
        """Check if two objects are aligned in the x-y plane.
        
        Objects are considered aligned if their x and y coordinates are within
        the alignment threshold.
        
        Args:
            obj_a: Name of first object.
            obj_b: Name of second object (typically the base).
            
        Returns:
            True if objects are aligned, False otherwise.
        """
        if obj_a not in self.objects or obj_b not in self.objects:
            return False
        
        pos_a = self.objects[obj_a]
        pos_b = self.objects[obj_b]
        
        # Check x and y alignment
        x_diff = abs(pos_a[0] - pos_b[0])
        y_diff = abs(pos_a[1] - pos_b[1])
        
        x_aligned = x_diff < self.alignment_threshold
        y_aligned = y_diff < self.alignment_threshold
        
        return x_aligned and y_aligned
    
    def check_misalignment(self, obj, reference):
        """Check if an object is misaligned relative to a reference object.
        
        This is the inverse of check_alignment - returns True if the object
        is NOT aligned with the reference.
        
        Args:
            obj: Name of the object to check.
            reference: Name of the reference object (default: '0' - typically the base).
            
        Returns:
            True if object is misaligned, False if aligned.
        """
        return not self.check_alignment(obj, reference)
    
    def get_alignment_score(self, goal_relationships):
        """Compute alignment score as fraction of goal relationships maintained.
        
        Args:
            goal_relationships: Set of desired symbolic relationships.
            
        Returns:
            Score between 0 and 1, where 1 means all relationships maintained.
        """
        current_rels = self.get_relationships()
        
        if not goal_relationships:
            return 1.0
        
        maintained = len(current_rels & goal_relationships)
        total = len(goal_relationships)
        
        return maintained / total
    
    def get_position(self, obj):
        """Get the current position of an object.
        
        Args:
            obj: Name of the object.
            
        Returns:
            List [x, y, z] if object exists, None otherwise.
        """
        return self.objects.get(obj, None)
    
    def get_state_snapshot(self):
        """Get a complete snapshot of the current state.
        
        Returns:
            Dictionary containing 'objects' and 'relationships'.
        """
        return {
            'objects': copy.deepcopy(self.objects),
            'relationships': list(self.get_relationships()),
            'intervened_objects': list(self.intervened_objects)
        }
    
    def reset_to_initial(self) -> None:
        """Reset state to initial configuration."""
        self.objects = copy.deepcopy(self.initial_objects)
        self.intervened_objects.clear()
    
    def compute_displacement(self, obj):
        """Compute total displacement of an object from its initial position.
        
        Args:
            obj: Name of the object.
            
        Returns:
            Euclidean distance from initial position, or 0 if object not found.
        """
        if obj not in self.objects or obj not in self.initial_objects:
            return 0.0
        
        current = self.objects[obj]
        initial = self.initial_objects[obj]
        
        dx = current[0] - initial[0]
        dy = current[1] - initial[1]
        dz = current[2] - initial[2]
        
        return math.sqrt(dx**2 + dy**2 + dz**2)
    
    def get_critical_relationships(self):
        """Get the subset of critical 'On' relationships that form the stack.
        
        For a stack of blocks On(1,0), On(2,1), On(3,2), On(4,3), this returns
        all 'On' relationships that involve numbered blocks.
        
        Returns:
            Set of critical relationship strings.
        """
        critical = set()
        
        for rel in self.relationships:
            if rel.startswith('On('):
                # Parse to check if both are numbered blocks
                parts = rel[3:-1].split(',')
                if len(parts) == 2:
                    obj_a = parts[0].strip()
                    obj_b = parts[1].strip()
                    
                    # Check if both are numbered (like '1', '2', '3', '4')
                    if obj_a.isdigit() and (obj_b.isdigit() or obj_b == '0'):
                        critical.add(rel)
        
        return critical
    
    def __repr__(self):
        """String representation of the state."""
        return (f"StateManager(objects={len(self.objects)}, "
                f"relationships={len(self.relationships)}, "
                f"intervened={len(self.intervened_objects)})")