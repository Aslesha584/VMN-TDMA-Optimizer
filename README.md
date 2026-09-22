# VMN TDMA Schedule Planner and Optimizer

## Overview

This project implements a centralized TDMA Schedule Planner and Optimizer for a wireless network.

The optimizer takes the coordinates of network nodes as input, builds the communication graph based on a 500 meter communication range, creates a distance-2 conflict graph, and assigns TDMA transmission slots using graph coloring heuristics.

## Features

- Coordinate-based network construction
- 500 meter communication range
- 1-hop interference detection
- 2-hop / hidden-terminal interference detection
- Distance-2 graph coloring
- Greedy scheduling heuristics
- Spatial reuse
- TDMA Schedule Matrix
- Node-to-Slot mapping
- Schedule conflict verification
- JSON file input
- Automated validation test

## System Flow

Coordinates
↓
Communication Graph
↓
Distance-2 Conflict Graph
↓
Graph Coloring
↓
TDMA Schedule
↓
Schedule Matrix
↓
Conflict Verification

## Algorithm

Two nodes are considered conflicting if:

1. They have a direct communication link, or
2. They share a common neighbor.

The resulting conflict graph is colored using greedy graph-coloring heuristics.

Each color represents one TDMA slot.

Nodes with the same color can transmit in the same slot only when they do not have a distance-2 conflict.

## Input

The optimizer accepts node coordinates through a JSON file.

Example:

```json
{
  "Node_01": [0, 0],
  "Node_02": [300, 0],
  "Node_03": [800, 0],
  "Node_04": [300, 300],
  "Node_05": [800, 300]
}