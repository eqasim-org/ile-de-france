import fiona
import pandas as pd
import os
import shapely.geometry as geo
import geopandas as gpd

"""
This stage loads the raw data from the French address registry.
"""

def configure(context):
    context.config("data_path")
    context.config("bdtopo_path", "bdtopo/BATIMENT.shp")

    context.stage("data.spatial.codes")

def execute(context):
    
    # will be used in further version
    df_codes = context.stage("data.spatial.codes")

    df_bdtopo = []

    with context.progress(label = "Loading BD TOPO residential buildings registry ...") as progress:
        with fiona.open("%s/%s" % (context.config("data_path"), context.config("bdtopo_path"))) as archive:
            for item in archive:
                # we check for every buildings if it has residential use (only or mix use)
                if item['properties']["NB_LOGTS"] is not None and int(item['properties']["NB_LOGTS"]) > 0:
                   
                    df_bdtopo.append(dict(
                        geometry = geo.Point(*item["geometry"]["coordinates"][0][0][0:2]),
                        bdtopo_id = item["properties"]["ID"]
                    ))

                progress.update()

    df_bdtopo = pd.DataFrame.from_records(df_bdtopo)
    df_bdtopo = gpd.GeoDataFrame(df_bdtopo, crs = "EPSG:2154")
    df_bdtopo = df_bdtopo[df_bdtopo.is_valid].copy()
    return df_bdtopo

def validate(context):
    if not os.path.exists("%s/%s" % (context.config("data_path"), context.config("bdtopo_path"))):
        raise RuntimeError("BD TOPO data is not available")

    return os.path.getsize("%s/%s" % (context.config("data_path"), context.config("bdtopo_path")))
