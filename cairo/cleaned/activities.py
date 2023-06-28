import pandas as pd
import numpy as np

def configure(context):
    context.stage("cairo.raw.population")
    context.stage("cairo.cleaned.population")

def execute(context):
    df_persons = context.stage("cairo.cleaned.population")[[
        "person_id", "household_id", "census_person_id"
    ]]

    df_activities = context.stage("cairo.raw.population")
    df_activities = df_activities.rename(columns = { "person_id": "census_person_id" })

    # Impute IDs
    df_activities = pd.merge(df_activities, df_persons, on = "census_person_id")

    # Indices
    df_activities["trip_index"] = df_activities["activity_index"]
    df_activities["is_first"] = df_activities["activity_index"] == 0
    df_activities["is_last"] = df_activities["activity_index"] == df_activities["number_of_activities"] - 1

    # Purpose
    df_activities = df_activities.rename(columns = { "activity_start_time": "start_time" })
    df_activities = df_activities.rename(columns = { "activity_end_time": "end_time" })

    return df_activities[[
        "person_id", "household_id",
        "activity_index", "trip_index",
        "purpose", "start_time", "end_time",
        "is_first", "is_last"
    ]]
