import data.hts.hts as hts
import numpy as np

"""
This stage filters out EGT observations which live or work outside of
Île-de-France.
"""

def configure(context):
    context.stage("data.hts.egt.cleaned")
    context.stage("data.spatial.codes")

def execute(context):
    df_codes = context.stage("data.spatial.codes")
    assert (df_codes["region_id"] == 11).all() # Otherwise EGT doesn't make sense

    df_households, df_persons, df_trips = context.stage("data.hts.egt.cleaned")

    # Filter for non-residents
    requested_departments = df_codes["departement_id"].unique()
    f = df_persons["departement_id"].astype(str).isin(requested_departments) # pandas bug!
    df_persons = df_persons[f]

    # Filter for people going outside of the area (because they have NaN distances)
    remove_ids = set()

    remove_ids |= set(df_trips[
        ~df_trips["origin_departement_id"].astype(str).isin(requested_departments) | ~df_trips["destination_departement_id"].astype(str).isin(requested_departments)
    ]["person_id"].unique())

    remove_ids |= set(df_persons[
        ~df_persons["departement_id"].isin(requested_departments)
    ])

    df_persons = df_persons[~df_persons["person_id"].isin(remove_ids)]

    # Only keep trips and households that still have a person
    df_trips = df_trips[df_trips["person_id"].isin(df_persons["person_id"].unique())]
    df_households = df_households[df_households["household_id"].isin(df_persons["household_id"])]

    # Finish up
    df_households = df_households[hts.HOUSEHOLD_COLUMNS + ["income_class"] + ["egt_household_id"]]
    df_persons = df_persons[hts.PERSON_COLUMNS + ["egt_household_id", "egt_person_id"]]
    df_trips = df_trips[hts.TRIP_COLUMNS + ["euclidean_distance"] + ["egt_household_id", "egt_person_id", "egt_trip_id"]]

    hts.check(df_households, df_persons, df_trips)

    return df_households, df_persons, df_trips
