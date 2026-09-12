from copy import deepcopy
from typing import Any, Dict, List, Optional

from environment import Environment


class StateManager:
    """
    Manages execution state and state history for the Environment.

    Responsibilities:
    - Track state before and after each action
    - Record successful and failed actions
    - Detect state changes
    - Maintain state history
    - Restore the previous state when required
    - Provide an execution summary
    """

    def __init__(self, environment: Environment):
        self.environment = environment

        # Store an independent snapshot of the initial state.
        self.current_state = deepcopy(environment.get_state())

        # Every entry represents one state snapshot.
        self.state_history: List[Dict[str, Any]] = [
            deepcopy(self.current_state)
        ]

        # Record details of every executed action.
        self.action_history: List[Dict[str, Any]] = []

    def execute_action(self, action: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute an action through the Environment and track state changes.

        Supported actions:
        - purchase
        - transfer
        - reroute
        """

        supported_actions = {
            "purchase",
            "transfer",
            "reroute",
        }

        if action not in supported_actions:
            result = {
                "action": action,
                "status": "failure",
                "error": f"Unsupported action: {action}",
            }

            self.action_history.append(
                {
                    "action": action,
                    "status": "failure",
                    "state_changed": False,
                    "result": result,
                }
            )

            return result

        # Save the state before execution.
        state_before = deepcopy(self.environment.get_state())

        try:
            # Get the corresponding method from Environment.
            environment_method = getattr(self.environment, action)

            # Execute the action.
            result = environment_method(**kwargs)

            # Get the state after execution.
            state_after = deepcopy(self.environment.get_state())

            # Check whether the state actually changed.
            state_changed = state_before != state_after

            # Update current state.
            self.current_state = deepcopy(state_after)

            # Save the new state snapshot.
            self.state_history.append(deepcopy(state_after))

            # Record execution details.
            self.action_history.append(
                {
                    "action": action,
                    "status": result.get("status", "unknown"),
                    "state_changed": state_changed,
                    "state_before": deepcopy(state_before),
                    "state_after": deepcopy(state_after),
                    "result": deepcopy(result),
                }
            )

            return result

        except Exception as exc:
            # Keep the system running even if an unexpected error occurs.
            state_after = deepcopy(self.environment.get_state())

            self.current_state = deepcopy(state_after)

            result = {
                "action": action,
                "status": "failure",
                "error": str(exc),
            }

            self.action_history.append(
                {
                    "action": action,
                    "status": "failure",
                    "state_changed": state_before != state_after,
                    "state_before": deepcopy(state_before),
                    "state_after": deepcopy(state_after),
                    "result": deepcopy(result),
                }
            )

            return result

    def get_current_state(self) -> Dict[str, Any]:
        """Return an independent copy of the current state."""
        return deepcopy(self.current_state)

    def get_latest_state(self) -> Dict[str, Any]:
        """Return the most recent state snapshot."""
        if not self.state_history:
            return {}

        return deepcopy(self.state_history[-1])

    def get_state_history(self) -> List[Dict[str, Any]]:
        """Return all recorded state snapshots."""
        return deepcopy(self.state_history)

    def get_action_history(self) -> List[Dict[str, Any]]:
        """Return the history of executed actions."""
        return deepcopy(self.action_history)

    def has_state_changed(self) -> bool:
        """
        Check whether the current state differs from the initial state.
        """
        if not self.state_history:
            return False

        return self.current_state != self.state_history[0]

    def restore_previous_state(self) -> bool:
        """
        Restore the Environment to the state before the most recent action.

        Returns:
            True if restoration was successful, otherwise False.
        """

        if len(self.state_history) < 2:
            return False

        # The previous snapshot is the second-last snapshot.
        previous_state = deepcopy(self.state_history[-2])

        try:
            # Restore the Environment state.
            self.environment.state = deepcopy(previous_state)

            # Update StateManager's state.
            self.current_state = deepcopy(previous_state)

            # Remove the latest state snapshot.
            self.state_history.pop()

            # Record the restoration as an internal state operation.
            self.action_history.append(
                {
                    "action": "restore_previous_state",
                    "status": "success",
                    "state_changed": True,
                    "state_after": deepcopy(previous_state),
                }
            )

            return True

        except Exception:
            return False

    def get_summary(self) -> Dict[str, Any]:
        """
        Return a summary of execution activity.
        """

        total_actions = len(self.action_history)

        successful_actions = sum(
            1
            for entry in self.action_history
            if entry.get("status") == "success"
        )

        failed_actions = sum(
            1
            for entry in self.action_history
            if entry.get("status") == "failure"
        )

        state_changes = sum(
            1
            for entry in self.action_history
            if entry.get("state_changed") is True
        )

        return {
            "total_actions": total_actions,
            "successful_actions": successful_actions,
            "failed_actions": failed_actions,
            "state_changes": state_changes,
            "current_state": self.get_current_state(),
        }


if __name__ == "__main__":
    # Create the environment.
    env = Environment()

    # Create the state manager.
    manager = StateManager(env)

    print("=== PURCHASE ===")
    result = manager.execute_action(
        "purchase",
        item="laptop",
        quantity=10,
        location="warehouse",
    )
    print(result)

    print("\n=== TRANSFER ===")
    result = manager.execute_action(
        "transfer",
        item="laptop",
        quantity=3,
        source="warehouse",
        destination="store",
    )
    print(result)

    print("\n=== REROUTE ===")
    result = manager.execute_action(
        "reroute",
        item="laptop",
        quantity=2,
        from_location="store",
        to_location="office",
    )
    print(result)

    print("\n=== FAILED TRANSFER ===")
    result = manager.execute_action(
        "transfer",
        item="laptop",
        quantity=100,
        source="store",
        destination="office",
    )
    print(result)

    print("\n=== CURRENT STATE ===")
    print(manager.get_current_state())

    print("\n=== STATE HISTORY ===")
    for index, state in enumerate(manager.get_state_history()):
        print(f"State {index}: {state}")

    print("\n=== SUMMARY ===")
    print(manager.get_summary())