# ACTIVE-SIMULATE-PLAN

This repo contains the source code for ACTIVE-SIMULATE-PLAN, a simulation-free implementation of Monte Carlo Tree Search (MCTS) for finding sequences of causal interventions that transform an initial symbolic state into a goal state for unknown anomalies.

## Installation

ACTIVE-SIMULATE-PLAN has been tested on Ubuntu 22.04 LTS with Python 3.10.

# ACTIVE-PLAN

ACTIVE-PLAN identifies anomalies by applying causal interventions with Monte Carlo Tree Search (MCTS) to run “what-if” analyses.

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

### Dependencies

ACTIVE-PLAN uses only Python standard library modules and requires **no external dependencies**:

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

ACTIVE-PLAN will execute MCTS to find a sequence of interventions that achieves the goal state.

## Running Examples

Upon running `mcts.py`, the system will:

1. Load the scenario configuration from `config/scenario1.json`
2. Load the initial symbolic state from `config/symbolic_state.json`
3. Execute MCTS search to identify corrective interventions
4. Save results to `results_scenario1.json`


# SIMULATE-PLAN

SIMULATE-PLAN uses PDDL planning to generate recovery actions for geometrically misaligned blocks identified by MCTS.

## Architecture
```
src/simulate-plan/
└── recovery/
    ├── planner.py           # PDDL recovery planner
    ├── pddl_builder.py      # PDDL problem generator 
    ├── plan_parser.py       # Fast Downward output parser
    └── domains/
        └── domain_s1.pddl   # PDDL domain for block stacking
```

## Dependencies

SIMULATE-PLAN uses only Python standard library modules:

* `json` - State and configuration parsing
* `sys` - System operations
* `subprocess` - Fast Downward execution
* `pathlib` - File path handling
* `re` - Pattern matching for plan parsing

**External Dependency:**

* [Fast Downward](https://github.com/aibasel/downward) - Classical PDDL planner

### Installing Fast Downward
```bash
# Clone Fast Downward
git clone https://github.com/aibasel/downward.git
cd downward

# Build the planner
./build.py

# Place in simulate-plan directory
mv downward /path/to/active-simulate-plan/src/simulate-plan/
```

**Citation:** Helmert, M. (2006). The Fast Downward Planning System. *Journal of Artificial Intelligence Research*, 26, 191-246.

## Quick Start
```bash
cd src/simulate-plan/recovery
python3 planner.py
```

When prompted, select a scenario (default is Scenario 1):
```text
Select scenario (1-3, or press Enter for scenario1): 1
```

## Running Examples

Upon running `planner.py`, the system will:

1. Load the initial state from `active-plan/config/symbolic_state.json`
2. Load the goal state from `active-plan/config/scenario1.json`
3. Load MCTS interventions from `active-plan/identification/results_scenario1.json`
4. Generate PDDL problem with target predicates for misaligned blocks
5. Execute Fast Downward planner to find optimal action sequence
6. Parse and display the recovery plan
7. Save results to `fd_output/plan_scenario1.json`

## API and Tutorials

The documentation for ACTIVE-SIMULATE-PLAN can be found [here](https://convince-project.github.io/active-simulate-plan), where you can read more about the API and find tutorials.

## Maintainer

This repository is maintained by:

| | | |
|:---:|:---:|:---:|
| Yazz Warsame | [yazz](https://github.com/yazzwarsame) | [yazzwarsame@gmail.com](mailto:yazzwarsame@gmail.com) |

