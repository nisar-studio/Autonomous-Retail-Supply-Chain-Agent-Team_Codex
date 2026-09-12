from Mugil.robustness.robustness import check_robustness


def test_robustness_passes_for_normal_execution():
    result = {
        "actual": {
            "supplier_available": True,
            "shipment_delayed": False,
            "inventory_available": True,
            "tool_error": False,
            "feasible": True
        }
    }

    output = check_robustness(result)

    assert output["robust"] is True
    assert output["status"] == "PASS"
    assert output["recommendation"] == "CONTINUE"
    assert output["issues"] == []


def test_robustness_fails_when_supplier_unavailable():
    result = {
        "actual": {
            "supplier_available": False
        }
    }

    output = check_robustness(result)

    assert output["robust"] is False
    assert output["status"] == "FAIL"
    assert output["recommendation"] == "REPLAN"
    assert "Supplier unavailable." in output["issues"]


def test_robustness_fails_when_shipment_is_delayed():
    result = {
        "actual": {
            "shipment_delayed": True
        }
    }

    output = check_robustness(result)

    assert output["robust"] is False
    assert output["status"] == "FAIL"
    assert output["recommendation"] == "REPLAN"
    assert "Shipment delayed." in output["issues"]


def test_robustness_fails_when_inventory_is_unavailable():
    result = {
        "actual": {
            "inventory_available": False
        }
    }

    output = check_robustness(result)

    assert output["robust"] is False
    assert output["status"] == "FAIL"
    assert output["recommendation"] == "REPLAN"
    assert "Required inventory unavailable." in output["issues"]


def test_robustness_fails_when_tool_has_error():
    result = {
        "actual": {
            "tool_error": True
        }
    }

    output = check_robustness(result)

    assert output["robust"] is False
    assert output["status"] == "FAIL"
    assert output["recommendation"] == "REPLAN"
    assert "Tool or external API failure." in output["issues"]


def test_robustness_fails_when_solution_is_not_feasible():
    result = {
        "actual": {
            "feasible": False
        }
    }

    output = check_robustness(result)

    assert output["robust"] is False
    assert output["status"] == "FAIL"
    assert output["recommendation"] == "REPLAN"
    assert "No feasible solution found." in output["issues"]


def test_robustness_detects_multiple_failures():
    result = {
        "actual": {
            "supplier_available": False,
            "shipment_delayed": True,
            "inventory_available": False,
            "tool_error": True,
            "feasible": False
        }
    }

    output = check_robustness(result)

    assert output["robust"] is False
    assert output["status"] == "FAIL"
    assert output["recommendation"] == "REPLAN"
    assert len(output["issues"]) == 5


def test_robustness_fails_when_result_is_none():
    output = check_robustness(None)

    assert output["robust"] is False
    assert output["status"] == "FAIL"
    assert output["recommendation"] == "REPLAN"