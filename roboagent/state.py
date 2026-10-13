from typing import Any, TypedDict

class RoboState(TypedDict, total=False):
    raw_order: str
    order: dict[str, Any]
    inventory_check: dict[str, Any]
    tasks: list[dict[str, Any]]
    robot_assignments: list[dict[str, Any]]
    routes: list[dict[str, Any]]
    execution_log: list[str]
    robot_status: dict[str, dict[str, Any]]
    issues: list[str]
    replanned: bool
    final_report: dict[str, Any]
