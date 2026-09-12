"""Creates recovery objectives and requests for externally selected actions."""
from __future__ import annotations

from .contracts import CurrentState, Disruption, RecoveryGoal, RecoveryPlan


def create_recovery_goal(state: CurrentState, disruption: Disruption) -> RecoveryGoal:
    constraints = dict(disruption.metrics)
    constraints["state_snapshot"] = state.snapshot_id
    return RecoveryGoal(
        f"{state.snapshot_id}:{disruption.disruption_type.value}:{'-'.join(disruption.affected_ids)}",
        f"Restore service for affected supply-chain items after {disruption.disruption_type.value}.",
        disruption.affected_ids,
        disruption.disruption_type,
        constraints,
    )


def create_recovery_plan(goal: RecoveryGoal, state: CurrentState) -> RecoveryPlan:
    """Create an alternative request bound to the state that produced the goal."""
    return RecoveryPlan(
        goal,
        "Investigate feasible recovery alternatives that meet the goal constraints; return one selected action or no feasible action.",
        state.snapshot_id,
    )
