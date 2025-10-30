Welcome to the ACTIVE-PLAN and SIMULATE-PLAN documentation!
============================================================

Welcome to the documentation of ACTIVE-PLAN and SIMULATE-PLAN an online tools used for handling unknown anomalies. The input to ACTIVE/SIMULATE-PLAN is current state information, a list of available actions in JSON format. The output is a plan also in JSON format. 

Anomalies are detected using SIT-AW. ACTIVE-PLAN focus on anomaly identification by applying causal interventions with Monte Carlo Tree Search (MCTS) to run “what-if” analyses. SIMULATE-PLAN handles the anomaly recovery by using the information from ACTIVE-PLAN to plan and execute a sequence of actions that returns the system to a valid, goal-achievable state using Task and Motion Planning (TAMP).


Contents
--------

.. toctree::

   tutorials
   api
