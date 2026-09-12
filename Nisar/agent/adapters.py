"""Nisar-owned boundaries and conversions for finalized team contracts."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Protocol, Sequence
from .contracts import CurrentState, ExecutionResult, RecoveryGoal, RecoveryPlan, SelectedAction, VerificationResult


class AlternativeSelector(Protocol):
    """Preethesh: honor exclusions and return a feasible selected action or None."""
    def select_action(self, goal: RecoveryGoal, plan: RecoveryPlan, state: CurrentState, excluded_action_ids: Sequence[str]) -> SelectedAction | None: ...


class RawPreetheshSelector(Protocol):
    """Preethesh's selector before conversion to Nisar's action contract."""

    def select_action(
        self,
        goal: RecoveryGoal,
        plan: RecoveryPlan,
        state: CurrentState,
        excluded_action_ids: Sequence[str],
    ) -> Mapping[str, object] | None: ...


class ActionExecutor(Protocol):
    """Pavan: return execution status and updated_state when execution changes it."""
    def execute(self, action: SelectedAction, state: CurrentState) -> ExecutionResult: ...


class OutcomeVerifier(Protocol):
    """Mugil: evaluate the goal against the execution result and signal replan."""
    def verify(self, goal: RecoveryGoal, plan: RecoveryPlan, execution: ExecutionResult) -> VerificationResult: ...


class ActionConversionError(ValueError):
    """Raised when a selected action lacks an explicitly required parameter."""


@dataclass(frozen=True)
class PavanActionRequest:
    """Pavan's executable payload plus the Preethesh correlation identifier."""

    action_id: str
    action: str
    params: Mapping[str, object]

    def as_payload(self) -> dict[str, object]:
        return {
            "action_id": self.action_id,
            "action": self.action,
            "params": dict(self.params),
        }


def to_pavan_action(action: SelectedAction) -> PavanActionRequest:
    """Convert only the team-approved Preethesh action mappings for Pavan.

    ``action_id`` is intentionally retained outside Pavan's action payload so
    Nisar can correlate the execution and later Mugil evaluation.
    """
    _require_non_empty_text(action.action_id, "action_id")
    parameters = action.parameters
    if not isinstance(parameters, Mapping):
        raise ActionConversionError("parameters must be a mapping")

    if action.tool == "order" and action.operation == "create":
        return PavanActionRequest(
            action.action_id,
            "purchase",
            {
                "item": _required_item(parameters),
                "quantity": _required_positive_quantity(parameters),
                "location": _required_text(parameters, "location"),
            },
        )
    if action.operation == "transfer":
        return PavanActionRequest(
            action.action_id,
            "transfer",
            {
                "item": _required_item(parameters),
                "quantity": _required_positive_quantity(parameters),
                "source": _required_text(parameters, "source"),
                "destination": _required_text(parameters, "destination"),
            },
        )
    if action.operation == "reroute":
        return PavanActionRequest(
            action.action_id,
            "reroute",
            {
                "item": _required_item(parameters),
                "quantity": _required_positive_quantity(parameters),
                "from_location": _required_text(parameters, "from_location"),
                "to_location": _required_text(parameters, "to_location"),
            },
        )
    raise ActionConversionError(
        f"Unsupported Preethesh action mapping: tool={action.tool!r}, operation={action.operation!r}"
    )


def normalize_pavan_execution_result(result: Mapping[str, object]) -> ExecutionResult:
    """Normalize Pavan's standardized execution result without inventing state.

    Pavan's location-keyed inventory state lacks Nisar's required quantities,
    shipments, demand, and snapshot identifier. It is therefore deliberately
    represented as ``None`` rather than fabricated as ``CurrentState``.
    """
    success = result.get("success")
    if success is None:
        status = _required_text(result, "status")
        if status not in {"success", "failure"}:
            raise ActionConversionError("Pavan execution result status must be success or failure")
        success = status == "success"
    if not isinstance(success, bool):
        raise ActionConversionError("Pavan execution result requires boolean success")
    action_id = _required_text(result, "action_id")
    message = result.get("message")
    error = result.get("error")
    nested_result = result.get("result")
    if error is None and isinstance(nested_result, Mapping):
        error = nested_result.get("error")
    if message is not None and not isinstance(message, str):
        raise ActionConversionError("Pavan execution result message must be a string or null")
    if error is not None and not isinstance(error, str):
        raise ActionConversionError("Pavan execution result error must be a string or null")
    details = message or error or result.get("status")
    if not details:
        raise ActionConversionError("Pavan execution result requires message or error details")
    return ExecutionResult(
        succeeded=success,
        details=details,
        updated_state=None,
        action_unavailable=None,
        action_id=action_id,
    )


class PreetheshActionAdapter:
    """Converts Preethesh's selected-action dictionary to Nisar's contract."""

    def from_selected_action(self, selected_action: Mapping[str, object]) -> SelectedAction:
        parameters = selected_action.get("parameters")
        if not isinstance(parameters, Mapping):
            raise ActionConversionError("Preethesh selected action requires mapping parameters")
        return SelectedAction(
            action_id=_required_text(selected_action, "action_id"),
            tool=_required_text(selected_action, "tool"),
            operation=_required_text(selected_action, "operation"),
            parameters=dict(parameters),
        )


class PreetheshSelectorAdapter:
    """Adapts Preethesh's raw selector to Nisar's ``AlternativeSelector`` contract."""

    def __init__(
        self,
        selector: RawPreetheshSelector,
        action_adapter: PreetheshActionAdapter | None = None,
    ) -> None:
        self._selector = selector
        self._action_adapter = action_adapter or PreetheshActionAdapter()

    def select_action(
        self,
        goal: RecoveryGoal,
        plan: RecoveryPlan,
        state: CurrentState,
        excluded_action_ids: Sequence[str],
    ) -> SelectedAction | None:
        raw_action = self._selector.select_action(
            goal, plan, state, excluded_action_ids
        )
        if raw_action is None:
            return None
        return self._action_adapter.from_selected_action(raw_action)


class PavanExecutorAdapter:
    """Nisar protocol adapter around Pavan's ``Executor.execute_step`` callable."""

    def __init__(self, execute_step: Callable[[dict[str, object]], Mapping[str, object]]) -> None:
        self._execute_step = execute_step

    def execute(self, action: SelectedAction, state: CurrentState) -> ExecutionResult:
        del state  # Pavan's actual execute_step contract owns its Environment state.
        request = to_pavan_action(action)
        raw_result = self._execute_step(request.as_payload())
        normalized = normalize_pavan_execution_result(raw_result)
        if normalized.action_id != action.action_id:
            raise ActionConversionError("Pavan execution result action_id does not match selected action")
        return normalized


class MugilVerifierAdapter:
    """Nisar protocol adapter around Mugil's evaluator and a real request builder.

    The request builder is injected because Nisar must not fabricate Mugil's
    delivery, cost, carbon, or shipment evidence.
    """

    def __init__(
        self,
        evaluate_result: Callable[[dict[str, object]], Mapping[str, object]],
        build_evaluation_request: Callable[[RecoveryGoal, RecoveryPlan, ExecutionResult], dict[str, object]],
    ) -> None:
        self._evaluate_result = evaluate_result
        self._build_evaluation_request = build_evaluation_request

    def verify(
        self,
        goal: RecoveryGoal,
        plan: RecoveryPlan,
        execution: ExecutionResult,
    ) -> VerificationResult:
        if not execution.action_id:
            raise ActionConversionError("Mugil verification requires execution action_id")
        evaluation_request = self._build_evaluation_request(goal, plan, execution)
        if not isinstance(evaluation_request, dict):
            raise ActionConversionError("Mugil evaluation request builder must return a dictionary")
        evaluation_request.setdefault("action_id", execution.action_id)
        return normalize_mugil_result(
            self._evaluate_result(evaluation_request), execution.action_id
        )


def normalize_mugil_result(result: Mapping[str, object], action_id: str) -> VerificationResult:
    """Normalize Mugil's evaluator response while preserving action correlation."""
    _require_non_empty_text(action_id, "action_id")
    verified = result.get("verified")
    if not isinstance(verified, bool):
        raise ActionConversionError("Mugil result requires boolean verified")
    recommendation = _required_text(result, "recommendation")
    if recommendation not in {"CONTINUE", "REPLAN"}:
        raise ActionConversionError("Mugil recommendation must be CONTINUE or REPLAN")
    errors = result.get("errors", ())
    if not isinstance(errors, list) or not all(isinstance(error, str) for error in errors):
        raise ActionConversionError("Mugil errors must be a list of strings")
    details = "; ".join(errors) or _required_text(result, "status")
    return VerificationResult(
        succeeded=verified,
        details=details,
        requires_replan=recommendation == "REPLAN",
        action_id=action_id,
    )


def _required_item(parameters: Mapping[str, object]) -> str:
    item_id = parameters.get("item_id")
    item = parameters.get("item")
    if item_id is not None and item is not None and item_id != item:
        raise ActionConversionError("item_id and item disagree")
    return _required_text(parameters, "item_id" if item_id is not None else "item")


def _required_positive_quantity(parameters: Mapping[str, object]) -> int:
    quantity = parameters.get("quantity")
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
        raise ActionConversionError("quantity must be a positive integer")
    return quantity


def _required_text(values: Mapping[str, object], field: str) -> str:
    value = values.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ActionConversionError(f"Missing or invalid required parameter: {field}")
    return value


def _require_non_empty_text(value: object, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ActionConversionError(f"Missing or invalid required parameter: {field}")
