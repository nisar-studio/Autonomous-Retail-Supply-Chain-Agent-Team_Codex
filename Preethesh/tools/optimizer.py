from typing import Any

from Preethesh.tools.interfaces import ToolInterface


class Optimizer(ToolInterface):
    """Selects the best feasible recovery alternative."""

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        operation = kwargs.get("operation")

        if operation == "select":
            return self.select_best(
                goal=kwargs["goal"],
                alternatives=kwargs["alternatives"],
            )

        raise ValueError(f"Unknown optimizer operation: {operation}")

    def select_best(
        self,
        goal: dict[str, Any],
        alternatives: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Select the best feasible alternative."""

        if not alternatives:
            raise ValueError("No alternatives available.")

        feasible = [
            alternative
            for alternative in alternatives
            if alternative.get("feasible", True)
        ]

        if not feasible:
            raise ValueError("No feasible alternatives available.")

        budget = goal.get("budget")
        deadline = goal.get("deadline")

        valid = []

        for alternative in feasible:
            cost = alternative.get("total_cost")
            delivery_time = alternative.get("delivery_time")

            if budget is not None and cost is not None and cost > budget:
                continue

            if deadline is not None and delivery_time is not None:
                if delivery_time > deadline:
                    continue

            valid.append(alternative)

        if not valid:
            raise ValueError("No alternatives satisfy the recovery constraints.")

        return min(
            valid,
            key=lambda alternative: (
                alternative.get("total_cost", float("inf")),
                alternative.get("delivery_time", float("inf")),
                alternative.get("carbon_emission", float("inf")),
            ),
        )