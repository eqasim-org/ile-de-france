from tqdm import tqdm
import pandas as pd
import numpy as np

"""
This stage filters out census observations which live or work outside of
Île-de-France.
"""

def configure(context):
    context.stage("data.census.cleaned")
    context.stage("data.spatial.codes")

def execute(context):
    df = context.stage("data.census.cleaned")

    # Household size
    df_size = df[["household_id"]].groupby("household_id").size().reset_index(name = "household_size2")
    df = pd.merge(df_codes, df_size)

    assert np.all(df["household_size"] == df["household_size2"])
    print("all good")
    exit()


    # We remove people who study or work in another region
    f = df["work_outside_region"] | df["education_outside_region"]
    remove_ids = df[f]["household_id"].unique()

    initial_households = len(df["household_id"].unique())
    removed_households = len(remove_ids)

    initial_persons = len(df["person_id"].unique())
    removed_persons = np.count_nonzero(df["household_id"].isin(remove_ids))

    # Filter requested codes
    df_codes = context.stage("data.spatial.codes")

    requested_departements = df_codes["departement_id"].unique()
    df = df[df["departement_id"].isin(requested_departements)]

    excess_communes = set(df["commune_id"].unique()) - set(df_codes["commune_id"].unique())
    if not excess_communes == {"undefined"}:
        raise RuntimeError("Found additional communes: %s" % excess_communes)

    excess_iris = set(df["iris_id"].unique()) - set(df_codes["iris_id"].unique())
    if not excess_iris == {"undefined"}:
        raise RuntimeError("Found additional IRIS: %s" % excess_iris)

    # TODO: This filtering is not really compatible with defining multiple regions
    # or departments. This used to be a filter to avoid people going outside of
    # Île-de-France, but we should consider removing this filter altogether, or
    # find some smarter way (e.g. using OD matrices and filter out people in
    # each municipality by the share of outside workers).
    df_codes = context.stage("data.spatial.codes")

    if len(df_codes["region_id"].unique()) > 1:
        raise RuntimeError("""
            Multiple regions are defined, so the filtering for people going outside
            of Île-de-France does not make sense in that case. Consider adjusting the
            data.census.filtered stage!
        """)

    print(
        "Removing %d/%d (%.2f%%) households (with %d/%d persons, %.2f%%) because at least one person is working outside of Île-de-France" % (
        removed_households, initial_households, 100 * removed_households / initial_households,
        removed_persons, initial_persons, 100 * removed_persons / initial_persons
    ))

    context.set_info("filtered_households_share", removed_households / initial_households)
    context.set_info("filtered_persons_share", removed_persons / initial_persons)

    df = df[~df["household_id"].isin(remove_ids)]
    return df
