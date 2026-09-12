from typing import Any, Dict, List

from environment import Environment
from state_manager import StateManager


class Executor:
    """
    Executes a multi-step plan using the Environment and StateManager.

    Each step is executed in order. The result of every step is recorded,
    allowing the system to track successful and failed execution.
    """

    def __init__(self, environment: Environment):
        self.environment = environment
        self.state_manager = StateManager(environment)

        self.execution_history: List[Dict[str, Any]] = []

    def execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute one step from a plan.

        Expected step format:

        {
            "action": "purchase",
            "params": {
                "item": "laptop",
                "quantity": 10,
                "location": "warehouse"
            }
        }
        """

        action = step.get("action")
        params = step.get("params", {})

        if not action:
            result = {
                "status": "failure",
                "error": "Step does not contain an action.",
            }

            self.execution_history.append(result)
            return result

        if not isinstance(params, dict):
            result = {
                "action": action,
                "status": "failure",
                "error": "Step parameters must be a dictionary.",
            }

            self.execution_history.append(result)
            return result

        # Execute through StateManager.
        result = self.state_manager.execute_action(
            action,
            **params,
        )

        execution_result = {
            "step": step,
            "action": action,
            "status": result.get("status", "unknown"),
            "result": result,
            "state": self.state_manager.get_current_state(),
        }

        self.execution_history.append(execution_result)

        return execution_result

    def execute_plan(self, plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute a complete multi-step plan sequentially.

        Execution stops when a step fails.

        Returns a complete execution report.
        """

        results = []

        for index, step in enumerate(plan, start=1):
            result = self.execute_step(step)

            result["step_number"] = index
            results.append(result)

            # Stop execution if a step fails.
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
        """Return the history of execution results."""
        return self.execution_history.copy()

    def get_state(self) -> Dict[str, Any]:
        """Return the current environment state."""
        return self.state_manager.get_current_state()

    def get_summary(self) -> Dict[str, Any]:
        """Return an execution summary."""
        return self.state_manager.get_summary()


if __name__ == "__main__":
    # Create the environment.
    env = Environment()

    # Create the executor.
    executor = Executor(env)

    # Example multi-step plan.
    plan = [
        {
            "action": "purchase",
            "params": {
                "item": "laptop",
                "quantity": 10,
                "location": "warehouse",
            },
        },
        {
            "action": "transfer",
            "params": {
                "item": "laptop",
                "quantity": 3,
                "source": "warehouse",
                "destination": "store",
            },
        },
        {
            "action": "reroute",
            "params": {
                "item": "laptop",
                "quantity": 2,
                "from_location": "store",
                "to_location": "office",
            },
        },
    ]

    print("=== EXECUTING PLAN ===")

    result = executor.execute_plan(plan)

    print(result)

    print("\n=== FINAL STATE ===")
    print(executor.get_state())

    print("\n=== EXECUTION HISTORY ===")
    for entry in executor.get_execution_history():
        print(entry)

    print("\n=== SUMMARY ===")
    print(executor.get_summary())