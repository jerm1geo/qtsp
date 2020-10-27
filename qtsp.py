import sys
import csv
import time
from itertools import permutations
import networkx as nx
import dimod
from dwave.system import DWaveSampler
from dwave.system import LeapHybridSampler
import dwave_networkx as dnx
from node import Node

def read_nodes_from_file(filename):
    nodes = []
    with open(filename) as teamdatafile:
        nodereader = csv.reader(teamdatafile, delimiter=',', quotechar='"')
        for row in nodereader:
            nodes.append(Node(row[0], row[1], row[2], float(row[3]), float(row[4])))

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

def route_length(G, route):
    n = len(route)
    i = 0
    length = 0
    while i < n - 1:
        edge = G[route[i]][route[i+1]]
        length += edge['weight']
        i += 1
    
    return length    

def classic_tsp(G):
    # We want 'J' to be first, so remove it from the list before getting the permutations
    node_list = list(G)
    node_list.remove('J')

    routes = list(permutations(node_list))
    best_route_length = float("inf")
    best_route = None

    for route in routes:
        route_list = list(route)
        # Insert 'J' back in at the beginning of the route
        route_list.insert(0, 'J')
        length = route_length(G, route_list)
        if length < best_route_length:
            best_route_length = length
            best_route = route_list

    return best_route

def quantum_tsp(G):
    # I've inlined some code from the dwave_networkx library here to inspect things at a
    # lower level

    # 0.75 to 1.50 are typical values for this factor; 
    # smaller than that and you risk not including all the nodes
    factor = 1
    lagrange = factor * G.size(weight='weight') * G.number_of_nodes() / G.number_of_edges()
    
    sampler = LeapHybridSampler()
    # return dnx.traveling_salesperson(G, sampler=sampler, lagrange=lagrange, start='J')
    
    # This is the expanded version of the TSP method call on the previous line
    start = 'J'
    Q = dnx.traveling_salesperson_qubo(G, lagrange)

    # use the sampler to find low energy states
    response = sampler.sample_qubo(Q)

    print(response)
    sample = response.first.sample

    route = [None]*len(G)
    for (city, time), val in sample.items():
        if val:
            route[time] = city

    if start is not None and route[0] != start:
        # rotate to put the start in front
        idx = route.index(start)
        route = route[idx:] + route[:idx]

    return route

def main(argv):
    nodes = read_nodes_from_file('test-data.csv')
    edges = create_edges(nodes)
    G = nx.Graph()
    G.add_weighted_edges_from(edges)
    
    tic = time.perf_counter()
    if len(argv) > 0 and argv[0] == '1':
        route = quantum_tsp(G)
    else:
        route = classic_tsp(G)
    toc = time.perf_counter()

    length = route_length(G, route)
    print('Route: {0}'.format(route))
    print('Length: %.0f miles' % length)
    print('Compute Time: %.2f seconds' % (toc-tic))

if __name__ == "__main__":
    main(sys.argv[1:])
