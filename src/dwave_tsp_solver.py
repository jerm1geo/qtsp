from dwave.system.samplers import DWaveSampler           # Library to interact with the QPU
from dwave.system.composites import EmbeddingComposite   # Library to embed our problem onto the QPU physical graph

import itertools
import scipy.optimize
import utilities
import numpy as np

class DWaveTSPSolver(object):
    """
    Class for solving Travelling Salesman Problem using DWave.
    Specifying starting point is not implemented.
    """
    def __init__(self, distance_matrix):
        max_distance = np.max(np.array(distance_matrix))
        scaled_distance_matrix = distance_matrix / max_distance
        self.distance_matrix = scaled_distance_matrix
        self.constraint_constant = 400
        self.cost_constant = 10
        self.chainstrength = 800
        self.numruns = 1000
        self.qubo_dict = {}
        self.add_cost_objective()
        self.add_time_constraints()
        self.add_position_constraints()

    def add_cost_objective(self):
        n = len(self.distance_matrix)
        for t in range(n):
            for i in range(n):
                for j in range(n):
                    if i == j:
                        continue
                    qubit_a = t * n + i
                    qubit_b = (t + 1) % n * n + j
                    self.qubo_dict[(qubit_a, qubit_b)] = self.cost_constant * self.distance_matrix[i][j]

    def add_time_constraints(self):
        n = len(self.distance_matrix)
        for t in range(n):
            for i in range(n):
                qubit_a = t * n + i
                if (qubit_a, qubit_a) not in self.qubo_dict.keys():
                    self.qubo_dict[(qubit_a, qubit_a)] = -self.constraint_constant
                else:
                    self.qubo_dict[(qubit_a, qubit_a)] += -self.constraint_constant
                for j in range(n):
                    qubit_b = t * n + j
                    if i!=j:
                        self.qubo_dict[(qubit_a, qubit_b)] = 2 * self.constraint_constant

    def add_position_constraints(self):
        n = len(self.distance_matrix)
        for i in range(n):
            for t1 in range(n):
                qubit_a = t1 * n + i
                if (qubit_a, qubit_a) not in self.qubo_dict.keys():
                    self.qubo_dict[(qubit_a, qubit_a)] = -self.constraint_constant
                else:
                    self.qubo_dict[(qubit_a, qubit_a)] += -self.constraint_constant
                for t2 in range(n):
                    qubit_b = t2 * n + i
                    if t1!=t2:
                        self.qubo_dict[(qubit_a, qubit_b)] = 2 * self.constraint_constant

    def solve_tsp(self):
        response = EmbeddingComposite(DWaveSampler()).sample_qubo(self.qubo_dict, chain_strength=self.chainstrength, num_reads=self.numruns)
        self.decode_solution(response)
        return self.solution

    def decode_solution(self, response):
        distribution = {}
        min_energy = response.record[0].energy

        for record in response.record:
            sample = record[0]
            solution_binary = [node for node in sample] 
            solution = utilities.binary_state_to_points_order(solution_binary)
            distribution[tuple(solution)] = (record.energy, record.num_occurrences)
            if record.energy <= min_energy:
                self.solution = solution

        self.distribution = distribution