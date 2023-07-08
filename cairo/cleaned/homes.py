import pandas as pd
import geopandas as gpd
import numpy as np

def configure(context):
    context.stage("cairo.raw.population")
    context.stage("cairo.cleaned.population")

    context.config("crs")

def execute(context):
    df_persons = context.stage("cairo.cleaned.population")[[
        "household_id", "census_person_id"
    ]].drop_duplicates("census_person_id")

    df_homes = context.stage("cairo.raw.population")[["person_id", "home_location"]]
    df_homes = df_homes.rename(columns = { "home_location": "geometry", "person_id": "census_person_id" })
    df_homes = df_homes.drop_duplicates("census_person_id")

    # Impute IDs
    df_homes = pd.merge(df_homes, df_persons, on = "census_person_id")
    df_homes = df_homes[["household_id", "geometry"]]
    df_homes = df_homes.set_geometry("geometry") # Necessary after rename

    return df_homes
