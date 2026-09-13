class Environment:
    """
    Simulated environment for executing actions that change system state.

    Supports:
    - Purchase
    - Transfer
    - Reroute / Allocation
    """

    def __init__(self):
        self.state = {
            "inventory": {},
            "locations": {},
            "balances": {},
            "allocations": {},
        }

        self.history = []

    def purchase(self, item, quantity, location):
        """Purchase items and add them to a location."""

        if quantity <= 0:
            return self._failure("Quantity must be greater than 0.")

        current_quantity = self.state["inventory"].get(
            (item, location), 0
        )

        self.state["inventory"][(item, location)] = (
            current_quantity + quantity
        )

        result = {
            "action": "purchase",
            "status": "success",
            "item": item,
            "quantity": quantity,
            "location": location,
        }

        self.history.append(result)
        return result

    def transfer(self, item, quantity, source, destination):
        """Transfer items from one location to another."""

        if quantity <= 0:
            return self._failure("Quantity must be greater than 0.")

        source_key = (item, source)
        destination_key = (item, destination)

        available = self.state["inventory"].get(source_key, 0)

        if available < quantity:
            return self._failure(
                f"Not enough {item} at {source}. "
                f"Available: {available}, requested: {quantity}."
            )

        self.state["inventory"][source_key] = available - quantity

        destination_quantity = self.state["inventory"].get(
            destination_key, 0
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
        }

        self.history.append(result)
        return result

    def reroute(self, item, quantity, from_location, to_location):
        """
        Reroute inventory.

        This is implemented using the transfer operation so that
        state changes remain consistent.
        """

        result = self.transfer(
            item,
            quantity,
            from_location,
            to_location,
        )

        if result["status"] == "success":
            result["action"] = "reroute"

        return result

    def get_state(self):
        """Return a snapshot of the current environment state."""

        return {
            "inventory": self.state["inventory"].copy(),
            "locations": self.state["locations"].copy(),
            "balances": self.state["balances"].copy(),
            "allocations": self.state["allocations"].copy(),
        }

    def get_history(self):
        """Return the list of actions executed so far."""
        return self.history.copy()

    def _failure(self, message):
        """Create a standard failure result."""

        result = {
            "status": "failure",
            "error": message,
        }

        self.history.append(result)
        return result