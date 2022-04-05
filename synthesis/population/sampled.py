import numpy as np
import pandas as pd

"""
This stage has the census data as input and samples households according to the
household weights given by INSEE. The resulting sample size can be controlled
through the 'sampling_rate' configuration option.
"""

def configure(context):
    context.stage("synthesis.population.updated")

    context.config("random_seed")
    context.config("sampling_rate")

def execute(context):
    df_census = context.stage("synthesis.population.updated").sort_values(by = "household_id").copy()

    sampling_rate = context.config("sampling_rate")
    random = np.random.RandomState(context.config("random_seed"))

    # Perform stochastic rounding for the population (and scale weights)
    df_rounding = df_census[["household_id", "weight", "household_size"]].drop_duplicates("household_id")
    df_rounding["multiplicator"] = np.floor(df_rounding["weight"])
    df_rounding["multiplicator"] += random.random_sample(len(df_rounding)) <= (df_rounding["weight"] - df_rounding["multiplicator"])
    df_rounding["multiplicator"] = df_rounding["multiplicator"].astype(np.int)

    # Multiply households (use same multiplicator for all household members)
    household_multiplicators = df_rounding["multiplicator"].values
    household_sizes = df_rounding["household_size"].values

    person_muliplicators = np.repeat(household_multiplicators, household_sizes)
    df_census = df_census.iloc[np.repeat(np.arange(len(df_census)), person_muliplicators)]

    # Create new household and person IDs
    df_census["census_person_id"] = df_census["person_id"]
    df_census["census_household_id"] = df_census["household_id"]

    df_census["person_id"] = np.arange(len(df_census))

    household_sizes = np.repeat(household_sizes, household_multiplicators)
    household_count = np.sum(household_multiplicators)
    df_census.loc[:, "household_id"] = np.repeat(np.arange(household_count), household_sizes)

    # Select sample from 100% population
    selector = random.random_sample(household_count) < sampling_rate
    selector = np.repeat(selector, household_sizes)
    df_census = df_census[selector]

    del df_census["weight"]
    return df_census
