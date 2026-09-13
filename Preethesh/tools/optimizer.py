from typing import Any, Callable, Mapping

from Preethesh.tools.interfaces import ToolInterface


class Optimizer(ToolInterface):
    """Generates, evaluates, scores, and selects recovery alternatives."""

    def __init__(
        self,
        cost_calculator: Callable[[dict[str, Any]], float] | None = None,
        delivery_time_calculator: Callable[[dict[str, Any]], float] | None = None,
        carbon_calculator: Callable[[dict[str, Any]], float] | None = None,
    ) -> None:
        self._cost_calculator = cost_calculator
        self._delivery_time_calculator = delivery_time_calculator
        self._carbon_calculator = carbon_calculator

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        operation = kwargs.get("operation")

        if operation == "select":
            return self.select_best(
                goal=kwargs["goal"],
                alternatives=kwargs["alternatives"],
            )

        if operation == "optimize":
            return self.optimize(
                goal=kwargs["goal"],
                alternatives=kwargs["alternatives"],
            )

        raise ValueError(f"Unknown optimizer operation: {operation}")

    def optimize(
        self,
        goal: Mapping[str, Any],
        alternatives: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Run the complete evaluation workflow and select the best option."""

        evaluated = self.evaluate_alternatives(alternatives)
        return self.select_best(goal=dict(goal), alternatives=evaluated)

    def evaluate_alternatives(
        self,
        alternatives: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Remove infeasible options and calculate available evaluation metrics."""

        if not alternatives:
            raise ValueError("No alternatives available.")

        evaluated: list[dict[str, Any]] = []

        for original in alternatives:
            alternative = dict(original)

            if alternative.get("feasible", True) is False:
                continue

            if "total_cost" not in alternative and self._cost_calculator:
                alternative["total_cost"] = self._cost_calculator(alternative)

            if "delivery_time" not in alternative and self._delivery_time_calculator:
                alternative["delivery_time"] = self._delivery_time_calculator(
                    alternative
                )

            if "carbon_emission" not in alternative and self._carbon_calculator:
                alternative["carbon_emission"] = self._carbon_calculator(alternative)

            evaluated.append(alternative)

        if not evaluated:
            raise ValueError("No feasible alternatives available.")

        return evaluated

    def select_best(
        self,
        goal: dict[str, Any],
        alternatives: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Select the best feasible alternative within recovery constraints."""

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