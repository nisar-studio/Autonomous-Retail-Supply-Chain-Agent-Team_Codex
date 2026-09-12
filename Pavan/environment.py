class Environment:
    """
    Simulated environment for executing supply-chain actions.

    Supported actions:
    - Purchase
    - Transfer
    - Reroute / Allocation

    The environment also produces simulated evaluation metrics:
    - delivered_quantity
    - delivery_time (hours)
    - total_cost
    - carbon_emission (kg CO2e)

    Note:
    The metric values are deterministic simulation values for the
    hackathon environment, not real-world logistics calculations.
    """

    def __init__(self):
        self.state = {
            "inventory": {},
            "locations": {},
            "balances": {},
            "allocations": {},
        }

        self.history = []

    def _execution_metrics(self, action, quantity):
        """
        Generate deterministic simulated execution metrics.

        These values are used by the evaluation layer.
        """

        if action == "purchase":
            return {
                "delivered_quantity": quantity,
                "delivery_time": 24.0,
                "total_cost": float(quantity * 100),
                "carbon_emission": float(quantity * 0.5),
            }

        if action == "transfer":
            return {
                "delivered_quantity": quantity,
                "delivery_time": 4.0,
                "total_cost": float(quantity * 20),
                "carbon_emission": float(quantity * 0.2),
            }

        if action == "reroute":
            return {
                "delivered_quantity": quantity,
                "delivery_time": 6.0,
                "total_cost": float(quantity * 30),
                "carbon_emission": float(quantity * 0.3),
            }

        return {
            "delivered_quantity": 0,
            "delivery_time": 0.0,
            "total_cost": 0.0,
            "carbon_emission": 0.0,
        }

    def purchase(self, item, quantity, location):
        """
        Purchase inventory and add it to a location.
        """

        if quantity <= 0:
            return self._failure(
                "Quantity must be greater than 0."
            )

        current_quantity = self.state["inventory"].get(
            (item, location),
            0
        )

        self.state["inventory"][
            (item, location)
        ] = current_quantity + quantity

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

    def transfer(
        self,
        item,
        quantity,
        source,
        destination
    ):
        """
        Transfer inventory from one location to another.
        """

        if quantity <= 0:
            return self._failure(
                "Quantity must be greater than 0."
            )

        source_key = (item, source)
        destination_key = (item, destination)

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

        # Remove inventory from source
        self.state["inventory"][source_key] = (
            available - quantity
        )

        # Add inventory to destination
        destination_quantity = self.state["inventory"].get(
            destination_key,
            0
        )

        self.state["inventory"][destination_key] = (
            destination_quantity + quantity
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

    def reroute(
        self,
        item,
        quantity,
        from_location,
        to_location
    ):
        """
        Reroute inventory from one location to another.

        This performs the same inventory movement as transfer,
        but reports the action as 'reroute' and uses reroute
        evaluation metrics.
        """

        if quantity <= 0:
            return self._failure(
                "Quantity must be greater than 0."
            )

        source_key = (item, from_location)
        destination_key = (item, to_location)

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

        # Remove inventory from source
        self.state["inventory"][source_key] = (
            available - quantity
        )

        # Add inventory to destination
        destination_quantity = self.state["inventory"].get(
            destination_key,
            0
        )

        self.state["inventory"][destination_key] = (
            destination_quantity + quantity
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

    def get_history(self):
        """
        Return a copy of the execution history.
        """

        return self.history.copy()

    def _failure(self, message):
        """
        Create and record a failed execution result.
        """

        result = {
            "status": "failure",
            "error": message,
        }

        self.history.append(result)

        return result