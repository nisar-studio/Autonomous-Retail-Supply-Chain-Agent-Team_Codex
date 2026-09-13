from typing import Any, Dict, List

from executor import Executor
from environment import Environment


class FailureHandler:

    # ---------------------------------------------------------
    # Failure types required by Pavan Role PDF
    # ---------------------------------------------------------

    SUPPORTED_FAILURES = {
        "vendor_unavailable",
        "route_unavailable",
        "inventory_changed",
        "shipment_delayed",
        "demand_increased",

        # Backward-compatible failure types
        "inventory_unavailable",
        "transport_failure",
        "location_unavailable",
        "execution_failure",
        "unknown",
    }

    # ---------------------------------------------------------
    # INITIALIZATION
    # ---------------------------------------------------------

    def __init__(self, executor: Executor):

        self.executor = executor

        self.environment = executor.environment

        self.failure_history: List[
            Dict[str, Any]
        ] = []

        # Controlled failure waiting to affect execution
        self.active_failure: Dict[str, Any] | None = None

    # =========================================================
    # SIMULATE CONTROLLED FAILURE
    # =========================================================

    def simulate_failure(
        self,
        failure_type: str,
        message: str = ""
    ) -> Dict[str, Any]:

        # -----------------------------------------------------
        # Validate failure type
        # -----------------------------------------------------

        if failure_type not in self.SUPPORTED_FAILURES:

            failure_type = "unknown"

        # -----------------------------------------------------
        # Default messages
        # -----------------------------------------------------

        default_messages = {

            "vendor_unavailable":
                "Vendor became unavailable before execution.",

            "route_unavailable":
                "Route became unavailable before execution.",

            "inventory_changed":
                "Inventory changed before execution.",

            "shipment_delayed":
                "Shipment was delayed before execution.",

            "demand_increased":
                "Demand increased before execution.",

            "inventory_unavailable":
                "Inventory is unavailable.",

            "transport_failure":
                "Transport failed.",

            "location_unavailable":
                "Location is unavailable.",

            "execution_failure":
                "Execution failed.",

            "unknown":
                "An unknown failure occurred.",
        }

        failure = {

            "status": "failure",

            "failure_type": failure_type,

            "message": (
                message
                or default_messages.get(
                    failure_type,
                    "Simulated failure."
                )
            ),

            "replan_required": True,

            "controlled": True,
        }

        # -----------------------------------------------------
        # Store as active controlled failure
        # -----------------------------------------------------

        self.active_failure = failure

        self.failure_history.append(
            failure.copy()
        )

        return failure

    # =========================================================
    # APPLY CONTROLLED CONDITION CHANGE
    # =========================================================

    def apply_condition_change(
        self,
        failure_type: str,
        **kwargs
    ) -> Dict[str, Any]:

        """
        Applies a controlled environmental change.

        This is used to demonstrate changing conditions
        before an action is executed.
        """

        # -----------------------------------------------------
        # Vendor unavailable
        # -----------------------------------------------------

        if failure_type == "vendor_unavailable":

            vendor_id = kwargs.get(
                "vendor_id",
                kwargs.get("supplier_id")
            )

            if "vendors" not in self.environment.state:

                self.environment.state["vendors"] = {}

            if vendor_id:

                self.environment.state[
                    "vendors"
                ][vendor_id] = {
                    "available": False
                }

            return {
                "status": "success",
                "failure_type": failure_type,
                "condition_changed": True,
                "vendor_id": vendor_id,
                "available": False,
            }

        # -----------------------------------------------------
        # Route unavailable
        # -----------------------------------------------------

        if failure_type == "route_unavailable":

            route_id = kwargs.get(
                "route_id",
                kwargs.get("route")
            )

            if "routes" not in self.environment.state:

                self.environment.state["routes"] = {}

            if route_id:

                self.environment.state[
                    "routes"
                ][route_id] = {
                    "available": False
                }

            return {
                "status": "success",
                "failure_type": failure_type,
                "condition_changed": True,
                "route_id": route_id,
                "available": False,
            }

        # -----------------------------------------------------
        # Inventory changed
        # -----------------------------------------------------

        if failure_type == "inventory_changed":

            item = kwargs.get("item")
            location = kwargs.get("location")
            new_quantity = kwargs.get(
                "new_quantity"
            )

            if (
                item is None
                or location is None
                or new_quantity is None
            ):

                return {
                    "status": "failure",
                    "failure_type": failure_type,
                    "message": (
                        "item, location and "
                        "new_quantity are required."
                    ),
                    "condition_changed": False,
                }

            self.environment.state[
                "inventory"
            ][
                (item, location)
            ] = max(
                0,
                new_quantity
            )

            return {
                "status": "success",
                "failure_type": failure_type,
                "condition_changed": True,
                "item": item,
                "location": location,
                "new_quantity": max(
                    0,
                    new_quantity
                ),
            }

        # -----------------------------------------------------
        # Shipment delayed
        # -----------------------------------------------------

        if failure_type == "shipment_delayed":

            shipment_id = kwargs.get(
                "shipment_id",
                "shipment_1"
            )

            delay_hours = kwargs.get(
                "delay_hours",
                24
            )

            if "shipments" not in self.environment.state:

                self.environment.state[
                    "shipments"
                ] = {}

            self.environment.state[
                "shipments"
            ][shipment_id] = {

                "status": "delayed",

                "delay_hours": delay_hours,
            }

            return {
                "status": "success",
                "failure_type": failure_type,
                "condition_changed": True,
                "shipment_id": shipment_id,
                "delay_hours": delay_hours,
            }

        # -----------------------------------------------------
        # Demand increased
        # -----------------------------------------------------

        if failure_type == "demand_increased":

            item = kwargs.get("item")

            increased_quantity = kwargs.get(
                "increased_quantity",
                kwargs.get("quantity", 1)
            )

            if "demand" not in self.environment.state:

                self.environment.state[
                    "demand"
                ] = {}

            current_demand = self.environment.state[
                "demand"
            ].get(
                item,
                0
            )

            self.environment.state[
                "demand"
            ][item] = (
                current_demand
                + increased_quantity
            )

            return {
                "status": "success",
                "failure_type": failure_type,
                "condition_changed": True,
                "item": item,
                "new_demand": self.environment.state[
                    "demand"
                ][item],
            }

        return {
            "status": "success",
            "failure_type": failure_type,
            "condition_changed": False,
        }

    # =========================================================
    # HANDLE FAILURE
    # =========================================================

    def handle_failure(
        self,
        failure: Dict[str, Any]
    ) -> Dict[str, Any]:

        failure_type = failure.get(
            "failure_type",
            "unknown"
        )

        # -----------------------------------------------------
        # Recovery recommendations
        # -----------------------------------------------------

        recovery_actions = {

            "vendor_unavailable":
                "Find another available vendor.",

            "route_unavailable":
                "Use an alternative available route.",

            "inventory_changed":
                "Find another inventory source.",

            "shipment_delayed":
                "Use an alternative shipment or route.",

            "demand_increased":
                "Create a new plan for the increased demand.",

            "inventory_unavailable":
                "Find another inventory source.",

            "transport_failure":
                "Use an alternative transport route.",

            "location_unavailable":
                "Reroute to another available location.",

            "execution_failure":
                "Request a new plan after execution failure.",

            "unknown":
                "Request a new plan from the planning/controller layer.",
        }

        recovery = recovery_actions.get(
            failure_type,
            recovery_actions["unknown"]
        )

        result = {

            "status": "failure",

            "failure_type": failure_type,

            "recovery_action": recovery,

            "replan_required": True,
        }

        self.failure_history.append(
            result.copy()
        )

        return result

    # =========================================================
    # EXECUTE WITH FAILURE CHECK
    # =========================================================

    def execute_with_failure_check(
        self,
        plan
    ) -> Dict[str, Any]:

        # -----------------------------------------------------
        # If a controlled failure was activated,
        # make the execution fail before normal execution.
        # -----------------------------------------------------

        if self.active_failure:

            failure = self.active_failure

            failure_type = failure.get(
                "failure_type",
                "unknown"
            )

            failed_step = (
                plan[0]
                if isinstance(plan, list)
                and plan
                else plan
            )

            execution_result = {

                "status": "failure",

                "success": False,

                "message": failure.get(
                    "message",
                    "Controlled failure occurred."
                ),

                "failure_reason": failure_type,

                "results": [
                    {
                        "action_id": (
                            failed_step.get(
                                "action_id"
                            )
                            if isinstance(
                                failed_step,
                                dict
                            )
                            else None
                        ),

                        "status": "failure",

                        "failure_type":
                            failure_type,

                        "message":
                            failure.get(
                                "message"
                            ),
                    }
                ],
            }

            # Clear active failure so that
            # the next replanned attempt can execute.
            self.active_failure = None

            recorded_failure = {

                "status": "failure",

                "failure_type":
                    failure_type,

                "message":
                    failure.get(
                        "message"
                    ),

                "failed_step":
                    failed_step,

                "replan_required": True,
            }

            self.failure_history.append(
                recorded_failure
            )

            return {

                "status": "failure",

                "execution_result":
                    execution_result,

                "failure":
                    recorded_failure,

                "replan_required":
                    True,

                "replanning_trigger": {

                    "reason":
                        failure.get(
                            "message"
                        ),

                    "action":
                        "request_new_plan",

                    "failed_step":
                        failed_step,
                },
            }

        # -----------------------------------------------------
        # Normal execution
        # -----------------------------------------------------

        execution_result = (
            self.executor.execute_plan(
                plan
            )
        )

        # -----------------------------------------------------
        # Normal execution failed
        # -----------------------------------------------------

        if execution_result.get(
            "status"
        ) == "failure":

            failed_step = None

            for result in execution_result.get(
                "results",
                []
            ):

                if result.get(
                    "status"
                ) == "failure":

                    failed_step = result

                    break

            failure_message = (
                execution_result.get(
                    "message",
                    "A step failed during execution."
                )
            )

            failure = {

                "status": "failure",

                "failure_type":
                    "execution_failure",

                "message":
                    failure_message,

                "failed_step":
                    failed_step,

                "replan_required":
                    True,
            }

            self.failure_history.append(
                failure.copy()
            )

            return {

                "status": "failure",

                "execution_result":
                    execution_result,

                "failure":
                    failure,

                "replan_required":
                    True,

                "replanning_trigger": {

                    "reason":
                        failure_message,

                    "action":
                        "request_new_plan",

                    "failed_step":
                        failed_step,
                },
            }

        # -----------------------------------------------------
        # Successful execution
        # -----------------------------------------------------

        return {

            "status": "success",

            "execution_result":
                execution_result,

            "failure":
                None,

            "replan_required":
                False,

            "replanning_trigger":
                None,
        }

    # =========================================================
    # FAILURE HISTORY
    # =========================================================

    def get_failure_history(
        self
    ) -> List[Dict[str, Any]]:

        return self.failure_history.copy()

    # =========================================================
    # CLEAR FAILURE HISTORY
    # =========================================================

    def clear_failure_history(
        self
    ) -> None:

        self.failure_history.clear()

        self.active_failure = None

    # =========================================================
    # CHECK REPLANNING
    # =========================================================

    def requires_replanning(
        self
    ) -> bool:

        return any(

            failure.get(
                "replan_required",
                False
            )

            for failure
            in self.failure_history
        )


# =============================================================
# STANDALONE TEST
# =============================================================

if __name__ == "__main__":

    environment = Environment()

    executor = Executor(
        environment
    )

    handler = FailureHandler(
        executor
    )

    print(
        "\n--- Controlled Failure Test ---"
    )

    failure = handler.simulate_failure(
        "vendor_unavailable",
        "Vendor A became unavailable."
    )

    print(failure)

    handled = handler.handle_failure(
        failure
    )

    print(
        "\nRecovery:"
    )

    print(handled)

    print(
        "\nFailure History:"
    )

    print(
        handler.get_failure_history()
    )