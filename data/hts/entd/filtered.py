import data.hts.hts as hts

"""
This stage filters out ENTD observations which live or work outside of
Île-de-France.
"""

def configure(context):
    context.stage("data.hts.entd.cleaned")

def execute(context):
    df_households, df_persons, df_trips = context.stage("data.hts.entd.cleaned")

    # Only keep trips and households that still have a person
    df_trips = df_trips[df_trips["person_id"].isin(df_persons["person_id"].unique())]
    df_households = df_households[df_households["household_id"].isin(df_persons["household_id"])]

    # Finish up
    df_households = df_households[hts.HOUSEHOLD_COLUMNS + ["income_class"]]
    df_persons = df_persons[hts.PERSON_COLUMNS]
    df_trips = df_trips[hts.TRIP_COLUMNS + ["routed_distance"]]

    hts.check(df_households, df_persons, df_trips)
    return df_households, df_persons, df_trips
