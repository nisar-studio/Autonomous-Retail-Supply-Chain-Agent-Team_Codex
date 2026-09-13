"""State monitoring with a replaceable source."""
from __future__ import annotations

from typing import Protocol
from .contracts import CurrentState, DemandLevel, InventoryLevel, Shipment


class StateSource(Protocol):
    """Future API/data adapters must provide a current state snapshot."""
    def get_current_state(self) -> CurrentState: ...


class SampleStateSource:
    """Deterministic development-only source; not an external system."""
    def get_current_state(self) -> CurrentState:
        return CurrentState(
            snapshot_id="sample-healthy-state",
            inventory=(InventoryLevel("SKU-001", 120, 100),),
            shipments=(Shipment("SHIP-001", "SKU-001", 2, 3),),
            demand=(DemandLevel("SKU-001", 100, 100),),
        )


class Monitor:
    def __init__(self, state_source: StateSource) -> None:
        self._state_source = state_source

    def get_current_state(self) -> CurrentState:
        state = self._state_source.get_current_state()
        if not isinstance(state, CurrentState):
            raise TypeError("State source must return CurrentState")
        validate_state(state)
        return state


def validate_state(state: CurrentState) -> None:
    """Reject structurally invalid snapshots before planning depends on them."""
    if not state.snapshot_id:
        raise ValueError("CurrentState.snapshot_id must not be empty")
    _require_unique((item.sku for item in state.inventory), "inventory SKU")
    _require_unique((item.sku for item in state.demand), "demand SKU")
    _require_unique((shipment.shipment_id for shipment in state.shipments), "shipment ID")
    for item in state.inventory:
        if item.available_quantity < 0 or item.required_quantity < 0:
            raise ValueError("Inventory quantities must be non-negative")
    for demand in state.demand:
        if demand.current_quantity < 0 or demand.baseline_quantity < 0:
            raise ValueError("Demand quantities must be non-negative")
    for shipment in state.shipments:
        if shipment.expected_day < 0 or shipment.promised_day < 0:
            raise ValueError("Shipment days must be non-negative")


def _require_unique(values, label: str) -> None:
    value_list = list(values)
    if len(value_list) != len(set(value_list)):
        raise ValueError(f"CurrentState contains duplicate {label} values")
