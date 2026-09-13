from typing import Any, Dict


class Environment:
    """
    Simulated supply-chain environment.

    Supports:
    - Purchase
    - Inventory transfer
    - Inventory reroute
    - Inventory allocation
    - Item location management
    - Execution history
    """

    def __init__(self):
        self.state: Dict[str, Any] = {
            "inventory": {},
            "locations": {},
            "balances": {},
            "allocations": {},
        }

        self.history = []

    # ============================================================
    # STATE
    # ============================================================

    def get_state(self) -> Dict[str, Any]:
        """Return the current environment state."""
        return self.state

    # ============================================================
    # ITEM LOCATION
    # ============================================================

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

    def has_item_location(self, item: str) -> bool:
        """Return True if the item has a stored location."""
        return item in self.state["locations"]

    def get_all_item_locations(self) -> Dict[str, str]:
        """Return all item-to-location mappings."""
        return dict(self.state["locations"])

    # ============================================================
    # INVENTORY HELPERS
    # ============================================================

    def get_inventory(
        self,
        item: str,
        location: str
    ) -> int:
        """Return inventory quantity for an item at a location."""
        return self.state["inventory"].get(
            (item, location),
            0
        )

    def set_inventory(
        self,
        item: str,
        location: str,
        quantity: int
    ) -> None:
        """Set inventory quantity."""
        self.state["inventory"][
            (item, location)
        ] = quantity

    def add_inventory(
        self,
        item: str,
        location: str,
        quantity: int
    ) -> None:
        """Add inventory quantity."""
        key = (item, location)

        self.state["inventory"][key] = (
            self.state["inventory"].get(key, 0)
            + quantity
        )

    # ============================================================
    # PURCHASE
    # ============================================================

    def purchase(
        self,
        item: str,
        quantity: int,
        location: str
    ) -> Dict[str, Any]:
        """
        Purchase inventory and place it at a location.
        """

        if not item:
            raise ValueError("item is required")

        # Missing location must return a failure result
        # instead of raising an exception.
        if not location:
            result = {
                "action": "purchase",
                "status": "failure",
                "error": "location is required",
            }

            self.history.append(result)

            return result

        if quantity <= 0:
            result = {
                "action": "purchase",
                "status": "failure",
                "error": (
                    "Quantity must be greater than zero."
                ),
            }

            # Failed actions must also be recorded.
            self.history.append(result)

            return result

        self.add_inventory(
            item,
            location,
            quantity
        )

        self.set_item_location(
            item,
            location
        )

        result = {
            "action": "purchase",
            "status": "success",
            "item": item,
            "quantity": quantity,
            "location": location,

            # Execution metrics
            "delivered_quantity": quantity,
            "delivery_time": 24.0,
            "total_cost": round(
                100.0 * quantity,
                2
            ),
            "carbon_emission": round(
                0.5 * quantity,
                2
            ),
        }

        self.history.append(result)

        return result

    # ============================================================
    # TRANSFER
    # ============================================================

    def transfer(
        self,
        item: str,
        quantity: int,
        source: str,
        destination: str
    ) -> Dict[str, Any]:
        """
        Transfer inventory from one location to another.
        """

        if not item:
            raise ValueError("item is required")

        # Missing source must return a failure result.
        if not source:
            result = {
                "action": "transfer",
                "status": "failure",
                "error": "source is required",
            }

            self.history.append(result)

            return result

        # Missing destination must return a failure result.
        if not destination:
            result = {
                "action": "transfer",
                "status": "failure",
                "error": "destination is required",
            }

            self.history.append(result)

            return result

        if quantity <= 0:
            result = {
                "action": "transfer",
                "status": "failure",
                "error": (
                    "Quantity must be greater than zero."
                ),
            }

            self.history.append(result)

            return result

        source_key = (item, source)
        destination_key = (item, destination)

        available = self.state["inventory"].get(
            source_key,
            0
        )

        if available < quantity:
            result = {
                "action": "transfer",
                "status": "failure",
                "error": (
                    f"Insufficient inventory at {source}."
                ),
            }

            self.history.append(result)

            return result

        # Remove from source
        self.state["inventory"][source_key] = (
            available - quantity
        )

        # Add to destination
        self.state["inventory"][destination_key] = (
            self.state["inventory"].get(
                destination_key,
                0
            ) + quantity
        )

        # Update operational location
        self.set_item_location(
            item,
            destination
        )

        result = {
            "action": "transfer",
            "status": "success",
            "item": item,
            "quantity": quantity,
            "source": source,
            "destination": destination,

            # Execution metrics
            "delivered_quantity": quantity,
            "delivery_time": 4.0,
            "total_cost": round(
                20.0 * quantity,
                2
            ),
            "carbon_emission": round(
                0.2 * quantity,
                2
            ),
        }

        self.history.append(result)

        return result

    # ============================================================
    # REROUTE
    # ============================================================

    def reroute(
        self,
        item: str,
        quantity: int,
        source: str = None,
        destination: str = None,
        from_location: str = None,
        to_location: str = None,
    ) -> Dict[str, Any]:
        """
        Reroute inventory between locations.

        Supports both parameter naming conventions:

        source / destination

        and

        from_location / to_location
        """

        # Compatibility with Pavan executor / SelectedAction
        source = source or from_location
        destination = destination or to_location

        if not item:
            raise ValueError("item is required")

        # Missing source must return a failure result.
        if not source:
            result = {
                "action": "reroute",
                "status": "failure",
                "error": "source/from_location is required",
            }

            self.history.append(result)

            return result

        # Missing destination must return a failure result.
        if not destination:
            result = {
                "action": "reroute",
                "status": "failure",
                "error": "destination/to_location is required",
            }

            self.history.append(result)

            return result

        if quantity <= 0:
            result = {
                "action": "reroute",
                "status": "failure",
                "error": (
                    "Quantity must be greater than zero."
                ),
            }

            self.history.append(result)

            return result

        source_key = (item, source)
        destination_key = (item, destination)

        available = self.state["inventory"].get(
            source_key,
            0
        )

        if available < quantity:
            result = {
                "action": "reroute",
                "status": "failure",
                "error": (
                    f"Insufficient inventory at {source}."
                ),
            }

            self.history.append(result)

            return result

        # Remove from source
        self.state["inventory"][source_key] = (
            available - quantity
        )

        # Add to destination
        self.state["inventory"][destination_key] = (
            self.state["inventory"].get(
                destination_key,
                0
            ) + quantity
        )

        # Update operational location
        self.set_item_location(
            item,
            destination
        )

        result = {
            "action": "reroute",
            "status": "success",
            "item": item,
            "quantity": quantity,

            # Keep both naming conventions in response
            "source": source,
            "destination": destination,
            "from_location": source,
            "to_location": destination,

            # Execution metrics
            "delivered_quantity": quantity,
            "delivery_time": 6.0,
            "total_cost": round(
                30.0 * quantity,
                2
            ),
            "carbon_emission": round(
                0.3 * quantity,
                2
            ),
        }

        self.history.append(result)

        return result

    # ============================================================
    # ALLOCATION
    # ============================================================

    def allocate(
        self,
        item: str,
        quantity: int,
        location: str
    ) -> Dict[str, Any]:
        """
        Allocate/reserve inventory at a location.

        Allocation does not remove physical inventory.
        It records the allocated quantity separately.
        """

        if not item:
            raise ValueError("item is required")

        if not location:
            raise ValueError("location is required")

        if quantity <= 0:
            result = {
                "action": "allocation",
                "status": "failure",
                "error": (
                    "Quantity must be greater than zero."
                ),
            }

            self.history.append(result)

            return result

        key = (item, location)

        available = self.state["inventory"].get(
            key,
            0
        )

        if available < quantity:
            result = {
                "action": "allocation",
                "status": "failure",
                "error": (
                    f"Insufficient inventory at {location}."
                ),
            }

            self.history.append(result)

            return result

        # Allocation is tracked separately.
        # Physical inventory remains unchanged.
        self.state["allocations"][key] = (
            self.state["allocations"].get(
                key,
                0
            ) + quantity
        )

        result = {
            "action": "allocation",
            "status": "success",
            "item": item,
            "quantity": quantity,
            "location": location,
            "allocated_quantity": quantity,
            "total_allocated": (
                self.state["allocations"][key]
            ),
        }

        self.history.append(result)

        return result

    # ============================================================
    # GENERIC ACTION EXECUTION
    # ============================================================

    def execute_action(
        self,
        action: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute an action using the common environment interface.
        """

        if action == "purchase":
            return self.purchase(
                item=params["item"],
                quantity=params["quantity"],
                location=params["location"],
            )

        if action == "transfer":
            return self.transfer(
                item=params["item"],
                quantity=params["quantity"],
                source=params["source"],
                destination=params["destination"],
            )

        if action == "reroute":
            return self.reroute(
                item=params["item"],
                quantity=params["quantity"],
                source=params.get("source"),
                destination=params.get("destination"),
                from_location=params.get(
                    "from_location"
                ),
                to_location=params.get(
                    "to_location"
                ),
            )

        if action == "allocation":
            return self.allocate(
                item=params["item"],
                quantity=params["quantity"],
                location=params["location"],
            )

        return {
            "action": action,
            "status": "failure",
            "error": f"Unsupported action: {action}",
        }

    # ============================================================
    # HISTORY
    # ============================================================

    def get_history(self):
        """Return execution history."""
        return self.history

    def clear_history(self) -> None:
        """Clear execution history."""
        self.history.clear()