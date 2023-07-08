import sklearn.neighbors
import numpy as np
import numpy.linalg as la

from synthesis.population.spatial.secondary.rda import AssignmentSolver, AssignmentObjective, GravityChainSolver, GeneralRelaxationSolver, DistanceSampler, DiscretizationSolver

class CandidateIndex:
    def __init__(self, df_candidates, identifier = "identifier"):
        activity_types = df_candidates["activity_type"].unique()

        self.identifier = identifier
        self.indices = {}
        self.identifiers = {}

        for activity_type in activity_types:
            print("Constructing spatial index for {} ...".format(activity_type))
            f = df_candidates["activity_type"] == activity_type

            self.identifiers[activity_type] = df_candidates[f][self.identifier].values

            self.indices[activity_type] = sklearn.neighbors.KDTree(
                np.vstack([df_candidates[f]["geometry"].x, df_candidates[f]["geometry"].y]).T)
            
            print("  indexed {} observations".format(np.count_nonzero(f)))

    def query(self, activity_type, location):
        index = self.indices[activity_type].query(location.reshape(1, -1), return_distance = False)[0][0]
        return self.identifiers[activity_type][index], self.indices[activity_type].data[index]

    def sample(self, activity_type, random):
        index = random.randint(0, len(self.identifiers[activity_type]))
        identifier = self.identifiers[activity_type][index]
        location = self.indices[activity_type].base_values[index]
        return identifier, location

class StaticDistanceSampler(DistanceSampler):
    def sample(self, problem):
        return dict(
            valid = True,
            distances = problem["distances"],
            iterations = 0
        )
    
class CairoDiscretizationSolver(DiscretizationSolver):
    def __init__(self, index):
        self.index = index

    def solve(self, problem, locations):
        discretized_locations = []
        discretized_identifiers = []

        for location, purpose in zip(locations, problem["purposes"]):
            identifier, location = self.index.query(purpose, location.reshape(1, -1))

            discretized_identifiers.append(identifier)
            discretized_locations.append(location)

        assert len(discretized_locations) == problem["size"]

        return dict(
            valid = True, locations = np.vstack(discretized_locations), identifiers = discretized_identifiers
        )

class CairoObjective(AssignmentObjective):
    def evaluate(self, problem, distance_result, relaxation_result, discretization_result):
        sampled_distances = distance_result["distances"]
        
        discretized_locations = []
        discretized_locations.append(problem["origin"])
        discretized_locations.append(discretization_result["locations"])
        discretized_locations.append(problem["destination"])
        discretized_locations = np.vstack(discretized_locations)
        
        discretized_distances = la.norm(discretized_locations[:-1] - discretized_locations[1:], axis = 1)
        discretization_error = np.abs(sampled_distances - discretized_distances)
        
        valid = np.all(discretization_error < 200.0)
        valid &= distance_result["valid"]
        valid &= relaxation_result["valid"]
        valid &= discretization_result["valid"]

        return dict(valid = valid, objective = np.sum(discretization_error))