class Environment:
    """
    Simulated environment for executing supply-chain actions.

    Supported actions:
    - Purchase
    - Transfer
    - Reroute

    The environment also provides:
    - Explicit item -> location mapping
    - Inventory management
    - Execution history
    - Evaluation metrics

    Location policy:
    - Locations must be explicitly provided.
    - No default or guessed location is created.
    """

    def __init__(self):
        self.state = {
            "inventory": {},
            "locations": {},
            "balances": {},
            "allocations": {},
        }

        self.history = []

    # ==============================================================
    # LOCATION MANAGEMENT
    # ==============================================================

    def set_item_location(self, item, location):
        """
        Explicitly associate an item with a location.

        Example:
            env.set_item_location("laptop", "warehouse_1")
        """

        if not item:
            raise ValueError("Item is required.")

        if not location:
            raise ValueError("Location is required.")

        self.state["locations"][item] = location

        return {
            "status": "success",
            "item": item,
            "location": location,
        }

    def get_item_location(self, item):
        """
        Return the explicitly registered location for an item.

        Returns None if no location has been registered.
        """

        return self.state["locations"].get(item)

    def has_item_location(self, item):
        """
        Check whether an explicit location exists for an item.
        """

        return item in self.state["locations"]

    def get_all_item_locations(self):
        """
        Return a copy of the complete item -> location mapping.
        """

        return self.state["locations"].copy()

    # ==============================================================
    # EVALUATION METRICS
    # ==============================================================

    def _execution_metrics(self, action, quantity):
        """
        Deterministic simulation metrics.

        These values are for the hackathon simulation environment.
        They are not real-world logistics calculations.

        Metrics:
        - delivered_quantity
        - delivery_time
        - total_cost
        - carbon_emission
        """

        if action == "purchase":
            return {
                "delivered_quantity": quantity,
                "delivery_time": 24.0,
                "total_cost": round(float(quantity * 100), 2),
                "carbon_emission": round(float(quantity * 0.5), 2),
            }

        if action == "transfer":
            return {
                "delivered_quantity": quantity,
                "delivery_time": 4.0,
                "total_cost": round(float(quantity * 20), 2),
                "carbon_emission": round(float(quantity * 0.2), 2),
            }

        if action == "reroute":
            return {
                "delivered_quantity": quantity,
                "delivery_time": 6.0,
                "total_cost": round(float(quantity * 30), 2),
                "carbon_emission": round(float(quantity * 0.3), 2),
            }

        return {
            "delivered_quantity": 0,
            "delivery_time": 0.0,
            "total_cost": 0.0,
            "carbon_emission": 0.0,
        }

    # ==============================================================
    # PURCHASE
    # ==============================================================

    def purchase(self, item, quantity, location):
        """
        Purchase an item and add it to inventory at the given location.
        """

        if quantity <= 0:
            return self._failure(
                "Quantity must be greater than 0."
            )

        if not location:
            return self._failure(
                "Location is required for purchase."
            )

        current_quantity = self.state["inventory"].get(
            (item, location),
            0
        )

        self.state["inventory"][(item, location)] = (
            current_quantity + quantity
        )

        # Record the explicitly supplied location.
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
            **self._execution_metrics(
                "purchase",
                quantity
            ),
        }

        self.history.append(result)

        return result

    # ==============================================================
    # TRANSFER
    # ==============================================================

    def transfer(
        self,
        item,
        quantity,
        source,
        destination
    ):
        """
        Transfer inventory from source to destination.
        """

        if quantity <= 0:
            return self._failure(
                "Quantity must be greater than 0."
            )

        if not source:
            return self._failure(
                "Source location is required."
            )

        if not destination:
            return self._failure(
                "Destination location is required."
            )

        source_key = (
            item,
            source
        )

        destination_key = (
            item,
            destination
        )

        available = self.state["inventory"].get(
            source_key,
            0
        )

        if available < quantity:
            return self._failure(
                f"Not enough {item} at {source}. "
                f"Available: {available}, "
                f"requested: {quantity}."
            )

        # Remove from source.
        self.state["inventory"][source_key] = (
            available - quantity
        )

        # Add to destination.
        destination_quantity = self.state["inventory"].get(
            destination_key,
            0
        )

        self.state["inventory"][destination_key] = (
            destination_quantity + quantity
        )

        # Destination becomes current item location.
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
            **self._execution_metrics(
                "transfer",
                quantity
            ),
        }

        self.history.append(result)

        return result

    # ==============================================================
    # REROUTE
    # ==============================================================

    def reroute(
        self,
        item,
        quantity,
        from_location,
        to_location
    ):
        """
        Reroute inventory from one location to another.
        """

        if quantity <= 0:
            return self._failure(
                "Quantity must be greater than 0."
            )

        if not from_location:
            return self._failure(
                "Source location is required for reroute."
            )

        if not to_location:
            return self._failure(
                "Destination location is required for reroute."
            )

        source_key = (
            item,
            from_location
        )

        destination_key = (
            item,
            to_location
        )

        available = self.state["inventory"].get(
            source_key,
            0
        )

        if available < quantity:
            return self._failure(
                f"Not enough {item} at {from_location}. "
                f"Available: {available}, "
                f"requested: {quantity}."
            )

        # Remove from source.
        self.state["inventory"][source_key] = (
            available - quantity
        )

        # Add to destination.
        destination_quantity = self.state["inventory"].get(
            destination_key,
            0
        )

        self.state["inventory"][destination_key] = (
            destination_quantity + quantity
        )

        # Update current item location.
        self.set_item_location(
            item,
            to_location
        )

        result = {
            "action": "reroute",
            "status": "success",
            "item": item,
            "quantity": quantity,
            "source": from_location,
            "destination": to_location,
            **self._execution_metrics(
                "reroute",
                quantity
            ),
        }

        self.history.append(result)

        return result

    # ==============================================================
    # STATE
    # ==============================================================

    def get_state(self):
        """
        Return the current environment state.
        """

        return {
            "inventory": self.state["inventory"].copy(),
            "locations": self.state["locations"].copy(),
            "balances": self.state["balances"].copy(),
            "allocations": self.state["allocations"].copy(),
        }

    # ==============================================================
    # HISTORY
    # ==============================================================

    def get_history(self):
        """
        Return a copy of the execution history.
        """

        return self.history.copy()

    # ==============================================================
    # FAILURE HANDLING
    # ==============================================================

    def _failure(self, message):
        """
        Create and record a failed operation.
        """

        result = {
            "status": "failure",
            "error": message,
        }

        self.history.append(result)

        return result