# ACTIVE-SIMULATE-PLAN

This repo contains the source code for ACTIVE-SIMULATE-PLAN, a simulation-free implementation of Monte Carlo Tree Search (MCTS) for finding sequences of causal interventions that transform an initial symbolic state into a goal state for unknown anomalies.

## Installation

ACTIVE-SIMULATE-PLAN has been tested on Ubuntu 22.04 LTS with Python 3.10.

### Dependencies

ACTIVE-SIMULATE-PLAN uses only Python standard library modules and requires **no external dependencies**:

* `math` - Mathematical operations
* `random` - Random rollout policy
* `json` - Configuration and state file parsing
* `pathlib` - File path handling
* `copy` - State copying during simulation

# ACTIVE-PLAN

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

ACTIVE-PLAN will execute MCTS to find a sequence of interventions that achieves the goal state.

## Running Examples

Upon running `mcts.py`, the system will:

1. Load the scenario configuration from `config/scenario1.json`
2. Load the initial symbolic state from `config/symbolic_state.json`
3. Execute MCTS search to identify corrective interventions
4. Save results to `results_scenario1.json`


# SIMULATE-PLAN

## Architecture
TODO

### Quick Start
Clone the repository and run:

```bash
cd src/simulate-plan/recovery
python3 planner.py
```

When prompted, select a scenario (default is Scenario 1):

```text
Select scenario (1-3, or press Enter for scenario1): 1
```
SIMULATE-PLAN executes Fast-Downward using the interventions (`mcts.py`)  to find a sequence of actions that reaches the goal state, and then output the plan.

## Running Examples

Upon running `planner.py`, the system will:

1. Load the initial state `active-plan/config/symbolic_state.json` 
2. Load the goal state `active-plan/config/scenario1.json`
3. Load the intervention (output from mcts.py)  `identification/results_scenario1.json`
4. Execute the plan using Fast-Downwards [add citation]
5. Save results to `plan_scenario_1.json`

## API and Tutorials

The documentation for ACTIVE-SIMULATE-PLAN can be found [here](https://convince-project.github.io/active-simulate-plan), where you can read more about the API and find tutorials.

## Maintainer

This repository is maintained by:

| | | |
|:---:|:---:|:---:|
| Yazz Warsame | [yazz](https://github.com/yazzwarsame) | [yazzwarsame@gmail.com](mailto:yazzwarsame@gmail.com) |

