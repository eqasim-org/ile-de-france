import numpy as np
import pandas as pd

"""
LEAD: Create additional population for Confluence and apply population growth
"""

def configure(context):
    context.stage("data.census.filtered")
    context.stage("lead.factors")

    context.config("random_seed")

    context.config("lead_path")
    context.config("lead_year")

def execute(context):
    df_census = context.stage("data.census.filtered").sort_values(by = "household_id").copy()
    df_census = df_census.rename(columns = { "weight": "weight_2015" })

    # Merge growth factors
    df_growth = context.stage("lead.factors")
    df_census = pd.merge(df_census, df_growth, on = "departement_id", how = "left")
    assert np.count_nonzero(df_census["factor_2022"].isna()) == 0

    # First, bring the population to the level of 2022
    df_census["weight_2022"] = df_census["weight_2015"] * df_census["factor_2022"]

    print("Growth to 2022:")
    print(df_census[["departement_id", "weight_2015", "weight_2022"]].groupby("departement_id").sum())

    if context.config("lead_year") == 2022:
        df_census["weight"] = df_census["weight_2022"]

    elif context.config("lead_year") == 2030:
        # We select 2030, so we want to reconfigure Confluence

        df_census["weight_2030"] = df_census["weight_2022"] * df_census["factor_2030"]

        print("Growth to 2030 (region):")
        print(df_census[["departement_id", "weight_2015", "weight_2022", "weight_2030"]].groupby("departement_id").sum())

        source_iris = ["693820504", "693820502", "693820503"]
        target_iris = "693820501"

        # Find the persons from Confluence and remove target from census
        df_census = df_census[~(df_census["iris_id"] == target_iris)].copy()
        df_source = df_census[df_census["iris_id"].isin(source_iris)].copy()

        print("Growth to 2030 (Confluence):")
        df_source["iris_id"] = df_source["iris_id"].astype(str)
        print(df_source[["iris_id", "weight_2015", "weight_2022", "weight_2030"]].groupby("iris_id").sum())

        count_reference_2030 = 17000
        count_growth_2030 = df_source["weight_2030"].sum()
        count_missing = max(0, count_reference_2030 - count_growth_2030)

        print("Missing inhabitants:", count_missing)

        # We copy from the source IRIS to the target IRIS such that we meet the reference value
        # By that we gain the correct population and sociodemographic distribution

        df_target = df_source.copy()
        df_target["iris_id"] = target_iris
        df_target["weight_2030"] *= count_missing / df_target["weight_2030"].sum()
        print("Sum in 2030:", df_target["weight_2030"].sum())

        # Add back the new area
        df_census = pd.concat([df_census, df_target])

        # Choose weight
        df_census["weight"] = df_census["weight_2030"]

    else:
        raise RuntimeError("Invalid year chosen")

    return df_census
