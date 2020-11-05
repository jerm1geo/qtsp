import sys
import time
import networkx as nx
import utilities
from tsp_solver import TSPSolver

def main(argv):
    method = 'classic'
    if len(argv) > 0:
        method = argv[0]

    nodes = utilities.read_nodes_from_file('../data/test-data.csv')
    edges = utilities.create_edges(nodes)
    G = nx.Graph()
    G.add_weighted_edges_from(edges)
    solver = TSPSolver(G, 0)

    tic = time.perf_counter()
    if method == 'quantum':
        route = solver.quantum_tsp()
    elif method == 'hybrid':
        route = solver.hybrid_tsp()
    else:
        route = solver.classic_tsp()
    toc = time.perf_counter()

    length = utilities.route_length(G, route)
    print('Route: {0}'.format(route))
    print('Length: %.0f miles' % length)
    print('Compute Time: %.2f seconds' % (toc-tic))

if __name__ == "__main__":
    main(sys.argv[1:])
