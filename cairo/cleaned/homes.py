import pandas as pd
import geopandas as gpd
import numpy as np

def configure(context):
    context.stage("cairo.raw.population")
    context.stage("cairo.cleaned.population")

    context.config("cairo.crs")

def execute(context):
    df_persons = context.stage("cairo.cleaned.population")[[
        "household_id", "census_person_id"
    ]]

    df_homes = context.stage("cairo.raw.population")

    # Impute IDs
    df_homes = pd.merge(df_homes, df_persons, on = "census_person_id")

    df_homes = df_homes[["household_id", "geometry"]]
    df_homes = gpd.GeoDataFrame(df_homes, crs = context.config("cairo.crs"))

    return df_homes
