from typing import Any, Dict, Tuple


class Environment:
    """
    Simulated retail supply-chain environment.

    State contains:
        inventory  -> {(item, location): quantity}
        locations  -> {item: latest operational location}
        balances   -> optional balance information
        allocations -> {(item, location): allocated quantity}

    Supported actions:
        purchase
        transfer
        reroute
        allocate
    """

    def __init__(self):
        self.state: Dict[str, Any] = {
            "inventory": {},
            "locations": {},
            "balances": {},
            "allocations": {},
        }

        self.history = []

    # =========================================================
    # STATE
    # =========================================================

    def get_state(self) -> Dict[str, Any]:
        return self.state

    # =========================================================
    # LOCATION MANAGEMENT
    # =========================================================

    def set_item_location(
        self,
        item: str,
        location: str
    ) -> None:
        self.state["locations"][item] = location

    def get_item_location(
        self,
        item: str
    ):
        return self.state["locations"].get(item)

    def has_item_location(
        self,
        item: str
    ) -> bool:
        return item in self.state["locations"]

    def get_all_item_locations(
        self
    ) -> Dict[str, str]:
        return self.state["locations"].copy()

    # =========================================================
    # INVENTORY HELPERS
    # =========================================================

    def _inventory_key(
        self,
        item: str,
        location: str
    ) -> Tuple[str, str]:
        return (item, location)

    def _get_inventory(
        self,
        item: str,
        location: str
    ) -> float:
        key = self._inventory_key(
            item,
            location
        )

        return self.state["inventory"].get(
            key,
            0
        )

    def _set_inventory(
        self,
        item: str,
        location: str,
        quantity: float
    ) -> None:

        key = self._inventory_key(
            item,
            location
        )

        if quantity <= 0:
            self.state["inventory"].pop(
                key,
                None
            )
        else:
            self.state["inventory"][key] = quantity

    def _add_inventory(
        self,
        item: str,
        location: str,
        quantity: float
    ) -> None:

        current_quantity = self._get_inventory(
            item,
            location
        )

        self._set_inventory(
            item,
            location,
            current_quantity + quantity
        )

    # =========================================================
    # EXECUTION METRICS
    # =========================================================

    def _execution_metrics(
        self,
        action: str,
        quantity: float
    ) -> Dict[str, float]:

        if action == "purchase":

            delivery_time = 24.0
            total_cost = 100.0 * quantity
            carbon_emission = 0.5 * quantity

        elif action == "transfer":

            delivery_time = 4.0
            total_cost = 20.0 * quantity
            carbon_emission = 0.2 * quantity

        elif action == "reroute":

            delivery_time = 6.0
            total_cost = 30.0 * quantity
            carbon_emission = 0.3 * quantity

        else:

            delivery_time = 0.0
            total_cost = 0.0
            carbon_emission = 0.0

        return {
            "delivered_quantity": quantity,
            "delivery_time": delivery_time,
            "total_cost": round(
                total_cost,
                2
            ),
            "carbon_emission": round(
                carbon_emission,
                2
            ),
        }

    # =========================================================
    # PURCHASE
    # =========================================================

    def purchase(
        self,
        item: str,
        quantity: float,
        location: str,
        supplier_id: str = None
    ) -> Dict[str, Any]:

        if not item:

            return {
                "action": "purchase",
                "status": "failure",
                "error": "Item is required.",
            }

        if not location:

            return {
                "action": "purchase",
                "status": "failure",
                "error": "Location is required.",
            }

        if quantity <= 0:

            return {
                "action": "purchase",
                "status": "failure",
                "error": (
                    "Quantity must be greater than zero."
                ),
            }

        # Add purchased inventory
        self._add_inventory(
            item,
            location,
            quantity
        )

        # Update operational location
        self.set_item_location(
            item,
            location
        )

        # Calculate execution metrics
        metrics = self._execution_metrics(
            "purchase",
            quantity
        )

        result = {
            "action": "purchase",
            "status": "success",
            "item": item,
            "quantity": quantity,
            "location": location,
            "supplier_id": supplier_id,
            **metrics,
        }

        self.history.append(result)

        return result

    # =========================================================
    # TRANSFER
    # =========================================================

    def transfer(
        self,
        item: str,
        quantity: float,
        source: str,
        destination: str
    ) -> Dict[str, Any]:

        if not item:

            return {
                "action": "transfer",
                "status": "failure",
                "error": "Item is required.",
            }

        if not source:

            return {
                "action": "transfer",
                "status": "failure",
                "error": (
                    "Source location is required."
                ),
            }

        if not destination:

            return {
                "action": "transfer",
                "status": "failure",
                "error": (
                    "Destination location is required."
                ),
            }

        if source == destination:

            return {
                "action": "transfer",
                "status": "failure",
                "error": (
                    "Source and destination "
                    "cannot be the same."
                ),
            }

        if quantity <= 0:

            return {
                "action": "transfer",
                "status": "failure",
                "error": (
                    "Quantity must be greater than zero."
                ),
            }

        # Check source inventory
        available = self._get_inventory(
            item,
            source
        )

        if available < quantity:

            return {
                "action": "transfer",
                "status": "failure",
                "error": (
                    f"Insufficient inventory for "
                    f"{item} at {source}. "
                    f"Available: {available}, "
                    f"requested: {quantity}."
                ),
            }

        # Remove inventory from source
        self._set_inventory(
            item,
            source,
            available - quantity
        )

        # Add inventory to destination
        self._add_inventory(
            item,
            destination,
            quantity
        )

        # Update latest operational location
        self.set_item_location(
            item,
            destination
        )

        # Calculate metrics
        metrics = self._execution_metrics(
            "transfer",
            quantity
        )

        result = {
            "action": "transfer",
            "status": "success",
            "item": item,
            "quantity": quantity,
            "source": source,
            "destination": destination,
            **metrics,
        }

        self.history.append(result)

        return result

    # =========================================================
    # REROUTE
    # =========================================================

    def reroute(
        self,
        item: str,
        quantity: float,
        source: str,
        destination: str
    ) -> Dict[str, Any]:

        if not item:

            return {
                "action": "reroute",
                "status": "failure",
                "error": "Item is required.",
            }

        if not source:

            return {
                "action": "reroute",
                "status": "failure",
                "error": (
                    "Source location is required."
                ),
            }

        if not destination:

            return {
                "action": "reroute",
                "status": "failure",
                "error": (
                    "Destination location is required."
                ),
            }

        if source == destination:

            return {
                "action": "reroute",
                "status": "failure",
                "error": (
                    "Source and destination "
                    "cannot be the same."
                ),
            }

        if quantity <= 0:

            return {
                "action": "reroute",
                "status": "failure",
                "error": (
                    "Quantity must be greater than zero."
                ),
            }

        # -----------------------------------------------------
        # IMPORTANT:
        # Read inventory specifically from the source.
        # -----------------------------------------------------

        available = self._get_inventory(
            item,
            source
        )

        if available < quantity:

            return {
                "action": "reroute",
                "status": "failure",
                "error": (
                    f"Insufficient inventory for "
                    f"{item} at {source}. "
                    f"Available: {available}, "
                    f"requested: {quantity}."
                ),
            }

        # -----------------------------------------------------
        # Remove quantity from source
        # -----------------------------------------------------

        self._set_inventory(
            item,
            source,
            available - quantity
        )

        # -----------------------------------------------------
        # Add quantity to destination
        # -----------------------------------------------------

        self._add_inventory(
            item,
            destination,
            quantity
        )

        # -----------------------------------------------------
        # Update latest operational location
        # -----------------------------------------------------

        self.set_item_location(
            item,
            destination
        )

        # -----------------------------------------------------
        # Calculate reroute metrics
        # -----------------------------------------------------

        metrics = self._execution_metrics(
            "reroute",
            quantity
        )

        result = {
            "action": "reroute",
            "status": "success",
            "item": item,
            "quantity": quantity,
            "source": source,
            "destination": destination,
            **metrics,
        }

        self.history.append(result)

        return result

    # =========================================================
    # ALLOCATION
    # =========================================================

    def allocate(
        self,
        item: str,
        quantity: float,
        location: str
    ) -> Dict[str, Any]:

        if not item:

            return {
                "action": "allocation",
                "status": "failure",
                "error": "Item is required.",
            }

        if not location:

            return {
                "action": "allocation",
                "status": "failure",
                "error": "Location is required.",
            }

        if quantity <= 0:

            return {
                "action": "allocation",
                "status": "failure",
                "error": (
                    "Quantity must be greater than zero."
                ),
            }

        # Current inventory at location
        available_inventory = self._get_inventory(
            item,
            location
        )

        allocation_key = (
            item,
            location
        )

        # Already allocated quantity
        already_allocated = self.state[
            "allocations"
        ].get(
            allocation_key,
            0
        )

        # Remaining unallocated stock
        available_to_allocate = (
            available_inventory
            - already_allocated
        )

        if available_to_allocate < quantity:

            return {
                "action": "allocation",
                "status": "failure",
                "error": (
                    f"Insufficient unallocated "
                    f"inventory for {item} at "
                    f"{location}. "
                    f"Available: "
                    f"{available_to_allocate}, "
                    f"requested: {quantity}."
                ),
            }

        total_allocated = (
            already_allocated
            + quantity
        )

        # Reserve inventory
        self.state[
            "allocations"
        ][allocation_key] = total_allocated

        # Update item location
        self.set_item_location(
            item,
            location
        )

        result = {
            "action": "allocation",
            "status": "success",
            "item": item,
            "quantity": quantity,
            "location": location,
            "allocated_quantity": quantity,
            "total_allocated": total_allocated,
        }

        self.history.append(result)

        return result

    # =========================================================
    # HISTORY
    # =========================================================

    def get_history(self):

        return self.history.copy()