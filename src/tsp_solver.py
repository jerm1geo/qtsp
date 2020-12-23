import math
import utilities
import itertools
import dwave_networkx as dnx
from collections import defaultdict
from dwave.system import LeapHybridSampler
from dwave_tsp_solver import DWaveTSPSolver

class TSPSolver:
    def __init__(self, G, start=None, lagrange=None):
        self.G = G
        self.start = start
        self.lagrange = lagrange

    def classic_tsp(self):
        # We want '0' to be first, so remove it from the list before getting the permutations
        node_list = list(self.G)
        node_list.remove(self.start)

        routes = list(itertools.permutations(node_list))
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
        sampler = LeapHybridSampler()

        # Get a QUBO representation of the problem
        Q = self.quantum_tsp_qubo()

        # use the sampler to find low energy states
        response = sampler.sample_qubo(Q)
        sample = response.first.sample

        route = [None]*len(self.G)
        for (city, time), val in sample.items():
            if val:
                route[time] = city

        if self.start is not None and route[0] != self.start:
            # rotate to put the start in front
            idx = route.index(self.start)
            route = route[idx:] + route[:idx]

        return route

    def quantum_tsp_qubo(self):
        N = self.G.number_of_nodes()

        if self.lagrange is None:
            # If no lagrange parameter provided, set to 'average' tour length.
            # Usually a good estimate for a lagrange parameter is between 75-150%
            # of the objective function value, so we come up with an estimate for 
            # tour length and use that.
            if self.G.number_of_edges()>0:
                self.lagrange = self.G.size(weight='weight') * self.G.number_of_nodes() / self.G.number_of_edges()
            else:
                self.lagrange = 2

        print("A = ", self.lagrange)

        # some input checking
        if N in (1, 2) or len(self.G.edges) != N*(N-1)//2:
            msg = "graph must be a complete graph with at least 3 nodes or empty"
            raise ValueError(msg)

        # Creating the QUBO
        Q = defaultdict(float)

        # Constraint that each row has exactly one 1
        for node in self.G:
            for pos_1 in range(N):
                Q[((node, pos_1), (node, pos_1))] -= self.lagrange
                for pos_2 in range(pos_1+1, N):
                    Q[((node, pos_1), (node, pos_2))] += 2.0 * self.lagrange

        # Constraint that each col has exactly one 1
        for pos in range(N):
            for node_1 in self.G:
                Q[((node_1, pos), (node_1, pos))] -= self.lagrange
                for node_2 in set(self.G)-{node_1}:
                    # QUBO coefficient is 2*lagrange, but we are placing this value 
                    # above *and* below the diagonal, so we put half in each position.
                    Q[((node_1, pos), (node_2, pos))] += self.lagrange

        maxWeight = utilities.max_edge_weight(self.G)
        
        # 0 < weightFactor < lagrange; this is 1 by default
        weightFactor = self.lagrange / maxWeight
        if weightFactor < 1:
            weightFactor = 1
        elif weightFactor > 2:
            weightFactor = weightFactor / 2
        
        print("B = ", weightFactor * maxWeight)

        # Objective that minimizes distance
        for u, v in itertools.combinations(self.G.nodes, 2):
            for pos in range(N):
                nextpos = (pos + 1) % N

                # going from u -> v
                Q[((u, pos), (v, nextpos))] += weightFactor * self.G[u][v]['weight']

                # going from v -> u
                Q[((v, pos), (u, nextpos))] += weightFactor * self.G[u][v]['weight']

        return Q