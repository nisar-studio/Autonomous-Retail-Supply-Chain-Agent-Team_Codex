"""Rule-based detection over the information represented by CurrentState."""
from __future__ import annotations

from .contracts import CurrentState, Disruption, DisruptionType

DEMAND_SPIKE_MULTIPLIER = 1.20
_SEVERITY_RANK = {"high": 0, "medium": 1, "low": 2}
_TYPE_RANK = {
    DisruptionType.INVENTORY_SHORTAGE: 0,
    DisruptionType.SHIPMENT_DELAY: 1,
    DisruptionType.DEMAND_SPIKE: 2,
}


def detect_disruptions(state: CurrentState) -> tuple[Disruption, ...]:
    if not isinstance(state, CurrentState):
        raise TypeError("state must be a CurrentState")
    disruptions: list[Disruption] = []
    for item in state.inventory:
        if item.available_quantity < item.required_quantity:
            shortfall = item.required_quantity - item.available_quantity
            disruptions.append(Disruption(DisruptionType.INVENTORY_SHORTAGE, "high" if shortfall >= item.required_quantity / 2 else "medium", f"{item.sku} is short by {shortfall} units.", (item.sku,), {"shortfall_quantity": shortfall}))
    for shipment in state.shipments:
        if shipment.expected_day > shipment.promised_day:
            delay = shipment.expected_day - shipment.promised_day
            disruptions.append(Disruption(DisruptionType.SHIPMENT_DELAY, "high" if delay >= 2 else "medium", f"{shipment.shipment_id} is delayed by {delay} day(s).", (shipment.shipment_id, shipment.sku), {"delay_days": delay}))
    for demand in state.demand:
        if demand.baseline_quantity > 0 and demand.current_quantity > demand.baseline_quantity * DEMAND_SPIKE_MULTIPLIER:
            increase = demand.current_quantity - demand.baseline_quantity
            disruptions.append(Disruption(DisruptionType.DEMAND_SPIKE, "high" if demand.current_quantity >= demand.baseline_quantity * 1.5 else "medium", f"Demand for {demand.sku} is {increase} units above baseline.", (demand.sku,), {"demand_increase": increase}))
    return tuple(disruptions)


def prioritize_disruptions(disruptions: tuple[Disruption, ...]) -> tuple[Disruption, ...]:
    """Order simultaneous disruptions deterministically for one recovery run."""
    return tuple(sorted(disruptions, key=lambda disruption: (
        _SEVERITY_RANK.get(disruption.severity, len(_SEVERITY_RANK)),
        _TYPE_RANK[disruption.disruption_type],
        disruption.affected_ids,
    )))
