import numpy as np
import pandas as pd
import geopandas as gpd
import os

"""
Loads the IRIS zoning system.
"""

YEAR = 2017
SOURCE = "iris_%d/CONTOURS-IRIS.shp" % YEAR

def configure(context):
    context.config("data_path")
    context.stage("data.spatial.codes")

def execute(context):
    df_codes = context.stage("data.spatial.codes")

    df_iris = gpd.read_file("%s/%s" % (context.config("data_path"), SOURCE))[[
        "CODE_IRIS", "INSEE_COM", "geometry"
    ]].rename(columns = {
        "CODE_IRIS": "iris_id",
        "INSEE_COM": "commune_id"
    })

    df_iris.crs = "EPSG:2154"

    df_iris["iris_id"] = df_iris["iris_id"].astype("category")
    df_iris["commune_id"] = df_iris["commune_id"].astype("category")

    # Merge with requested codes and verify integrity
    df_iris = pd.merge(df_iris, df_codes, on = ["iris_id", "commune_id"])

    requested_iris = set(df_codes["iris_id"].unique())
    merged_iris = set(df_iris["iris_id"].unique())

    if requested_iris != merged_iris:
        raise RuntimeError("Some IRIS are missing: %s" % (requested_iris - merged_iris,))

    return df_iris

def validate(context):
    if not os.path.exists("%s/%s" % (context.config("data_path"), SOURCE)):
        raise RuntimeError("IRIS data is not available")

    return os.path.getsize("%s/%s" % (context.config("data_path"), SOURCE))
