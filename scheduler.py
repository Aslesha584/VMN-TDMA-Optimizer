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
    """
    Calculate Euclidean distance between two nodes.
    Coordinates are represented as [x, y].
    """

    x1, y1 = node_a
    x2, y2 = node_b

    return math.sqrt(
        (x2 - x1) ** 2 +
        (y2 - y1) ** 2
    )


# ============================================================
# INPUT VALIDATION
# ============================================================

def validate_coordinates(coordinates):
    """
    Validate that the input contains valid node coordinates.
    """

    if not isinstance(coordinates, dict):
        raise ValueError("Input must be a JSON object.")

    if not coordinates:
        raise ValueError("At least one node is required.")

    for node, position in coordinates.items():

        if not isinstance(node, str):
            raise ValueError("Node names must be strings.")

        if (
            not isinstance(position, list)
            or len(position) != 2
        ):
            raise ValueError(
                f"{node} must have exactly two coordinates."
            )

        if not all(
            isinstance(value, (int, float))
            for value in position
        ):
            raise ValueError(
                f"{node} coordinates must be numeric."
            )


# ============================================================
# BUILD COMMUNICATION GRAPH
# ============================================================

def build_network_graph(coordinates):
    """
    Build the communication graph.

    Two nodes are connected when their distance
    is less than or equal to 500 meters.
    """

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
                graph.add_edge(
                    node_a,
                    node_b,
                    distance=distance
                )

    return graph


# ============================================================
# BUILD DISTANCE-2 CONFLICT GRAPH
# ============================================================

def build_conflict_graph(network_graph):
    """
    Build the distance-2 conflict graph.

    Two nodes conflict when:

    1. They have a direct communication link, or
    2. They share a common neighbor.

    This handles both direct interference
    and hidden/two-hop interference.
    """

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

                conflict_graph.add_edge(
                    node_a,
                    node_b
                )

            # 2-hop conflict
            else:

                common_neighbors = (
                    set(network_graph.neighbors(node_a))
                    &
                    set(network_graph.neighbors(node_b))
                )

                if common_neighbors:
                    conflict_graph.add_edge(
                        node_a,
                        node_b
                    )

    return conflict_graph


# ============================================================
# TDMA SCHEDULE USING GREEDY COLORING
# ============================================================

def create_schedule(conflict_graph):
    """
    Generate a TDMA schedule using multiple
    greedy graph-coloring strategies.

    Each color represents one TDMA slot.

    The strategy producing the fewest slots
    is selected.
    """

    if len(conflict_graph.nodes) == 0:
        return {}, None

    strategies = [
        "largest_first",
        "smallest_last",
        "saturation_largest_first"
    ]

    best_schedule = None
    best_strategy = None
    best_slots = float("inf")

    strategy_results = {}

    for strategy in strategies:

        coloring = nx.coloring.greedy_color(
            conflict_graph,
            strategy=strategy
        )

        total_slots = max(coloring.values()) + 1

        strategy_results[strategy] = total_slots

        if total_slots < best_slots:

            best_slots = total_slots
            best_schedule = coloring
            best_strategy = strategy

    return best_schedule, best_strategy


# ============================================================
# CONVERT SCHEDULE TO MATRIX
# ============================================================

def create_schedule_matrix(schedule, nodes):
    """
    Convert the node-to-slot schedule into
    a Slot x Node binary matrix.
    """

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
    """
    Verify that no conflicting nodes share
    the same TDMA slot.
    """

    for node_a, node_b in conflict_graph.edges:

        if schedule[node_a] == schedule[node_b]:

            return False, node_a, node_b

    return True, None, None


# ============================================================
# PRINT RESULTS
# ============================================================

def print_results(
    network_graph,
    conflict_graph,
    schedule,
    matrix,
    selected_strategy
):

    nodes = list(schedule.keys())

    print("\n==============================")
    print("VMN TDMA SCHEDULE OPTIMIZER")
    print("==============================")

    # --------------------------------------------------------
    # Communication Graph
    # --------------------------------------------------------

    print("\n1. Communication Graph")
    print("------------------------------")

    print("Nodes:", len(network_graph.nodes))
    print("Links:", len(network_graph.edges))

    for node_a, node_b, data in network_graph.edges(
        data=True
    ):

        print(
            f"{node_a} <-> {node_b} "
            f"({data['distance']:.2f} m)"
        )

    # --------------------------------------------------------
    # Conflict Graph
    # --------------------------------------------------------

    print("\n2. Distance-2 Conflict Graph")
    print("------------------------------")

    print(
        "Conflict edges:",
        len(conflict_graph.edges)
    )

    # --------------------------------------------------------
    # TDMA Schedule
    # --------------------------------------------------------

    print("\n3. TDMA Schedule")
    print("------------------------------")

    total_slots = len(matrix)

    print("Total Slots:", total_slots)

    print("\nSchedule Matrix")

    print(
        "Slot | " +
        " ".join(nodes)
    )

    for slot_number, row in enumerate(matrix):

        print(
            f"{slot_number + 1:4} | "
            +
            " ".join(map(str, row))
        )

    # --------------------------------------------------------
    # Node -> Slot Mapping
    # --------------------------------------------------------

    print("\n4. Node -> Slot Mapping")
    print("------------------------------")

    for node in nodes:

        print(
            f"{node} -> Slot "
            f"{schedule[node] + 1}"
        )

    # --------------------------------------------------------
    # Verification
    # --------------------------------------------------------

    print("\n5. Schedule Verification")
    print("------------------------------")

    valid, node_a, node_b = verify_schedule(
        conflict_graph,
        schedule
    )

    if valid:

        print(
            "SUCCESS: No scheduling conflicts found."
        )

    else:

        print(
            f"ERROR: Conflict between "
            f"{node_a} and {node_b}"
        )

    # --------------------------------------------------------
    # Optimization Metrics
    # --------------------------------------------------------

    print("\n6. Optimization Metrics")
    print("------------------------------")

    print(
        "Total Nodes:",
        len(network_graph.nodes)
    )

    print(
        "Communication Links:",
        len(network_graph.edges)
    )

    print(
        "Conflict Links:",
        len(conflict_graph.edges)
    )

    print(
        "Total TDMA Slots:",
        total_slots
    )

    print(
        "Selected Coloring Strategy:",
        selected_strategy
    )

    if total_slots > 0:

        average_reuse = (
            len(nodes) / total_slots
        )

        print(
            f"Average Nodes per Slot: "
            f"{average_reuse:.2f}"
        )

    print("Spatial Reuse: Enabled")


# ============================================================
# DEFAULT NETWORK
# ============================================================

def get_default_coordinates():
    """
    Return the default 16-node network
    provided for the project.
    """

    return {

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


# ============================================================
# LOAD INPUT
# ============================================================

def load_coordinates():
    """
    Load coordinates either from:

    1. A JSON file
    2. Direct JSON command-line input
    3. The default 16-node network
    """

    if len(sys.argv) <= 1:

        return get_default_coordinates()

    input_source = sys.argv[1]

    try:

        # ----------------------------------------------------
        # JSON FILE
        # ----------------------------------------------------

        if input_source.lower().endswith(".json"):

            with open(
                input_source,
                "r"
            ) as file:

                coordinates = json.load(file)

        # ----------------------------------------------------
        # DIRECT JSON
        # ----------------------------------------------------

        else:

            json_input = " ".join(
                sys.argv[1:]
            ).strip()

            # Handle PowerShell escaped quotes
            json_input = json_input.replace(
                '\\"',
                '"'
            )

            if (
                len(json_input) >= 2
                and json_input[0] == json_input[-1]
                and json_input[0] in ["'", '"']
            ):

                json_input = json_input[1:-1]

            coordinates = json.loads(
                json_input
            )

        validate_coordinates(coordinates)

        return coordinates

    except FileNotFoundError:

        print(
            "ERROR: JSON file not found."
        )

        sys.exit(1)

    except json.JSONDecodeError as error:

        print(
            "ERROR: Invalid JSON input."
        )

        print(
            "Details:",
            error
        )

        sys.exit(1)

    except ValueError as error:

        print(
            "ERROR: Invalid coordinate data."
        )

        print(
            "Details:",
            error
        )

        sys.exit(1)


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    coordinates = load_coordinates()

    # Build communication graph
    network_graph = build_network_graph(
        coordinates
    )

    # Build distance-2 conflict graph
    conflict_graph = build_conflict_graph(
        network_graph
    )

    # Generate optimized TDMA schedule
    schedule, selected_strategy = create_schedule(
        conflict_graph
    )

    # Keep original coordinate order
    nodes = list(coordinates.keys())

    # Convert schedule to matrix
    matrix = create_schedule_matrix(
        schedule,
        nodes
    )

    # Print complete results
    print_results(
        network_graph,
        conflict_graph,
        schedule,
        matrix,
        selected_strategy
    )


# ============================================================
# START PROGRAM
# ============================================================

if __name__ == "__main__":
    main()