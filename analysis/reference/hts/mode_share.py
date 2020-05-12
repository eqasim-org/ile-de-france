import pandas as pd
import numpy as np
import geopandas as gpd

import analysis.bootstrapping as bs
import analysis.statistics as stats
import analysis.marginals as marginals

ESTIMATION_SAMPLE_SIZE = 1000
DISTANCE_CLASSES = np.arange(1, 41) * 500

def configure(context):
    context.stage("data.hts.egt.filtered")

def execute(context):
    df_persons, df = context.stage("data.hts.egt.filtered")[1:]
    df = pd.merge(df, df_persons[["person_id", "person_weight"]])
    df = df.rename(columns = dict(person_weight = "weight"))

    df["travel_time"] = df["arrival_time"] - df["departure_time"]

    # Filter irrelevant information
    df = df[df["euclidean_distance"] > 0]
    df = df[df["travel_time"] > 0]

    # Add distance classes
    df["distance_class"] = np.digitize(df["euclidean_distance"], DISTANCE_CLASSES)

    # Calculate totals
    df_total = df[["distance_class", "weight"]].groupby("distance_class").sum().rename(columns = { "weight": "total" }).reset_index()
    df_modal = df[["distance_class", "mode", "weight"]].groupby(["distance_class", "mode"]).sum().reset_index()
    df_modal = pd.merge(df_modal, df_total)
    df_modal["share"] = df_modal["weight"] / df_modal["total"]

    return df_modal
