from copy import deepcopy
from typing import Any, Dict, List

from environment import Environment


class StateManager:

    def __init__(
        self,
        environment: Environment
    ):

        self.environment = environment

        self.current_state = deepcopy(
            environment.get_state()
        )

        self.state_history: List[
            Dict[str, Any]
        ] = [
            deepcopy(self.current_state)
        ]

        self.action_history: List[
            Dict[str, Any]
        ] = []

    # =========================================================
    # EXECUTE ACTION
    # =========================================================

    def execute_action(
        self,
        action: str,
        **kwargs
    ) -> Dict[str, Any]:

        supported_actions = {
            "purchase",
            "transfer",
            "reroute",
            "allocation",
        }

        if action not in supported_actions:

            result = {
                "action": action,
                "status": "failure",
                "error": (
                    f"Unsupported action: {action}"
                ),
            }

            self.action_history.append(
                result
            )

            return result

        # Save state before action
        state_before = deepcopy(
            self.environment.get_state()
        )

        try:

            # Environment method for allocation
            # is called "allocate".
            environment_action = (
                "allocate"
                if action == "allocation"
                else action
            )

            environment_method = getattr(
                self.environment,
                environment_action
            )

            result = environment_method(
                **kwargs
            )

            # Save state after action
            state_after = deepcopy(
                self.environment.get_state()
            )

            state_changed = (
                state_before != state_after
            )

            self.current_state = deepcopy(
                state_after
            )

            self.state_history.append(
                deepcopy(state_after)
            )

            self.action_history.append({

                "action": action,

                "status": result.get(
                    "status",
                    "unknown"
                ),

                "state_changed": state_changed,

                "state_before": deepcopy(
                    state_before
                ),

                "state_after": deepcopy(
                    state_after
                ),

                "result": deepcopy(
                    result
                ),
            })

            return result

        except Exception as exc:

            result = {
                "action": action,
                "status": "failure",
                "error": str(exc),
            }

            self.action_history.append(
                result
            )

            return result

    # =========================================================
    # CURRENT STATE
    # =========================================================

    def get_current_state(
        self
    ) -> Dict[str, Any]:

        return deepcopy(
            self.current_state
        )

    def get_latest_state(
        self
    ) -> Dict[str, Any]:

        return self.get_current_state()

    # =========================================================
    # STATE HISTORY
    # =========================================================

    def get_state_history(
        self
    ) -> List[Dict[str, Any]]:

        return deepcopy(
            self.state_history
        )

    # =========================================================
    # ACTION HISTORY
    # =========================================================

    def get_action_history(
        self
    ) -> List[Dict[str, Any]]:

        return deepcopy(
            self.action_history
        )

    # =========================================================
    # STATE CHANGE CHECK
    # =========================================================

    def has_state_changed(
        self
    ) -> bool:

        if len(self.state_history) < 2:

            return False

        return (
            self.state_history[-1]
            != self.state_history[-2]
        )

    # =========================================================
    # RESTORE PREVIOUS STATE
    # =========================================================

    def restore_previous_state(
        self
    ) -> Dict[str, Any]:

        if len(self.state_history) < 2:

            return self.get_current_state()

        previous_state = deepcopy(
            self.state_history[-2]
        )

        self.environment.state = deepcopy(
            previous_state
        )

        self.current_state = deepcopy(
            previous_state
        )

        self.state_history.append(
            deepcopy(previous_state)
        )

        return self.get_current_state()

    # =========================================================
    # SUMMARY
    # =========================================================

    def get_summary(
        self
    ) -> Dict[str, Any]:

        return {
            "current_state": (
                self.get_current_state()
            ),
            "number_of_actions": len(
                self.action_history
            ),
            "number_of_state_snapshots": len(
                self.state_history
            ),
        }