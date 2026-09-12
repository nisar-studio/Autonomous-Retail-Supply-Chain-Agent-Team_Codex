"""Nisar workflow tests using explicit teammate test doubles."""
from __future__ import annotations

import unittest
from agent.contracts import CurrentState, DemandLevel, DisruptionType, ExecutionResult, InventoryLevel, OutcomeStatus, SelectedAction, Shipment, VerificationResult
from agent.controller import RecoveryController
from agent.disruption_detector import detect_disruptions
from agent.monitor import Monitor
from agent.planner import create_recovery_goal

HEALTHY = CurrentState(inventory=(InventoryLevel("SKU-1", 10, 10),), shipments=(Shipment("SHIP-1", "SKU-1", 1, 1),), demand=(DemandLevel("SKU-1", 10, 10),), snapshot_id="healthy")
SHORTAGE = CurrentState(inventory=(InventoryLevel("SKU-1", 3, 10),), snapshot_id="shortage")

class FixedSource:
    def __init__(self, state): self.state = state
    def get_current_state(self): return self.state
class ScriptedSelector:
    def __init__(self, actions): self.actions = iter(actions)
    def select_action(self, goal, plan, state, excluded_action_ids): return next(self.actions, None)
class ScriptedExecutor:
    def __init__(self, results): self.results = iter(results)
    def execute(self, action, state): return next(self.results)
class ScriptedVerifier:
    def __init__(self, results): self.results = iter(results)
    def verify(self, goal, plan, execution): return next(self.results)
def action(identifier): return SelectedAction(identifier, "transfer", f"Test action {identifier}")

class DetectionAndPlanningTests(unittest.TestCase):
    def test_no_disruption(self): self.assertEqual(detect_disruptions(HEALTHY), ())
    def test_inventory_shortage_detected(self): self.assertEqual(detect_disruptions(SHORTAGE)[0].disruption_type, DisruptionType.INVENTORY_SHORTAGE)
    def test_shipment_delay_detected(self): self.assertEqual(detect_disruptions(CurrentState(shipments=(Shipment("SHIP-2", "SKU-2", 5, 3),)))[0].disruption_type, DisruptionType.SHIPMENT_DELAY)
    def test_recovery_goal_created(self):
        goal = create_recovery_goal(SHORTAGE, detect_disruptions(SHORTAGE)[0])
        self.assertEqual((goal.disruption_type, goal.affected_ids), (DisruptionType.INVENTORY_SHORTAGE, ("SKU-1",)))

class ControllerTests(unittest.TestCase):
    def build(self, actions, executions, verifications, retries=2):
        return RecoveryController(Monitor(FixedSource(SHORTAGE)), ScriptedSelector(actions), ScriptedExecutor(executions), ScriptedVerifier(verifications), retries)
    def test_successful_recovery_workflow(self):
        outcome = self.build([action("a1")], [ExecutionResult(True, "executed")], [VerificationResult(True, "verified")]).recover()
        self.assertEqual((outcome.status, outcome.attempts), (OutcomeStatus.RECOVERED, 1))
    def test_execution_failure_causes_replanning(self):
        outcome = self.build([action("a1"), action("a2")], [ExecutionResult(False, "failed"), ExecutionResult(True, "executed")], [VerificationResult(True, "verified")], 1).recover()
        self.assertEqual((outcome.status, outcome.attempts), (OutcomeStatus.RECOVERED, 2))
    def test_verification_failure_causes_replanning(self):
        outcome = self.build([action("a1"), action("a2")], [ExecutionResult(True, "executed"), ExecutionResult(True, "executed")], [VerificationResult(False, "not achieved", True), VerificationResult(True, "verified")], 1).recover()
        self.assertEqual((outcome.status, outcome.attempts), (OutcomeStatus.RECOVERED, 2))
    def test_no_feasible_action_is_safe(self): self.assertEqual(self.build([], [], []).recover().status, OutcomeStatus.NO_FEASIBLE_ACTION)
    def test_maximum_replanning_attempts_stops_loop(self):
        outcome = self.build([action("a1"), action("a2")], [ExecutionResult(False, "failed"), ExecutionResult(False, "failed")], [], 1).recover()
        self.assertEqual((outcome.status, outcome.attempts), (OutcomeStatus.REPLAN_LIMIT_REACHED, 2))
