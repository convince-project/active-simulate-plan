Tutorials
=========

This page provides tutorials for using ACTIVE-PLAN to identify and resolve unknown anomalies through causal intervention planning.

ACTIVE-PLAN
-----------

Quick Start
~~~~~~~~~~~

Running Scenario 1: Block Misalignment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The simplest way to get started is to run the block stacking misalignment scenario:

.. code-block:: bash

   cd src/active-plan/identification
   python3 mcts.py

When prompted, select scenario 1:

.. code-block:: text

   Select scenario (1-3, or press Enter for scenario1): 1

The planner will run Monte Carlo Tree Search to find a sequence of interventions that aligns all blocks with the base block.

Understanding the Output
^^^^^^^^^^^^^^^^^^^^^^^^

The MCTS planner will print progress as it searches:

.. code-block:: text

   [DEBUG] Initial alignment state (all vs Object 0):
     Obj 1 vs 0: x_diff=0.0000, y_diff=0.0100, aligned=False
     Obj 2 vs 0: x_diff=0.0200, y_diff=0.0000, aligned=False
     Obj 3 vs 0: x_diff=0.0250, y_diff=0.0000, aligned=False
     Obj 4 vs 0: x_diff=0.0100, y_diff=0.0000, aligned=False

   Starting MCTS with 96 possible root actions

   --- Iteration 0 ---
   [ITER 0] reward=0.250, depth=1, interventions=[('1', 'forward,0.01')]
   
   --- Iteration 237 ---
   [ITER 237] reward=1.000, depth=4, interventions=[('1', 'forward,0.01'), ...]
   
   Success! Found solution at iteration 237

Once complete, you'll see the final intervention sequence:

.. code-block:: text

   ============================================================
   RESULTS
   ============================================================
   
   Final intervention sequence (4 steps):
     1. Object '1': forward,0.01
     2. Object '2': left,0.02
     3. Object '3': right,0.025
     4. Object '4': left,0.01
   
   Total iterations: 237
   Results saved to: results_scenario1.json

Interpreting Results
^^^^^^^^^^^^^^^^^^^^

**Reward Values:**

* ``0.0`` - No objects aligned
* ``0.25`` - 1 object aligned with base
* ``0.50`` - 2 objects aligned
* ``0.75`` - 3 objects aligned  
* ``1.00`` - All objects aligned (success!)

**Interventions Format:**

Each intervention is a tuple ``(object_id, action)``:

* ``object_id``: The block to manipulate (``'1'``, ``'2'``, ``'3'``, ``'4'``)
* ``action``: Direction and magnitude (e.g., ``'left,0.02'`` means shift 0.02m left)

Configuration
~~~~~~~~~~~~~

Scenario Configuration Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Scenarios are defined in JSON files located in ``config/``:

* ``scenario1.json`` - Block misalignment problem
* ``scenario2.json`` - (To be implemented)
* ``scenario3.json`` - (To be implemented)
* ``symbolic_state.json`` - Initial object positions and relationships

Modifying Initial State
^^^^^^^^^^^^^^^^^^^^^^^

Edit ``config/symbolic_state.json`` to change object positions:

.. code-block:: json

   {
     "objects": {
       "0": [0.970, 1.308, 0.857],
       "1": [0.970, 1.298, 0.916],
       "2": [0.990, 1.308, 0.975],
       "3": [0.945, 1.308, 1.034],
       "4": [0.980, 1.308, 1.093]
     },
     "relationships": [
       "On(1, 0)",
       "On(2, 1)",
       "On(3, 2)",
       "On(4, 3)"
     ]
   }

Each object has ``[x, y, z]`` coordinates in meters. The ``relationships`` define symbolic predicates describing the scene structure.

Modifying Intervention Space
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Edit the ``intv_space`` section of a scenario file to change available actions:

.. code-block:: json

   {
     "intv_space": {
       "1": [
         "left,0.005", "left,0.01", "left,0.02",
         "right,0.005", "right,0.01", "right,0.02",
         "forward,0.005", "forward,0.01", "forward,0.02",
         "back,0.005", "back,0.01", "back,0.02"
       ]
     }
   }

Each action follows the format ``direction,magnitude`` where:

* Direction: ``left``, ``right``, ``forward``, ``back``
* Magnitude: Distance in meters (e.g., ``0.01`` = 1cm)

Advanced Usage
~~~~~~~~~~~~~~

Tuning MCTS Parameters
^^^^^^^^^^^^^^^^^^^^^^

Key parameters that affect search performance:

**Exploration Constant** (``exploration_constant``)

Controls the exploration-exploitation trade-off in the UCT formula:

.. code-block:: python

   planner = CausalMCTS(
       ...,
       exploration_constant=0.1  # Lower = more exploitation
   )

* ``0.5`` - High exploration (slower, more thorough)
* ``0.1`` - Balanced (recommended for Scenario 1)
* ``0.01-0.05`` - Low exploration (faster, greedy search)
* ``0.0`` - Pure exploitation (fastest for convex problems)

**Typical performance:**

* ``C=0.5``: ~4000 iterations to solution
* ``C=0.1``: ~600 iterations  
* ``C=0.01``: ~200 iterations

**Max Rollout Depth** (``max_rollout_depth``)

Maximum number of interventions to try in a single rollout:

.. code-block:: json

   {
     "max_rollout_depth": 4
   }

Set this based on expected solution complexity. For Scenario 1 with 4 objects, depth 4 is appropriate.

**Termination Threshold** (``termination_threshold``)

Reward value that indicates success:

.. code-block:: json

   {
     "termination_threshold": 1.0
   }

For Scenario 1: ``1.0`` means all 4 objects aligned (4 x 0.25).

**Alignment Threshold** (``alignment_threshold``)

Maximum position error (in meters) to consider objects aligned:

.. code-block:: python

   state_mgr = StateManager(
       initial_state, 
       alignment_threshold=0.005  # 5mm tolerance
   )

Smaller values require more precise alignment.

Reward Shaping
^^^^^^^^^^^^^^

Modify reward shaping to guide search behavior:

.. code-block:: json

   {
     "reward_shaping": {
       "shift_bonus": 0.05,
       "depth_penalty": 0.02
     }
   }

* ``shift_bonus``: Immediate reward for each action (encourages exploration)
* ``depth_penalty``: Penalty per intervention (encourages shorter solutions)

**Sparse vs. Dense Rewards:**

* **Sparse** (``shift_bonus=0.0``): Only reward complete solutions (slower search)
* **Dense** (``shift_bonus=0.05``): Reward incremental progress (faster convergence)

For problems with monotonic reward landscapes (like Scenario 1), dense rewards provide valuable gradient information.

Running Multiple Scenarios
^^^^^^^^^^^^^^^^^^^^^^^^^^^

To run a different scenario:

.. code-block:: bash

   python3 mcts.py
   # When prompted:
   Select scenario (1-3, or press Enter for scenario1): 2

Or modify the default in ``mcts.py``:

.. code-block:: python

   scenario_name = scenario_map.get(choice, 'scenario2')  # Change default

Analyzing Results
^^^^^^^^^^^^^^^^^

The planner saves detailed results to ``results_scenario1.json``:

.. code-block:: json

   {
     "scenario": "scenario1",
     "interventions": [
       ["1", "forward,0.01"],
       ["2", "left,0.02"],
       ["3", "right,0.025"],
       ["4", "left,0.01"]
     ],
     "iterations": 237,
     "total_rollouts": 238,
     "goal_achieved": true
   }

Use this output to:

* Verify the solution achieves the goal
* Analyze search efficiency (iterations needed)
* Compare different parameter configurations


SIMULATE-PLAN
-------------

This section provides tutorials for using SIMULATE-PLAN to generate recovery plans using PDDL-based symbolic planning for blocks identified as geometrically misaligned by ACTIVE-PLAN.

Quick Start
~~~~~~~~~~~

Running Recovery Planning
^^^^^^^^^^^^^^^^^^^^^^^^^

After running ACTIVE-PLAN to identify misaligned blocks, use SIMULATE-PLAN to generate a recovery plan:

.. code-block:: bash

   cd src/simulate-plan/recovery
   python3 planner.py

When prompted, select the same scenario you used with ACTIVE-PLAN:

.. code-block:: text

   Select scenario (1-3, or press Enter for scenario1): 1

The planner will generate a PDDL problem, execute Fast Downward, and display the recovery plan.

Understanding the Output
^^^^^^^^^^^^^^^^^^^^^^^^

The planner will show progress as it works:

.. code-block:: text

   Loading scenario1...
   [planner] Loaded MCTS results: 4 objects need correction
   [planner] Target objects: ['2', '4', '1', '3']
   [planner] Wrote problem: fd_output/problem.pddl
   [planner] Running Fast Downward...
   [planner] Plan generated: fd_output/sas_plan

Once complete, you'll see the recovery action sequence:

.. code-block:: text

   ============================================================
   RECOVERY PLAN
   ============================================================
   
   Action sequence (10 steps):
     1. unstack D C
     2. putdown-to-table D
     3. unstack C B
     4. stack C D
     5. unstack B A
     6. stack-target B A
     7. unstack C D
     8. stack-target C B
     9. pickup-from-table D
     10. stack-target D C
   
   Plan saved to: fd_output/plan_scenario1.json

Interpreting the Plan
^^^^^^^^^^^^^^^^^^^^^

**Action Types:**

* ``unstack X Y`` - Pick up block X from block Y
* ``pickup-from-table X`` - Pick up block X from the table
* ``putdown-to-table X`` - Place held block X on the table
* ``stack X Y`` - Place held block X on block Y (normal placement)
* ``stack-target X Y`` - Place held block X on block Y with **precise geometric alignment**

**The Target Trick:**

Notice that some actions use ``stack-target`` instead of ``stack``. These are the blocks that ACTIVE-PLAN identified as geometrically misaligned. The ``stack-target`` action ensures precise placement that corrects the geometric misalignment, even though the symbolic relationship ``On(X,Y)`` may already be satisfied.

This is the "Target Trick" - a symbolic proxy for geometric precision that bridges ACTIVE-PLAN's geometric reasoning with SIMULATE-PLAN's symbolic planning.

Configuration
~~~~~~~~~~~~~

PDDL Domain Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^

The PDDL domain is defined in ``domains/domain_s1.pddl`` and includes:

**Predicates:**

.. code-block:: text

   (On ?x - block ?y - block)        # Block X is on block Y
   (OnTable ?x - block)              # Block X is on the table
   (Clear ?x - block)                # Block X has nothing on top
   (Holding ?x - block)              # Robot is holding block X
   (HandEmpty)                       # Robot hand is empty
   (TargetOn ?x - block ?y - block)  # X needs precise placement on Y
   (AtTarget ?x - block)             # X has been precisely placed

**Key Actions:**

The domain includes standard blocksworld actions (``unstack``, ``stack``, ``pickup-from-table``, ``putdown-to-table``) plus the special ``stack-target`` action:

.. code-block:: text

   (:action stack-target
     :parameters (?x - block ?y - block)
     :precondition (and (Holding ?x) (Clear ?y) (TargetOn ?x ?y))
     :effect (and (On ?x ?y) (Clear ?x) (HandEmpty)
                  (not (Holding ?x)) (not (Clear ?y))
                  (AtTarget ?x)))

The ``stack-target`` action requires ``TargetOn(?x, ?y)`` to be true and achieves ``AtTarget(?x)``, which is required in the goal for misaligned blocks.

Integration with ACTIVE-PLAN
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Workflow Overview
^^^^^^^^^^^^^^^^^

The complete pipeline consists of two stages:

1. **ACTIVE-PLAN (Identification):**
   
   - Runs MCTS to identify which blocks are geometrically misaligned
   - Saves intervention sequence to ``results_scenario1.json``
   - Each intervention identifies an object needing geometric correction

2. **SIMULATE-PLAN (Recovery):**
   
   - Reads MCTS results to identify target objects
   - Generates PDDL problem with Target Trick predicates
   - Runs Fast Downward to find optimal action sequence
   - Outputs executable recovery plan

Data Flow Between Modules
^^^^^^^^^^^^^^^^^^^^^^^^^^

**Input to SIMULATE-PLAN:**

.. code-block:: json

   {
     "scenario": "scenario1",
     "interventions": [
       ["1", "forward,0.01"],
       ["2", "left,0.02"],
       ["3", "right,0.025"],
       ["4", "left,0.01"]
     ],
     "goal_achieved": true
   }

The ``interventions`` list identifies which objects need geometric correction (objects 1, 2, 3, 4 in this example).

**PDDL Problem Generation:**

For each object in the interventions list:

1. Add ``(TargetOn X Y)`` to initial state → marks "needs precise placement"
2. Add ``(AtTarget X)`` to goal state → requires precise placement

**Output from SIMULATE-PLAN:**

.. code-block:: json

   [
     {"action": "unstack", "args": ["D", "C"]},
     {"action": "putdown-to-table", "args": ["D"]},
     {"action": "unstack", "args": ["C", "B"]},
     {"action": "stack-target", "args": ["C", "B"]},
     ...
   ]

This plan can be executed by a robot controller to physically correct the misalignments.

Advanced Usage
~~~~~~~~~~~~~~

Understanding the Target Trick
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Problem:** MCTS identifies geometric misalignments that are invisible to pure symbolic reasoning.

Example:

* Current state: ``On(B, A)`` is symbolically true, but Block B is 2cm misaligned
* Goal state: ``On(B, A)`` is required
* A pure symbolic planner sees: initial state = goal state → no action needed!

**Solution:** The Target Trick creates a symbolic gap:

1. For misaligned Block B, add to initial state:
   
   .. code-block:: text
   
      (On B A)        # Symbolic relationship already satisfied
      (TargetOn B A)  # But needs precise placement

2. For misaligned Block B, add to goal state:
   
   .. code-block:: text
   
      (On B A)        # Symbolic relationship must be maintained
      (AtTarget B)    # Must be precisely placed

3. Now the planner sees:
   
   * Initial: ``On(B,A)`` TRUE, ``TargetOn(B,A)`` True, ``AtTarget(B)`` FALSE
   * Goal: ``On(B,A)`` required, ``AtTarget(B)`` required
   * Gap: Need to achieve ``AtTarget(B)``
   * Solution: Use ``stack-target`` to achieve ``AtTarget(B)``

This forces the planner to unstack B and use ``stack-target`` to place it precisely, even though ``On(B,A)`` is already symbolically satisfied.

Modifying the Domain
^^^^^^^^^^^^^^^^^^^^

To add new action types or scenarios, edit ``domains/domain_s1.pddl``.

Example: Adding a ``slide`` action for lateral adjustments without unstacking:

.. code-block:: text

   (:action slide
     :parameters (?x - block ?y - block)
     :precondition (and (On ?x ?y) (Clear ?x) (TargetOn ?x ?y))
     :effect (AtTarget ?x))

This action allows correcting misalignments without full disassembly, potentially generating shorter plans.

Analyzing Plan Quality
^^^^^^^^^^^^^^^^^^^^^^

Compare plan metrics across different configurations:

* **Plan length:** Number of actions (shorter is usually better)
* **Execution time:** Fast Downward search time
* **Optimality:** Is the plan cost-optimal?

Fast Downward uses A* with landmark cut heuristic (``lmcut()``) by default, which guarantees optimal plans.

To use a faster but potentially suboptimal planner, modify ``planner.py``:

.. code-block:: python

   cmd = [
       sys.executable, str(fd_script),
       str(domain_path), str(problem_path),
       "--search", "astar(blind())"  # Faster, may not be optimal
   ]

Troubleshooting
~~~~~~~~~~~~~~~

No Plan Found
^^^^^^^^^^^^^

If Fast Downward fails to find a plan:

1. **Check PDDL problem:** View ``fd_output/problem.pddl`` to verify:
   
   * Initial state includes current configuration
   * Goal state is achievable
   * All blocks are declared as objects

2. **Check goal consistency:** Ensure goal state in ``scenario1.json`` matches the physical configuration

3. **Verify Fast Downward installation:** Test Fast Downward directly:
   
   .. code-block:: bash
   
      cd simulate-plan/downward
      ./fast-downward.py --help

Incorrect Target Objects
^^^^^^^^^^^^^^^^^^^^^^^^^

If wrong blocks are marked for precise placement:

1. **Verify ACTIVE-PLAN results:** Check ``results_scenario1.json`` to ensure correct interventions
2. **Check scenario configuration:** Ensure ``symbolic_goal`` matches intended final configuration
3. **Re-run ACTIVE-PLAN:** If MCTS didn't identify the right objects, tune search parameters

Integration Issues
^^^^^^^^^^^^^^^^^^

If SIMULATE-PLAN can't find ACTIVE-PLAN files:

1. **Check directory structure:** Verify paths in ``planner.py`` match your setup
2. **Run from correct location:** Execute from ``src/simulate-plan/recovery/``
3. **Verify scenario files exist:** Ensure ``config/scenario1.json`` and ``results_scenario1.json`` are present