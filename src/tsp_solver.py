import dwave_networkx as dnx
import utilities
from itertools import permutations
from dwave.system import LeapHybridSampler
from dwave_tsp_solver import DWaveTSPSolver

class TSPSolver:
    def __init__(self, G, start=None):
        self.G = G
        self.start = start

    def classic_tsp(self):
        # We want '0' to be first, so remove it from the list before getting the permutations
        node_list = list(self.G)
        node_list.remove(self.start)

        routes = list(permutations(node_list))
        best_route_length = float("inf")
        best_route = None

        for route in routes:
            route_list = list(route)
            # Insert '0' back in at the beginning of the route
            route_list.insert(0, self.start)
            length = utilities.route_length(self.G, route_list)
            if length < best_route_length:
                best_route_length = length
                best_route = route_list

        return best_route       

    def hybrid_tsp(self):
        sampler = LeapHybridSampler()
        return dnx.traveling_salesperson(self.G, sampler, start=self.start)

    def quantum_tsp(self):
        tsp_matrix = utilities.matrix_from_graph(self.G)
        dwave_solver = DWaveTSPSolver(tsp_matrix)
        route = dwave_solver.solve_tsp()
        if self.start is not None and route[0] != self.start:
            idx = route.index(self.start)
            route = route[idx:] + route[:idx]
        
        return route