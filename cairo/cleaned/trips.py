import pandas as pd
import numpy as np

def configure(context):
    context.stage("cairo.cleaned.activities")

def execute(context):
    df_trips = context.stage("cairo.cleaned.activities")

    # First / last
    df_trips["is_first_trip"] = df_trips["trip_index"] == 0
    df_trips["is_last_trip"] = df_trips["is_last"].shift(-1) == True

    # Timing
    df_trips["departure_time"] = df_trips["end_time"].shift(0)
    df_trips["arrival_time"] = df_trips["start_time"].shift(-1)

    # Purpose
    df_trips["preceding_purpose"] = df_trips["purpose"].shift(0)
    df_trips["following_purpose"] = df_trips["purpose"].shift(-1)

    # Mode placeholder
    df_trips["mode"] = "car"

    # Drop last activity
    df_trips = df_trips[~df_trips["is_last"]]
    df_trips = df_trips.sort_values(by = ["person_id", "trip_index"])
    
    return df_trips[[
        "person_id", "household_id",
        "trip_index", "is_first_trip", "is_last_trip",
        "preceding_purpose", "following_purpose",
        "departure_time", "arrival_time",
        "mode"        
    ]]
