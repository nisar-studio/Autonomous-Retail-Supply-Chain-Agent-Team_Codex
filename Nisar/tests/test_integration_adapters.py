"""Unit tests for Nisar-owned finalized-contract conversions."""
from __future__ import annotations

import unittest

from agent.adapters import (
    ActionConversionError,
    PavanExecutorAdapter,
    PreetheshActionAdapter,
    PreetheshSelectorAdapter,
    normalize_mugil_result,
    normalize_pavan_execution_result,
    to_pavan_action,
)
from agent.contracts import (
    CurrentState,
    DisruptionType,
    ExecutionResult,
    InventoryLevel,
    OutcomeStatus,
    RecoveryGoal,
    RecoveryPlan,
    SelectedAction,
    VerificationResult,
)
from agent.controller import RecoveryController
from agent.monitor import Monitor


def selected(action_id: str, tool: str, operation: str, parameters: dict) -> SelectedAction:
    return SelectedAction(
        action_id=action_id,
        tool=tool,
        operation=operation,
        parameters=parameters,
    )


class ActionConversionTests(unittest.TestCase):
    def test_purchase_conversion_preserves_action_id(self):
        request = to_pavan_action(selected("A001", "order", "create", {
            "order_id": "ORD001", "item_id": "laptop", "quantity": 10,
            "supplier_id": "SUP001", "location": "warehouse",
        }))
        self.assertEqual(request.action_id, "A001")
        self.assertEqual(request.as_payload(), {
            "action_id": "A001",
            "action": "purchase",
            "params": {"item": "laptop", "quantity": 10, "location": "warehouse"},
        })

    def test_transfer_conversion(self):
        request = to_pavan_action(selected("A002", "inventory", "transfer", {
            "item": "laptop", "quantity": 2, "source": "warehouse", "destination": "store",
        }))
        self.assertEqual(request.as_payload()["action"], "transfer")
        self.assertEqual(request.params["source"], "warehouse")

    def test_reroute_conversion(self):
        request = to_pavan_action(selected("A003", "route", "reroute", {
            "item_id": "laptop", "quantity": 2, "from_location": "store", "to_location": "office",
        }))
        self.assertEqual(request.as_payload()["action"], "reroute")
        self.assertEqual(request.params["to_location"], "office")

    def test_purchase_missing_location_is_rejected(self):
        with self.assertRaisesRegex(ActionConversionError, "location"):
            to_pavan_action(selected("A004", "order", "create", {
                "item_id": "laptop", "quantity": 1,
            }))

    def test_transfer_missing_source_or_destination_is_rejected(self):
        with self.assertRaisesRegex(ActionConversionError, "source"):
            to_pavan_action(selected("A005", "inventory", "transfer", {
                "item": "laptop", "quantity": 1, "destination": "store",
            }))

    def test_reroute_missing_locations_are_rejected(self):
        with self.assertRaisesRegex(ActionConversionError, "from_location"):
            to_pavan_action(selected("A006", "route", "reroute", {
                "item": "laptop", "quantity": 1, "to_location": "office",
            }))


class ResultNormalizationTests(unittest.TestCase):
    def test_pavan_success_normalizes(self):
        result = normalize_pavan_execution_result({
            "action_id": "A007", "success": True, "status": "success",
            "action": "purchase", "message": "Action executed successfully",
            "updated_state": {}, "error": None,
        })
        self.assertTrue(result.succeeded)
        self.assertEqual(result.details, "Action executed successfully")
        self.assertEqual(result.action_id, "A007")
        self.assertIsNone(result.updated_state)

    def test_pavan_failure_normalizes(self):
        result = normalize_pavan_execution_result({
            "action_id": "A008", "success": False, "status": "failure",
            "action": "transfer", "message": "", "updated_state": {}, "error": "Insufficient stock",
        })
        self.assertFalse(result.succeeded)
        self.assertEqual(result.details, "Insufficient stock")
        self.assertIsNone(result.action_unavailable)

    def test_actual_pavan_step_result_normalizes(self):
        result = normalize_pavan_execution_result({
            "action_id": "A008B", "action": "purchase", "status": "success",
            "result": {"action": "purchase", "status": "success"}, "state": {},
        })
        self.assertTrue(result.succeeded)
        self.assertEqual(result.details, "success")
        self.assertEqual(result.action_id, "A008B")

    def test_mugil_continue_does_not_require_replan(self):
        result = normalize_mugil_result({
            "verified": True, "status": "PASS", "recommendation": "CONTINUE", "errors": [],
        }, "A009")
        self.assertTrue(result.succeeded)
        self.assertFalse(result.requires_replan)
        self.assertEqual(result.action_id, "A009")

    def test_mugil_replan_requires_replan(self):
        result = normalize_mugil_result({
            "verified": False, "status": "FAIL", "recommendation": "REPLAN", "errors": ["Quantity unmet"],
        }, "A010")
        self.assertFalse(result.succeeded)
        self.assertTrue(result.requires_replan)
        self.assertEqual(result.details, "Quantity unmet")


class WiringBridgeTests(unittest.TestCase):
    def test_preethesh_to_pavan_bridge_preserves_action_id(self):
        selected_action = PreetheshActionAdapter().from_selected_action({
            "action_id": "A011", "tool": "order", "operation": "create",
            "parameters": {"item_id": "laptop", "quantity": 1, "location": "warehouse"},
        })

        def execute_step(payload):
            self.assertEqual(payload, {
                "action_id": "A011",
                "action": "purchase",
                "params": {"item": "laptop", "quantity": 1, "location": "warehouse"},
            })
            return {"action_id": "A011", "action": "purchase", "status": "success", "result": {}, "state": {}}

        result = PavanExecutorAdapter(execute_step).execute(selected_action, None)
        self.assertTrue(result.succeeded)
        self.assertEqual(result.action_id, "A011")


class RecordingRawSelector:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def select_action(self, goal, plan, state, excluded_action_ids):
        self.calls.append((goal, plan, state, excluded_action_ids))
        return self.result


class FixedStateSource:
    def __init__(self, state):
        self.state = state

    def get_current_state(self):
        return self.state


class SuccessfulExecutor:
    def __init__(self):
        self.action = None

    def execute(self, action, state):
        self.action = action
        return ExecutionResult(True, "executed", action_id=action.action_id)


class SuccessfulVerifier:
    def verify(self, goal, plan, execution):
        return VerificationResult(True, "verified", action_id=execution.action_id)


class PreetheshSelectorAdapterTests(unittest.TestCase):
    def setUp(self):
        self.goal = RecoveryGoal(
            "goal-1", "Restore inventory.", ("SKU-1",),
            DisruptionType.INVENTORY_SHORTAGE,
        )
        self.plan = RecoveryPlan(self.goal, "Find an alternative.", "snapshot-1")
        self.state = CurrentState(snapshot_id="snapshot-1")
        self.raw_action = {
            "action_id": "A012",
            "tool": "order",
            "operation": "create",
            "parameters": {"item_id": "SKU-1", "quantity": 7, "location": "store-1"},
        }

    def test_raw_action_is_converted_without_losing_contract_fields(self):
        raw_selector = RecordingRawSelector(self.raw_action)
        selected_action = PreetheshSelectorAdapter(raw_selector).select_action(
            self.goal, self.plan, self.state, ("A011",)
        )

        self.assertEqual(selected_action.action_id, self.raw_action["action_id"])
        self.assertEqual(selected_action.tool, self.raw_action["tool"])
        self.assertEqual(selected_action.operation, self.raw_action["operation"])
        self.assertEqual(selected_action.parameters, self.raw_action["parameters"])

    def test_none_is_returned_unchanged(self):
        raw_selector = RecordingRawSelector(None)
        self.assertIsNone(
            PreetheshSelectorAdapter(raw_selector).select_action(
                self.goal, self.plan, self.state, ()
            )
        )

    def test_excluded_action_ids_are_delegated_unchanged(self):
        excluded_action_ids = ("A010", "A011")
        raw_selector = RecordingRawSelector(self.raw_action)
        PreetheshSelectorAdapter(raw_selector).select_action(
            self.goal, self.plan, self.state, excluded_action_ids
        )

        self.assertIs(raw_selector.calls[0][3], excluded_action_ids)

    def test_controller_consumes_the_converted_selected_action(self):
        raw_selector = RecordingRawSelector(self.raw_action)
        executor = SuccessfulExecutor()
        shortage_state = CurrentState(
            inventory=(InventoryLevel("SKU-1", 3, 10),), snapshot_id="shortage",
        )
        controller = RecoveryController(
            Monitor(FixedStateSource(shortage_state)),
            PreetheshSelectorAdapter(raw_selector),
            executor,
            SuccessfulVerifier(),
        )

        outcome = controller.recover()

        self.assertEqual(outcome.status, OutcomeStatus.RECOVERED)
        self.assertIsInstance(executor.action, SelectedAction)
        self.assertEqual(executor.action.action_id, "A012")
