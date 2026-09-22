import sys
import json
import math
import networkx as nx


# ============================================================
# CONFIGURATION
# ============================================================

MAX_DISTANCE = 500.0


# ============================================================
# DISTANCE CALCULATION
# ============================================================

def calculate_distance(node_a, node_b):
    x1, y1 = node_a
    x2, y2 = node_b

    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


# ============================================================
# BUILD COMMUNICATION GRAPH
# ============================================================

def build_network_graph(coordinates):
    graph = nx.Graph()

    for node in coordinates:
        graph.add_node(node)

    nodes = list(coordinates.keys())

    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            node_a = nodes[i]
            node_b = nodes[j]

            distance = calculate_distance(
                coordinates[node_a],
                coordinates[node_b]
            )

            if distance <= MAX_DISTANCE:
                graph.add_edge(node_a, node_b, distance=distance)

    return graph


# ============================================================
# BUILD DISTANCE-2 CONFLICT GRAPH
# ============================================================

def build_conflict_graph(network_graph):
    conflict_graph = nx.Graph()

    for node in network_graph.nodes:
        conflict_graph.add_node(node)

    nodes = list(network_graph.nodes)

    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            node_a = nodes[i]
            node_b = nodes[j]

            # Direct 1-hop conflict
            if network_graph.has_edge(node_a, node_b):
                conflict_graph.add_edge(node_a, node_b)

            # 2-hop conflict
            elif set(network_graph.neighbors(node_a)) & set(
                network_graph.neighbors(node_b)
            ):
                conflict_graph.add_edge(node_a, node_b)

    return conflict_graph


# ============================================================
# TDMA SCHEDULE USING GREEDY COLORING
# ============================================================
def create_schedule(conflict_graph):

    strategies = [
        "largest_first",
        "smallest_last",
        "saturation_largest_first"
    ]

    best_schedule = None
    best_slots = float("inf")

    for strategy in strategies:

        coloring = nx.coloring.greedy_color(
            conflict_graph,
            strategy=strategy
        )

        total_slots = max(coloring.values()) + 1

        if total_slots < best_slots:
            best_slots = total_slots
            best_schedule = coloring

    schedule = {}

    for node in conflict_graph.nodes:
        schedule[node] = best_schedule[node]

    return schedule
# ============================================================
# CONVERT SCHEDULE TO MATRIX
# ============================================================

def create_schedule_matrix(schedule, nodes):
    if not schedule:
        return []

    total_slots = max(schedule.values()) + 1

    matrix = []

    for slot in range(total_slots):
        row = []

        for node in nodes:
            if schedule[node] == slot:
                row.append(1)
            else:
                row.append(0)

        matrix.append(row)

    return matrix


# ============================================================
# VERIFY NO CONFLICTS
# ============================================================

def verify_schedule(conflict_graph, schedule):
    for node_a, node_b in conflict_graph.edges:

        if schedule[node_a] == schedule[node_b]:
            return False, node_a, node_b

    return True, None, None


# ============================================================
# PRINT RESULTS
# ============================================================

def print_results(network_graph, conflict_graph, schedule, matrix):
    nodes = list(schedule.keys())

    print("\n==============================")
    print("VMN TDMA SCHEDULE OPTIMIZER")
    print("==============================")

    print("\n1. Communication Graph")
    print("------------------------------")

    print("Nodes:", len(network_graph.nodes))
    print("Links:", len(network_graph.edges))

    for node_a, node_b, data in network_graph.edges(data=True):
        print(
            f"{node_a} <-> {node_b} "
            f"({data['distance']:.2f} m)"
        )

    print("\n2. Distance-2 Conflict Graph")
    print("------------------------------")

    print("Conflict edges:", len(conflict_graph.edges))

    print("\n3. TDMA Schedule")
    print("------------------------------")

    total_slots = len(matrix)

    print("Total Slots:", total_slots)

    print("\nSchedule Matrix")
    print("Slot | " + " ".join(nodes))

    for slot_number, row in enumerate(matrix):
        print(
            f"{slot_number + 1:4} | "
            + " ".join(map(str, row))
        )

    print("\n4. Node -> Slot Mapping")
    print("------------------------------")

    for node in nodes:
        print(f"{node} -> Slot {schedule[node] + 1}")

    print("\n5. Schedule Verification")
    print("------------------------------")

    valid, node_a, node_b = verify_schedule(
        conflict_graph,
        schedule
    )

    if valid:
        print("SUCCESS: No scheduling conflicts found.")
    else:
        print(
            f"ERROR: Conflict between {node_a} and {node_b}"
        )
        print("\n6. Optimization Metrics")
    print("------------------------------")

    print("Total Nodes:", len(network_graph.nodes))
    print("Communication Links:", len(network_graph.edges))
    print("Conflict Links:", len(conflict_graph.edges))
    print("Total TDMA Slots:", total_slots)

    if total_slots > 0:
        average_reuse = len(nodes) / total_slots
        print(f"Average Nodes per Slot: {average_reuse:.2f}")

    print("Spatial Reuse: Enabled")


# ============================================================
# MAIN PROGRAM
# ============================================================
def main():

    if len(sys.argv) > 1:

        try:
            input_source = sys.argv[1]

            # If a JSON file is provided
            if input_source.endswith(".json"):

                with open(input_source, "r") as file:
                    coordinates = json.load(file)

            # Otherwise, treat the argument as direct JSON
            else:

                json_input = " ".join(sys.argv[1:]).strip()

                # Handle PowerShell escaped JSON
                json_input = json_input.replace('\\"', '"')

                if (
                    len(json_input) >= 2
                    and json_input[0] == json_input[-1]
                    and json_input[0] in ["'", '"']
                ):
                    json_input = json_input[1:-1]

                coordinates = json.loads(json_input)

        except (json.JSONDecodeError, FileNotFoundError) as e:

            print("ERROR: Invalid JSON input.")
            print("Details:", e)
            sys.exit(1)

    else:

        coordinates = {
            "Node_01": [0, 0],
            "Node_02": [300, 0],
            "Node_03": [800, 0],
            "Node_04": [300, 300],
            "Node_05": [800, 300],
            "Node_06": [1200, 0],
            "Node_07": [1200, 300],
            "Node_08": [1500, 300],
            "Node_09": [1800, 300],
            "Node_10": [1500, 600],
            "Node_11": [1800, 600],
            "Node_12": [2100, 600],
            "Node_13": [2400, 600],
            "Node_14": [2100, 900],
            "Node_15": [2400, 900],
            "Node_16": [2700, 900]
        }

    network_graph = build_network_graph(coordinates)

    conflict_graph = build_conflict_graph(network_graph)

    schedule = create_schedule(conflict_graph)

    nodes = list(coordinates.keys())

    matrix = create_schedule_matrix(
        schedule,
        nodes
    )

    print_results(
        network_graph,
        conflict_graph,
        schedule,
        matrix
    )
# ============================================================
# START PROGRAM
# ============================================================

if __name__ == "__main__":
    main()