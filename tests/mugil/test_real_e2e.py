from Nisar.agent.adapters import MugilVerifierAdapter, PavanExecutorAdapter, PreetheshSelectorAdapter
from Nisar.agent.contracts import CurrentState, InventoryLevel
from Nisar.agent.controller import RecoveryController
from Nisar.agent.monitor import Monitor
from Pavan.environment import Environment
from Pavan.executor import Executor
from Preethesh.tools.alternatives import AlternativeGenerator, AlternativeSelector
from Mugil.evaluation.evaluator import evaluate_result


def build_evaluation_request(goal, plan, execution):
    evidence = dict(execution.execution_evidence)
    result = evidence.get("result", {})

    if not isinstance(result, dict):
        result = {}

    constraints = dict(goal.constraints)

    if "shortfall_quantity" in constraints:
        constraints["required_quantity"] = constraints["shortfall_quantity"]

    expected = {
        key: constraints[key]
        for key in ("required_quantity", "deadline", "max_cost", "budget", "carbon_limit")
        if key in constraints
    }

    return {
        "action_id": execution.action_id,
        "goal": goal,
        "expected": expected,
        "actual": {
            "delivered_quantity": result.get("delivered_quantity"),
            "delivery_time": result.get("delivery_time"),
            "total_cost": result.get("total_cost"),
            "carbon_emission": result.get("carbon_emission"),
        },
    }


def test_real_nisar_preethesh_pavan_mugil_e2e():
    initial_state = CurrentState(
        snapshot_id="e2e-shortage",
        inventory=(InventoryLevel("SKU-001", 2, 5),),
        shipments=(),
        demand=(),
    )

    class ShortageSource:
        def get_current_state(self):
            return initial_state

    monitor = Monitor(ShortageSource())

    supplier_getter = lambda item_id, location: [
        {
            "action_id": "purchase-1",
            "supplier_id": "supplier-1",
            "status": "available",
            "capacity": 100,
        }
    ]

    route_getter = lambda item_id, location: []

    generator = AlternativeGenerator()

    raw_selector = AlternativeSelector(
        generator,
        supplier_getter,
        route_getter,
    )

    selector = PreetheshSelectorAdapter(raw_selector)

    environment = Environment()
    pavan = Executor(environment)

    executor = PavanExecutorAdapter(pavan.execute_step)

    verifier = MugilVerifierAdapter(
        evaluate_result,
        build_evaluation_request,
    )

    controller = RecoveryController(
        monitor=monitor,
        alternative_selector=selector,
        executor=executor,
        verifier=verifier,
        max_replanning_attempts=2,
        recovery_location="warehouse",
    )

    outcome = controller.recover()

    assert outcome.status.value == "recovered"
    assert outcome.action is not None
    assert outcome.action.action_id == "purchase-1"
    assert outcome.goal is not None
    assert outcome.context.active_goal is not None
