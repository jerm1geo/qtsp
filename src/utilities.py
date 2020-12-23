import csv
import numpy as np
from node import Node

def read_nodes_from_file(filename):
    nodes = []
    with open(filename) as teamdatafile:
        nodereader = csv.reader(teamdatafile, delimiter=',', quotechar='"')
        for row in nodereader:
            nodes.append(Node(int(row[0]), row[1], row[2], float(row[3]), float(row[4])))

    return nodes

def create_edges(nodes):
    edges = []
    sub_nodes = nodes.copy()
    for n in nodes:
        sub_nodes.remove(n)
        for sn in sub_nodes:
            dist = n.compute_distance(sn)
            edges.append((n.id, sn.id, dist))
            edges.append((sn.id, n.id, dist))

    return edges

def matrix_from_graph(G):
    n = G.number_of_nodes()
    matrix = np.zeros((n, n))
    for u, v, weight in G.edges.data("weight"):
        matrix[u][v] = weight

    return matrix

def route_length(G, route):
    n = len(route)
    i = 0
    length = 0
    while i < n - 1:
        edge = G[route[i]][route[i+1]]
        length += edge['weight']
        i += 1
    
    return length

def max_edge_weight(G):
    max = 0
    for u, v, weight in G.edges.data("weight"):
        if weight is not None and weight > max:
            max = weight

    return max

def calculate_cost(cost_matrix, solution):
    cost = 0
    for i in range(len(solution)):
        a = i % len(solution)
        b = (i + 1) % len(solution)
        cost += cost_matrix[solution[a]][solution[b]]

    return cost

def binary_state_to_points_order(binary_state):
    """
    Transforms the the order of points from the binary representation: [1,0,0,0,1,0,0,0,1],
    to the binary one: [0, 1, 2]
    """
    points_order = []
    number_of_points = int(np.sqrt(len(binary_state)))
    for p in range(number_of_points):
        for j in range(number_of_points):
            if binary_state[(number_of_points) * p + j] == 1:
                points_order.append(j)
    return points_order