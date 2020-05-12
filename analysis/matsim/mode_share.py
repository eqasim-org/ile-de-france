import pandas as pd
import numpy as np
import geopandas as gpd

import analysis.bootstrapping as bs
import analysis.statistics as stats
import analysis.marginals as marginals

ESTIMATION_SAMPLE_SIZE = 1000
DISTANCE_CLASSES = np.arange(1, 41) * 500

def configure(context):
    acquisition_sample_size = context.config("acquisition_sample_size")
    bs.configure(context, "matsim.simulation.run", acquisition_sample_size) #, ephemeral = False)

def execute(context):
    acquisition_sample_size = context.config("acquisition_sample_size")

    df_all = []

    with context.progress(label = "Processing mode share data ...", total = acquisition_sample_size) as progress:
        for path in bs.get_paths(context, "matsim.simulation.run", acquisition_sample_size):
            df = pd.read_csv("%s/simulation_output/trips.csv" % path, sep = ";")
            df["weight"] = 1.0

            # Filter irrelevant information
            df = df[df["crowfly_distance"] > 0]
            df = df[df["travel_time"] > 0]

            # Add distance classes
            df["distance_class"] = np.digitize(df["crowfly_distance"], DISTANCE_CLASSES)

            # Calculate totals
            df_total = df[["distance_class", "weight"]].groupby("distance_class").sum().rename(columns = { "weight": "total" }).reset_index()
            df_modal = df[["distance_class", "mode", "weight"]].groupby(["distance_class", "mode"]).sum().reset_index()
            df_modal = pd.merge(df_modal, df_total)
            df_modal["share"] = df_modal["weight"] / df_modal["total"]

            df_all.append(df_modal[["distance_class", "mode", "share"]])

    df_all = pd.concat(df_all)
    df_all = df_all.groupby(["distance_class", "mode"])["share"].apply(lambda x: dict(
        mean = x.mean(),
        median = x.median(),
        q10 = x.quantile(0.1),
        q90 = x.quantile(0.9)
    )).reset_index().rename(columns = dict(level_2 = "metric"))

    return df_all
