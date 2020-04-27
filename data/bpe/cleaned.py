import simpledbf
from tqdm import tqdm
import pandas as pd
import numpy as np
import data.spatial.utils
import data.spatial.zones as zones

"""
This stage cleans the enterprise census:
  - Filter out enterprises that do not have a valid municipality or IRIS
  - Assign coordinates randomly to enterprises that do not have coordinates
  - Simplify activity types for all enterprises
"""

def configure(context):
    context.stage("data.bpe.raw")
    context.stage("data.spatial.zones")
    context.config("bpe_random_seed", 0)

ACTIVITY_TYPE_MAP = [
    ("A", "other"),         # Police, post office, etc ...
    ("A504", "leisure"),    # Restaurant
    ("B", "shop"),          # Shopping
    ("C", "education"),     # Education
    ("D", "other"),         # Health
    ("E", "other"),         # Transport
    ("F", "leisure"),       # Sports & Culture
    ("G", "other"),         # Tourism, hotels, etc. (Hôtel = G102)
]

def execute(context):
    df = context.stage("data.bpe.raw")

    # Clean IDs
    df["enterprise_id"] = np.arange(len(df))

    # Clean activity type
    df["activity_type"] = "other"
    for prefix, activity_type in ACTIVITY_TYPE_MAP:
        df.loc[df["TYPEQU"].str.startswith(prefix), "activity_type"] = activity_type

    df["activity_type"] = df["activity_type"].astype("category")

    # Clean coordinates
    df["x"] = df["LAMBERT_X"].astype(np.float)
    df["y"] = df["LAMBERT_Y"].astype(np.float)

    # Clean IRIS and commune
    df["iris_id"] = df["DCIRIS"].str.replace("_", "")
    df["commune_id"] = df["DEPCOM"].astype(np.int)

    df["has_iris"] = df["DEPCOM"] != df["DCIRIS"]
    df.loc[~df["has_iris"], "iris_id"] = -1
    df["iris_id"] = df["iris_id"].astype(np.int)

    # Impute zone ID
    df_zones = context.stage("data.spatial.zones")

    initial_count = len(df)
    df = pd.merge(df, zones.translate_zone_ids(df_zones, df, "enterprise_id"))
    final_count = len(df)

    assert (df["commune_id"] >= 0).all()

    print("Removing %d/%d (%.2f%%) enterprises with unknown zone ..." % (
        initial_count - final_count, initial_count, 100 * (initial_count - final_count) / initial_count
    ))

    # Impute missing coordinates
    df["imputed_location"] = df["x"].isna()

    df_imputed = df[df["imputed_location"]].copy()
    random = np.random.RandomState(context.config("bpe_random_seed"))
    zones.sample_coordinates(context, df_zones, df_imputed, random, label = "Imputing unknown coordinates ...")
    df = pd.concat([df[~df["imputed_location"]], df_imputed])

    df = data.spatial.utils.to_gpd(context, df)
    return df[["enterprise_id", "activity_type", "commune_id", "geometry", "imputed_location"]]
