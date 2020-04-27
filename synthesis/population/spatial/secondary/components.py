import synthesis.population.spatial.secondary.rda as rda
import sklearn.neighbors
import numpy as np

class CustomDistanceSampler(rda.FeasibleDistanceSampler):
    def __init__(self, random, distributions, maximum_iterations = 1000):
        rda.FeasibleDistanceSampler.__init__(self, random = random, maximum_iterations = maximum_iterations)

        self.random = random
        self.distributions = distributions

    def sample_distances(self, problem):
        distances = np.zeros((problem["size"] + 1))

        for index, (mode, travel_time) in enumerate(zip(problem["modes"], problem["travel_times"])):
            mode_distribution = self.distributions[mode]

            bound_index = np.count_nonzero(travel_time > mode_distribution["bounds"])
            mode_distribution = mode_distribution["distributions"][bound_index]

            distances[index] = mode_distribution["values"][
                np.count_nonzero(self.random.random_sample() > mode_distribution["cdf"])
            ]

        return distances

class CustomDiscretizationSolver(rda.DiscretizationSolver):
    def __init__(self, data):
        self.data = data
        self.indices = {}

        for purpose, data in self.data.items():
            print("Constructing spatial index for %s ..." % purpose)
            self.indices[purpose] = sklearn.neighbors.KDTree(data["locations"])

    def solve(self, problem, locations):
        discretized_locations = []
        discretized_identifiers = []

        for location, purpose in zip(locations, problem["purposes"]):
            index = self.indices[purpose].query(location.reshape(1, -1), return_distance = False)[0][0]

            discretized_identifiers.append(self.data[purpose]["identifiers"][index])
            discretized_locations.append(self.data[purpose]["locations"][index])

        return dict(
            valid = True, locations = np.vstack(discretized_locations), identifiers = discretized_identifiers
        )
