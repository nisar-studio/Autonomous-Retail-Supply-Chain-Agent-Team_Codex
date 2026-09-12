"""Minimal internal contracts for Nisar's recovery workflow."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Optional, Tuple


class DisruptionType(str, Enum):
    INVENTORY_SHORTAGE = "inventory_shortage"
    SHIPMENT_DELAY = "shipment_delay"
    DEMAND_SPIKE = "demand_spike"


class OutcomeStatus(str, Enum):
    RECOVERED = "recovered"
    NO_DISRUPTION = "no_disruption"
    NO_FEASIBLE_ACTION = "no_feasible_action"
    REPLAN_LIMIT_REACHED = "replan_limit_reached"


class RecoveryStage(str, Enum):
    """Observable stages of one controller recovery run."""

    MONITORED = "monitored"
    DETECTED = "detected"
    PLANNED = "planned"
    ACTION_SELECTED = "action_selected"
    EXECUTED = "executed"
    VERIFIED = "verified"
    REPLANNING = "replanning"
    TERMINATED = "terminated"


@dataclass(frozen=True)
class InventoryLevel:
    sku: str
    available_quantity: int
    required_quantity: int


@dataclass(frozen=True)
class Shipment:
    shipment_id: str
    sku: str
    expected_day: int
    promised_day: int
    status: str = "in_transit"


@dataclass(frozen=True)
class DemandLevel:
    sku: str
    current_quantity: int
    baseline_quantity: int


@dataclass(frozen=True)
class CurrentState:
    """State snapshot supplied by a replaceable source; days are simulated."""
    inventory: Tuple[InventoryLevel, ...] = ()
    shipments: Tuple[Shipment, ...] = ()
    demand: Tuple[DemandLevel, ...] = ()
    snapshot_id: str = "unknown"


@dataclass(frozen=True)
class Disruption:
    disruption_type: DisruptionType
    severity: str
    details: str
    affected_ids: Tuple[str, ...]
    metrics: Mapping[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class RecoveryGoal:
    """A required outcome, without choosing a supplier, route, or action."""
    goal_id: str
    objective: str
    affected_ids: Tuple[str, ...]
    disruption_type: DisruptionType
    constraints: Mapping[str, int | str] = field(default_factory=dict)
    location: str | None = None


@dataclass(frozen=True)
class RecoveryPlan:
    """A request for Preethesh's alternative investigation."""
    goal: RecoveryGoal
    alternative_request: str
    state_snapshot_id: str


@dataclass(frozen=True)
class SelectedAction:
    """A selected Preethesh action with Nisar's existing trace fields."""

    action_id: str
    action_type: str = ""
    description: str = ""
    tool: str = ""
    operation: str = ""
    parameters: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutionResult:
    succeeded: bool
    details: str
    updated_state: Optional[CurrentState] = None
    action_unavailable: Optional[bool] = None
    action_id: Optional[str] = None


@dataclass(frozen=True)
class VerificationResult:
    succeeded: bool
    details: str
    requires_replan: bool = False
    action_id: Optional[str] = None


@dataclass(frozen=True)
class LifecycleEvent:
    """Structured controller trace entry retained during recovery."""

    attempt: int
    stage: RecoveryStage
    details: str
    state_snapshot_id: Optional[str] = None
    action_id: Optional[str] = None


@dataclass(frozen=True)
class RecoveryContext:
    """Controller-owned state that must persist across replan attempts."""

    attempt: int = 0
    excluded_action_ids: Tuple[str, ...] = ()
    latest_state_snapshot_id: Optional[str] = None
    active_disruption: Optional[Disruption] = None
    active_goal: Optional[RecoveryGoal] = None
    events: Tuple[LifecycleEvent, ...] = ()


@dataclass(frozen=True)
class ControllerOutcome:
    status: OutcomeStatus
    details: str
    attempts: int
    goal: Optional[RecoveryGoal] = None
    action: Optional[SelectedAction] = None
    context: RecoveryContext = field(default_factory=RecoveryContext)
