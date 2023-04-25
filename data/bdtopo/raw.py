import fiona
import pandas as pd
import os
import shapely.geometry as geo
import geopandas as gpd
import py7zr
import re
import glob
import numpy as np

"""
This stage loads the raw data from the BAN French building registry.
"""
 
def configure(context):
    context.config("data_path")
    context.config("bdtopo_path", "bdtopo")

    context.stage("data.spatial.departments")

def execute(context):
    df_departments = context.stage("data.spatial.departments")
    df_bdtopo = []

    # finding required file
    source_path = find_bdtopo("{}/{}".format(context.config("data_path"), context.config("bdtopo_path")))

    with py7zr.SevenZipFile(source_path) as archive:
        building_paths = [
            path for path in archive.getnames()
            if re.search(r"/BATIMENT\.[a-z]{3}$", path)
        ]

        archive.extract(context.path(), building_paths)

    shp_path = [path for path in building_paths if path.endswith(".shp")]

    if len(shp_path) != 1:
        raise RuntimeError("Cannot find buildings inside the archive, please report this as an error!")

    with context.progress(label = "Loading BD TOPO residential buildings registry ...") as progress:
        with fiona.open("{}/{}".format(context.path(), shp_path[0])) as archive:
            for item in archive:

                # we check for every buildings if it has residential use (only or mix use)
                if item['properties']["NB_LOGTS"] is not None and int(item['properties']["NB_LOGTS"]) > 0:
                    poly = geo.Polygon([i for i in item["geometry"]["coordinates"][0]])

                    if np.any(df_departments.covers(poly)):   
    
                        df_bdtopo.append(dict(geometry = item["geometry"],
                                              bdtopo_id = item["properties"]["ID"],
                                              housing = int(item['properties']["NB_LOGTS"])))
                                                         
                progress.update()

    df_bdtopo = pd.DataFrame.from_records(df_bdtopo)
    df_bdtopo = gpd.GeoDataFrame(df_bdtopo, crs = "EPSG:2154")
    df_bdtopo["centroid"] = df_bdtopo.centroid
        
    return df_bdtopo

def find_bdtopo(path):
    candidates = list(glob.glob("{}/*.7z".format(path)))

    if len(candidates) == 0:
        raise RuntimeError("BD TOPO data is not available in {}".format(path))
    
    if len(candidates) > 1:
        raise RuntimeError("Multiple candidates for BD TOPO are available in {}".format(path))
    
    return candidates[0]

def validate(context):
    path = find_bdtopo("{}/{}".format(context.config("data_path"), context.config("bdtopo_path")))
    return os.path.getsize(path)
