import sklearn.neighbors
import numpy as np

class CandidateIndex:
    def __init__(self, df_candidates, identifier = "identifier"):
        location_types = df_candidates["location_type"].unique()

        self.identifier = identifier
        self.indices = {}
        self.identifiers = {}

        for location_type in location_types:
            print("Constructing spatial index for {} ...".format(location_type))
            f = df_candidates["location_type"] == location_type

            self.identifiers[location_type] = df_candidates[f][self.identifer].values

            self.indices[location_type] = sklearn.neighbors.KDTree(
                df_candidates[f]["geometry"].xy)
            
            print("  indexed {} observations".format(np.count_nonzero(f)))

    def query(self, location_type, location):
        index = self.indices[location_type].query(location.reshape(1, -1), return_distance = False)[0][0]
        return self.identifiers[location_type][index], self.indices[location_type].base_values[index]

    def sample(self, location_type, random):
        index = random.randint(0, len(self.identifiers[location_type]))
        identifier = self.identifiers[location_type][index]
        location = self.indices[location_type].base_values[index]
        return identifier, location
