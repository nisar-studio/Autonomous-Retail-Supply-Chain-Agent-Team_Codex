from typing import Any, Dict, Tuple


class Environment:
    """
    Simulation environment for the autonomous retail supply-chain agent.

    Supports:
    - Purchase
    - Transfer
    - Reroute
    - Allocation
    - Inventory management
    - Item location tracking
    - Execution history
    - Controlled state changes
    """

    def __init__(self):
        self.state: Dict[str, Any] = {
            "inventory": {},
            "locations": {},
            "balances": {},
            "allocations": {},
        }

        self.history = []

    # ------------------------------------------------------------------
    # STATE
    # ------------------------------------------------------------------

    def get_state(self) -> Dict[str, Any]:
        """Return the current environment state."""
        return self.state

    # ------------------------------------------------------------------
    # ITEM LOCATION
    # ------------------------------------------------------------------

    def set_item_location(
        self,
        item: str,
        location: str
    ) -> Dict[str, Any]:
        """
        Set the current operational location of an item.

        Both item and location are required.
        """
        if not item:
            raise ValueError("item is required")

        if not location:
            raise ValueError("location is required")

        self.state["locations"][item] = location

        return {
            "status": "success",
            "item": item,
            "location": location,
        }

    def get_item_location(self, item: str) -> Any:
        """Return the current location of an item."""
        return self.state["locations"].get(item)

    # ------------------------------------------------------------------
    # INVENTORY
    # ------------------------------------------------------------------

    def get_inventory(
        self,
        item: str,
        location: str
    ) -> float:
        """Return inventory quantity for an item at a location."""
        return self.state["inventory"].get(
            (item, location),
            0
        )

    def set_inventory(
        self,
        item: str,
        location: str,
        quantity: float
    ) -> None:
        """Set inventory quantity for an item at a location."""
        self.state["inventory"][(item, location)] = quantity

    def add_inventory(
        self,
        item: str,
        location: str,
        quantity: float
    ) -> None:
        """Add inventory quantity."""
        current = self.get_inventory(item, location)

        self.set_inventory(
            item,
            location,
            current + quantity
        )

    # ------------------------------------------------------------------
    # PURCHASE
    # ------------------------------------------------------------------

    def purchase(
        self,
        item: str,
        quantity: float,
        location: str
    ) -> Dict[str, Any]:
        """
        Purchase inventory and place it at a location.
        """

        if not item:
            result = {
                "action": "purchase",
                "status": "failure",
                "error": "Item is required.",
            }

            self.history.append(result)
            return result

        if not location:
            result = {
                "action": "purchase",
                "status": "failure",
                "error": "Location is required.",
            }

            self.history.append(result)
            return result

        if quantity <= 0:
            result = {
                "action": "purchase",
                "status": "failure",
                "error": "Quantity must be greater than zero.",
            }

            self.history.append(result)
            return result

        # Add purchased inventory
        self.add_inventory(
            item,
            location,
            quantity
        )

        # Update latest operational location
        self.state["locations"][item] = location

        # Execution metrics
        result = {
            "action": "purchase",
            "status": "success",
            "item": item,
            "quantity": quantity,
            "location": location,
            "delivered_quantity": quantity,
            "delivery_time": 24.0,
            "total_cost": round(100.0 * quantity, 2),
            "carbon_emission": round(0.5 * quantity, 2),
        }

        self.history.append(result)

        return result

    # ------------------------------------------------------------------
    # TRANSFER
    # ------------------------------------------------------------------

    def transfer(
        self,
        item: str,
        quantity: float,
        source: str,
        destination: str
    ) -> Dict[str, Any]:
        """
        Transfer inventory from one location to another.
        """

        if not item:
            result = {
                "action": "transfer",
                "status": "failure",
                "error": "Item is required.",
            }

            self.history.append(result)
            return result

        if quantity <= 0:
            result = {
                "action": "transfer",
                "status": "failure",
                "error": "Quantity must be greater than zero.",
            }

            self.history.append(result)
            return result

        if not source:
            result = {
                "action": "transfer",
                "status": "failure",
                "error": "Source location is required.",
            }

            self.history.append(result)
            return result

        if not destination:
            result = {
                "action": "transfer",
                "status": "failure",
                "error": "Destination location is required.",
            }

            self.history.append(result)
            return result

        available = self.get_inventory(
            item,
            source
        )

        if available < quantity:
            result = {
                "action": "transfer",
                "status": "failure",
                "error": "Insufficient inventory at source.",
                "item": item,
                "quantity": quantity,
                "source": source,
                "destination": destination,
            }

            self.history.append(result)
            return result

        # Remove from source
        self.set_inventory(
            item,
            source,
            available - quantity
        )

        # Add to destination
        self.add_inventory(
            item,
            destination,
            quantity
        )

        # Update latest operational location
        self.state["locations"][item] = destination

        result = {
            "action": "transfer",
            "status": "success",
            "item": item,
            "quantity": quantity,
            "source": source,
            "destination": destination,
            "delivered_quantity": quantity,
            "delivery_time": 4.0,
            "total_cost": round(20.0 * quantity, 2),
            "carbon_emission": round(0.2 * quantity, 2),
        }

        self.history.append(result)

        return result

    # ------------------------------------------------------------------
    # REROUTE
    # ------------------------------------------------------------------

    def reroute(
        self,
        item: str,
        quantity: float,
        source: str,
        destination: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Reroute inventory from one location to another.

        Supports both:
            source / destination

        and:
            from_location / to_location

        This keeps compatibility with the Executor / SelectedAction flow.
        """

        # Compatibility with Executor's parameter names
        if not source:
            source = kwargs.get("from_location")

        if not destination:
            destination = kwargs.get("to_location")

        if not item:
            result = {
                "action": "reroute",
                "status": "failure",
                "error": "Item is required.",
            }

            self.history.append(result)
            return result

        if quantity <= 0:
            result = {
                "action": "reroute",
                "status": "failure",
                "error": "Quantity must be greater than zero.",
            }

            self.history.append(result)
            return result

        if not source:
            result = {
                "action": "reroute",
                "status": "failure",
                "error": "Source location is required.",
            }

            self.history.append(result)
            return result

        if not destination:
            result = {
                "action": "reroute",
                "status": "failure",
                "error": "Destination location is required.",
            }

            self.history.append(result)
            return result

        available = self.get_inventory(
            item,
            source
        )

        if available < quantity:
            result = {
                "action": "reroute",
                "status": "failure",
                "error": "Insufficient inventory at source.",
                "item": item,
                "quantity": quantity,
                "source": source,
                "destination": destination,
            }

            self.history.append(result)
            return result

        # Remove from source
        self.set_inventory(
            item,
            source,
            available - quantity
        )

        # Add to destination
        self.add_inventory(
            item,
            destination,
            quantity
        )

        # Update latest operational location
        self.state["locations"][item] = destination

        result = {
            "action": "reroute",
            "status": "success",
            "item": item,
            "quantity": quantity,
            "source": source,
            "destination": destination,
            "delivered_quantity": quantity,
            "delivery_time": 6.0,
            "total_cost": round(30.0 * quantity, 2),
            "carbon_emission": round(0.3 * quantity, 2),
        }

        self.history.append(result)

        return result

    # ------------------------------------------------------------------
    # ALLOCATION
    # ------------------------------------------------------------------

    def allocate(
        self,
        item: str,
        quantity: float,
        location: str
    ) -> Dict[str, Any]:
        """
        Reserve inventory for allocation.

        Allocation does not remove the inventory.
        It records the reserved quantity separately.
        """

        if not item:
            result = {
                "action": "allocation",
                "status": "failure",
                "error": "Item is required.",
            }

            self.history.append(result)
            return result

        if quantity <= 0:
            result = {
                "action": "allocation",
                "status": "failure",
                "error": "Quantity must be greater than zero.",
            }

            self.history.append(result)
            return result

        if not location:
            result = {
                "action": "allocation",
                "status": "failure",
                "error": "Location is required.",
            }

            self.history.append(result)
            return result

        available = self.get_inventory(
            item,
            location
        )

        if available < quantity:
            result = {
                "action": "allocation",
                "status": "failure",
                "error": "Insufficient inventory for allocation.",
                "item": item,
                "quantity": quantity,
                "location": location,
            }

            self.history.append(result)
            return result

        key: Tuple[str, str] = (
            item,
            location
        )

        current_allocation = self.state[
            "allocations"
        ].get(key, 0)

        self.state["allocations"][key] = (
            current_allocation + quantity
        )

        result = {
            "action": "allocation",
            "status": "success",
            "item": item,
            "quantity": quantity,
            "location": location,
            "allocated_quantity": quantity,
            "total_allocated": self.state["allocations"][key],

        }

        self.history.append(result)

        return result

    # ------------------------------------------------------------------
    # GENERIC ACTION EXECUTION
    # ------------------------------------------------------------------

    def execute_action(
        self,
        action: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute an action using the environment.

        Supported actions:
        - purchase
        - transfer
        - reroute
        - allocation
        """

        if action == "purchase":
            return self.purchase(
                item=params.get("item"),
                quantity=params.get("quantity", 0),
                location=params.get("location"),
            )

        if action == "transfer":
            return self.transfer(
                item=params.get("item"),
                quantity=params.get("quantity", 0),
                source=params.get("source"),
                destination=params.get("destination"),
            )

        if action == "reroute":
            return self.reroute(
                item=params.get("item"),
                quantity=params.get("quantity", 0),
                source=params.get(
                    "source",
                    params.get("from_location")
                ),
                destination=params.get(
                    "destination",
                    params.get("to_location")
                ),
            )

        if action == "allocation":
            return self.allocate(
                item=params.get("item"),
                quantity=params.get("quantity", 0),
                location=params.get("location"),
            )

        result = {
            "action": action,
            "status": "failure",
            "error": f"Unsupported action: {action}",
        }

        self.history.append(result)

        return result

    # ------------------------------------------------------------------
    # HISTORY
    # ------------------------------------------------------------------

    def get_history(self):
        """Return all execution history."""
        return self.history

    def clear_history(self) -> None:
        """Clear execution history."""
        self.history.clear()