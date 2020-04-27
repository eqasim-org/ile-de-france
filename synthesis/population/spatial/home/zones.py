import numpy as np
import pandas as pd
import data.spatial.zones as zones
from tqdm import tqdm
import data.spatial.utils

"""
This stage samples home zones for all synthesized households. From the census
data we have several special cases that we need to cover:
- For people that live in municipalities without IRIS, only their departement is known
- For people that live in IRIS with less than 200 inhabitants, only their municipality is known

Based on these criteria, we can attach a random commune from the departement (which is not
covered by IRIS) to the first case, and we can attach a random IRIS within a commune that
has less than 200 inhabitants to the second case.
"""

def configure(context):
    context.stage("synthesis.population.sampled")
    context.stage("data.spatial.zones")

    context.config("random_seed")

def execute(context):
    random = np.random.RandomState(context.config("random_seed"))

    df_households = context.stage("synthesis.population.sampled").drop_duplicates("household_id")[[
        "household_id", "has_commune", "has_iris", "commune_id", "iris_id", "departement_id"
    ]].copy()

    df_zones = context.stage("data.spatial.zones")

    # Fix missing communes (we select from those without IRIS)
    f_missing_commune = ~df_households["has_commune"]
    df_missing_commune = df_households[f_missing_commune].copy()

    for departement_id in context.progress(df_missing_commune["departement_id"].unique(), label = "Fixing missing communes ..."):
        df_candidates = df_zones[
            (df_zones["zone_level"] == "commune") &
            ~df_zones["has_iris"] &
            (df_zones["departement_id"] == departement_id)
        ][["zone_id", "population", "commune_id"]].copy()

        weights = df_candidates["population"].values
        weights /= np.sum(weights)

        f = df_missing_commune["departement_id"] == departement_id
        indices = np.repeat(np.arange(weights.shape[0]), random.multinomial(np.count_nonzero(f), weights))

        df_missing_commune.loc[f, "zone_id"] = df_candidates.iloc[indices]["zone_id"].values
        df_missing_commune.loc[f, "commune_id"] = df_candidates.iloc[indices]["commune_id"].values

    assert not df_missing_commune["zone_id"].isna().any()

    # Fix missing IRIS (we select from those with <200 inhabitants)
    f_missing_iris = ~df_households["has_iris"] & df_households["has_commune"]
    df_missing_iris = df_households[f_missing_iris].copy()

    for commune_id in context.progress(np.unique(df_missing_iris["commune_id"]), label = "Fixing missing IRIS ..."):
        df_candidates = df_zones[
            (df_zones["zone_level"] == "iris") &
            (df_zones["population"] <= 200) &
            (df_zones["commune_id"] == commune_id)
        ][["zone_id", "population", "commune_id"]].copy()

        weights = df_candidates["population"].values
        if (weights == 0.0).all(): weights += 1.0
        weights /= np.sum(weights)

        f = df_missing_iris["commune_id"] == commune_id
        indices = np.repeat(np.arange(weights.shape[0]), random.multinomial(np.count_nonzero(f), weights))

        df_missing_iris.loc[f, "zone_id"] = df_candidates.iloc[indices]["zone_id"].values
        df_missing_iris.loc[f, "commune_id"] = df_candidates.iloc[indices]["commune_id"].values

    assert len(df_missing_iris) == 0 or not df_missing_iris["zone_id"].isna().any()

    # Finally, we can attach the zone ID to the valid ones
    df_valid = df_households[df_households["has_iris"] & df_households["has_commune"]]
    df_valid = pd.merge(df_valid, df_zones[["iris_id", "zone_id"]])

    # Merge everything together and test consistency
    df_result = pd.concat([df_missing_commune, df_missing_iris, df_valid])
    df_result["zone_id"] = df_result["zone_id"].astype(np.int)

    assert len(df_result) == len(df_households)
    assert (df_result["commune_id"] >= 0).all()
    assert (df_result["zone_id"] >= 0).all()

    return df_result[["household_id", "zone_id", "departement_id", "commune_id", "has_iris", "has_commune"]]
