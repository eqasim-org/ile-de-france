import pandas as pd
import geopandas as gpd
import os
import py7zr

"""
Loads the IRIS zoning system.
"""

def configure(context):
    context.config("data_path")
    context.config("iris_path", "iris_2021/CONTOURS-IRIS.shp")
    context.stage("data.spatial.codes")

def execute(context):
    df_codes = context.stage("data.spatial.codes")

    with py7zr.SevenZipFile("{}/{}".format(context.config("data_path"), context.config("iris_path"))) as archive:
        contour_paths = [
            path for path in archive.getnames()
            if "LAMB93" in path
        ]

        archive.extract(context.path(), contour_paths)
    
    shp_path = [path for path in contour_paths if path.endswith(".shp")]

    if len(shp_path) != 1:
        raise RuntimeError("Cannot find IRIS shapes inside the archive, please report this as an error!")

    df_iris = gpd.read_file("{}/{}".format(context.path(), shp_path[0]))[[
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
    if not os.path.exists("%s/%s" % (context.config("data_path"), context.config("iris_path"))):
        raise RuntimeError("IRIS data is not available")

    return os.path.getsize("%s/%s" % (context.config("data_path"), context.config("iris_path")))
