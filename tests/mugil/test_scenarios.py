from Mugil.evaluation.scenarios import (
    shipment_delay_scenario,
    vendor_unavailable_scenario,
    route_unavailable_scenario,
    no_feasible_option_scenario,
    get_all_scenarios,
)


def test_shipment_delay_scenario():
    scenario = shipment_delay_scenario()

    assert scenario["scenario"] == "shipment_delay"
    assert scenario["actual"]["shipment_delayed"] is True
    assert scenario["expected_outcome"] == "RECOVERY_SUCCESS"


def test_vendor_unavailable_scenario():
    scenario = vendor_unavailable_scenario()

    assert scenario["scenario"] == "vendor_unavailable"
    assert scenario["actual"]["supplier_available"] is False
    assert scenario["expected_outcome"] == "REPLAN_SUCCESS"


def test_route_unavailable_scenario():
    scenario = route_unavailable_scenario()

    assert scenario["scenario"] == "route_unavailable"
    assert scenario["actual"]["route_available"] is False
    assert scenario["actual"]["alternate_route_available"] is True
    assert scenario["expected_outcome"] == "ALTERNATE_ROUTE_SUCCESS"


def test_no_feasible_option_scenario():
    scenario = no_feasible_option_scenario()

    assert scenario["scenario"] == "no_feasible_option"
    assert scenario["actual"]["feasible"] is False
    assert scenario["expected_outcome"] == "FAILURE_REPORTED"


def test_all_scenarios():
    scenarios = get_all_scenarios()

    assert len(scenarios) == 4