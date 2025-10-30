Tutorials
=========

This page provides tutorials for using ACTIVE-PLAN to identify and resolve unknown anomalies through causal intervention planning.

Quick Start
-----------

Running Scenario 1: Block Misalignment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The simplest way to get started is to run the block stacking misalignment scenario:

.. code-block:: bash

   cd src/active-plan/identification
   python3 mcts.py

When prompted, select scenario 1:

.. code-block:: text

   Select scenario (1-3, or press Enter for scenario1): 1

The planner will run Monte Carlo Tree Search to find a sequence of interventions that aligns all blocks with the base block.

Understanding the Output
~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~

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
-------------

Scenario Configuration Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Scenarios are defined in JSON files located in ``config/``:

* ``scenario1.json`` - Block misalignment problem
* ``scenario2.json`` - (To be implemented)
* ``scenario3.json`` - (To be implemented)
* ``symbolic_state.json`` - Initial object positions and relationships

Modifying Initial State
~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
--------------

Tuning MCTS Parameters
~~~~~~~~~~~~~~~~~~~~~~

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

For Scenario 1: ``1.0`` means all 4 objects aligned (4 × 0.25).

**Alignment Threshold** (``alignment_threshold``)

Maximum position error (in meters) to consider objects aligned:

.. code-block:: python

   state_mgr = StateManager(
       initial_state, 
       alignment_threshold=0.005  # 5mm tolerance
   )

Smaller values require more precise alignment.

Reward Shaping
~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~

To run a different scenario:

.. code-block:: bash

   python3 mcts.py
   # When prompted:
   Select scenario (1-3, or press Enter for scenario1): 2

Or modify the default in ``mcts.py``:

.. code-block:: python

   scenario_name = scenario_map.get(choice, 'scenario2')  # Change default

Analyzing Results
~~~~~~~~~~~~~~~~~

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

