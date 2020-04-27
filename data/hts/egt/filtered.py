import data.hts.hts as hts
import numpy as np

"""
This stage filters out EGT observations which live or work outside of
Île-de-France.
"""

def configure(context):
    context.stage("data.hts.egt.cleaned")

def execute(context):
    df_households, df_persons, df_trips = context.stage("data.hts.egt.cleaned")

    # Filter for non-residents
    f = df_persons["departement_id"].isin(hts.FILTER_DEPARTEMENTS)
    df_persons = df_persons[f]

    # Filter for people going outside of the area (because they have NaN distances)
    remove_ids = set()

    remove_ids |= set(df_trips[
        ~df_trips["origin_departement_id"].isin(hts.FILTER_DEPARTEMENTS) | ~df_trips["destination_departement_id"].isin(hts.FILTER_DEPARTEMENTS)
    ]["person_id"].unique())

    remove_ids |= set(df_persons[
        ~df_persons["departement_id"].isin(hts.FILTER_DEPARTEMENTS)
    ])

    df_persons = df_persons[~df_persons["person_id"].isin(remove_ids)]

    # Only keep trips and households that still have a person
    df_trips = df_trips[df_trips["person_id"].isin(df_persons["person_id"].unique())]
    df_households = df_households[df_households["household_id"].isin(df_persons["household_id"])]

    # Finish up
    df_households = df_households[hts.HOUSEHOLD_COLUMNS]
    df_persons = df_persons[hts.PERSON_COLUMNS]
    df_trips = df_trips[hts.TRIP_COLUMNS + ["euclidean_distance"]]

    hts.check(df_households, df_persons, df_trips)
    return df_households, df_persons, df_trips
