from .components import CandidateIndex, StaticDistanceSampler, CairoDiscretizationSolver, CairoObjective
from synthesis.population.spatial.secondary.rda import GravityChainSolver, GeneralRelaxationSolver, AssignmentSolver
from .problems import find_assignment_problems

import numpy as np
import pandas as pd
import geopandas as gpd
import shapely.geometry as geo

def configure(context):
    context.config("random_seed")
    context.config("processes")
    context.config("secloc_maximum_iterations", np.inf)
    context.config("cairo.sla_iterations", 20)

    context.stage("cairo.locations.candidates")
    context.stage("cairo.cleaned.trips")
    context.stage("cairo.cleaned.homes")
    context.stage("cairo.cleaned.population")

MAPPING = {
    "work": ("primary_education", "secondary_education", "higher_education", "university", "other_education", "other", "clinic", "hospital", "other_health_activities", "recreation", "restaurant_cafe", "sports", "shop", "manufacturing"),
    "personal": ("clinic", "hospital", "other_health_activities", "recreation", "restaurant_cafe", "sports"),
    "primary": ("primary_education",),
    "secondary": ("secondary_education",),
    "uni": ("higher_education", "university"),
    "shopping": ("shop",)
}

def execute(context):
    # Prepare candidates
    df_candidates = context.stage("cairo.locations.candidates")
    print("Mapping locations to activity types")
    df_mapped = []

    for activity_type, location_types in MAPPING.items():
        f = df_candidates["location_type"].isin(location_types)

        df_partial = df_candidates[f].copy().drop(columns = ["location_type"])
        df_partial["activity_type"] = activity_type

        print("Found {} locations for {}".format(np.count_nonzero(f), activity_type))
        df_mapped.append(df_partial)

    df_mapped = pd.concat(df_mapped)
    del df_candidates

    # Prepare population data
    df_trips = context.stage("cairo.cleaned.trips")
    df_trips = df_trips.sort_values(by = ["person_id", "trip_index"])

    df_homes = context.stage("cairo.cleaned.homes")
    df_persons = context.stage("cairo.cleaned.population")[["person_id", "household_id"]]
    df_homes = pd.merge(df_homes, df_persons, on = "household_id")
    df_homes = df_homes.rename(columns = { "geometry": "home" })
    df_homes = df_homes[["person_id", "home"]]
    df_homes = df_homes.sort_values(by = "person_id")

    # Segment into subsamples
    processes = context.config("processes")

    unique_person_ids = df_trips["person_id"].unique()
    number_of_persons = len(unique_person_ids)
    unique_person_ids = np.array_split(unique_person_ids, processes)

    random = np.random.RandomState(context.config("random_seed"))
    random_seeds = random.randint(10000, size = processes)

    # Create batch problems for parallelization
    batches = []

    for index in range(processes):
        batches.append((
            df_trips[df_trips["person_id"].isin(unique_person_ids[index])],
            df_homes[df_homes["person_id"].isin(unique_person_ids[index])],
            random_seeds[index]
        ))
    
    # Run algorithm in parallel
    with context.progress(label = "Assigning secondary locations to persons", total = number_of_persons):
        with context.parallel(processes = processes, data = dict(
            candidates = df_mapped
        )) as parallel:
            df_locations, df_convergence = [], []

            for df_locations_item, df_convergence_item in parallel.imap_unordered(process, batches):
                df_locations.append(df_locations_item)
                df_convergence.append(df_convergence_item)

    df_locations = pd.concat(df_locations).sort_values(by = ["person_id", "activity_index"])
    df_convergence = pd.concat(df_convergence)

    print("Success rate:", df_convergence["valid"].mean())

    return df_locations, df_convergence

def process(context, arguments):
    df_trips, df_homes, random_seed = arguments

    # Set up RNG
    random = np.random.RandomState(context.config("random_seed"))
    maximum_iterations = context.config("secloc_maximum_iterations")

    # Set up candidate index
    df_candidates = context.data("candidates")
    candidate_index = CandidateIndex(df_candidates, "location_id")

    # Set up distance sampler
    distance_sampler = StaticDistanceSampler()

    # Set up the chain solver, currently we don't have "tail" chains that start/end with non-fixed activities
    random = np.random.RandomState(context.config("random_seed"))
    
    chain_solver = GravityChainSolver(
        random = random, eps = 10.0, lateral_deviation = 10.0, alpha = 0.1,
        maximum_iterations = 1000
    )

    # Relaxation solver delegating to the gravity chain solver 
    relaxation_solver = GeneralRelaxationSolver(chain_solver)
        
    # Discretization
    discretization_solver = CairoDiscretizationSolver(candidate_index)

    # Objective
    objective = CairoObjective()

    # Set up the solver
    ITERATIONS = context.config("cairo.sla_iterations")
    assignment_solver = AssignmentSolver(
        distance_sampler = distance_sampler,
        relaxation_solver = relaxation_solver,
        discretization_solver = discretization_solver,
        objective = objective,
        maximum_iterations = ITERATIONS
    )

    df_locations = []
    df_convergence = []

    last_person_id = None

    for problem in find_assignment_problems(df_trips, df_homes):
        result = assignment_solver.solve(problem)

        starting_activity_index = problem["activity_index"]

        for index, (identifier, location) in enumerate(zip(result["discretization"]["identifiers"], result["discretization"]["locations"])):
            df_locations.append((
                problem["person_id"], starting_activity_index + index, identifier, geo.Point(location)
            ))

            df_convergence.append((
                result["valid"], problem["size"]
            ))

            if problem["person_id"] != last_person_id:
                last_person_id = problem["person_id"]
                context.progress.update()
    
    df_locations = pd.DataFrame.from_records(df_locations, columns = ["person_id", "activity_index", "location_id", "geometry"])
    df_locations = gpd.GeoDataFrame(df_locations, crs = df_candidates.crs)
    assert not df_locations["geometry"].isna().any()

    df_convergence = pd.DataFrame.from_records(df_convergence, columns = ["valid", "size"])
    return df_locations, df_convergence
