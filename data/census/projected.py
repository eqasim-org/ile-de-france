import pandas as pd
import numpy as np

"""
This stage reweights the census data set according to the projection data for a different year.
"""

def configure(context):
    context.stage("data.census.cleaned")
    context.stage("data.census.projection")

def execute(context):
    df_census = context.stage("data.census.cleaned")
    projection = context.stage("data.census.projection")

    # Prepare indexing
    df_households = df_census[["household_id", "household_size", "weight"]].drop_duplicates("household_id")
    df_households["household_index"] = np.arange(len(df_households))
    df_census = pd.merge(df_census, df_households[["household_id", "household_index"]])

    # Obtain weights and sizes as arrays
    household_weights = df_households["weight"].values
    household_sizes = df_households["household_size"].values

    # Obtain the attribute levels and membership of attributes for all households
    attributes = []

    attribute_membership = []
    attribute_counts = []
    attribute_targets = []

    # Proccesing age ...
    df_marginal = projection["age"]
    for index, row in context.progress(df_marginal.iterrows(), label = "Processing attribute: age", total = len(df_marginal)):
        f = df_census["age"] == row["age"]

        if row["age"] == 0:
            continue # we skip incompatible values for peopel of zero age

        if np.count_nonzero(f) == 0:
            print("Did not find age:", row["age"])

        else:
            df_counts = df_census.loc[f, "household_index"].value_counts()
        
            attribute_targets.append(row["projection_year"])
            attribute_membership.append(df_counts.index.values)
            attribute_counts.append(df_counts.values)
            attributes.append("age={}".format(row["age"]))
    
    # Processing sex ...
    df_marginal = projection["sex"]
    for index, row in context.progress(df_marginal.iterrows(), label = "Processing attribute: sex", total = len(df_marginal)):
        f = df_census["sex"] == row["sex"]
        
        if np.count_nonzero(f) == 0:
            print("Did not find sex:", row["sex"])

        else:
            df_counts = df_census.loc[f, "household_index"].value_counts()
        
            attribute_targets.append(row["projection_year"])
            attribute_membership.append(df_counts.index.values)
            attribute_counts.append(df_counts.values)
            attributes.append("sex={}".format(row["sex"]))

    # Processing age x sex ...
    df_marginal = projection["cross"]
    for index, row in context.progress(df_marginal.iterrows(), label = "Processing attributes: sex x age", total = len(df_marginal)):
        f = (df_census["sex"] == row["sex"]) & (df_census["age"] == row["age"])

        if row["age"] == 0:
            continue
        
        if np.count_nonzero(f) == 0:
            print("Did not find values:", row["sex"], row["age"])

        else:
            df_counts = df_census.loc[f, "household_index"].value_counts()
        
            attribute_targets.append(row["projection_year"])
            attribute_membership.append(df_counts.index.values)
            attribute_counts.append(df_counts.values)
            attributes.append("sex={},age={}".format(row["sex"], row["age"]))

    # Processing total ...
    attribute_targets.append(projection["total"]["projection_year"].values[0])
    attribute_membership.append(np.arange(len(household_sizes)))
    attribute_counts.append(household_sizes)
    attributes.append("total")

    # Perform IPU to obtain update weights
    update = np.ones((len(df_households),))

    minimum_factors = []
    maximum_factors = []

    for iteration in context.progress(range(100), label = "Performing IPU"):
        factors = []    
        for k in np.arange(len(attributes)):
            selection = attribute_membership[k]
        
            target = attribute_targets[k]
            current = np.sum(update[selection] * household_weights[selection] * attribute_counts[k])
        
            factor = target / current
            factors.append(factor)
                
            update[selection] *= factor

        minimum_factors.append(np.min(factors))
        maximum_factors.append(np.max(factors))

        if np.max(factors) - np.min(factors) < 1e-3:
            break
    
    criterion = np.max(factors) - np.min(factors)

    # Check that the applied factors in the last iteration are sufficiently small
    assert criterion > 0.01

    for q in np.arange(10):
        print("Q", q, np.quantile(update, q / 10.0))

    # For a sanity check, we check for the obtained distribution in 2019, but this
    # may evolve in the future. 
    assert np.quantile(update, 0.9) < 2.0

    # Update the weights
    df_census["weight"] *= update
    
    return df_census
