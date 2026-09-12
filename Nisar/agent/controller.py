"""Bounded agentic recovery orchestration for Nisar's module."""
from __future__ import annotations

from .adapters import ActionExecutor, AlternativeSelector, OutcomeVerifier
from .contracts import (
    ControllerOutcome,
    CurrentState,
    LifecycleEvent,
    OutcomeStatus,
    RecoveryContext,
    RecoveryStage,
)
from .disruption_detector import detect_disruptions, prioritize_disruptions
from .monitor import Monitor
from .planner import create_recovery_goal, create_recovery_plan


class RecoveryController:
    """Coordinates monitor -> detect -> plan -> act -> verify -> replan."""

    def __init__(
        self,
        monitor: Monitor,
        alternative_selector: AlternativeSelector,
        executor: ActionExecutor,
        verifier: OutcomeVerifier,
        max_replanning_attempts: int = 2,
        recovery_location: str | None = None,
    ) -> None:
        if max_replanning_attempts < 0:
            raise ValueError("max_replanning_attempts must be non-negative")
        self._monitor = monitor
        self._alternative_selector = alternative_selector
        self._executor = executor
        self._verifier = verifier
        self._max_replanning_attempts = max_replanning_attempts
        self._recovery_location = recovery_location

    def recover(self) -> ControllerOutcome:
        """Recover the highest-priority active disruption within the retry bound."""
        context = RecoveryContext()
        last_state: CurrentState | None = None

        for attempt in range(self._max_replanning_attempts + 1):
            state = last_state or self._monitor.get_current_state()
            last_state = None
            context = self._record(
                context, attempt, RecoveryStage.MONITORED, "State snapshot acquired.",
                state_snapshot_id=state.snapshot_id,
            )
            disruptions = prioritize_disruptions(detect_disruptions(state))
            if not disruptions:
                status = OutcomeStatus.NO_DISRUPTION if attempt == 0 else OutcomeStatus.RECOVERED
                return self._outcome(status, "No active disruption remains.", attempt, context)

            disruption = disruptions[0]
            context = self._record(
                context, attempt, RecoveryStage.DETECTED,
                f"Prioritized {disruption.disruption_type.value}; {len(disruptions) - 1} other disruption(s) remain queued.",
                state_snapshot_id=state.snapshot_id, disruption=disruption,
            )
            goal = create_recovery_goal(state, disruption, self._recovery_location)
            plan = create_recovery_plan(goal, state)
            context = self._record(
                context, attempt, RecoveryStage.PLANNED,
                f"Recovery plan created for {goal.goal_id}.",
                state_snapshot_id=state.snapshot_id, goal=goal,
            )
            action = self._alternative_selector.select_action(
                goal, plan, state, context.excluded_action_ids
            )
            if action is None:
                return self._outcome(
                    OutcomeStatus.NO_FEASIBLE_ACTION,
                    "No feasible recovery action was supplied by the alternative selector.",
                    attempt, context,
                )

            context = self._record(
                context, attempt, RecoveryStage.ACTION_SELECTED,
                "Alternative selector supplied an action.",
                state_snapshot_id=state.snapshot_id, action_id=action.action_id,
            )
            execution = self._executor.execute(action, state)
            execution_detail = "Execution succeeded." if execution.succeeded else "Execution failed."
            if execution.action_unavailable:
                execution_detail = "Execution reported the selected action unavailable."
            context = self._record(
                context, attempt, RecoveryStage.EXECUTED, execution_detail,
                state_snapshot_id=state.snapshot_id, action_id=action.action_id,
            )

            if execution.succeeded:
                verification = self._verifier.verify(goal, plan, execution)
                context = self._record(
                    context, attempt, RecoveryStage.VERIFIED,
                    "Verification succeeded." if verification.succeeded else "Verification failed.",
                    state_snapshot_id=(execution.updated_state.snapshot_id if execution.updated_state else state.snapshot_id),
                    action_id=action.action_id,
                )
                if verification.succeeded:
                    return ControllerOutcome(
                        OutcomeStatus.RECOVERED, verification.details, attempt + 1,
                        goal, action, context,
                    )
                failure_reason = verification.details
            else:
                failure_reason = execution.details

            context = self._record(
                context, attempt + 1, RecoveryStage.REPLANNING, failure_reason,
                state_snapshot_id=(execution.updated_state.snapshot_id if execution.updated_state else state.snapshot_id),
                action_id=action.action_id, excluded_action_id=action.action_id,
            )
            last_state = execution.updated_state
            if attempt == self._max_replanning_attempts:
                return ControllerOutcome(
                    OutcomeStatus.REPLAN_LIMIT_REACHED,
                    f"Recovery did not succeed after {attempt + 1} action attempt(s): {failure_reason}",
                    attempt + 1, goal, action, context,
                )

        raise RuntimeError("Unreachable recovery loop termination")

    @staticmethod
    def _record(
        context: RecoveryContext,
        attempt: int,
        stage: RecoveryStage,
        details: str,
        *,
        state_snapshot_id: str | None = None,
        action_id: str | None = None,
        disruption=None,
        goal=None,
        excluded_action_id: str | None = None,
    ) -> RecoveryContext:
        exclusions = context.excluded_action_ids
        if excluded_action_id is not None and excluded_action_id not in exclusions:
            exclusions = (*exclusions, excluded_action_id)
        event = LifecycleEvent(attempt, stage, details, state_snapshot_id, action_id)
        return RecoveryContext(
            attempt=attempt,
            excluded_action_ids=exclusions,
            latest_state_snapshot_id=state_snapshot_id or context.latest_state_snapshot_id,
            active_disruption=disruption or context.active_disruption,
            active_goal=goal or context.active_goal,
            events=(*context.events, event),
        )

    @staticmethod
    def _outcome(
        status: OutcomeStatus,
        details: str,
        attempts: int,
        context: RecoveryContext,
    ) -> ControllerOutcome:
        terminated_context = RecoveryController._record(
            context, attempts, RecoveryStage.TERMINATED, details
        )
        return ControllerOutcome(status, details, attempts, context=terminated_context)
