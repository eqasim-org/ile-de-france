from tqdm import tqdm
import pandas as pd
import numpy as np

"""
This stage filters out census observations which live or work outside of
Île-de-France.
"""

def configure(context):
    context.stage("data.census.cleaned")

def execute(context):
    df = context.stage("data.census.cleaned")

    # We remove people who study or work in another region
    f = df["work_outside_idf"] | df["education_outside_idf"]
    remove_ids = df[f]["household_id"].unique()

    initial_households = len(df["household_id"].unique())
    removed_households = len(remove_ids)

    initial_persons = len(df["person_id"].unique())
    removed_persons = np.count_nonzero(df["household_id"].isin(remove_ids))

    print(
        "Removing %d/%d (%.2f%%) households (with %d/%d persons, %.2f%%) because at least one person is working outside of Île-de-France" % (
        removed_households, initial_households, 100 * removed_households / initial_households,
        removed_persons, initial_persons, 100 * removed_persons / initial_persons
    ))

    context.set_info("filtered_households_share", removed_households / initial_households)
    context.set_info("filtered_persons_share", removed_persons / initial_persons)

    df = df[~df["household_id"].isin(remove_ids)]
    return df
