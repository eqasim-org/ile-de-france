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
    context.config("bdtopo_path", "bdtopo/ADRESSE.shp")

    context.stage("data.spatial.codes")

def execute(context):
    df_codes = context.stage("data.spatial.codes")
    requested_departements = set(df_codes["departement_id"].unique())

    df_bdtopo = []

    with context.progress(label = "Loading BD TOPO address registry ...") as progress:
        with fiona.open("%s/%s" % (context.config("data_path"), context.config("bdtopo_path"))) as archive:
            for item in archive:
                code = item["properties"]["CODE_INSEE"]

                if code[:2] in requested_departements or code[:3] in requested_departements:
                    df_bdtopo.append(dict(
                        geometry = geo.Point(*item["geometry"]["coordinates"]),
                        commune_id = item["properties"]["CODE_INSEE"],
                        raw_number = pd.to_numeric(item["properties"]["NUMERO"]),
                        raw_street = item["properties"]["NOM_1"]
                    ))

                progress.update()

    df_bdtopo = pd.DataFrame.from_records(df_bdtopo)
    df_bdtopo = gpd.GeoDataFrame(df_bdtopo, crs = "EPSG:2154")

    return df_bdtopo

def validate(context):
    if not os.path.exists("%s/%s" % (context.config("data_path"), context.config("bdtopo_path"))):
        raise RuntimeError("BD TOPO data is not available")

    return os.path.getsize("%s/%s" % (context.config("data_path"), context.config("bdtopo_path")))
