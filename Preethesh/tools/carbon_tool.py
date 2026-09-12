from typing import Any

from Preethesh.tools.interfaces import ToolInterface


class CarbonTool(ToolInterface):
    """Tool for calculating simulated transport cost and carbon emissions."""

    def execute(self, **kwargs: Any) -> Any:
        operation = kwargs.get("operation")

        if operation == "calculate_cost":
            return self.calculate_cost(
                quantity=kwargs["quantity"],
                cost_per_unit=kwargs["cost_per_unit"],
            )

        if operation == "calculate_carbon":
            return self.calculate_carbon(
                quantity=kwargs["quantity"],
                carbon_per_unit=kwargs["carbon_per_unit"],
            )

        raise ValueError(f"Unknown carbon operation: {operation}")

    def calculate_cost(
        self,
        quantity: int,
        cost_per_unit: float,
    ) -> float:
        """Calculate total cost for a quantity."""
        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")
        if cost_per_unit < 0:
            raise ValueError("Cost per unit cannot be negative.")

        return quantity * cost_per_unit

    def calculate_carbon(
        self,
        quantity: int,
        carbon_per_unit: float,
    ) -> float:
        """Calculate total carbon emissions in kg CO2e."""
        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")
        if carbon_per_unit < 0:
            raise ValueError("Carbon per unit cannot be negative.")

        return quantity * carbon_per_unit