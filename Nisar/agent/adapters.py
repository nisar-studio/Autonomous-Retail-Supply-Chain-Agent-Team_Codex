"""Integration boundaries; TODO: replace with agreed Shared contracts later."""
from __future__ import annotations

from typing import Protocol, Sequence
from .contracts import CurrentState, ExecutionResult, RecoveryGoal, RecoveryPlan, SelectedAction, VerificationResult


class AlternativeSelector(Protocol):
    """Preethesh: honor exclusions and return a feasible selected action or None."""
    def select_action(self, goal: RecoveryGoal, plan: RecoveryPlan, state: CurrentState, excluded_action_ids: Sequence[str]) -> SelectedAction | None: ...


class ActionExecutor(Protocol):
    """Pavan: return execution status and updated_state when execution changes it."""
    def execute(self, action: SelectedAction, state: CurrentState) -> ExecutionResult: ...


class OutcomeVerifier(Protocol):
    """Mugil: evaluate the goal against the execution result and signal replan."""
    def verify(self, goal: RecoveryGoal, plan: RecoveryPlan, execution: ExecutionResult) -> VerificationResult: ...
