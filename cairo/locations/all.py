import pandas as pd
import geopandas as gpd
import numpy as np

def configure(context):
    context.stage("cairo.cleaned.homes")
    context.stage("cairo.locations.assigned")

    context.stage("cairo.cleaned.activities")
    context.stage("cairo.cleaned.population")

def execute(context):
    df_home = context.stage("cairo.cleaned.homes")
    df_assigned = context.stage("cairo.locations.assigned")[0]

    df_persons = context.stage("cairo.cleaned.population")[["person_id", "household_id"]]
    df_locations = context.stage("cairo.cleaned.activities")[["person_id", "activity_index", "purpose"]]

    # Home locations
    df_home_locations = df_locations[df_locations["purpose"] == "home"]
    df_home_locations = pd.merge(df_home_locations, df_persons, on = "person_id")
    df_home_locations = pd.merge(df_home_locations, df_home[["household_id", "geometry"]], on = "household_id")
    df_home_locations["location_id"] = -1
    df_home_locations = df_home_locations[["person_id", "activity_index", "location_id", "geometry"]]

    # Assigned locations
    df_assigned_locations = df_locations[~df_locations["purpose"].isin(("home",))].copy()
    df_assigned_locations = pd.merge(df_assigned_locations, df_assigned[[
        "person_id", "activity_index", "location_id", "geometry"
    ]], on = ["person_id", "activity_index"], how = "left")
    df_assigned_locations = df_assigned_locations[["person_id", "activity_index", "location_id", "geometry"]]
    assert not df_assigned_locations["geometry"].isna().any()

    # Validation
    initial_count = len(df_locations)
    df_locations = pd.concat([df_home_locations, df_assigned_locations])

    df_locations = df_locations.sort_values(by = ["person_id", "activity_index"])
    final_count = len(df_locations)
    assert initial_count == final_count

    assert not df_locations["geometry"].isna().any()
    df_locations = gpd.GeoDataFrame(df_locations, crs = df_home.crs)

    return df_locations
