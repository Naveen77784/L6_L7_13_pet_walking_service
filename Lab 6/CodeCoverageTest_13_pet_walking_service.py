import pytest

from pet_walking_service import inspect_gps_collars, process_walking_routes


def test_invalid_routes_or_fee():
    with pytest.raises(ValueError):
        process_walking_routes("not-a-list", 1)
    with pytest.raises(ValueError):
        process_walking_routes([], -1)


def test_unconfirmed_and_unsupported_route():
    result = process_walking_routes([
        {"route_confirmed": False},
        {"route_confirmed": True, "session_type": "unknown", "walks": []},
    ], 5)
    assert result == {"total_revenue": 0.0, "status": "ZERO_EARNINGS"}


@pytest.mark.parametrize("session,base", [("standard_60", 35), ("standard_30", 22), ("express_15", 14)])
def test_session_types_and_weekend(session, base):
    result = process_walking_routes([{
        "route_confirmed": True, "session_type": session, "is_weekend": True,
        "walks": [{"num_pets": 1, "needs_meds": True}],
    }], 5)
    assert result == {"total_revenue": base + 5 + 6 + 5, "status": "COMPLETED"}


def test_invalid_pet_count_and_aggression_modes():
    result = process_walking_routes([
        {"route_confirmed": True, "session_type": "express_15", "walks": [
            {"num_pets": 0}, {"num_pets": 1, "aggression_alert": True},
            {"num_pets": 4},
        ]},
        {"route_confirmed": True, "session_type": "standard_60", "walks": [
            {"num_pets": 1, "aggression_alert": True},
        ]},
    ], 0)
    assert result == {"total_revenue": 41.4, "status": "COMPLETED"}


def test_incident_audit_and_zero_earnings():
    routes = [{"route_confirmed": True, "session_type": "bad", "walks": []} for _ in range(5)]
    assert process_walking_routes(routes, 0)["status"] == "INCIDENT_AUDIT"
    assert process_walking_routes([], 0)["status"] == "ZERO_EARNINGS"


def test_gps_empty_recovery_and_lost_streak():
    assert inspect_gps_collars([]) == "NO_DATA"
    assert inspect_gps_collars([[10, 20, 19, 21], [1, 2]]) == "LOST_SIGNAL_ALERT"
    assert inspect_gps_collars([[10, 20, 19, 21]]) == "ONLINE"
