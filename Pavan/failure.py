from typing import Any, Dict, List

from executor import Executor
from environment import Environment


class FailureHandler:
    """
    Simulates execution failures and handles recovery.

    Responsibilities:
    - Simulate failures
    - Detect failed execution
    - Trigger recovery
    - Indicate when replanning is required
    """

    def __init__(self, executor: Executor):
        self.executor = executor

        self.failure_history: List[Dict[str, Any]] = []

    def simulate_failure(
        self,
        failure_type: str,
        message: str = "",
    ) -> Dict[str, Any]:
        """
        Simulate a failure during execution.

        Examples of failure types:
        - inventory_unavailable
        - transport_failure
        - location_unavailable
        - unknown
        """

        failure = {
            "status": "failure",
            "failure_type": failure_type,
            "message": message or f"Simulated {failure_type}.",
            "replan_required": True,
        }

        self.failure_history.append(failure)

        return failure

    def handle_failure(
        self,
        failure: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Handle a failure and determine the appropriate recovery action.
        """

        failure_type = failure.get("failure_type", "unknown")

        if failure_type == "inventory_unavailable":
            recovery = "Find another inventory source."

        elif failure_type == "transport_failure":
            recovery = "Use an alternative transport route."

        elif failure_type == "location_unavailable":
            recovery = "Reroute to another available location."

        else:
            recovery = "Request a new plan from the planning/controller layer."

        result = {
            "status": "failure",
            "failure_type": failure_type,
            "recovery_action": recovery,
            "replan_required": True,
        }

        self.failure_history.append(result)

        return result

    def execute_with_failure_check(
        self,
        plan: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Execute a plan and check whether a failure occurs.

        If execution fails, a replanning trigger is returned.
        """

        result = self.executor.execute_plan(plan)

        if result.get("status") == "failure":
            failure = {
                "failure_type": "execution_failure",
                "message": result.get(
                    "message",
                    "A step failed during execution.",
                ),
            }

            self.failure_history.append(failure)

            return {
                "status": "failure",
                "execution_result": result,
                "replan_required": True,
                "replanning_trigger": {
                    "reason": failure["message"],
                    "action": "request_new_plan",
                },
            }

        return {
            "status": "success",
            "execution_result": result,
            "replan_required": False,
        }

    def get_failure_history(self) -> List[Dict[str, Any]]:
        """Return all recorded failures."""
        return self.failure_history.copy()

    def requires_replanning(self) -> bool:
        """Return True if any recorded failure requires replanning."""

        return any(
            failure.get("replan_required", False)
            for failure in self.failure_history
        )


if __name__ == "__main__":
    # Create the environment.
    env = Environment()

    # Create the executor.
    executor = Executor(env)

    # Create the failure handler.
    failure_handler = FailureHandler(executor)

    print("=== FAILURE SIMULATION ===")

    failure = failure_handler.simulate_failure(
        "transport_failure",
        "Truck became unavailable.",
    )

    print(failure)

    print("\n=== FAILURE HANDLING ===")

    recovery = failure_handler.handle_failure(failure)

    print(recovery)

    print("\n=== REPLANNING CHECK ===")

    print(
        "Replanning required:",
        failure_handler.requires_replanning(),
    )

    print("\n=== EXECUTION WITH FAILURE CHECK ===")

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

    result = failure_handler.execute_with_failure_check(plan)

    print(result)

    print("\n=== FAILURE HISTORY ===")
    print(failure_handler.get_failure_history())