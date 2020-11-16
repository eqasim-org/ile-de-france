import geopandas as gpd
import pandas as pd
import shapely.geometry as geo
import os, datetime, json

def configure(context):
    context.stage("synthesis.population.enriched")

    context.stage("synthesis.population.activities")
    context.stage("synthesis.population.trips")

    context.stage("synthesis.population.spatial.locations")

    context.stage("documentation.meta_output")

def validate(context):
    output_path = context.config("output_path")

    if not os.path.isdir(output_path):
        raise RuntimeError("Output directory must exist: %s" % output_path)

def execute(context):
    output_path = context.config("output_path")

    # Prepare households
    df_households = context.stage("synthesis.population.enriched").rename(
        columns = { "household_income": "income" }
    ).drop_duplicates("household_id")

    df_households = df_households[[
        "household_id",
        "car_availability", "bike_availability",
        "income",
        "census_household_id"
    ]]

    df_households.to_csv("%s/households.csv" % output_path, sep = ";", index = None)

    # Prepare persons
    df_persons = context.stage("synthesis.population.enriched").rename(
        columns = { "has_license": "has_driving_license" }
    )

    df_persons = df_persons[[
        "person_id", "household_id",
        "age", "employed", "sex", "socioprofessional_class",
        "has_driving_license", "has_pt_subscription",
        "census_person_id", "hts_id"
    ]]

    df_persons.to_csv("%s/persons.csv" % output_path, sep = ";", index = None)

    # Prepare activities
    df_activities = context.stage("synthesis.population.activities").rename(
        columns = { "trip_index": "following_trip_index" }
    )

    df_activities["preceding_trip_index"] = df_activities["following_trip_index"].shift(1)
    df_activities.loc[df_activities["is_first"], "preceding_trip_index"] = -1
    df_activities["preceding_trip_index"] = df_activities["preceding_trip_index"].astype(int)

    df_activities = df_activities[[
        "person_id", "activity_index",
        "preceding_trip_index", "following_trip_index",
        "purpose", "start_time", "end_time",
        "is_first", "is_last"
    ]]

    df_activities.to_csv("%s/activities.csv" % output_path, sep = ";", index = None)

    # Prepare trips
    df_trips = context.stage("synthesis.population.trips").rename(
        columns = {
            "is_first_trip": "is_first",
            "is_last_trip": "is_last"
        }
    )

    df_trips["preceding_activity_index"] = df_trips["trip_index"]
    df_trips["following_activity_index"] = df_trips["trip_index"] + 1

    df_trips = df_trips[[
        "person_id", "trip_index",
        "preceding_activity_index", "following_activity_index",
        "departure_time", "arrival_time", "mode",
        "preceding_purpose", "following_purpose",
        "is_first", "is_last"
    ]]

    df_trips.to_csv("%s/trips.csv" % output_path, sep = ";", index = None)

    # Prepare spatial data sets
    df_locations = context.stage("synthesis.population.spatial.locations")[[
        "person_id", "activity_index", "geometry"
    ]]

    df_activities = pd.merge(df_activities, df_locations[[
        "person_id", "activity_index", "geometry"
    ]], how = "left", on = ["person_id", "activity_index"])

    # Write spatial activities
    df_spatial = gpd.GeoDataFrame(df_activities, crs = "EPSG:2154")
    df_spatial["purpose"] = df_spatial["purpose"].astype(str)
    df_spatial.to_file("%s/activities.gpkg" % output_path, driver = "GPKG")

    # Write spatial trips
    df_spatial = pd.merge(df_trips, df_locations[[
        "person_id", "activity_index", "geometry"
    ]].rename(columns = {
        "activity_index": "preceding_activity_index",
        "geometry": "preceding_geometry"
    }), how = "left", on = ["person_id", "preceding_activity_index"])

    df_spatial = pd.merge(df_spatial, df_locations[[
        "person_id", "activity_index", "geometry"
    ]].rename(columns = {
        "activity_index": "following_activity_index",
        "geometry": "following_geometry"
    }), how = "left", on = ["person_id", "following_activity_index"])

    df_spatial["geometry"] = [
        geo.LineString(od)
        for od in zip(df_spatial["preceding_geometry"], df_spatial["following_geometry"])
    ]

    df_spatial = df_spatial.drop(columns = ["preceding_geometry", "following_geometry"])

    df_spatial = gpd.GeoDataFrame(df_spatial, crs = "EPSG:2154")
    df_spatial["following_purpose"] = df_spatial["following_purpose"].astype(str)
    df_spatial["preceding_purpose"] = df_spatial["preceding_purpose"].astype(str)
    df_spatial["mode"] = df_spatial["mode"].astype(str)
    df_spatial.to_file("%s/trips.gpkg" % output_path, driver = "GPKG")
