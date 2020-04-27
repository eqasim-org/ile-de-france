from tqdm import tqdm
import pandas as pd
import numpy as np
import simpledbf

"""
Cleans OD data to arrive at OD flows between municipalities for work
and education.
"""

def configure(context):
    context.stage("data.od.raw")
    context.stage("data.spatial.zones")

RENAME = { "COMMUNE" : "origin_id", "DCLT" : "destination_id", "IPONDI" : "weight", "DCETUF" : "destination_id" }

def execute(context):
    df_zones = context.stage("data.spatial.zones")
    df_zones = df_zones[df_zones["zone_level"] == "commune"][[
        "zone_id", "commune_id"
    ]]
    commune_ids = set(np.unique(df_zones["commune_id"]))

    # Load data
    df_work = pd.read_hdf("%s/work.hdf" % context.path("data.od.raw"))
    df_education = pd.read_hdf("%s/education.hdf" % context.path("data.od.raw"))

    # Renaming
    df_work = df_work.rename(RENAME, axis = 1)
    df_education = df_education.rename(RENAME, axis = 1)

    # Fix arrondissements
    df_work.loc[df_work["origin_id"] == "75056", "origin_id"] = df_work["ARM"]
    df_education.loc[df_education["origin_id"] == "75056", "origin_id"] = df_education["ARM"]

    # Clear invalid data
    df_work["origin_id"] = pd.to_numeric(df_work["origin_id"], errors = "coerce")
    df_work["destination_id"] = pd.to_numeric(df_work["destination_id"], errors = "coerce")
    df_work = df_work[["origin_id", "destination_id", "weight", "TRANS"]].dropna()

    df_education["origin_id"] = pd.to_numeric(df_education["origin_id"], errors = "coerce")
    df_education["destination_id"] = pd.to_numeric(df_education["destination_id"], errors = "coerce")
    df_education = df_education[["origin_id", "destination_id", "weight"]].dropna()

    # Remove 99999
    df_work = df_work[df_work["origin_id"] != 99999]
    df_work = df_work[df_work["destination_id"] != 99999]

    df_education = df_education[df_education["origin_id"] != 99999]
    df_education = df_education[df_education["destination_id"] != 99999]

    # Remove uninteresting communes
    df_work = df_work[df_work["origin_id"].isin(commune_ids)]
    df_work = df_work[df_work["destination_id"].isin(commune_ids)]
    df_education = df_education[df_education["origin_id"].isin(commune_ids)]
    df_education = df_education[df_education["destination_id"].isin(commune_ids)]

    # Convert communes to integer
    df_work["origin_id"] = df_work["origin_id"].astype(np.int)
    df_work["destination_id"] = df_work["destination_id"].astype(np.int)
    df_education["origin_id"] = df_education["origin_id"].astype(np.int)
    df_education["destination_id"] = df_education["destination_id"].astype(np.int)

    # Clean commute mode for work
    df_work["commute_mode"] = np.nan
    df_work.loc[df_work["TRANS"] == "1", "commute_mode"] = "no transport"
    df_work.loc[df_work["TRANS"] == "2", "commute_mode"] = "walk"
    df_work.loc[df_work["TRANS"] == "3", "commute_mode"] = "bike"
    df_work.loc[df_work["TRANS"] == "4", "commute_mode"] = "car"
    df_work.loc[df_work["TRANS"] == "5", "commute_mode"] = "pt"
    df_work["commute_mode"] = df_work["commute_mode"].astype("category")

    # Aggregate the flows
    df_work = df_work.groupby(["origin_id", "destination_id", "commute_mode"]).sum().reset_index()
    df_education = df_education.groupby(["origin_id", "destination_id"]).sum().reset_index()

    df_work["weight"] = df_work["weight"].fillna(0.0)
    df_education["weight"] = df_education["weight"].fillna(0.0)

    return df_work, df_education
