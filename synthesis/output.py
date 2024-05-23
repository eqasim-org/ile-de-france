import shutil
import geopandas as gpd
import pandas as pd
import shapely.geometry as geo
import os, datetime, json
import sqlite3
import math
import numpy as np

def configure(context):
    context.stage("synthesis.population.enriched")

    context.stage("synthesis.population.activities")
    context.stage("synthesis.population.trips")

    if context.config("generate_vehicles_file", False):
        context.stage("synthesis.vehicles.selected")

    context.stage("synthesis.population.spatial.locations")

    context.stage("documentation.meta_output")

    context.config("output_path")
    context.config("output_prefix", "ile_de_france_")

    if context.config("mode_choice", False):
        context.stage("matsim.simulation.prepare")


def validate(context):
    output_path = context.config("output_path")

    if not os.path.isdir(output_path):
        raise RuntimeError("Output directory must exist: %s" % output_path)

def clean_gpkg(path):
    '''
    Make GPKG files time and OS independent.

    In GeoPackage metadata:
    - replace last_change date with a placeholder, and
    - round coordinates.

    This allow for comparison of output digests between runs and between OS.
    '''
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    for table_name, min_x, min_y, max_x, max_y in cur.execute(
        "SELECT table_name, min_x, min_y, max_x, max_y FROM gpkg_contents"
    ):
        cur.execute(
            "UPDATE gpkg_contents " +
            "SET last_change='2000-01-01T00:00:00Z', min_x=?, min_y=?, max_x=?, max_y=? " +
            "WHERE table_name=?",
            (math.floor(min_x), math.floor(min_y), math.ceil(max_x), math.ceil(max_y), table_name)
        )
    conn.commit()
    conn.close()

def execute(context):
    output_path = context.config("output_path")
    output_prefix = context.config("output_prefix")

    # Prepare households
    df_households = context.stage("synthesis.population.enriched").rename(
        columns = { "household_income": "income" }
    ).drop_duplicates("household_id")

    df_households = df_households[[
        "household_id",
        "car_availability", "bike_availability",
        "number_of_vehicles", "number_of_bikes",
        "income",
        "census_household_id"
    ]]

    df_households.to_csv("%s/%shouseholds.csv" % (output_path, output_prefix), sep = ";", index = None, lineterminator = "\n")

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

    df_persons.to_csv("%s/%spersons.csv" % (output_path, output_prefix), sep = ";", index = None, lineterminator = "\n")

    # Prepare activities
    df_activities = context.stage("synthesis.population.activities").rename(
        columns = { "trip_index": "following_trip_index" }
    )

    df_activities = pd.merge(
        df_activities, df_persons[["person_id", "household_id"]], on = "person_id")

    df_activities["preceding_trip_index"] = df_activities["following_trip_index"].shift(1)
    df_activities.loc[df_activities["is_first"], "preceding_trip_index"] = -1
    df_activities["preceding_trip_index"] = df_activities["preceding_trip_index"].astype(int)

    df_activities = df_activities[[
        "person_id", "household_id", "activity_index",
        "preceding_trip_index", "following_trip_index",
        "purpose", "start_time", "end_time",
        "is_first", "is_last"
    ]]

    df_activities.to_csv("%s/%sactivities.csv" % (output_path, output_prefix), sep = ";", index = None, lineterminator = "\n")

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
        "departure_time", "arrival_time",
        "preceding_purpose", "following_purpose",
        "is_first", "is_last"
    ]]

    if context.config("mode_choice"):
        df_mode_choice = pd.read_csv(
            "{}/mode_choice/output_trips.csv".format(context.path("matsim.simulation.prepare"), output_prefix),
            delimiter = ";")

        df_mode_choice = df_mode_choice.rename(columns={"person_trip_id": "trip_index"})
        columns_to_keep = ["person_id", "trip_index"]
        columns_to_keep.extend([c for c in df_trips.columns if c not in df_mode_choice.columns])
        df_trips = df_trips[columns_to_keep]
        df_trips = pd.merge(df_trips, df_mode_choice, on = [
            "person_id", "trip_index"], how="left", validate = "one_to_one")

        shutil.copy("%s/mode_choice/output_pt_legs.csv" % (context.path("matsim.simulation.prepare")),
                    "%s/%spt_legs.csv" % (output_path, output_prefix))

        assert not np.any(df_trips["mode"].isna())                                 

    df_trips.to_csv("%s/%strips.csv" % (output_path, output_prefix), sep = ";", index = None, lineterminator = "\n")

    if context.config("generate_vehicles_file"):
        # Prepare vehicles
        df_vehicle_types, df_vehicles = context.stage("synthesis.vehicles.selected")

        df_vehicle_types.to_csv("%s/%svehicle_types.csv" % (output_path, output_prefix), sep = ";", index = None, lineterminator = "\n")
        df_vehicles.to_csv("%s/%svehicles.csv" % (output_path, output_prefix), sep = ";", index = None, lineterminator = "\n")

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
    path = "%s/%sactivities.gpkg" % (output_path, output_prefix)
    df_spatial.to_file(path, driver = "GPKG")
    clean_gpkg(path)

    # Write spatial homes
    path = "%s/%shomes.gpkg" % (output_path, output_prefix)
    df_spatial[
        df_spatial["purpose"] == "home"
    ].drop_duplicates("household_id")[[
        "household_id", "geometry"
    ]].to_file(path, driver = "GPKG")
    clean_gpkg(path)

    # Write spatial commutes
    df_spatial = pd.merge(
        df_spatial[df_spatial["purpose"] == "home"].drop_duplicates("person_id")[["person_id", "geometry"]].rename(columns = { "geometry": "home_geometry" }),
        df_spatial[df_spatial["purpose"] == "work"].drop_duplicates("person_id")[["person_id", "geometry"]].rename(columns = { "geometry": "work_geometry" })
    )

    df_spatial["geometry"] = [
        geo.LineString(od)
        for od in zip(df_spatial["home_geometry"], df_spatial["work_geometry"])
    ]

    df_spatial = df_spatial.drop(columns = ["home_geometry", "work_geometry"])
    path = "%s/%scommutes.gpkg" % (output_path, output_prefix)
    df_spatial.to_file(path, driver = "GPKG")
    clean_gpkg(path)

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

    if "mode" in df_spatial:
        df_spatial["mode"] = df_spatial["mode"].astype(str)

    path = "%s/%strips.gpkg" % (output_path, output_prefix)
    df_spatial.to_file(path, driver = "GPKG")
    clean_gpkg(path)
