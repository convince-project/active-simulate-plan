# ACTIVE-SIMULATE-PLAN

This repo contains the source code for ACTIVE-SIMULATE-PLAN, a simulation-free implementation of Monte Carlo Tree Search (MCTS) for finding sequences of causal interventions that transform an initial symbolic state into a goal state for unknown anomalies.

## Architecture

```
src/active-plan/
└── identification/
    ├── mcts.py                # Core MCTS algorithm
    ├── state_manager.py       # Symbolic state tracking and updates
    ├── interventions.py       # Intervention parsing and application
    ├── reward_shaper.py       # Reward computation
   

config/
├── scenario1.json             # Block misalignment scenario
├── scenario2.json             # (to be added)
├── scenario3.json             # (to be added)
└── symbolic_state.json        # Initial world state
```

## Installation

ACTIVE-SIMULATE-PLAN has been tested on Ubuntu 22.04 LTS with Python 3.10.

### Dependencies

ACTIVE-SIMULATE-PLAN uses only Python standard library modules and requires **no external dependencies**:

* `math` - Mathematical operations
* `random` - Random rollout policy
* `json` - Configuration and state file parsing
* `pathlib` - File path handling
* `copy` - State copying during simulation

### Quick Start

Clone the repository and run:

```bash
cd src/active-plan/identification
python3 mcts.py
```

When prompted, select a scenario (default is Scenario 1):

```text
Select scenario (1-3, or press Enter for scenario1): 1
```

The planner will execute MCTS to find a sequence of interventions that achieves the goal state.

## Running Examples

Upon running `mcts.py`, the system will:

1. Load the scenario configuration from `config/scenario1.json`
2. Load the initial symbolic state from `config/symbolic_state.json`
3. Execute MCTS search to identify corrective interventions
4. Save results to `results_scenario1.json`

Example output:

```text
============================================================
RESULTS
============================================================

Final intervention sequence (4 steps):
  1. Object '1': forward,0.01
  2. Object '2': left,0.02
  3. Object '3': right,0.025
  4. Object '4': left,0.01

Total iterations: 237
Total rollouts evaluated: 238
Results saved to: results_scenario1.json
```

## API and Tutorials

The documentation for ACTIVE-SIMULATE-PLAN can be found [here](https://convince-project.github.io/active-simulate-plan), where you can read more about the API and find tutorials.


## Configuration

Scenarios and initial states are defined in JSON files in the `config/` directory.

### Scenario Files

Each scenario file (e.g., `scenario1.json`) defines:

* **Intervention space**: Available actions for each object
* **Symbolic goal**: Target relationships to achieve
* **Reward shaping**: Parameters for guiding search
* **Search parameters**: Max depth, termination threshold, alignment tolerance

Example:

```json
{
  "intv_space": {
    "1": ["left,0.01", "right,0.01", "forward,0.01", "back,0.01"]
  },
  "symbolic_goal": ["On(2,1)", "On(3,2)", "On(4,3)"],
  "reward_shaping": {
    "shift_bonus": 0.05,
    "depth_penalty": 0.02
  },
  "termination_threshold": 1.0,
  "max_rollout_depth": 4
}
```

### Symbolic State Files

The `symbolic_state.json` file defines the initial scene:

* **Objects**: Position of each object as [x, y, z] coordinates in meters
* **Relationships**: Symbolic predicates describing the scene (e.g., `On(A,B)`)

Example:

```json
{
  "objects": {
    "0": [0.970, 1.308, 0.857],
    "1": [0.970, 1.298, 0.916]
  },
  "relationships": ["On(1, 0)"]
}
```

## Features

* **Simulation-free**: Operates purely on symbolic state updates and geometric checks
* **Configurable**: JSON-based scenario and state definitions
* **Modular**: Clean separation between MCTS, state management, and interventions
* **Extensible**: Easy to add new intervention types and reward functions
* **Documented**: Comprehensive API documentation with Google-style docstrings

## Project Status

**Current Implementation:**

* Scenario 1: Block misalignment identification and correction
* Scenario 2: In development
* Scenario 3: In development

**Planned Features:**

* GPU-parallelized MCTS for faster search
* Integration with physics simulation (Isaac Lab)
* TAMP-based recovery planning
* Real robot execution interface


