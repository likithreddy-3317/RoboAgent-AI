# Project Plan

## Problem
Order fulfilment requires coordinated order understanding, inventory checks, task planning, robot assignment, route planning, execution, monitoring, and recovery.

## Objectives
- Parse natural-language orders into validated structured data.
- Check stock and locations.
- Create traceable tasks and allocate robots above a battery threshold.
- Calculate routes with Dijkstra's algorithm.
- Simulate robot actions and detect incomplete tasks.
- Re-plan after simulated failures and save JSON reports.

## Success criteria
- Valid structured order produced.
- Stock shortages surfaced before picking.
- Each task has a robot assignment and route when feasible.
- Injected failure is recorded and triggers re-planning.
- A JSON report is saved for each run.

## Future work
SQLite persistence, task batching, unit tests for agent workflow, ROS 2/Gazebo adapter, sensor-driven monitoring, and approval checkpoints.
