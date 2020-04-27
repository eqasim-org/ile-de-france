import numpy as np
import pandas as pd
import geopandas as gpd
import os

"""
Loads the IRIS zoning system.
"""

def configure(context):
    context.config("data_path")

IDF_DEPARTEMENTS = ["75", "77", "78", "91", "92", "93", "94", "95"]

def execute(context):
    df_iris = gpd.read_file("%s/iris_2017/CONTOURS-IRIS.shp" % context.config("data_path"))
    df_iris = df_iris[["INSEE_COM", "CODE_IRIS", "geometry"]]
    df_iris.columns = ["commune_id", "iris_id", "geometry"]
    df_iris.crs = {"init":"EPSG:2154"}

    df_iris["departement_id"] = df_iris["commune_id"].str[:2]

    df_iris = df_iris[
        df_iris["departement_id"].isin(IDF_DEPARTEMENTS)
    ]

    return df_iris

def validate(context):
    if not os.path.exists("%s/iris_2017/CONTOURS-IRIS.shp" % context.config("data_path")):
        raise RuntimeError("IRIS data is not available")

    return os.path.getsize("%s/iris_2017/CONTOURS-IRIS.shp" % context.config("data_path"))
