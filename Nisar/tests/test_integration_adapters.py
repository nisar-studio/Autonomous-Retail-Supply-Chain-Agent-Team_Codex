"""Unit tests for Nisar-owned finalized-contract conversions."""
from __future__ import annotations

import unittest

from agent.adapters import (
    ActionConversionError,
    PavanExecutorAdapter,
    PreetheshActionAdapter,
    normalize_mugil_result,
    normalize_pavan_execution_result,
    to_pavan_action,
)
from agent.contracts import SelectedAction


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
