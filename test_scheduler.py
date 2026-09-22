from scheduler import (
    build_network_graph,
    build_conflict_graph,
    create_schedule,
    verify_schedule
)


def test_scheduler():

    coordinates = {
        "Node_01": [0, 0],
        "Node_02": [300, 0],
        "Node_03": [800, 0],
        "Node_04": [300, 300],
        "Node_05": [800, 300]
    }

    network = build_network_graph(coordinates)
    conflicts = build_conflict_graph(network)
    schedule = create_schedule(conflicts)

    valid, node_a, node_b = verify_schedule(
        conflicts,
        schedule
    )

    assert valid

    print("TEST PASSED")
    print("Nodes:", len(coordinates))
    print("Communication Links:", len(network.edges))
    print("Conflict Links:", len(conflicts.edges))
    print("Slots:", max(schedule.values()) + 1)


if __name__ == "__main__":
    test_scheduler()