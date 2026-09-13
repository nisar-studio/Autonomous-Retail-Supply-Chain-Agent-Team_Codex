from typing import Any, Dict, List

from environment import Environment
from state_manager import StateManager


class Executor:
    """
    Executes actions using Environment and StateManager.

    Supports both:
    1. Existing internal step format:
       {
           "action": "purchase",
           "params": {...}
       }

    2. SelectedAction format:
       {
           "action_id": "A001",
           "tool": "order",
           "operation": "create",
           "parameters": {...}
       }
    """

    ACTION_MAP = {
        ("order", "create"): "purchase",
        ("inventory", "transfer"): "transfer",
        ("inventory", "reroute"): "reroute",
    }

    def __init__(self, environment: Environment):
        self.environment = environment
        self.state_manager = StateManager(environment)
        self.execution_history: List[Dict[str, Any]] = []

    def execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an internal Pavan step.
        """

        action = step.get("action")
        params = step.get("params", {})
        action_id = step.get("action_id")

        if not action:
            result = {
                "action_id": action_id,
                "status": "failure",
                "error": "Step does not contain an action.",
            }
            self.execution_history.append(result)
            return result

        if not isinstance(params, dict):
            result = {
                "action_id": action_id,
                "action": action,
                "status": "failure",
                "error": "Step parameters must be a dictionary.",
            }
            self.execution_history.append(result)
            return result

        result = self.state_manager.execute_action(action, **params)

        execution_result = {
            "action_id": action_id,
            "step": step,
            "action": action,
            "status": result.get("status", "unknown"),
            "result": result,
            "state": self.state_manager.get_current_state(),
        }

        self.execution_history.append(execution_result)
        return execution_result

    def execute_selected_action(
        self,
        selected_action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute Nisar's SelectedAction format.

        Example:
        {
            "action_id": "A001",
            "tool": "order",
            "operation": "create",
            "parameters": {
                "item": "laptop",
                "quantity": 10,
                "location": "warehouse"
            }
        }
        """

        action_id = selected_action.get("action_id")
        tool = selected_action.get("tool")
        operation = selected_action.get("operation")
        parameters = selected_action.get("parameters", {})

        if not action_id:
            return {
                "action_id": None,
                "status": "failure",
                "error": "SelectedAction does not contain action_id.",
            }

        if not tool or not operation:
            return {
                "action_id": action_id,
                "status": "failure",
                "error": "SelectedAction must contain tool and operation.",
            }

        if not isinstance(parameters, dict):
            return {
                "action_id": action_id,
                "status": "failure",
                "error": "parameters must be a dictionary.",
            }

        action = self.ACTION_MAP.get((tool, operation))

        if not action:
            return {
                "action_id": action_id,
                "status": "failure",
                "error": f"Unsupported action: {tool}/{operation}",
            }

        step = {
            "action_id": action_id,
            "action": action,
            "params": parameters,
        }

        return self.execute_step(step)

    def execute_plan(self, plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        results = []

        for index, step in enumerate(plan, start=1):
            result = self.execute_step(step)
            result["step_number"] = index
            results.append(result)

            if result.get("status") == "failure":
                return {
                    "status": "failure",
                    "completed_steps": index - 1,
                    "total_steps": len(plan),
                    "results": results,
                    "state": self.state_manager.get_current_state(),
                    "message": f"Execution stopped at step {index}.",
                }

        return {
            "status": "success",
            "completed_steps": len(plan),
            "total_steps": len(plan),
            "results": results,
            "state": self.state_manager.get_current_state(),
            "message": "All steps executed successfully.",
        }

    def get_execution_history(self) -> List[Dict[str, Any]]:
        return self.execution_history.copy()

    def get_state(self) -> Dict[str, Any]:
        return self.state_manager.get_current_state()

    def get_summary(self) -> Dict[str, Any]:
        return self.state_manager.get_summary()