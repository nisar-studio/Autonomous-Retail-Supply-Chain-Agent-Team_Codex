from typing import Any, Dict, List

from environment import Environment
from state_manager import StateManager


class Executor:

    # =========================================================
    # NISAR -> PAVAN ACTION MAPPING
    # =========================================================

    ACTION_MAP = {

        ("order", "create"):
            "purchase",

        ("inventory", "transfer"):
            "transfer",

        ("inventory", "reroute"):
            "reroute",

        ("inventory", "allocate"):
            "allocation",
    }

    SUPPORTED_ACTIONS = {
        "purchase",
        "transfer",
        "reroute",
        "allocation",
    }

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def __init__(
        self,
        environment: Environment
    ):

        self.environment = environment

        self.state_manager = StateManager(
            environment
        )

        self.execution_history: List[
            Dict[str, Any]
        ] = []

    # =========================================================
    # EXECUTE ONE STEP
    # =========================================================

    def execute_step(
        self,
        step: Dict[str, Any]
    ) -> Dict[str, Any]:

        action_id = step.get(
            "action_id"
        )

        action = step.get(
            "action"
        )

        params = step.get(
            "params",
            {}
        )

        # -----------------------------------------------------
        # Validate action
        # -----------------------------------------------------

        if not action:

            result = {
                "action_id": action_id,
                "step": step,
                "status": "failure",
                "error": (
                    "Step does not contain an action."
                ),
            }

            self.execution_history.append(
                result
            )

            return result

        if action not in self.SUPPORTED_ACTIONS:

            result = {
                "action_id": action_id,
                "step": step,
                "action": action,
                "status": "failure",
                "error": (
                    f"Unsupported action: {action}"
                ),
            }

            self.execution_history.append(
                result
            )

            return result

        # -----------------------------------------------------
        # Validate parameters
        # -----------------------------------------------------

        if not isinstance(
            params,
            dict
        ):

            result = {
                "action_id": action_id,
                "step": step,
                "action": action,
                "status": "failure",
                "error": (
                    "Step parameters must be "
                    "a dictionary."
                ),
            }

            self.execution_history.append(
                result
            )

            return result

        # -----------------------------------------------------
        # Execute through StateManager
        # -----------------------------------------------------

        result = (
            self.state_manager
            .execute_action(
                action,
                **params
            )
        )

        # -----------------------------------------------------
        # Build execution result
        # -----------------------------------------------------

        execution_result = {

            "action_id": action_id,

            "step": step,

            "action": action,

            "status": result.get(
                "status",
                "unknown"
            ),

            "result": result,

            "state": (
                self.state_manager
                .get_current_state()
            ),
        }

        self.execution_history.append(
            execution_result
        )

        return execution_result

    # =========================================================
    # EXECUTE ALLOCATION
    # =========================================================

    def execute_allocation(
        self,
        action_id: str,
        item: str,
        quantity: float,
        location: str
    ) -> Dict[str, Any]:

        step = {

            "action_id": action_id,

            "action": "allocation",

            "params": {

                "item": item,

                "quantity": quantity,

                "location": location,
            },
        }

        return self.execute_step(
            step
        )

    # =========================================================
    # EXECUTE SELECTED ACTION
    # =========================================================

    def execute_selected_action(
        self,
        selected_action: Dict[str, Any]
    ) -> Dict[str, Any]:

        action_id = selected_action.get(
            "action_id"
        )

        tool = selected_action.get(
            "tool"
        )

        operation = selected_action.get(
            "operation"
        )

        parameters = selected_action.get(
            "parameters",
            {}
        )

        # Convert Nisar's tool/operation
        # into Pavan's internal action.
        action = self.ACTION_MAP.get(
            (
                tool,
                operation
            )
        )

        if not action:

            return {
                "action_id": action_id,
                "status": "failure",
                "error": (
                    "Unsupported selected action: "
                    f"{tool}/{operation}"
                ),
            }

        step = {

            "action_id": action_id,

            "action": action,

            "params": parameters,
        }

        return self.execute_step(
            step
        )

    # =========================================================
    # EXECUTE COMPLETE PLAN
    # =========================================================

    def execute_plan(
        self,
        plan: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        results = []

        for index, step in enumerate(
            plan,
            start=1
        ):

            result = self.execute_step(
                step
            )

            result["step_number"] = index

            results.append(
                result
            )

            # Stop execution immediately
            # when one step fails.
            if result.get(
                "status"
            ) == "failure":

                return {

                    "status": "failure",

                    "completed_steps": (
                        index - 1
                    ),

                    "total_steps": len(
                        plan
                    ),

                    "results": results,

                    "state": (
                        self.state_manager
                        .get_current_state()
                    ),

                    "message": (
                        f"Execution stopped "
                        f"at step {index}."
                    ),
                }

        return {

            "status": "success",

            "completed_steps": len(
                plan
            ),

            "total_steps": len(
                plan
            ),

            "results": results,

            "state": (
                self.state_manager
                .get_current_state()
            ),

            "message": (
                "All steps executed successfully."
            ),
        }

    # =========================================================
    # EXECUTION HISTORY
    # =========================================================

    def get_execution_history(
        self
    ) -> List[Dict[str, Any]]:

        return self.execution_history.copy()

    # =========================================================
    # STATE
    # =========================================================

    def get_state(
        self
    ) -> Dict[str, Any]:

        return (
            self.state_manager
            .get_current_state()
        )

    # =========================================================
    # SUMMARY
    # =========================================================

    def get_summary(
        self
    ) -> Dict[str, Any]:

        return (
            self.state_manager
            .get_summary()
        )