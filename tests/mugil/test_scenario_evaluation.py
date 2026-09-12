from Mugil.evaluation.scenarios import (
    shipment_delay_scenario,
    vendor_unavailable_scenario,
    route_unavailable_scenario,
    no_feasible_option_scenario,
)


def test_shipment_delay_recovery_success():
    scenario = shipment_delay_scenario()

    assert scenario["actual"]["shipment_delayed"] is True
    assert scenario["actual"]["recovery_available"] is True
    assert scenario["expected_outcome"] == "RECOVERY_SUCCESS"


def test_vendor_unavailable_requires_replan():
    scenario = vendor_unavailable_scenario()

    assert scenario["actual"]["supplier_available"] is False
    assert scenario["actual"]["alternative_supplier_available"] is True
    assert scenario["expected_outcome"] == "REPLAN_SUCCESS"


def test_route_unavailable_supports_alternate_route():
    scenario = route_unavailable_scenario()

    assert scenario["actual"]["route_available"] is False
    assert scenario["actual"]["alternate_route_available"] is True
    assert scenario["expected_outcome"] == "ALTERNATE_ROUTE_SUCCESS"


def test_no_feasible_option_reports_failure():
    scenario = no_feasible_option_scenario()

    assert scenario["actual"]["feasible"] is False
    assert scenario["expected_outcome"] == "FAILURE_REPORTED"


def test_all_scenarios_have_required_evaluation_fields():
    scenarios = [
        shipment_delay_scenario(),
        vendor_unavailable_scenario(),
        route_unavailable_scenario(),
        no_feasible_option_scenario(),
    ]

    for scenario in scenarios:
        assert "scenario" in scenario
        assert "goal" in scenario
        assert "actual" in scenario
        assert "expected_outcome" in scenario
