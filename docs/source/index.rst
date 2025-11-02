Welcome to the ACTIVE-SIMULATE-PLAN documentation!
==================================================

Welcome to the documentation of ACTIVE-SIMULATE-PLAN, online tools used for handling unknown anomalies. The input to ACTIVE/SIMULATE-PLAN is current state information and a list of available actions in JSON format. The output is a plan also in JSON format.

Anomalies are detected using SIT-AW. ACTIVE-PLAN focuses on anomaly identification by applying causal interventions with Monte Carlo Tree Search (MCTS) to run "what-if" analyses. SIMULATE-PLAN handles the anomaly recovery by using the information from ACTIVE-PLAN to plan and execute a sequence of actions that returns the system to a valid, goal-achievable state using PDDL planning.

**GitHub Repository:** `active-simulate-plan <https://github.com/convince-project/active-simulate-plan>`_

Quick Links
-----------

* `Fast Downward Planner <http://www.fast-downward.org/>`_ - Required for SIMULATE-PLAN
* `PDDL Resources <https://planning.wiki/>`_ - Learn more about PDDL planning

Contents
--------

.. toctree::
   :maxdepth: 2

   tutorials
   api


